from locust import HttpUser, task, between
import random

# The 5 products the model was trained on (same list as GET /items returns).
# A name outside this list gets 404 and would be counted as a failure.
ITEMS = [
    "BLACK VELVET",
    "FIREBALL CINNAMON WHISKEY",
    "HAWKEYE VODKA",
    "TITOS HANDMADE VODKA",
    "FIVE O'CLOCK VODKA",
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
