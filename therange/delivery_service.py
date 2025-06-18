from enum import Enum


class DeliveryService(Enum):
    """Enum for delivery service types."""
    MAINLAND = "mainland"
    HIGHLANDS = "highlands"
    ISLANDS = "islands"
    NORTHERN_IRELAND = "northern_ireland"