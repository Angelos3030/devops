"""Κύκλος ζωής του preview server, με ρητή ιδιοκτησία θύρας.

Γιατί υπάρχει: στο 4ο proof ο worker μέτρησε «3 console errors» που ήταν
`MIME type 'text/html'` για `.css` — δηλαδή απάντησε **παλιός** server. Το
`netstat` έδειξε ζόμπι `next start` στο 3881 και 3884 από προηγούμενα
τρεξίματα. Δύο αιτίες:

  1. `Popen.terminate()` σκοτώνει το `npx`, όχι το node παιδί του. Στα Windows
     χρειάζεται `taskkill /T /F` για ολόκληρο το δέντρο διεργασιών.
  2. Κανείς δεν έλεγχε αν η θύρα ήταν ελεύθερη ΠΡΙΝ το launch, οπότε ο νέος
     server αποτύγχανε σιωπηλά και η αποτύπωση έπαιρνε την απάντηση του παλιού.

Κανόνας ασφαλείας: σκοτώνουμε **μόνο** διεργασία που κρατά τη δική μας θύρα και
της οποίας η γραμμή εντολής μοιάζει με δικό μας preview server. Ποτέ τυφλά.
"""
from __future__ import annotations

import os
import re
import shutil
import socket
import subprocess
import time
import urllib.request
from pathlib import Path


class PreviewServerError(RuntimeError):
    """Η θύρα δεν ελευθερώθηκε ή ο server δεν σηκώθηκε."""


def port_owner_pids(port: int) -> list[int]:
    """PIDs που ακούνε στη θύρα. Κενή λίστα = ελεύθερη."""
    try:
        out = subprocess.run(["netstat", "-ano"], capture_output=True, text=True,
                             timeout=25, encoding="utf-8", errors="replace").stdout
    except Exception:  # noqa: BLE001
        return []
    pids: list[int] = []
    for line in out.splitlines():
        if f":{port} " not in line or "LISTENING" not in line:
            continue
        parts = line.split()
        if parts and parts[-1].isdigit():
            pid = int(parts[-1])
            if pid and pid not in pids:
                pids.append(pid)
    return pids


def is_free(port: int) -> bool:
    if port_owner_pids(port):
        return False
    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def _cmdline(pid: int) -> str:
    """Γραμμή εντολής μιας διεργασίας — για να μη σκοτώσουμε ξένη.

    Το `wmic` ΔΕΝ υπάρχει σε Windows 11 (καταργήθηκε) και επέστρεφε πάντα κενό.
    Σε συνδυασμό με fail-open λογική, ο reclaim σκότωνε ξένες διεργασίες — το
    έπιασε το `tests/test_preview_server_lifecycle.py`. Πηγή τώρα το CIM.
    """
    ps = shutil.which("pwsh") or shutil.which("powershell")
    if not ps:
        return ""
    try:
        out = subprocess.run(
            [ps, "-NoProfile", "-NonInteractive", "-Command",
             f"(Get-CimInstance Win32_Process -Filter 'ProcessId={pid}').CommandLine"],
            capture_output=True, text=True, timeout=25,
            encoding="utf-8", errors="replace").stdout
        return out.strip()
    except Exception:  # noqa: BLE001
        return ""


# Υπογραφή δικού μας server. Ό,τι δεν ταιριάζει ΔΕΝ σκοτώνεται.
OWNED = re.compile(r"next.{0,40}start|\.next-port", re.I)


def kill_tree(pid: int) -> bool:
    """`taskkill /T /F` — ολόκληρο το δέντρο, γιατί το npx είναι wrapper."""
    try:
        r = subprocess.run(["taskkill", "/T", "/F", "/PID", str(pid)],
                           capture_output=True, text=True, timeout=25,
                           encoding="utf-8", errors="replace")
        return r.returncode == 0
    except Exception:  # noqa: BLE001
        return False


def reclaim(port: int) -> dict[str, list[int]]:
    """Ελευθερώνει τη θύρα σκοτώνοντας ΜΟΝΟ δικές μας διεργασίες."""
    found = port_owner_pids(port)
    killed, skipped = [], []
    for pid in found:
        cmd = _cmdline(pid)
        # FAIL CLOSED: σκοτώνουμε μόνο με ΘΕΤΙΚΗ επιβεβαίωση ιδιοκτησίας. Άγνωστη
        # ή μη αναγνώσιμη γραμμή εντολής σημαίνει «δεν την αγγίζω». Η προηγούμενη
        # έκδοση ήταν fail-open και σκότωνε ξένες διεργασίες όταν το wmic έλειπε.
        if not (cmd and OWNED.search(cmd)):
            skipped.append(pid)
            continue
        if kill_tree(pid):
            killed.append(pid)
    for _ in range(20):
        if is_free(port):
            break
        time.sleep(0.5)
    return {"found": found, "killed": killed, "skipped": skipped}


class PreviewServer:
    """Context manager: εξασφαλίζει τη θύρα, σηκώνει, και ΠΑΝΤΑ καθαρίζει."""

    def __init__(self, cwd: Path, port: int, dist_dir: str = ".next-port") -> None:
        self.cwd, self.port, self.dist_dir = cwd, port, dist_dir
        self.proc: subprocess.Popen | None = None
        self.reclaimed: dict[str, list[int]] = {}

    def __enter__(self) -> "PreviewServer":
        self.reclaimed = reclaim(self.port)
        if not is_free(self.port):
            raise PreviewServerError(
                f"η θύρα {self.port} παραμένει κατειλημμένη από "
                f"{self.reclaimed.get('skipped') or self.reclaimed.get('found')} — δεν ξεκινώ")
        self.proc = subprocess.Popen(
            [shutil.which("npx") or "npx", "next", "start", "-p", str(self.port)],
            cwd=self.cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            env=dict(os.environ, NEXT_DIST_DIR=self.dist_dir),
        )
        return self

    def wait_ready(self, path: str, timeout_s: int = 60) -> bool:
        url = f"http://127.0.0.1:{self.port}/{path.lstrip('/')}"
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            if self.proc and self.proc.poll() is not None:
                return False                       # πέθανε στο ξεκίνημα
            try:
                with urllib.request.urlopen(url, timeout=4) as r:
                    if r.getcode() == 200:
                        return True
            except Exception:  # noqa: BLE001
                pass
            time.sleep(1)
        return False

    def __exit__(self, *_exc: object) -> None:
        if self.proc and self.proc.poll() is None:
            kill_tree(self.proc.pid)
            try:
                self.proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        # Ακόμη κι αν το PID πέθανε, η θύρα μπορεί να κρατιέται από παιδί.
        if not is_free(self.port):
            reclaim(self.port)
