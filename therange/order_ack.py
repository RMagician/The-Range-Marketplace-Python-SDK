from pydantic import BaseModel, Field, validator
from typing import List
from .base_client import BaseClient


class OrderAckRequest(BaseModel):
    """Pydantic model for order acknowledgment request validation."""
    order_arr: List[str] = Field(..., description="List of order numbers to acknowledge")
    
    @validator('order_arr')
    def validate_order_arr(cls, v):
        """Validate that order_arr is a non-empty list of strings."""
        if not isinstance(v, list):
            raise ValueError("order_arr must be a list")
        if not v:
            raise ValueError("order_arr must be a non-empty list")
        for order_id in v:
            if not isinstance(order_id, str):
                raise ValueError("All order IDs must be strings")
            if not order_id.strip():
                raise ValueError("Order IDs cannot be empty strings")
        return v


class OrderAckClient(BaseClient):
    def acknowledge_orders(self, order_numbers: List[str]):
        """Acknowledge orders received via order_feed.api with type='new'.
        
        Args:
            order_numbers: List of order numbers (strings) to acknowledge
            
        Returns:
            API response containing acknowledged order_arr
            
        Raises:
            ValueError: If authentication state is invalid or order_numbers is invalid
            PermissionError: If not authenticated (401)
        """
        # Create and validate request using Pydantic model first
        try:
            request = OrderAckRequest(order_arr=order_numbers)
        except Exception as e:
            raise ValueError(f"Invalid order_numbers: {e}")
        
        # Validate authentication state
        if not self.auth.session:
            raise ValueError("Must be authenticated before making this call")
        if not self.auth.supplier_id:
            raise ValueError("Must be authenticated before making this call")
        
        # Convert to dict for API call
        payload = request.model_dump()
        
        return self._post("order_ack.api", payload)
