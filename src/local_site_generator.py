from __future__ import annotations

import html
import json
import re
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "skills" / "greek-website" / "templates"

PLACEHOLDER_RE = re.compile(r"{{\s*([A-Z0-9_]+)(?:\|([^}]*))?\s*}}")


DEFAULTS: dict[str, str] = {
    "NAME": "Η Επιχείρησή σας",
    "CITY": "Αθήνα",
    "PHONE": "2100000000",
    "ADDRESS": "Κέντρο, Αθήνα",
    "TAGLINE": "Ποιότητα και άμεση εξυπηρέτηση",
    "TRADE": "Τεχνικός",
    "PRIMARY": "#1F3A5F",
    "ACCENT": "#FF7A00",
    "BG": "#F4F6F8",
    "FONT_DISPLAY": "'Inter', system-ui, sans-serif",
    "FONT_BODY": "'Inter', system-ui, sans-serif",
    "HERO_IMAGE": "https://images.unsplash.com/photo-1601058268499-e52658b8bb88?auto=format&fit=crop&w=1800&q=80",
    "WORKSHOP_IMAGE": "https://images.unsplash.com/photo-1562259929-b4e1fd3aef09?auto=format&fit=crop&w=1200&q=80",
    "URL": "",
    "CANONICAL_URL": "",
    "SEO_TITLE": "",
    "SEO_DESCRIPTION": "",
    "SEO_H1": "",
    "SEO_KEYWORDS": "",
    "SCHEMA_TYPE": "LocalBusiness",
    "AREA_SERVED_JSON": '"Αθήνα"',
    "OG_IMAGE": "",
    "LOGO_SVG": "",
}

TAVERNA_DISHES = [
    {"DISH_NAME": "Χωριάτικη σαλάτα", "PRICE": "7.50"},
    {"DISH_NAME": "Μπιφτέκια σχάρας", "PRICE": "10.90"},
    {"DISH_NAME": "Κοντοσούβλι χοιρινό", "PRICE": "12.50"},
    {"DISH_NAME": "Σπιτικό γλυκό ημέρας", "PRICE": "4.50"},
]

DENTIST_SERVICES = [
    {
        "SERVICE_NAME": "Καθαρισμός δοντιών",
        "SERVICE_DESC": "Προσεκτικός καθαρισμός και οδηγίες στοματικής υγιεινής.",
    },
    {
        "SERVICE_NAME": "Σφραγίσματα",
        "SERVICE_DESC": "Αισθητικές αποκαταστάσεις με σύγχρονα υλικά.",
    },
    {
        "SERVICE_NAME": "Λεύκανση",
        "SERVICE_DESC": "Ασφαλής βελτίωση χρώματος με εξατομικευμένη προσέγγιση.",
    },
    {
        "SERVICE_NAME": "Παιδοδοντία",
        "SERVICE_DESC": "Φιλική φροντίδα για παιδιά και νέους ασθενείς.",
    },
]

MASTORAS_SERVICES = [
    {
        "SERVICE_NAME": "Άμεση βλάβη",
        "SERVICE_DESC": "Γρήγορη ανταπόκριση για επείγοντα περιστατικά.",
    },
    {
        "SERVICE_NAME": "Επισκευές",
        "SERVICE_DESC": "Αξιόπιστες επισκευές με καθαρή συνεννόηση.",
    },
    {
        "SERVICE_NAME": "Συντηρήσεις",
        "SERVICE_DESC": "Προληπτικός έλεγχος για να αποφεύγονται μεγαλύτερες ζημιές.",
    },
    {
        "SERVICE_NAME": "Νέες εγκαταστάσεις",
        "SERVICE_DESC": "Οργάνωση και υλοποίηση εργασιών από την αρχή.",
    },
]

WOODWORKER_SERVICES = [
    {
        "SERVICE_NAME": "Κουζίνες στα μέτρα σας",
        "SERVICE_DESC": "Σχεδιασμός, κατασκευή και τοποθέτηση με πρακτική διάταξη και καθαρό φινίρισμα.",
    },
    {
        "SERVICE_NAME": "Ντουλάπες και αποθηκευτικοί χώροι",
        "SERVICE_DESC": "Λύσεις που αξιοποιούν σωστά κάθε εκατοστό του χώρου.",
    },
    {
        "SERVICE_NAME": "Πόρτες και έπιπλα",
        "SERVICE_DESC": "Ξύλινες κατασκευές, επισκευές και προσαρμογές για σπίτι ή επαγγελματικό χώρο.",
    },
    {
        "SERVICE_NAME": "Ειδικές ξυλουργικές κατασκευές",
        "SERVICE_DESC": "Κατασκευές με μέτρο, συνεννόηση και προσοχή στη λεπτομέρεια.",
    },
]

DEFAULT_AREAS = ["Κέντρο", "Ανατολικά", "Δυτικά", "Βόρεια Προάστια"]

DESIGN_ROUTES: dict[str, dict[str, dict[str, str]]] = {
    "premium": {
        "taverna": {
            "PRIMARY": "#18231f",
            "ACCENT": "#e86f2a",
            "BG": "#f7f1e8",
            "FONT_DISPLAY": "'Playfair Display', Georgia, serif",
            "FONT_BODY": "'Source Sans 3', system-ui, sans-serif",
        },
        "dentist": {
            "PRIMARY": "#123c69",
            "ACCENT": "#2aa7a5",
            "BG": "#f4f8fb",
            "FONT_DISPLAY": "'Poppins', system-ui, sans-serif",
            "FONT_BODY": "'Inter', system-ui, sans-serif",
        },
        "mastoras": {
            "PRIMARY": "#172033",
            "ACCENT": "#ff7a1a",
            "BG": "#f4f6f8",
            "FONT_DISPLAY": "'Oswald', system-ui, sans-serif",
            "FONT_BODY": "'Inter', system-ui, sans-serif",
        },
    },
    "warm": {
        "taverna": {
            "PRIMARY": "#49251f",
            "ACCENT": "#c45c2d",
            "BG": "#fbf0df",
            "FONT_DISPLAY": "'Georgia', 'Times New Roman', serif",
            "FONT_BODY": "'Source Sans 3', system-ui, sans-serif",
        },
        "dentist": {
            "PRIMARY": "#23566a",
            "ACCENT": "#d57a4d",
            "BG": "#f8f3ed",
            "FONT_DISPLAY": "'Poppins', system-ui, sans-serif",
            "FONT_BODY": "'Inter', system-ui, sans-serif",
        },
        "mastoras": {
            "PRIMARY": "#27323a",
            "ACCENT": "#df6f2d",
            "BG": "#f7f0e6",
            "FONT_DISPLAY": "'Oswald', system-ui, sans-serif",
            "FONT_BODY": "'Inter', system-ui, sans-serif",
        },
    },
    "minimal": {
        "taverna": {
            "PRIMARY": "#2d211c",
            "ACCENT": "#b95f3c",
            "BG": "#f4eadc",
            "FONT_DISPLAY": "'Georgia', 'Times New Roman', serif",
            "FONT_BODY": "'Source Sans 3', ui-sans-serif, system-ui, sans-serif",
        },
        "dentist": {
            "PRIMARY": "#0f5f78",
            "ACCENT": "#74c7c1",
            "BG": "#f8fbfc",
            "FONT_DISPLAY": "'Inter', system-ui, sans-serif",
            "FONT_BODY": "'Inter', system-ui, sans-serif",
        },
        "mastoras": {
            "PRIMARY": "#151515",
            "ACCENT": "#b77945",
            "BG": "#f7f4ef",
            "FONT_DISPLAY": "'Noto Sans Display', 'Aptos Display', 'Segoe UI', system-ui, sans-serif",
            "FONT_BODY": "'Noto Sans', 'Aptos', 'Segoe UI', system-ui, sans-serif",
        },
    },
    "trust": {
        "taverna": {
            "PRIMARY": "#202a25",
            "ACCENT": "#2f8f5f",
            "BG": "#f4f7f1",
            "FONT_DISPLAY": "'Noto Sans Display', 'Aptos Display', 'Segoe UI', system-ui, sans-serif",
            "FONT_BODY": "'Noto Sans', 'Aptos', 'Segoe UI', system-ui, sans-serif",
        },
        "dentist": {
            "PRIMARY": "#143d52",
            "ACCENT": "#18a8a0",
            "BG": "#f3f8fa",
            "FONT_DISPLAY": "'Noto Sans Display', 'Aptos Display', 'Segoe UI', system-ui, sans-serif",
            "FONT_BODY": "'Noto Sans', 'Aptos', 'Segoe UI', system-ui, sans-serif",
        },
        "mastoras": {
            "PRIMARY": "#18202a",
            "ACCENT": "#26a269",
            "BG": "#f3f6f4",
            "FONT_DISPLAY": "'Noto Sans Display', 'Aptos Display', 'Segoe UI', system-ui, sans-serif",
            "FONT_BODY": "'Noto Sans', 'Aptos', 'Segoe UI', system-ui, sans-serif",
        },
    },
    "editorial": {
        "taverna": {
            "PRIMARY": "#251b16",
            "ACCENT": "#bd6f3d",
            "BG": "#f5eadc",
            "FONT_DISPLAY": "'Georgia', 'Times New Roman', serif",
            "FONT_BODY": "'Noto Sans', 'Aptos', 'Segoe UI', system-ui, sans-serif",
        },
        "dentist": {
            "PRIMARY": "#182832",
            "ACCENT": "#77b8b2",
            "BG": "#f7f5f0",
            "FONT_DISPLAY": "'Georgia', 'Times New Roman', serif",
            "FONT_BODY": "'Noto Sans', 'Aptos', 'Segoe UI', system-ui, sans-serif",
        },
        "mastoras": {
            "PRIMARY": "#201713",
            "ACCENT": "#c5915d",
            "BG": "#f5efe5",
            "FONT_DISPLAY": "'Georgia', 'Times New Roman', serif",
            "FONT_BODY": "'Noto Sans', 'Aptos', 'Segoe UI', system-ui, sans-serif",
        },
    },
}

THEME_META: dict[str, dict[str, str]] = {
    "premium": {
        "label": "Craft Premium",
        "description": "Δυνατό πρώτο viewport, μεγάλο έργο/φωτογραφία και αίσθηση ακριβής δουλειάς.",
    },
    "warm": {
        "label": "Warm Local",
        "description": "Πιο φιλικό, γειτονικό και ανθρώπινο ύφος για οικογενειακές επιχειρήσεις.",
    },
    "minimal": {
        "label": "Minimal Clean",
        "description": "Καθαρό, ήρεμο, πολύ εύκολο στο διάβασμα και επαγγελματικό.",
    },
    "trust": {
        "label": "Trust / Call-first",
        "description": "Πιο πρακτικό, με έμφαση στο τηλέφωνο, τις υπηρεσίες και την άμεση εμπιστοσύνη.",
    },
    "editorial": {
        "label": "Editorial Portfolio",
        "description": "Πιο καλλιτεχνικό, με έμφαση στις φωτογραφίες και στο χειροποίητο αποτέλεσμα.",
    },
}


def generate_site(intake: dict[str, Any], route: str | None = None) -> str:
    """Generate a complete static HTML site using local Greek website templates."""
    template_name = _select_template(str(intake.get("type", "")))
    template = (TEMPLATE_DIR / f"{template_name}.html").read_text(encoding="utf-8")
    selected_route = _select_route(route or str(intake.get("route", "")))
    values = _build_values(intake, template_name, selected_route)

    if template_name == "taverna":
        template = _replace_taverna_rows(template, intake)
    elif template_name == "dentist":
        template = _replace_service_rows(template, intake, DENTIST_SERVICES)
    else:
        template = _replace_service_rows(template, intake, _default_services_for(intake))
        template = _replace_area_rows(template, intake)
        template = _replace_slideshow_rows(template, intake)
        template = _replace_gallery_rows(template, intake)

    rendered = _render_placeholders(template, values)
    rendered = re.sub(r"<!--\s*{{LOOP_[A-Z_]+}}\s*-->", "", rendered)

    if "{{" in rendered or "}}" in rendered:
        unresolved = sorted(set(re.findall(r"{{[^}]+}}", rendered)))
        raise ValueError(f"Unresolved placeholders remain: {', '.join(unresolved)}")

    return rendered


def generate_site_variants(intake: dict[str, Any], routes: list[str] | None = None) -> dict[str, str]:
    """Generate multiple visual routes for a chooser/preview gallery."""
    template_name = _select_template(str(intake.get("type", "")))
    selected_routes = routes or _recommended_routes_for(intake, template_name)
    return {route: generate_site({**intake, "route": route}, route=route) for route in selected_routes}


def theme_label(route: str) -> str:
    normalized = _select_route(route)
    return THEME_META.get(normalized, THEME_META["premium"])["label"]


def theme_description(route: str) -> str:
    normalized = _select_route(route)
    return THEME_META.get(normalized, THEME_META["premium"])["description"]


def _select_template(business_type: str) -> str:
    normalized = _normalize_text(business_type)
    if any(word in normalized for word in ("taverna", "ταβερ", "cafe", "καφε", "restaurant", "εστιατο")):
        return "taverna"
    if any(word in normalized for word in ("dentist", "οδοντ")):
        return "dentist"
    return "mastoras"


def _select_route(route: str) -> str:
    normalized = _normalize_text(route)
    return normalized if normalized in DESIGN_ROUTES else "premium"


def _recommended_routes_for(intake: dict[str, Any], template_name: str) -> list[str]:
    business_text = _normalize_text(" ".join(str(intake.get(key, "")) for key in ("type", "trade", "description")))
    if template_name == "taverna":
        return ["premium", "warm", "editorial"]
    if template_name == "dentist":
        return ["minimal", "trust", "premium"]
    if any(word in business_text for word in ("ξυλουργ", "ξυλουργος", "μαραγκ", "maragk", "wood", "carpenter")):
        return ["premium", "trust", "editorial"]
    return ["premium", "minimal", "trust"]


def _build_values(intake: dict[str, Any], template_name: str, route: str) -> dict[str, str]:
    name = _pick(intake, "name", "business_name", default=DEFAULTS["NAME"])
    city = _pick(intake, "city", "area", default=DEFAULTS["CITY"])
    phone = _pick(intake, "phone", "telephone", default=DEFAULTS["PHONE"])
    address = _pick(intake, "address", default=f"{city}, Ελλάδα")
    trade = _pick(intake, "trade", "type", default=DEFAULTS["TRADE"])

    template_defaults = {
        "taverna": {
            "TAGLINE": "Παραδοσιακή ελληνική κουζίνα",
            "PRIMARY": "#18231f",
            "ACCENT": "#e86f2a",
            "BG": "#f7f1e8",
            "FONT_DISPLAY": "'Playfair Display', Georgia, serif",
            "FONT_BODY": "'Source Sans 3', system-ui, sans-serif",
        },
        "dentist": {
            "TAGLINE": "Φροντίδα για το χαμόγελό σας",
            "PRIMARY": "#0A6EBD",
            "ACCENT": "#13C4C4",
            "BG": "#F5FAFD",
            "FONT_DISPLAY": "'Poppins', system-ui, sans-serif",
            "FONT_BODY": "'Inter', system-ui, sans-serif",
        },
        "mastoras": {
            "PRIMARY": "#1F3A5F",
            "ACCENT": "#FF7A00",
            "BG": "#F4F6F8",
            "FONT_DISPLAY": "'Oswald', system-ui, sans-serif",
            "FONT_BODY": "'Inter', system-ui, sans-serif",
        },
    }[template_name]
    route_defaults = DESIGN_ROUTES.get(route, DESIGN_ROUTES["premium"]).get(template_name, {})

    values = {**DEFAULTS, **template_defaults, **route_defaults}
    values.update(
        {
            "NAME": html.escape(name),
            "CITY": html.escape(city),
            "PHONE": html.escape(phone),
            "ADDRESS": html.escape(address),
            "ADDRESS_ENCODED": quote_plus(address),
            "TRADE": html.escape(trade),
            "TAGLINE": html.escape(_pick(intake, "tagline", "style", default=values["TAGLINE"])),
            "HOURS": html.escape(_pick(intake, "hours", default="Δευτέρα-Σάββατο 09:00-21:00")),
            "HERO_IMAGE": _asset_url(_pick(intake, "hero_image", default=values["HERO_IMAGE"])),
            "WORKSHOP_IMAGE": _asset_url(_pick(intake, "workshop_image", default=values["WORKSHOP_IMAGE"])),
            "YEAR": str(date.today().year),
        }
    )
    seo = _build_seo_values(intake, values, template_name)
    values.update(seo)
    values["LOGO_SVG"] = _build_logo_svg(intake, values)
    return values


def _replace_taverna_rows(template: str, intake: dict[str, Any]) -> str:
    dishes = _list_of_dicts(intake.get("dishes")) or TAVERNA_DISHES
    rows = "\n".join(
        f'        <div class="dish"><span class="price">{html.escape(str(item.get("PRICE", item.get("price", ""))))}€</span>'
        f'<div class="dish-name">{html.escape(str(item.get("DISH_NAME", item.get("name", "Πιάτο ημέρας"))))}</div></div>'
        for item in dishes[:4]
    )
    return re.sub(
        r"\s*<!--\s*{{LOOP_DISHES}}\s*-->\s*<div class=\"dish\">.*?{{DISH_NAME}}.*?</div>",
        "\n" + rows,
        template,
        count=1,
        flags=re.DOTALL,
    )


def _replace_service_rows(template: str, intake: dict[str, Any], defaults: list[dict[str, str]]) -> str:
    services = _list_of_dicts(intake.get("services")) or defaults
    rows = "\n".join(
        f'        <div class="service"><h3>{html.escape(str(item.get("SERVICE_NAME", item.get("name", "Υπηρεσία"))))}</h3>'
        f'<p>{html.escape(str(item.get("SERVICE_DESC", item.get("description", "Περιγραφή υπηρεσίας."))))}</p></div>'
        for item in services[:8]
    )
    return template.replace(
        '        <!-- {{LOOP_SERVICES}} -->\n        <div class="service"><h3>{{SERVICE_NAME}}</h3><p>{{SERVICE_DESC}}</p></div>',
        rows,
    )


def _default_services_for(intake: dict[str, Any]) -> list[dict[str, str]]:
    business_text = _normalize_text(" ".join(str(intake.get(key, "")) for key in ("type", "trade", "description")))
    if any(word in business_text for word in ("ξυλουργ", "ξυλουργος", "μαραγκ", "maragk", "wood", "carpenter")):
        return WOODWORKER_SERVICES
    return MASTORAS_SERVICES


def _replace_area_rows(template: str, intake: dict[str, Any]) -> str:
    raw_areas = intake.get("areas") or DEFAULT_AREAS
    areas = raw_areas if isinstance(raw_areas, list) else DEFAULT_AREAS
    rows = "\n".join(f"        <span>{html.escape(str(area))}</span>" for area in areas[:4])
    return re.sub(
        r"\s*<!--\s*\{\{LOOP_AREAS\}\}\s*-->\s*<span>\{\{AREA\}\}</span>",
        "\n" + rows,
        template,
        count=1,
    )


def _replace_gallery_rows(template: str, intake: dict[str, Any]) -> str:
    projects = _list_of_dicts(intake.get("gallery"))
    if not projects:
        return re.sub(
            r"\s*<section class=\"portfolio\" id=\"portfolio\">.*?</section>",
            "",
            template,
            count=1,
            flags=re.DOTALL,
        )

    rows = "\n".join(
        '        <figure class="project">'
        f'<img src="{_asset_url(str(item.get("image", "")))}" '
        f'alt="{html.escape(str(item.get("alt", item.get("title", "Ξυλουργική εργασία"))))}" loading="lazy">'
        f'<figcaption>{html.escape(str(item.get("title", "Ξυλουργική εργασία")))}</figcaption>'
        "</figure>"
        for item in projects[:12]
        if str(item.get("image", "")).strip()
    )
    return template.replace(
        '        <!-- {{LOOP_GALLERY}} -->\n        <figure class="project"><img src="{{PROJECT_IMAGE}}" alt="{{PROJECT_ALT}}" loading="lazy"><figcaption>{{PROJECT_TITLE}}</figcaption></figure>',
        rows,
    )


def _replace_slideshow_rows(template: str, intake: dict[str, Any]) -> str:
    slides = _list_of_dicts(intake.get("slides"))
    if not slides:
        return re.sub(
            r"\s*<section class=\"showcase\" id=\"showcase\">.*?</section>",
            "",
            template,
            count=1,
            flags=re.DOTALL,
        )

    rows: list[str] = []
    dots: list[str] = []
    for index, item in enumerate(slides[:10]):
        image = str(item.get("image", "")).strip()
        if not image:
            continue
        title = html.escape(str(item.get("title", "Ξυλουργική εργασία")))
        desc = html.escape(str(item.get("description", "")))
        alt = html.escape(str(item.get("alt", item.get("title", "Ξυλουργική εργασία"))))
        active = " active" if index == 0 else ""
        current = ' aria-current="true"' if index == 0 else ""
        rows.append(
            f'        <article class="slide{active}" data-slide="{index}">'
            f'<img src="{_asset_url(image)}" alt="{alt}" loading="{"eager" if index == 0 else "lazy"}">'
            f'<div class="slide-copy"><span>Έργο {index + 1:02d}</span><h3>{title}</h3><p>{desc}</p></div>'
            "</article>"
        )
        dots.append(
            f'          <button class="slide-dot{active}" type="button" data-target="{index}" '
            f'aria-label="Δες έργο {index + 1}"{current}></button>'
        )

    if not rows:
        return template

    template = template.replace(
        '        <!-- {{LOOP_SLIDES}} -->\n        <article class="slide active" data-slide="0"><img src="{{SLIDE_IMAGE}}" alt="{{SLIDE_ALT}}" loading="lazy"><div class="slide-copy"><span>{{SLIDE_LABEL}}</span><h3>{{SLIDE_TITLE}}</h3><p>{{SLIDE_DESC}}</p></div></article>',
        "\n".join(rows),
    )
    return template.replace(
        '          <!-- {{LOOP_SLIDE_DOTS}} -->\n          <button class="slide-dot active" type="button" data-target="0" aria-label="Δες έργο 1" aria-current="true"></button>',
        "\n".join(dots),
    )


def _build_seo_values(intake: dict[str, Any], values: dict[str, str], template_name: str) -> dict[str, str]:
    name = values["NAME"]
    city = values["CITY"]
    trade = values["TRADE"]
    phone = values["PHONE"]
    tagline = values["TAGLINE"]
    address = values["ADDRESS"]
    business_text = _normalize_text(" ".join(str(intake.get(key, "")) for key in ("type", "trade", "description")))
    is_woodworker = any(word in business_text for word in ("ξυλουργ", "ξυλουργος", "μαραγκ", "maragk", "wood", "carpenter"))
    if template_name == "taverna":
        schema_type = "Restaurant"
        service_keyword = "Ελληνική κουζίνα"
    elif template_name == "dentist":
        schema_type = "Dentist"
        service_keyword = "Οδοντιατρική φροντίδα"
    elif is_woodworker:
        schema_type = "HomeAndConstructionBusiness"
        service_keyword = "Ξυλουργικές κατασκευές"
    else:
        schema_type = "LocalBusiness"
        service_keyword = "Άμεση εξυπηρέτηση"
    raw_areas = intake.get("areas") or [city]
    areas = raw_areas if isinstance(raw_areas, list) else [city]
    area_names = [str(area).strip() for area in areas if str(area).strip()]
    if city not in area_names:
        area_names.insert(0, city)
    site_url = _pick(intake, "site_url", "url", "domain", default="")
    if site_url and not site_url.startswith(("http://", "https://")):
        site_url = "https://" + site_url
    keywords = [
        f"{trade} {city}",
        f"{service_keyword} {city}",
        f"{trade} Γέρακας" if "Γέρακας" in " ".join(area_names) else f"{trade} κοντά μου",
        f"μαραγκός {city}" if is_woodworker else f"τεχνίτης {city}",
        name,
    ]
    custom_keywords = intake.get("seo_keywords")
    if isinstance(custom_keywords, list):
        keywords.extend(str(keyword).strip() for keyword in custom_keywords if str(keyword).strip())
    base_area = str(address).split(",", 1)[0].strip() or city
    description = f"{trade} στην {city} με βάση {base_area}. {tagline}. Τηλ. {phone}."
    return {
        "SEO_TITLE": html.escape(f"{trade} {city} | {service_keyword} — {name}"),
        "SEO_DESCRIPTION": html.escape(description),
        "SEO_H1": html.escape(f"{name} — {trade} στην {city}"),
        "SEO_KEYWORDS": html.escape(", ".join(dict.fromkeys(keywords))),
        "SCHEMA_TYPE": schema_type,
        "URL": html.escape(site_url),
        "CANONICAL_URL": f'<link rel="canonical" href="{html.escape(site_url)}">' if site_url else "",
        "AREA_SERVED_JSON": json.dumps(area_names[:8], ensure_ascii=False),
        "OG_IMAGE": values["HERO_IMAGE"],
    }


def _build_logo_svg(intake: dict[str, Any], values: dict[str, str]) -> str:
    name = html.unescape(values.get("NAME", ""))
    initials = _initials(name)
    business_text = _normalize_text(" ".join(str(intake.get(key, "")) for key in ("type", "trade", "description")))
    if any(word in business_text for word in ("ξυλουργ", "ξυλουργος", "μαραγκ", "maragk", "wood", "carpenter")):
        return f'''<svg viewBox="0 0 64 64" role="img" focusable="false">
            <defs>
              <linearGradient id="logoWood" x1="9" y1="8" x2="55" y2="58" gradientUnits="userSpaceOnUse">
                <stop stop-color="#f4c08a"/>
                <stop offset=".48" stop-color="#b77945"/>
                <stop offset="1" stop-color="#6d4328"/>
              </linearGradient>
            </defs>
            <path d="M12 17h33c4 0 7 3 7 7v5H19c-4 0-7-3-7-7v-5Z" fill="url(#logoWood)"/>
            <path d="M12 35h28c4 0 7 3 7 7v5H19c-4 0-7-3-7-7v-5Z" fill="#f2d0a6"/>
            <path d="M19 24h25M18 42h21" stroke="#5a341f" stroke-width="2" stroke-linecap="round" opacity=".5"/>
            <path d="M45 12l8 8-22 22-10 4 4-10 20-24Z" fill="#fff7e8"/>
            <path d="M45 12l8 8M25 36l6 6" stroke="#5a341f" stroke-width="2" stroke-linecap="round"/>
            <text x="32" y="58" text-anchor="middle" fill="#fff7e8" font-size="12" font-weight="900" font-family="system-ui, sans-serif">{html.escape(initials)}</text>
          </svg>'''
    return f'''<svg viewBox="0 0 64 64" role="img" focusable="false">
            <circle cx="32" cy="32" r="22" fill="rgba(255,255,255,.18)"/>
            <text x="32" y="39" text-anchor="middle" fill="#fff" font-size="18" font-weight="900" font-family="system-ui, sans-serif">{html.escape(initials)}</text>
          </svg>'''


def _initials(name: str) -> str:
    words = [word.strip(".,·-–— ") for word in name.split() if word.strip(".,·-–— ")]
    if not words:
        return "V"
    if len(words) == 1:
        return words[0][:2].upper()
    return "".join(word[0] for word in words[:2]).upper()


def _render_placeholders(template: str, values: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        default = match.group(2)
        return values.get(key) or (default.strip() if default is not None else DEFAULTS.get(key, ""))

    return PLACEHOLDER_RE.sub(replace, template)


def _pick(intake: dict[str, Any], *keys: str, default: str) -> str:
    for key in keys:
        value = intake.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return default


def _list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value.casefold())
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


def _asset_url(value: str) -> str:
    if value.startswith(("http://", "https://", "/", "./", "../")):
        return value
    return html.escape(value)
