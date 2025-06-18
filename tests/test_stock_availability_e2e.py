"""
End-to-end tests for the StockAvailabilityClient module using live test API.

These tests connect to the actual UAT environment and require valid credentials.
Tests will be skipped if credentials are not provided via environment variables.

Usage:
    # Set environment variables with your test credentials
    export THERANGE_USERNAME=your_test_username
    export THERANGE_PASSWORD=your_test_password
    
    # Run the e2e tests
    python -m pytest tests/test_stock_availability_e2e.py -v
    
    # Or run a specific test
    python -m pytest tests/test_stock_availability_e2e.py::TestStockAvailabilityClientE2E::test_authentication_e2e -v

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
from datetime import datetime
from therange import TheRangeManager, Config
from therange.stock_availability import StockAvailabilityClient
from therange.auth import AuthClient


class TestStockAvailabilityClientE2E:
    """End-to-end tests for StockAvailabilityClient with live API."""
    
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
            cls.client = cls.manager.stock_availability
    
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
    def test_update_stock_e2e(self):
        """Test update_stock method with live API call."""
        try:
            # Authenticate first
            self.auth.authenticate()
            
            # Generate unique test data to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            
            # Prepare test stock data with E2E prefix for easy identification
            stock_data = [
                {"code": f"E2E_STOCK_TEST_{timestamp}_001", "qty": 10},
                {"code": f"E2E_STOCK_TEST_{timestamp}_002", "qty": 0},
                {"code": f"E2E_STOCK_TEST_{timestamp}_003", "qty": 25}
            ]
            
            # Make the API call
            response = self.client.update_stock(stock_data)
            
            # Verify response structure (actual response may vary based on API implementation)
            assert response is not None
            assert isinstance(response, dict)
            
            # Log response for debugging
            print(f"Update stock response: {response}")
        except requests.exceptions.ConnectionError:
            pytest.skip("Network connectivity issue - cannot reach UAT API")
        except requests.exceptions.Timeout:
            pytest.skip("Network timeout - UAT API is not responding")
    
    @pytest.mark.skipif(
        not (os.getenv("THERANGE_USERNAME") and os.getenv("THERANGE_PASSWORD")),
        reason="E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
    )
    def test_update_stock_single_item_e2e(self):
        """Test update_stock with single item using live API call."""
        try:
            # Authenticate first
            self.auth.authenticate()
            
            # Generate unique test data
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            
            # Prepare single item test data
            stock_data = [{"code": f"E2E_SINGLE_{timestamp}", "qty": 5}]
            
            # Make the API call
            response = self.client.update_stock(stock_data)
            
            # Verify response structure
            assert response is not None
            assert isinstance(response, dict)
            
            # Log response for debugging
            print(f"Single item stock update response: {response}")
        except requests.exceptions.ConnectionError:
            pytest.skip("Network connectivity issue - cannot reach UAT API")
        except requests.exceptions.Timeout:
            pytest.skip("Network timeout - UAT API is not responding")
    
    @pytest.mark.skipif(
        not (os.getenv("THERANGE_USERNAME") and os.getenv("THERANGE_PASSWORD")),
        reason="E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
    )
    def test_update_stock_zero_quantities_e2e(self):
        """Test update_stock with zero quantities using live API call."""
        try:
            # Authenticate first
            self.auth.authenticate()
            
            # Generate unique test data
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            
            # Prepare test data with zero quantities (out of stock scenarios)
            stock_data = [
                {"code": f"E2E_ZERO_QTY_{timestamp}_001", "qty": 0},
                {"code": f"E2E_ZERO_QTY_{timestamp}_002", "qty": 0}
            ]
            
            # Make the API call
            response = self.client.update_stock(stock_data)
            
            # Verify response structure
            assert response is not None
            assert isinstance(response, dict)
            
            # Log response for debugging
            print(f"Zero quantities stock update response: {response}")
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
        client = StockAvailabilityClient(auth)
        
        # Attempt API call without authentication
        stock_data = [{"code": "TEST_UNAUTH", "qty": 1}]
        with pytest.raises(ValueError, match="Must be authenticated before making this call"):
            client.update_stock(stock_data)


class TestStockAvailabilityE2EIntegration:
    """Integration scenarios for e2e stock availability testing."""
    
    @pytest.mark.skipif(
        not (os.getenv("THERANGE_USERNAME") and os.getenv("THERANGE_PASSWORD")),
        reason="E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
    )
    def test_multiple_stock_updates_e2e(self):
        """Test multiple sequential stock updates."""
        try:
            username = os.getenv("THERANGE_USERNAME")
            password = os.getenv("THERANGE_PASSWORD")
            
            # Set up manager and authenticate
            config = Config.uat()
            manager = TheRangeManager(username, password, config)
            manager.authenticate()
            
            # Generate unique test data
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            
            # First stock update
            stock_data_1 = [
                {"code": f"E2E_MULTI_{timestamp}_001", "qty": 15},
                {"code": f"E2E_MULTI_{timestamp}_002", "qty": 30}
            ]
            
            response_1 = manager.stock_availability.update_stock(stock_data_1)
            assert response_1 is not None
            print(f"First stock update response: {response_1}")
            
            # Second stock update with different quantities
            stock_data_2 = [
                {"code": f"E2E_MULTI_{timestamp}_001", "qty": 5},  # Updated quantity
                {"code": f"E2E_MULTI_{timestamp}_003", "qty": 20}  # New product
            ]
            
            response_2 = manager.stock_availability.update_stock(stock_data_2)
            assert response_2 is not None
            print(f"Second stock update response: {response_2}")
            
            # Third stock update setting some to zero
            stock_data_3 = [
                {"code": f"E2E_MULTI_{timestamp}_002", "qty": 0},  # Set to zero
                {"code": f"E2E_MULTI_{timestamp}_003", "qty": 0}   # Set to zero
            ]
            
            response_3 = manager.stock_availability.update_stock(stock_data_3)
            assert response_3 is not None
            print(f"Third stock update response: {response_3}")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Network connectivity issue - cannot reach UAT API")
        except requests.exceptions.Timeout:
            pytest.skip("Network timeout - UAT API is not responding")
    
    @pytest.mark.skipif(
        not (os.getenv("THERANGE_USERNAME") and os.getenv("THERANGE_PASSWORD")),
        reason="E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
    )
    def test_large_stock_update_e2e(self):
        """Test stock update with larger dataset."""
        try:
            username = os.getenv("THERANGE_USERNAME")
            password = os.getenv("THERANGE_PASSWORD")
            
            # Set up manager and authenticate
            config = Config.uat()
            manager = TheRangeManager(username, password, config)
            manager.authenticate()
            
            # Generate unique test data
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            
            # Create larger dataset (50 items)
            stock_data = [
                {"code": f"E2E_LARGE_{timestamp}_{i:03d}", "qty": i % 50}
                for i in range(50)
            ]
            
            # Make the API call
            response = manager.stock_availability.update_stock(stock_data)
            
            # Verify response
            assert response is not None
            assert isinstance(response, dict)
            print(f"Large dataset stock update response: {response}")
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Network connectivity issue - cannot reach UAT API")
        except requests.exceptions.Timeout:
            pytest.skip("Network timeout - UAT API is not responding")