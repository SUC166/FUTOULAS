"""Utilities for FUTO Attendance System."""

import hashlib
import random
import time
import io
import csv
from datetime import datetime


# ─── Password ─────────────────────────────────────────────────────────────────

import json as _json
import os as _os

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def verify_password(pw: str, hashed: str) -> bool:
    return hash_password(pw) == hashed


def _load_password_hashes() -> dict:
    """Load hashes from rep_passwords.json (lives in app repo root)."""
    path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "rep_passwords.json")
    try:
        with open(path, "r") as f:
            return _json.load(f)
    except Exception:
        return {}


def verify_rep_login(school: str, dept: str, level: str, password: str) -> bool:
    """Verify rep password against rep_passwords.json."""
    hashes = _load_password_hashes()
    key = f"{school}|{dept}|{level}"
    if key not in hashes:
        return False
    return verify_password(password, hashes[key])


# ─── Code generation ──────────────────────────────────────────────────────────

def get_current_code(started_at: float, interval: int = 10):
    """
    Returns (code, slot, seconds_remaining).
    Code is seeded from (started_at, slot) so it's deterministic but unpredictable.
    """
    elapsed = time.time() - started_at
    slot = int(elapsed // interval)
    rng = random.Random(int(started_at * 1000) + slot * 997)
    code = f"{rng.randint(0, 9999):04d}"
    secs_left = interval - (elapsed % interval)
    return code, slot, round(secs_left, 1)


def is_code_valid(entered: str, started_at: float, interval: int = 10) -> bool:
    current, _, _ = get_current_code(started_at, interval)
    return entered.strip() == current


# ─── CSV ──────────────────────────────────────────────────────────────────────

HEADERS = ["S/N", "Surname", "First Name", "Middle Name", "Matric Number", "Timestamp"]


def entries_to_csv(entries: list) -> str:
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(HEADERS)
    for i, e in enumerate(entries, 1):
        w.writerow([i, e.get("surname", ""), e.get("first_name", ""),
                    e.get("middle_name", ""), e.get("matric", ""), e.get("timestamp", "")])
    return out.getvalue()


def csv_to_entries(csv_str: str) -> list:
    reader = csv.DictReader(io.StringIO(csv_str))
    return [{
        "surname": row.get("Surname", ""),
        "first_name": row.get("First Name", ""),
        "middle_name": row.get("Middle Name", ""),
        "matric": row.get("Matric Number", ""),
        "timestamp": row.get("Timestamp", ""),
    } for row in reader]


def is_dup_name(surname, first, middle, entries):
    norm = lambda s: s.strip().upper()
    key = norm(surname) + norm(first) + norm(middle)
    for e in entries:
        if norm(e["surname"]) + norm(e["first_name"]) + norm(e["middle_name"]) == key:
            return True
    return False


def is_dup_matric(matric, entries):
    m = matric.strip().upper()
    return any(e["matric"].strip().upper() == m for e in entries)


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def date_str():
    return datetime.now().strftime("%Y-%m-%d")


def time_str():
    return datetime.now().strftime("%H-%M-%S")
