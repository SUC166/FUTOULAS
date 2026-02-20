import streamlit as st

st.set_page_config(
    page_title="FUTO Attendance System",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("📋 FUTO Attendance System")
st.caption("Federal University of Technology, Owerri")

st.markdown("""
---

### Welcome! Choose your role from the sidebar:

**📌 Course Rep** — Start/manage attendance sessions  
**🎓 Student Recorder** — Sign into an active attendance

---

### Quick Guide

**Course Reps:**
1. Login with your school, department, level & password
2. Type a course code and click **Start Attendance**
3. A 4-digit code appears — share it verbally with students in the hall
4. The code changes every 10 seconds (old codes stop working immediately)
5. View entries live, manually add students, or edit entries
6. Click **End Attendance** when done — CSV is saved automatically

**Students:**
1. Pick your school, department and level
2. If attendance is open, enter the 4-digit code from your rep
3. Enter your name (Surname, First, Middle) and matric number
4. Done — one entry per device, no re-entry allowed

---

> 💡 **Tip for Course Reps:** Your default password is the first 3 letters of your  
> department name (uppercase) followed by your level.  
> *Example: Chemical Engineering, 300L → **CHE300***
""")
