"""Κεντρική φόρτωση ρυθμίσεων από το .env. Import αυτό παντού."""

import os
from dotenv import load_dotenv

load_dotenv()


def _req(key: str) -> str:
    val = os.environ.get(key)
    if not val:
        raise RuntimeError(f"Λείπει το env var: {key} (δες .env.example)")
    return val


# --- Claude (απαιτείται μόνο για upload_skills / setup_agents / daily_post) ---
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# --- Agents / Environment (από setup_agents.py) ---
ENV_ID = os.environ.get("ENV_ID", "")
ONBOARDING_AGENT_ID = os.environ.get("ONBOARDING_AGENT_ID", "")
WEBSITE_AGENT_ID = os.environ.get("WEBSITE_AGENT_ID", "")
SOCIAL_AGENT_ID = os.environ.get("SOCIAL_AGENT_ID", "")

# --- Skill IDs (από upload_skills.py) ---
SKILL_IDS = {
    "brand-builder-gr": os.environ.get("SKILL_BRAND", ""),
    "greek-website": os.environ.get("SKILL_WEBSITE", ""),
    "social-post-gr": os.environ.get("SKILL_SOCIAL", ""),
    "meta-publisher": os.environ.get("SKILL_META", ""),
    "local-seo-gr": os.environ.get("SKILL_SEO", ""),
    "facebook-ads-gr": os.environ.get("SKILL_ADS", ""),
    "conversion-copy-gr": os.environ.get("SKILL_COPY", ""),
}

# --- Μοντέλα (token-efficient: Haiku/Sonnet, Opus σπάνια) ---
MODEL_CHEAP = "claude-haiku-4-5"      # brand, captions
MODEL_PROD = "claude-sonnet-4-6"      # website
MODEL_SMART = "claude-opus-4-8"       # μόνο για σύνθετα (σπάνια)

# --- Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# --- Meta ---
META_APP_ID = os.environ.get("META_APP_ID", "")
META_APP_SECRET = os.environ.get("META_APP_SECRET", "")

# --- Stripe ---
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PRICE_STARTER = os.environ.get("STRIPE_PRICE_STARTER", "")
STRIPE_PRICE_SOCIAL = os.environ.get("STRIPE_PRICE_SOCIAL", "")
STRIPE_PRICE_PREMIUM = os.environ.get("STRIPE_PRICE_PREMIUM", "")
# MVP single plan — Website only, €14.99/μήνα (χωρίς social).
STRIPE_PRICE_SITE = os.environ.get("STRIPE_PRICE_SITE", "")

# --- Cloudflare Pages (deploy) ---
CF_API_TOKEN = os.environ.get("CF_API_TOKEN", "")
CF_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID", "")

# --- Domain registration ---
# DOMAIN_REGISTRAR=manual keeps paid orders for manual fulfillment.
# DOMAIN_REGISTRAR=papaki enables the Papaki adapter once reseller credentials/docs are available.
DOMAIN_ADMIN_TOKEN = os.environ.get("DOMAIN_ADMIN_TOKEN", "")
DOMAIN_REGISTRAR = os.environ.get("DOMAIN_REGISTRAR", "manual")  # manual | papaki
PAPAKI_API_BASE = os.environ.get("PAPAKI_API_BASE", "")
PAPAKI_API_KEY = os.environ.get("PAPAKI_API_KEY", "")
PAPAKI_RESELLER_ID = os.environ.get("PAPAKI_RESELLER_ID", "")
PAPAKI_CONTACT_ID = os.environ.get("PAPAKI_CONTACT_ID", "")
