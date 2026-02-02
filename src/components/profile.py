import streamlit as st
from src.db import get_db
from src.auth import hash_password, get_user_by_username

def render_profile_page():
    st.title("👤 My Profile")
    
    st.markdown(f"""
    **Username:** {st.session_state.username}  
    **Role:** {'Admin' if st.session_state.get('is_admin') else 'User'}
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
                db = next(get_db())
                user = get_user_by_username(db, st.session_state.username)
                if user:
                    user.password_hash = hash_password(new_pass)
                    db.commit()
                    st.success("Password updated successfully!")
                else:
                    st.error("User not found.")
