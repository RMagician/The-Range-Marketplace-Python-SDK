from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from .base_client import BaseClient


class OrderItem(BaseModel):
    """Model for individual order item."""
    code: str = Field(..., description="Product code")
    qty: int = Field(..., ge=1, description="Quantity must be at least 1")


class DispatchOrderRequest(BaseModel):
    """Pydantic model for dispatch order request validation."""
    order_number: str = Field(..., description="Order number to dispatch")
    delivery_service: str = Field(..., description="Delivery service name")
    courier_name: str = Field(..., description="Courier company name")
    despatch_date: str = Field(..., description="Dispatch date in YYYY-MM-DD HH:MM:SS format")
    tracking_reference: str = Field(..., description="Tracking reference number")
    earliest_delivery: Optional[str] = Field(None, description="Earliest delivery date in YYYY-MM-DD format")
    latest_delivery: Optional[str] = Field(None, description="Latest delivery date in YYYY-MM-DD format")
    item_arr: List[OrderItem] = Field(..., description="List of items to dispatch")
    
    @validator('despatch_date')
    def validate_despatch_date(cls, v):
        """Validate dispatch date format."""
        try:
            datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValueError("despatch_date must be in format 'YYYY-MM-DD HH:MM:SS'")
        return v
    
    @validator('earliest_delivery', 'latest_delivery')
    def validate_delivery_dates(cls, v):
        """Validate delivery date format."""
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                raise ValueError("Delivery dates must be in format 'YYYY-MM-DD'")
        return v
    
    @validator('item_arr')
    def validate_item_arr(cls, v):
        """Validate that item_arr is non-empty."""
        if not v:
            raise ValueError("item_arr must be a non-empty list")
        return v


class CancelOrderRequest(BaseModel):
    """Pydantic model for cancel order request validation."""
    order_number: str = Field(..., description="Order number to cancel")
    cancel_code: str = Field(..., description="Reason code for cancellation")
    cancel_reason: str = Field(default="", description="Optional free-text reason")
    item_arr: List[OrderItem] = Field(..., description="List of items to cancel")
    
    @validator('cancel_code')
    def validate_cancel_code(cls, v):
        """Validate that cancel_code is one of the allowed values."""
        allowed_codes = [
            "Stock not available",
            "Unable to contact customer to arrange delivery",
            "Unable to deliver to address"
        ]
        if v not in allowed_codes:
            raise ValueError(f"cancel_code must be one of {allowed_codes}, got '{v}'")
        return v
    
    @validator('item_arr')
    def validate_item_arr(cls, v):
        """Validate that item_arr is non-empty."""
        if not v:
            raise ValueError("item_arr must be a non-empty list")
        return v


class OrderEventClient(BaseClient):
    def send_event(self, event_payload):
        """Legacy method for sending order events with basic validation.
        
        Args:
            event_payload: Dictionary containing event data
            
        Returns:
            API response
        """
        return self._post("order_event.api", event_payload)
    
    def dispatch_order(self, order_number: str, items: list, despatch_date: str, 
                      delivery_service: str, courier_name: str, tracking_reference: str,
                      earliest_delivery: str = None, latest_delivery: str = None):
        """Dispatch order items by sending a dispatch event.
        
        Args:
            order_number: Order number to dispatch
            items: List of dicts with 'code' (str) and 'qty' (int)
            despatch_date: Dispatch date in "YYYY-MM-DD HH:MM:SS" format
            delivery_service: Delivery service name
            courier_name: Courier company name
            tracking_reference: Tracking reference number
            earliest_delivery: Optional earliest delivery date in "YYYY-MM-DD" format
            latest_delivery: Optional latest delivery date in "YYYY-MM-DD" format
            
        Returns:
            API response
            
        Raises:
            ValueError: If authentication state is invalid or parameters are invalid
            PermissionError: If not authenticated (401)
        """
        # Validate authentication state
        if not self.auth.session:
            raise ValueError("Must be authenticated before making this call")
        if not self.auth.supplier_id:
            raise ValueError("Must be authenticated before making this call")
        
        # Validate input parameters
        if not isinstance(order_number, str) or not order_number.strip():
            raise ValueError("order_number must be a non-empty string")
        
        if not isinstance(items, list) or not items:
            raise ValueError("items must be a non-empty list")
        
        # Convert items to OrderItem objects for validation
        try:
            validated_items = [OrderItem(**item) for item in items]
        except Exception as e:
            raise ValueError(f"Invalid items: {e}")
        
        # Create and validate request using Pydantic model
        try:
            request = DispatchOrderRequest(
                order_number=order_number,
                delivery_service=delivery_service,
                courier_name=courier_name,
                despatch_date=despatch_date,
                tracking_reference=tracking_reference,
                earliest_delivery=earliest_delivery,
                latest_delivery=latest_delivery,
                item_arr=validated_items
            )
        except Exception as e:
            raise ValueError(f"Invalid dispatch parameters: {e}")
        
        # Convert to dict for API call
        payload = request.model_dump()
        
        return self._post("order_event.api", payload)
    
    def cancel_order(self, order_number: str, items: list, cancel_code: str, cancel_reason: str = ""):
        """Cancel order items by sending a cancellation event.
        
        Args:
            order_number: Order number to cancel
            items: List of dicts with 'code' (str) and 'qty' (int)  
            cancel_code: Must be one of the allowed cancellation codes
            cancel_reason: Optional free-text reason
            
        Returns:
            API response
            
        Raises:
            ValueError: If authentication state is invalid or parameters are invalid
            PermissionError: If not authenticated (401)
        """
        # Validate authentication state
        if not self.auth.session:
            raise ValueError("Must be authenticated before making this call")
        if not self.auth.supplier_id:
            raise ValueError("Must be authenticated before making this call")
        
        # Validate input parameters
        if not isinstance(order_number, str) or not order_number.strip():
            raise ValueError("order_number must be a non-empty string")
        
        if not isinstance(items, list) or not items:
            raise ValueError("items must be a non-empty list")
        
        # Convert items to OrderItem objects for validation
        try:
            validated_items = [OrderItem(**item) for item in items]
        except Exception as e:
            raise ValueError(f"Invalid items: {e}")
        
        # Create and validate request using Pydantic model
        try:
            request = CancelOrderRequest(
                order_number=order_number,
                cancel_code=cancel_code,
                cancel_reason=cancel_reason,
                item_arr=validated_items
            )
        except Exception as e:
            raise ValueError(f"Invalid cancel parameters: {e}")
        
        # Convert to dict for API call
        payload = request.model_dump()
        
        return self._post("order_event.api", payload)
