from therange import TheRangeManager

api = TheRangeManager("your_username", "your_password", test=True)
api.authenticate()

# Example: Get orders
orders = api.order_feed.get_orders()
print("Orders:", orders)

# Example: Submit a product
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
