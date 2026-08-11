#!/usr/bin/env python3
"""
Αποδεικνύει ότι το baseline αναπαράγει ΑΚΡΙΒΩΣ την παραγωγή.

    python scripts/verify_baseline.py

Σηκώνει καθαρό Postgres σε container, εφαρμόζει το baseline, παίρνει αποτύπωμα
και το συγκρίνει με το αποτύπωμα της παραγωγής. Έξοδος 0 = ταυτίζονται.

Είναι το gate που κάνει το baseline αξιόπιστο: χωρίς αυτό, «το baseline
αναπαριστά την παραγωγή» είναι ισχυρισμός. Με αυτό, είναι μέτρηση.
Ο container σβήνεται πάντα.
"""
sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")
import psycopg2
from scripts.schema_snapshot import snapshot, diff

name = f"vitrina-baseline-{secrets.token_hex(4)}"
port = 55000 + secrets.randbelow(2000)
pw = secrets.token_hex(12)
print(f"[1] container {name} @ {port}")
subprocess.run(["docker","run","-d","--rm","--name",name,"-e",f"POSTGRES_PASSWORD={pw}",
                "-p",f"{port}:5432","postgres:16-alpine"], capture_output=True, check=True, timeout=600)
dsn = f"postgresql://postgres:{pw}@127.0.0.1:{port}/postgres"
try:
    for _ in range(45):
        try:
            psycopg2.connect(dsn, connect_timeout=3).close(); break
        except Exception:
            time.sleep(1.5)
    print("[2] εφαρμογή baseline")
    sql = io.open("db/migrations/baseline/0000_production_baseline.sql", encoding="utf-8").read()
    conn = psycopg2.connect(dsn); conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.close()
    print("    ✓ εφαρμόστηκε\n[3] αποτύπωμα & σύγκριση με παραγωγή\n")
    snap = snapshot("staging", dsn)
    snap["env"] = "baseline-σε-καθαρή-βάση"
    prod = json.loads(io.open("db/snapshots/production.json", encoding="utf-8").read())
    code = diff(prod, snap)
finally:
    subprocess.run(["docker","rm","-f",name], capture_output=True, timeout=60)
    print(f"\n[4] {name} σβήστηκε")
raise SystemExit(code)
