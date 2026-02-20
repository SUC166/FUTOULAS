# 📋 FUTO Attendance System

A digital attendance management system for the Federal University of Technology, Owerri.

---

## 🏗️ Architecture — Two-Repo Strategy

To prevent Streamlit Cloud from reloading the app every time a student submits, we use **two separate GitHub repos**:

| Repo | Purpose |
|------|---------|
| **App repo** | All Python/Streamlit code + `rep_passwords.json` |
| **Data repo** | Live attendance CSVs and JSON state files |

Streamlit Cloud only watches the **app repo**. Attendance data is read/written to the **data repo** via the GitHub API — student submissions never trigger app restarts.

---

## 🚀 Deployment

### 1. Create the Data Repo
Create a new empty GitHub repo (e.g. `yourname/futo-attendance-data`), make it private, initialize with a README.

### 2. Create a GitHub Token
GitHub → Settings → Developer Settings → Fine-grained tokens  
→ Access: **only** the data repo  
→ Permissions: **Contents — Read and Write**

### 3. Deploy to Streamlit Cloud
Push this folder to your app repo. At [share.streamlit.io](https://share.streamlit.io), set main file to `Home.py` and add secrets:

```toml
GITHUB_TOKEN = "ghp_your_token_here"
GITHUB_REPO  = "yourname/futo-attendance-data"
GITHUB_BRANCH = "main"
```

---

## 🔐 Managing Rep Passwords

Passwords are SHA-256 hashes in `rep_passwords.json` (app repo). No in-app UI — you edit this file directly.

### To change a password:
1. Open `rep_passwords.json`
2. Find the key: `"SchoolName|DeptName|Level"` (e.g. `"School of Engineering...|Chemical Engineering|300"`)
3. Get the SHA-256 hash of your new password:
   - Online: https://emn178.github.io/online-tools/sha256.html
   - Python: `import hashlib; print(hashlib.sha256(b"NewPassword").hexdigest())`
4. Replace the value, commit and push

### Default Password Format
First 3 letters of department (uppercase) + level number: `CHE300`, `Com400`, `Pet500`

See **`rep_passwords_REFERENCE.txt`** for the full table of all 282 entries with defaults and hashes.

---

## 📁 Data Repo Structure

```
futo-attendance-data/
├── active_attendances.json
└── attendances/
    └── School_of_Engineering.../
        └── Chemical_Engineering/
            └── 300L/
                ├── CHE401_2025-02-20_09-15-00.csv
                └── CHE401_2025-02-20_09-15-00_devices.json
```

---

## 📱 How It Works

**Course Reps:** Login → Start attendance with course code → Share the rotating 4-digit code verbally → Monitor entries → Edit if needed → End attendance

**Students:** Select school/dept/level → Enter 4-digit code from rep → Enter name + matric → Submit (one per device)

---

## ⚙️ Rules

- No overlapping attendances for the same school/dept/level
- Duplicate names (case-insensitive) and matric numbers are rejected
- Codes change every 10 seconds; old codes instantly invalid
- One submission per device per session (encrypted cookies)

---

## 📦 Files

| File | Purpose |
|------|---------|
| `Home.py` | Landing page |
| `pages/1_Course_Rep.py` | Rep login + dashboard |
| `pages/2_Student_Recorder.py` | Student sign-in |
| `futo_data.py` | FUTO schools & departments database |
| `github_storage.py` | GitHub API layer |
| `utils.py` | Hashing, code gen, CSV helpers |
| `rep_passwords.json` | **Edit this to change passwords** |
| `rep_passwords_REFERENCE.txt` | All defaults + hashes for reference |
| `requirements.txt` | Dependencies |
