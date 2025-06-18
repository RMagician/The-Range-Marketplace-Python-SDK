from typing import Optional
from .auth import AuthClient
from .order_feed import OrderFeedClient
from .order_ack import OrderAckClient
from .order_event import OrderEventClient
from .stock_availability import StockAvailabilityClient
from .product_feed import ProductFeedClient
from .config import Config

class TheRangeManager:
    def __init__(self, username, password, test=False, config: Optional[Config] = None):
        """
        Initialize TheRangeManager.
        
        Args:
            username: The username for authentication
            password: The password for authentication
            test: Legacy parameter for backward compatibility. If True, uses UAT environment.
                  Ignored if config is provided.
            config: Configuration object. If not provided, uses production or UAT based on test parameter.
        """
        self.auth = AuthClient(username, password, test=test, config=config)
        self.order_feed = OrderFeedClient(self.auth)
        self.order_ack = OrderAckClient(self.auth)
        self.order_event = OrderEventClient(self.auth)
        self.stock_availability = StockAvailabilityClient(self.auth)
        self.product_feed = ProductFeedClient(self.auth)

    def authenticate(self):
        return self.auth.authenticate()
