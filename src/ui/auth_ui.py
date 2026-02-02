import streamlit as st
from src.services.auth_service import AuthService
from src.database.manager import get_db_session

def render_login():
    st.title("🔐 timesheets-companion")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            db = get_db_session()
            user = AuthService.authenticate(db, username, password)
            if user:
                st.session_state.auth_user = user
                st.rerun()
            else:
                st.error("Invalid credentials.")

def render_sidebar():
    with st.sidebar:
        st.write(f"Logged in as: **{st.session_state.auth_user.name}**")
        if st.button("Logout"):
            del st.session_state.auth_user
            st.rerun()
