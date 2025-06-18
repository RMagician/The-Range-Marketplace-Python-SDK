"""
End-to-end tests for the OrderEventClient module using live test API.

These tests connect to the actual UAT environment and require valid credentials.
Tests will be skipped if credentials are not provided via environment variables.

Usage:
    # Set environment variables with your test credentials
    export THERANGE_USERNAME=your_test_username
    export THERANGE_PASSWORD=your_test_password
    
    # Run the e2e tests
    python -m pytest tests/test_order_event_e2e.py -v
    
    # Or run a specific test
    python -m pytest tests/test_order_event_e2e.py::TestOrderEventClientE2E::test_authentication_e2e -v

Requirements:
    - Valid UAT environment credentials
    - Network access to uatsupplier.rstore.com
    - Environment variables: THERANGE_USERNAME, THERANGE_PASSWORD

Note: These tests make actual API calls to the live UAT environment and will create
test data. Use appropriate test credentials and clean up any test data as needed.
"""

import pytest
import os
import requests
from datetime import datetime, timedelta
from therange import TheRangeManager, Config
from therange.order_event import OrderEventClient
from therange.auth import AuthClient


class TestOrderEventClientE2E:
    """End-to-end tests for OrderEventClient with live API."""
    
    @classmethod
    def setup_class(cls):
        """Set up test fixtures before running the test class."""
        cls.username = os.getenv("THERANGE_USERNAME")
        cls.password = os.getenv("THERANGE_PASSWORD")
        cls.skip_reason = "E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
        
        if cls.username and cls.password:
            cls.config = Config.uat()
            cls.manager = TheRangeManager(cls.username, cls.password, cls.config)
            cls.auth = cls.manager.auth
            cls.client = cls.manager.order_event
    
    @pytest.mark.skipif(
        not (os.getenv("THERANGE_USERNAME") and os.getenv("THERANGE_PASSWORD")),
        reason="E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
    )
    def test_network_connectivity_e2e(self):
        """Test network connectivity to the UAT API."""
        config = Config.uat()
        try:
            response = requests.get(config.base_url, timeout=10)
            # We don't care about the response content, just that we can reach the server
            assert True  # If we get here, connectivity is working
        except requests.exceptions.ConnectionError:
            pytest.skip("Network connectivity issue - cannot reach UAT API")
        except requests.exceptions.Timeout:
            pytest.skip("Network timeout - UAT API is not responding")
    
    @pytest.mark.skipif(
        not (os.getenv("THERANGE_USERNAME") and os.getenv("THERANGE_PASSWORD")),
        reason="E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
    )
    def test_authentication_e2e(self):
        """Test successful authentication against the live UAT API."""
        try:
            # Authenticate with the live API
            auth_response = self.auth.authenticate()
            
            # Verify authentication was successful
            assert auth_response is not None
            assert self.auth.session is not None
            assert self.auth.supplier_id is not None
            assert self.auth.ksi is not None
            assert self.auth.mode is not None
            
            # Verify we're using the UAT environment
            assert "uatsupplier.rstore.com" in self.auth.base_url
        except requests.exceptions.ConnectionError:
            pytest.skip("Network connectivity issue - cannot reach UAT API")
        except requests.exceptions.Timeout:
            pytest.skip("Network timeout - UAT API is not responding")
    
    @pytest.mark.skipif(
        not (os.getenv("THERANGE_USERNAME") and os.getenv("THERANGE_PASSWORD")),
        reason="E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
    )
    def test_dispatch_order_e2e(self):
        """Test dispatch_order method with live API call."""
        try:
            # Authenticate first
            self.auth.authenticate()
            
            # Generate unique order number and tracking reference for testing
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            test_order_number = f"E2E_TEST_{timestamp}"
            tracking_ref = f"TR_E2E_{timestamp}"
            
            # Prepare test data
            items = [{"code": "E2E_TEST_PRODUCT", "qty": 1}]
            despatch_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            earliest_delivery = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
            latest_delivery = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
            
            # Make the API call
            response = self.client.dispatch_order(
                order_number=test_order_number,
                items=items,
                despatch_date=despatch_date,
                delivery_service="Standard",
                courier_name="E2E Test Courier",
                tracking_reference=tracking_ref,
                earliest_delivery=earliest_delivery,
                latest_delivery=latest_delivery
            )
            
            # Verify response structure (actual response may vary based on API implementation)
            assert response is not None
            assert isinstance(response, dict)
            
            # Log response for debugging
            print(f"Dispatch order response: {response}")
        except requests.exceptions.ConnectionError:
            pytest.skip("Network connectivity issue - cannot reach UAT API")
        except requests.exceptions.Timeout:
            pytest.skip("Network timeout - UAT API is not responding")
    
    @pytest.mark.skipif(
        not (os.getenv("THERANGE_USERNAME") and os.getenv("THERANGE_PASSWORD")),
        reason="E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
    )
    def test_cancel_order_e2e(self):
        """Test cancel_order method with live API call."""
        try:
            # Authenticate first
            self.auth.authenticate()
            
            # Generate unique order number for testing
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            test_order_number = f"E2E_CANCEL_TEST_{timestamp}"
            
            # Prepare test data
            items = [{"code": "E2E_CANCEL_PRODUCT", "qty": 2}]
            
            # Make the API call
            response = self.client.cancel_order(
                order_number=test_order_number,
                items=items,
                cancel_code="Stock not available",
                cancel_reason="E2E test cancellation"
            )
            
            # Verify response structure (actual response may vary based on API implementation)
            assert response is not None
            assert isinstance(response, dict)
            
            # Log response for debugging
            print(f"Cancel order response: {response}")
        except requests.exceptions.ConnectionError:
            pytest.skip("Network connectivity issue - cannot reach UAT API")
        except requests.exceptions.Timeout:
            pytest.skip("Network timeout - UAT API is not responding")
    
    @pytest.mark.skipif(
        not (os.getenv("THERANGE_USERNAME") and os.getenv("THERANGE_PASSWORD")),
        reason="E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
    )
    def test_send_event_e2e(self):
        """Test send_event method with live API call."""
        try:
            # Authenticate first
            self.auth.authenticate()
            
            # Generate unique test data
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            
            # Prepare test event payload
            event_payload = {
                "type": "e2e_test_event",
                "order_number": f"E2E_EVENT_TEST_{timestamp}",
                "timestamp": timestamp,
                "test_data": "End-to-end test event data"
            }
            
            # Make the API call
            response = self.client.send_event(event_payload)
            
            # Verify response structure (actual response may vary based on API implementation)
            assert response is not None
            assert isinstance(response, dict)
            
            # Log response for debugging
            print(f"Send event response: {response}")
        except requests.exceptions.ConnectionError:
            pytest.skip("Network connectivity issue - cannot reach UAT API")
        except requests.exceptions.Timeout:
            pytest.skip("Network timeout - UAT API is not responding")
    
    @pytest.mark.skipif(
        not (os.getenv("THERANGE_USERNAME") and os.getenv("THERANGE_PASSWORD")),
        reason="E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
    )
    def test_authentication_error_handling_e2e(self):
        """Test authentication error handling with invalid credentials."""
        # Create auth client with invalid credentials
        config = Config.uat()
        invalid_auth = AuthClient("invalid_user", "invalid_pass", config)
        
        # Attempt authentication and expect it to fail
        try:
            with pytest.raises(PermissionError, match="Unauthorized: Invalid credentials"):
                invalid_auth.authenticate()
        except requests.exceptions.ConnectionError:
            pytest.skip("Network connectivity issue - cannot reach UAT API")
        except Exception as e:
            # If we get any other exception, re-raise it as it might be what we're testing for
            if "Unauthorized" in str(e) or "401" in str(e):
                # This is expected - authentication failed as intended
                pass
            else:
                raise
    
    @pytest.mark.skipif(
        not (os.getenv("THERANGE_USERNAME") and os.getenv("THERANGE_PASSWORD")),
        reason="E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
    )
    def test_unauthenticated_api_call_e2e(self):
        """Test that API calls fail without authentication."""
        # Create client without authentication
        config = Config.uat()
        auth = AuthClient(self.username, self.password, config)
        client = OrderEventClient(auth)
        
        # Attempt API call without authentication
        items = [{"code": "TEST", "qty": 1}]
        with pytest.raises(ValueError, match="Must be authenticated before making this call"):
            client.dispatch_order(
                order_number="TEST_ORDER",
                items=items,
                despatch_date="2023-12-01 10:30:00",
                delivery_service="Standard",
                courier_name="Test",
                tracking_reference="TEST123"
            )


class TestOrderEventE2EIntegration:
    """Integration scenarios for e2e order event testing."""
    
    @pytest.mark.skipif(
        not (os.getenv("THERANGE_USERNAME") and os.getenv("THERANGE_PASSWORD")),
        reason="E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
    )
    def test_full_order_lifecycle_e2e(self):
        """Test complete order lifecycle: dispatch then cancel."""
        try:
            username = os.getenv("THERANGE_USERNAME")
            password = os.getenv("THERANGE_PASSWORD")
            
            # Set up manager and authenticate
            config = Config.uat()
            manager = TheRangeManager(username, password, config)
            manager.authenticate()
            
            # Generate unique test data
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            test_order_number = f"E2E_LIFECYCLE_{timestamp}"
            items = [{"code": "LIFECYCLE_PRODUCT", "qty": 1}]
            
            # First, dispatch the order
            despatch_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            dispatch_response = manager.order_event.dispatch_order(
                order_number=test_order_number,
                items=items,
                despatch_date=despatch_date,
                delivery_service="Express",
                courier_name="Lifecycle Test Courier",
                tracking_reference=f"LC_{timestamp}"
            )
            
            # Verify dispatch response
            assert dispatch_response is not None
            print(f"Dispatch response: {dispatch_response}")
            
            # Then, cancel the same order
            cancel_response = manager.order_event.cancel_order(
                order_number=test_order_number,
                items=items,
                cancel_code="Unable to deliver to address",
                cancel_reason="E2E lifecycle test - order cancelled after dispatch"
            )
            
            # Verify cancel response
            assert cancel_response is not None
            print(f"Cancel response: {cancel_response}")
        except requests.exceptions.ConnectionError:
            pytest.skip("Network connectivity issue - cannot reach UAT API")
        except requests.exceptions.Timeout:
            pytest.skip("Network timeout - UAT API is not responding")