"""End-to-end-ish test harness for the Vitrina design engine (no external services).

Part A: generator unit checks (offline).
Part B: onboarding + approve endpoints via FastAPI TestClient with an in-memory
        fake DB (no Supabase, no Anthropic).

Run:  python -m scripts.test_design_engine
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

_passed = 0
_failed = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  ✓ {name}")
    else:
        _failed += 1
        print(f"  ✗ {name}  {('-> ' + detail) if detail else ''}")


# ---------------------------------------------------------------------------
# Part A — generator (offline, deterministic)
# ---------------------------------------------------------------------------
def test_generator() -> None:
    print("\n[A] Generator — offline")
    from src import premium_generator as pg

    full = {
        "name": "Κουτράκης", "type": "ξυλουργός", "city": "Γέρακας", "phone": "6956297670",
        "services": [{"name": "Κουζίνες", "description": "στα μέτρα σου"},
                     {"name": "Ντουλάπες", "description": "σε κάθε χώρο"}],
        "gallery": [{"image": "assets/a.jpg", "title": "Έργο 1"},
                    {"image": "assets/b.jpg", "title": "Έργο 2"},
                    {"image": "assets/c.jpg", "title": "Έργο 3"}],
    }
    variants = pg.generate_variants(full)
    check("returns all layouts", set(variants) == set(pg.LAYOUTS), str(list(variants)))
    for layout, html in variants.items():
        check(f"[{layout}] no unresolved {{{{ }}}}", "{{" not in html)
        check(f"[{layout}] no loop markers", "<!--#" not in html and "<!--/" not in html)
        check(f"[{layout}] has viewport meta", 'name="viewport"' in html)
        check(f"[{layout}] responsive @media", "@media" in html)
        check(f"[{layout}] phone tel link", "tel:+306956297670" in html)
        check(f"[{layout}] service present", "Κουζίνες" in html)
        check(f"[{layout}] gallery image present", "assets/a.jpg" in html)
        check(f"[{layout}] well-formed (parses)", _parses(html))

    # edge: no photos, no services, missing phone -> fallback hero + defaults, still clean
    bare = {"name": "Οδοντιατρείο Χ", "type": "οδοντίατρος", "city": "Χαλάνδρι"}
    bv = pg.generate_variants(bare)
    for layout, html in bv.items():
        check(f"[bare/{layout}] clean", "{{" not in html)
        check(f"[bare/{layout}] fallback hero (unsplash)", "unsplash.com" in html)
    check("dentist -> atelier", pg.recommend_layout(bare) == "atelier", pg.recommend_layout(bare))
    check("taverna -> studio", pg.recommend_layout({"type": "ταβέρνα"}) == "studio")
    cafe_intake = {
        "type": "Άλλο",
        "description": "Έχω καφέ και παραδοσιακό φούρνο στο Ναύπλιο με specialty coffee και γλυκά",
    }
    cafe_content = pg.normalize(cafe_intake)
    cafe_services = " ".join(item["title"] for item in cafe_content["services"])
    check("cafe -> cafe content profile", pg._profession(cafe_intake) == "cafe")
    check("cafe content includes coffee", "Specialty coffee" in cafe_services, cafe_services)
    check("cafe content excludes grill", "Σχάρα" not in cafe_services, cafe_services)
    check("taverna keeps food content", pg._profession({"type": "ταβέρνα"}) == "food")
    nail_intake = {"description": "Έχω νυχάδικο στην Αθήνα"}
    check("nail salon -> nail-specific copy", pg._profession(nail_intake) == "nails")
    check("nail salon -> beauty vertical", pg._vertical(nail_intake) == "beauty")
    check("nail salon -> beauty atelier first", pg.recommend_templates(nail_intake)[0] == "beauty-atelier")
    themed = pg.normalize({"type": "καφέ", "palette": "forest", "font_pair": "modern"})
    check("palette reaches template data", themed["PALETTE"] == "forest", themed["PALETTE"])
    check("font pair reaches template data", themed["FONT_PAIR"] == "modern", themed["FONT_PAIR"])

    # edge: HTML escaping of special chars in name
    danger = {"name": "Café & Σία <b>x</b>", "type": "καφέ", "city": "Αθήνα", "phone": "2100000000"}
    dv = pg.generate(danger, "commerce")
    check("escapes < in name", "<b>x</b>" not in dv)
    check("escapes & in name", "&amp;" in dv)


def _parses(html: str) -> bool:
    from html.parser import HTMLParser
    try:
        HTMLParser().feed(html)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Part B — endpoints with in-memory fake DB (no Supabase / no Anthropic)
# ---------------------------------------------------------------------------
class FakeDB:
    def __init__(self) -> None:
        self.clients: dict[str, dict] = {}
        self.variants: dict[tuple[str, str], dict] = {}
        self.assets: dict[str, list] = {}
        self._n = 0

    def create_client(self, intake: dict) -> str:
        self._n += 1
        cid = f"client-{self._n}"
        self.clients[cid] = {"id": cid, **intake, "selected_layout": None}
        return cid

    def get_client(self, client_id: str):
        return self.clients.get(client_id)

    def get_site_content(self, client_id: str) -> dict:
        return self.clients.get(client_id, {}).get("site_content", {})

    def save_site_content(self, client_id: str, content: dict) -> None:
        self.clients.setdefault(client_id, {})["site_content"] = content

    def get_client_assets(self, client_id: str, usage=None) -> list:
        return self.assets.get(client_id, [])

    def save_site_variant(self, client_id, layout, html, recommended=False) -> None:
        self.variants[(client_id, layout)] = {
            "layout": layout, "html": html, "recommended": recommended, "status": "preview"}

    def get_site_variant(self, client_id, layout):
        return self.variants.get((client_id, layout))

    def list_site_variants(self, client_id) -> list:
        return [{"layout": v["layout"], "recommended": v["recommended"], "status": v["status"]}
                for (c, _), v in self.variants.items() if c == client_id]

    def set_selected_design(self, client_id, layout) -> None:
        self.clients[client_id]["selected_layout"] = layout
        if (client_id, layout) in self.variants:
            self.variants[(client_id, layout)]["status"] = "selected"

    def get_selected_design(self, client_id):
        return self.clients.get(client_id, {}).get("selected_layout")

    def get_live_site(self, client_id):
        return self.clients.get(client_id, {}).get("live_url")

    def save_site(self, client_id, url, preset, variant, html):
        self.clients.setdefault(client_id, {})["live_url"] = url


def test_endpoints() -> None:
    print("\n[B] Endpoints — TestClient + fake DB (no Supabase/Anthropic)")
    from src import config as cfg
    cfg.ANTHROPIC_API_KEY = ""            # force site_copy no-op (offline, fast)
    cfg.AI_API_KEY = ""
    cfg.AI_BASE_URL = ""
    from src.premium_generator import LAYOUTS
    n = len(LAYOUTS)
    from src import meta_oauth
    fake = FakeDB()
    meta_oauth.db = fake                  # inject fake db into the app module
    from fastapi.testclient import TestClient
    tc = TestClient(meta_oauth.app)

    # onboard -> triggers background generation of 3 variants
    r = tc.post("/onboard", json={"name": "Ταβέρνα Ο Μήτσος", "type": "ταβέρνα",
                                  "city": "Θεσσαλονίκη", "phone": "2310000000",
                                  "description": "Οικογενειακή ταβέρνα", "style": "ζεστό"})
    check("POST /onboard 200", r.status_code == 200, r.text)
    cid = r.json().get("client_id")
    check("onboard returns client_id", bool(cid))
    check("onboard persists matching description",
          fake.get_site_content(cid).get("description") == "Οικογενειακή ταβέρνα")
    check(f"background generated {n} variants", len(fake.list_site_variants(cid)) == n,
          str(fake.list_site_variants(cid)))

    # designs list
    r = tc.get(f"/clients/{cid}/designs")
    check("GET /designs 200", r.status_code == 200)
    body = r.json()
    check(f"designs: {n} variants", len(body["variants"]) == n)
    check("designs: 7 curated React templates", len(body["templates"]) == 7,
          str(body.get("templates")))
    check("designs: one recommended", sum(v["recommended"] for v in body["variants"]) == 1)
    check("designs: none selected yet", body["selected"] is None)

    # preview
    r = tc.get(f"/clients/{cid}/preview/studio")
    check("GET /preview/studio 200 HTML", r.status_code == 200 and "<!DOCTYPE html>" in r.text)
    r = tc.get(f"/clients/{cid}/preview/nope")
    check("GET /preview/<missing> 404", r.status_code == 404)

    # approve
    r = tc.post(f"/clients/{cid}/select-design", json={"layout": "commerce"})
    check("POST /select-design 200", r.status_code == 200 and r.json().get("selected") == "commerce")
    r = tc.get(f"/clients/{cid}/designs")
    check("after approve: selected=commerce", r.json()["selected"] == "commerce")
    r = tc.post(f"/clients/{cid}/select-design", json={"layout": "bogus"})
    check("POST /select-design invalid -> 400", r.status_code == 400)


def main() -> int:
    print("=" * 60)
    print("Vitrina Design Engine — test harness")
    print("=" * 60)
    test_generator()
    test_endpoints()
    print("\n" + "=" * 60)
    print(f"RESULT: {_passed} passed, {_failed} failed")
    print("=" * 60)
    return 1 if _failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
