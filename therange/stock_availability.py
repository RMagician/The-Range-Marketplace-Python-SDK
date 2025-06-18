from .base_client import BaseClient

class StockAvailabilityClient(BaseClient):
    def update_stock(self, stock_payload):
        return self._post("stock_availability.api", stock_payload, include_mode=False)
