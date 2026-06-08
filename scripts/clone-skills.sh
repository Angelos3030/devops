#!/usr/bin/env bash
# Κατεβάζει ΜΟΝΟ τη curated shortlist (δες docs/11-EXTERNAL-SKILLS.md) για μελέτη.
# ΟΧΙ install — απλώς clone για να δεις πώς είναι γραμμένα. Έλεγξε license πριν χρήση.
set -euo pipefail

DIR="external-skills"
mkdir -p "$DIR"
cd "$DIR"

clone() {  # clone <url> <όνομα>
  if [ -d "$2" ]; then echo "✓ $2 (υπάρχει)"; else
    echo "↓ $2"; git clone --depth 1 "$1" "$2" || echo "  ⚠️ απέτυχε: $1";
  fi
}

# --- Επίπεδο 1: άμεση αξία ---
clone https://github.com/anthropics/claude-code.git            anthropic-claude-code   # frontend-design skill μέσα
clone https://github.com/lfurze/claude-skills.git              lfurze-claude-skills    # astro-website
clone https://github.com/Mood-Global-Services/How-to-Clone-Website---Claude-Skills.git how-to-clone-website  # design tokens

# --- Mega-curated (browsing) ---
clone https://github.com/hesreallyhim/awesome-claude-code.git  awesome-claude-code
clone https://github.com/travisvn/awesome-claude-skills.git    awesome-claude-skills

echo ""
echo "Έτοιμο. Τα υπόλοιπα (Caveman, Nothing Design, Interface Design, Marketing Skills,"
echo "SEO & GEO) ψάξ' τα στο awesome-claude-skills και πρόσθεσέ τα εδώ με σιγουριά για URL."
echo "⚠️ Διάβασε license + SKILL.md/scripts πριν χρησιμοποιήσεις οτιδήποτε εμπορικά."
