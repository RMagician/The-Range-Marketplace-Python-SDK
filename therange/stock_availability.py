from .base_client import BaseClient

class StockAvailabilityClient(BaseClient):
    def update_stock(self, stock_data: list):
        # Validate authentication state
        if not self.auth.session:
            raise ValueError("Must be authenticated before making this call")
        if not self.auth.supplier_id:
            raise ValueError("Must be authenticated before making this call")
        
        # Validate stock_data format
        if not isinstance(stock_data, list):
            raise ValueError("stock_data must be a list")
        if not stock_data:
            raise ValueError("stock_data must be a non-empty list")
        
        # Validate each stock entry
        for item in stock_data:
            if not isinstance(item, dict):
                raise ValueError("Each item in stock_data must be a dictionary")
            if "code" not in item:
                raise ValueError("Each item must include 'code'")
            if "qty" not in item:
                raise ValueError("Each item must include 'qty'")
            if not isinstance(item["code"], str):
                raise ValueError("'code' must be a string")
            if not isinstance(item["qty"], int) or item["qty"] < 0:
                raise ValueError("'qty' must be an integer >= 0")
        
        return self._post("stock_availability.api", stock_data, include_mode=False)
