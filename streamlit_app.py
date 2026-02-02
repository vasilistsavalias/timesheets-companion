import streamlit as st
from src.database.manager import DatabaseManager
from src.ui.auth_ui import render_login, render_sidebar
from src.components.timesheet_ui import render_timesheet_tool # Reuse your existing logic

# Initialize DB on startup
manager = DatabaseManager()
manager.create_tables()

st.set_page_config(page_title="timesheets-companion", page_icon="🚀", layout="wide")

if "auth_user" not in st.session_state:
    render_login()
else:
    render_sidebar()
    render_timesheet_tool()
