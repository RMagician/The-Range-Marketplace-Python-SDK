from pydantic import BaseModel, HttpUrl, Field, ValidationError
from typing import List, Optional, Dict
from datetime import date
from .base_client import BaseClient


class PriceEntry(BaseModel):
    price: float
    currency: str = "GBP"
    effective_from: date


class ProductAttribute(BaseModel):
    colour: Optional[str] = None
    colour_name: Optional[str] = None
    colour_group: Optional[str] = None
    length: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    other_attribute: Optional[Dict[str, str]] = Field(default_factory=dict)


class ProductEntry(BaseModel):
    vendor_sku: str
    related_product: Optional[str] = None
    title: str = Field(..., max_length=80)
    brand: str
    gtin: Optional[str] = None
    price_arr: List[PriceEntry]
    product_category: str
    description: str
    feature_arr: Optional[List[str]] = Field(default_factory=list)
    child_hazard: Optional[int] = None
    age_restriction: Optional[str] = None
    image_url_arr: List[HttpUrl]
    youtube_url_arr: Optional[List[HttpUrl]] = Field(default_factory=list)
    fulfilment_class: str
    product_attribute: Optional[ProductAttribute] = None
    launch_date: Optional[date] = None
    active: Optional[int] = None
    visible: Optional[int] = None


class ProductFeedRequest(BaseModel):
    product_arr: List[ProductEntry]


class PriceAmendmentEntry(BaseModel):
    vendor_sku: str
    price_arr: List[PriceEntry]


class PriceAmendmentRequest(BaseModel):
    product_arr: List[PriceAmendmentEntry]


class ProductFeedClient(BaseClient):
    def submit_products(self, product_arr):
        """Legacy method for submitting products with basic validation.
        
        Args:
            product_arr: List of product dictionaries
            
        Returns:
            API response
            
        Raises:
            ValueError: If validation fails
        """
        if not isinstance(product_arr, list):
            raise ValueError("product_arr must be a list")
        for p in product_arr:
            title = p.get("title")
            if title and len(title) > 80:
                raise ValueError(f"Product title exceeds 80 characters: {title}")

        return self._post("product_feed.api", {"product_arr": product_arr}, include_mode=False)

    def send_product_feed(self, request: ProductFeedRequest):
        """Send product feed using Pydantic validation.
        
        Args:
            request: ProductFeedRequest containing validated product data
            
        Returns:
            API response
            
        Raises:
            ValueError: If authentication state is invalid
        """
        # Validate authentication state
        if not self.auth.session:
            raise ValueError("Must be authenticated before making this call")
        if not self.auth.supplier_id:
            raise ValueError("Must be authenticated before making this call")
        
        # Convert to dict for API call
        payload = request.model_dump()
        
        return self._post("product_feed.api", payload, include_mode=False)

    def send_product_feed_dict(self, product_data: List[dict]):
        """Send product feed from list of dictionaries with Pydantic validation.
        
        Args:
            product_data: List of product dictionaries to validate and send
            
        Returns:
            API response
            
        Raises:
            ValueError: If validation fails or authentication state is invalid
        """
        # Validate authentication state
        if not self.auth.session:
            raise ValueError("Must be authenticated before making this call")
        if not self.auth.supplier_id:
            raise ValueError("Must be authenticated before making this call")
        
        # Validate data is a non-empty list
        if not isinstance(product_data, list):
            raise ValueError("product_data must be a list")
        if not product_data:
            raise ValueError("product_data must be a non-empty list")
        
        # Validate using Pydantic
        try:
            request = ProductFeedRequest(product_arr=product_data)
        except ValidationError as e:
            raise ValueError(f"Invalid product data: {e}")
        
        return self.send_product_feed(request)

    def send_price_amendment(self, request: PriceAmendmentRequest):
        """Send price-only amendment request.
        
        Args:
            request: PriceAmendmentRequest containing price update data
            
        Returns:
            API response
            
        Raises:
            ValueError: If authentication state is invalid
        """
        # Validate authentication state
        if not self.auth.session:
            raise ValueError("Must be authenticated before making this call")
        if not self.auth.supplier_id:
            raise ValueError("Must be authenticated before making this call")
        
        # Convert to dict for API call
        payload = request.model_dump()
        
        return self._post("product_feed.api", payload, include_mode=False)

    def send_price_amendment_dict(self, price_data: List[dict]):
        """Send price-only amendment from list of dictionaries with Pydantic validation.
        
        Args:
            price_data: List of price amendment dictionaries
            
        Returns:
            API response
            
        Raises:
            ValueError: If validation fails or authentication state is invalid
        """
        # Validate authentication state
        if not self.auth.session:
            raise ValueError("Must be authenticated before making this call")
        if not self.auth.supplier_id:
            raise ValueError("Must be authenticated before making this call")
        
        # Validate data is a non-empty list
        if not isinstance(price_data, list):
            raise ValueError("price_data must be a list")
        if not price_data:
            raise ValueError("price_data must be a non-empty list")
        
        # Validate using Pydantic
        try:
            request = PriceAmendmentRequest(product_arr=price_data)
        except ValidationError as e:
            raise ValueError(f"Invalid price data: {e}")
        
        return self.send_price_amendment(request)
