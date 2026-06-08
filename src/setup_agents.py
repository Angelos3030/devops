"""
ONE-TIME SETUP — Δημιουργία agents (token-efficient). Τρέξε ΜΙΑ φορά.

Ιεραρχία για λιγότερα tokens (δες docs/10-TOKEN-EFFICIENCY.md):
  - ΟΧΙ runtime coordinator. Το backend (κώδικας) καλεί απευθείας τον σωστό agent.
  - Brand + Captions → Haiku (φθηνό). Website → Sonnet. Opus σχεδόν ποτέ.

  pip install -r requirements.txt
  python -m src.setup_agents
"""

import anthropic
from . import config as cfg

client = anthropic.Anthropic(api_key=cfg.ANTHROPIC_API_KEY)

SK = cfg.SKILL_IDS


def _skill(name: str) -> dict:
    sid = SK.get(name)
    if not sid:
        raise RuntimeError(f"Λείπει skill_id για {name} — τρέξε upload_skills.py πρώτα.")
    return {"type": "custom", "skill_id": sid, "version": "latest"}


def main() -> None:
    # 1) Environment (cloud). allow_mcp_servers για Meta posting.
    env = client.beta.environments.create(
        name="parea-prod",
        config={"type": "cloud",
                "networking": {"type": "limited", "allow_mcp_servers": True,
                               "allow_package_managers": True}},
    )
    print("ENV_ID =", env.id)

    # 2) Onboarding Agent — Haiku (φθηνό, απλό δομημένο output)
    onboarding = client.beta.agents.create(
        name="Onboarding Agent",
        model=cfg.MODEL_CHEAP,
        system=("Φτιάχνεις brand profile (JSON) για ελληνικά μικρομάγαζα από λίγες "
                "πληροφορίες. Σύντομα, στα ελληνικά. Η μεθοδολογία είναι στο skill."),
        skills=[_skill("brand-builder-gr")],
        tools=[{"type": "agent_toolset_20260401",
                "default_config": {"enabled": True}}],
    )
    print("ONBOARDING_AGENT_ID =", onboarding.id)

    # 3) Website Agent — Sonnet (θέλει ποιότητα design)
    website = client.beta.agents.create(
        name="Website Agent",
        model=cfg.MODEL_PROD,
        system=("Φτιάχνεις όμορφα static websites στα ελληνικά για μικρές ελληνικές "
                "επιχειρήσεις. Διαλέγεις preset ανά επάγγελμα, δίνεις 3 επιλογές, "
                "εφαρμόζεις SEO. Όχι e-shop. Λεπτομέρειες στα skills."),
        skills=[
            _skill("greek-website"),
            _skill("local-seo-gr"),
            _skill("conversion-copy-gr"),
        ],
        tools=[{"type": "agent_toolset_20260401",
                "default_config": {"enabled": True}}],
    )
    print("WEBSITE_AGENT_ID =", website.id)

    # 4) Social Agent — Haiku (captions είναι μικρά· αν χρειαστεί ανέβασέ το σε Sonnet)
    # Posting path: DIRECT GRAPH API (όχι Meta MCP). Ο agent επιστρέφει JSON,
    # το orchestrator (daily_post.py) καλεί publish_all() από publish.py.
    social = client.beta.agents.create(
        name="Social Agent",
        model=cfg.MODEL_CHEAP,
        system=(
            "Γράφεις καθημερινό caption για Facebook & Instagram στα ελληνικά, "
            "σωστός τόνος ανά τύπο μαγαζιού. Λεπτομέρειες στα skills.\n\n"
            "ΣΗΜΑΝΤΙΚΟ: Επίστρεψε ΠΑΝΤΑ ένα JSON object (και μόνο αυτό) με fields:\n"
            '  {"caption": "...", "hashtags": ["#tag1", "#tag2"]}\n'
            "Μην γράφεις τίποτε άλλο εκτός από το JSON."
        ),
        skills=[
            _skill("social-post-gr"),
            _skill("meta-publisher"),
        ],
        tools=[{"type": "agent_toolset_20260401",
                "default_config": {"enabled": True}}],
    )
    print("SOCIAL_AGENT_ID =", social.id)

    # Το facebook-ads-gr ανεβαίνει από upload_skills.py, αλλά ΔΕΝ φτιάχνουμε Ads Agent
    # ακόμα. Είναι post-MVP Growth add-on με approval + budget limits.

    print("\n✅ Βάλε τα IDs στο .env. ⚠️ Μην ξανατρέξεις (φτιάχνει διπλά agents).")


if __name__ == "__main__":
    main()
