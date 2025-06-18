from .base_client import BaseClient

class OrderFeedClient(BaseClient):
    def get_orders(self):
        return self._post("order_feed.api", {})
