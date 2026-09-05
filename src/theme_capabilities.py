"""ΠΑΡΑΓΟΜΕΝΟ ΑΡΧΕΙΟ — μην το γράψεις στο χέρι.

Πηγή: research/theme-library/capabilities.py
Ξαναγράφεται με: python scripts/apply_capabilities.py
"""

from __future__ import annotations

THEME_CAPABILITIES: dict[str, dict] = {
    'aegean': {'cls': 'C', 'mode': 'light', 'palettes': (), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'airspace-office': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('modern', 'friendly'), 'logo': True},
    'area-first': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('modern', 'friendly'), 'logo': True},
    'bakery-editorial': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('modern', 'friendly'), 'logo': True},
    'barber-shop': {'cls': 'B', 'mode': 'light', 'palettes': ('warm', 'rose'), 'typography': ('modern', 'friendly'), 'logo': True},
    'beauty-atelier': {'cls': 'B', 'mode': 'light', 'palettes': (), 'typography': ('editorial', 'modern', 'friendly'), 'logo': True},
    'bigspring-advisory': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'billys-barber': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'bloom': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'blue-onepage': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('modern', 'friendly'), 'logo': True},
    'callout': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'canvas': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'modern', 'friendly'), 'logo': True},
    'chapter-snap': {'cls': 'C', 'mode': 'light', 'palettes': (), 'typography': ('modern', 'friendly'), 'logo': True},
    'cinematic': {'cls': 'C', 'mode': 'dark', 'palettes': (), 'typography': ('editorial', 'modern', 'friendly'), 'logo': True},
    'clean-work': {'cls': 'B', 'mode': 'light', 'palettes': ('warm', 'rose', 'ocean'), 'typography': ('modern', 'friendly'), 'logo': True},
    'clinic-triage': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'coast': {'cls': 'C', 'mode': 'light', 'palettes': (), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'constra-build': {'cls': 'C', 'mode': 'light', 'palettes': (), 'typography': ('modern', 'friendly'), 'logo': True},
    'counter-menu': {'cls': 'B', 'mode': 'dark', 'palettes': ('mono', 'forest'), 'typography': ('modern', 'friendly'), 'logo': True},
    'directory-index': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('modern', 'friendly'), 'logo': True},
    'dispatch': {'cls': 'C', 'mode': 'dark', 'palettes': (), 'typography': ('modern', 'friendly'), 'logo': True},
    'educenter-campus': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'elegance-salon': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'ember': {'cls': 'A', 'mode': 'dark', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'forge': {'cls': 'B', 'mode': 'light', 'palettes': ('warm',), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'freight-lane': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('modern', 'friendly'), 'logo': True},
    'frost-bakery': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'grecko-table': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'gymso-fitness': {'cls': 'B', 'mode': 'light', 'palettes': ('warm', 'rose', 'mono'), 'typography': ('modern', 'friendly'), 'logo': True},
    'heritage-bakery': {'cls': 'B', 'mode': 'light', 'palettes': ('warm', 'forest'), 'typography': ('modern', 'friendly'), 'logo': True},
    'horizontal-story': {'cls': 'A', 'mode': 'dark', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'infinite': {'cls': 'C', 'mode': 'dark', 'palettes': (), 'typography': ('editorial', 'modern', 'friendly'), 'logo': True},
    'kinetic': {'cls': 'B', 'mode': 'light', 'palettes': ('warm', 'mono'), 'typography': ('friendly',), 'logo': True},
    'klassy-cafe': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('friendly',), 'logo': True},
    'living': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'modern', 'friendly'), 'logo': True},
    'marble': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'medic-care': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('modern', 'friendly'), 'logo': True},
    'microbakery-lab': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('modern', 'friendly'), 'logo': True},
    'morning-journal': {'cls': 'B', 'mode': 'light', 'palettes': ('warm', 'rose'), 'typography': ('modern', 'friendly'), 'logo': True},
    'moso-interior': {'cls': 'B', 'mode': 'light', 'palettes': ('warm', 'rose'), 'typography': ('modern', 'friendly'), 'logo': True},
    'motor': {'cls': 'A', 'mode': 'dark', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'neighborhood-market': {'cls': 'B', 'mode': 'light', 'palettes': ('warm', 'rose'), 'typography': ('modern', 'friendly'), 'logo': True},
    'novena-care': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'price-first': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'property-atlas': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'pulse': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'quiet': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'runway': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'modern', 'friendly'), 'logo': True},
    'scandinavian-coffee': {'cls': 'C', 'mode': 'light', 'palettes': (), 'typography': ('modern', 'friendly'), 'logo': True},
    'signature': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'terra': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('modern', 'friendly', 'classic'), 'logo': True},
    'thomson-stylist': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'friendly', 'classic'), 'logo': True},
    'type-gallery': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'vertical-snap': {'cls': 'C', 'mode': 'dark', 'palettes': (), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'vex-counter': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('modern', 'friendly'), 'logo': True},
    'villa-agency': {'cls': 'A', 'mode': 'light', 'palettes': ('warm', 'forest', 'ocean', 'rose', 'mono'), 'typography': ('modern', 'friendly'), 'logo': True},
    'volt': {'cls': 'B', 'mode': 'dark', 'palettes': ('mono',), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
    'warmth': {'cls': 'C', 'mode': 'light', 'palettes': (), 'typography': ('editorial', 'modern', 'friendly', 'classic'), 'logo': True},
}


def get(theme_id: str) -> dict:
    """Οι δυνατότητες ενός theme. Άγνωστο id -> τίποτα επιτρεπτό."""
    return THEME_CAPABILITIES.get(theme_id, {
        'cls': 'C', 'mode': 'light', 'palettes': (),
        'typography': (), 'logo': True})


def is_allowed(theme_id: str, op: str, value=None) -> bool:
    """Η ΜΟΝΗ πύλη. Το frontend κρύβει· εδώ απορρίπτεται.

    Παράδειγμα: coast + set_palette(forest) -> False, ό,τι κι αν στείλει
    ο client. Το `original` επιτρέπεται πάντα: είναι επιστροφή στην
    ταυτότητα του theme, όχι προσαρμογή.
    """
    c = get(theme_id)
    if op == 'set_palette':
        return value == 'original' or value in c['palettes']
    if op == 'set_font_pair':
        return value in c['typography']
    if op == 'set_logo':
        return bool(c['logo'])
    return False
