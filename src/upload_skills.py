"""
ONE-TIME — Ανεβάζει τα custom skills στη Skills API. Τρέξε ΜΙΑ φορά.

  python -m src.upload_skills

Χρησιμοποιεί το Anthropic Python SDK (client.beta.skills.create).
Το SDK βάζει αυτόματα το beta header skills-2025-10-02.
"""

import os
import anthropic
from . import config as cfg

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "skills")
CUSTOM_SKILLS = [
    "brand-builder-gr", "greek-website", "social-post-gr",
    "meta-publisher", "local-seo-gr", "facebook-ads-gr",
    "conversion-copy-gr",
]


def _collect_files(folder: str) -> list:
    """Επιστρέφει list από (filename, bytes, mimetype) για όλα τα αρχεία του skill."""
    path = os.path.join(SKILLS_DIR, folder)
    assert os.path.exists(os.path.join(path, "SKILL.md")), f"Λείπει SKILL.md στο {path}"
    result = []
    for root, _, filenames in os.walk(path):
        for fname in filenames:
            full_path = os.path.join(root, fname)
            arc_name = os.path.relpath(full_path, path)  # SKILL.md στη ρίζα
            with open(full_path, "rb") as f:
                result.append((arc_name, f.read(), "text/plain"))
    return result


def upload_skill(client: anthropic.Anthropic, folder: str) -> str:
    """Δημιουργεί skill + ανεβάζει version 1. Επιστρέφει skill_id."""
    files = _collect_files(folder)
    response = client.beta.skills.create(
        display_title=folder,
        files=files,
    )
    skill_id = response.id
    print(f"  ✅ {folder} → {skill_id}")
    return skill_id


ENV_KEY = {  # folder → .env μεταβλητή
    "brand-builder-gr": "SKILL_BRAND",
    "greek-website": "SKILL_WEBSITE",
    "social-post-gr": "SKILL_SOCIAL",
    "meta-publisher": "SKILL_META",
    "local-seo-gr": "SKILL_SEO",
    "facebook-ads-gr": "SKILL_ADS",
    "conversion-copy-gr": "SKILL_COPY",
}


def main() -> None:
    client = anthropic.Anthropic(api_key=cfg.ANTHROPIC_API_KEY)
    print("Ανεβάζω custom skills...\n")
    lines = []
    for s in CUSTOM_SKILLS:
        try:
            sid = upload_skill(client, s)
            lines.append(f"{ENV_KEY[s]}={sid}")
        except Exception as e:
            print(f"  ❌ {s}: {e}")
    print("\n📋 Βάλ' τα στο .env:\n" + "\n".join(lines))


if __name__ == "__main__":
    main()
