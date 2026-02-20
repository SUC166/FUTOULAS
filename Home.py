import streamlit as st

st.set_page_config(
    page_title="FUTO ULAS — Unified Lecture Attendance System",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="expanded",
)

from components import footer, APP_FULL, CREDIT

st.markdown(
    f"""<div style="margin-bottom:2px">
    <span style="color:#888;font-size:12px;letter-spacing:1px">{APP_FULL}</span>
    </div>""",
    unsafe_allow_html=True,
)
st.title("📋 FUTO ULAS")
st.caption("Federal University of Technology, Owerri")

st.markdown("""
---

### Welcome — choose your role from the sidebar:

**📌 Course Rep** — Start and manage attendance sessions  
**🎓 Student Recorder** — Sign into an active attendance

---

### How It Works

**Course Reps:**
1. Log in with your school, department, level and password
2. Enter a course code and click **Start Attendance**
3. A 4-digit code appears on screen — **tell students verbally**, do not show them your screen
4. The code changes every 10 seconds; old codes stop working immediately
5. View incoming entries live, manually add students, or edit any entry
6. Click **End Attendance** when done — the CSV is saved automatically

**Students:**
1. Pick your school, department and level
2. If attendance is open, enter the 4-digit code from your rep
3. Enter your name (Surname, First, Middle) and matric number
4. Done — one entry per device per session

---

> 💡 **Default password for reps:** first 3 letters of your department (uppercase) + level  
> *e.g. Chemical Engineering · 300L → **CHE300***
""")

footer()
