import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.write(f"Welcome, **{st.session_state.username}**!")
        
        if st.button("Logout"):
            st.session_state.authentication_status = None
            st.session_state.username = None
            st.session_state.is_admin = False
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
        if st.session_state.get("is_admin"):
            if st.button("👥 User Management", use_container_width=True):
                st.session_state.current_page = "admin"
                st.rerun()
