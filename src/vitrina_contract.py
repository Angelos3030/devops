"""Εξαγωγή του data contract ΑΠΟ ΤΟΝ ΚΩΔΙΚΑ, όχι από μνήμη.

Γιατί υπάρχει αυτό το αρχείο: στο πρώτο proof του port worker περιέγραψα το
data model με το χέρι (`d.name`, `d.about[]`, `d.hours[]`, `d.social`). Κανένα
από αυτά δεν υπάρχει. Το DeepSeek ακολούθησε πιστά λάθος προδιαγραφή και
παρήγαγε theme που δεν αποδιδόταν καθόλου: τέσσερα διαφορετικά runtime σφάλματα,
όλα από την ίδια αιτία.

Ένα συμβόλαιο γραμμένο με το χέρι παλιώνει σιωπηλά. Ένα συμβόλαιο που
παράγεται από τα ίδια τα αρχεία δεν μπορεί.

Πηγές αλήθειας, με αυτή τη σειρά:
  1. `sites/app/preview/[template]/page.jsx` — το ΟΝΟΜΑ του prop
  2. `sites/lib/demoData.js`                 — τα πεδία και ο ΤΥΠΟΣ τους
  3. ένα canonical theme                     — το ιδίωμα χρήσης
  4. `sites/lib/templates/*.jsx` (shared)    — υπογραφές κοινών components
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SITES = ROOT / "sites"
OUT = ROOT / "research" / "port-worker" / "data-contract.json"

CANONICAL_THEME = "BlueOnepage"
SHARED = ("Brand", "FindUs", "SocialLinks", "CallBar", "MapEmbed", "MediaDisclosure")


def _prop_name() -> str:
    """Πώς λέγεται το prop που περνά το route στο theme."""
    route = SITES / "app" / "preview" / "[template]" / "page.jsx"
    txt = route.read_text(encoding="utf-8")
    m = re.search(r"<Tpl\s+([A-Za-z_]+)=\{", txt)
    if not m:
        raise RuntimeError(f"Δεν βρέθηκε η κλήση του template στο {route}")
    return m.group(1)


def _demo_fields() -> dict[str, dict[str, Any]]:
    """Πεδία + τύπος, από το πρώτο πλήρες demo business."""
    txt = (SITES / "lib" / "demoData.js").read_text(encoding="utf-8")
    start = txt.index("export const demoBusinesses")
    # Το πρώτο business object: από το πρώτο `{` μετά το πρώτο key μέχρι να
    # κλείσει, με μέτρημα αγκυλών (τα nested arrays/objects το χρειάζονται).
    key = re.search(r"\n  ([a-z]+):\s*\{", txt[start:])
    if not key:
        raise RuntimeError("Δεν βρέθηκε demo business")
    i = start + key.end() - 1
    depth, j = 0, i
    while j < len(txt):
        if txt[j] == "{":
            depth += 1
        elif txt[j] == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    block = txt[i:j + 1]

    fields: dict[str, dict[str, Any]] = {}
    # Πεδία πρώτου επιπέδου μόνο: αγνοούμε ό,τι είναι μέσα σε nested δομές.
    depth = 0
    for m in re.finditer(r"([A-Za-z_][A-Za-z0-9_]*)\s*:\s*|[\[\]{}]", block):
        tok = m.group(0)
        if tok in "[{":
            depth += 1
            continue
        if tok in "]}":
            depth -= 1
            continue
        if depth != 1:
            continue
        name = m.group(1)
        rest = block[m.end():m.end() + 60].lstrip()
        kind = ("array" if rest.startswith("[")
                else "object" if rest.startswith("{")
                else "string")
        fields[name] = {"type": kind}

    # Σχήμα στοιχείου για κάθε array — ένωση από ΟΛΑ τα demo businesses, όχι
    # μόνο το πρώτο: ο ξυλουργός δεν έχει τιμές στις υπηρεσίες, το κομμωτήριο
    # έχει `price` και `duration`. Ένα theme που τα υποστηρίζει πρέπει να ξέρει
    # ότι υπάρχουν, αλλιώς τα αγνοεί σιωπηλά.
    for name, meta in fields.items():
        if meta["type"] != "array":
            continue
        keys: set[str] = set()
        for am in re.finditer(rf"\b{name}\s*:\s*\[", txt):
            # Οριοθέτηση στο ΠΡΑΓΜΑΤΙΚΟ κλείσιμο του πίνακα. Με σταθερό παράθυρο
            # χαρακτήρων τα κλειδιά διέρρεαν από τον επόμενο πίνακα και το
            # `services` έβγαζε 20 κλειδιά αντί για 4.
            depth, k = 1, am.end()
            while k < len(txt) and depth:
                depth += (txt[k] == "[") - (txt[k] == "]")
                k += 1
            for item in re.finditer(r"\{([^{}]*)\}", txt[am.end():k]):
                keys.update(re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*:", item.group(1)))
        # `https` κ.λπ. προκύπτουν από URL μέσα σε τιμές string, δεν είναι κλειδιά.
        meta["item_keys"] = sorted(keys - {"https", "http", "data"})
    return fields


def _canonical_usage() -> dict[str, Any]:
    """Το ιδίωμα: υπογραφή, ποια πεδία χρησιμοποιεί, πώς καλεί τα shared."""
    p = SITES / "lib" / "templates" / f"{CANONICAL_THEME}.jsx"
    txt = p.read_text(encoding="utf-8")
    sig = re.search(r"export default function \w+\(\{([^}]*)\}\)", txt)
    used = sorted(set(re.findall(r"\bd\.([A-Za-z_][A-Za-z0-9_]*)", txt)))
    calls = {}
    for comp in SHARED:
        cm = re.search(rf"<{comp}\s+([A-Za-z_]+)=\{{d\}}", txt)
        if cm:
            calls[comp] = cm.group(1)
    return {"signature": sig.group(1).strip() if sig else "", "fields_used": used,
            "shared_prop": calls, "excerpt": txt[txt.index("return ("):][:1400]}


def _shared_signatures() -> dict[str, str]:
    out = {}
    for comp in SHARED:
        p = SITES / "lib" / "templates" / f"{comp}.jsx"
        if not p.exists():
            continue
        m = re.search(r"export default function \w+\(\{([^}]*)\}\)",
                      p.read_text(encoding="utf-8"))
        if m:
            out[comp] = m.group(1).strip()
    return out


def extract() -> dict[str, Any]:
    prop = _prop_name()
    fields = _demo_fields()
    canonical = _canonical_usage()
    contract = {
        "generated_from": ["sites/app/preview/[template]/page.jsx",
                           "sites/lib/demoData.js",
                           f"sites/lib/templates/{CANONICAL_THEME}.jsx"],
        "prop_name": prop,
        "signature": f"{{ {prop}: d }}",
        "fields": fields,
        "canonical_theme": CANONICAL_THEME,
        "canonical_usage": canonical,
        "shared_components": _shared_signatures(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(contract, indent=1, ensure_ascii=False), encoding="utf-8")
    return contract


def as_prompt(contract: dict[str, Any], component: str) -> str:
    """Το συμβόλαιο σε μορφή που διαβάζει το μοντέλο. Καμία χειρόγραφη λίστα."""
    f = contract["fields"]
    strings = [k for k, v in f.items() if v["type"] == "string"]
    arrays = [(k, v.get("item_keys", [])) for k, v in f.items() if v["type"] == "array"]
    shared = "\n".join(f"    <{c} {p}={{d}} />  // υπογραφή: {{ {contract['shared_components'].get(c, '')} }}"
                       for c, p in contract["canonical_usage"]["shared_prop"].items())
    return f"""=== VITRINA DATA CONTRACT (εξήχθη από τον κώδικα, {', '.join(contract['generated_from'])}) ===

Signature — ΑΚΡΙΒΩΣ αυτή:
    export default function {component}({{ {contract['prop_name']}: d }}) {{ ... }}

The route passes the prop named `{contract['prop_name']}`. Any other name renders undefined.

STRING fields (χρήση ως {{d.FIELD}}, ΠΟΤΕ .map()):
  {', '.join(strings)}

ARRAY fields (μόνο αυτά δέχονται .map()):
{chr(10).join(f'  d.{k} — στοιχεία με κλειδιά: {", ".join(keys) or "(άγνωστα)"}' for k, keys in arrays)}

ΔΕΝ ΥΠΑΡΧΕΙ κανένα άλλο πεδίο. Μην επινοήσεις `d.name`, `d.hours[]`, `d.about[]`,
`d.social`, `d.mapQuery` — δεν υπάρχουν. Χρησιμοποίησε μόνο τα παραπάνω, με
ακριβώς αυτά τα ονόματα και αυτούς τους τύπους.

Shared components — κάλεσέ τα έτσι, μην τα ξαναγράψεις:
{shared}

Ιδίωμα από το canonical theme ({contract['canonical_theme']}), ακολούθησέ το:
{contract['canonical_usage']['excerpt'][:900]}
"""


if __name__ == "__main__":
    c = extract()
    print(f"prop: {c['prop_name']}")
    print(f"πεδία: {len(c['fields'])} — "
          f"{sum(1 for v in c['fields'].values() if v['type'] == 'string')} string, "
          f"{sum(1 for v in c['fields'].values() if v['type'] == 'array')} array")
    for k, v in c["fields"].items():
        if v["type"] == "array":
            print(f"  {k}: [{', '.join(v.get('item_keys', []))}]")
    print(f"shared: {c['canonical_usage']['shared_prop']}")
