# your_project/utils/session_utils.py

import streamlit as st
import os
import secrets
from dotenv import load_dotenv
from auths.permissions import Permissions
from typing import Optional

load_dotenv() # Load environment variables

class SessionManager:
    def __init__(self):
        """Initializes default session state variables if they don't exist."""
        if 'logged_in' not in st.session_state:
            st.session_state['logged_in'] = False
        if 'user_email' not in st.session_state:
            st.session_state['user_email'] = None
        if 'user_role' not in st.session_state:
            st.session_state['user_role'] = 'guest'

        # Secure cookies for Streamlit session
        if "SESSION_SECRET_KEY" in os.environ:
            os.environ["STREAMLIT_SERVER_COOKIE_SECRET"] = os.getenv("SESSION_SECRET_KEY")
        elif not st.session_state.get('_secret_key_generated'):
            st.session_state['_secret_key_generated'] = secrets.token_hex(32)
            os.environ["STREAMLIT_SERVER_COOKIE_SECRET"] = st.session_state['_secret_key_generated']

    def login_user(self, email: str, role: str = 'free'):
        """Sets session variables upon successful login."""
        st.session_state['logged_in'] = True
        st.session_state['user_email'] = email
        st.session_state['user_role'] = role

    def logout_user(self):
        """Clears session variables upon logout."""
        st.session_state['logged_in'] = False
        st.session_state['user_email'] = None
        st.session_state['user_role'] = 'guest'

    def is_logged_in(self) -> bool:
        """Checks if the user is currently logged in."""
        return st.session_state.get('logged_in', False)

    def get_current_user_email(self) -> Optional[str]:
        """Returns the logged-in user's email, or None if not logged in."""
        return st.session_state.get('user_email')

    def get_current_user_role(self) -> str:
        """Returns the logged-in user's role (defaults to guest)."""
        return st.session_state.get('user_role', 'guest')

    def has_permission(self, feature_name: str) -> bool:
        # Boom! Everything is now unlocked for everyone.
        return True