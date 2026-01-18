"""Example usage of the recommendation system."""
import requests
import json
import time
from typing import List


class RecommendationClient:
    """Client for interacting with the recommendation API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def record_click(self, session_id: str, item_id: str):
        """Record a click event."""
        response = requests.post(
            f"{self.base_url}/api/v1/click",
            json={"session_id": session_id, "item_id": item_id}
        )
        return response.json()
    
    def get_recommendations(self, session_id: str):
        """Get recommendations for a session."""
        response = requests.post(
            f"{self.base_url}/api/v1/recommend",
            json={"session_id": session_id}
        )
        return response.json()
    
    def record_feedback(self, session_id: str, recommended_items: List[str], 
                       clicked_item: str = None):
        """Record feedback for recommendations."""
        response = requests.post(
            f"{self.base_url}/api/v1/feedback",
            json={
                "session_id": session_id,
                "recommended_items": recommended_items,
                "clicked_item": clicked_item
            }
        )
        return response.json()
    
    def get_metrics(self):
        """Get system metrics."""
        response = requests.get(f"{self.base_url}/api/v1/metrics")
        return response.json()
    
    def health_check(self):
        """Check system health."""
        response = requests.get(f"{self.base_url}/api/v1/health")
        return response.json()


def simulate_user_session(client: RecommendationClient, session_id: str):
    """Simulate a user session."""
    print(f"\n{'='*60}")
    print(f"Simulating session: {session_id}")
    print(f"{'='*60}\n")
    
    # Initially, session is empty (cold-start scenario)
    print("Step 1: Getting initial recommendations (cold-start)")
    recs = client.get_recommendations(session_id)
    print(f"  Recommendations: {recs['recommendations']}")
    print(f"  Used cold-start: {recs['used_coldstart']}")
    print(f"  Message: {recs['message']}\n")
    
    # User clicks on first recommendation
    first_item = recs['recommendations'][0]
    print(f"Step 2: User clicks on {first_item}")
    client.record_click(session_id, first_item)
    client.record_feedback(session_id, recs['recommendations'], first_item)
    print(f"  Click recorded\n")
    
    # Get recommendations after 1 click (still cold-start)
    print("Step 3: Getting recommendations after 1 click (still cold-start)")
    recs = client.get_recommendations(session_id)
    print(f"  Recommendations: {recs['recommendations']}")
    print(f"  Used cold-start: {recs['used_coldstart']}\n")
    
    # User clicks on another item
    second_item = recs['recommendations'][1]
    print(f"Step 4: User clicks on {second_item}")
    client.record_click(session_id, second_item)
    client.record_feedback(session_id, recs['recommendations'], second_item)
    print(f"  Click recorded\n")
    
    # Get recommendations after 2 clicks (now using model)
    print("Step 5: Getting recommendations after 2 clicks (using model)")
    recs = client.get_recommendations(session_id)
    print(f"  Recommendations: {recs['recommendations']}")
    print(f"  Used cold-start: {recs['used_coldstart']}")
    print(f"  Message: {recs['message']}\n")
    
    # User continues clicking
    for i in range(3):
        item = recs['recommendations'][i % len(recs['recommendations'])]
        print(f"Step {6+i}: User clicks on {item}")
        client.record_click(session_id, item)
        client.record_feedback(session_id, recs['recommendations'], item)
        recs = client.get_recommendations(session_id)
        print(f"  New recommendations: {recs['recommendations']}")
        print(f"  Used cold-start: {recs['used_coldstart']}\n")
        time.sleep(0.5)


def main():
    """Run example usage."""
    client = RecommendationClient()
    
    # Check health
    print("Checking system health...")
    try:
        health = client.health_check()
        print(f"Status: {health['status']}")
        print(f"Components: {json.dumps(health['components'], indent=2)}\n")
    except Exception as e:
        print(f"Error: Could not connect to API. Make sure the service is running.")
        print(f"Start the service with: python main.py")
        print(f"Or use docker-compose: docker-compose up")
        return
    
    # Simulate multiple user sessions
    sessions = ["user_001", "user_002", "user_003"]
    
    for session_id in sessions:
        simulate_user_session(client, session_id)
        time.sleep(1)
    
    # Show final metrics
    print(f"\n{'='*60}")
    print("Final System Metrics")
    print(f"{'='*60}\n")
    
    metrics = client.get_metrics()
    print(f"Hit Rate@10: {metrics['hit_rate_at_10']}%")
    print(f"P99 Latency: {metrics['p99_latency_ms']} ms")
    print(f"P50 Latency: {metrics['p50_latency_ms']} ms")
    print(f"Average Latency: {metrics['avg_latency_ms']} ms")
    print(f"Total Requests: {metrics['total_requests']}")
    print(f"Cold-start Requests: {metrics['coldstart_requests']}")
    print(f"Model Requests: {metrics['model_requests']}")
    print(f"Cold-start %: {metrics['coldstart_percentage']}%")
    print()


if __name__ == "__main__":
    main()
