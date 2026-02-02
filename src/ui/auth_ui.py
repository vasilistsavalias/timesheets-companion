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
                # Initialize navigation state
                if "current_page" not in st.session_state:
                    st.session_state.current_page = "dashboard"
                st.rerun()
            else:
                st.error("Invalid credentials.")

def render_sidebar():
    with st.sidebar:
        user = st.session_state.auth_user
        st.write(f"Welcome, **{user.name or user.username}**!")
        
        if st.button("Logout"):
            del st.session_state.auth_user
            if "current_page" in st.session_state:
                del st.session_state.current_page
            st.rerun()
            
        st.markdown("---")
        st.subheader("Go to")
        
        # Navigation Buttons
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()
            
        if st.button("👤 My Profile", use_container_width=True):
            st.session_state.current_page = "profile"
            st.rerun()
            
        # Admin Only Link
        if getattr(user, 'is_admin', False):
            if st.button("👥 User Management", use_container_width=True):
                st.session_state.current_page = "admin"
                st.rerun()