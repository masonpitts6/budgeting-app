import streamlit as st

def login_redirect():
    # Force login check
    if "user" not in st.session_state or st.session_state.user is None:
        st.warning("🚨 You must log in to access this page.")
        st.switch_page("budgeting-app/app/views/login.py")  # Redirect to login page
