import streamlit as st
from src.database.manager import get_db_session
from src.services.auth_service import AuthService
from src.database.models import User

def render_profile_page():
    st.title("👤 My Profile")
    
    user = st.session_state.auth_user
    
    st.markdown(f"""
    **Username:** {user.username}  
    **Name:** {user.name or 'N/A'}
    **Role:** {'Admin' if getattr(user, 'is_admin', False) else 'User'}
    """)
    
    st.divider()
    
    st.subheader("Update Password")
    with st.form("password_change"):
        new_pass = st.text_input("New Password", type="password")
        confirm_pass = st.text_input("Confirm New Password", type="password")
        btn = st.form_submit_button("Update Password")
        
        if btn:
            if new_pass != confirm_pass:
                st.error("Passwords do not match!")
            elif len(new_pass) < 4:
                st.error("Password too short.")
            else:
                db = get_db_session()
                # Refresh user from DB to be safe
                db_user = db.query(User).filter(User.username == user.username).first()
                if db_user:
                    db_user.password_hash = AuthService.hash_password(new_pass)
                    db.commit()
                    st.success("Password updated successfully!")
                else:
                    st.error("User not found.")