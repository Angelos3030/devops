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

# --- Cloudflare Pages (deploy) ---
CF_API_TOKEN = os.environ.get("CF_API_TOKEN", "")
CF_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID", "")

# --- Domain registration via Cloudflare Registrar ---
# Δεν χρειάζεται ξεχωριστό API key — χρησιμοποιεί CF_API_TOKEN + CF_ACCOUNT_ID παραπάνω.
# SSL: δωρεάν Universal SSL αυτόματα. Χωρίς Papaki, χωρίς certificate αγορά.
