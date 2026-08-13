# -*- coding: utf-8 -*-
"""A/B: τι αλλάζει αν ο πελάτης δώσει ΑΛΗΘΙΝΕΣ φωτογραφίες.

A. Καμία φωτογραφία → η σημασιολογία επιβάλλει τυπογραφική παρουσίαση στις
   ενότητες ταυτότητας. Καμία δανεική εικόνα δεν παριστάνει χώρο/δουλειά/πρόσωπο.
B. Συνθετικά «αληθινά» υλικά, δηλωμένα ανά κλάση (REAL_WORK/REAL_SPACE/
   REAL_OWNER_PERSON), όπως θα τα ανέβαζε ο πελάτης από τη ροή του staging.

Το ίδιο pipeline παραγωγής με πριν· αλλάζει ΜΟΝΟ το υλικό και η εφαρμογή του
συμβολαίου `src/media_semantics.py`. Καμία αλλαγή σε production κώδικα.
"""
from __future__ import annotations

import html as _html
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src import media_semantics as ms  # noqa: E402
from src import premium_generator as pg  # noqa: E402
from src import quick_start as qs  # noqa: E402
from src import site_copy  # noqa: E402

_spec = importlib.util.spec_from_file_location("bench_businesses", Path(__file__).with_name("businesses.py"))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
BUSINESSES = _mod.BUSINESSES

OUT = ROOT / "sites" / "artifacts" / "benchmark"
U = "https://images.unsplash.com/photo-{}?auto=format&fit=crop&w=1400&q=80"

# Συνθετικά «αληθινά» υλικά ανά επιχείρηση: ό,τι θα ανέβαζε ένας πελάτης που
# βγάζει 4-6 φωτογραφίες με το κινητό του. Δηλωμένη κλάση σε κάθε μία.
REAL_FIXTURES: dict[str, list[tuple[str, str, str]]] = {
    "bench-01-plumber": [
        ("1607472586893-edb57bdc0e39", ms.REAL_WORK, "Αλλαγή σωληνώσεων"),
        ("1585704032915-c3400ca199e7", ms.REAL_WORK, "Τοποθέτηση θερμοσίφωνα"),
        ("1621905252507-b35492cc74b4", ms.REAL_WORK, "Επισκευή μπάνιου"),
        ("1504148455328-c376907d081c", ms.REAL_SPACE, "Το συνεργείο μας"),
    ],
    "bench-02-electrician": [
        ("1621905251189-08b45d6a269e", ms.REAL_WORK, "Ηλεκτρολογικές εργασίες"),
        ("1558618666-fcd25c85cd64", ms.REAL_WORK, "Νέος πίνακας"),
        ("1565608087341-404b25492fee", ms.REAL_WORK, "Φωτισμός καταστήματος"),
        ("1581092160562-40aa08e78837", ms.REAL_SPACE, "Στο συνεργείο"),
    ],
    "bench-03-accountant": [
        ("1573496359142-b8d87734a5a2", ms.REAL_OWNER_PERSON, "Γεωργία Στεφανίδου"),
        ("1497366754035-f200968a6e72", ms.REAL_SPACE, "Το γραφείο"),
        ("1450101499163-c8848c66ca85", ms.REAL_WORK, "Στη δουλειά"),
    ],
    "bench-04-dietitian": [
        ("1594824476967-48c8b964273f", ms.REAL_OWNER_PERSON, "Νίκη Αρβανίτη"),
        ("1490645935967-10de6ba17061", ms.REAL_WORK, "Πρόγραμμα διατροφής"),
        ("1505576399279-565b52d4ac71", ms.REAL_SPACE, "Ο χώρος συνεδριών"),
    ],
    "bench-05-salon": [
        ("1560066984-138dadb4c035", ms.REAL_SPACE, "Στον χώρο μας"),
        ("1522337360788-8b13dee7a37e", ms.REAL_WORK, "Κούρεμα"),
        ("1595476108010-b4d1f102b1b1", ms.REAL_WORK, "Βαφή"),
        ("1521590832167-7bcbfaa6381f", ms.REAL_WORK, "Χτένισμα"),
        ("1502767089025-6572583495b0", ms.REAL_OWNER_PERSON, "Η Ελένη"),
    ],
    "bench-06-bakery": [
        ("1509440159596-0249088772ff", ms.REAL_WORK, "Ψωμί με προζύμι"),
        ("1608198093002-ad4e005484ec", ms.REAL_SPACE, "Ο ξυλόφουρνος"),
        ("1587248720327-8eb72564be1e", ms.REAL_WORK, "Χειροποίητες πίτες"),
        ("1486427944299-d1955d23e34d", ms.REAL_WORK, "Γλυκά ταψιού"),
        ("1517433670267-08bbd4be890f", ms.REAL_WORK, "Κουλούρια"),
    ],
    "bench-07-taverna": [
        ("1414235077428-338989a2e8c0", ms.REAL_SPACE, "Στην ταβέρνα"),
        ("1555939594-58d7cb561ad1", ms.REAL_WORK, "Ψητά στα κάρβουνα"),
        ("1466637574441-749b8f19452f", ms.REAL_WORK, "Μεζέδες"),
        ("1544025162-d76694265947", ms.REAL_WORK, "Φρέσκο ψάρι"),
    ],
    "bench-08-dentist": [
        ("1588776814546-1ffcf47267a5", ms.REAL_SPACE, "Το ιατρείο"),
        ("1606811841689-23dfddce3e95", ms.REAL_SPACE, "Η αίθουσα αναμονής"),
        ("1609840114035-3c981b782dfe", ms.REAL_WORK, "Εξοπλισμός"),
    ],
    "bench-09-realestate": [
        ("1512917774080-9991f1c4c750", ms.REAL_WORK, "Κατοικία προς πώληση"),
        ("1560448204-e02f11c3d0e2", ms.REAL_WORK, "Διαμέρισμα στον Βόλο"),
        ("1449844908441-8829872d2607", ms.REAL_WORK, "Μονοκατοικία στο Πήλιο"),
        ("1497366811353-6870744d04b2", ms.REAL_SPACE, "Το γραφείο μας"),
    ],
    "bench-10-petgroomer": [
        ("1601758228041-f3b2795255f1", ms.REAL_WORK, "Μετά το κούρεμα"),
        ("1583337130417-3346a1be7dee", ms.REAL_WORK, "Στο μπάνιο"),
        ("1615751072497-5f5169febe17", ms.REAL_SPACE, "Ο χώρος μας"),
        ("1518717758536-85ae29035b6d", ms.REAL_WORK, "Ήρεμη διαδικασία"),
    ],
}

# Οι ενότητες που εμφανίζει ένα τυπικό site μας.
SECTIONS = ("hero", "work", "space", "portrait", "product")


def _unesc(v):
    if isinstance(v, str):
        return _html.unescape(v)
    if isinstance(v, list):
        return [_unesc(x) for x in v]
    if isinstance(v, dict):
        return {k: _unesc(x) for k, x in v.items()}
    return v


def build(entry: dict, mode: str) -> dict:
    bid, prompt, extra = entry["id"], entry["prompt"], entry["intake"]

    assets: list[ms.Asset] = []
    if mode == "B":
        assets = [ms.Asset(U.format(pid), cls, title)
                  for pid, cls, title in REAL_FIXTURES.get(bid, [])]

    plan = ms.plan(assets, SECTIONS)

    parsed = qs.parse(prompt)
    parsed.pop("services", None)
    intake = {**parsed, **extra}
    intake["description"] = extra.get("description") or prompt
    # ΜΟΝΟ πραγματικά υλικά μπαίνουν στο gallery. Στο A δεν υπάρχει κανένα, οπότε
    # το site πρέπει να σταθεί τυπογραφικά — αυτό ακριβώς μετράμε.
    intake["gallery"] = [a.to_dict() for a in assets]
    portrait = next((a for a in assets if a.media_class == ms.REAL_OWNER_PERSON), None)
    if portrait:
        intake["hero_image"] = portrait.url if plan["typographic"] is False else intake.get("hero_image", "")

    intake = site_copy.enrich_with_copy(intake)
    ranked = pg.recommend_templates(intake)
    chosen = ranked[0]
    ctx = pg.normalize(intake)
    data = {k: _unesc(v) for k, v in ctx.items() if not k.startswith("_")}

    # ΕΠΙΒΟΛΗ ΣΥΜΒΟΛΑΙΟΥ: χωρίς πραγματικό υλικό, καμία ενότητα ταυτότητας δεν
    # γεμίζει με δανεικό. Το `normalize` βάζει πάντα stock hero — επιτρεπτό ως
    # ατμόσφαιρα, αλλά ΟΧΙ ως «η δουλειά μου».
    if plan["typographic"]:
        data["gallery"] = []
        data["MEDIA_ILLUSTRATIVE"] = True
        data["HERO_IS_REAL"] = False
        # Τίτλοι που ισχυρίζονται ταυτότητα γίνονται ουδέτεροι.
        data["GALLERY_TITLE"] = ms.NEUTRAL_TITLE["work"]
        data["MEDIA_POLICY"] = "real-only"
    else:
        data["HERO_IS_REAL"] = True
        data["MEDIA_ILLUSTRATIVE"] = False
        data["MEDIA_POLICY"] = "real-only"
        data["GALLERY_TITLE"] = ms.title_for("work", ms.select("work", assets)) or "Η δουλειά μας"

    payload = {"layout": chosen, "layouts": list(pg.LAYOUTS), "data": data}
    (OUT / f"ab{mode}-{bid}.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return {"id": bid, "mode": mode, "theme": chosen, "real_assets": plan["real_count"],
            "typographic": plan["typographic"], "identity_filled": plan["identity_filled"],
            "gallery": len(data.get("gallery") or [])}


def main() -> None:
    rows = []
    for mode in ("A", "B"):
        for entry in BUSINESSES:
            r = build(entry, mode)
            rows.append(r)
            print(json.dumps(r, ensure_ascii=False))
    (OUT / "ab-log.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
