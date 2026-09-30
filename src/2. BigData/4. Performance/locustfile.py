from locust import HttpUser, task, between
import random

# Sample items to test with
ITEMS = [
    "BLACK VELVET",
    "JACK DANIELS",
    "CAPTAIN MORGAN",
    "JAGERMEISTER",
    "BACARDI",
]


class IowaAPIUser(HttpUser):
    """
    Simulates a user making prediction requests to the Iowa Sales API.

    Each user:
    - Waits 1-3 seconds between requests (simulates realistic usage)
    - Makes prediction requests for random items
    """

    wait_time = between(1, 3)

    @task(10)
    def predict_random_item(self):
        """Make prediction for a random item (90% of traffic)"""
        item = random.choice(ITEMS)
        self.client.get(f"/predict/{item}", name="/predict/[item]")

    @task(1)
    def get_items(self):
        """Get list of all items (10% of traffic)"""
        self.client.get("/items")
