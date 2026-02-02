import streamlit as st
from src.database.manager import DatabaseManager
from src.ui.auth_ui import render_login, render_sidebar
from src.components.timesheet_ui import render_timesheet_tool
from src.components.profile import render_profile_page
from src.components.admin import render_admin_page

# Initialize DB on startup
manager = DatabaseManager()
manager.create_tables()

st.set_page_config(page_title="timesheets-companion", page_icon="🚀", layout="wide")

if "auth_user" not in st.session_state:
    render_login()
else:
    render_sidebar()
    
    # Routing based on session state
    page = st.session_state.get("current_page", "dashboard")
    
    if page == "dashboard":
        render_timesheet_tool()
    elif page == "profile":
        render_profile_page()
    elif page == "admin":
        if getattr(st.session_state.auth_user, 'is_admin', False):
            render_admin_page()
        else:
            st.error("Access Denied.")
            st.session_state.current_page = "dashboard"
            st.rerun()