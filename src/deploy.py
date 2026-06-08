"""
Deploy static site σε Cloudflare Pages (Direct Upload API).
Δέχεται έτοιμο HTML (ή φάκελο Astro build) και το ανεβάζει.

⚠️ Το ακριβές Cloudflare Pages Direct Upload API έχει πολλά βήματα (create project,
upload manifest, upload files). Εδώ ο σκελετός — για production προτίμησε:
  - Cloudflare Wrangler CLI (wrangler pages deploy <dir>), ή
  - GitHub integration (push → auto deploy).
Δες: https://developers.cloudflare.com/pages/
"""

import subprocess
import tempfile
import os
from . import config as cfg


def deploy_site(slug: str, html: str) -> str:
    """
    Απλούστερη αξιόπιστη μέθοδος: γράψε το HTML σε φάκελο, κάνε `wrangler pages deploy`.
    Επιστρέφει το live URL. Απαιτεί εγκατεστημένο wrangler + CF_API_TOKEN.
    """
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        project = f"parea-{slug}"
        env = {**os.environ, "CLOUDFLARE_API_TOKEN": cfg.CF_API_TOKEN,
               "CLOUDFLARE_ACCOUNT_ID": cfg.CF_ACCOUNT_ID}
        # δημιουργία project (αγνόησε σφάλμα αν υπάρχει ήδη)
        subprocess.run(["wrangler", "pages", "project", "create", project,
                        "--production-branch", "main"], env=env, capture_output=True)
        out = subprocess.run(
            ["wrangler", "pages", "deploy", d, "--project-name", project],
            env=env, capture_output=True, text=True)
        if out.returncode != 0:
            raise RuntimeError(f"Deploy απέτυχε: {out.stderr}")
    return f"https://{project}.pages.dev"


def deploy_astro(slug: str, astro_dir: str) -> str:
    """
    Για Astro sites (δες astro-website skill). Κάνει build και deploy το dist/.
    """
    build = subprocess.run(["npm", "run", "build"], cwd=astro_dir,
                           capture_output=True, text=True)
    if build.returncode != 0:
        raise RuntimeError(f"Astro build απέτυχε: {build.stderr}")
    return deploy_dir(slug, os.path.join(astro_dir, "dist"))


def deploy_dir(slug: str, directory: str) -> str:
    project = f"parea-{slug}"
    env = {**os.environ, "CLOUDFLARE_API_TOKEN": cfg.CF_API_TOKEN,
           "CLOUDFLARE_ACCOUNT_ID": cfg.CF_ACCOUNT_ID}
    out = subprocess.run(
        ["wrangler", "pages", "deploy", directory, "--project-name", project],
        env=env, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"Deploy απέτυχε: {out.stderr}")
    return f"https://{project}.pages.dev"
