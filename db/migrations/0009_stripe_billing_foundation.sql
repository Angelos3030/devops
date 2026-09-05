-- Stripe billing foundation: additive lifecycle state, event ledger and one
-- atomic service-role transition. Stripe remains the source of truth.

ALTER TABLE public.subscriptions
  ADD COLUMN IF NOT EXISTS stripe_price_id text,
  ADD COLUMN IF NOT EXISTS trial_start timestamptz,
  ADD COLUMN IF NOT EXISTS trial_end timestamptz,
  ADD COLUMN IF NOT EXISTS current_period_start timestamptz,
  ADD COLUMN IF NOT EXISTS cancel_at_period_end boolean NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS canceled_at timestamptz,
  ADD COLUMN IF NOT EXISTS ended_at timestamptz,
  ADD COLUMN IF NOT EXISTS latest_invoice_id text,
  ADD COLUMN IF NOT EXISTS first_payment_failed_at timestamptz,
  ADD COLUMN IF NOT EXISTS last_stripe_event_created_at timestamptz,
  ADD COLUMN IF NOT EXISTS last_stripe_event_id text,
  ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();

CREATE UNIQUE INDEX IF NOT EXISTS subscriptions_stripe_customer_unique
  ON public.subscriptions(stripe_customer_id)
  WHERE stripe_customer_id IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS subscriptions_stripe_sub_unique
  ON public.subscriptions(stripe_sub_id)
  WHERE stripe_sub_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS public.stripe_events (
  stripe_event_id text PRIMARY KEY,
  event_type text NOT NULL,
  stripe_created_at timestamptz NOT NULL,
  received_at timestamptz NOT NULL DEFAULT now(),
  processed_at timestamptz,
  processing_status text NOT NULL DEFAULT 'processing'
    CHECK (processing_status IN (
      'processing', 'processed', 'failed', 'ignored_stale',
      'ignored_unknown', 'ignored_malformed', 'ignored_conflict'
    )),
  client_id uuid REFERENCES public.clients(id) ON DELETE SET NULL,
  stripe_customer_id text,
  stripe_subscription_id text,
  result_code text,
  error_message text,
  attempt_count integer NOT NULL DEFAULT 1 CHECK (attempt_count > 0)
);

CREATE INDEX IF NOT EXISTS stripe_events_client_received_idx
  ON public.stripe_events(client_id, received_at DESC);
CREATE INDEX IF NOT EXISTS stripe_events_subscription_created_idx
  ON public.stripe_events(stripe_subscription_id, stripe_created_at DESC);

ALTER TABLE public.stripe_events ENABLE ROW LEVEL SECURITY;
GRANT SELECT, INSERT, UPDATE ON public.stripe_events TO service_role;
REVOKE ALL ON public.stripe_events FROM PUBLIC, anon, authenticated;

CREATE OR REPLACE FUNCTION public.process_stripe_billing_event(
  p_event_id text,
  p_event_type text,
  p_event_created bigint,
  p_client_id uuid DEFAULT NULL,
  p_customer_id text DEFAULT NULL,
  p_subscription_id text DEFAULT NULL,
  p_price_id text DEFAULT NULL,
  p_subscription_status text DEFAULT NULL,
  p_trial_start bigint DEFAULT NULL,
  p_trial_end bigint DEFAULT NULL,
  p_period_start bigint DEFAULT NULL,
  p_period_end bigint DEFAULT NULL,
  p_cancel_at_period_end boolean DEFAULT NULL,
  p_canceled_at bigint DEFAULT NULL,
  p_ended_at bigint DEFAULT NULL,
  p_latest_invoice_id text DEFAULT NULL,
  p_customer_email text DEFAULT NULL,
  p_disposition text DEFAULT NULL,
  p_error_message text DEFAULT NULL
) RETURNS jsonb
LANGUAGE plpgsql
SECURITY INVOKER
SET search_path = public, pg_temp
AS $$
DECLARE
  v_existing public.stripe_events%ROWTYPE;
  v_client_id uuid := p_client_id;
  v_last_created timestamptz;
  v_event_time timestamptz;
  v_effective_end timestamptz;
  v_client_status text;
BEGIN
  IF coalesce(p_event_id, '') = '' OR coalesce(p_event_type, '') = ''
     OR p_event_created IS NULL THEN
    RAISE EXCEPTION 'missing Stripe event identity';
  END IF;
  v_event_time := to_timestamp(p_event_created);

  INSERT INTO public.stripe_events (
    stripe_event_id, event_type, stripe_created_at, client_id,
    stripe_customer_id, stripe_subscription_id
  ) VALUES (
    p_event_id, p_event_type, v_event_time, v_client_id,
    p_customer_id, p_subscription_id
  ) ON CONFLICT (stripe_event_id) DO NOTHING;

  SELECT * INTO v_existing FROM public.stripe_events
    WHERE stripe_event_id = p_event_id FOR UPDATE;

  IF v_existing.processing_status IN (
      'processed', 'ignored_stale', 'ignored_unknown',
      'ignored_malformed', 'ignored_conflict') THEN
    RETURN jsonb_build_object(
      'ok', true, 'duplicate', true,
      'status', v_existing.processing_status,
      'client_id', v_existing.client_id
    );
  END IF;

  IF v_existing.processing_status = 'failed' THEN
    UPDATE public.stripe_events SET
      processing_status = 'processing', processed_at = NULL,
      error_message = NULL, attempt_count = attempt_count + 1
    WHERE stripe_event_id = p_event_id;
  END IF;

  IF p_disposition IN ('ignored_malformed', 'ignored_unknown') THEN
    UPDATE public.stripe_events SET
      processing_status = p_disposition,
      processed_at = now(), result_code = p_disposition,
      error_message = left(p_error_message, 500)
    WHERE stripe_event_id = p_event_id;
    RETURN jsonb_build_object('ok', true, 'duplicate', false,
                              'status', p_disposition);
  END IF;

  BEGIN
    IF v_client_id IS NULL AND p_customer_id IS NOT NULL THEN
      SELECT client_id INTO v_client_id FROM public.subscriptions
        WHERE stripe_customer_id = p_customer_id LIMIT 1;
    END IF;

    IF v_client_id IS NULL OR NOT EXISTS (
        SELECT 1 FROM public.clients WHERE id = v_client_id) THEN
      UPDATE public.stripe_events SET
        processing_status = 'ignored_unknown', processed_at = now(),
        result_code = 'unknown_client', error_message = 'unknown client relationship'
      WHERE stripe_event_id = p_event_id;
      RETURN jsonb_build_object('ok', true, 'duplicate', false,
                                'status', 'ignored_unknown');
    END IF;

    IF p_customer_id IS NOT NULL AND EXISTS (
      SELECT 1 FROM public.subscriptions
      WHERE stripe_customer_id = p_customer_id AND client_id <> v_client_id
    ) THEN
      UPDATE public.stripe_events SET
        processing_status = 'ignored_conflict', processed_at = now(),
        client_id = v_client_id, result_code = 'customer_tenant_conflict',
        error_message = 'Stripe customer already belongs to another client'
      WHERE stripe_event_id = p_event_id;
      RETURN jsonb_build_object('ok', true, 'duplicate', false,
                                'status', 'ignored_conflict');
    END IF;

    IF p_event_type = 'checkout.session.completed' THEN
      IF p_customer_email IS NOT NULL AND position('@' in p_customer_email) > 1 THEN
        UPDATE public.clients SET email = lower(trim(p_customer_email))
          WHERE id = v_client_id AND (email IS NULL OR trim(email) = '');
      END IF;
      UPDATE public.stripe_events SET
        processing_status = 'processed', processed_at = now(),
        client_id = v_client_id, result_code = 'checkout_linked'
      WHERE stripe_event_id = p_event_id;
      RETURN jsonb_build_object('ok', true, 'duplicate', false,
                                'status', 'processed', 'client_id', v_client_id);
    END IF;

    SELECT last_stripe_event_created_at INTO v_last_created
      FROM public.subscriptions WHERE client_id = v_client_id FOR UPDATE;
    IF v_last_created IS NOT NULL AND v_event_time < v_last_created THEN
      UPDATE public.stripe_events SET
        processing_status = 'ignored_stale', processed_at = now(),
        client_id = v_client_id, result_code = 'older_than_subscription_state'
      WHERE stripe_event_id = p_event_id;
      RETURN jsonb_build_object('ok', true, 'duplicate', false,
                                'status', 'ignored_stale', 'client_id', v_client_id);
    END IF;

    INSERT INTO public.subscriptions (
      client_id, stripe_customer_id, stripe_sub_id, stripe_price_id, plan,
      status, trial_start, trial_end, current_period_start, current_period_end,
      cancel_at_period_end, canceled_at, ended_at, latest_invoice_id,
      first_payment_failed_at, last_stripe_event_created_at,
      last_stripe_event_id, updated_at
    ) VALUES (
      v_client_id, p_customer_id, p_subscription_id, p_price_id, 'site',
      p_subscription_status,
      CASE WHEN p_trial_start IS NULL THEN NULL ELSE to_timestamp(p_trial_start) END,
      CASE WHEN p_trial_end IS NULL THEN NULL ELSE to_timestamp(p_trial_end) END,
      CASE WHEN p_period_start IS NULL THEN NULL ELSE to_timestamp(p_period_start) END,
      CASE WHEN p_period_end IS NULL THEN NULL ELSE to_timestamp(p_period_end) END,
      coalesce(p_cancel_at_period_end, false),
      CASE WHEN p_canceled_at IS NULL THEN NULL ELSE to_timestamp(p_canceled_at) END,
      CASE WHEN p_ended_at IS NULL THEN NULL ELSE to_timestamp(p_ended_at) END,
      p_latest_invoice_id,
      CASE WHEN p_event_type = 'invoice.payment_failed' THEN v_event_time ELSE NULL END,
      v_event_time, p_event_id, now()
    ) ON CONFLICT (client_id) DO UPDATE SET
      stripe_customer_id = coalesce(EXCLUDED.stripe_customer_id, subscriptions.stripe_customer_id),
      stripe_sub_id = coalesce(EXCLUDED.stripe_sub_id, subscriptions.stripe_sub_id),
      stripe_price_id = coalesce(EXCLUDED.stripe_price_id, subscriptions.stripe_price_id),
      plan = coalesce(subscriptions.plan, EXCLUDED.plan),
      status = coalesce(EXCLUDED.status, subscriptions.status),
      trial_start = coalesce(EXCLUDED.trial_start, subscriptions.trial_start),
      trial_end = coalesce(EXCLUDED.trial_end, subscriptions.trial_end),
      current_period_start = coalesce(EXCLUDED.current_period_start, subscriptions.current_period_start),
      current_period_end = coalesce(EXCLUDED.current_period_end, subscriptions.current_period_end),
      cancel_at_period_end = CASE
        WHEN p_cancel_at_period_end IS NULL THEN subscriptions.cancel_at_period_end
        ELSE p_cancel_at_period_end END,
      canceled_at = coalesce(EXCLUDED.canceled_at, subscriptions.canceled_at),
      ended_at = coalesce(EXCLUDED.ended_at, subscriptions.ended_at),
      latest_invoice_id = coalesce(EXCLUDED.latest_invoice_id, subscriptions.latest_invoice_id),
      first_payment_failed_at = CASE
        WHEN p_event_type = 'invoice.payment_failed'
          THEN coalesce(subscriptions.first_payment_failed_at, v_event_time)
        WHEN EXCLUDED.status = 'active' THEN NULL
        ELSE subscriptions.first_payment_failed_at END,
      last_stripe_event_created_at = v_event_time,
      last_stripe_event_id = p_event_id,
      updated_at = now();

    SELECT coalesce(
      CASE WHEN p_ended_at IS NULL THEN NULL ELSE to_timestamp(p_ended_at) END,
      greatest(
        CASE WHEN p_trial_end IS NULL THEN '-infinity'::timestamptz ELSE to_timestamp(p_trial_end) END,
        CASE WHEN p_period_end IS NULL THEN '-infinity'::timestamptz ELSE to_timestamp(p_period_end) END
      )
    ) INTO v_effective_end;
    v_client_status := CASE
      WHEN p_subscription_status IN ('trialing', 'active') THEN 'active'
      WHEN p_subscription_status = 'past_due' THEN 'active'
      WHEN p_subscription_status = 'canceled' AND v_effective_end > now() THEN 'active'
      WHEN p_subscription_status = 'canceled' THEN 'cancelled'
      ELSE 'paused' END;
    UPDATE public.clients SET status = v_client_status, plan = 'site'
      WHERE id = v_client_id;

    UPDATE public.stripe_events SET
      processing_status = 'processed', processed_at = now(),
      client_id = v_client_id, result_code = 'applied'
    WHERE stripe_event_id = p_event_id;
    RETURN jsonb_build_object('ok', true, 'duplicate', false,
                              'status', 'processed', 'client_id', v_client_id);
  EXCEPTION WHEN OTHERS THEN
    UPDATE public.stripe_events SET
      processing_status = 'failed', processed_at = now(),
      client_id = v_client_id, result_code = 'database_transition_failed',
      error_message = left(SQLSTATE || ': ' || SQLERRM, 500)
    WHERE stripe_event_id = p_event_id;
    RETURN jsonb_build_object('ok', false, 'duplicate', false,
                              'status', 'failed', 'error', 'billing transition failed');
  END;
END;
$$;

REVOKE ALL ON FUNCTION public.process_stripe_billing_event(
  text,text,bigint,uuid,text,text,text,text,bigint,bigint,bigint,bigint,
  boolean,bigint,bigint,text,text,text,text
) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.process_stripe_billing_event(
  text,text,bigint,uuid,text,text,text,text,bigint,bigint,bigint,bigint,
  boolean,bigint,bigint,text,text,text,text
) TO service_role;
