"""
Unit tests for the BaseClient module.

Tests base client functionality including initialization and _post method
with various scenarios using mocked HTTP requests.
"""

import pytest
from unittest.mock import Mock, patch
from therange.base_client import BaseClient


class TestBaseClientInitialization:
    """Test BaseClient initialization."""
    
    def test_init_with_auth_client(self):
        """Test initialization with auth client."""
        mock_auth = Mock()
        mock_auth.supplier_id = "12345"
        mock_auth.mode = "test_mode"
        mock_auth.base_url = "https://test.api.com/"
        mock_auth.session = Mock()
        
        client = BaseClient(mock_auth)
        
        assert client.auth == mock_auth
        assert client.auth.supplier_id == "12345"
        assert client.auth.mode == "test_mode"
        assert client.auth.base_url == "https://test.api.com/"


class TestBaseClientPost:
    """Test BaseClient _post method functionality."""
    
    def test_post_success_with_defaults(self):
        """Test successful _post call with default parameters."""
        # Setup mock auth client
        mock_auth = Mock()
        mock_auth.supplier_id = "12345"
        mock_auth.mode = "test_mode"
        mock_auth.base_url = "https://api.test.com/"
        
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": "test"}
        mock_response.raise_for_status.return_value = None
        
        # Setup mock session
        mock_auth.session.post.return_value = mock_response
        
        # Test _post method
        client = BaseClient(mock_auth)
        payload = {"test_key": "test_value"}
        result = client._post("test/endpoint", payload)
        
        # Verify URL construction
        expected_url = "https://api.test.com/test/endpoint?supplier_id=12345"
        mock_auth.session.post.assert_called_once_with(expected_url, json={"test_key": "test_value", "mode": "test_mode"})
        
        # Verify return value
        assert result == {"status": "success", "data": "test"}
        mock_response.raise_for_status.assert_called_once()
    
    def test_post_success_without_supplier_id(self):
        """Test successful _post call with include_supplier_id=False."""
        # Setup mock auth client
        mock_auth = Mock()
        mock_auth.supplier_id = "12345"
        mock_auth.mode = "test_mode"
        mock_auth.base_url = "https://api.test.com/"
        
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        
        # Setup mock session
        mock_auth.session.post.return_value = mock_response
        
        # Test _post method
        client = BaseClient(mock_auth)
        payload = {"test_key": "test_value"}
        result = client._post("test/endpoint", payload, include_supplier_id=False)
        
        # Verify URL construction without supplier_id
        expected_url = "https://api.test.com/test/endpoint"
        mock_auth.session.post.assert_called_once_with(expected_url, json={"test_key": "test_value", "mode": "test_mode"})
        
        assert result == {"status": "success"}
    
    def test_post_success_without_mode(self):
        """Test successful _post call with include_mode=False."""
        # Setup mock auth client
        mock_auth = Mock()
        mock_auth.supplier_id = "12345"
        mock_auth.mode = "test_mode"
        mock_auth.base_url = "https://api.test.com/"
        
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        
        # Setup mock session
        mock_auth.session.post.return_value = mock_response
        
        # Test _post method
        client = BaseClient(mock_auth)
        payload = {"test_key": "test_value"}
        result = client._post("test/endpoint", payload, include_mode=False)
        
        # Verify URL construction and payload without mode
        expected_url = "https://api.test.com/test/endpoint?supplier_id=12345"
        mock_auth.session.post.assert_called_once_with(expected_url, json={"test_key": "test_value"})
        
        assert result == {"status": "success"}
    
    def test_post_success_without_supplier_id_and_mode(self):
        """Test successful _post call with both include_supplier_id=False and include_mode=False."""
        # Setup mock auth client
        mock_auth = Mock()
        mock_auth.supplier_id = "12345"
        mock_auth.mode = "test_mode"
        mock_auth.base_url = "https://api.test.com/"
        
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        
        # Setup mock session
        mock_auth.session.post.return_value = mock_response
        
        # Test _post method
        client = BaseClient(mock_auth)
        payload = {"test_key": "test_value"}
        result = client._post("test/endpoint", payload, include_supplier_id=False, include_mode=False)
        
        # Verify URL construction and payload without parameters
        expected_url = "https://api.test.com/test/endpoint"
        mock_auth.session.post.assert_called_once_with(expected_url, json={"test_key": "test_value"})
        
        assert result == {"status": "success"}
    
    def test_post_with_empty_supplier_id(self):
        """Test _post call when supplier_id is None or empty."""
        # Setup mock auth client with None supplier_id
        mock_auth = Mock()
        mock_auth.supplier_id = None
        mock_auth.mode = "test_mode"
        mock_auth.base_url = "https://api.test.com/"
        
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        
        # Setup mock session
        mock_auth.session.post.return_value = mock_response
        
        # Test _post method
        client = BaseClient(mock_auth)
        payload = {"test_key": "test_value"}
        result = client._post("test/endpoint", payload)
        
        # Verify URL construction without supplier_id when it's None
        expected_url = "https://api.test.com/test/endpoint"
        mock_auth.session.post.assert_called_once_with(expected_url, json={"test_key": "test_value", "mode": "test_mode"})
        
        assert result == {"status": "success"}
    
    def test_post_with_empty_mode(self):
        """Test _post call when mode is None or empty."""
        # Setup mock auth client with None mode
        mock_auth = Mock()
        mock_auth.supplier_id = "12345"
        mock_auth.mode = None
        mock_auth.base_url = "https://api.test.com/"
        
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        
        # Setup mock session
        mock_auth.session.post.return_value = mock_response
        
        # Test _post method
        client = BaseClient(mock_auth)
        payload = {"test_key": "test_value"}
        result = client._post("test/endpoint", payload)
        
        # Verify URL construction and payload without mode when it's None
        expected_url = "https://api.test.com/test/endpoint?supplier_id=12345"
        mock_auth.session.post.assert_called_once_with(expected_url, json={"test_key": "test_value"})
        
        assert result == {"status": "success"}


class TestBaseClientPostErrors:
    """Test BaseClient _post method error scenarios."""
    
    def test_post_401_unauthorized(self):
        """Test _post with 401 unauthorized error."""
        # Setup mock auth client
        mock_auth = Mock()
        mock_auth.supplier_id = "12345"
        mock_auth.mode = "test_mode"
        mock_auth.base_url = "https://api.test.com/"
        
        # Setup mock response with 401 status
        mock_response = Mock()
        mock_response.status_code = 401
        
        # Setup mock session
        mock_auth.session.post.return_value = mock_response
        
        # Test _post method
        client = BaseClient(mock_auth)
        payload = {"test_key": "test_value"}
        
        with pytest.raises(PermissionError, match="Not authenticated."):
            client._post("test/endpoint", payload)
    
    def test_post_400_bad_request(self):
        """Test _post with 400 bad request error."""
        # Setup mock auth client
        mock_auth = Mock()
        mock_auth.supplier_id = "12345"
        mock_auth.mode = "test_mode"
        mock_auth.base_url = "https://api.test.com/"
        
        # Setup mock response with 400 status
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid request format"
        
        # Setup mock session
        mock_auth.session.post.return_value = mock_response
        
        # Test _post method
        client = BaseClient(mock_auth)
        payload = {"test_key": "test_value"}
        
        with pytest.raises(ValueError, match="Bad request: Invalid request format"):
            client._post("test/endpoint", payload)
    
    def test_post_other_http_error(self):
        """Test _post with other HTTP errors (e.g., 500)."""
        # Setup mock auth client
        mock_auth = Mock()
        mock_auth.supplier_id = "12345"
        mock_auth.mode = "test_mode"
        mock_auth.base_url = "https://api.test.com/"
        
        # Setup mock response with 500 status
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("Internal Server Error")
        
        # Setup mock session
        mock_auth.session.post.return_value = mock_response
        
        # Test _post method
        client = BaseClient(mock_auth)
        payload = {"test_key": "test_value"}
        
        with pytest.raises(Exception, match="Internal Server Error"):
            client._post("test/endpoint", payload)


class TestBaseClientEdgeCases:
    """Test BaseClient edge cases and integration scenarios."""
    
    def test_post_with_complex_payload(self):
        """Test _post with complex nested payload."""
        # Setup mock auth client
        mock_auth = Mock()
        mock_auth.supplier_id = "12345"
        mock_auth.mode = "test_mode"
        mock_auth.base_url = "https://api.test.com/"
        
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "id": 123}
        mock_response.raise_for_status.return_value = None
        
        # Setup mock session
        mock_auth.session.post.return_value = mock_response
        
        # Test _post method with complex payload
        client = BaseClient(mock_auth)
        payload = {
            "nested": {
                "data": ["item1", "item2"],
                "meta": {"count": 2}
            },
            "simple": "value"
        }
        result = client._post("complex/endpoint", payload)
        
        # Verify the payload was modified correctly with mode
        expected_payload = {
            "nested": {
                "data": ["item1", "item2"],
                "meta": {"count": 2}
            },
            "simple": "value",
            "mode": "test_mode"
        }
        
        expected_url = "https://api.test.com/complex/endpoint?supplier_id=12345"
        mock_auth.session.post.assert_called_once_with(expected_url, json=expected_payload)
        
        assert result == {"status": "success", "id": 123}
    
    def test_post_preserves_original_payload(self):
        """Test that _post method preserves the original payload object."""
        # Setup mock auth client
        mock_auth = Mock()
        mock_auth.supplier_id = "12345"
        mock_auth.mode = "test_mode"
        mock_auth.base_url = "https://api.test.com/"
        
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        
        # Setup mock session
        mock_auth.session.post.return_value = mock_response
        
        # Test _post method
        client = BaseClient(mock_auth)
        original_payload = {"test_key": "test_value"}
        original_payload_copy = original_payload.copy()
        
        client._post("test/endpoint", original_payload)
        
        # Verify original payload was modified by adding mode
        assert original_payload == {"test_key": "test_value", "mode": "test_mode"}
        assert original_payload != original_payload_copy
    
    def test_post_endpoint_url_construction(self):
        """Test various endpoint URL constructions."""
        # Setup mock auth client
        mock_auth = Mock()
        mock_auth.supplier_id = "12345"
        mock_auth.mode = "test_mode"
        mock_auth.base_url = "https://api.test.com/"
        
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        
        # Setup mock session
        mock_auth.session.post.return_value = mock_response
        
        client = BaseClient(mock_auth)
        payload = {"test": "data"}
        
        # Test various endpoint formats
        test_cases = [
            ("endpoint", "https://api.test.com/endpoint?supplier_id=12345"),
            ("path/to/endpoint", "https://api.test.com/path/to/endpoint?supplier_id=12345"),
            ("endpoint.api", "https://api.test.com/endpoint.api?supplier_id=12345"),
            ("", "https://api.test.com/?supplier_id=12345"),
        ]
        
        for endpoint, expected_url in test_cases:
            mock_auth.session.post.reset_mock()
            client._post(endpoint, payload.copy())
            mock_auth.session.post.assert_called_once_with(expected_url, json={"test": "data", "mode": "test_mode"})