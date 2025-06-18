"""
Unit tests for the AuthClient module.

Tests authentication functionality including initialization, successful auth,
and various error scenarios using mocked HTTP requests.
"""

import pytest
import requests
from unittest.mock import Mock, patch
from therange.auth import AuthClient


class TestAuthClientInitialization:
    """Test AuthClient initialization."""
    
    def test_init_default_production(self):
        """Test initialization with default production settings."""
        auth = AuthClient("test_user", "test_pass")
        
        assert auth.username == "test_user"
        assert auth.password == "test_pass"
        assert auth.test is False
        assert auth.base_url == "https://supplier.rstore.com/rest/"
        assert isinstance(auth.session, requests.Session)
        assert auth.mode is None
        assert auth.supplier_id is None
        assert auth.ksi is None
    
    def test_init_test_mode(self):
        """Test initialization with test mode enabled."""
        auth = AuthClient("test_user", "test_pass", test=True)
        
        assert auth.username == "test_user"
        assert auth.password == "test_pass"
        assert auth.test is True
        assert auth.base_url == "https://uatsupplier.rstore.com/rest/"
        assert isinstance(auth.session, requests.Session)
        assert auth.mode is None
        assert auth.supplier_id is None
        assert auth.ksi is None


class TestAuthClientAuthentication:
    """Test AuthClient authentication functionality."""
    
    @patch('therange.auth.requests.Session')
    def test_authenticate_success(self, mock_session_class):
        """Test successful authentication flow."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Set-Cookie": "ksi=test_ksi_value; Path=/"}
        mock_response.json.return_value = {
            "mode": "test_mode",
            "supplier_id": 12345
        }
        mock_response.raise_for_status.return_value = None
        
        # Setup mock session
        mock_session = Mock()
        mock_session.post.return_value = mock_response
        mock_session.cookies.set = Mock()
        mock_session_class.return_value = mock_session
        
        # Test authentication
        auth = AuthClient("test_user", "test_pass", test=True)
        result = auth.authenticate()
        
        # Verify request was made correctly
        expected_url = "https://uatsupplier.rstore.com/rest/authenticate.api"
        expected_payload = {"user": "test_user", "pass": "test_pass"}
        mock_session.post.assert_called_once_with(expected_url, json=expected_payload)
        
        # Verify cookie was set
        mock_session.cookies.set.assert_called_once_with("ksi", "test_ksi_value")
        
        # Verify auth state was updated
        assert auth.ksi == "test_ksi_value"
        assert auth.mode == "test_mode"
        assert auth.supplier_id == "12345"
        
        # Verify return value
        assert result == {"mode": "test_mode", "supplier_id": 12345}
    
    @patch('therange.auth.requests.Session')
    def test_authenticate_401_unauthorized(self, mock_session_class):
        """Test authentication with 401 unauthorized error."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 401
        
        # Setup mock session
        mock_session = Mock()
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Test authentication
        auth = AuthClient("bad_user", "bad_pass")
        
        with pytest.raises(PermissionError, match="Unauthorized: Invalid credentials"):
            auth.authenticate()
    
    @patch('therange.auth.requests.Session')
    def test_authenticate_400_bad_request(self, mock_session_class):
        """Test authentication with 400 bad request error."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid request format"
        
        # Setup mock session
        mock_session = Mock()
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Test authentication
        auth = AuthClient("test_user", "test_pass")
        
        with pytest.raises(ValueError, match="Bad request: Invalid request format"):
            auth.authenticate()
    
    @patch('therange.auth.requests.Session')
    def test_authenticate_missing_ksi_cookie(self, mock_session_class):
        """Test authentication when ksi cookie is missing from response."""
        # Setup mock response without ksi cookie
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Set-Cookie": "other_cookie=value; Path=/"}
        mock_response.raise_for_status.return_value = None
        
        # Setup mock session
        mock_session = Mock()
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Test authentication
        auth = AuthClient("test_user", "test_pass")
        
        with pytest.raises(RuntimeError, match="Authentication failed: 'ksi' cookie missing"):
            auth.authenticate()
    
    @patch('therange.auth.requests.Session')
    def test_authenticate_no_set_cookie_header(self, mock_session_class):
        """Test authentication when Set-Cookie header is missing."""
        # Setup mock response without Set-Cookie header
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.raise_for_status.return_value = None
        
        # Setup mock session
        mock_session = Mock()
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Test authentication
        auth = AuthClient("test_user", "test_pass")
        
        with pytest.raises(RuntimeError, match="Authentication failed: 'ksi' cookie missing"):
            auth.authenticate()
    
    @patch('therange.auth.requests.Session')
    def test_authenticate_http_error(self, mock_session_class):
        """Test authentication with other HTTP errors."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
        
        # Setup mock session
        mock_session = Mock()
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # Test authentication
        auth = AuthClient("test_user", "test_pass")
        
        with pytest.raises(requests.exceptions.HTTPError):
            auth.authenticate()
    
    @patch('therange.auth.requests.Session')
    def test_authenticate_with_supplier_id_none(self, mock_session_class):
        """Test authentication when supplier_id is None in response."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Set-Cookie": "ksi=test_ksi_value; Path=/"}
        mock_response.json.return_value = {
            "mode": "test_mode",
            "supplier_id": None
        }
        mock_response.raise_for_status.return_value = None
        
        # Setup mock session
        mock_session = Mock()
        mock_session.post.return_value = mock_response
        mock_session.cookies.set = Mock()
        mock_session_class.return_value = mock_session
        
        # Test authentication
        auth = AuthClient("test_user", "test_pass")
        result = auth.authenticate()
        
        # Verify supplier_id is converted to string "None"
        assert auth.supplier_id == "None"
        assert result == {"mode": "test_mode", "supplier_id": None}
    
    @patch('therange.auth.requests.Session')
    def test_authenticate_with_numeric_supplier_id(self, mock_session_class):
        """Test authentication with numeric supplier_id."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Set-Cookie": "ksi=test_ksi_value; Path=/"}
        mock_response.json.return_value = {
            "mode": "test_mode",
            "supplier_id": 67890
        }
        mock_response.raise_for_status.return_value = None
        
        # Setup mock session
        mock_session = Mock()
        mock_session.post.return_value = mock_response
        mock_session.cookies.set = Mock()
        mock_session_class.return_value = mock_session
        
        # Test authentication
        auth = AuthClient("test_user", "test_pass")
        result = auth.authenticate()
        
        # Verify supplier_id is converted to string
        assert auth.supplier_id == "67890"
        assert result == {"mode": "test_mode", "supplier_id": 67890}
    
    @patch('therange.auth.requests.Session')
    def test_authenticate_missing_mode_in_response(self, mock_session_class):
        """Test authentication when mode is missing from response."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Set-Cookie": "ksi=test_ksi_value; Path=/"}
        mock_response.json.return_value = {
            "supplier_id": 12345
        }
        mock_response.raise_for_status.return_value = None
        
        # Setup mock session
        mock_session = Mock()
        mock_session.post.return_value = mock_response
        mock_session.cookies.set = Mock()
        mock_session_class.return_value = mock_session
        
        # Test authentication
        auth = AuthClient("test_user", "test_pass")
        result = auth.authenticate()
        
        # Verify mode remains None
        assert auth.mode is None
        assert auth.supplier_id == "12345"
        assert result == {"supplier_id": 12345}


class TestAuthClientEdgeCases:
    """Test AuthClient edge cases and integration scenarios."""
    
    @patch('therange.auth.requests.Session')
    def test_authenticate_complex_cookie_string(self, mock_session_class):
        """Test authentication with complex Set-Cookie header containing multiple cookies."""
        # Setup mock response with multiple cookies
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "Set-Cookie": "session=abc123; Path=/; ksi=test_ksi_value; HttpOnly; other=xyz"
        }
        mock_response.json.return_value = {
            "mode": "production",
            "supplier_id": 54321
        }
        mock_response.raise_for_status.return_value = None
        
        # Setup mock session
        mock_session = Mock()
        mock_session.post.return_value = mock_response
        mock_session.cookies.set = Mock()
        mock_session_class.return_value = mock_session
        
        # Test authentication
        auth = AuthClient("test_user", "test_pass")
        result = auth.authenticate()
        
        # Verify ksi cookie was extracted correctly
        assert auth.ksi == "test_ksi_value"
        mock_session.cookies.set.assert_called_once_with("ksi", "test_ksi_value")
    
    @patch('therange.auth.requests.Session')
    def test_authenticate_empty_response_json(self, mock_session_class):
        """Test authentication when response JSON is empty."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Set-Cookie": "ksi=test_ksi_value; Path=/"}
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        
        # Setup mock session
        mock_session = Mock()
        mock_session.post.return_value = mock_response
        mock_session.cookies.set = Mock()
        mock_session_class.return_value = mock_session
        
        # Test authentication
        auth = AuthClient("test_user", "test_pass")
        result = auth.authenticate()
        
        # Verify defaults are handled correctly
        assert auth.ksi == "test_ksi_value"
        assert auth.mode is None
        assert auth.supplier_id == "None"  # str(None)
        assert result == {}
    
    def test_auth_client_state_persistence(self):
        """Test that AuthClient maintains state correctly after initialization."""
        auth = AuthClient("user1", "pass1", test=True)
        
        # Verify initial state
        assert auth.username == "user1"
        assert auth.password == "pass1"
        assert auth.test is True
        
        # State should persist
        assert auth.session is not None
        assert isinstance(auth.session, requests.Session)
        
        # Verify URLs are set correctly
        assert "uatsupplier.rstore.com" in auth.base_url
    
    @patch('therange.auth.requests.Session')
    def test_multiple_authenticate_calls(self, mock_session_class):
        """Test that multiple authenticate calls work correctly."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Set-Cookie": "ksi=new_ksi_value; Path=/"}
        mock_response.json.return_value = {
            "mode": "updated_mode",
            "supplier_id": 99999
        }
        mock_response.raise_for_status.return_value = None
        
        # Setup mock session
        mock_session = Mock()
        mock_session.post.return_value = mock_response
        mock_session.cookies.set = Mock()
        mock_session_class.return_value = mock_session
        
        # Test multiple authentication calls
        auth = AuthClient("test_user", "test_pass")
        
        # First authentication
        result1 = auth.authenticate()
        assert auth.ksi == "new_ksi_value"
        assert auth.mode == "updated_mode"
        assert auth.supplier_id == "99999"
        
        # Second authentication should update state
        result2 = auth.authenticate()
        assert auth.ksi == "new_ksi_value"
        assert auth.mode == "updated_mode"
        assert auth.supplier_id == "99999"
        
        # Should have called post twice
        assert mock_session.post.call_count == 2