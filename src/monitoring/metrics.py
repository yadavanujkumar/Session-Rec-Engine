"""Metrics tracking for observability."""

import time
import numpy as np
from typing import List, Dict
from collections import deque
from threading import Lock


class MetricsTracker:
    """Real-time metrics tracker for recommendation system."""

    def __init__(self, window_size: int = 1000):
        """
        Initialize metrics tracker.

        Args:
            window_size: Size of sliding window for metrics
        """
        self.window_size = window_size
        self.lock = Lock()

        # Hit Rate tracking
        self.hit_events = deque(maxlen=window_size)

        # Latency tracking (in milliseconds)
        self.latencies = deque(maxlen=window_size)

        # Request tracking
        self.total_requests = 0
        self.coldstart_requests = 0
        self.model_requests = 0

    def record_recommendation(
        self,
        items_recommended: List[str],
        item_clicked: str = None,
        latency_ms: float = None,
        used_coldstart: bool = False,
    ):
        """
        Record a recommendation event.

        Args:
            items_recommended: List of recommended item IDs
            item_clicked: Item that was actually clicked (if any)
            latency_ms: Latency in milliseconds
            used_coldstart: Whether cold-start logic was used
        """
        with self.lock:
            # Record hit rate
            hit = 1 if item_clicked and item_clicked in items_recommended else 0
            self.hit_events.append(hit)

            # Record latency
            if latency_ms is not None:
                self.latencies.append(latency_ms)

            # Update counters
            self.total_requests += 1
            if used_coldstart:
                self.coldstart_requests += 1
            else:
                self.model_requests += 1

    def _calculate_hit_rate(self) -> float:
        """Calculate hit rate without lock (internal use only)."""
        if not self.hit_events:
            return 0.0
        return (sum(self.hit_events) / len(self.hit_events)) * 100

    def _calculate_p99_latency(self) -> float:
        """Calculate P99 latency without lock (internal use only)."""
        if not self.latencies:
            return 0.0
        return float(np.percentile(list(self.latencies), 99))

    def _calculate_average_latency(self) -> float:
        """Calculate average latency without lock (internal use only)."""
        if not self.latencies:
            return 0.0
        return float(np.mean(list(self.latencies)))

    def _calculate_p50_latency(self) -> float:
        """Calculate P50 latency without lock (internal use only)."""
        if not self.latencies:
            return 0.0
        return float(np.percentile(list(self.latencies), 50))

    def get_hit_rate(self, k: int = 10) -> float:
        """
        Calculate Hit Rate@K.

        Args:
            k: Number of recommendations (not used in calculation, just for naming)

        Returns:
            Hit rate as a percentage
        """
        with self.lock:
            return self._calculate_hit_rate()

    def get_p99_latency(self) -> float:
        """
        Calculate P99 latency.

        Returns:
            99th percentile latency in milliseconds
        """
        with self.lock:
            return self._calculate_p99_latency()

    def get_average_latency(self) -> float:
        """
        Calculate average latency.

        Returns:
            Average latency in milliseconds
        """
        with self.lock:
            return self._calculate_average_latency()

    def get_p50_latency(self) -> float:
        """
        Calculate median (P50) latency.

        Returns:
            Median latency in milliseconds
        """
        with self.lock:
            return self._calculate_p50_latency()

    def get_metrics_summary(self) -> Dict:
        """
        Get summary of all metrics.

        Returns:
            Dictionary with all metrics
        """
        with self.lock:
            return {
                "hit_rate_at_10": round(self._calculate_hit_rate(), 2),
                "p99_latency_ms": round(self._calculate_p99_latency(), 2),
                "p50_latency_ms": round(self._calculate_p50_latency(), 2),
                "avg_latency_ms": round(self._calculate_average_latency(), 2),
                "total_requests": self.total_requests,
                "coldstart_requests": self.coldstart_requests,
                "model_requests": self.model_requests,
                "coldstart_percentage": round(
                    (
                        (self.coldstart_requests / self.total_requests * 100)
                        if self.total_requests > 0
                        else 0.0
                    ),
                    2,
                ),
            }

    def reset(self):
        """Reset all metrics."""
        with self.lock:
            self.hit_events.clear()
            self.latencies.clear()
            self.total_requests = 0
            self.coldstart_requests = 0
            self.model_requests = 0


class LatencyTimer:
    """Context manager for measuring latency."""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.latency_ms = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.latency_ms = (self.end_time - self.start_time) * 1000  # Convert to ms
        return False
