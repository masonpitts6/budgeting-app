import streamlit as st
import os
import sys

# Get the absolute path of the project root dynamically
# This allows all Streamlit pages to reference all files and directories in project root.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Append the project root to sys.path if it's not already included
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Ensure session state is initialized
if "user" not in st.session_state:
    st.session_state.user = None

import pages
import config

st.set_page_config(layout="wide")

# --- NAVIGATION SETUP ---
current_page = st.navigation(
    pages=[
        pages.dashboard_page,
        pages.projections_page,
        pages.income_page,
        pages.budget_page,
        pages.subscriptions_page,
        pages.planned_purchases,
        pages.about_page,
        pages.settings_page,
        pages.login_page
    ]
)

# --- RUN NAVIGATION ---

st.session_state.user = 'admin'
# Check if user is NOT logged in and NOT already on login page
if st.session_state.user is None and current_page.title != config.PAGE_NAMES['login']:
    if "redirecting" not in st.session_state or not st.session_state.redirecting:
        st.session_state.redirecting = True  # Prevents infinite loop
        st.switch_page(pages.login_page)  # Correct way to switch pages
else:
    st.session_state.redirecting = False  # Reset after login

# Logout functionality
with st.sidebar:
    if st.button('⬅️ Logout'):
        st.session_state.user = None
        st.switch_page(pages.login_page)

current_page.run()
