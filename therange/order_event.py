from .base_client import BaseClient

class OrderEventClient(BaseClient):
    def send_event(self, event_payload):
        return self._post("order_event.api", event_payload)
