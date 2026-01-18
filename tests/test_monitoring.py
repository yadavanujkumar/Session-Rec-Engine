"""Tests for metrics tracking."""

import pytest
from src.monitoring import MetricsTracker, LatencyTimer
import time


def test_metrics_initialization():
    """Test metrics tracker initialization."""
    tracker = MetricsTracker(window_size=100)

    assert tracker.window_size == 100
    assert tracker.total_requests == 0


def test_record_recommendation():
    """Test recording recommendations."""
    tracker = MetricsTracker(window_size=100)

    # Record a hit
    tracker.record_recommendation(
        items_recommended=["item_1", "item_2", "item_3"],
        item_clicked="item_2",
        latency_ms=10.5,
        used_coldstart=False,
    )

    assert tracker.total_requests == 1
    assert tracker.model_requests == 1
    assert tracker.coldstart_requests == 0
    assert tracker.get_hit_rate(10) == 100.0


def test_hit_rate_calculation():
    """Test hit rate calculation."""
    tracker = MetricsTracker(window_size=100)

    # Record hits and misses
    tracker.record_recommendation(["item_1", "item_2"], "item_1")  # Hit
    tracker.record_recommendation(["item_1", "item_2"], "item_3")  # Miss
    tracker.record_recommendation(["item_1", "item_2"], "item_2")  # Hit

    hit_rate = tracker.get_hit_rate(10)
    assert hit_rate == pytest.approx(66.67, rel=0.1)


def test_latency_tracking():
    """Test latency tracking."""
    tracker = MetricsTracker(window_size=100)

    # Record different latencies
    tracker.record_recommendation(["item_1"], latency_ms=10.0)
    tracker.record_recommendation(["item_1"], latency_ms=20.0)
    tracker.record_recommendation(["item_1"], latency_ms=100.0)

    avg_latency = tracker.get_average_latency()
    p99_latency = tracker.get_p99_latency()

    assert avg_latency == pytest.approx(43.33, rel=0.1)
    assert p99_latency >= 90.0  # P99 should be close to max


def test_latency_timer():
    """Test latency timer context manager."""
    with LatencyTimer() as timer:
        time.sleep(0.01)  # Sleep for 10ms

    assert timer.latency_ms is not None
    assert timer.latency_ms >= 10.0  # At least 10ms


def test_metrics_summary():
    """Test metrics summary."""
    tracker = MetricsTracker(window_size=100)

    tracker.record_recommendation(["item_1"], "item_1", 10.0, False)
    tracker.record_recommendation(["item_2"], None, 20.0, True)

    summary = tracker.get_metrics_summary()

    assert "hit_rate_at_10" in summary
    assert "p99_latency_ms" in summary
    assert "total_requests" in summary
    assert summary["total_requests"] == 2
    assert summary["model_requests"] == 1
    assert summary["coldstart_requests"] == 1
