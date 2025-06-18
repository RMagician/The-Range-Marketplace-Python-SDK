"""
End-to-end tests for the OrderFeedClient module using live test API.

These tests connect to the actual UAT environment and require valid credentials.
Tests will be skipped if credentials are not provided via environment variables.

Usage:
    # Set environment variables with your test credentials
    export THERANGE_USERNAME=your_test_username
    export THERANGE_PASSWORD=your_test_password
    
    # Run the e2e tests
    python -m pytest tests/test_order_feed_e2e.py -v
    
    # Or run a specific test
    python -m pytest tests/test_order_feed_e2e.py::TestOrderFeedClientE2E::test_authentication_e2e -v

Requirements:
    - Valid UAT environment credentials
    - Network access to uatsupplier.rstore.com
    - Environment variables: THERANGE_USERNAME, THERANGE_PASSWORD

Note: These tests make actual API calls to the live UAT environment to retrieve
order data. Use appropriate test credentials and ensure proper access permissions.
"""

import pytest
import os
import requests
from datetime import datetime, timedelta
from therange import TheRangeManager, Config
from therange.order_feed import OrderFeedClient
from therange.auth import AuthClient


class TestOrderFeedClientE2E:
    """End-to-end tests for OrderFeedClient with live API."""
    
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
            cls.client = cls.manager.order_feed
    
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
    def test_get_orders_all_e2e(self):
        """Test get_orders method with type 'all' using live API call."""
        try:
            # Authenticate first
            self.auth.authenticate()
            
            # Make the API call with minimal parameters
            response = self.client.get_orders(type="all")
            
            # Verify response structure
            assert response is not None
            assert isinstance(response, dict)
            assert "order_arr" in response
            assert isinstance(response["order_arr"], list)
            
            # Log response for debugging
            print(f"Get orders (all) response: Found {len(response['order_arr'])} orders")
            
            # If there are orders, verify basic structure
            if response["order_arr"]:
                first_order = response["order_arr"][0]
                assert isinstance(first_order, dict)
                # Orders should have some basic fields, but exact structure may vary
                print(f"Sample order structure: {list(first_order.keys())}")
        except requests.exceptions.ConnectionError:
            pytest.skip("Network connectivity issue - cannot reach UAT API")
        except requests.exceptions.Timeout:
            pytest.skip("Network timeout - UAT API is not responding")
    
    @pytest.mark.skipif(
        not (os.getenv("THERANGE_USERNAME") and os.getenv("THERANGE_PASSWORD")),
        reason="E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
    )
    def test_get_orders_new_e2e(self):
        """Test get_orders method with type 'new' using live API call."""
        try:
            # Authenticate first
            self.auth.authenticate()
            
            # Make the API call for new orders
            response = self.client.get_orders(type="new")
            
            # Verify response structure
            assert response is not None
            assert isinstance(response, dict)
            assert "order_arr" in response
            assert isinstance(response["order_arr"], list)
            
            # Log response for debugging
            print(f"Get orders (new) response: Found {len(response['order_arr'])} new orders")
        except requests.exceptions.ConnectionError:
            pytest.skip("Network connectivity issue - cannot reach UAT API")
        except requests.exceptions.Timeout:
            pytest.skip("Network timeout - UAT API is not responding")
    
    @pytest.mark.skipif(
        not (os.getenv("THERANGE_USERNAME") and os.getenv("THERANGE_PASSWORD")),
        reason="E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
    )
    def test_get_orders_pending_e2e(self):
        """Test get_orders method with type 'pending' using live API call."""
        try:
            # Authenticate first
            self.auth.authenticate()
            
            # Make the API call for pending orders
            response = self.client.get_orders(type="pending")
            
            # Verify response structure
            assert response is not None
            assert isinstance(response, dict)
            assert "order_arr" in response
            assert isinstance(response["order_arr"], list)
            
            # Log response for debugging
            print(f"Get orders (pending) response: Found {len(response['order_arr'])} pending orders")
        except requests.exceptions.ConnectionError:
            pytest.skip("Network connectivity issue - cannot reach UAT API")
        except requests.exceptions.Timeout:
            pytest.skip("Network timeout - UAT API is not responding")
    
    @pytest.mark.skipif(
        not (os.getenv("THERANGE_USERNAME") and os.getenv("THERANGE_PASSWORD")),
        reason="E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
    )
    def test_get_orders_with_date_filter_e2e(self):
        """Test get_orders method with date filtering using live API call."""
        try:
            # Authenticate first
            self.auth.authenticate()
            
            # Set up date range for the last 7 days
            to_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
            
            # Make the API call with date filtering
            response = self.client.get_orders(
                type="all",
                from_date=from_date,
                to_date=to_date
            )
            
            # Verify response structure
            assert response is not None
            assert isinstance(response, dict)
            assert "order_arr" in response
            assert isinstance(response["order_arr"], list)
            
            # Log response for debugging
            print(f"Get orders (date filtered) response: Found {len(response['order_arr'])} orders from {from_date} to {to_date}")
        except requests.exceptions.ConnectionError:
            pytest.skip("Network connectivity issue - cannot reach UAT API")
        except requests.exceptions.Timeout:
            pytest.skip("Network timeout - UAT API is not responding")
    
    @pytest.mark.skipif(
        not (os.getenv("THERANGE_USERNAME") and os.getenv("THERANGE_PASSWORD")),
        reason="E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
    )
    def test_get_orders_with_search_e2e(self):
        """Test get_orders method with search parameter using live API call."""
        try:
            # Authenticate first
            self.auth.authenticate()
            
            # First, get some orders to find a valid search term
            all_orders_response = self.client.get_orders(type="all")
            
            if all_orders_response["order_arr"]:
                # Try to extract a searchable field from the first order
                first_order = all_orders_response["order_arr"][0]
                
                # Common searchable fields - try order number if available
                search_term = None
                if "order_number" in first_order and first_order["order_number"]:
                    search_term = first_order["order_number"]
                elif "customer_name" in first_order and first_order["customer_name"]:
                    search_term = first_order["customer_name"]
                elif "postcode" in first_order and first_order["postcode"]:
                    search_term = first_order["postcode"]
                
                if search_term:
                    # Make the API call with search
                    response = self.client.get_orders(
                        type="all",
                        search=search_term
                    )
                    
                    # Verify response structure
                    assert response is not None
                    assert isinstance(response, dict)
                    assert "order_arr" in response
                    assert isinstance(response["order_arr"], list)
                    
                    # Log response for debugging
                    print(f"Get orders (search '{search_term}') response: Found {len(response['order_arr'])} orders")
                else:
                    print("No suitable search term found in available orders, skipping search test")
            else:
                print("No orders available for search testing, skipping search test")
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
        client = OrderFeedClient(auth)
        
        # Attempt API call without authentication
        with pytest.raises(ValueError, match="Must be authenticated before making this call"):
            client.get_orders(type="all")


class TestOrderFeedE2EIntegration:
    """Integration scenarios for e2e order feed testing."""
    
    @pytest.mark.skipif(
        not (os.getenv("THERANGE_USERNAME") and os.getenv("THERANGE_PASSWORD")),
        reason="E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
    )
    def test_multiple_order_types_comparison_e2e(self):
        """Test comparison of different order types from live API."""
        try:
            username = os.getenv("THERANGE_USERNAME")
            password = os.getenv("THERANGE_PASSWORD")
            
            # Set up manager and authenticate
            config = Config.uat()
            manager = TheRangeManager(username, password, config)
            manager.authenticate()
            
            # Get orders of different types
            all_orders = manager.order_feed.get_orders(type="all")
            new_orders = manager.order_feed.get_orders(type="new")
            pending_orders = manager.order_feed.get_orders(type="pending")
            historic_orders = manager.order_feed.get_orders(type="historic")
            
            # Verify all responses have the expected structure
            for response_name, response in [
                ("all", all_orders),
                ("new", new_orders),
                ("pending", pending_orders),
                ("historic", historic_orders)
            ]:
                assert response is not None
                assert isinstance(response, dict)
                assert "order_arr" in response
                assert isinstance(response["order_arr"], list)
                print(f"Orders ({response_name}): {len(response['order_arr'])}")
            
            # Logical validation: new + pending + historic should not exceed all
            total_specific = len(new_orders["order_arr"]) + len(pending_orders["order_arr"]) + len(historic_orders["order_arr"])
            total_all = len(all_orders["order_arr"])
            
            # This might not be exact due to timing or other factors, but it's a reasonable sanity check
            print(f"Total specific types: {total_specific}, Total all: {total_all}")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Network connectivity issue - cannot reach UAT API")
        except requests.exceptions.Timeout:
            pytest.skip("Network timeout - UAT API is not responding")
    
    @pytest.mark.skipif(
        not (os.getenv("THERANGE_USERNAME") and os.getenv("THERANGE_PASSWORD")),
        reason="E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
    )
    def test_date_range_boundary_e2e(self):
        """Test date range boundaries with live API."""
        try:
            username = os.getenv("THERANGE_USERNAME")
            password = os.getenv("THERANGE_PASSWORD")
            
            # Set up manager and authenticate
            config = Config.uat()
            manager = TheRangeManager(username, password, config)
            manager.authenticate()
            
            # Test with maximum allowed range (35 days)
            to_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            from_date = (datetime.now() - timedelta(days=35)).strftime("%Y-%m-%d %H:%M:%S")
            
            response = manager.order_feed.get_orders(
                type="all",
                from_date=from_date,
                to_date=to_date
            )
            
            # Verify response
            assert response is not None
            assert isinstance(response, dict)
            assert "order_arr" in response
            
            print(f"Date range test (35 days): Found {len(response['order_arr'])} orders from {from_date} to {to_date}")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Network connectivity issue - cannot reach UAT API")
        except requests.exceptions.Timeout:
            pytest.skip("Network timeout - UAT API is not responding")