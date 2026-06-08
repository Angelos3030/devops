"""
RUNTIME — Onboarding: brand profile → 3 επιλογές site → refinement → deploy.
Token-efficient: Onboarding (Haiku) → Website (Sonnet), απευθείας (όχι coordinator).

  python -m src.onboard_client
"""

import json
from . import config as cfg
from .agent_runtime import client, run_agent, continue_session
from .db import save_brand_profile, save_site
from .deploy import deploy_site


def build_brand(intake: dict) -> dict:
    raw = run_agent(
        cfg.ONBOARDING_AGENT_ID,
        "Φτιάξε brand profile σε ΚΑΘΑΡΟ JSON (χωρίς markdown) για: "
        + json.dumps(intake, ensure_ascii=False),
        title="brand profile",
    )
    # απομόνωσε το JSON (ο agent μπορεί να βάλει κείμενο γύρω)
    start, end = raw.find("{"), raw.rfind("}")
    return json.loads(raw[start:end + 1])


def create_site_options(brand: dict) -> tuple[str, str]:
    """Επιστρέφει (session_id, κείμενο με 3 επιλογές). Κρατά το session για refinement."""
    session = client.beta.sessions.create(
        agent=cfg.WEBSITE_AGENT_ID, environment_id=cfg.ENV_ID,
        title=f"Site — {brand.get('name','')}")
    msg = ("Με βάση αυτό το brand profile: διάλεξε το σωστό preset για τον τύπο μαγαζιού, "
           "φτιάξε 3 ΔΙΑΦΟΡΕΤΙΚΕΣ εκδοχές site (ζεστή / μοντέρνα / τολμηρή), εφάρμοσε SEO. "
           "Γράψε κάθε εκδοχή ως πλήρες static HTML σε ξεχωριστό code block.\n"
           f"Brand profile:\n{json.dumps(brand, ensure_ascii=False)}")
    out = continue_session(session.id, msg)
    return session.id, out


def refine(session_id: str, change: str) -> str:
    """Συνομιλιακή αλλαγή: 'βάλε το μενού πάνω', 'πιο σκούρα χρώματα'..."""
    return continue_session(
        session_id,
        f"Εφάρμοσε αυτή την αλλαγή και δώσε ξανά το πλήρες HTML: {change}")


def onboard(intake: dict, client_id: str) -> dict:
    # 1) Brand
    brand = build_brand(intake)
    save_brand_profile(client_id, brand)
    print("✅ Brand profile έτοιμο")

    # 2) 3 επιλογές site
    session_id, options = create_site_options(brand)
    print("✅ 3 επιλογές site έτοιμες (δείξε στον πελάτη)")

    # 3) Interactive refinement — εδώ μπαίνει το UI/πελάτης.
    #    π.χ.: refine(session_id, "διάλεξα τη 2η, βάλε το μενού πάνω")
    #    Επανέλαβε μέχρι "τέλειο", πάρε το τελικό HTML.

    return {"brand": brand, "session_id": session_id, "options": options}


def finalize_and_deploy(client_id: str, html: str, preset: str, variant: int,
                        slug: str) -> str:
    url = deploy_site(slug, html)
    save_site(client_id, url=url, preset=preset, variant=variant, html=html)
    print("✅ Deployed:", url)
    return url


if __name__ == "__main__":
    demo = {"type": "ταβέρνα", "city": "Θεσσαλονίκη",
            "style": "παραδοσιακό", "name": "Ο Μήτσος"}
    print("Demo onboarding — σύνδεσε agents/DB και κάλεσε onboard(demo, client_id).")
