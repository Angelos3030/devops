# Runbook: πρώτη μετανάστευση της παραγωγής

**Κατάσταση: ΔΕΝ ΕΧΕΙ ΕΚΤΕΛΕΣΤΕΙ.** Το κείμενο περιγράφει τι θα γίνει· καμία
εντολή του δεν έχει τρέξει στην παραγωγή.

Η παραγωγή έχει τους πίνακες του `0000` αλλά **δεν έχει `schema_migrations`**.
Δεν έχει επίσης κανένα αντικείμενο του editor. Ένα σκέτο `--apply` θα
εκτελούσε το `0000` πάνω σε υπάρχοντες πίνακες και θα σταματούσε με
`multiple primary keys for table "clients"`. Γι' αυτό υπάρχει το βήμα Δ.

Ο κύκλος διαρκεί ~10 λεπτά. Δεν εκτελείται με ανοιχτή κίνηση πελατών αν
μπορεί να αποφευχθεί.

---

## Α. Έλεγχοι πριν από οτιδήποτε — ΜΟΝΟ ΑΝΑΓΝΩΣΗ

Καμία εντολή αυτής της ενότητας δεν γράφει.

### Α1. Είμαι όντως στην παραγωγή;

```bash
VITRINA_ENV=production python -c "from src import env; print(env.banner())"
```

Αναμένεται: `VITRINA_ENV=production · βάση: production`. Αν λέει `staging`,
**σταμάτα** — ο υπόλοιπος runbook θα μετρούσε λάθος βάση.

### Α2. Η βάση είναι πράγματι εκτός διαχείρισης;

```sql
SELECT to_regclass('public.schema_migrations');   -- αναμένεται: NULL
SELECT to_regclass('public.site_revisions');      -- αναμένεται: NULL
SELECT count(*) FROM information_schema.columns
 WHERE table_schema='public' AND table_name='site_content'
   AND column_name='editor_version';              -- αναμένεται: 0
```

Αν το `schema_migrations` **υπάρχει**, αυτός ο runbook δεν ισχύει: η βάση είναι
ήδη υπό διαχείριση και το βήμα Δ θα την απορρίψει (σωστά). Πήγαινε στο Ζ.

Αν το `site_revisions` **υπάρχει** ενώ το `schema_migrations` όχι, **σταμάτα**:
κάποιος έτρεξε SQL χειροκίνητα και η κατάσταση δεν είναι αυτή που δοκιμάστηκε.

### Α3. Πόσα δεδομένα κινδυνεύουν;

```sql
SELECT 'clients' t, count(*) FROM clients
UNION ALL SELECT 'sites', count(*) FROM sites
UNION ALL SELECT 'site_content', count(*) FROM site_content
UNION ALL SELECT 'subscriptions', count(*) FROM subscriptions
UNION ALL SELECT 'domains', count(*) FROM domains
UNION ALL SELECT 'domain_orders', count(*) FROM domain_orders
UNION ALL SELECT 'posts', count(*) FROM posts;
```

**Κράτα αυτόν τον πίνακα.** Το βήμα Ζ τον συγκρίνει αριθμό προς αριθμό.

### Α4. Το repo είναι σε γνωστή κατάσταση;

```bash
git status --porcelain db/migrations/ scripts/migrate.py db/baseline_fingerprint.json
python -m unittest tests.test_migration_chain tests.test_baseline_adoption
```

Και τα δύο πρέπει να είναι καθαρά/πράσινα. Αν κάποιο test κάνει **SKIP** επειδή
λείπει Docker, **σταμάτα**: SKIP δεν είναι απόδειξη.

---

## Β. Αντίγραφο ασφαλείας — ΥΠΟΧΡΕΩΤΙΚΟ

**Χωρίς επαληθευμένο αντίγραφο δεν προχωράει τίποτα.** Δεν υπάρχει «undo» για
migration που έτρεξε στη μισή του διαδρομή.

1. Supabase → Database → Backups → **Point-in-time recovery**: επιβεβαίωσε ότι
   είναι ενεργό και σημείωσε τη **χρονική στιγμή** έναρξης (`T0`, σε UTC).
2. Τράβα και δικό σου λογικό αντίγραφο, ανεξάρτητο από τον πάροχο:
   ```bash
   pg_dump "$DATABASE_URL_PRODUCTION" --format=custom --no-owner \
     --file="backup-pre-migration-$(date -u +%Y%m%dT%H%M%SZ).dump"
   ```
3. **Επαλήθευσε ότι το αντίγραφο διαβάζεται** — ένα dump που δεν άνοιξε ποτέ
   δεν είναι αντίγραφο:
   ```bash
   pg_restore --list backup-pre-migration-*.dump | head -40
   ```
4. Σημείωσε πού είναι αποθηκευμένο και ποιος έχει πρόσβαση.

---

## Γ. Επαλήθευση αποτυπώματος — ΜΟΝΟ ΑΝΑΓΝΩΣΗ

Το βήμα Δ κάνει την ίδια επαλήθευση μόνο του και **σταματά κλειστά** αν
αποτύχει. Το τρέχουμε ξεχωριστά πρώτα, ώστε μια αποτυχία να μη μοιάζει με
αποτυχία εγγραφής.

```bash
python -c "
import json,os,psycopg2
fp=json.load(open('db/baseline_fingerprint.json',encoding='utf-8'))
c=psycopg2.connect(os.environ['DATABASE_URL_PRODUCTION']); cur=c.cursor()
cur.execute('''SELECT table_name||'.'||column_name, data_type||'|'||is_nullable
               FROM information_schema.columns WHERE table_schema='public' ''')
cols=dict(cur.fetchall())
cur.execute('''SELECT rel.relname||':'||con.conname, pg_get_constraintdef(con.oid)
               FROM pg_constraint con JOIN pg_class rel ON rel.oid=con.conrelid
               JOIN pg_namespace n ON n.oid=rel.relnamespace
               WHERE n.nspname='public' AND con.contype IN ('p','u','f')''')
cons=dict(cur.fetchall()); c.close()
miss=[k for k,v in fp['columns'].items() if cols.get(k)!=v]
for g in ('primary_keys','unique_constraints','foreign_keys'):
    miss+= [k for k,v in fp[g].items() if cons.get(k)!=v]
print('ΑΠΟΚΛΙΣΕΙΣ:', len(miss))
[print('  ·',m) for m in miss[:20]]
"
```

**Αναμένεται `ΑΠΟΚΛΙΣΕΙΣ: 0`.** Οτιδήποτε άλλο → **σταμάτα** και πήγαινε στο Θ.

---

## Δ. Υιοθέτηση baseline

```bash
VITRINA_ENV=production python scripts/migrate.py --adopt-baseline 0000
```

**Τι κάνει:** επαληθεύει ξανά το αποτύπωμα, φτιάχνει το `schema_migrations` και
γράφει **μία** γραμμή για το `0000`. **Δεν εκτελεί το SQL του `0000`.**

**Τι πρέπει να δεις:**

```
✅ Υιοθετήθηκε το baseline 0000 — ΧΩΡΙΣ εκτέλεση SQL.

   αρχείο            0000_production_baseline.sql
   checksum          baa936fbea60c179
   επαληθεύτηκαν     12 πίνακες, 95 στήλες, 12 PK, 4 unique, 12 FK
```

Οτιδήποτε ξεκινά με `⛔` σημαίνει ότι **δεν γράφτηκε τίποτα**. Πήγαινε στο Θ.

---

## Ε. Επαλήθευση κατάστασης — ΜΟΝΟ ΑΝΑΓΝΩΣΗ

```bash
VITRINA_ENV=production python scripts/migrate.py --status
```

**Πρέπει να δεις:**

- `✓ 0000_production_baseline.sql` — υιοθετημένο
- `⊘ 0001_agency_kernel.sql (staging-only — δεν αφορά την παραγωγή)`
- `· 0002 … 0008 (εκκρεμεί)` — επτά εκκρεμή
- **καμία** γραμμή `⚠️ ΑΛΛΑΞΕ`

Αν εμφανιστεί `⚠️ ΑΛΛΑΞΕ`, **σταμάτα**: το repo δεν είναι στην έκδοση που
δοκιμάστηκε.

---

## ΣΤ. Εφαρμογή

```bash
VITRINA_ENV=production python scripts/migrate.py --apply --confirm-production
```

**Πρέπει να δεις** `✓` για 0002 έως 0008 και `✅ Εφαρμόστηκαν 7.`

**Το `0000` ΔΕΝ πρέπει να εμφανιστεί στο τμήμα εκτέλεσης** — μόνο στη λίστα
κατάστασης από πάνω, με `✓`.

Κάθε migration τρέχει σε δική του συναλλαγή· αποτυχία κάνει rollback **αυτού**
και σταματά τα υπόλοιπα. Αν δεις `⛔ Σταμάτησα`, πήγαινε στο Θ.

---

## Ζ. Επαλήθευση μετά — ΜΟΝΟ ΑΝΑΓΝΩΣΗ

### Ζ1. Ιστορικό
```sql
SELECT version, filename, checksum, applied_at
FROM schema_migrations ORDER BY version;
```
Αναμένονται **οκτώ** γραμμές: 0000 (υιοθετημένο) και 0002-0008. Το 0001 λείπει
σωστά — είναι `staging-only`.

### Ζ2. Τα δεδομένα επέζησαν
Τρέξε **ξανά** το Α3 και σύγκρινε αριθμό προς αριθμό. **Κάθε διαφορά είναι λόγος
για το Θ.**

### Ζ3. Το σχήμα του editor
```sql
SELECT count(*) FROM information_schema.columns
 WHERE table_schema='public' AND table_name='site_revisions';        -- 14
SELECT count(*) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
 WHERE n.nspname='public' AND p.proname IN ('editor_commit','editor_undo'); -- 2
SELECT data_type, is_nullable FROM information_schema.columns
 WHERE table_schema='public' AND table_name='site_content'
   AND column_name='editor_version';                                 -- bigint, NO
SELECT count(*) FROM information_schema.columns
 WHERE table_schema='public' AND table_name='site_revisions'
   AND column_name IN ('timestamp','publish_status');                -- 0
```

### Ζ4. Δικαιώματα
```sql
SELECT t.table_name FROM information_schema.tables t
WHERE t.table_schema='public' AND t.table_type='BASE TABLE'
  AND 0=(SELECT count(*) FROM information_schema.role_table_grants g
         WHERE g.table_schema='public' AND g.table_name=t.table_name
           AND g.grantee='service_role');
```
Αναμένεται: **καμία γραμμή**.

### Ζ5. RLS
```sql
SELECT relname FROM pg_class rel JOIN pg_namespace n ON n.oid=rel.relnamespace
WHERE n.nspname='public' AND rel.relkind='r' AND NOT rel.relrowsecurity;
```
Αναμένεται: **καμία γραμμή**.

### Ζ6. Η εφαρμογή δουλεύει
Άνοιξε το dashboard ενός **υπαρκτού** πελάτη, κάνε **μία** αλλαγή με τον chat
editor, δες το preview, πάτα **Έγκριση** και μετά **Αναίρεση**. Επαλήθευσε ότι
το δημοσιευμένο site δεν άλλαξε.

---

## Η. Πότε ΣΤΑΜΑΤΑΜΕ

Σταμάτα αμέσως, χωρίς να δοκιμάσεις «άλλη μια φορά», αν:

| σημάδι | τι σημαίνει |
|---|---|
| Α1 δεν λέει `production` | λάθος βάση |
| Α2: υπάρχει `schema_migrations` ή `site_revisions` | η βάση δεν είναι στην κατάσταση που δοκιμάστηκε |
| Α4: κάποιο test **SKIP** | δεν υπάρχει απόδειξη, μόνο απουσία αποτυχίας |
| Β3: το dump δεν διαβάζεται | δεν υπάρχει δίχτυ |
| Γ: αποκλίσεις > 0 | το σχήμα δεν είναι το baseline |
| Δ: μήνυμα `⛔` | η υιοθέτηση αρνήθηκε — **δεν γράφτηκε τίποτα** |
| Ε: γραμμή `⚠️ ΑΛΛΑΞΕ` | το repo διαφέρει από ό,τι δοκιμάστηκε |
| ΣΤ: `⛔ Σταμάτησα` | migration απέτυχε στη μέση |
| Ζ2: αλλαγμένα πλήθη γραμμών | χάθηκαν ή προστέθηκαν δεδομένα |

---

## Θ. Ανάκτηση — τι σημαίνει πραγματικά

**Δεν υπάρχει «rollback των migrations».** Δεν γράφτηκαν down-migrations, και
δεν πρέπει να γραφτούν βιαστικά: μια αντίστροφη `DROP` σε λάθος στιγμή
καταστρέφει δεδομένα που το πρόβλημα δεν είχε ακόμη αγγίξει.

Τρεις καταστάσεις, τρεις διαφορετικές απαντήσεις:

### Θ1. Αποτυχία **πριν** από το βήμα Δ
Δεν γράφτηκε τίποτα. Διόρθωσε την αιτία και ξεκίνα από το Α. **Καμία ανάκτηση.**

### Θ2. Το βήμα Δ **αρνήθηκε**
Η υιοθέτηση φτιάχνει το `schema_migrations` **μόνο αφού** περάσει η επαλήθευση.
Άρνηση σημαίνει ότι η βάση είναι ανέπαφη. **Καμία ανάκτηση.**

Αν παρ' όλα αυτά υπάρχει άδειο `schema_migrations`, κάποιος έτρεξε κάτι άλλο —
**σταμάτα και ρώτα**, μη σβήσεις πίνακα στην παραγωγή αυτοσχεδιάζοντας.

### Θ3. Αποτυχία **μέσα** στο βήμα ΣΤ
Το migration που απέτυχε έκανε rollback μόνο του· τα **προηγούμενα έχουν ήδη
δεσμευτεί**. Η βάση είναι σε ενδιάμεση, γνωστή κατάσταση.

**Μην τρέξεις ξανά `--apply` για να «περάσει».** Πρώτα:

1. Κατάγραψε το ακριβές μήνυμα και ποιο migration απέτυχε.
2. `SELECT version FROM schema_migrations ORDER BY version;` — τι πρόλαβε.
3. Αναπαρήγαγε **τοπικά**: στήσε βάση σε σχήμα παραγωγής, φτάσε στο ίδιο σημείο,
   αναπαρήγαγε την αποτυχία. Χωρίς αναπαραγωγή δεν υπάρχει διόρθωση, υπάρχει
   εικασία.
4. Διόρθωσε με **νέο** migration. Ποτέ με επεξεργασία εφαρμοσμένου.

**Επαναφορά από αντίγραφο** χρειάζεται **μόνο** αν ισχύει ένα από:

- το Ζ2 δείχνει χαμένα ή αλλοιωμένα δεδομένα πελατών,
- η εφαρμογή δεν λειτουργεί και η αιτία δεν εντοπίζεται σε λογικό χρόνο,
- η βάση είναι σε κατάσταση που δεν εξηγείται από το ιστορικό.

Η επαναφορά είναι **καταστροφική για ό,τι γράφτηκε μετά το `T0`**: point-in-time
restore σβήνει κάθε εγγραφή πελάτη από εκείνη τη στιγμή. Γι' αυτό είναι τελευταία
επιλογή και όχι πρώτη αντίδραση — και γι' αυτό ο κύκλος γίνεται με όσο το δυνατόν
λιγότερη κίνηση.

Αν αποφασιστεί: Supabase → Database → Backups → PITR → `T0`. Μετά την επαναφορά η
βάση δεν έχει ξανά `schema_migrations` και ο runbook ξεκινά από το Α.

---

## Τι έχει ήδη αποδειχθεί

Πριν γραφτεί αυτό το κείμενο, ολόκληρη η ροή Δ→Ε→ΣΤ→Ζ εκτελέστηκε σε
**αναλώσιμη βάση σε σχήμα παραγωγής**, με συνθετικές γραμμές μέσα:

- η βάση χτίστηκε από το `0000` και επαληθεύτηκε ότι ταιριάζει με το read-only
  αποτύπωμα της παραγωγής,
- αναπαράχθηκε ότι η εκτέλεση του `0000` **σκάει** εκεί,
- η υιοθέτηση πέρασε, το `--apply` έτρεξε 0002-0008 και **ποτέ** το `0000`,
- οι προϋπάρχουσες γραμμές έμειναν **byte-ίδιες**, τα πλήθη αμετάβλητα,
- ο editor δούλεψε πάνω σε πελάτη που υπήρχε **πριν** τη μετανάστευση,
- 12 επικίνδυνες περιπτώσεις υιοθέτησης σταμάτησαν κλειστά, χωρίς να γράψουν.

`tests/test_baseline_adoption.py` (28 tests) · `tests/test_migration_chain.py`
(18 tests).
