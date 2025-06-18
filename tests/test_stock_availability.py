"""
Unit tests for the StockAvailabilityClient module.

Tests stock availability functionality including initialization, successful updates,
and various error scenarios using mocked HTTP requests.
"""

import pytest
from unittest.mock import Mock, patch
from pydantic import ValidationError
from therange.auth import AuthClient
from therange.config import Config
from therange.stock_availability import StockAvailabilityClient, StockItem


class TestStockItem:
    """Test StockItem Pydantic model validation."""
    
    def test_valid_stock_item(self):
        """Test creating a valid StockItem."""
        item = StockItem(code="PROD123", qty=10)
        assert item.code == "PROD123"
        assert item.qty == 10
    
    def test_stock_item_zero_quantity(self):
        """Test StockItem with zero quantity (should be valid)."""
        item = StockItem(code="PROD123", qty=0)
        assert item.code == "PROD123"
        assert item.qty == 0
    
    def test_stock_item_negative_quantity(self):
        """Test StockItem with negative quantity (should fail)."""
        with pytest.raises(ValidationError) as exc_info:
            StockItem(code="PROD123", qty=-1)
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_stock_item_missing_code(self):
        """Test StockItem with missing code field."""
        with pytest.raises(ValidationError) as exc_info:
            StockItem(qty=10)
        assert "Field required" in str(exc_info.value)
    
    def test_stock_item_missing_qty(self):
        """Test StockItem with missing qty field."""
        with pytest.raises(ValidationError) as exc_info:
            StockItem(code="PROD123")
        assert "Field required" in str(exc_info.value)
    
    def test_stock_item_invalid_qty_type(self):
        """Test StockItem with invalid qty type."""
        with pytest.raises(ValidationError) as exc_info:
            StockItem(code="PROD123", qty="not_a_number")
        assert "Input should be a valid integer" in str(exc_info.value)


class TestStockAvailabilityClientInitialization:
    """Test StockAvailabilityClient initialization."""
    
    def test_init_with_auth_client(self):
        """Test initialization with auth client."""
        config = Config.production()
        auth = AuthClient("test_user", "test_pass", config)
        client = StockAvailabilityClient(auth)
        
        assert client.auth is auth


class TestStockAvailabilityClientUpdateStock:
    """Test StockAvailabilityClient update_stock functionality."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        config = Config.production()
        self.auth = AuthClient("test_user", "test_pass", config)
        self.auth.session = Mock()
        self.auth.supplier_id = "12345"
        self.auth.mode = "test_mode"
        self.auth.base_url = "https://test.example.com/rest/"
        self.client = StockAvailabilityClient(self.auth)
    
    def test_update_stock_success(self):
        """Test successful stock update."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        mock_response.text = "OK"
        self.auth.session.post.return_value = mock_response
        
        # Test data
        stock_data = [
            {"code": "PROD123", "qty": 10},
            {"code": "PROD456", "qty": 0},
            {"code": "PROD789", "qty": 25}
        ]
        
        # Call update_stock
        result = self.client.update_stock(stock_data)
        
        # Verify the API call was made correctly
        expected_url = "https://test.example.com/rest/stock_availability.api?supplier_id=12345"
        expected_payload = stock_data  # Should be same as input after validation
        
        self.auth.session.post.assert_called_once_with(expected_url, json=expected_payload)
        assert result == {"status": "success"}
    
    def test_update_stock_no_session(self):
        """Test update_stock when session is None."""
        self.auth.session = None
        
        stock_data = [{"code": "PROD123", "qty": 10}]
        
        with pytest.raises(ValueError) as exc_info:
            self.client.update_stock(stock_data)
        
        assert "Must be authenticated before making this call" in str(exc_info.value)
    
    def test_update_stock_no_supplier_id(self):
        """Test update_stock when supplier_id is None."""
        self.auth.supplier_id = None
        
        stock_data = [{"code": "PROD123", "qty": 10}]
        
        with pytest.raises(ValueError) as exc_info:
            self.client.update_stock(stock_data)
        
        assert "Must be authenticated before making this call" in str(exc_info.value)
    
    def test_update_stock_not_a_list(self):
        """Test update_stock with non-list input."""
        with pytest.raises(ValueError) as exc_info:
            self.client.update_stock("not_a_list")
        
        assert "stock_data must be a list" in str(exc_info.value)
    
    def test_update_stock_empty_list(self):
        """Test update_stock with empty list."""
        with pytest.raises(ValueError) as exc_info:
            self.client.update_stock([])
        
        assert "stock_data must be a non-empty list" in str(exc_info.value)
    
    def test_update_stock_invalid_item_missing_code(self):
        """Test update_stock with item missing code field."""
        stock_data = [{"qty": 10}]  # Missing 'code'
        
        with pytest.raises(ValueError) as exc_info:
            self.client.update_stock(stock_data)
        
        assert "Invalid stock data:" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)
    
    def test_update_stock_invalid_item_missing_qty(self):
        """Test update_stock with item missing qty field."""
        stock_data = [{"code": "PROD123"}]  # Missing 'qty'
        
        with pytest.raises(ValueError) as exc_info:
            self.client.update_stock(stock_data)
        
        assert "Invalid stock data:" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)
    
    def test_update_stock_invalid_item_negative_qty(self):
        """Test update_stock with negative quantity."""
        stock_data = [{"code": "PROD123", "qty": -5}]
        
        with pytest.raises(ValueError) as exc_info:
            self.client.update_stock(stock_data)
        
        assert "Invalid stock data:" in str(exc_info.value)
        assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    def test_update_stock_invalid_item_wrong_qty_type(self):
        """Test update_stock with invalid qty type."""
        stock_data = [{"code": "PROD123", "qty": "not_a_number"}]
        
        with pytest.raises(ValueError) as exc_info:
            self.client.update_stock(stock_data)
        
        assert "Invalid stock data:" in str(exc_info.value)
        assert "Input should be a valid integer" in str(exc_info.value)
    
    def test_update_stock_mixed_valid_invalid(self):
        """Test update_stock with mix of valid and invalid items."""
        stock_data = [
            {"code": "PROD123", "qty": 10},  # Valid
            {"code": "PROD456", "qty": -1}   # Invalid (negative qty)
        ]
        
        with pytest.raises(ValueError) as exc_info:
            self.client.update_stock(stock_data)
        
        assert "Invalid stock data:" in str(exc_info.value)
    
    def test_update_stock_http_401_error(self):
        """Test update_stock with 401 HTTP error."""
        # Setup mock response with 401 error
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        self.auth.session.post.return_value = mock_response
        
        stock_data = [{"code": "PROD123", "qty": 10}]
        
        with pytest.raises(PermissionError) as exc_info:
            self.client.update_stock(stock_data)
        
        assert "Not authenticated." in str(exc_info.value)
    
    def test_update_stock_http_400_error(self):
        """Test update_stock with 400 HTTP error."""
        # Setup mock response with 400 error
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request - invalid data"
        self.auth.session.post.return_value = mock_response
        
        stock_data = [{"code": "PROD123", "qty": 10}]
        
        with pytest.raises(ValueError) as exc_info:
            self.client.update_stock(stock_data)
        
        assert "Bad request: Bad request - invalid data" in str(exc_info.value)
    
    def test_update_stock_http_500_error(self):
        """Test update_stock with 500 HTTP error."""
        # Setup mock response with 500 error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("Server error")
        self.auth.session.post.return_value = mock_response
        
        stock_data = [{"code": "PROD123", "qty": 10}]
        
        with pytest.raises(Exception) as exc_info:
            self.client.update_stock(stock_data)
        
        assert "Server error" in str(exc_info.value)
    
    def test_update_stock_include_mode_false(self):
        """Test that update_stock calls _post with include_mode=False."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        mock_response.text = "OK"
        self.auth.session.post.return_value = mock_response
        
        stock_data = [{"code": "PROD123", "qty": 10}]
        
        # Call update_stock
        self.client.update_stock(stock_data)
        
        # Verify that mode was NOT added to payload (include_mode=False)
        call_args = self.auth.session.post.call_args
        payload = call_args.kwargs['json']
        
        # Mode should not be in payload since include_mode=False
        assert 'mode' not in payload
        
        # But supplier_id should be in URL params
        expected_url = "https://test.example.com/rest/stock_availability.api?supplier_id=12345"
        assert call_args.args[0] == expected_url
    
    def test_update_stock_no_supplier_id_in_url_when_none(self):
        """Test that supplier_id is not added to URL when auth.supplier_id is None."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        mock_response.text = "OK"
        
        # Create new auth with supplier_id None but valid session
        config = Config.production()
        auth_no_supplier = AuthClient("test_user", "test_pass", config)
        auth_no_supplier.session = Mock()
        auth_no_supplier.session.post.return_value = mock_response
        auth_no_supplier.supplier_id = None  # This should cause validation error
        auth_no_supplier.base_url = "https://test.example.com/rest/"
        
        client = StockAvailabilityClient(auth_no_supplier)
        stock_data = [{"code": "PROD123", "qty": 10}]
        
        # Should fail due to validation, not because of URL construction
        with pytest.raises(ValueError) as exc_info:
            client.update_stock(stock_data)
        
        assert "Must be authenticated before making this call" in str(exc_info.value)


class TestStockAvailabilityClientEdgeCases:
    """Test StockAvailabilityClient edge cases and integration scenarios."""
    
    def test_update_stock_large_dataset(self):
        """Test update_stock with large dataset."""
        config = Config.production()
        auth = AuthClient("test_user", "test_pass", config)
        auth.session = Mock()
        auth.supplier_id = "12345"
        auth.base_url = "https://test.example.com/rest/"
        client = StockAvailabilityClient(auth)
        
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "updated": 1000}
        mock_response.raise_for_status.return_value = None
        mock_response.text = "OK"
        auth.session.post.return_value = mock_response
        
        # Create large dataset
        stock_data = [{"code": f"PROD{i:06d}", "qty": i % 100} for i in range(1000)]
        
        # Should handle large dataset without issues
        result = client.update_stock(stock_data)
        
        assert result == {"status": "success", "updated": 1000}
        auth.session.post.assert_called_once()
    
    def test_update_stock_special_characters_in_code(self):
        """Test update_stock with special characters in product codes."""
        config = Config.production()
        auth = AuthClient("test_user", "test_pass", config)
        auth.session = Mock()
        auth.supplier_id = "12345"
        auth.base_url = "https://test.example.com/rest/"
        client = StockAvailabilityClient(auth)
        
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        mock_response.text = "OK"
        auth.session.post.return_value = mock_response
        
        # Test with special characters
        stock_data = [
            {"code": "PROD-123_ABC", "qty": 10},
            {"code": "PROD.456@TEST", "qty": 5},
            {"code": "PROD#789$SPECIAL", "qty": 15}
        ]
        
        # Should handle special characters in codes
        result = client.update_stock(stock_data)
        
        assert result == {"status": "success"}
        
        # Verify payload contains the special characters as-is
        call_args = auth.session.post.call_args
        payload = call_args.kwargs['json']
        assert payload == stock_data