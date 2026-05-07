# your_project/tests/test_auth.py

import pytest
from unittest.mock import MagicMock, patch
from auths.auth import AuthManager
from db.user_manager import UserManager
from utils.password_utils import PasswordUtils
from utils.email_utils import EmailUtils
from utils.session_utils import SessionManager

@pytest.fixture
def mock_user_manager():
    manager = MagicMock(spec=UserManager)
    manager.get_user_by_email.return_value = None 
    manager.add_user.return_value = True 
    manager.store_otp.return_value = True 
    manager.verify_otp.return_value = False 
    manager.set_email_verified.return_value = True
    manager.update_password.return_value = True
    manager.log_activity = MagicMock()
    return manager

@pytest.fixture
def mock_password_utils():
    utils = MagicMock(spec=PasswordUtils)
    utils.hash_password.return_value = "hashed_password_mock"
    utils.verify_password.return_value = True 
    return utils

@pytest.fixture
def mock_email_utils():
    utils = MagicMock(spec=EmailUtils)
    utils.generate_otp.return_value = "123456"
    utils.send_verification_email.return_value = True
    return utils

@pytest.fixture
def mock_session_manager():
    manager = MagicMock()
    manager.is_logged_in.return_value = False 
    manager.login_user = MagicMock()
    manager.logout_user = MagicMock()
    return manager

@pytest.fixture
def auth_manager(mock_user_manager, mock_password_utils, mock_email_utils, mock_session_manager):
    with patch('auths.auth.UserManager', return_value=mock_user_manager), \
         patch('auths.auth.PasswordUtils', return_value=mock_password_utils), \
         patch('auths.auth.EmailUtils', return_value=mock_email_utils), \
         patch('auths.auth.SessionManager', return_value=mock_session_manager):
        with patch('streamlit.rerun'):
            yield AuthManager()

def test_signup_success(auth_manager, mock_user_manager, mock_email_utils):
    with patch('streamlit.text_input', side_effect=["test@example.com", "password123", "password123"]), \
         patch('streamlit.form_submit_button', return_value=True), \
         patch('streamlit.success') as mock_st_success, \
         patch('streamlit.error') as mock_st_error, \
         patch('streamlit.session_state', new_callable=dict) as mock_session_state:
        
        auth_manager.signup_ui()

        mock_user_manager.add_user.assert_called_once_with("test@example.com", "hashed_password_mock", role='free')
        mock_user_manager.store_otp.assert_called_once()
        mock_email_utils.send_verification_email.assert_called_once_with("test@example.com", "123456")
        mock_st_success.assert_called_once_with("Account created! Check your email for a verification OTP.")

def test_login_success(auth_manager, mock_user_manager, mock_session_manager):
    test_email = "login@example.com"
    mock_user_manager.get_user_by_email.return_value = {"email": test_email, "password_hash": "hashed_password_mock", "is_verified": True, "role": "free"}
    
    with patch('streamlit.text_input', side_effect=[test_email, "correct_password"]), \
         patch('streamlit.form_submit_button', return_value=True), \
         patch('streamlit.error') as mock_st_error, \
         patch('streamlit.rerun'): 
        
        auth_manager.login_ui()

        mock_user_manager.log_activity.assert_called_once_with(test_email, "login", "Successful login.")
        mock_st_error.assert_not_called()

def test_reset_password_set_new_password_success(auth_manager, mock_user_manager, mock_password_utils):
    test_email = "reset@example.com"
    mock_user_manager.verify_otp.return_value = True 
    mock_user_manager.update_password.return_value = True

    with patch('streamlit.text_input', side_effect=["123456", "newpassword123", "newpassword123"]), \
         patch('streamlit.form_submit_button', return_value=True), \
         patch('streamlit.success') as mock_st_success, \
         patch('streamlit.rerun'), \
         patch('streamlit.session_state', new_callable=dict) as mock_session_state:
        
        mock_session_state['reset_email_sent'] = True 
        mock_session_state['reset_token_email'] = test_email
        
        auth_manager.reset_password_ui()

        mock_user_manager.verify_otp.assert_called_once_with(test_email, "123456")
        mock_user_manager.update_password.assert_called_once_with(test_email, "hashed_password_mock")
        mock_st_success.assert_called_once_with("Your password has been reset successfully. You can now log in.")