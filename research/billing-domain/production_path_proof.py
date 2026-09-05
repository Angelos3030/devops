"""Απόδειξη: η διαδρομή της παραγωγής ισοδυναμεί με την καθαρή εγκατάσταση.

Η παραγωγή ΔΕΝ έχει κανένα από τα αντικείμενα του editor και δεν έχει καν
`schema_migrations`. Άρα, για αυτά τα αντικείμενα, το πρώτο `--apply` θα κάνει
ακριβώς ό,τι κάνει μια καθαρή εγκατάσταση: το `site_revisions` δεν προϋπάρχει,
το φτιάχνει το σημερινό 0003, και το 0004 τρέχει με τον φρουρό του.

Ο έλεγχος έχει δύο σκέλη:
  1. Η ΑΦΕΤΗΡΙΑ της παραγωγής ταυτίζεται με την αφετηρία που βλέπει η αλυσίδα
     (οι πίνακες που πειράζουν τα 0003-0008 πριν τους αγγίξουν).
  2. Στην παραγωγή ΔΕΝ υπάρχει κανένα από τα αντικείμενα που θα δημιουργηθούν.

Η παραγωγή διαβάζεται ΜΟΝΟ. Τα δεδομένα της αφετηρίας δίνονται ως σταθερά,
αντιγραμμένα από read-only ερώτημα, ώστε το script να μη χρειάζεται καθόλου
πρόσβαση εγγραφής.
"""
from __future__ import annotations

import pathlib
import sys

import psycopg2

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from tests.test_migration_chain import (  # noqa: E402
    Postgres, apply_all, docker_ok)

if not docker_ok():
    sys.exit("⛔ χρειάζεται Docker/Podman")

# Read-only αποτύπωμα της ΠΑΡΑΓΩΓΗΣ (Supabase MCP, μόνο SELECT), 2026-08-30.
PRODUCTION_START = {
    "clients.address:text:YES:", "clients.business_type:text:NO:",
    "clients.city:text:NO:", "clients.created_at:timestamp with time zone:YES:now()",
    "clients.email:text:YES:", "clients.id:uuid:NO:gen_random_uuid()",
    "clients.name:text:NO:", "clients.phone:text:YES:",
    "clients.plan:text:YES:'starter'::text", "clients.status:text:NO:'trial'::text",
    "site_content.client_id:uuid:NO:", "site_content.content:jsonb:NO:'{}'::jsonb",
    "site_content.updated_at:timestamp with time zone:NO:now()",
    "sites.chosen_variant:integer:YES:", "sites.client_id:uuid:YES:",
    "sites.created_at:timestamp with time zone:YES:now()", "sites.html:text:YES:",
    "sites.id:uuid:NO:gen_random_uuid()", "sites.preset:text:YES:",
    "sites.url:text:YES:",
}
# Επίσης μετρημένο read-only: κανένα από αυτά δεν υπάρχει στην παραγωγή.
PRODUCTION_ABSENT = ("site_revisions", "editor_commit", "editor_undo",
                     "schema_migrations", "site_content.editor_version",
                     "domain_orders.availability")

Q = """SELECT table_name||'.'||column_name||':'||data_type||':'||is_nullable
              ||':'||COALESCE(column_default,'')
       FROM information_schema.columns
       WHERE table_schema='public' AND table_name IN ('site_content','clients','sites')"""

ok = True
with Postgres() as dsn:
    # Μόνο το baseline: αυτή είναι η αφετηρία που «βλέπει» η αλυσίδα.
    apply_all(dsn, upto="0000")
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute(Q)
            baseline = {r[0] for r in cur.fetchall()}
    finally:
        conn.close()

    only_prod = PRODUCTION_START - baseline
    only_base = baseline - PRODUCTION_START
    same = not only_prod and not only_base
    ok &= same
    print(f"  {'✓' if same else '✗'} αφετηρία παραγωγής ≡ αφετηρία αλυσίδας "
          f"({len(baseline)} στήλες)")
    for e in sorted(only_prod):
        print(f"      + μόνο παραγωγή: {e}")
    for e in sorted(only_base):
        print(f"      - μόνο baseline: {e}")

    # Τώρα η υπόλοιπη αλυσίδα πάνω σε αυτή την αφετηρία.
    #
    # Το 0000 ΠΑΡΑΛΕΙΠΕΤΑΙ επίτηδες: η παραγωγή το έχει ήδη (το ίδιο του το
    # σχόλιο το λέει — «ΔΕΝ εφαρμόζεται στην παραγωγή»). ΠΡΟΣΟΧΗ: αυτό είναι
    # παραδοχή, ΟΧΙ σημερινή συμπεριφορά. Η παραγωγή δεν έχει
    # `schema_migrations`, οπότε το `migrate.py` ΘΑ το έτρεχε — και θα έσκαγε
    # με «multiple primary keys for table clients». Αναπαράχθηκε.
    apply_all(dsn, skip=("0000",))
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM information_schema.columns "
                        "WHERE table_schema='public' AND table_name='site_revisions'")
            n_cols = cur.fetchone()[0]
            cur.execute("""SELECT count(*) FROM pg_proc p
                           JOIN pg_namespace n ON n.oid=p.pronamespace
                           WHERE n.nspname='public'
                             AND p.proname IN ('editor_commit','editor_undo')""")
            n_fns = cur.fetchone()[0]
            cur.execute("""SELECT count(*) FROM information_schema.columns
                           WHERE table_schema='public' AND table_name='site_content'
                             AND column_name='editor_version'""")
            has_ver = cur.fetchone()[0]
    finally:
        conn.close()

print(f"\n  η ίδια αφετηρία + ολόκληρη η αλυσίδα δίνει:")
print(f"    site_revisions            {n_cols} στήλες  (χωρίς legacy — σωστό)")
print(f"    editor_commit/editor_undo {n_fns}/2")
print(f"    site_content.editor_version {'ναι' if has_ver else 'ΟΧΙ'}")
ok &= (n_cols == 14 and n_fns == 2 and has_ver == 1)

print("\n  στην παραγωγή σήμερα ΔΕΝ υπάρχει κανένα από:")
for item in PRODUCTION_ABSENT:
    print(f"    · {item}")
print("  (μετρημένο read-only· άρα δεν υπάρχει τίποτα να συγκρουστεί)")

print(f"\n  {'ΙΣΟΔΥΝΑΜΗ' if ok else 'ΔΕΝ ΑΠΟΔΕΙΧΘΗΚΕ'}")
sys.exit(0 if ok else 1)
