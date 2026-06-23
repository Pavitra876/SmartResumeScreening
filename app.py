import streamlit as st
import database
from auth import login

st.set_page_config(page_title="Smart Resume Screening", page_icon="📄", layout="wide")

# Make sure the database and tables exist every time the app starts.
database.init_db()

# Initialize session_state keys if they don't exist yet.
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False


def show_dashboard():
    """Shown once a user is logged in."""
    st.title("📄 Smart Resume Screening and Career Improvement System")
    st.write(f"Welcome, **{st.session_state['user_name']}**! 👋")
    st.write(f"Account type: `{st.session_state['user_role']}`")

    if st.sidebar.button("Logout"):
        login.logout()

    st.info("Next: we'll add resume upload, ATS scoring, and skill gap analysis here.")


# Main routing: show login/register page, or the dashboard, based on session state.
if st.session_state["logged_in"]:
    show_dashboard()
else:
    login.show_auth_page()