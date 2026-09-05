# Billing Contract

Stripe is the billing source of truth. Vitrina stores Stripe state and dates so
the product can enforce access and explain billing without calling Stripe for
every request. It does not invent a parallel subscription state machine.

## Commercial Offer

- 30 days free, then EUR 14.99 per month.
- A payment card is collected during Checkout.
- Amount due at signup is EUR 0.
- Checkout is created only by the server with the configured Stripe Price and
  `trial_period_days=30`. The browser cannot choose price, currency or duration.

## Stripe Status Mapping

| Stripe status | Stored status | Customer meaning |
|---|---|---|
| `trialing` | `trialing` | Full access until `trial_end`. |
| `active` | `active` | Full access through the current paid period. |
| `past_due` | `past_due` | Payment recovery; full access for a 7-day grace period. |
| `unpaid` | `unpaid` | No paid entitlement; data and site remain stored. |
| `canceled` | `canceled` | Access remains only until a future effective end supplied by Stripe. |
| `incomplete` | `incomplete` | No paid entitlement. Checkout/payment is incomplete. |
| `incomplete_expired` | `incomplete_expired` | No paid entitlement. Data remains stored. |
| `paused` | `paused` | No paid entitlement unless Stripe supplies a future access end. |

`invoice.payment_failed` records `past_due` when Stripe has not yet sent a
newer subscription status. `invoice.paid` records the invoice and the
subscription event remains authoritative for `active`.

## Entitlement Policy

Entitlement is derived from the stored Stripe status and Stripe dates:

- `trialing`, `active`: full normal product entitlement.
- `past_due`: full entitlement until seven days after the first failed-payment
  event. Further failures do not extend the original grace window.
- `canceled` with a future `trial_end` or `current_period_end`: entitlement
  remains until that effective end.
- `cancel_at_period_end=true`: entitlement remains while the underlying status
  is `trialing` or `active`, through the effective end.
- `unpaid`, `incomplete`, `incomplete_expired`, `paused`, or a cancellation
  whose effective end has passed: paid entitlement is removed.

Loss of entitlement never deletes customer data, removes the site, or changes
published content automatically. The UI must provide a billing-recovery path.

## Event Contract

- Every signed Stripe event is entered in `stripe_events` by event id.
- A processed event is an exact duplicate and becomes a no-op.
- A failed event can be retried with the same id.
- Subscription transitions compare Stripe event creation time. An older event
  is recorded as `ignored_stale` and cannot overwrite newer state.
- Event claim, subscription transition and successful ledger completion occur
  in one database transaction through `process_stripe_billing_event()`.
- The RPC is revoked from `PUBLIC`, `anon` and `authenticated`; only
  `service_role` may execute it.
- Full Stripe payloads and payment details are not stored.

## Cancellation Semantics

Cancellation behavior is exactly what Stripe reports:

- `cancel_at_period_end=true`: service continues until `trial_end` or
  `current_period_end`.
- immediate `canceled`: service continues only if Stripe supplies a future
  effective end; otherwise paid entitlement ends immediately.
- customer data remains available for recovery/support and is never deleted by
  the billing webhook.
