"""
GitHub Storage Backend.
All attendance data lives in a SEPARATE GitHub repo (data repo).
This avoids Streamlit Cloud reloading the app when data changes,
since only the app repo triggers rebuilds.

Setup:
  - Create a SEPARATE repo for data (e.g. "yourusername/futo-attendance-data")
  - Set GITHUB_TOKEN and GITHUB_REPO (data repo) in Streamlit secrets
  - The app repo contains only code

Streamlit secrets.toml:
  GITHUB_TOKEN = "ghp_xxxxx"
  GITHUB_REPO  = "yourusername/futo-attendance-data"
  GITHUB_BRANCH = "main"
"""

import os
import json
import base64
import requests
import streamlit as st


@st.cache_data(ttl=0)
def _get_config():
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo = st.secrets["GITHUB_REPO"]
        branch = st.secrets.get("GITHUB_BRANCH", "main")
    except Exception:
        token = os.environ.get("GITHUB_TOKEN", "")
        repo = os.environ.get("GITHUB_REPO", "")
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
    """Read a file. Returns (content_str, sha) or (None, None)."""
    _, _, branch = _get_config()
    resp = requests.get(_api_url(path), headers=_headers(), params={"ref": branch}, timeout=15)
    if resp.status_code == 404:
        return None, None
    resp.raise_for_status()
    data = resp.json()
    content = base64.b64decode(data["content"]).decode("utf-8")
    return content, data["sha"]


def write_file(path, content_str, message, sha=None):
    """Create or update a file. Returns True on success."""
    _, _, branch = _get_config()
    encoded = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
    payload = {"message": message, "content": encoded, "branch": branch}
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
    """List all blob paths under a directory prefix."""
    _, repo, branch = _get_config()
    url = f"https://api.github.com/repos/{repo}/git/trees/{branch}"
    resp = requests.get(url, headers=_headers(), params={"recursive": "1"}, timeout=20)
    if resp.status_code != 200:
        return []
    tree = resp.json().get("tree", [])
    return [item["path"] for item in tree
            if item["path"].startswith(path_prefix) and item["type"] == "blob"]


# ─── Attendance helpers ───────────────────────────────────────────────────────

ACTIVE_PATH = "active_attendances.json"
ATTENDANCES_ROOT = "attendances"


def _safe(s):
    return s.replace("/", "_").replace(" ", "_").replace("(", "").replace(")", "").replace(",", "")


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
    directory = att_dir(school, dept, level)
    filename = f"{course_code.replace(' ', '_')}_{date_str}_{time_str}.csv"
    return f"{directory}/{filename}"


def get_devices_path(csv_path):
    return csv_path.replace(".csv", "_devices.json")


def list_attendance_csvs(school, dept, level):
    prefix = att_dir(school, dept, level)
    all_files = list_files_in_dir(prefix)
    return sorted([f for f in all_files if f.endswith(".csv")], reverse=True)
