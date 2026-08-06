# Vitrina Social Engine

Το Vitrina χρησιμοποιεί δικό του approval-first social engine και συνδέεται απευθείας με
τα επίσημα Meta Graph APIs. Δεν εξαρτάται από Postiz, Make, Zapier ή άλλο scheduler.

## Ροή

`pending_approval → scheduled → publishing → published`

Εναλλακτικές τελικές/ενδιάμεσες καταστάσεις: `rejected`, `failed`. Ένα αποτυχημένο post
επιστρέφει σε `scheduled` μέχρι το `max_attempts`, με αυξανόμενο backoff.

Κανόνες ασφαλείας:

- Κάθε νέο post έχει `approval_required=true`.
- Μόνο authenticated owner του client μπορεί να εγκρίνει ή να απορρίψει.
- Το `dry_run` δεν αλλάζει post σε `published`.
- Αν πετύχει ένα δίκτυο και αποτύχει άλλο, το retry δεν ξαναποστάρει στο επιτυχημένο δίκτυο.
- Κάθε απόπειρα γράφεται στο `publish_logs`.
- Instagram post απαιτεί δημόσιο `image_url`. Text-only draft στο dashboard στοχεύει μόνο Facebook.
- Ads και spend δεν ανήκουν σε αυτό το milestone.

## Αρχεία

- `db/add_social_engine.sql`: production migration (εφαρμόστηκε 2026-08-06).
- `src/social_engine.py`: queue worker και retry/idempotency logic.
- `src/publisher.py`: direct Facebook/Instagram Graph API adapter.
- `src/daily_post.py`: δημιουργεί drafts, δεν δημοσιεύει.
- `scripts/run_social_worker.py`: one-shot worker command.
- `sites/app/dashboard/page.jsx`: content queue, approve/reject UI.
- `tests/test_social_engine.py`: approval, dry-run και partial retry tests.

## API

Όλα απαιτούν `Authorization: Bearer <Supabase access token>`:

- `GET /clients/{client_id}/social-queue`
- `POST /clients/{client_id}/social-queue`
- `POST /clients/{client_id}/social-queue/{post_id}/approve`
- `POST /clients/{client_id}/social-queue/{post_id}/reject`
- `POST /clients/{client_id}/social-queue/{post_id}/preview`

## Worker

Το command είναι one-shot και κατάλληλο για Railway Cron:

```bash
python scripts/run_social_worker.py --dry-run
python scripts/run_social_worker.py
```

Μην ενεργοποιήσεις το πραγματικό command πριν ολοκληρωθεί το Meta App Review και περάσει
ένα end-to-end test με test Page. Για πρώτη δοκιμή χρησιμοποίησε πάντα `--dry-run`.

## Επόμενα milestones

1. Meta App Review και test Page σύνδεση.
2. Railway Cron service κάθε 1-5 λεπτά.
3. Upload/asset picker για Instagram εικόνα.
4. Content generation policy ανά πελάτη (`auto_draft` ή manual).
5. Analytics ingestion.
6. Ξεχωριστό Ads engine με hard budget cap και ρητή έγκριση spend.
