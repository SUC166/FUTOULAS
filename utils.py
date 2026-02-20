"""Utilities for FUTO ULAS - Unified Lecture Attendance System."""

import hashlib
import random
import time
import io
import csv
from datetime import datetime


# ─── Password ─────────────────────────────────────────────────────────────────

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def verify_password(pw: str, hashed: str) -> bool:
    return hash_password(pw) == hashed

def default_password(dept: str, level: str) -> str:
    abbr = dept.replace(" ", "")[:3].upper()
    return f"{abbr}{level}"

def verify_rep_login(school, dept, level, password, custom_hashes: dict) -> bool:
    key = f"{school}|{dept}|{level}"
    if key in custom_hashes:
        return verify_password(password, custom_hashes[key])
    return verify_password(password, hash_password(default_password(dept, level)))


# ─── Code generation ──────────────────────────────────────────────────────────

INTERVAL = 10  # seconds per code slot

def get_current_code(started_at: float):
    """
    Returns (code_str, slot_index, seconds_remaining_float).
    Deterministic: same started_at + same slot always gives same code.
    """
    elapsed = time.time() - started_at
    slot = int(elapsed // INTERVAL)
    rng = random.Random(int(started_at * 1000) + slot * 997)
    code = f"{rng.randint(0, 9999):04d}"
    secs_left = INTERVAL - (elapsed % INTERVAL)
    return code, slot, secs_left

def is_code_valid(entered: str, started_at: float) -> bool:
    current, _, _ = get_current_code(started_at)
    return entered.strip() == current


# ─── CSV ──────────────────────────────────────────────────────────────────────

HEADERS = ["S/N", "Surname", "First Name", "Middle Name", "Matric Number", "Timestamp"]

def entries_to_csv(entries: list) -> str:
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(HEADERS)
    for i, e in enumerate(entries, 1):
        w.writerow([i, e.get("surname",""), e.get("first_name",""),
                    e.get("middle_name",""), e.get("matric",""), e.get("timestamp","")])
    return out.getvalue()

def csv_to_entries(csv_str: str) -> list:
    reader = csv.DictReader(io.StringIO(csv_str))
    return [{
        "surname":    row.get("Surname", ""),
        "first_name": row.get("First Name", ""),
        "middle_name":row.get("Middle Name", ""),
        "matric":     row.get("Matric Number", ""),
        "timestamp":  row.get("Timestamp", ""),
    } for row in reader]

def is_dup_name(surname, first, middle, entries):
    key = (surname.strip().upper() + first.strip().upper() + middle.strip().upper())
    for e in entries:
        if (e["surname"].upper() + e["first_name"].upper() + e["middle_name"].upper()) == key:
            return True
    return False

def is_dup_matric(matric, entries):
    m = matric.strip().upper()
    return any(e["matric"].strip().upper() == m for e in entries)

def now_str():  return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def date_str(): return datetime.now().strftime("%Y-%m-%d")
def time_str(): return datetime.now().strftime("%H-%M-%S")
