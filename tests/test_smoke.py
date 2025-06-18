"""
Smoke tests for The Range SDK.

Basic tests to verify core functionality works without making live API calls.
"""


def test_basic_truth():
    """Basic smoke test to verify testing framework works."""
    assert True


def test_enum():
    """Test that DeliveryService enum works correctly."""
    from therange.delivery_service import DeliveryService
    assert DeliveryService.MAINLAND.value == "mainland"


def test_package_import():
    """Test that the main package can be imported."""
    import therange
    assert hasattr(therange, 'TheRangeManager')


def test_delivery_service_enum_values():
    """Test all DeliveryService enum values."""
    from therange.delivery_service import DeliveryService
    
    # Test all expected values
    assert DeliveryService.MAINLAND.value == "mainland"
    assert DeliveryService.HIGHLANDS.value == "highlands"
    assert DeliveryService.ISLANDS.value == "islands"
    assert DeliveryService.NORTHERN_IRELAND.value == "northern_ireland"
    
    # Test that enum has 4 members
    assert len(DeliveryService) == 4