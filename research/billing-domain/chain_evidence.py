"""Τεκμήρια της αλυσίδας: ΔΙΑΔΡΟΜΗ Α vs ΔΙΑΔΡΟΜΗ Β vs ΠΡΑΓΜΑΤΙΚΟ STAGING.

Η τρίτη σύγκριση είναι αυτή που δικαιολογεί την ενημέρωση του checksum:
αν το ΔΙΟΡΘΩΜΕΝΟ 0004, ξεκινώντας από την ιστορική μορφή, καταλήγει στο ίδιο
σχήμα με το σημερινό staging, τότε το staging ΔΕΝ χρειάζεται να το ξανατρέξει
— και η ενημέρωση της εγγραφής του είναι καταγραφή γεγονότος, όχι αλλαγή.

Χρήση:  VITRINA_ENV=staging python research/billing-domain/chain_evidence.py
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

import psycopg2
from dotenv import load_dotenv

load_dotenv()
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from tests.test_migration_chain import (  # noqa: E402
    LEGACY_SHAPE, Postgres, apply_all, drop_legacy, introspect, docker_ok)

if not docker_ok():
    sys.exit("⛔ χρειάζεται Docker/Podman")

STAGING = os.environ["DATABASE_URL_STAGING"]

# Το staging έχει και ιστορικά αντικείμενα εκτός αλυσίδας (π.χ. πίνακες που
# προϋπήρχαν του baseline). Η σύγκριση περιορίζεται σε ό,τι ΟΡΙΖΕΙ η αλυσίδα
# του editor και του 0006 — εκεί που ζητείται ισοδυναμία.
SCOPE = ("site_revisions", "site_content", "domain_orders")


def scoped(entries: set[str]) -> set[str]:
    # ΟΙ ΣΥΝΑΡΤΗΣΕΙΣ ΜΠΑΙΝΟΥΝ ΠΑΝΤΑ. Η πρώτη γραφή αυτού του φίλτρου κρατούσε
    # μόνο ό,τι ξεκινά με όνομα πίνακα — οπότε τα `editor_commit(...)` και
    # `editor_undo(...)` κόβονταν και η σύγκριση έδειχνε «0 στοιχεία,
    # ταυτόσημα». Δηλαδή το πιο κρίσιμο κομμάτι δεν ελεγχόταν καθόλου.
    return {e for e in drop_legacy(entries)
            if e.startswith(("editor_commit(", "editor_undo("))
            or any(e.startswith(t + ".") or e.startswith(t + ":")
                   for t in SCOPE)}


print("  χτίζω ΔΙΑΔΡΟΜΗ Α (καθαρή εγκατάσταση)…")
with Postgres() as dsn_a:
    apply_all(dsn_a)
    A = introspect(dsn_a)
    print("  χτίζω ΔΙΑΔΡΟΜΗ Β (ιστορική μορφή staging)…")
    with Postgres() as dsn_b:
        apply_all(dsn_b, after_version={"0003": LEGACY_SHAPE})
        B = introspect(dsn_b)
        S = introspect(STAGING)

report: dict[str, dict] = {}


def compare(label: str, left: dict, right: dict, ln: str, rn: str) -> bool:
    print(f"\n  ── {label} ──")
    clean = True
    for key in sorted(left):
        a, b = scoped(left[key]), scoped(right[key])
        if a == b:
            print(f"    ✓ {key:<14}{len(a)} στοιχεία, ταυτόσημα")
            continue
        clean = False
        print(f"    ✗ {key:<14}μόνο-{ln}={len(a - b)}  μόνο-{rn}={len(b - a)}")
        for e in sorted(a - b)[:5]:
            print(f"        + {ln}: {e[:104]}")
        for e in sorted(b - a)[:5]:
            print(f"        - {rn}: {e[:104]}")
        report.setdefault(label, {})[key] = {
            f"μόνο_{ln}": sorted(a - b), f"μόνο_{rn}": sorted(b - a)}
    return clean


ab = compare("ΔΙΑΔΡΟΜΗ Α  vs  ΔΙΑΔΡΟΜΗ Β", A, B, "Α", "Β")
bs = compare("ΔΙΑΔΡΟΜΗ Β  vs  ΠΡΑΓΜΑΤΙΚΟ STAGING", B, S, "Β", "staging")
as_ = compare("ΔΙΑΔΡΟΜΗ Α  vs  ΠΡΑΓΜΑΤΙΚΟ STAGING", A, S, "Α", "staging")

(HERE / "chain_evidence.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

print("\n  ── σύνοψη ──")
print(f"    Α ≡ Β                : {'ΝΑΙ' if ab else 'ΟΧΙ'}")
print(f"    Β ≡ σημερινό staging : {'ΝΑΙ' if bs else 'ΟΧΙ'}"
      "   ← δικαιολογεί την ενημέρωση checksum")
print(f"    Α ≡ σημερινό staging : {'ΝΑΙ' if as_ else 'ΟΧΙ'}")
sys.exit(0 if (ab and bs and as_) else 1)
