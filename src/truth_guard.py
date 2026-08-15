# -*- coding: utf-8 -*-
"""Συμβόλαιο αλήθειας για το παραγόμενο κείμενο.

> Ένας πραγματολογικός ισχυρισμός επιτρέπεται να εμφανιστεί ΜΟΝΟ αν τον στηρίζει
> το intake ή ντετερμινιστικός μετασχηματισμός του intake.

Γιατί υπάρχει: στο benchmark των 10 sites (13/8/2026) το μοντέλο έγραψε «Από το
'90 δουλεύουμε στο Περιστέρι», «15+ χρόνια», «για 30 χρόνια εδώ», «Τρεις
δεκαετίες», «θα κοστίσει 80 ευρώ». Τίποτα από αυτά δεν υπήρχε στο intake. Το
μοντέλο δεν ψεύδεται επίτηδες — γεμίζει κενά, και τα κενά που γεμίζει είναι
ακριβώς αυτά που πουλάνε.

ΔΕΝ είναι blacklist των φράσεων που βρέθηκαν. Είναι κατηγορίες ισχυρισμών που
απαιτούν απόδειξη. Η απόδειξη είναι το ίδιο το intake: αν ο αριθμός ή η λέξη δεν
υπάρχει εκεί, ο ισχυρισμός φεύγει.

Απουσία απόδειξης σημαίνει ΠΑΡΑΛΕΙΨΗ — ποτέ αντικατάσταση με άλλον ισχυρισμό.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any, Iterable

__all__ = ["scrub_copy", "find_claims", "Claim"]


def _norm(value: str) -> str:
    """Πεζά χωρίς τόνους — «Εγγύηση» και «εγγύηση» είναι ο ίδιος ισχυρισμός."""
    decomposed = unicodedata.normalize("NFD", str(value).casefold())
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


class Claim:
    """Ένας ανιχνευμένος ισχυρισμός: τι είδους, πού, και τι τον στηρίζει."""

    __slots__ = ("kind", "text", "needs")

    def __init__(self, kind: str, text: str, needs: str) -> None:
        self.kind, self.text, self.needs = kind, text, needs

    def __repr__(self) -> str:  # pragma: no cover - διαγνωστικό
        return f"Claim({self.kind!r}, {self.text!r})"


# Κάθε κατηγορία: (όνομα, pattern, τι θεωρείται απόδειξη).
# `numbers`  → ο ίδιος ο αριθμός πρέπει να υπάρχει στο intake
# `keyword`  → η λέξη-έννοια πρέπει να υπάρχει στο intake
_RULES: tuple[tuple[str, re.Pattern[str], str], ...] = (
    # χρόνια λειτουργίας / εμπειρίας — «15+ χρόνια», «30 χρόνων», «μια δεκαετία»
    ("tenure", re.compile(r"\b\d{1,3}\s*\+?\s*(?:χρονι|χρονων|ετων|ετη\b)", re.I), "numbers"),
    ("tenure", re.compile(r"\b(?:μια|δυο|τρεις|τεσσερις|πεντε|εξι)\s+δεκαετ", re.I), "keyword:δεκαετ"),
    ("tenure", re.compile(r"\bδεκαετ(?:ια|ιες|ιων)\b", re.I), "keyword:δεκαετ"),
    # ΧΩΡΙΣ αριθμό, ίδιος ισχυρισμός: «δουλεύουμε στο Περιστέρι χρόνια», «είμαστε
    # εδώ χρόνια», «με πολλά χρόνια πείρα». Το μοντέλο το βρήκε αυτό μόλις του
    # απαγορεύτηκαν οι αριθμοί — η κατηγορία είναι «διάρκεια», όχι «ψηφίο».
    ("tenure", re.compile(r"\b(?:ειμαστε|δουλευ\w+|λειτουργ\w+|υπαρχ\w+)\b[^.·;!?]{0,40}"
                          r"\b(?:χρονια|χρονιων|καιρο)\b", re.I), "keyword:__never__"),
    ("tenure", re.compile(r"\b(?:πολλα|αρκετα)\s+χρονια\b|\bχρονια\s+(?:εμπειρια|πειρα)\b", re.I),
     "keyword:__never__"),
    # έτος ίδρυσης — «από το 1998», «από το '90», «since 1998», «depuis 2015»
    ("founded", re.compile(r"\bαπο\s+το\s+['’΄]?\s*\d{2,4}\b", re.I), "numbers"),
    ("founded", re.compile(r"\b(?:since|depuis|est\.)\s*\d{2,4}\b", re.I), "numbers"),
    # τιμές
    ("price", re.compile(r"\b\d+[.,]?\d*\s*(?:€|ευρω|eur\b)", re.I), "numbers"),
    ("price", re.compile(r"(?:€|απο)\s*\d+[.,]?\d*\s*(?:ευρω|€)", re.I), "numbers"),
    # εγγυήσεις
    ("guarantee", re.compile(r"\bεγγυ(?:ηση|ησεις|ημεν|ουμαστε|ατα)\b|\bguarantee", re.I), "keyword:εγγυ"),
    # πιστοποιήσεις / βραβεία / διαπιστεύσεις
    ("credential", re.compile(r"\bπιστοποι\w*|\bδιαπιστευ\w*|\bcertified\b", re.I), "keyword:πιστοποι|διαπιστευ"),
    ("award", re.compile(r"\bβραβε(?:ιο|ια|υμεν)\w*|\baward", re.I), "keyword:βραβε"),
    # βαθμολογίες / κριτικές
    ("rating", re.compile(r"\b\d(?:[.,]\d)?\s*/\s*5\b|\b\d(?:[.,]\d)?\s*αστερ", re.I), "numbers"),
    ("reviews", re.compile(r"\bκριτικ(?:η|ες|ων)\b|\bαξιολογησ\w*|\breviews?\b", re.I), "keyword:κριτικ|αξιολογ"),
    # μετρήσιμα πλήθη — πελάτες, έργα, χρόνια συνεργασίας
    ("counts", re.compile(r"\b\d{2,}\s*\+?\s*(?:πελατ|εργα\b|κατασκευ|projects?\b|ασθεν|συνεργατ)", re.I), "numbers"),
    # συνεργασίες / αντιπροσωπείες
    ("partnership", re.compile(r"\bεπισημ(?:ος|οι|η)\s+(?:συνεργατ|αντιπροσωπ)|\bexclusive\s+partner", re.I),
     "keyword:συνεργατ|αντιπροσωπ"),
    # χρόνος απόκρισης / διαθεσιμότητα
    ("availability", re.compile(r"\b24\s*/\s*7\b|\b24\s*ωρες\b|\bολο\s+το\s+24ωρο\b", re.I), "keyword:24"),
    ("response", re.compile(r"\bεντος\s+\d+\s*(?:λεπτ|ωρ)|\bσε\s+\d+\s*(?:λεπτα|ωρες)\b", re.I), "numbers"),
    # Υγεία/θεραπεία ως αποτέλεσμα υπηρεσίας. Ισχύει και εκτός ιατρικών verticals
    # (π.χ. pet grooming ή αισθητική), όπου το μοντέλο συχνά μετατρέπει τη
    # φροντίδα εμφάνισης σε ατεκμηρίωτη υπόσχεση υγείας.
    ("health_claim", re.compile(
        r"\b(?:φροντιζ\w*|βελτιων\w*|ενισχυ\w*|προστατευ\w*)\b[^.·;!?]{0,35}"
        r"\b(?:υγεια|θεραπει\w*|ευεξια)\b", re.I
    ), "keyword:υγεια|θεραπει|ευεξια"),
    # υπερθετικά ως γεγονός
    ("superlative", re.compile(r"\b(?:ο|η|το)\s+(?:καλυτερ|κορυφαι|νουμερο\s+ενα|no\.?\s*1\b)", re.I),
     "keyword:__never__"),
    ("superlative", re.compile(r"#\s*1\b|\bΝο\.?\s*1\b", re.I), "keyword:__never__"),
)

# Πεδία που παράγει το AI. Τα πραγματολογικά (ώρες, περιοχές, τηλέφωνο, τιμές)
# ΔΕΝ τα γράφει ποτέ το μοντέλο — έρχονται από το intake και δεν ελέγχονται εδώ.
_CREATIVE_FIELDS = ("tagline", "intro", "story_title", "story_paragraphs", "cta_title")


def _evidence(intake: dict[str, Any]) -> tuple[str, set[str]]:
    """Ό,τι έχει δηλώσει ο πελάτης, ως κείμενο και ως σύνολο αριθμών."""
    parts: list[str] = []
    for key in ("name", "type", "trade", "description", "tagline", "hours", "areas",
                "style", "differentiators", "about", "website"):
        val = intake.get(key)
        if isinstance(val, (list, tuple)):
            parts.extend(str(v) for v in val)
        elif val:
            parts.append(str(val))
    for svc in intake.get("services") or []:
        if isinstance(svc, dict):
            parts.extend(str(svc.get(k, "")) for k in ("name", "title", "description", "desc"))
        else:
            parts.append(str(svc))
    blob = _norm(" ".join(parts))
    return blob, set(re.findall(r"\d+", blob))


def _supported(claim_text: str, needs: str, blob: str, numbers: set[str]) -> bool:
    if needs == "numbers":
        found = re.findall(r"\d+", claim_text)
        # Χωρίς αριθμό στο intake δεν στέκει αριθμός στο site.
        return bool(found) and all(n in numbers for n in found)
    if needs.startswith("keyword:"):
        keys = needs.split(":", 1)[1].split("|")
        if "__never__" in keys:
            return False
        return any(k in blob for k in keys)
    return False


def find_claims(text: str, intake: dict[str, Any]) -> list[Claim]:
    """Οι ΑΤΕΚΜΗΡΙΩΤΟΙ ισχυρισμοί ενός κειμένου. Κενή λίστα = καθαρό."""
    blob, numbers = _evidence(intake)
    norm = _norm(text)
    out: list[Claim] = []
    for kind, pattern, needs in _RULES:
        for m in pattern.finditer(norm):
            if not _supported(m.group(0), needs, blob, numbers):
                out.append(Claim(kind, m.group(0).strip(), needs))
    return out


# Χωρισμός σε προτάσεις που σέβεται την ελληνική τελεία/άνω τελεία/παύλα.
_SENTENCE = re.compile(r"[^.!?;·]+[.!?;·]?\s*")


def _scrub_text(text: str, intake: dict[str, Any]) -> tuple[str, list[Claim]]:
    """Κόβει ΤΗΝ ΠΡΟΤΑΣΗ που περιέχει ατεκμηρίωτο ισχυρισμό, όχι όλο το πεδίο.

    Αφαίρεση ολόκληρης πρότασης αντί για «έξυπνη» επιδιόρθωση: κάθε προσπάθεια
    να ξαναγράψουμε τον ισχυρισμό παράγει έναν δεύτερο ισχυρισμό που κανείς δεν
    επαλήθευσε."""
    removed: list[Claim] = []
    kept: list[str] = []
    for sentence in _SENTENCE.findall(text):
        claims = find_claims(sentence, intake)
        if claims:
            removed.extend(claims)
            continue
        kept.append(sentence)
    return "".join(kept).strip(), removed


def scrub_copy(copy: dict[str, Any], intake: dict[str, Any]) -> tuple[dict[str, Any], list[Claim]]:
    """Καθαρίζει AI copy. Fail closed: πεδίο που δεν σώζεται ΠΕΦΤΕΙ.

    Πεδίο που πέφτει σημαίνει ότι το site χρησιμοποιεί το ελεγμένο, γραμμένο από
    άνθρωπο default του vertical — χειρότερο marketing, σωστό γεγονός."""
    out: dict[str, Any] = dict(copy)
    removed: list[Claim] = []

    for field in _CREATIVE_FIELDS:
        val = out.get(field)
        if isinstance(val, str):
            cleaned, gone = _scrub_text(val, intake)
            removed.extend(gone)
            # Κομμένος τίτλος/tagline δεν μπαλώνεται: ή στέκει ολόκληρος ή φεύγει.
            if gone and (len(cleaned) < 12 or field in ("tagline", "story_title", "cta_title")):
                out.pop(field, None)
            elif gone:
                out[field] = cleaned
        elif isinstance(val, list):
            paras: list[str] = []
            for para in val:
                cleaned, gone = _scrub_text(str(para), intake)
                removed.extend(gone)
                if len(cleaned) >= 40:
                    paras.append(cleaned)
            if paras:
                out[field] = paras
            else:
                out.pop(field, None)

    # Οι υπηρεσίες που γράφει το AI περνούν τον ίδιο έλεγχο στην περιγραφή τους.
    services = out.get("services")
    if isinstance(services, list):
        safe = []
        for svc in services:
            if not isinstance(svc, dict):
                continue
            desc, gone = _scrub_text(str(svc.get("description", "")), intake)
            removed.extend(gone)
            safe.append({**svc, "description": desc})
        out["services"] = safe

    return out, removed
