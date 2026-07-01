"""
auth/login.py
Handles user registration and login for the
Smart Resume Screening and Career Improvement System.
"""

import hashlib
import streamlit as st
import database


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(name, email, password, role="student"):
    if not name or not email or not password:
        return False, "Please fill in all fields."
    existing = database.get_user_by_email(email)
    if existing is not None:
        return False, "An account with this email already exists."
    password_hash = hash_password(password)
    database.create_user(name, email, password_hash, role)
    return True, "Account created successfully! Please log in."


def login_user(email, password):
    user = database.get_user_by_email(email)
    if user is None:
        return False, None, "No account found with that email."
    if user["password_hash"] != hash_password(password):
        return False, None, "Incorrect password."
    return True, user, "Login successful."


def show_auth_page():
    """Renders the login/register UI with a modern dark AI-style background."""
    import theme

    st.markdown("""
    <style>
        .stApp {
            background: #060B18 !important;
        }
        .stApp::before {
            content: '';
            position: fixed;
            top: -20%;
            left: -10%;
            width: 600px;
            height: 600px;
            background: radial-gradient(circle, rgba(16,185,129,0.15) 0%, transparent 70%);
            border-radius: 50%;
            animation: float1 8s ease-in-out infinite;
            pointer-events: none;
            z-index: 0;
        }
        .stApp::after {
            content: '';
            position: fixed;
            bottom: -20%;
            right: -10%;
            width: 500px;
            height: 500px;
            background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%);
            border-radius: 50%;
            animation: float2 10s ease-in-out infinite;
            pointer-events: none;
            z-index: 0;
        }
        @keyframes float1 {
            0%, 100% { transform: translate(0, 0); }
            50% { transform: translate(40px, 40px); }
        }
        @keyframes float2 {
            0%, 100% { transform: translate(0, 0); }
            50% { transform: translate(-40px, -30px); }
        }
        .login-glass {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.10);
            border-radius: 20px;
            padding: 2.5rem 2rem;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            margin-top: 1rem;
        }
        .stTextInput input {
            background-color: rgba(255,255,255,0.06) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            border-radius: 10px !important;
            color: #F1F5F9 !important;
            padding: 0.6rem 0.9rem !important;
        }
        .stTextInput input:focus {
            border-color: #10B981 !important;
            box-shadow: 0 0 0 2px rgba(16,185,129,0.2) !important;
        }
        .stTextInput label {
            color: #94A3B8 !important;
            font-size: 0.85rem !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            background: transparent !important;
            border-bottom: 1px solid rgba(255,255,255,0.1) !important;
        }
        .stTabs [data-baseweb="tab"] {
            color: #64748B !important;
            font-weight: 600 !important;
        }
        .stTabs [aria-selected="true"] {
            color: #10B981 !important;
            border-bottom-color: #10B981 !important;
        }
        .stApp h2, .stApp h3 {
            color: #F1F5F9 !important;
        }
        .stSelectbox div[data-baseweb="select"] > div {
            background-color: rgba(255,255,255,0.06) !important;
            border-color: rgba(255,255,255,0.12) !important;
            color: #F1F5F9 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    col_l, col_mid, col_r = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("""
        <div style="text-align:center; margin-top:3rem; margin-bottom:1.5rem;">
            <div style="display:inline-flex; align-items:center; gap:10px; margin-bottom:0.5rem;">
                <div style="width:10px; height:10px; border-radius:50%;
                            background:#10B981; box-shadow:0 0 12px #10B981;"></div>
                <span style="color:#10B981; font-size:0.8rem; font-weight:700;
                             letter-spacing:0.15em; text-transform:uppercase;">
                    AI-Powered Resume Analysis
                </span>
                <div style="width:10px; height:10px; border-radius:50%;
                            background:#10B981; box-shadow:0 0 12px #10B981;"></div>
            </div>
            <h1 style="color:#F8FAFC !important; font-size:2.2rem;
                       font-weight:800; margin:0; line-height:1.2;">
                Smart Resume Screening
            </h1>
            <p style="color:#64748B; margin-top:0.4rem; font-size:0.95rem;">
                Career Improvement System
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="login-glass">', unsafe_allow_html=True)

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

        st.markdown('</div>', unsafe_allow_html=True)


def logout():
    for key in ["logged_in", "user_id", "user_name", "user_role"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()