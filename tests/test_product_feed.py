"""
Unit tests for the ProductFeed module.

Tests product feed functionality including Pydantic model validation,
client methods, authentication checks, and various error scenarios.
"""

import pytest
from datetime import date
from unittest.mock import Mock, patch
from pydantic import ValidationError

from therange.product_feed import (
    PriceEntry,
    ProductAttribute,
    ProductEntry,
    ProductFeedRequest,
    PriceAmendmentEntry,
    PriceAmendmentRequest,
    ProductFeedClient
)
from therange.auth import AuthClient


class TestPydanticModels:
    """Test Pydantic model validation for product feed data structures."""
    
    def test_price_entry_valid(self):
        """Test valid PriceEntry creation."""
        price = PriceEntry(
            price=29.99,
            currency="GBP",
            effective_from=date(2025, 1, 1)
        )
        
        assert price.price == 29.99
        assert price.currency == "GBP"
        assert price.effective_from == date(2025, 1, 1)
    
    def test_price_entry_default_currency(self):
        """Test PriceEntry with default currency."""
        price = PriceEntry(
            price=19.95,
            effective_from=date(2025, 6, 15)
        )
        
        assert price.currency == "GBP"  # Default value
    
    def test_price_entry_invalid_price(self):
        """Test PriceEntry with invalid price type."""
        with pytest.raises(ValidationError):
            PriceEntry(
                price="invalid",
                effective_from=date(2025, 1, 1)
            )
    
    def test_product_attribute_valid(self):
        """Test valid ProductAttribute creation."""
        attr = ProductAttribute(
            colour="Blue",
            colour_name="Ocean Blue",
            length="25cm",
            width="15cm",
            weight="500g"
        )
        
        assert attr.colour == "Blue"
        assert attr.colour_name == "Ocean Blue"
        assert attr.length == "25cm"
        assert attr.width == "15cm"
        assert attr.weight == "500g"
    
    def test_product_attribute_empty(self):
        """Test ProductAttribute with all optional fields."""
        attr = ProductAttribute()
        
        assert attr.colour is None
        assert attr.colour_name is None
        assert attr.other_attribute == {}
    
    def test_product_entry_valid_minimal(self):
        """Test ProductEntry with minimal required fields."""
        price = PriceEntry(price=29.99, effective_from=date(2025, 1, 1))
        
        product = ProductEntry(
            vendor_sku="TEST123",
            title="Test Product",
            brand="Test Brand",
            price_arr=[price],
            product_category="Electronics",
            description="A test product",
            image_url_arr=["https://example.com/image.jpg"],
            fulfilment_class="Small"
        )
        
        assert product.vendor_sku == "TEST123"
        assert product.title == "Test Product"
        assert product.brand == "Test Brand"
        assert len(product.price_arr) == 1
        assert product.feature_arr == []  # Default empty list
        assert product.youtube_url_arr == []  # Default empty list
    
    def test_product_entry_valid_complete(self):
        """Test ProductEntry with all fields populated."""
        price = PriceEntry(price=89.99, effective_from=date(2025, 1, 1))
        attr = ProductAttribute(colour="Red", weight="1kg")
        
        product = ProductEntry(
            vendor_sku="COMPLETE123",
            related_product="RELATED456",
            title="Complete Test Product",
            brand="Premium Brand",
            gtin="1234567890123",
            price_arr=[price],
            product_category="Home & Garden",
            description="A complete test product with all features",
            feature_arr=["Feature 1", "Feature 2", "Waterproof"],
            child_hazard=0,
            age_restriction="3+",
            image_url_arr=["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
            youtube_url_arr=["https://youtube.com/watch?v=test"],
            fulfilment_class="Medium",
            product_attribute=attr,
            launch_date=date(2025, 2, 1),
            active=1,
            visible=1
        )
        
        assert product.related_product == "RELATED456"
        assert product.gtin == "1234567890123"
        assert len(product.feature_arr) == 3
        assert product.child_hazard == 0
        assert product.age_restriction == "3+"
        assert len(product.image_url_arr) == 2
        assert len(product.youtube_url_arr) == 1
        assert product.product_attribute.colour == "Red"
        assert product.launch_date == date(2025, 2, 1)
        assert product.active == 1
        assert product.visible == 1
    
    def test_product_entry_title_too_long(self):
        """Test ProductEntry with title exceeding 80 characters."""
        price = PriceEntry(price=29.99, effective_from=date(2025, 1, 1))
        
        with pytest.raises(ValidationError):
            ProductEntry(
                vendor_sku="TEST123",
                title="A" * 81,  # 81 characters, exceeds max_length=80
                brand="Test Brand",
                price_arr=[price],
                product_category="Electronics",
                description="A test product",
                image_url_arr=["https://example.com/image.jpg"],
                fulfilment_class="Small"
            )
    
    def test_product_entry_invalid_url(self):
        """Test ProductEntry with invalid image URL."""
        price = PriceEntry(price=29.99, effective_from=date(2025, 1, 1))
        
        with pytest.raises(ValidationError):
            ProductEntry(
                vendor_sku="TEST123",
                title="Test Product",
                brand="Test Brand",
                price_arr=[price],
                product_category="Electronics",
                description="A test product",
                image_url_arr=["not-a-valid-url"],
                fulfilment_class="Small"
            )
    
    def test_product_entry_missing_required_fields(self):
        """Test ProductEntry missing required fields."""
        with pytest.raises(ValidationError):
            ProductEntry(
                vendor_sku="TEST123"
                # Missing all other required fields
            )
    
    def test_product_feed_request_valid(self):
        """Test valid ProductFeedRequest creation."""
        price = PriceEntry(price=29.99, effective_from=date(2025, 1, 1))
        product = ProductEntry(
            vendor_sku="TEST123",
            title="Test Product",
            brand="Test Brand",
            price_arr=[price],
            product_category="Electronics",
            description="A test product",
            image_url_arr=["https://example.com/image.jpg"],
            fulfilment_class="Small"
        )
        
        request = ProductFeedRequest(product_arr=[product])
        
        assert len(request.product_arr) == 1
        assert request.product_arr[0].vendor_sku == "TEST123"
    
    def test_product_feed_request_empty_list(self):
        """Test ProductFeedRequest with empty product list."""
        request = ProductFeedRequest(product_arr=[])
        assert len(request.product_arr) == 0
    
    def test_price_amendment_entry_valid(self):
        """Test valid PriceAmendmentEntry creation."""
        price = PriceEntry(price=39.99, effective_from=date(2025, 2, 1))
        
        amendment = PriceAmendmentEntry(
            vendor_sku="AMEND123",
            price_arr=[price]
        )
        
        assert amendment.vendor_sku == "AMEND123"
        assert len(amendment.price_arr) == 1
        assert amendment.price_arr[0].price == 39.99
    
    def test_price_amendment_request_valid(self):
        """Test valid PriceAmendmentRequest creation."""
        price = PriceEntry(price=49.99, effective_from=date(2025, 3, 1))
        amendment = PriceAmendmentEntry(vendor_sku="AMEND123", price_arr=[price])
        
        request = PriceAmendmentRequest(product_arr=[amendment])
        
        assert len(request.product_arr) == 1
        assert request.product_arr[0].vendor_sku == "AMEND123"


class TestProductFeedClient:
    """Test ProductFeedClient functionality including authentication and API calls."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create mock auth client
        self.auth = Mock(spec=AuthClient)
        self.auth.session = Mock()
        self.auth.supplier_id = "12345"
        self.auth.mode = "test_mode"
        self.auth.base_url = "https://test.api.com/"
        
        # Create client
        self.client = ProductFeedClient(self.auth)
    
    def test_submit_products_valid(self):
        """Test submit_products with valid data."""
        # Setup mock response
        mock_response = {"status": "success", "message": "Products submitted"}
        self.client._post = Mock(return_value=mock_response)
        
        product_data = [{
            "vendor_sku": "TEST123",
            "title": "Test Product",
            "brand": "Test Brand",
            "description": "Test description"
        }]
        
        result = self.client.submit_products(product_data)
        
        assert result == mock_response
        self.client._post.assert_called_once_with(
            "product_feed.api", 
            {"product_arr": product_data}, 
            include_mode=False
        )
    
    def test_submit_products_not_list(self):
        """Test submit_products with non-list input."""
        with pytest.raises(ValueError, match="product_arr must be a list"):
            self.client.submit_products("not a list")
    
    def test_submit_products_title_too_long(self):
        """Test submit_products with title exceeding 80 characters."""
        product_data = [{
            "vendor_sku": "TEST123",
            "title": "A" * 81,  # 81 characters
            "brand": "Test Brand"
        }]
        
        with pytest.raises(ValueError, match="Product title exceeds 80 characters"):
            self.client.submit_products(product_data)
    
    def test_submit_products_no_title_validation(self):
        """Test submit_products with missing title (should not validate)."""
        # Setup mock response
        mock_response = {"status": "success"}
        self.client._post = Mock(return_value=mock_response)
        
        product_data = [{
            "vendor_sku": "TEST123",
            "brand": "Test Brand"
            # No title field
        }]
        
        result = self.client.submit_products(product_data)
        assert result == mock_response
    
    def test_send_product_feed_valid(self):
        """Test send_product_feed with valid ProductFeedRequest."""
        # Setup mock response
        mock_response = {"status": "success", "feed_id": "12345"}
        self.client._post = Mock(return_value=mock_response)
        
        # Create valid request
        price = PriceEntry(price=29.99, effective_from=date(2025, 1, 1))
        product = ProductEntry(
            vendor_sku="TEST123",
            title="Test Product",
            brand="Test Brand",
            price_arr=[price],
            product_category="Electronics",
            description="A test product",
            image_url_arr=["https://example.com/image.jpg"],
            fulfilment_class="Small"
        )
        request = ProductFeedRequest(product_arr=[product])
        
        result = self.client.send_product_feed(request)
        
        assert result == mock_response
        self.client._post.assert_called_once_with(
            "product_feed.api",
            request.model_dump(),
            include_mode=False
        )
    
    def test_send_product_feed_no_session(self):
        """Test send_product_feed without authenticated session."""
        self.auth.session = None
        
        price = PriceEntry(price=29.99, effective_from=date(2025, 1, 1))
        product = ProductEntry(
            vendor_sku="TEST123",
            title="Test Product",
            brand="Test Brand",
            price_arr=[price],
            product_category="Electronics",
            description="A test product",
            image_url_arr=["https://example.com/image.jpg"],
            fulfilment_class="Small"
        )
        request = ProductFeedRequest(product_arr=[product])
        
        with pytest.raises(ValueError, match="Must be authenticated before making this call"):
            self.client.send_product_feed(request)
    
    def test_send_product_feed_no_supplier_id(self):
        """Test send_product_feed without supplier_id."""
        self.auth.supplier_id = None
        
        price = PriceEntry(price=29.99, effective_from=date(2025, 1, 1))
        product = ProductEntry(
            vendor_sku="TEST123",
            title="Test Product",
            brand="Test Brand",
            price_arr=[price],
            product_category="Electronics",
            description="A test product",
            image_url_arr=["https://example.com/image.jpg"],
            fulfilment_class="Small"
        )
        request = ProductFeedRequest(product_arr=[product])
        
        with pytest.raises(ValueError, match="Must be authenticated before making this call"):
            self.client.send_product_feed(request)
    
    def test_send_product_feed_dict_valid(self):
        """Test send_product_feed_dict with valid dictionary data."""
        # Setup mock for send_product_feed method
        mock_response = {"status": "success"}
        self.client.send_product_feed = Mock(return_value=mock_response)
        
        product_data = [{
            "vendor_sku": "TEST123",
            "title": "Test Product",
            "brand": "Test Brand",
            "price_arr": [{
                "price": 29.99,
                "currency": "GBP",
                "effective_from": "2025-01-01"
            }],
            "product_category": "Electronics",
            "description": "A test product",
            "image_url_arr": ["https://example.com/image.jpg"],
            "fulfilment_class": "Small"
        }]
        
        result = self.client.send_product_feed_dict(product_data)
        
        assert result == mock_response
        # Verify send_product_feed was called with validated request
        assert self.client.send_product_feed.call_count == 1
        call_args = self.client.send_product_feed.call_args[0][0]
        assert isinstance(call_args, ProductFeedRequest)
        assert len(call_args.product_arr) == 1
    
    def test_send_product_feed_dict_not_list(self):
        """Test send_product_feed_dict with non-list input."""
        with pytest.raises(ValueError, match="product_data must be a list"):
            self.client.send_product_feed_dict("not a list")
    
    def test_send_product_feed_dict_empty_list(self):
        """Test send_product_feed_dict with empty list."""
        with pytest.raises(ValueError, match="product_data must be a non-empty list"):
            self.client.send_product_feed_dict([])
    
    def test_send_product_feed_dict_invalid_data(self):
        """Test send_product_feed_dict with invalid product data."""
        product_data = [{
            "vendor_sku": "TEST123",
            # Missing required fields
        }]
        
        with pytest.raises(ValueError, match="Invalid product data"):
            self.client.send_product_feed_dict(product_data)
    
    def test_send_product_feed_dict_no_session(self):
        """Test send_product_feed_dict without authenticated session."""
        self.auth.session = None
        
        product_data = [{"test": "data"}]
        
        with pytest.raises(ValueError, match="Must be authenticated before making this call"):
            self.client.send_product_feed_dict(product_data)
    
    def test_send_price_amendment_valid(self):
        """Test send_price_amendment with valid PriceAmendmentRequest."""
        # Setup mock response
        mock_response = {"status": "success", "amendment_id": "67890"}
        self.client._post = Mock(return_value=mock_response)
        
        # Create valid request
        price = PriceEntry(price=39.99, effective_from=date(2025, 2, 1))
        amendment = PriceAmendmentEntry(vendor_sku="AMEND123", price_arr=[price])
        request = PriceAmendmentRequest(product_arr=[amendment])
        
        result = self.client.send_price_amendment(request)
        
        assert result == mock_response
        self.client._post.assert_called_once_with(
            "product_feed.api",
            request.model_dump(),
            include_mode=False
        )
    
    def test_send_price_amendment_no_session(self):
        """Test send_price_amendment without authenticated session."""
        self.auth.session = None
        
        price = PriceEntry(price=39.99, effective_from=date(2025, 2, 1))
        amendment = PriceAmendmentEntry(vendor_sku="AMEND123", price_arr=[price])
        request = PriceAmendmentRequest(product_arr=[amendment])
        
        with pytest.raises(ValueError, match="Must be authenticated before making this call"):
            self.client.send_price_amendment(request)
    
    def test_send_price_amendment_no_supplier_id(self):
        """Test send_price_amendment without supplier_id."""
        self.auth.supplier_id = None
        
        price = PriceEntry(price=39.99, effective_from=date(2025, 2, 1))
        amendment = PriceAmendmentEntry(vendor_sku="AMEND123", price_arr=[price])
        request = PriceAmendmentRequest(product_arr=[amendment])
        
        with pytest.raises(ValueError, match="Must be authenticated before making this call"):
            self.client.send_price_amendment(request)
    
    def test_send_price_amendment_dict_valid(self):
        """Test send_price_amendment_dict with valid dictionary data."""
        # Setup mock for send_price_amendment method
        mock_response = {"status": "success"}
        self.client.send_price_amendment = Mock(return_value=mock_response)
        
        price_data = [{
            "vendor_sku": "AMEND123",
            "price_arr": [{
                "price": 39.99,
                "currency": "GBP",
                "effective_from": "2025-02-01"
            }]
        }]
        
        result = self.client.send_price_amendment_dict(price_data)
        
        assert result == mock_response
        # Verify send_price_amendment was called with validated request
        assert self.client.send_price_amendment.call_count == 1
        call_args = self.client.send_price_amendment.call_args[0][0]
        assert isinstance(call_args, PriceAmendmentRequest)
        assert len(call_args.product_arr) == 1
    
    def test_send_price_amendment_dict_not_list(self):
        """Test send_price_amendment_dict with non-list input."""
        with pytest.raises(ValueError, match="price_data must be a list"):
            self.client.send_price_amendment_dict("not a list")
    
    def test_send_price_amendment_dict_empty_list(self):
        """Test send_price_amendment_dict with empty list."""
        with pytest.raises(ValueError, match="price_data must be a non-empty list"):
            self.client.send_price_amendment_dict([])
    
    def test_send_price_amendment_dict_invalid_data(self):
        """Test send_price_amendment_dict with invalid price data."""
        price_data = [{
            "vendor_sku": "AMEND123",
            # Missing price_arr
        }]
        
        with pytest.raises(ValueError, match="Invalid price data"):
            self.client.send_price_amendment_dict(price_data)
    
    def test_send_price_amendment_dict_no_session(self):
        """Test send_price_amendment_dict without authenticated session."""
        self.auth.session = None
        
        price_data = [{"test": "data"}]
        
        with pytest.raises(ValueError, match="Must be authenticated before making this call"):
            self.client.send_price_amendment_dict(price_data)


class TestProductFeedEdgeCases:
    """Test edge cases and integration scenarios for product feed."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.auth = Mock(spec=AuthClient)
        self.auth.session = Mock()
        self.auth.supplier_id = "12345"
        self.auth.mode = "test_mode"
        self.auth.base_url = "https://test.api.com/"
        self.client = ProductFeedClient(self.auth)
    
    def test_product_entry_with_multiple_prices(self):
        """Test ProductEntry with multiple price entries."""
        price1 = PriceEntry(price=29.99, effective_from=date(2025, 1, 1))
        price2 = PriceEntry(price=24.99, effective_from=date(2025, 2, 1))
        
        product = ProductEntry(
            vendor_sku="MULTI123",
            title="Multi-Price Product",
            brand="Test Brand",
            price_arr=[price1, price2],
            product_category="Electronics",
            description="Product with multiple pricing",
            image_url_arr=["https://example.com/image.jpg"],
            fulfilment_class="Small"
        )
        
        assert len(product.price_arr) == 2
        assert product.price_arr[0].price == 29.99
        assert product.price_arr[1].price == 24.99
    
    def test_product_feed_request_multiple_products(self):
        """Test ProductFeedRequest with multiple products."""
        price = PriceEntry(price=29.99, effective_from=date(2025, 1, 1))
        
        product1 = ProductEntry(
            vendor_sku="PROD1",
            title="Product 1",
            brand="Brand 1",
            price_arr=[price],
            product_category="Electronics",
            description="First product",
            image_url_arr=["https://example.com/image1.jpg"],
            fulfilment_class="Small"
        )
        
        product2 = ProductEntry(
            vendor_sku="PROD2",
            title="Product 2",
            brand="Brand 2",
            price_arr=[price],
            product_category="Home",
            description="Second product",
            image_url_arr=["https://example.com/image2.jpg"],
            fulfilment_class="Medium"
        )
        
        request = ProductFeedRequest(product_arr=[product1, product2])
        
        assert len(request.product_arr) == 2
        assert request.product_arr[0].vendor_sku == "PROD1"
        assert request.product_arr[1].vendor_sku == "PROD2"
    
    def test_submit_products_empty_list(self):
        """Test submit_products with empty list."""
        mock_response = {"status": "success"}
        self.client._post = Mock(return_value=mock_response)
        
        result = self.client.submit_products([])
        
        assert result == mock_response
        self.client._post.assert_called_once_with(
            "product_feed.api",
            {"product_arr": []},
            include_mode=False
        )
    
    def test_product_entry_maximum_title_length(self):
        """Test ProductEntry with exactly 80 character title (boundary case)."""
        price = PriceEntry(price=29.99, effective_from=date(2025, 1, 1))
        
        # Exactly 80 characters
        title_80_chars = "A" * 80
        
        product = ProductEntry(
            vendor_sku="BOUNDARY123",
            title=title_80_chars,
            brand="Test Brand",
            price_arr=[price],
            product_category="Electronics",
            description="Boundary test product",
            image_url_arr=["https://example.com/image.jpg"],
            fulfilment_class="Small"
        )
        
        assert len(product.title) == 80
        assert product.title == title_80_chars
    
    def test_submit_products_with_none_title(self):
        """Test submit_products with None title (should not trigger validation)."""
        mock_response = {"status": "success"}
        self.client._post = Mock(return_value=mock_response)
        
        product_data = [{
            "vendor_sku": "NONE123",
            "title": None,  # None title should not trigger length validation
            "brand": "Test Brand"
        }]
        
        result = self.client.submit_products(product_data)
        assert result == mock_response