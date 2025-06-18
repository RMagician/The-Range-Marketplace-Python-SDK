from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from .base_client import BaseClient


class OrderItem(BaseModel):
    """Model for individual order line items."""
    code: str = Field(..., description="Product code")
    qty: int = Field(..., ge=1, description="Quantity, must be >= 1")


class DispatchOrderRequest(BaseModel):
    """Pydantic model for dispatch order request validation."""
    order_number: str = Field(..., description="Order number to dispatch")
    items: List[OrderItem] = Field(..., description="List of items to dispatch")
    despatch_date: str = Field(..., description="Dispatch date in format YYYY-MM-DD HH:MM:SS")
    delivery_service: str = Field(..., description="Delivery service name")
    courier_name: str = Field(..., description="Courier name")
    tracking_reference: str = Field(..., description="Tracking reference")
    earliest_delivery: Optional[str] = Field(None, description="Earliest delivery date in format YYYY-MM-DD")
    latest_delivery: Optional[str] = Field(None, description="Latest delivery date in format YYYY-MM-DD")
    
    @validator('items')
    def validate_items(cls, v):
        """Validate that items is a non-empty list."""
        if not v:
            raise ValueError("items must be a non-empty list")
        return v
    
    @validator('despatch_date')
    def validate_despatch_date(cls, v):
        """Validate despatch_date format."""
        try:
            datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValueError("despatch_date must be in format YYYY-MM-DD HH:MM:SS")
        return v
    
    @validator('earliest_delivery', 'latest_delivery')
    def validate_delivery_dates(cls, v):
        """Validate delivery date format."""
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                raise ValueError("delivery dates must be in format YYYY-MM-DD")
        return v


class CancelOrderRequest(BaseModel):
    """Pydantic model for cancel order request validation."""
    order_number: str = Field(..., description="Order number to cancel")
    items: List[OrderItem] = Field(..., description="List of items to cancel")
    cancel_code: str = Field(..., description="Cancellation code")
    cancel_reason: str = Field("", description="Optional cancellation reason")
    
    @validator('items')
    def validate_items(cls, v):
        """Validate that items is a non-empty list."""
        if not v:
            raise ValueError("items must be a non-empty list")
        return v
    
    @validator('cancel_code')
    def validate_cancel_code(cls, v):
        """Validate cancel_code is one of the allowed values."""
        allowed_codes = [
            "Stock not available",
            "Unable to contact customer to arrange delivery",
            "Unable to deliver to address"
        ]
        if v not in allowed_codes:
            raise ValueError(f"cancel_code must be one of {allowed_codes}")
        return v


class OrderEventClient(BaseClient):
    def send_event(self, event_payload):
        return self._post("order_event.api", event_payload)
    
    def dispatch_order(self, order_number: str, items: list, despatch_date: str, delivery_service: str,
                       courier_name: str, tracking_reference: str, earliest_delivery: str = None,
                       latest_delivery: str = None):
        """Dispatch an order by sending a dispatch event.
        
        Args:
            order_number: Order number to dispatch
            items: List of {"code": str, "qty": int}
            despatch_date: Dispatch date in format "YYYY-MM-DD HH:MM:SS"
            delivery_service: Delivery service name
            courier_name: Courier name
            tracking_reference: Tracking reference
            earliest_delivery: Optional earliest delivery date in format "YYYY-MM-DD"
            latest_delivery: Optional latest delivery date in format "YYYY-MM-DD"
            
        Returns:
            API response
            
        Raises:
            ValueError: If authentication state is invalid or validation fails
            PermissionError: If not authenticated (401)
        """
        # Validate authentication state
        if not self.auth.session:
            raise ValueError("Must be authenticated before making this call")
        if not self.auth.supplier_id:
            raise ValueError("Must be authenticated before making this call")
        
        # Create and validate request using Pydantic model
        try:
            request = DispatchOrderRequest(
                order_number=order_number,
                items=items,
                despatch_date=despatch_date,
                delivery_service=delivery_service,
                courier_name=courier_name,
                tracking_reference=tracking_reference,
                earliest_delivery=earliest_delivery,
                latest_delivery=latest_delivery
            )
        except Exception as e:
            raise ValueError(f"Invalid dispatch request: {e}")
        
        # Convert to dict and restructure for API call
        request_dict = request.model_dump(exclude_none=True)
        
        # Transform items to item_arr as expected by API
        payload = {
            "order_number": request_dict["order_number"],
            "delivery_service": request_dict["delivery_service"],
            "courier_name": request_dict["courier_name"],
            "despatch_date": request_dict["despatch_date"],
            "tracking_reference": request_dict["tracking_reference"],
            "item_arr": [{"code": item.code, "qty": item.qty} for item in request.items]
        }
        
        # Add optional delivery dates if provided
        if request_dict.get("earliest_delivery"):
            payload["earliest_delivery"] = request_dict["earliest_delivery"]
        if request_dict.get("latest_delivery"):
            payload["latest_delivery"] = request_dict["latest_delivery"]
        
        return self._post("order_event.api", payload)
    
    def cancel_order(self, order_number: str, items: list, cancel_code: str, cancel_reason: str = ""):
        """Cancel an order by sending a cancellation event.
        
        Args:
            order_number: Order number to cancel
            items: List of {"code": str, "qty": int}
            cancel_code: Must be one of: "Stock not available", "Unable to contact customer to arrange delivery", "Unable to deliver to address"
            cancel_reason: Optional free-text cancellation reason
            
        Returns:
            API response
            
        Raises:
            ValueError: If authentication state is invalid or validation fails
            PermissionError: If not authenticated (401)
        """
        # Validate authentication state
        if not self.auth.session:
            raise ValueError("Must be authenticated before making this call")
        if not self.auth.supplier_id:
            raise ValueError("Must be authenticated before making this call")
        
        # Create and validate request using Pydantic model
        try:
            request = CancelOrderRequest(
                order_number=order_number,
                items=items,
                cancel_code=cancel_code,
                cancel_reason=cancel_reason
            )
        except Exception as e:
            raise ValueError(f"Invalid cancel request: {e}")
        
        # Convert to dict and restructure for API call
        request_dict = request.model_dump()
        
        # Transform items to item_arr as expected by API
        payload = {
            "order_number": request_dict["order_number"],
            "cancel_code": request_dict["cancel_code"],
            "cancel_reason": request_dict["cancel_reason"],
            "item_arr": [{"code": item.code, "qty": item.qty} for item in request.items]
        }
        
        return self._post("order_event.api", payload)
