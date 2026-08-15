"""Εμπλουτισμός του ευρετηρίου: περιγραφή + πρόταση άδειας ανά template.

Ένα πέρασμα για ΟΛΑ τα verticals. Χωρίς αυτό, η κατανομή σε επάγγελμα γίνεται
από το όνομα — και ονόματα όπως «orbital» ή «vora bold» δεν λένε τίποτα.

Η πρόταση άδειας διαβάζεται από τη σελίδα του ΚΑΘΕ template, όχι από τη γενική
δήλωση του studio: η γενική δήλωση δεν είναι τεκμήριο ανά αρχείο.
"""
from __future__ import annotations

import re
import json
import html
import pathlib
import urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
PATH = pathlib.Path("research/verticals/studio-index.json")
LIC = re.compile(r"(allowed to|licen|commercial|redistribut|credit)", re.I)


def text_of(url: str) -> str:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
            raw = r.read().decode("utf-8", "ignore")
    except Exception:
        return ""
    raw = re.sub(r"(?is)<(script|style|nav|footer)[^>]*>.*?</\1>", " ", raw)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"(?s)<[^>]+>", " ", raw)))


def enrich(row: dict) -> dict:
    t = text_of(row["url"])
    if not t:
        row["http"] = 0
        return row
    row["http"] = 200
    sents = [s.strip() for s in re.split(r"(?<=[.!?]) ", t)]
    row["license"] = next((s for s in sents if LIC.search(s)), "")[:200]
    # Η περιγραφή: οι πρώτες ουσιαστικές προτάσεις που δεν είναι η άδεια.
    desc = [s for s in sents[:40] if 40 < len(s) < 300 and not LIC.search(s)]
    row["desc"] = " ".join(desc[:3])[:420]
    return row


def main() -> None:
    index = json.loads(PATH.read_text(encoding="utf-8"))
    rows = [r for studio in index.values() for r in studio]
    with ThreadPoolExecutor(10) as ex:
        list(ex.map(enrich, rows))
    PATH.write_text(json.dumps(index, indent=1, ensure_ascii=False), encoding="utf-8")
    ok = sum(1 for r in rows if r.get("http") == 200)
    lic = sum(1 for r in rows if r.get("license"))
    print(f"εμπλουτίστηκαν {ok}/{len(rows)} · με δήλωση άδειας: {lic}")


if __name__ == "__main__":
    main()
