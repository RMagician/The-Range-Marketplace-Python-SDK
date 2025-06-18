"""
End-to-end tests for the ProductFeedClient module using live test API.

These tests connect to the actual UAT environment and require valid credentials.
Tests will be skipped if credentials are not provided via environment variables.

Usage:
    # Set environment variables with your test credentials
    export THERANGE_USERNAME=your_test_username
    export THERANGE_PASSWORD=your_test_password
    
    # Run the e2e tests
    python -m pytest tests/test_product_feed_e2e.py -v
    
    # Or run a specific test
    python -m pytest tests/test_product_feed_e2e.py::TestProductFeedClientE2E::test_send_product_feed_e2e -v

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
from datetime import datetime, date, timedelta
from therange import TheRangeManager, Config
from therange.product_feed import (
    ProductFeedClient, 
    ProductFeedRequest, 
    ProductEntry, 
    PriceEntry, 
    PriceAmendmentRequest,
    PriceAmendmentEntry
)
from therange.auth import AuthClient


class TestProductFeedClientE2E:
    """End-to-end tests for ProductFeedClient with live API."""
    
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
            cls.client = cls.manager.product_feed
    
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
    def test_send_product_feed_e2e(self):
        """Test send_product_feed method with live API call using ProductFeedRequest."""
        try:
            # Authenticate first
            self.auth.authenticate()
            
            # Generate unique test data
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            test_sku = f"E2E_PRODUCT_{timestamp}"
            
            # Create test product data
            price = PriceEntry(
                price=29.99,
                currency="GBP",
                effective_from=date.today()
            )
            
            product = ProductEntry(
                vendor_sku=test_sku,
                title="E2E Test Product",
                brand="E2E Test Brand",
                price_arr=[price],
                product_category="Test Category",
                description="End-to-end test product for SDK validation",
                image_url_arr=["https://example.com/test-image.jpg"],
                fulfilment_class="Small"
            )
            
            request = ProductFeedRequest(product_arr=[product])
            
            # Make the API call
            response = self.client.send_product_feed(request)
            
            # Verify response structure (actual response may vary based on API implementation)
            assert response is not None
            assert isinstance(response, dict)
            
            # Log response for debugging
            print(f"Send product feed response: {response}")
        except requests.exceptions.ConnectionError:
            pytest.skip("Network connectivity issue - cannot reach UAT API")
        except requests.exceptions.Timeout:
            pytest.skip("Network timeout - UAT API is not responding")
    
    @pytest.mark.skipif(
        not (os.getenv("THERANGE_USERNAME") and os.getenv("THERANGE_PASSWORD")),
        reason="E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
    )
    def test_send_product_feed_dict_e2e(self):
        """Test send_product_feed_dict method with live API call using dictionary data."""
        try:
            # Authenticate first
            self.auth.authenticate()
            
            # Generate unique test data
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            test_sku = f"E2E_DICT_PRODUCT_{timestamp}"
            
            # Create test product data as dictionary
            product_data = [{
                "vendor_sku": test_sku,
                "title": "E2E Dict Test Product",
                "brand": "E2E Dict Brand",
                "price_arr": [{
                    "price": 39.99,
                    "currency": "GBP",
                    "effective_from": date.today().isoformat()
                }],
                "product_category": "Test Category",
                "description": "End-to-end test product using dictionary method",
                "image_url_arr": ["https://example.com/dict-test-image.jpg"],
                "fulfilment_class": "Medium"
            }]
            
            # Make the API call
            response = self.client.send_product_feed_dict(product_data)
            
            # Verify response structure
            assert response is not None
            assert isinstance(response, dict)
            
            # Log response for debugging
            print(f"Send product feed dict response: {response}")
        except requests.exceptions.ConnectionError:
            pytest.skip("Network connectivity issue - cannot reach UAT API")
        except requests.exceptions.Timeout:
            pytest.skip("Network timeout - UAT API is not responding")
    
    @pytest.mark.skipif(
        not (os.getenv("THERANGE_USERNAME") and os.getenv("THERANGE_PASSWORD")),
        reason="E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
    )
    def test_submit_products_e2e(self):
        """Test submit_products legacy method with live API call."""
        try:
            # Authenticate first
            self.auth.authenticate()
            
            # Generate unique test data
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            test_sku = f"E2E_LEGACY_{timestamp}"
            
            # Create test product data for legacy method
            product_data = [{
                "vendor_sku": test_sku,
                "title": "E2E Legacy Test Product",
                "brand": "E2E Legacy Brand",
                "description": "Legacy method test product",
                "category": "Test Category"
            }]
            
            # Make the API call
            response = self.client.submit_products(product_data)
            
            # Verify response structure
            assert response is not None
            assert isinstance(response, dict)
            
            # Log response for debugging
            print(f"Submit products legacy response: {response}")
        except requests.exceptions.ConnectionError:
            pytest.skip("Network connectivity issue - cannot reach UAT API")
        except requests.exceptions.Timeout:
            pytest.skip("Network timeout - UAT API is not responding")
    
    @pytest.mark.skipif(
        not (os.getenv("THERANGE_USERNAME") and os.getenv("THERANGE_PASSWORD")),
        reason="E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
    )
    def test_send_price_amendment_e2e(self):
        """Test send_price_amendment method with live API call."""
        try:
            # Authenticate first
            self.auth.authenticate()
            
            # Generate unique test data
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            test_sku = f"E2E_PRICE_{timestamp}"
            
            # Create test price amendment data
            price = PriceEntry(
                price=49.99,
                currency="GBP", 
                effective_from=date.today() + timedelta(days=1)
            )
            
            price_amendment = PriceAmendmentEntry(
                vendor_sku=test_sku,
                price_arr=[price]
            )
            
            request = PriceAmendmentRequest(product_arr=[price_amendment])
            
            # Make the API call
            response = self.client.send_price_amendment(request)
            
            # Verify response structure
            assert response is not None
            assert isinstance(response, dict)
            
            # Log response for debugging
            print(f"Send price amendment response: {response}")
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
        client = ProductFeedClient(auth)
        
        # Create test product data
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        test_sku = f"E2E_UNAUTH_{timestamp}"
        
        price = PriceEntry(
            price=19.99,
            currency="GBP",
            effective_from=date.today()
        )
        
        product = ProductEntry(
            vendor_sku=test_sku,
            title="Unauthorized Test",
            brand="Test Brand",
            price_arr=[price],
            product_category="Test",
            description="Test product",
            image_url_arr=["https://example.com/test.jpg"],
            fulfilment_class="Small"
        )
        
        request = ProductFeedRequest(product_arr=[product])
        
        # Attempt API call without authentication
        with pytest.raises(ValueError, match="Must be authenticated before making this call"):
            client.send_product_feed(request)


class TestProductFeedE2EIntegration:
    """Integration scenarios for e2e product feed testing."""
    
    @pytest.mark.skipif(
        not (os.getenv("THERANGE_USERNAME") and os.getenv("THERANGE_PASSWORD")),
        reason="E2E tests require THERANGE_USERNAME and THERANGE_PASSWORD environment variables"
    )
    def test_full_product_lifecycle_e2e(self):
        """Test complete product lifecycle: create product then update price."""
        try:
            username = os.getenv("THERANGE_USERNAME")
            password = os.getenv("THERANGE_PASSWORD")
            
            # Set up manager and authenticate
            config = Config.uat()
            manager = TheRangeManager(username, password, config)
            manager.authenticate()
            
            # Generate unique test data
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            test_sku = f"E2E_LIFECYCLE_{timestamp}"
            
            # First, create a product
            price = PriceEntry(
                price=25.99,
                currency="GBP",
                effective_from=date.today()
            )
            
            product = ProductEntry(
                vendor_sku=test_sku,
                title="E2E Lifecycle Product",
                brand="Lifecycle Brand",
                price_arr=[price],
                product_category="Lifecycle Category",
                description="Product for testing complete lifecycle",
                image_url_arr=["https://example.com/lifecycle.jpg"],
                fulfilment_class="Large"
            )
            
            request = ProductFeedRequest(product_arr=[product])
            
            # Create the product
            create_response = manager.product_feed.send_product_feed(request)
            assert create_response is not None
            print(f"Create product response: {create_response}")
            
            # Then, update the price
            updated_price = PriceEntry(
                price=35.99,
                currency="GBP",
                effective_from=date.today() + timedelta(days=1)
            )
            
            price_amendment = PriceAmendmentEntry(
                vendor_sku=test_sku,
                price_arr=[updated_price]
            )
            
            price_request = PriceAmendmentRequest(product_arr=[price_amendment])
            
            # Update the price
            update_response = manager.product_feed.send_price_amendment(price_request)
            assert update_response is not None
            print(f"Update price response: {update_response}")
        except requests.exceptions.ConnectionError:
            pytest.skip("Network connectivity issue - cannot reach UAT API")
        except requests.exceptions.Timeout:
            pytest.skip("Network timeout - UAT API is not responding")