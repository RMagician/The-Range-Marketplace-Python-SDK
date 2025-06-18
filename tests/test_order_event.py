"""
Unit tests for the OrderEventClient module.

Tests order event functionality including Pydantic model validation,
dispatch order operations, cancel order operations, and various error scenarios.
"""

import pytest
from unittest.mock import Mock, patch
from therange.order_event import (
    OrderItem, 
    DispatchOrderRequest, 
    CancelOrderRequest, 
    OrderEventClient
)
from therange.auth import AuthClient


class TestOrderItem:
    """Test OrderItem model validation."""
    
    def test_valid_order_item(self):
        """Test valid OrderItem creation."""
        item = OrderItem(code="ABC123", qty=5)
        
        assert item.code == "ABC123"
        assert item.qty == 5
    
    def test_order_item_minimum_qty(self):
        """Test OrderItem with minimum valid quantity."""
        item = OrderItem(code="TEST", qty=1)
        
        assert item.code == "TEST"
        assert item.qty == 1
    
    def test_order_item_invalid_qty_zero(self):
        """Test OrderItem with invalid quantity of zero."""
        with pytest.raises(ValueError, match="Input should be greater than or equal to 1"):
            OrderItem(code="TEST", qty=0)
    
    def test_order_item_invalid_qty_negative(self):
        """Test OrderItem with negative quantity."""
        with pytest.raises(ValueError, match="Input should be greater than or equal to 1"):
            OrderItem(code="TEST", qty=-1)
    
    def test_order_item_missing_code(self):
        """Test OrderItem without required code field."""
        with pytest.raises(ValueError, match="Field required"):
            OrderItem(qty=1)
    
    def test_order_item_missing_qty(self):
        """Test OrderItem without required qty field."""
        with pytest.raises(ValueError, match="Field required"):
            OrderItem(code="TEST")


class TestDispatchOrderRequest:
    """Test DispatchOrderRequest model validation."""
    
    def test_valid_dispatch_request(self):
        """Test valid DispatchOrderRequest creation."""
        items = [{"code": "ABC123", "qty": 2}]
        request = DispatchOrderRequest(
            order_number="ORD001",
            items=items,
            despatch_date="2023-12-01 10:30:00",
            delivery_service="Standard",
            courier_name="DHL",
            tracking_reference="TR123456"
        )
        
        assert request.order_number == "ORD001"
        assert len(request.items) == 1
        assert request.items[0].code == "ABC123"
        assert request.items[0].qty == 2
        assert request.despatch_date == "2023-12-01 10:30:00"
        assert request.delivery_service == "Standard"
        assert request.courier_name == "DHL"
        assert request.tracking_reference == "TR123456"
        assert request.earliest_delivery is None
        assert request.latest_delivery is None
    
    def test_dispatch_request_with_delivery_dates(self):
        """Test DispatchOrderRequest with optional delivery dates."""
        items = [{"code": "ABC123", "qty": 1}]
        request = DispatchOrderRequest(
            order_number="ORD002",
            items=items,
            despatch_date="2023-12-01 10:30:00",
            delivery_service="Express",
            courier_name="UPS",
            tracking_reference="UP987654",
            earliest_delivery="2023-12-03",
            latest_delivery="2023-12-05"
        )
        
        assert request.earliest_delivery == "2023-12-03"
        assert request.latest_delivery == "2023-12-05"
    
    def test_dispatch_request_empty_items(self):
        """Test DispatchOrderRequest with empty items list."""
        with pytest.raises(ValueError, match="items must be a non-empty list"):
            DispatchOrderRequest(
                order_number="ORD003",
                items=[],
                despatch_date="2023-12-01 10:30:00",
                delivery_service="Standard",
                courier_name="DHL",
                tracking_reference="TR123456"
            )
    
    def test_dispatch_request_invalid_despatch_date_format(self):
        """Test DispatchOrderRequest with invalid despatch_date format."""
        items = [{"code": "ABC123", "qty": 1}]
        with pytest.raises(ValueError, match="despatch_date must be in format YYYY-MM-DD HH:MM:SS"):
            DispatchOrderRequest(
                order_number="ORD004",
                items=items,
                despatch_date="2023-12-01",  # Missing time
                delivery_service="Standard",
                courier_name="DHL",
                tracking_reference="TR123456"
            )
    
    def test_dispatch_request_invalid_earliest_delivery_format(self):
        """Test DispatchOrderRequest with invalid earliest_delivery format."""
        items = [{"code": "ABC123", "qty": 1}]
        with pytest.raises(ValueError, match="delivery dates must be in format YYYY-MM-DD"):
            DispatchOrderRequest(
                order_number="ORD005",
                items=items,
                despatch_date="2023-12-01 10:30:00",
                delivery_service="Standard",
                courier_name="DHL",
                tracking_reference="TR123456",
                earliest_delivery="2023-12-01 10:30:00"  # Should be date only
            )
    
    def test_dispatch_request_invalid_latest_delivery_format(self):
        """Test DispatchOrderRequest with invalid latest_delivery format."""
        items = [{"code": "ABC123", "qty": 1}]
        with pytest.raises(ValueError, match="delivery dates must be in format YYYY-MM-DD"):
            DispatchOrderRequest(
                order_number="ORD006",
                items=items,
                despatch_date="2023-12-01 10:30:00",
                delivery_service="Standard",
                courier_name="DHL",
                tracking_reference="TR123456",
                latest_delivery="Dec 5, 2023"  # Wrong format
            )
    
    def test_dispatch_request_missing_required_fields(self):
        """Test DispatchOrderRequest with missing required fields."""
        with pytest.raises(ValueError, match="Field required"):
            DispatchOrderRequest(
                items=[{"code": "ABC123", "qty": 1}],
                despatch_date="2023-12-01 10:30:00",
                delivery_service="Standard",
                courier_name="DHL",
                tracking_reference="TR123456"
                # Missing order_number
            )


class TestCancelOrderRequest:
    """Test CancelOrderRequest model validation."""
    
    def test_valid_cancel_request(self):
        """Test valid CancelOrderRequest creation."""
        items = [{"code": "ABC123", "qty": 2}]
        request = CancelOrderRequest(
            order_number="ORD007",
            items=items,
            cancel_code="Stock not available",
            cancel_reason="Product discontinued"
        )
        
        assert request.order_number == "ORD007"
        assert len(request.items) == 1
        assert request.items[0].code == "ABC123"
        assert request.items[0].qty == 2
        assert request.cancel_code == "Stock not available"
        assert request.cancel_reason == "Product discontinued"
    
    def test_cancel_request_default_reason(self):
        """Test CancelOrderRequest with default empty reason."""
        items = [{"code": "ABC123", "qty": 1}]
        request = CancelOrderRequest(
            order_number="ORD008",
            items=items,
            cancel_code="Unable to contact customer to arrange delivery"
        )
        
        assert request.cancel_reason == ""
    
    def test_cancel_request_all_valid_codes(self):
        """Test CancelOrderRequest with all valid cancel codes."""
        items = [{"code": "ABC123", "qty": 1}]
        valid_codes = [
            "Stock not available",
            "Unable to contact customer to arrange delivery",
            "Unable to deliver to address"
        ]
        
        for code in valid_codes:
            request = CancelOrderRequest(
                order_number="ORD009",
                items=items,
                cancel_code=code
            )
            assert request.cancel_code == code
    
    def test_cancel_request_invalid_cancel_code(self):
        """Test CancelOrderRequest with invalid cancel code."""
        items = [{"code": "ABC123", "qty": 1}]
        with pytest.raises(ValueError, match="cancel_code must be one of"):
            CancelOrderRequest(
                order_number="ORD010",
                items=items,
                cancel_code="Invalid reason",
                cancel_reason="Test"
            )
    
    def test_cancel_request_empty_items(self):
        """Test CancelOrderRequest with empty items list."""
        with pytest.raises(ValueError, match="items must be a non-empty list"):
            CancelOrderRequest(
                order_number="ORD011",
                items=[],
                cancel_code="Stock not available"
            )


class TestOrderEventClient:
    """Test OrderEventClient functionality."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_auth = Mock(spec=AuthClient)
        self.mock_auth.session = Mock()
        self.mock_auth.supplier_id = "12345"
        self.client = OrderEventClient(self.mock_auth)
    
    def test_init(self):
        """Test OrderEventClient initialization."""
        assert self.client.auth == self.mock_auth
    
    def test_send_event_success(self):
        """Test successful send_event call."""
        # Setup mock response
        mock_response = {"status": "success", "event_id": "EVT123"}
        self.client._post = Mock(return_value=mock_response)
        
        # Test send_event
        payload = {"type": "test", "data": "test_data"}
        result = self.client.send_event(payload)
        
        # Verify
        assert result == mock_response
        self.client._post.assert_called_once_with("order_event.api", payload)
    
    def test_dispatch_order_success(self):
        """Test successful dispatch_order call."""
        # Setup mock response
        mock_response = {"status": "dispatched", "order_number": "ORD001"}
        self.client._post = Mock(return_value=mock_response)
        
        # Test dispatch_order
        items = [{"code": "ABC123", "qty": 2}]
        result = self.client.dispatch_order(
            order_number="ORD001",
            items=items,
            despatch_date="2023-12-01 10:30:00",
            delivery_service="Standard",
            courier_name="DHL",
            tracking_reference="TR123456"
        )
        
        # Verify result
        assert result == mock_response
        
        # Verify the API call was made with correct payload
        self.client._post.assert_called_once()
        call_args = self.client._post.call_args
        assert call_args[0][0] == "order_event.api"
        
        payload = call_args[0][1]
        assert payload["order_number"] == "ORD001"
        assert payload["delivery_service"] == "Standard"
        assert payload["courier_name"] == "DHL"
        assert payload["despatch_date"] == "2023-12-01 10:30:00"
        assert payload["tracking_reference"] == "TR123456"
        assert len(payload["item_arr"]) == 1
        assert payload["item_arr"][0]["code"] == "ABC123"
        assert payload["item_arr"][0]["qty"] == 2
        assert "earliest_delivery" not in payload
        assert "latest_delivery" not in payload
    
    def test_dispatch_order_with_delivery_dates(self):
        """Test dispatch_order with optional delivery dates."""
        # Setup mock response
        mock_response = {"status": "dispatched"}
        self.client._post = Mock(return_value=mock_response)
        
        # Test dispatch_order with delivery dates
        items = [{"code": "ABC123", "qty": 1}]
        result = self.client.dispatch_order(
            order_number="ORD002",
            items=items,
            despatch_date="2023-12-01 10:30:00",
            delivery_service="Express",
            courier_name="UPS",
            tracking_reference="UP987654",
            earliest_delivery="2023-12-03",
            latest_delivery="2023-12-05"
        )
        
        # Verify result
        assert result == mock_response
        
        # Verify delivery dates are included in payload
        call_args = self.client._post.call_args
        payload = call_args[0][1]
        assert payload["earliest_delivery"] == "2023-12-03"
        assert payload["latest_delivery"] == "2023-12-05"
    
    def test_dispatch_order_no_session(self):
        """Test dispatch_order without authenticated session."""
        self.mock_auth.session = None
        
        items = [{"code": "ABC123", "qty": 1}]
        with pytest.raises(ValueError, match="Must be authenticated before making this call"):
            self.client.dispatch_order(
                order_number="ORD003",
                items=items,
                despatch_date="2023-12-01 10:30:00",
                delivery_service="Standard",
                courier_name="DHL",
                tracking_reference="TR123456"
            )
    
    def test_dispatch_order_no_supplier_id(self):
        """Test dispatch_order without supplier_id."""
        self.mock_auth.supplier_id = None
        
        items = [{"code": "ABC123", "qty": 1}]
        with pytest.raises(ValueError, match="Must be authenticated before making this call"):
            self.client.dispatch_order(
                order_number="ORD004",
                items=items,
                despatch_date="2023-12-01 10:30:00",
                delivery_service="Standard",
                courier_name="DHL",
                tracking_reference="TR123456"
            )
    
    def test_dispatch_order_validation_error(self):
        """Test dispatch_order with validation error."""
        items = []  # Empty items will cause validation error
        with pytest.raises(ValueError, match="Invalid dispatch request"):
            self.client.dispatch_order(
                order_number="ORD005",
                items=items,
                despatch_date="2023-12-01 10:30:00",
                delivery_service="Standard",
                courier_name="DHL",
                tracking_reference="TR123456"
            )
    
    def test_cancel_order_success(self):
        """Test successful cancel_order call."""
        # Setup mock response
        mock_response = {"status": "cancelled", "order_number": "ORD006"}
        self.client._post = Mock(return_value=mock_response)
        
        # Test cancel_order
        items = [{"code": "ABC123", "qty": 2}]
        result = self.client.cancel_order(
            order_number="ORD006",
            items=items,
            cancel_code="Stock not available",
            cancel_reason="Product discontinued"
        )
        
        # Verify result
        assert result == mock_response
        
        # Verify the API call was made with correct payload
        self.client._post.assert_called_once()
        call_args = self.client._post.call_args
        assert call_args[0][0] == "order_event.api"
        
        payload = call_args[0][1]
        assert payload["order_number"] == "ORD006"
        assert payload["cancel_code"] == "Stock not available"
        assert payload["cancel_reason"] == "Product discontinued"
        assert len(payload["item_arr"]) == 1
        assert payload["item_arr"][0]["code"] == "ABC123"
        assert payload["item_arr"][0]["qty"] == 2
    
    def test_cancel_order_default_reason(self):
        """Test cancel_order with default empty reason."""
        # Setup mock response
        mock_response = {"status": "cancelled"}
        self.client._post = Mock(return_value=mock_response)
        
        # Test cancel_order without reason
        items = [{"code": "ABC123", "qty": 1}]
        result = self.client.cancel_order(
            order_number="ORD007",
            items=items,
            cancel_code="Unable to contact customer to arrange delivery"
        )
        
        # Verify result
        assert result == mock_response
        
        # Verify empty reason is included
        call_args = self.client._post.call_args
        payload = call_args[0][1]
        assert payload["cancel_reason"] == ""
    
    def test_cancel_order_no_session(self):
        """Test cancel_order without authenticated session."""
        self.mock_auth.session = None
        
        items = [{"code": "ABC123", "qty": 1}]
        with pytest.raises(ValueError, match="Must be authenticated before making this call"):
            self.client.cancel_order(
                order_number="ORD008",
                items=items,
                cancel_code="Stock not available"
            )
    
    def test_cancel_order_no_supplier_id(self):
        """Test cancel_order without supplier_id."""
        self.mock_auth.supplier_id = None
        
        items = [{"code": "ABC123", "qty": 1}]
        with pytest.raises(ValueError, match="Must be authenticated before making this call"):
            self.client.cancel_order(
                order_number="ORD009",
                items=items,
                cancel_code="Stock not available"
            )
    
    def test_cancel_order_validation_error(self):
        """Test cancel_order with validation error."""
        items = [{"code": "ABC123", "qty": 1}]
        with pytest.raises(ValueError, match="Invalid cancel request"):
            self.client.cancel_order(
                order_number="ORD010",
                items=items,
                cancel_code="Invalid cancel code"  # Invalid code will cause validation error
            )


class TestOrderEventClientIntegration:
    """Integration tests for OrderEventClient with mocked HTTP responses."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_auth = Mock(spec=AuthClient)
        self.mock_auth.session = Mock()
        self.mock_auth.supplier_id = "12345"
        self.mock_auth.mode = "test"
        self.mock_auth.base_url = "https://test.api.com/"
        self.client = OrderEventClient(self.mock_auth)
    
    @patch('therange.base_client.BaseClient._post')
    def test_dispatch_order_http_success(self, mock_post):
        """Test dispatch_order with successful HTTP response."""
        mock_post.return_value = {"status": "success", "message": "Order dispatched"}
        
        items = [{"code": "TEST123", "qty": 3}]
        result = self.client.dispatch_order(
            order_number="ORD100",
            items=items,
            despatch_date="2023-12-15 14:30:00",
            delivery_service="Express",
            courier_name="FedEx",
            tracking_reference="FX987654321"
        )
        
        assert result["status"] == "success"
        assert result["message"] == "Order dispatched"
        mock_post.assert_called_once()
    
    @patch('therange.base_client.BaseClient._post')
    def test_cancel_order_http_success(self, mock_post):
        """Test cancel_order with successful HTTP response."""
        mock_post.return_value = {"status": "cancelled", "message": "Order cancelled"}
        
        items = [{"code": "TEST456", "qty": 1}]
        result = self.client.cancel_order(
            order_number="ORD101",
            items=items,
            cancel_code="Unable to deliver to address",
            cancel_reason="Address not accessible"
        )
        
        assert result["status"] == "cancelled"
        assert result["message"] == "Order cancelled"
        mock_post.assert_called_once()
    
    @patch('therange.base_client.BaseClient._post')
    def test_send_event_http_success(self, mock_post):
        """Test send_event with successful HTTP response."""
        mock_post.return_value = {"event_id": "EVT789", "processed": True}
        
        event_payload = {
            "type": "custom_event",
            "order_number": "ORD102",
            "data": {"custom_field": "custom_value"}
        }
        
        result = self.client.send_event(event_payload)
        
        assert result["event_id"] == "EVT789"
        assert result["processed"] is True
        mock_post.assert_called_once_with("order_event.api", event_payload)