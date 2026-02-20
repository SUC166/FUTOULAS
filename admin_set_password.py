"""
Admin utility — FUTO ULAS
Run locally to set/change course rep passwords.

  export GITHUB_TOKEN="ghp_xxx"
  export GITHUB_REPO="yourusername/futo-attendance-data"
  python admin_set_password.py
"""
import sys, os, hashlib, json, base64, requests

GITHUB_TOKEN  = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO   = os.environ.get("GITHUB_REPO", "")
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main")
PATH = "rep_passwords.json"

h = lambda pw: hashlib.sha256(pw.encode()).hexdigest()
url = lambda: f"https://api.github.com/repos/{GITHUB_REPO}/contents/{PATH}"
hdrs = lambda: {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

def read():
    r = requests.get(url(), headers=hdrs(), params={"ref": GITHUB_BRANCH})
    if r.status_code == 404: return {}, None
    d = r.json(); return json.loads(base64.b64decode(d["content"]).decode()), d["sha"]

def write(data, sha=None):
    p = {"message": "Update rep passwords", "branch": GITHUB_BRANCH,
         "content": base64.b64encode(json.dumps(data, indent=2).encode()).decode()}
    if sha: p["sha"] = sha
    r = requests.put(url(), headers=hdrs(), json=p)
    print("✅ Password updated." if r.status_code in (200,201) else f"❌ {r.status_code}: {r.text}")

if __name__ == "__main__":
    if not GITHUB_TOKEN or not GITHUB_REPO:
        print("❌ Set GITHUB_TOKEN and GITHUB_REPO env vars."); sys.exit(1)
    school  = input("School (exact name): ").strip()
    dept    = input("Department (exact name): ").strip()
    level   = input("Level number only (e.g. 300): ").strip()
    pw      = input("New password: ").strip()
    confirm = input("Confirm password: ").strip()
    if pw != confirm: print("❌ Passwords don't match."); sys.exit(1)
    data, sha = read()
    data[f"{school}|{dept}|{level}"] = h(pw)
    write(data, sha)
