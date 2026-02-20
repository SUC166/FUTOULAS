"""
GitHub Storage Backend for FUTO ULAS.

All attendance data lives in a SEPARATE GitHub data repo.
This prevents Streamlit Cloud from reloading the app on data changes.

Streamlit secrets.toml:
  GITHUB_TOKEN  = "ghp_xxxxx"
  GITHUB_REPO   = "yourusername/futo-attendance-data"
  GITHUB_BRANCH = "main"
"""

import os
import json
import base64
import requests
import streamlit as st


def _get_config():
    try:
        token  = st.secrets["GITHUB_TOKEN"]
        repo   = st.secrets["GITHUB_REPO"]
        branch = st.secrets.get("GITHUB_BRANCH", "main")
    except Exception:
        token  = os.environ.get("GITHUB_TOKEN", "")
        repo   = os.environ.get("GITHUB_REPO", "")
        branch = os.environ.get("GITHUB_BRANCH", "main")
    return token, repo, branch


def _headers():
    token, _, _ = _get_config()
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }


def _api_url(path):
    _, repo, _ = _get_config()
    return f"https://api.github.com/repos/{repo}/contents/{path}"


def read_file(path):
    """Returns (content_str, sha) or (None, None)."""
    _, _, branch = _get_config()
    resp = requests.get(_api_url(path), headers=_headers(), params={"ref": branch}, timeout=15)
    if resp.status_code == 404:
        return None, None
    resp.raise_for_status()
    data = resp.json()
    return base64.b64decode(data["content"]).decode("utf-8"), data["sha"]


def write_file(path, content_str, message, sha=None):
    _, _, branch = _get_config()
    payload = {
        "message": message,
        "content": base64.b64encode(content_str.encode("utf-8")).decode("utf-8"),
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha
    resp = requests.put(_api_url(path), headers=_headers(), json=payload, timeout=20)
    if resp.status_code in (200, 201):
        return True
    raise Exception(f"GitHub write error {resp.status_code}: {resp.text[:400]}")


def read_json(path):
    content, sha = read_file(path)
    if content is None:
        return None, None
    return json.loads(content), sha


def write_json(path, data, message, sha=None):
    return write_file(path, json.dumps(data, indent=2, ensure_ascii=False), message, sha)


def list_files_in_dir(path_prefix):
    _, repo, branch = _get_config()
    url = f"https://api.github.com/repos/{repo}/git/trees/{branch}"
    resp = requests.get(url, headers=_headers(), params={"recursive": "1"}, timeout=20)
    if resp.status_code != 200:
        return []
    return [item["path"] for item in resp.json().get("tree", [])
            if item["path"].startswith(path_prefix) and item["type"] == "blob"]


# ─── Attendance helpers ───────────────────────────────────────────────────────

ACTIVE_PATH    = "active_attendances.json"
PASSWORDS_PATH = "rep_passwords.json"
ATTENDANCES_ROOT = "attendances"


def _safe(s):
    for ch in ["/", " ", "(", ")", ","]:
        s = s.replace(ch, "_")
    return s


def att_dir(school, dept, level):
    return f"{ATTENDANCES_ROOT}/{_safe(school)}/{_safe(dept)}/{level}L"


def att_key(school, dept, level):
    return f"{school}||{dept}||{level}"


def get_active_attendances():
    data, sha = read_json(ACTIVE_PATH)
    return (data or {}), sha


def set_active_attendances(data, sha=None):
    return write_json(ACTIVE_PATH, data, "Update active attendances", sha)


def get_csv_path(school, dept, level, course_code, date_str, time_str):
    safe_code = course_code.replace(" ", "_")
    return f"{att_dir(school, dept, level)}/{safe_code}_{date_str}_{time_str}.csv"


def get_devices_path(csv_path):
    return csv_path.replace(".csv", "_devices.json")


def list_attendance_csvs(school, dept, level):
    prefix = att_dir(school, dept, level)
    return sorted([f for f in list_files_in_dir(prefix) if f.endswith(".csv")], reverse=True)


def get_custom_passwords():
    data, sha = read_json(PASSWORDS_PATH)
    return (data or {}), sha


def set_custom_passwords(data, sha=None):
    return write_json(PASSWORDS_PATH, data, "Update rep passwords", sha)
