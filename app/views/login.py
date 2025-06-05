import streamlit as st
from app import pages

st.title(pages.login_page.title)

# Initialize session state for login
if 'user' not in st.session_state:
    st.session_state.user = None  # No user logged in

# Function to open login dialog
@st.dialog('Login')
def login():
    st.write('Enter your credentials to log in:')
    username = st.text_input('Username', key='username')
    password = st.text_input('Password', type='password', key='password')

    if st.button('Submit'):
        if username == 'admin' and password == 'password':  # Replace with real authentication
            st.session_state.user = username
            st.success('Login successful!')
            st.rerun()
        else:
            st.error('Invalid username or password. Try again.')

# Display login page content
st.write('Please log in to continue.')

if st.button('Login'):
    login()

logout = False
# Redirect users after login
if st.session_state.user is not None:
    if not logout:
        st.success('✅ Login successful! Redirecting...')
        logout = True
        st.switch_page(pages.dashboard_page)  # Change to the main page of your app
    else:
        st.session_state.user = None
        st.success('✅ Logout successful!')

