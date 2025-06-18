"""
Unit tests for the OrderAck module.

Tests order acknowledgment functionality including request validation and client behavior.
"""

import pytest
from unittest.mock import Mock, patch
from pydantic import ValidationError
from therange.order_ack import OrderAckRequest, OrderAckClient
from therange.auth import AuthClient


class TestOrderAckRequest:
    """Test OrderAckRequest Pydantic model validation."""
    
    def test_valid_order_arr(self):
        """Test validation with valid order array."""
        request = OrderAckRequest(order_arr=["ORDER123", "ORDER456"])
        assert request.order_arr == ["ORDER123", "ORDER456"]
    
    def test_single_order(self):
        """Test validation with single order."""
        request = OrderAckRequest(order_arr=["ORDER123"])
        assert request.order_arr == ["ORDER123"]
    
    def test_empty_list_raises_error(self):
        """Test that empty list raises validation error."""
        with pytest.raises(ValueError, match="order_arr must be a non-empty list"):
            OrderAckRequest(order_arr=[])
    
    def test_non_list_raises_error(self):
        """Test that non-list input raises validation error."""
        with pytest.raises(ValidationError, match="Input should be a valid list"):
            OrderAckRequest(order_arr="ORDER123")
    
    def test_non_string_order_id_raises_error(self):
        """Test that non-string order IDs raise validation error."""
        with pytest.raises(ValidationError, match="Input should be a valid string"):
            OrderAckRequest(order_arr=[123, "ORDER456"])
    
    def test_empty_string_order_id_raises_error(self):
        """Test that empty string order IDs raise validation error."""
        with pytest.raises(ValueError, match="Order IDs cannot be empty strings"):
            OrderAckRequest(order_arr=["ORDER123", ""])
    
    def test_whitespace_only_order_id_raises_error(self):
        """Test that whitespace-only order IDs raise validation error."""
        with pytest.raises(ValueError, match="Order IDs cannot be empty strings"):
            OrderAckRequest(order_arr=["ORDER123", "   "])


class TestOrderAckClient:
    """Test OrderAckClient functionality."""
    
    def setup_method(self):
        """Setup method called before each test."""
        self.mock_auth = Mock(spec=AuthClient)
        self.mock_auth.session = Mock()
        self.mock_auth.supplier_id = "12345"
        self.mock_auth.mode = "test"
        self.client = OrderAckClient(self.mock_auth)
    
    def test_initialization(self):
        """Test that OrderAckClient initializes correctly."""
        assert self.client.auth == self.mock_auth
    
    @patch('therange.order_ack.OrderAckClient._post')
    def test_acknowledge_orders_success(self, mock_post):
        """Test successful order acknowledgment."""
        mock_post.return_value = {"order_arr": ["ORDER123", "ORDER456"]}
        
        result = self.client.acknowledge_orders(["ORDER123", "ORDER456"])
        
        mock_post.assert_called_once_with("order_ack.api", {"order_arr": ["ORDER123", "ORDER456"]})
        assert result == {"order_arr": ["ORDER123", "ORDER456"]}
    
    @patch('therange.order_ack.OrderAckClient._post')
    def test_acknowledge_single_order(self, mock_post):
        """Test acknowledging a single order."""
        mock_post.return_value = {"order_arr": ["ORDER123"]}
        
        result = self.client.acknowledge_orders(["ORDER123"])
        
        mock_post.assert_called_once_with("order_ack.api", {"order_arr": ["ORDER123"]})
        assert result == {"order_arr": ["ORDER123"]}
    
    def test_acknowledge_orders_no_session_raises_error(self):
        """Test that missing session raises ValueError."""
        self.mock_auth.session = None
        
        with pytest.raises(ValueError, match="Must be authenticated before making this call"):
            self.client.acknowledge_orders(["ORDER123"])
    
    def test_acknowledge_orders_no_supplier_id_raises_error(self):
        """Test that missing supplier_id raises ValueError."""
        self.mock_auth.supplier_id = None
        
        with pytest.raises(ValueError, match="Must be authenticated before making this call"):
            self.client.acknowledge_orders(["ORDER123"])
    
    def test_acknowledge_orders_empty_supplier_id_raises_error(self):
        """Test that empty supplier_id raises ValueError."""
        self.mock_auth.supplier_id = ""
        
        with pytest.raises(ValueError, match="Must be authenticated before making this call"):
            self.client.acknowledge_orders(["ORDER123"])
    
    def test_acknowledge_orders_invalid_input_raises_error(self):
        """Test that invalid order numbers raise ValueError."""
        with pytest.raises(ValueError, match="Invalid order_numbers"):
            self.client.acknowledge_orders([])
    
    def test_acknowledge_orders_non_string_input_raises_error(self):
        """Test that non-string order numbers raise ValueError."""
        with pytest.raises(ValueError, match="Invalid order_numbers"):
            self.client.acknowledge_orders([123, "ORDER456"])
    
    @patch('therange.order_ack.OrderAckClient._post')
    def test_acknowledge_orders_401_raises_permission_error(self, mock_post):
        """Test that 401 response raises PermissionError."""
        mock_post.side_effect = PermissionError("Not authenticated.")
        
        with pytest.raises(PermissionError, match="Not authenticated."):
            self.client.acknowledge_orders(["ORDER123"])
    
    @patch('therange.order_ack.OrderAckClient._post')
    def test_acknowledge_orders_400_raises_value_error(self, mock_post):
        """Test that 400 response raises ValueError."""
        mock_post.side_effect = ValueError("Bad request: Invalid order format")
        
        with pytest.raises(ValueError, match="Bad request: Invalid order format"):
            self.client.acknowledge_orders(["ORDER123"])


class TestOrderAckClientIntegration:
    """Test OrderAckClient integration scenarios."""
    
    def setup_method(self):
        """Setup method called before each test."""
        self.mock_auth = Mock(spec=AuthClient)
        self.mock_auth.session = Mock()
        self.mock_auth.supplier_id = "12345"
        self.mock_auth.mode = "test"
        self.mock_auth.base_url = "https://uatsupplier.rstore.com/rest/"
        self.client = OrderAckClient(self.mock_auth)
    
    def test_full_api_call_flow(self):
        """Test the complete API call flow including URL construction and payload."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"order_arr": ["ORDER123", "ORDER456"]}
        mock_response.raise_for_status.return_value = None
        self.mock_auth.session.post.return_value = mock_response
        
        # Make the call
        result = self.client.acknowledge_orders(["ORDER123", "ORDER456"])
        
        # Verify the call was made correctly
        expected_url = "https://uatsupplier.rstore.com/rest/order_ack.api?supplier_id=12345"
        expected_payload = {"order_arr": ["ORDER123", "ORDER456"], "mode": "test"}
        
        self.mock_auth.session.post.assert_called_once_with(expected_url, json=expected_payload)
        assert result == {"order_arr": ["ORDER123", "ORDER456"]}
    
    def test_api_call_without_mode(self):
        """Test API call when auth.mode is None."""
        self.mock_auth.mode = None
        
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"order_arr": ["ORDER123"]}
        mock_response.raise_for_status.return_value = None
        self.mock_auth.session.post.return_value = mock_response
        
        # Make the call
        result = self.client.acknowledge_orders(["ORDER123"])
        
        # Verify mode is not included in payload when it's None
        expected_url = "https://uatsupplier.rstore.com/rest/order_ack.api?supplier_id=12345"
        expected_payload = {"order_arr": ["ORDER123"]}
        
        self.mock_auth.session.post.assert_called_once_with(expected_url, json=expected_payload)
        assert result == {"order_arr": ["ORDER123"]}