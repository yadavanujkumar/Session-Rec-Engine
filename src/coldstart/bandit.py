"""Multi-Armed Bandit algorithm for cold-start handling."""
import numpy as np
from typing import List, Dict, Tuple
import json


class ThompsonSamplingBandit:
    """
    Thompson Sampling Multi-Armed Bandit for trending items.
    
    Uses Beta distribution for each item (arm) to balance exploration vs exploitation.
    """
    
    def __init__(self, item_ids: List[str]):
        """
        Initialize Thompson Sampling bandit.
        
        Args:
            item_ids: List of all item IDs
        """
        self.item_ids = item_ids
        # Initialize Beta distribution parameters (alpha=successes+1, beta=failures+1)
        self.alpha = {item_id: 1.0 for item_id in item_ids}
        self.beta = {item_id: 1.0 for item_id in item_ids}
    
    def select_items(self, k: int = 5) -> List[str]:
        """
        Select top-k items using Thompson Sampling.
        
        Args:
            k: Number of items to select
            
        Returns:
            List of selected item IDs
        """
        # Sample from Beta distribution for each item
        samples = {
            item_id: np.random.beta(self.alpha[item_id], self.beta[item_id])
            for item_id in self.item_ids
        }
        
        # Sort by sampled values and return top-k
        sorted_items = sorted(samples.items(), key=lambda x: x[1], reverse=True)
        return [item_id for item_id, _ in sorted_items[:k]]
    
    def update(self, item_id: str, reward: float):
        """
        Update bandit statistics based on observed reward.
        
        Args:
            item_id: Item that was shown
            reward: Reward (1.0 for click, 0.0 for no click)
        """
        if item_id in self.item_ids:
            if reward > 0:
                self.alpha[item_id] += 1.0
            else:
                self.beta[item_id] += 1.0
    
    def get_statistics(self) -> Dict[str, Dict[str, float]]:
        """
        Get current statistics for all items.
        
        Returns:
            Dictionary with item statistics
        """
        stats = {}
        for item_id in self.item_ids:
            total = self.alpha[item_id] + self.beta[item_id] - 2
            ctr = (self.alpha[item_id] - 1) / total if total > 0 else 0.0
            stats[item_id] = {
                "alpha": self.alpha[item_id],
                "beta": self.beta[item_id],
                "estimated_ctr": ctr,
                "total_impressions": total
            }
        return stats
    
    def save_state(self, filepath: str):
        """Save bandit state to file."""
        state = {
            "item_ids": self.item_ids,
            "alpha": self.alpha,
            "beta": self.beta
        }
        with open(filepath, 'w') as f:
            json.dump(state, f)
    
    @classmethod
    def load_state(cls, filepath: str):
        """Load bandit state from file."""
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        bandit = cls(state["item_ids"])
        bandit.alpha = state["alpha"]
        bandit.beta = state["beta"]
        return bandit


class ColdStartHandler:
    """Handler for cold-start situations using Multi-Armed Bandit."""
    
    def __init__(self, bandit: ThompsonSamplingBandit, threshold: int = 2):
        """
        Initialize cold-start handler.
        
        Args:
            bandit: Thompson Sampling bandit instance
            threshold: Minimum session length to use model
        """
        self.bandit = bandit
        self.threshold = threshold
    
    def should_use_coldstart(self, session_length: int) -> bool:
        """
        Determine if cold-start logic should be used.
        
        Args:
            session_length: Number of clicks in the session
            
        Returns:
            True if cold-start should be used
        """
        return session_length < self.threshold
    
    def get_recommendations(self, k: int = 5) -> List[str]:
        """
        Get cold-start recommendations.
        
        Args:
            k: Number of recommendations
            
        Returns:
            List of recommended item IDs
        """
        return self.bandit.select_items(k)
    
    def update_feedback(self, item_id: str, clicked: bool):
        """
        Update bandit with user feedback.
        
        Args:
            item_id: Item that was shown
            clicked: Whether the item was clicked
        """
        reward = 1.0 if clicked else 0.0
        self.bandit.update(item_id, reward)
