"""Πλήρες ευρετήριο των δύο αποδεδειγμένων studios, μία φορά για όλα τα verticals.

Γιατί: το fetch ανά vertical ξαναδιαβάζει τις ίδιες σελίδες. Ένα ευρετήριο
χτίζεται μία φορά, αποθηκεύεται, και κάθε vertical διαβάζει από εκεί. Κάθε
εγγραφή έχει ΑΚΡΙΒΕΣ URL — δεν συντίθεται και δεν μαντεύεται.

Έξοδος: research/verticals/studio-index.json
"""
from __future__ import annotations

import re
import json
import pathlib
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
OUT = pathlib.Path("research/verticals/studio-index.json")


def fetch(url: str) -> str:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
            return r.read().decode("utf-8", "ignore")
    except Exception:
        return ""


def templatemo() -> dict[str, str]:
    """Σαρώνει τις σελίδες καταλόγου μέχρι να σταματήσουν να δίνουν νέα."""
    found: dict[str, str] = {}
    for page in range(1, 12):
        url = "https://templatemo.com/" if page == 1 else f"https://templatemo.com/page/{page}"
        html = fetch(url)
        if not html:
            break
        items = re.findall(r'href="(?:https://templatemo\.com)?(/tm-\d+-[a-z0-9-]+)"', html)
        new = {p: "https://templatemo.com" + p for p in set(items) if p not in found}
        if not new:
            break
        found.update(new)
    return found


def tooplate() -> dict[str, str]:
    found: dict[str, str] = {}
    for page in range(1, 20):
        url = ("https://www.tooplate.com/free-templates" if page == 1
               else f"https://www.tooplate.com/free-templates/{page}")
        html = fetch(url)
        if not html:
            break
        items = re.findall(r'href="(?:https://www\.tooplate\.com)?(/view/\d+-[a-z0-9-]+)"', html)
        new = {p: "https://www.tooplate.com" + p for p in set(items) if p not in found}
        if not new:
            break
        found.update(new)
    return found


def main() -> None:
    with ThreadPoolExecutor(2) as ex:
        tm_f = ex.submit(templatemo)
        tp_f = ex.submit(tooplate)
        tm, tp = tm_f.result(), tp_f.result()
    index = {
        "templatemo": [{"slug": p.strip("/"), "url": u,
                        "name": re.sub(r"^tm-\d+-", "", p.strip("/")).replace("-", " ")}
                       for p, u in sorted(tm.items())],
        "tooplate": [{"slug": p.split("/")[-1], "url": u,
                      "name": re.sub(r"^\d+-", "", p.split("/")[-1]).replace("-", " ")}
                     for p, u in sorted(tp.items())],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(index, indent=1), encoding="utf-8")
    for studio, rows in index.items():
        print(f"{studio:12} {len(rows)} templates")


if __name__ == "__main__":
    main()
