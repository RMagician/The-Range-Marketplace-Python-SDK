"""
Unit tests for the OrderFeed module.

Tests order feed functionality including request validation,
client methods, and various error scenarios using mocked HTTP requests.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from therange.order_feed import OrderFeedRequest, OrderFeedClient
from therange.auth import AuthClient


class TestOrderFeedRequest:
    """Test OrderFeedRequest Pydantic model validation."""
    
    def test_valid_request_all_parameters(self):
        """Test creating a valid request with all parameters."""
        request = OrderFeedRequest(
            search="W000001",
            type="new",
            **{"from": "2025-06-01 00:00:00", "to": "2025-06-15 23:59:59"}
        )
        
        assert request.search == "W000001"
        assert request.type == "new"
        assert request.from_date == "2025-06-01 00:00:00"
        assert request.to_date == "2025-06-15 23:59:59"
    
    def test_valid_request_defaults(self):
        """Test creating a request with default values."""
        request = OrderFeedRequest()
        
        assert request.search is None
        assert request.type == "all"
        assert request.from_date is None
        assert request.to_date is None
    
    def test_valid_request_partial_parameters(self):
        """Test creating a request with some parameters."""
        request = OrderFeedRequest(
            search="customer_name",
            type="pending"
        )
        
        assert request.search == "customer_name"
        assert request.type == "pending"
        assert request.from_date is None
        assert request.to_date is None
    
    def test_field_aliases(self):
        """Test that field aliases work correctly."""
        request = OrderFeedRequest(**{"from": "2025-06-01 00:00:00", "to": "2025-06-15 23:59:59"})
        
        assert request.from_date == "2025-06-01 00:00:00"
        assert request.to_date == "2025-06-15 23:59:59"
        
        # Test model_dump with aliases
        dumped = request.model_dump(by_alias=True)
        assert "from" in dumped
        assert "to" in dumped
        assert dumped["from"] == "2025-06-01 00:00:00"
        assert dumped["to"] == "2025-06-15 23:59:59"
    
    def test_type_validation_valid_values(self):
        """Test that valid type values are accepted."""
        valid_types = ["all", "new", "pending", "historic"]
        
        for valid_type in valid_types:
            request = OrderFeedRequest(type=valid_type)
            assert request.type == valid_type
    
    def test_type_validation_invalid_value(self):
        """Test that invalid type values raise ValidationError."""
        with pytest.raises(ValueError, match="type must be one of"):
            OrderFeedRequest(type="invalid_type")
    
    def test_date_range_validation_valid_range(self):
        """Test that valid date ranges (≤35 days) are accepted."""
        # Test exactly 35 days
        from_date = "2025-06-01 00:00:00"
        to_date = "2025-07-06 00:00:00"  # 35 days later
        
        request = OrderFeedRequest(**{"from": from_date, "to": to_date})
        assert request.from_date == from_date
        assert request.to_date == to_date
    
    def test_date_range_validation_exceed_35_days(self):
        """Test that date ranges exceeding 35 days raise ValidationError."""
        from_date = "2025-06-01 00:00:00"
        to_date = "2025-07-07 00:00:00"  # 36 days later
        
        with pytest.raises(ValueError, match="Date range cannot exceed 35 days"):
            OrderFeedRequest(**{"from": from_date, "to": to_date})
    
    def test_date_range_validation_no_from_date(self):
        """Test that validation passes when only to_date is provided."""
        request = OrderFeedRequest(**{"to": "2025-06-15 23:59:59"})
        assert request.to_date == "2025-06-15 23:59:59"
        assert request.from_date is None
    
    def test_date_range_validation_no_to_date(self):
        """Test that validation passes when only from_date is provided."""
        request = OrderFeedRequest(**{"from": "2025-06-01 00:00:00"})
        assert request.from_date == "2025-06-01 00:00:00"
        assert request.to_date is None
    
    def test_date_range_validation_invalid_date_format(self):
        """Test that invalid date formats are handled gracefully."""
        # This should not raise an error due to the try-catch in validator
        request = OrderFeedRequest(**{"from": "invalid-date", "to": "also-invalid"})
        assert request.from_date == "invalid-date"
        assert request.to_date == "also-invalid"
    
    def test_model_dump_exclude_none(self):
        """Test that model_dump correctly excludes None values."""
        request = OrderFeedRequest(search="test", type="new")
        dumped = request.model_dump(by_alias=True, exclude_none=True)
        
        assert dumped == {"search": "test", "type": "new"}
        assert "from" not in dumped
        assert "to" not in dumped


class TestOrderFeedClient:
    """Test OrderFeedClient functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_auth = Mock(spec=AuthClient)
        self.mock_auth.session = Mock()
        self.mock_auth.supplier_id = "12345"
        self.mock_auth.base_url = "https://test.api.com/rest/"
        self.mock_auth.mode = "test_mode"
        
        self.client = OrderFeedClient(self.mock_auth)
    
    def test_get_orders_success_all_parameters(self):
        """Test successful get_orders call with all parameters."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "order_arr": [
                {"order_number": "W000001", "status": "new"},
                {"order_number": "W000002", "status": "pending"}
            ]
        }
        mock_response.raise_for_status.return_value = None
        self.mock_auth.session.post.return_value = mock_response
        
        # Call method
        result = self.client.get_orders(
            search="W000001",
            type="new", 
            from_date="2025-06-01 00:00:00",
            to_date="2025-06-15 23:59:59"
        )
        
        # Verify API call
        self.mock_auth.session.post.assert_called_once()
        call_args = self.mock_auth.session.post.call_args
        
        # Check URL
        expected_url = "https://test.api.com/rest/order_feed.api?supplier_id=12345"
        assert call_args[1]['url'] if 'url' in call_args[1] else call_args[0][0] == expected_url
        
        # Check payload
        expected_payload = {
            "search": "W000001",
            "type": "new",
            "from": "2025-06-01 00:00:00",
            "to": "2025-06-15 23:59:59",
            "mode": "test_mode"
        }
        actual_payload = call_args[1]['json'] if 'json' in call_args[1] else call_args[1]['data']
        assert actual_payload == expected_payload
        
        # Verify response
        assert result == {"order_arr": [
            {"order_number": "W000001", "status": "new"},
            {"order_number": "W000002", "status": "pending"}
        ]}
    
    def test_get_orders_success_defaults(self):
        """Test successful get_orders call with default parameters."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"order_arr": []}
        mock_response.raise_for_status.return_value = None
        self.mock_auth.session.post.return_value = mock_response
        
        # Call method with defaults
        result = self.client.get_orders()
        
        # Verify API call
        self.mock_auth.session.post.assert_called_once()
        call_args = self.mock_auth.session.post.call_args
        
        # Check payload - should only include type and mode (exclude_none=True)
        expected_payload = {
            "type": "all",
            "mode": "test_mode"
        }
        actual_payload = call_args[1]['json'] if 'json' in call_args[1] else call_args[1]['data']
        assert actual_payload == expected_payload
        
        assert result == {"order_arr": []}
    
    def test_get_orders_authentication_no_session(self):
        """Test that authentication is validated - no session."""
        self.mock_auth.session = None
        
        with pytest.raises(ValueError, match="Must be authenticated before making this call"):
            self.client.get_orders()
    
    def test_get_orders_authentication_no_supplier_id(self):
        """Test that authentication is validated - no supplier_id."""
        self.mock_auth.supplier_id = None
        
        with pytest.raises(ValueError, match="Must be authenticated before making this call"):
            self.client.get_orders()
    
    def test_get_orders_authentication_empty_supplier_id(self):
        """Test that authentication is validated - empty supplier_id."""
        self.mock_auth.supplier_id = ""
        
        with pytest.raises(ValueError, match="Must be authenticated before making this call"):
            self.client.get_orders()
    
    def test_get_orders_invalid_type_parameter(self):
        """Test that invalid type parameter raises ValueError."""
        with pytest.raises(ValueError, match="Invalid parameters"):
            self.client.get_orders(type="invalid_type")
    
    def test_get_orders_invalid_date_range(self):
        """Test that invalid date range raises ValueError."""
        with pytest.raises(ValueError, match="Invalid parameters"):
            self.client.get_orders(
                from_date="2025-06-01 00:00:00",
                to_date="2025-07-07 00:00:00"  # 36 days later
            )
    
    def test_get_orders_401_unauthorized(self):
        """Test handling of 401 Unauthorized response."""
        mock_response = Mock()
        mock_response.status_code = 401
        self.mock_auth.session.post.return_value = mock_response
        
        with pytest.raises(PermissionError, match="Not authenticated"):
            self.client.get_orders()
    
    def test_get_orders_400_bad_request(self):
        """Test handling of 400 Bad Request response."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid request parameters"
        self.mock_auth.session.post.return_value = mock_response
        
        with pytest.raises(ValueError, match="Bad request: Invalid request parameters"):
            self.client.get_orders()
    
    def test_get_orders_500_server_error(self):
        """Test handling of 500 Server Error response."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("Server Error")
        self.mock_auth.session.post.return_value = mock_response
        
        with pytest.raises(Exception, match="Server Error"):
            self.client.get_orders()
    
    def test_get_orders_exclude_none_values(self):
        """Test that None values are excluded from the payload."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"order_arr": []}
        mock_response.raise_for_status.return_value = None
        self.mock_auth.session.post.return_value = mock_response
        
        # Call with some None values
        self.client.get_orders(
            search="test_search",
            type="new",
            from_date=None,
            to_date=None
        )
        
        # Verify that None values are excluded
        call_args = self.mock_auth.session.post.call_args
        actual_payload = call_args[1]['json'] if 'json' in call_args[1] else call_args[1]['data']
        
        expected_payload = {
            "search": "test_search",
            "type": "new",
            "mode": "test_mode"
        }
        assert actual_payload == expected_payload
        assert "from" not in actual_payload
        assert "to" not in actual_payload


class TestOrderFeedIntegration:
    """Integration tests for OrderFeed components."""
    
    def test_request_model_with_client_integration(self):
        """Test that OrderFeedRequest model integrates properly with OrderFeedClient."""
        # Create a valid request model
        request = OrderFeedRequest(
            search="integration_test",
            type="pending",
            **{"from": "2025-06-01 00:00:00", "to": "2025-06-10 00:00:00"}
        )
        
        # Verify the model can be dumped properly for API use
        payload = request.model_dump(by_alias=True, exclude_none=True)
        
        expected_payload = {
            "search": "integration_test",
            "type": "pending",
            "from": "2025-06-01 00:00:00",
            "to": "2025-06-10 00:00:00"
        }
        
        assert payload == expected_payload
    
    def test_date_edge_cases(self):
        """Test edge cases in date validation."""
        # Test leap year February 29th
        request = OrderFeedRequest(**{
            "from": "2024-02-29 00:00:00",
            "to": "2024-03-05 00:00:00"
        })
        assert request.from_date == "2024-02-29 00:00:00"
        assert request.to_date == "2024-03-05 00:00:00"
        
        # Test year boundary
        request = OrderFeedRequest(**{
            "from": "2024-12-15 00:00:00",
            "to": "2025-01-15 00:00:00"
        })
        assert request.from_date == "2024-12-15 00:00:00"
        assert request.to_date == "2025-01-15 00:00:00"