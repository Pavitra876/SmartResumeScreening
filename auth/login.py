"""
auth/login.py
Handles user registration and login.
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
    database.create_user(name, email, hash_password(password), role)
    return True, "Account created successfully! Please log in."


def login_user(email, password):
    user = database.get_user_by_email(email)
    if user is None:
        return False, None, "No account found with that email."
    if user["password_hash"] != hash_password(password):
        return False, None, "Incorrect password."
    return True, user, "Login successful."


def show_auth_page():
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #0D1B2A 0%, #1B0D2A 50%, #0A1628 100%) !important;
        }
        .stApp::before {
            content: '';
            position: fixed;
            top: -10%; left: -5%;
            width: 500px; height: 500px;
            background: radial-gradient(circle, rgba(16,185,129,0.28) 0%, transparent 65%);
            border-radius: 50%;
            animation: float1 8s ease-in-out infinite;
            pointer-events: none; z-index: 0;
        }
        .stApp::after {
            content: '';
            position: fixed;
            bottom: -10%; right: -5%;
            width: 450px; height: 450px;
            background: radial-gradient(circle, rgba(139,92,246,0.28) 0%, transparent 65%);
            border-radius: 50%;
            animation: float2 10s ease-in-out infinite;
            pointer-events: none; z-index: 0;
        }
        @keyframes float1 {
            0%, 100% { transform: translate(0, 0); }
            50% { transform: translate(30px, 30px); }
        }
        @keyframes float2 {
            0%, 100% { transform: translate(0, 0); }
            50% { transform: translate(-30px, -25px); }
        }
        .login-glass {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.13);
            border-radius: 20px;
            padding: 2rem 1.8rem;
            backdrop-filter: blur(16px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.5);
        }
        .stTextInput input {
            background-color: rgba(255,255,255,0.07) !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            border-radius: 10px !important;
            color: #F1F5F9 !important;
        }
        .stTextInput input:focus {
            border-color: #10B981 !important;
            box-shadow: 0 0 0 2px rgba(16,185,129,0.25) !important;
        }
        .stTextInput label { color: #94A3B8 !important; }
        .stTabs [data-baseweb="tab-list"] {
            background: transparent !important;
            border-bottom: 1px solid rgba(255,255,255,0.1) !important;
        }
        .stTabs [data-baseweb="tab"] { color: #64748B !important; font-weight: 600 !important; }
        .stTabs [aria-selected="true"] { color: #10B981 !important; }
        .stApp h1, .stApp h2, .stApp h3 { color: #F1F5F9 !important; }
        .stApp p { color: #94A3B8 !important; }
        .stSelectbox div[data-baseweb="select"] > div {
            background-color: rgba(255,255,255,0.07) !important;
            border-color: rgba(255,255,255,0.15) !important;
            color: #F1F5F9 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    col_l, col_mid, col_r = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("""
        <div style="text-align:center; margin-top:3rem; margin-bottom:1.8rem;">
            <div style="display:inline-flex; align-items:center; gap:8px; margin-bottom:0.8rem;">
                <div style="width:8px; height:8px; border-radius:50%;
                            background:#10B981; box-shadow:0 0 12px #10B981;"></div>
                <span style="color:#10B981; font-size:0.75rem; font-weight:700;
                             letter-spacing:0.18em; text-transform:uppercase;">
                    AI-Powered Resume Analysis
                </span>
                <div style="width:8px; height:8px; border-radius:50%;
                            background:#10B981; box-shadow:0 0 12px #10B981;"></div>
            </div>
            <h1 style="color:#FFFFFF !important; font-size:2.3rem; font-weight:800;
                       margin:0 0 0.3rem 0; text-shadow:0 0 40px rgba(16,185,129,0.35);">
                Smart Resume Screening
            </h1>
            <p style="color:#64748B; margin:0; font-size:0.95rem;">
                Career Improvement System
            </p>
        </div>
        """, unsafe_allow_html=True)

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

def logout():
    for key in ["logged_in", "user_id", "user_name", "user_role"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()