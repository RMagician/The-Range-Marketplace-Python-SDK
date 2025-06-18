from .base_client import BaseClient

class ProductFeedClient(BaseClient):
    def submit_products(self, product_arr):
        if not isinstance(product_arr, list):
            raise ValueError("product_arr must be a list")
        for p in product_arr:
            title = p.get("title")
            if title and len(title) > 80:
                raise ValueError(f"Product title exceeds 80 characters: {title}")

        return self._post("product_feed.api", {"product_arr": product_arr}, include_mode=False)
