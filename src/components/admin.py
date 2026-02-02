import streamlit as st
import pandas as pd
from src.database.manager import get_db_session
from src.database.models import User
from src.services.auth_service import AuthService

def render_admin_page():
    st.title("👥 User Management (Admin Console)")
    st.info("Manage application access and user roles.")
    
    tab1, tab2 = st.tabs(["Manage Users", "Add New User"])
    
    db = get_db_session()
    
    # --- TAB 1: LIST & EDIT ---
    with tab1:
        users = db.query(User).all()
        
        # Display Table
        data = [{"ID": u.id, "Username": u.username, "Name": u.name, "Role": "admin" if u.is_admin else "user", "Created At": u.created_at} for u in users]
        st.dataframe(pd.DataFrame(data), use_container_width=True)
        
        st.divider()
        st.subheader("Edit User Role & Access")
        
        # User Selection
        user_options = {u.username: u for u in users}
        selected_username = st.selectbox("Select User to Edit/Delete", list(user_options.keys()))
        
        if selected_username:
            selected_user = user_options[selected_username]
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                with st.form("edit_role"):
                    st.write(f"**Edit Role for {selected_username}**")
                    new_role = st.selectbox("Role", ["user", "admin"], index=0 if not selected_user.is_admin else 1)
                    if st.form_submit_button("Update Role"):
                        selected_user.is_admin = (new_role == "admin")
                        db.commit()
                        st.success(f"Updated {selected_username} to {new_role}.")
                        st.rerun()
            
            with col2:
                st.write("**Danger Zone**")
                if st.button("🗑️ Delete User", type="primary"):
                    if selected_username == st.session_state.auth_user.username:
                        st.error("You cannot delete yourself!")
                    else:
                        db.delete(selected_user)
                        db.commit()
                        st.success(f"Deleted {selected_username}.")
                        st.rerun()

    # --- TAB 2: ADD USER ---
    with tab2:
        with st.form("add_user"):
            new_user = st.text_input("Username")
            new_name = st.text_input("Full Name")
            new_pass = st.text_input("Password", type="password")
            is_admin = st.checkbox("Grant Admin Privileges")
            if st.form_submit_button("Create User"):
                if not new_user or not new_pass:
                    st.error("Username and Password required.")
                else:
                    existing = db.query(User).filter(User.username == new_user).first()
                    if existing:
                        st.error("User already exists.")
                    else:
                        AuthService.create_user(db, new_user, new_pass, name=new_name, is_admin=is_admin)
                        st.success(f"User {new_user} created!")
                        st.rerun()