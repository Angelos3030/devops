"""Ντετερμινιστική απαρίθμηση των vertical-specific καταλόγων των studios.

Γιατί ντετερμινιστικά και όχι DeepSeek: η απαρίθμηση μιας σελίδας tag είναι
μέτρηση, όχι κρίση. Το DeepSeek μένει για ανακάλυψη ΝΕΩΝ οικοσυστημάτων και για
κρίση καταλληλότητας. Έτσι δεν πληρώνουμε tokens για κάτι που ένα regex κάνει
ακριβώς, και δεν υπάρχει περιθώριο να επινοηθεί URL.

Χρήση:  python scripts/studio_tags.py probe <slug> [<slug> ...]
        python scripts/studio_tags.py list  <slug>
"""
from __future__ import annotations

import re
import sys
import json
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
TIMEOUT = 25

STUDIOS = {
    "templatemo": {
        "tag": "https://templatemo.com/tag/{slug}",
        # οι σελίδες templates είναι /tm-<num>-<name>
        "item": re.compile(r'href="(?:https://templatemo\.com)?(/tm-\d+-[a-z0-9-]+)"'),
        "base": "https://templatemo.com",
    },
    "tooplate": {
        "tag": "https://www.tooplate.com/tag/{slug}",
        "item": re.compile(r'href="(?:https://www\.tooplate\.com)?(/view/\d+-[a-z0-9-]+)"'),
        "base": "https://www.tooplate.com",
    },
}


def fetch(url: str) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=TIMEOUT) as r:
            return r.getcode(), r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return 0, ""


def enumerate_tag(studio: str, slug: str) -> tuple[int, list[str]]:
    cfg = STUDIOS[studio]
    code, html = fetch(cfg["tag"].format(slug=slug))
    if code != 200:
        return code, []
    paths = sorted(set(cfg["item"].findall(html)))
    return code, [cfg["base"] + p for p in paths]


def probe(slugs: list[str]) -> dict:
    jobs = [(s, slug) for slug in slugs for s in STUDIOS]
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(lambda a: (a[0], a[1], *enumerate_tag(a[0], a[1])), jobs))
    out: dict[str, dict] = {}
    for studio, slug, code, urls in res:
        out.setdefault(slug, {})[studio] = {"http": code, "n": len(urls), "urls": urls}
    return out


if __name__ == "__main__":
    mode, args = sys.argv[1], sys.argv[2:]
    data = probe(args)
    if mode == "probe":
        for slug, per in data.items():
            bits = " ".join(f"{s}:{v['http']}/{v['n']}" for s, v in per.items())
            total = sum(v["n"] for v in per.values())
            if total:
                print(f"{slug:22} {bits}")
    else:
        print(json.dumps(data, indent=1))
