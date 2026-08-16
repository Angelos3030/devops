"""Συναλλακτικό όριο αποδοχής γύρω από τον βρόχο επιδιόρθωσης.

Το σφάλμα που κλείνει: ο worker εφάρμοζε κάθε patch, μετά μετρούσε, μετά
παραπονιόταν. Το χειρότερο αποτέλεσμα έμενε στον δίσκο και ο επόμενος γύρος
ξεκινούσε από εκεί — σωρευτικά. Στο 10ο τρέξιμο κάθε γύρος χειροτέρευε:
desktop 1→4, mobile 0→1, `h1` 1→None (η σελίδα έπαψε να αποδίδεται), desktop 0→5.
Ο ανιχνευτής τα έβλεπε όλα και τα ανέφερε· κανείς δεν τα σταματούσε.

Η αμετάβλητη ιδιότητα που επιβάλλεται εδώ:

    LAST_ACCEPTED_STATE δεν αλλάζει μέχρι ένας υποψήφιος να περάσει ΟΛΑ
    τα κριτήρια — desktop ΚΑΙ mobile ΚΑΙ guards, ατομικά.

Ένας απορριφθείς υποψήφιος δεν γίνεται ΠΟΤΕ είσοδος για την επόμενη απόπειρα.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Μετρικές που δεν επιτρέπεται να χειροτερέψουν. Το κλειδί είναι ο τρόπος
# σύγκρισης, όχι απλώς η ύπαρξη: «λιγότερο είναι καλύτερα» για μετρητές,
# «ήταν 1, πρέπει να μείνει 1» για δομικά στοιχεία.
COUNTERS = ("overflow", "inner", "broken", "console")
VIEWPORTS = ("desktop", "mobile")


@dataclass
class State:
    """Ένα πλήρες, επαναφέρσιμο στιγμιότυπο."""
    files: dict[str, str] = field(default_factory=dict)
    metrics: dict[str, dict[str, Any]] = field(default_factory=dict)
    guards: dict[str, bool] = field(default_factory=dict)
    label: str = "baseline"

    def is_empty(self) -> bool:
        return not self.files


def snapshot_files(paths: list[Path]) -> dict[str, str]:
    return {str(p): p.read_text(encoding="utf-8") for p in paths if p.exists()}


def qa_metrics(vit: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Μηχανική κατάσταση ανά viewport. `renderable=False` όταν η σελίδα έπεσε."""
    out: dict[str, dict[str, Any]] = {}
    for vp in VIEWPORTS:
        m = vit.get(vp) or {}
        failed = ("fail" in m) or not m
        out[vp] = {
            "renderable": not failed,
            "overflow": 0 if failed else (m.get("overflow") or 0),
            "inner": 0 if failed else len(m.get("innerOverflow") or []),
            "broken": 0 if failed else (m.get("broken") or 0),
            "console": 0 if failed else (m.get("consoleErrors") or 0),
            "h1": None if failed else m.get("h1"),
        }
    return out


def regressions(baseline: State, candidate: State) -> list[str]:
    """Τι ΧΕΙΡΟΤΕΡΕΨΕ σε σχέση με το τελευταίο αποδεκτό. Κενή λίστα = καθαρό."""
    out: list[str] = []
    for vp in VIEWPORTS:
        b = baseline.metrics.get(vp, {})
        c = candidate.metrics.get(vp, {})
        if not b:
            continue
        if b.get("renderable") and not c.get("renderable"):
            out.append(f"{vp.upper()}: το viewport έπαψε να αποδίδεται")
            continue
        for key in COUNTERS:
            if (c.get(key) or 0) > (b.get(key) or 0):
                out.append(f"{vp.upper()}: {key} {b.get(key)} -> {c.get(key)}")
        if b.get("h1") == 1 and c.get("h1") != 1:
            out.append(f"{vp.upper()}: το h1 χάθηκε ({b.get('h1')} -> {c.get('h1')})")
    for name, passed in baseline.guards.items():
        if passed and not candidate.guards.get(name, False):
            out.append(f"GUARD {name}: πέρναγε -> αποτυγχάνει")
    return out


def restore(state: State) -> bool:
    """Επαναφορά ΑΚΡΙΒΩΣ του αποδεκτού στιγμιότυπου, με επαλήθευση."""
    if state.is_empty():
        return False
    for path, content in state.files.items():
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return all(Path(k).read_text(encoding="utf-8") == v for k, v in state.files.items())


@dataclass
class Attempt:
    """Ό,τι πρέπει να είναι ορατό για κάθε απόπειρα, χωρίς εξαίρεση."""
    attempt: int
    baseline_state: dict[str, Any]
    candidate_state: dict[str, Any]
    regressions: list[str]
    decision: str                    # ACCEPTED | REJECTED
    rollback_success: bool | None
    retry_reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "ATTEMPT": self.attempt,
            "BASELINE_STATE": self.baseline_state,
            "CANDIDATE_STATE": self.candidate_state,
            "REGRESSIONS": self.regressions,
            "DECISION": self.decision,
            "ROLLBACK_SUCCESS": self.rollback_success,
            "RETRY_REASON": self.retry_reason,
        }


class Ledger:
    """Κρατά το LAST_ACCEPTED_STATE και αποφασίζει αποδοχή ή επαναφορά."""

    def __init__(self, paths: list[Path]) -> None:
        self.paths = paths
        self.accepted = State()
        self.attempts: list[Attempt] = []

    def seed(self, vit: dict[str, Any], guards: dict[str, bool]) -> None:
        """Το πρώτο αποδεκτό: ό,τι υπάρχει μετά την αρχική παραγωγή."""
        self.accepted = State(files=snapshot_files(self.paths),
                              metrics=qa_metrics(vit), guards=guards, label="seed")

    def judge(self, attempt: int, vit: dict[str, Any], guards: dict[str, bool],
              all_gates_pass: bool) -> Attempt:
        """Αποδοχή μόνο αν ΚΑΜΙΑ προστατευμένη μετρική δεν χειροτέρεψε."""
        candidate = State(files=snapshot_files(self.paths),
                          metrics=qa_metrics(vit), guards=guards, label=f"candidate-{attempt}")
        regs = regressions(self.accepted, candidate)

        if regs:
            ok = restore(self.accepted)
            rec = Attempt(attempt, self.accepted.metrics, candidate.metrics, regs,
                          "REJECTED", ok,
                          "οπισθοδρόμηση — η επόμενη απόπειρα ξεκινά από το LAST_ACCEPTED_STATE")
        else:
            self.accepted = candidate
            self.accepted.label = f"accepted-{attempt}"
            rec = Attempt(attempt, candidate.metrics, candidate.metrics, [],
                          "ACCEPTED", None,
                          "" if all_gates_pass else "καμία οπισθοδρόμηση, αλλά μένουν gates")
        self.attempts.append(rec)
        return rec

    def rollback_to_accepted(self) -> bool:
        """Τελικό δίχτυ: το repo δεν μένει ΠΟΤΕ στην τελευταία αποτυχία."""
        return restore(self.accepted)

    def report(self) -> list[dict[str, Any]]:
        return [a.to_dict() for a in self.attempts]
