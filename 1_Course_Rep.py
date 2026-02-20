import time
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Course Rep — FUTO Attendance", page_icon="📌", layout="wide")

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from futo_data import get_schools, get_departments, get_levels
from utils import (verify_rep_login, get_current_code, entries_to_csv,
                   csv_to_entries, is_dup_name, is_dup_matric, now_str, date_str, time_str)
import github_storage as gs


# ─── Session state ────────────────────────────────────────────────────────────
for k, v in {
    "rep_logged_in": False, "rep_school": None, "rep_dept": None, "rep_level": None,
    "active_session": None, "current_entries": [], "csv_path": None, "confirm_end": False,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─── Login ────────────────────────────────────────────────────────────────────
def show_login():
    st.title("📌 Course Rep Login")
    st.caption("FUTO Attendance System")

    schools = get_schools()
    school = st.selectbox("Select Your School", ["— Select School —"] + schools)
    if school.startswith("—"):
        return

    depts = get_departments(school)
    dept = st.selectbox("Select Your Department", ["— Select Department —"] + depts)
    if dept.startswith("—"):
        return

    levels = get_levels(school, dept)
    level = st.selectbox("Select Your Level", ["— Select Level —"] + [f"{l}L" for l in levels])
    if level.startswith("—"):
        return
    level_num = level.replace("L", "")

    st.info(f"🔑 Default password: **{dept.replace(' ', '')[:3].upper()}{level_num}**  "
            f"(Contact admin to change)")
    password = st.text_input("Password", type="password")

    if st.button("Login →", type="primary"):
        custom_hashes, _ = gs.get_custom_passwords()
        if verify_rep_login(school, dept, level_num, password, custom_hashes):
            st.session_state.rep_logged_in = True
            st.session_state.rep_school = school
            st.session_state.rep_dept = dept
            st.session_state.rep_level = level_num
            st.rerun()
        else:
            st.error("❌ Incorrect password.")


# ─── Helpers ──────────────────────────────────────────────────────────────────
def reload_session():
    school = st.session_state.rep_school
    dept = st.session_state.rep_dept
    level = st.session_state.rep_level
    key = gs.att_key(school, dept, level)
    active_all, _ = gs.get_active_attendances()
    if key in active_all:
        sess = active_all[key]
        st.session_state.active_session = sess
        csv_path = sess.get("csv_path", "")
        st.session_state.csv_path = csv_path
        content, _ = gs.read_file(csv_path)
        st.session_state.current_entries = csv_to_entries(content) if content else []
    else:
        st.session_state.active_session = None
        st.session_state.current_entries = []


def save_entries(entries):
    csv_str = entries_to_csv(entries)
    _, sha = gs.read_file(st.session_state.csv_path)
    gs.write_file(st.session_state.csv_path, csv_str, "Update attendance entries", sha)
    st.session_state.current_entries = entries


# ─── Dashboard ────────────────────────────────────────────────────────────────
def show_dashboard():
    school = st.session_state.rep_school
    dept = st.session_state.rep_dept
    level = st.session_state.rep_level

    col_title, col_logout = st.columns([7, 1])
    with col_title:
        st.title("📌 Course Rep Dashboard")
        st.caption(f"**{school}** · {dept} · {level}L")
    with col_logout:
        st.write("")
        st.write("")
        if st.button("Logout"):
            for k in ["rep_logged_in","rep_school","rep_dept","rep_level",
                      "active_session","current_entries","csv_path","confirm_end"]:
                st.session_state[k] = False if k == "rep_logged_in" else ([] if k == "current_entries" else None)
            st.rerun()

    st.divider()

    # Only reload session from GitHub when NOT on the attendance tab with an active session
    # (to avoid disrupting the auto-refresh loop with extra API calls)
    reload_session()

    tab_att, tab_edit, tab_download = st.tabs(["📋 Attendance", "✏️ Edit Entries", "📥 Download Records"])

    with tab_att:
        show_attendance_tab(school, dept, level)
    with tab_edit:
        show_edit_tab()
    with tab_download:
        show_download_tab(school, dept, level)


# ─── Attendance Tab ───────────────────────────────────────────────────────────
def show_attendance_tab(school, dept, level):
    active = st.session_state.active_session

    if active is None:
        st.subheader("Start Attendance")
        course_code = st.text_input("Course Code", placeholder="e.g. CHE 401").strip().upper()
        if st.button("▶ Start Attendance", type="primary"):
            if not course_code:
                st.error("Enter a course code first.")
                return
            active_all, sha = gs.get_active_attendances()
            own_key = gs.att_key(school, dept, level)
            if own_key in active_all:
                st.error("You already have an active attendance.")
                return
            d, t = date_str(), time_str()
            csv_path = gs.get_csv_path(school, dept, level, course_code, d, t)
            gs.write_file(csv_path, entries_to_csv([]), "Start attendance", None)
            sess = {
                "school": school, "dept": dept, "level": level,
                "course_code": course_code, "started_at": time.time(),
                "date": d, "start_time": t, "csv_path": csv_path,
            }
            active_all[own_key] = sess
            gs.set_active_attendances(active_all, sha)
            st.session_state.active_session = sess
            st.session_state.current_entries = []
            st.session_state.csv_path = csv_path
            st.success(f"✅ Attendance started for **{course_code}**")
            st.rerun()
        return

    course_code = active["course_code"]
    started_at = active["started_at"]

    st.subheader(f"🟢 Active Attendance — {course_code}")
    st.caption(f"Started {active['date']} at {active['start_time'].replace('-', ':')}")

    # ── AUTO-REFRESH: re-runs the page every 1 second so the code updates live ──
    # We use st_autorefresh which fires a JS setInterval rerun.
    # Import here so it only runs when there's an active session.
    try:
        from streamlit_autorefresh import st_autorefresh
        # Run every 1000ms (1 second). The key avoids conflicts with other widgets.
        st_autorefresh(interval=1000, limit=None, key="code_autorefresh")
    except ImportError:
        st.warning("⚠️ Install `streamlit-autorefresh` for live code updates. Using manual refresh for now.")
        if st.button("🔄 Refresh Code"):
            st.rerun()

    # Code display - recomputed every rerun = live update
    code, slot, secs_left = get_current_code(started_at)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"""<div style="background:#1a1a2e;border-radius:16px;padding:24px;text-align:center;border:2px solid #00ff88">
            <p style="color:#aaa;margin:0;font-size:13px;letter-spacing:2px">CURRENT CODE</p>
            <h1 style="color:#00ff88;font-size:72px;letter-spacing:12px;margin:8px 0;font-family:monospace">{code}</h1>
            <p style="color:#666;font-size:12px">Tell students this verbally — do NOT show them your screen</p>
            </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(
            f"""<div style="background:#1a1a2e;border-radius:16px;padding:24px;text-align:center;border:2px solid #ffb800">
            <p style="color:#aaa;margin:0;font-size:13px;letter-spacing:2px">REFRESHES IN</p>
            <h1 style="color:#ffb800;font-size:72px;margin:8px 0">{int(secs_left)}s</h1>
            <p style="color:#666;font-size:12px">Code changes every 10 seconds — old codes stop working immediately</p>
            </div>""", unsafe_allow_html=True)

    st.divider()

    # Manual add
    st.subheader("➕ Manually Add Student")
    with st.form("manual_add"):
        mc1, mc2, mc3 = st.columns(3)
        with mc1: surname = st.text_input("Surname*")
        with mc2: first = st.text_input("First Name*")
        with mc3: middle = st.text_input("Middle Name")
        matric = st.text_input("Matric Number*")
        add_btn = st.form_submit_button("Add Student")

    if add_btn:
        entries = st.session_state.current_entries
        if not surname or not first or not matric:
            st.error("Surname, First Name and Matric Number are required.")
        elif is_dup_name(surname, first, middle, entries):
            st.error("A student with that name is already in this attendance.")
        elif is_dup_matric(matric, entries):
            st.error("That matric number is already in this attendance.")
        else:
            entries.append({
                "surname": surname.strip().upper(),
                "first_name": first.strip().upper(),
                "middle_name": middle.strip().upper(),
                "matric": matric.strip().upper(),
                "timestamp": now_str(),
            })
            save_entries(entries)
            st.success(f"Added: {surname.upper()} {first.upper()}")
            st.rerun()

    # Entries table
    entries = st.session_state.current_entries
    st.subheader(f"📝 Current Entries ({len(entries)} students)")
    if st.button("🔄 Refresh List"):
        reload_session()
        st.rerun()
    if entries:
        df = pd.DataFrame([{
            "S/N": i+1, "Surname": e["surname"], "First Name": e["first_name"],
            "Middle Name": e["middle_name"], "Matric No.": e["matric"], "Time": e["timestamp"],
        } for i, e in enumerate(entries)])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No entries yet. Students can sign in from the Student Recorder page.")

    st.divider()

    # End Attendance
    st.subheader("🔴 End Attendance")
    if not st.session_state.confirm_end:
        if st.button("End Attendance", type="secondary"):
            st.session_state.confirm_end = True
            st.rerun()
    else:
        st.warning(f"Confirm ending attendance for **{course_code}**?  \n"
                   "The CSV will be saved and the session closed.")
        yes_col, no_col = st.columns(2)
        with yes_col:
            if st.button("✅ Yes, End It", type="primary"):
                own_key = gs.att_key(school, dept, level)
                active_all, sha = gs.get_active_attendances()
                active_all.pop(own_key, None)
                gs.set_active_attendances(active_all, sha)
                st.session_state.active_session = None
                st.session_state.current_entries = []
                st.session_state.confirm_end = False
                st.success(f"✅ Attendance for **{course_code}** ended and saved.")
                st.balloons()
                time.sleep(1)
                st.rerun()
        with no_col:
            if st.button("❌ Cancel"):
                st.session_state.confirm_end = False
                st.rerun()


# ─── Edit Tab ─────────────────────────────────────────────────────────────────
def show_edit_tab():
    st.subheader("✏️ Edit Attendance Entries")
    if not st.session_state.active_session:
        st.info("No active attendance session.")
        return
    entries = st.session_state.current_entries
    if not entries:
        st.info("No entries to edit yet.")
        return

    idx = st.selectbox(
        "Select entry",
        range(len(entries)),
        format_func=lambda i: f"{i+1}. {entries[i]['surname']} {entries[i]['first_name']} — {entries[i]['matric']}"
    )
    e = entries[idx]

    with st.form("edit_form"):
        ec1, ec2, ec3 = st.columns(3)
        with ec1: new_sn = st.text_input("Surname", value=e["surname"])
        with ec2: new_fn = st.text_input("First Name", value=e["first_name"])
        with ec3: new_mn = st.text_input("Middle Name", value=e["middle_name"])
        new_mat = st.text_input("Matric Number", value=e["matric"])
        sc, dc = st.columns(2)
        with sc: save_btn = st.form_submit_button("💾 Save")
        with dc: del_btn = st.form_submit_button("🗑️ Delete")

    others = [e2 for i, e2 in enumerate(entries) if i != idx]

    if save_btn:
        if not new_sn or not new_fn or not new_mat:
            st.error("Required fields missing.")
        elif is_dup_name(new_sn, new_fn, new_mn, others):
            st.error("Duplicate name.")
        elif is_dup_matric(new_mat, others):
            st.error("Duplicate matric number.")
        else:
            entries[idx] = {"surname": new_sn.strip().upper(), "first_name": new_fn.strip().upper(),
                            "middle_name": new_mn.strip().upper(), "matric": new_mat.strip().upper(),
                            "timestamp": e["timestamp"]}
            save_entries(entries)
            st.success("Entry updated!")
            st.rerun()

    if del_btn:
        entries.pop(idx)
        save_entries(entries)
        st.success("Entry deleted.")
        st.rerun()


# ─── Download Tab ─────────────────────────────────────────────────────────────
def show_download_tab(school, dept, level):
    st.subheader("📥 Download Attendance Records")
    st.caption(f"{dept} · {level}L — all sessions (past and present)")

    with st.spinner("Fetching records..."):
        files = gs.list_attendance_csvs(school, dept, level)

    if not files:
        st.info("No records found yet.")
        return

    for fpath in files:
        fname = fpath.split("/")[-1]
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"📄 `{fname}`")
        with col2:
            content, _ = gs.read_file(fpath)
            if content:
                st.download_button(
                    "⬇️ Download", data=content, file_name=fname,
                    mime="text/csv", key=f"dl_{fpath}"
                )


# ─── Entry ────────────────────────────────────────────────────────────────────
if not st.session_state.rep_logged_in:
    show_login()
else:
    show_dashboard()
