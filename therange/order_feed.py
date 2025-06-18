from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from .base_client import BaseClient


class OrderFeedRequest(BaseModel):
    """Pydantic model for order feed request validation."""
    search: Optional[str] = None
    type: str = Field(default="all", description="Order type filter")
    from_date: Optional[str] = Field(alias="from", default=None, description="Start date for filtering")
    to_date: Optional[str] = Field(alias="to", default=None, description="End date for filtering")
    
    @validator('type')
    def validate_type(cls, v):
        """Validate that type is one of the allowed values."""
        allowed_types = ["all", "new", "pending", "historic"]
        if v not in allowed_types:
            raise ValueError(f"type must be one of {allowed_types}, got '{v}'")
        return v
    
    @validator('to_date')
    def validate_date_range(cls, v, values):
        """Validate that date range doesn't exceed 35 days."""
        if v is not None and 'from_date' in values and values['from_date'] is not None:
            try:
                from_dt = datetime.strptime(values['from_date'], '%Y-%m-%d %H:%M:%S')
                to_dt = datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
                delta = to_dt - from_dt
                if delta.days > 35:
                    raise ValueError("Date range cannot exceed 35 days")
            except ValueError as e:
                if "Date range cannot exceed 35 days" in str(e):
                    raise e
                # If parsing fails, let it slide for now (optional validation)
                pass
        return v


class OrderFeedClient(BaseClient):
    def get_orders(self, search=None, type="all", from_date=None, to_date=None):
        """Get orders from the order feed API with optional filtering.
        
        Args:
            search: Optional search term (order number, customer name, postcode, phone, etc.)
            type: Order type filter ("all", "new", "pending", "historic")
            from_date: Start date for filtering (format: "YYYY-MM-DD HH:MM:SS")
            to_date: End date for filtering (format: "YYYY-MM-DD HH:MM:SS")
            
        Returns:
            API response containing order_arr
            
        Raises:
            ValueError: If authentication state is invalid or parameters are invalid
            PermissionError: If not authenticated (401)
        """
        # Validate authentication state
        if not self.auth.session:
            raise ValueError("Must be authenticated before making this call")
        if not self.auth.supplier_id:
            raise ValueError("Must be authenticated before making this call")
        
        # Create and validate request using Pydantic model
        try:
            request = OrderFeedRequest(
                search=search,
                type=type,
                **{"from": from_date, "to": to_date}
            )
        except Exception as e:
            raise ValueError(f"Invalid parameters: {e}")
        
        # Convert to dict for API call, excluding None values
        payload = request.model_dump(by_alias=True, exclude_none=True)
        
        return self._post("order_feed.api", payload)
