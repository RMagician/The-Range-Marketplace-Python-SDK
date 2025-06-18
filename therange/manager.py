from .auth import AuthClient
from .order_feed import OrderFeedClient
from .order_ack import OrderAckClient
from .order_event import OrderEventClient
from .stock_availability import StockAvailabilityClient
from .product_feed import ProductFeedClient

class TheRangeManager:
    def __init__(self, username, password, test=False):
        self.auth = AuthClient(username, password, test)
        self.order_feed = OrderFeedClient(self.auth)
        self.order_ack = OrderAckClient(self.auth)
        self.order_event = OrderEventClient(self.auth)
        self.stock_availability = StockAvailabilityClient(self.auth)
        self.product_feed = ProductFeedClient(self.auth)

    def authenticate(self):
        return self.auth.authenticate()
