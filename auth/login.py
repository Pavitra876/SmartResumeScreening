"""
auth/login.py
Handles user registration and login for the
Smart Resume Screening and Career Improvement System.
"""

import hashlib
import streamlit as st
import database


def hash_password(password: str) -> str:
    """Convert a plain text password into a secure hash.
    We store this hash, never the real password."""
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(name, email, password, role="student"):
    """Create a new user account. Returns (success: bool, message: str)."""
    if not name or not email or not password:
        return False, "Please fill in all fields."

    existing = database.get_user_by_email(email)
    if existing is not None:
        return False, "An account with this email already exists."

    password_hash = hash_password(password)
    database.create_user(name, email, password_hash, role)
    return True, "Account created successfully! Please log in."


def login_user(email, password):
    """Check email/password against the database.
    Returns (success: bool, user_row_or_None, message: str)."""
    user = database.get_user_by_email(email)
    if user is None:
        return False, None, "No account found with that email."

    if user["password_hash"] != hash_password(password):
        return False, None, "Incorrect password."

    return True, user, "Login successful."


def show_auth_page():
    """Renders the login/register UI. Call this from app.py when no user is logged in."""
    import theme

    col_l, col_mid, col_r = st.columns([1, 1.4, 1])
    with col_mid:
        st.markdown(
            """
            <div style="text-align:center; margin-top:2.5rem; margin-bottom:0.5rem;">
                <div style="font-size:2.4rem;">📄</div>
                <h1 style="margin-bottom:0;">Smart Resume Screening</h1>
                <p style="color:#64748B; margin-top:0.2rem; font-size:1rem;">
                    & Career Improvement System
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        theme.card_open()
        tab_login, tab_register = st.tabs(["Login", "Register"])

        with tab_login:
            st.subheader("Welcome back")
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")

            if st.button("Login", key="login_button", type="primary", use_container_width=True):
                success, user, message = login_user(login_email, login_password)
                if success:
                    st.session_state["logged_in"] = True
                    st.session_state["user_id"] = user["user_id"]
                    st.session_state["user_name"] = user["name"]
                    st.session_state["user_role"] = user["role"]
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

        with tab_register:
            st.subheader("Create your account")
            reg_name = st.text_input("Full Name", key="reg_name")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            reg_role = st.selectbox("Account Type", ["student", "admin"], key="reg_role")

            if st.button("Register", key="register_button", type="primary", use_container_width=True):
                success, message = register_user(reg_name, reg_email, reg_password, reg_role)
                if success:
                    st.success(message)
                else:
                    st.error(message)
        theme.card_close()


def logout():
    """Clear session state to log the user out."""
    for key in ["logged_in", "user_id", "user_name", "user_role"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()