"""Μια απόπειρα επιδιόρθωσης δεν μπορεί πλέον να χειροτερέψει αποδεκτή σελίδα.

Αυτό είναι το κριτήριο επιτυχίας — όχι το να γίνει τέλειο το physician.

Το σφάλμα που κλείνει (10ο τρέξιμο): κάθε γύρος εφαρμοζόταν άκριτα, το χειρότερο
αποτέλεσμα έμενε στον δίσκο, και ο επόμενος γύρος ξεκινούσε από εκεί. Desktop
1→4, mobile 0→1, `h1` 1→None, desktop 0→5 — σωρευτικά.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.repair_txn import Ledger, qa_metrics, regressions, restore, State  # noqa: E402


def vit(d_inner: int = 0, m_inner: int = 0, d_h1: int = 1, m_h1: int = 1,
        d_fail: bool = False, m_fail: bool = False, broken: int = 0,
        console: int = 0) -> dict:
    def one(inner: int, h1: int, fail: bool) -> dict:
        if fail:
            return {"fail": "δεν αποδόθηκε"}
        return {"overflow": 0, "innerOverflow": ["x"] * inner, "broken": broken,
                "consoleErrors": console, "h1": h1}
    return {"desktop": one(d_inner, d_h1, d_fail), "mobile": one(m_inner, m_h1, m_fail)}


GUARDS_OK = {"spine_guard": True, "trust_guard": True, "templateRegistry": True}


class RepairAcceptance(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = Path(tempfile.mkdtemp())
        self.jsx = self.dir / "T.jsx"
        self.css = self.dir / "T.module.css"
        self.jsx.write_text("BASELINE_JSX", encoding="utf-8")
        self.css.write_text("BASELINE_CSS", encoding="utf-8")
        self.ledger = Ledger([self.jsx, self.css])
        self.ledger.seed(vit(d_inner=1), GUARDS_OK)   # baseline: desktop 1, mobile 0

    def _write_candidate(self) -> None:
        self.jsx.write_text("CANDIDATE_JSX", encoding="utf-8")
        self.css.write_text("CANDIDATE_CSS", encoding="utf-8")

    # 1 ------------------------------------------------------------------
    def test_desktop_better_mobile_worse_is_rejected(self) -> None:
        self._write_candidate()
        rec = self.ledger.judge(1, vit(d_inner=0, m_inner=1), GUARDS_OK, False)
        self.assertEqual(rec.decision, "REJECTED")
        self.assertTrue(any("MOBILE" in r for r in rec.regressions), rec.regressions)

    # 2 ------------------------------------------------------------------
    def test_removing_h1_is_rejected(self) -> None:
        self._write_candidate()
        rec = self.ledger.judge(1, vit(d_inner=0, m_inner=0, d_h1=0), GUARDS_OK, False)
        self.assertEqual(rec.decision, "REJECTED")
        self.assertTrue(any("h1" in r for r in rec.regressions), rec.regressions)

    # 3 ------------------------------------------------------------------
    def test_new_overflow_is_rejected(self) -> None:
        self._write_candidate()
        rec = self.ledger.judge(1, vit(d_inner=4), GUARDS_OK, False)
        self.assertEqual(rec.decision, "REJECTED")
        self.assertIn("DESKTOP: inner 1 -> 4", rec.regressions)

    def test_non_renderable_viewport_is_rejected(self) -> None:
        self._write_candidate()
        rec = self.ledger.judge(1, vit(m_fail=True), GUARDS_OK, False)
        self.assertEqual(rec.decision, "REJECTED")
        self.assertTrue(any("έπαψε να αποδίδεται" in r for r in rec.regressions))

    def test_guard_regression_is_rejected(self) -> None:
        self._write_candidate()
        rec = self.ledger.judge(1, vit(d_inner=0), dict(GUARDS_OK, spine_guard=False), False)
        self.assertEqual(rec.decision, "REJECTED")
        self.assertTrue(any("spine_guard" in r for r in rec.regressions))

    # 4 + 5 --------------------------------------------------------------
    def test_files_restored_exactly_and_next_attempt_starts_there(self) -> None:
        self._write_candidate()
        rec = self.ledger.judge(1, vit(d_inner=9), GUARDS_OK, False)
        self.assertEqual(rec.decision, "REJECTED")
        self.assertTrue(rec.rollback_success)
        self.assertEqual(self.jsx.read_text(encoding="utf-8"), "BASELINE_JSX")
        self.assertEqual(self.css.read_text(encoding="utf-8"), "BASELINE_CSS")
        # η επόμενη απόπειρα συγκρίνεται με το ΑΡΧΙΚΟ, όχι με τον απορριφθέντα
        self.assertEqual(self.ledger.accepted.metrics["desktop"]["inner"], 1)

    # 6 ------------------------------------------------------------------
    def test_clean_improvement_is_accepted_and_becomes_baseline(self) -> None:
        self._write_candidate()
        rec = self.ledger.judge(1, vit(d_inner=0, m_inner=0), GUARDS_OK, True)
        self.assertEqual(rec.decision, "ACCEPTED")
        self.assertEqual(rec.regressions, [])
        self.assertEqual(self.jsx.read_text(encoding="utf-8"), "CANDIDATE_JSX")
        self.assertEqual(self.ledger.accepted.metrics["desktop"]["inner"], 0)
        # και τώρα μια οπισθοδρόμηση κρίνεται έναντι του ΝΕΟΥ baseline
        self.jsx.write_text("WORSE", encoding="utf-8")
        rec2 = self.ledger.judge(2, vit(d_inner=1), GUARDS_OK, False)
        self.assertEqual(rec2.decision, "REJECTED")
        self.assertEqual(self.jsx.read_text(encoding="utf-8"), "CANDIDATE_JSX")

    # 7 ------------------------------------------------------------------
    def test_exhausted_retries_leave_accepted_state_intact(self) -> None:
        for i in range(1, 5):
            self.jsx.write_text(f"BAD_{i}", encoding="utf-8")
            self.ledger.judge(i, vit(d_inner=5 + i), GUARDS_OK, False)
        self.assertTrue(self.ledger.rollback_to_accepted())
        self.assertEqual(self.jsx.read_text(encoding="utf-8"), "BASELINE_JSX")
        self.assertEqual(self.css.read_text(encoding="utf-8"), "BASELINE_CSS")
        self.assertEqual(len(self.ledger.attempts), 4)
        self.assertTrue(all(a.decision == "REJECTED" for a in self.ledger.attempts))

    # 8 ------------------------------------------------------------------
    def test_report_has_every_required_field(self) -> None:
        self._write_candidate()
        self.ledger.judge(1, vit(d_inner=3), GUARDS_OK, False)
        row = self.ledger.report()[0]
        for key in ("ATTEMPT", "BASELINE_STATE", "CANDIDATE_STATE", "REGRESSIONS",
                    "DECISION", "ROLLBACK_SUCCESS", "RETRY_REASON"):
            self.assertIn(key, row)

    def test_equal_state_is_not_a_regression(self) -> None:
        """Ίδιες μετρικές = καμία οπισθοδρόμηση· η βελτίωση δεν είναι υποχρεωτική."""
        self._write_candidate()
        rec = self.ledger.judge(1, vit(d_inner=1), GUARDS_OK, False)
        self.assertEqual(rec.decision, "ACCEPTED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
