"""Ντετερμινιστικός έλεγχος του κύκλου ζωής της preview θύρας.

Αποδεικνύει τέσσερα πράγματα, με ΠΡΑΓΜΑΤΙΚΕΣ διεργασίες και πραγματική θύρα:

  1. ένας ζόμπι server που κρατά τη θύρα ΑΝΙΧΝΕΥΕΤΑΙ
  2. τερματίζεται ολόκληρο το δέντρο του
  3. η θύρα είναι πράγματι ελεύθερη μετά
  4. ξένη διεργασία ΔΕΝ σκοτώνεται

Το (4) είναι το σημαντικότερο: ένας worker που σκοτώνει ό,τι βρει σε μια θύρα
είναι πιο επικίνδυνος από έναν worker που αποτυγχάνει.
"""
from __future__ import annotations

import subprocess
import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.preview_server import (  # noqa: E402
    OWNED, is_free, kill_tree, port_owner_pids, reclaim,
)

PORT = 3899  # δικός μας, εκτός των θυρών που χρησιμοποιεί ο worker


def _holder(port: int, tag: str) -> subprocess.Popen:
    """Διεργασία που κρατά τη θύρα. Το `tag` μπαίνει στη γραμμή εντολής."""
    code = (f"# {tag}\n"
            "import socket, time\n"
            "s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)\n"
            f"s.bind(('127.0.0.1', {port})); s.listen(1)\n"
            "time.sleep(120)\n")
    p = subprocess.Popen([sys.executable, "-c", code],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(40):
        if port_owner_pids(port):
            return p
        time.sleep(0.25)
    p.kill()
    raise AssertionError(f"ο holder δεν κατέλαβε τη θύρα {port}")


class PreviewLifecycle(unittest.TestCase):
    def setUp(self) -> None:
        self.spawned: list[subprocess.Popen] = []

    def tearDown(self) -> None:
        for p in self.spawned:
            if p.poll() is None:
                kill_tree(p.pid)
                try:
                    p.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    p.kill()

    def test_free_port_reports_free(self) -> None:
        self.assertTrue(is_free(PORT), f"η {PORT} έπρεπε να είναι ελεύθερη πριν το τεστ")

    def test_stale_server_detected_and_reclaimed(self) -> None:
        # 1. ζόμπι με δική μας υπογραφή στη γραμμή εντολής
        p = _holder(PORT, "next start .next-port")
        self.spawned.append(p)
        pids = port_owner_pids(PORT)
        self.assertIn(p.pid, pids, "ο ζόμπι δεν ανιχνεύθηκε ως κάτοχος της θύρας")
        self.assertFalse(is_free(PORT), "η θύρα αναφέρθηκε ελεύθερη ενώ ήταν πιασμένη")

        # 2-3. ανάκτηση: σκοτώνεται και η θύρα ελευθερώνεται πραγματικά
        result = reclaim(PORT)
        self.assertIn(p.pid, result["killed"], f"δεν τερματίστηκε ο δικός μας: {result}")
        self.assertTrue(is_free(PORT), f"η θύρα δεν ελευθερώθηκε: {result}")
        self.assertIsNotNone(p.poll(), "η διεργασία ζει ακόμη μετά το kill_tree")

    def test_foreign_process_is_not_killed(self) -> None:
        # 4. ξένη διεργασία: δεν ταιριάζει η υπογραφή -> δεν την αγγίζουμε
        p = _holder(PORT, "some-unrelated-user-service")
        self.spawned.append(p)
        result = reclaim(PORT)
        self.assertIn(p.pid, result["skipped"],
                      f"ξένη διεργασία δεν έπρεπε να σκοτωθεί: {result}")
        self.assertIsNone(p.poll(), "ξένη διεργασία τερματίστηκε — απαγορεύεται")
        self.assertFalse(is_free(PORT), "η θύρα έπρεπε να παραμείνει πιασμένη")

    def test_ownership_signature(self) -> None:
        self.assertTrue(OWNED.search("node .../next start -p 3881"))
        self.assertTrue(OWNED.search("NEXT_DIST_DIR=.next-port npx next start"))
        self.assertFalse(OWNED.search("postgres -D data"))
        self.assertFalse(OWNED.search("chrome.exe --type=renderer"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
