import uuid
import json
import streamlit as st

st.set_page_config(page_title="Student Recorder — FUTO Attendance", page_icon="🎓", layout="centered")

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from futo_data import get_schools, get_departments, get_levels
from utils import is_code_valid, is_dup_name, is_dup_matric, entries_to_csv, csv_to_entries, now_str
import github_storage as gs

# ─── Device ID via cookies ────────────────────────────────────────────────────
# We use streamlit-cookies-manager. If not available, fallback to session state.
COOKIES_AVAILABLE = False
cookies = None

try:
    from streamlit_cookies_manager import EncryptedCookieManager
    cookies = EncryptedCookieManager(
        prefix="futo_att_",
        password="futo_att_device_secret_2025"
    )
    if cookies.ready():
        COOKIES_AVAILABLE = True
    else:
        st.stop()
except ImportError:
    pass
except Exception:
    pass


def get_device_id():
    if COOKIES_AVAILABLE and cookies is not None:
        did = cookies.get("device_id", "")
        if not did:
            did = str(uuid.uuid4())
            cookies["device_id"] = did
            cookies.save()
        return did
    # Fallback
    if "device_id" not in st.session_state:
        st.session_state.device_id = str(uuid.uuid4())
    return st.session_state.device_id


def device_already_signed(device_id, csv_path):
    dev_path = gs.get_devices_path(csv_path)
    content, _ = gs.read_file(dev_path)
    if content is None:
        return False
    try:
        return device_id in json.loads(content)
    except Exception:
        return False


def register_device(device_id, csv_path):
    dev_path = gs.get_devices_path(csv_path)
    content, sha = gs.read_file(dev_path)
    try:
        devices = json.loads(content) if content else []
    except Exception:
        devices = []
    if device_id not in devices:
        devices.append(device_id)
    gs.write_file(dev_path, json.dumps(devices), "Register device", sha)


# ─── Main ─────────────────────────────────────────────────────────────────────
st.title("🎓 Student Attendance Sign-In")
st.caption("Federal University of Technology, Owerri")

device_id = get_device_id()

# Step 1 — Location
st.subheader("Step 1: Select Your Details")
school = st.selectbox("School", ["— Select School —"] + get_schools())
if school.startswith("—"):
    st.stop()

dept = st.selectbox("Department", ["— Select Department —"] + get_departments(school))
if dept.startswith("—"):
    st.stop()

levels = get_levels(school, dept)
level_disp = st.selectbox("Level", ["— Select Level —"] + [f"{l}L" for l in levels])
if level_disp.startswith("—"):
    st.stop()
level = level_disp.replace("L", "")

st.divider()

# Step 2 — Check active attendance
with st.spinner("Checking for active attendance..."):
    active_all, _ = gs.get_active_attendances()

key = gs.att_key(school, dept, level)

if key not in active_all:
    st.warning("⚠️ **No active attendance** found for your school/department/level.")
    st.caption("Ask your course rep if attendance is currently running.")
    st.stop()

session = active_all[key]
course_code = session["course_code"]
started_at = session["started_at"]
csv_path = session["csv_path"]

st.success(f"✅ Active attendance found: **{course_code}**")

# Check if device already signed
if device_already_signed(device_id, csv_path):
    st.info("✅ You have already signed this attendance from this device.")
    st.caption("Each device can only sign once per attendance session.")
    st.stop()

st.divider()

# Step 3 — Enter Code
st.subheader("Step 2: Enter the 4-Digit Code")
st.caption("Ask your course rep for the current code. Only works if you're in the lecture hall.")

entered_code = st.text_input("4-Digit Code", max_chars=4, placeholder="e.g. 4782").strip()

if not entered_code:
    st.stop()

if not is_code_valid(entered_code, started_at):
    st.error("❌ Wrong or expired code. The code changes every 10 seconds — ask your rep for the latest one.")
    st.stop()

st.success("✅ Code accepted! Fill in your details below.")
st.divider()

# Step 4 — Student Details
st.subheader("Step 3: Enter Your Details")
st.caption("Double-check before submitting — you cannot change your entry afterwards.")

with st.form("student_form"):
    f1, f2, f3 = st.columns(3)
    with f1: surname = st.text_input("Surname*")
    with f2: first = st.text_input("First Name*")
    with f3: middle = st.text_input("Middle Name")
    matric = st.text_input("Matric Number*", placeholder="e.g. 2021/ND/12345")
    submit = st.form_submit_button("✅ Submit Attendance", type="primary")

if submit:
    if not surname or not first or not matric:
        st.error("Surname, First Name and Matric Number are required.")
        st.stop()

    # Revalidate code (may have expired during form fill)
    if not is_code_valid(entered_code, started_at):
        st.error("⏱️ The code expired while you were filling in. Get the new code from your rep.")
        st.stop()

    # Load current entries for duplicate check
    content, csv_sha = gs.read_file(csv_path)
    entries = csv_to_entries(content) if content else []

    if is_dup_name(surname, first, middle, entries):
        st.error("❌ A student with that name is already in this attendance.")
        st.stop()
    if is_dup_matric(matric, entries):
        st.error("❌ That matric number is already registered in this attendance.")
        st.stop()

    # Write entry
    entry = {
        "surname": surname.strip().upper(),
        "first_name": first.strip().upper(),
        "middle_name": middle.strip().upper(),
        "matric": matric.strip().upper(),
        "timestamp": now_str(),
    }
    entries.append(entry)
    gs.write_file(csv_path, entries_to_csv(entries), "Add student entry", csv_sha)

    # Lock this device
    register_device(device_id, csv_path)

    st.balloons()
    st.success(
        f"🎉 **Attendance recorded!**  \n"
        f"Name: **{entry['surname']} {entry['first_name']} {entry['middle_name']}**  \n"
        f"Matric: **{entry['matric']}**  \n"
        f"Course: **{course_code}**"
    )
    st.info("You're marked present. You cannot sign again from this device for this session.")
