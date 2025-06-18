from .base_client import BaseClient

class OrderAckClient(BaseClient):
    def acknowledge_orders(self, ack_payload):
        return self._post("order_ack.api", ack_payload)
