from typing import List
from pydantic import BaseModel, Field, ValidationError
from .base_client import BaseClient


class StockItem(BaseModel):
    """Model for individual stock availability item."""
    code: str = Field(..., description="Product code used to identify a product")
    qty: int = Field(..., ge=0, description="Quantity of stock on hand, including awaiting despatch")


class StockAvailabilityClient(BaseClient):
    def update_stock(self, stock_data: List[dict]):
        """Update stock availability for products.
        
        Args:
            stock_data: List of dictionaries, each containing 'code' (str) and 'qty' (int >= 0)
            
        Raises:
            ValueError: If authentication state is invalid or stock_data validation fails
        """
        # Validate authentication state
        if not self.auth.session:
            raise ValueError("Must be authenticated before making this call")
        if not self.auth.supplier_id:
            raise ValueError("Must be authenticated before making this call")
        
        # Validate stock_data is a non-empty list
        if not isinstance(stock_data, list):
            raise ValueError("stock_data must be a list")
        if not stock_data:
            raise ValueError("stock_data must be a non-empty list")
        
        # Validate each stock entry using Pydantic
        try:
            validated_items = [StockItem(**item) for item in stock_data]
        except ValidationError as e:
            raise ValueError(f"Invalid stock data: {e}")
        
        # Convert back to list of dicts for API call
        validated_data = [item.model_dump() for item in validated_items]
        
        return self._post("stock_availability.api", validated_data, include_mode=False)
