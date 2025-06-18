from therange import TheRangeManager
from therange.product_feed import (
    ProductFeedRequest, ProductEntry, PriceEntry, ProductAttribute,
    PriceAmendmentRequest, PriceAmendmentEntry
)
from datetime import date

api = TheRangeManager("your_username", "your_password", test=True)
api.authenticate()

# Example: Get orders
orders = api.order_feed.get_orders()
print("Orders:", orders)

# Example: Submit a product (legacy method - still works)
response = api.product_feed.submit_products([
    {
        "vendor_sku": "ABC123",
        "title": "Test Shoe",
        "brand": "The Range",
        "price_arr": [
            {
                "price": "49.99",
                "currency": "GBP",
                "effective_from": "2025-06-20"
            }
        ],
        "product_category": "Shoes",
        "description": "A Shoe Test",
        "image_url_arr": ["https://www.therange.co.uk/example1.jpg"],
        "fulfilment_class": "Small"
    }
])
print("Product feed result:", response)

# Example: Submit products using new Pydantic models
price = PriceEntry(
    price=89.99,
    currency="GBP",
    effective_from=date(2025, 7, 1)
)

product_attributes = ProductAttribute(
    colour="Blue",
    colour_name="Ocean Blue",
    length="25cm",
    width="15cm",
    weight="500g"
)

product = ProductEntry(
    vendor_sku="DEF456",
    title="Premium Test Product",
    brand="The Range",
    price_arr=[price],
    product_category="Electronics",
    description="A premium test product with full attribute support",
    feature_arr=["Feature 1", "Feature 2", "Waterproof"],
    image_url_arr=["https://www.therange.co.uk/premium1.jpg"],
    youtube_url_arr=["https://youtube.com/watch?v=demo"],
    fulfilment_class="Medium",
    product_attribute=product_attributes,
    gtin="9876543210987",
    child_hazard=0,
    age_restriction="8+",
    launch_date=date(2025, 8, 1),
    active=1,
    visible=1
)

# Using the new send_product_feed method
feed_request = ProductFeedRequest(product_arr=[product])
response = api.product_feed.send_product_feed(feed_request)
print("Enhanced product feed result:", response)

# Example: Send product feed from dictionaries with validation
product_data = [
    {
        "vendor_sku": "GHI789",
        "title": "Validated Product",
        "brand": "The Range",
        "price_arr": [
            {
                "price": 19.99,
                "currency": "GBP",
                "effective_from": "2025-06-15"
            }
        ],
        "product_category": "Home & Garden",
        "description": "Product validated with Pydantic models",
        "image_url_arr": ["https://www.therange.co.uk/validated.jpg"],
        "fulfilment_class": "Small"
    }
]

response = api.product_feed.send_product_feed_dict(product_data)
print("Validated product feed result:", response)

# Example: Price amendment
price_amendment = PriceAmendmentEntry(
    vendor_sku="ABC123",
    price_arr=[PriceEntry(
        price=39.99,  # Reduced price
        currency="GBP",
        effective_from=date(2025, 7, 15)
    )]
)

amendment_request = PriceAmendmentRequest(product_arr=[price_amendment])
response = api.product_feed.send_price_amendment(amendment_request)
print("Price amendment result:", response)

# Example: Price amendment from dictionary
price_data = [
    {
        "vendor_sku": "DEF456",
        "price_arr": [
            {
                "price": 79.99,
                "currency": "GBP",
                "effective_from": "2025-08-01"
            }
        ]
    }
]

response = api.product_feed.send_price_amendment_dict(price_data)
print("Price amendment from dict result:", response)
