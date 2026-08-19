"""Κανένα content-bearing στοιχείο χωρίς πραγματικά δεδομένα.

Το σφάλμα που κλείνει, μετρημένο σε τρία themes: το συμβόλαιο έλεγε ποια πεδία
ΥΠΑΡΧΟΥΝ στο σχήμα, όχι ποια είναι ΓΕΜΑΤΑ για το επιλεγμένο demo. Το μοντέλο
έδεσε `d.services[].price` ενώ το demo «taverna» είχε 0/4 τιμές, και το μενού
μιας ταβέρνας αποδόθηκε ως τέσσερα κενά μαύρα κουτιά με σκέτο «€».

Η αλήθεια έχει δύο σκέλη: ΚΑΜΙΑ ΕΠΙΝΟΗΣΗ και ΚΑΜΙΑ ΣΗΜΑΣΙΟΛΟΓΙΚΗ ΥΠΟΚΑΤΑΣΤΑΣΗ.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.port_guards import check_data_binding  # noqa: E402
from src.vitrina_contract import availability, availability_prompt  # noqa: E402


def av(count: int, **fields: int) -> dict:
    """Συνθετική διαθεσιμότητα: fields={'price': 0} => 0/count γεμάτα."""
    return {"business": "test", "scalars": {},
            "arrays": {"services": {"count": count,
                                    "fields": {k: {"populated": v, "total": count}
                                               for k, v in fields.items()}}}}


def jsx(body: str) -> list[dict[str, str]]:
    return [{"path": "sites/lib/templates/T.jsx", "content":
             "export default function T({ data: d }) { return (<div>" + body + "</div>) }"}]


PRICE_ALWAYS = "{d.services.map((s) => (<li key={s.title}>{s.title}<b>{s.price}</b></li>))}"
PRICE_COND = ("{d.services.map((s) => (<li key={s.title}>{s.title}"
              "{s.price ? <b>{s.price}</b> : null}</li>))}")


class DataBinding(unittest.TestCase):
    # A ------------------------------------------------------------------
    def test_schema_and_demo_have_price_may_render(self) -> None:
        self.assertEqual(check_data_binding(jsx(PRICE_ALWAYS),
                                            av(4, title=4, price=4)), [])

    # B ------------------------------------------------------------------
    def test_demo_has_no_price_blocks_the_shell(self) -> None:
        p = check_data_binding(jsx(PRICE_ALWAYS), av(4, title=4, price=0))
        self.assertTrue(p, "κενό κέλυφος πέρασε")
        self.assertIn("0/4", p[0])
        self.assertIn("ΜΗΝ αποδίδεται", p[0])

    # C ------------------------------------------------------------------
    def test_partial_availability_requires_conditional(self) -> None:
        bad = check_data_binding(jsx(PRICE_ALWAYS), av(4, title=4, price=3))
        self.assertTrue(bad, "μερική διαθεσιμότητα χωρίς συνθήκη πέρασε")
        good = check_data_binding(jsx(PRICE_COND), av(4, title=4, price=3))
        self.assertEqual(good, [], f"υπό συνθήκη απόδοση απορρίφθηκε: {good}")

    # D ------------------------------------------------------------------
    def test_currency_symbol_alone_cannot_survive(self) -> None:
        body = "{d.services.map((s) => (<span key={s.title}>€{s.price}</span>))}"
        self.assertTrue(check_data_binding(jsx(body), av(4, title=4, price=0)))

    # E ------------------------------------------------------------------
    def test_label_shell_cannot_survive(self) -> None:
        body = ("{d.services.map((s) => (<p key={s.title}>Διάρκεια: "
                "{s.duration}</p>))}")
        self.assertTrue(check_data_binding(jsx(body), av(4, title=4, duration=0)))

    # F ------------------------------------------------------------------
    def test_decorative_element_is_allowed(self) -> None:
        body = ("<span className={s.dot} aria-hidden=\"true\" />"
                "{d.services.map((x) => (<li key={x.title}>{x.title}</li>))}")
        self.assertEqual(check_data_binding(jsx(body), av(4, title=4)), [])

    # G ------------------------------------------------------------------
    def test_num_cannot_stand_in_for_price(self) -> None:
        body = "{d.services.map((s) => (<span key={s.title}>price {s.num}</span>))}"
        p = check_data_binding(jsx(body), av(4, title=4, num=4))
        self.assertTrue(any("υποκατάσταση" in x for x in p), p)

    # H ------------------------------------------------------------------
    def test_ordinal_cannot_replace_property_specification(self) -> None:
        for slot in ("sqm", "bedrooms", "bathrooms"):
            body = ("{d.services.map((s) => (<span key={s.title}>"
                    + slot + " {s.num}</span>))}")
            p = check_data_binding(jsx(body), av(3, title=3, num=3))
            self.assertTrue(any("υποκατάσταση" in x for x in p), f"{slot}: {p}")

    # I ------------------------------------------------------------------
    def test_truth_guard_untouched(self) -> None:
        src = (Path(__file__).resolve().parents[1] / "sites" / "tests"
               / "trust_guard.mjs").read_text(encoding="utf-8")
        self.assertGreater(len(src), 500, "το trust_guard δεν πρέπει να έχει αδειάσει")

    # J ------------------------------------------------------------------
    def test_availability_comes_from_real_demo_data(self) -> None:
        a = availability("taverna")
        self.assertEqual(a["business"], "taverna")
        svc = a["arrays"]["services"]
        self.assertEqual(svc["fields"]["title"]["populated"], svc["count"])
        self.assertNotIn("price", svc["fields"],
                         "το taverna ΔΕΝ έχει price — αν εμφανιστεί, ο εξαγωγέας λέει ψέματα")
        b = availability("salon")
        self.assertIn("price", b["arrays"]["services"]["fields"],
                      "το salon ΕΧΕΙ price — δεν είναι hard-coded ανά επάγγελμα")

    def test_prompt_states_the_rule(self) -> None:
        txt = availability_prompt(availability("taverna"))
        for needle in ("ΚΑΝΕΝΑ", "ΜΕΡΙΚΑ", "ΥΠΟΚΑΤΑΣΤΑΣΗ", "ΚΛΕΙΝΕΙ ΚΑΘΑΡΑ"):
            self.assertIn(needle, txt, f"λείπει ο κανόνας «{needle}»")


if __name__ == "__main__":
    unittest.main(verbosity=2)
