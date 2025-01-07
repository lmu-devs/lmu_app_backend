from locust import HttpUser, task, between
import random

class WishlistUser(HttpUser):
    # Wait between 1 to 5 seconds between tasks
    wait_time = between(1, 5)
    
    def on_start(self):
        """Initialize user with API key"""
        # You might want to get a real API key for testing
        self.headers = {
            "user-api-key": "e6fa19d33ad0e52e258d3cd33c2b637cec9e7478d7bcc30685ccc301c50c9fb1"
        }

    @task(3)  # Weight of 3 (more frequent)
    def get_wishlists(self):
        self.client.get("/wishlists", headers=self.headers)
    
    @task(2)
    def get_single_wishlist(self):
        # Assuming you have wishlists with IDs 1-10
        wishlist_id = random.randint(1, 10)
        self.client.get(f"/wishlists?id={wishlist_id}", headers=self.headers)
    
    @task(1)  # Weight of 1 (less frequent)
    def toggle_like(self):
        wishlist_id = random.randint(1, 10)
        self.client.post(
            f"/wishlists/toggle-like?id={wishlist_id}",
            headers=self.headers
        )

    # @task(1)
    # def create_wishlist(self):
    #     payload = {
    #         "status": "PLANNED",
    #         "translations": [
    #             {
    #                 "title": f"Test Wishlist {random.randint(1, 1000)}",
    #                 "description": "Test Description",
    #                 "description_short": "Test Short",
    #                 "language": "GERMAN"
    #             }
    #         ]
    #     }
    #     self.client.post(
    #         "/wishlists",
    #         json=payload,
    #         headers=self.headers
    #     )