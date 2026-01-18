"""Tests for cold-start bandit."""

from src.coldstart import ThompsonSamplingBandit, ColdStartHandler


def test_bandit_initialization():
    """Test bandit initialization."""
    item_ids = ["item_1", "item_2", "item_3"]
    bandit = ThompsonSamplingBandit(item_ids)

    assert len(bandit.item_ids) == 3
    assert all(bandit.alpha[item_id] == 1.0 for item_id in item_ids)
    assert all(bandit.beta[item_id] == 1.0 for item_id in item_ids)


def test_bandit_select_items():
    """Test item selection."""
    item_ids = ["item_1", "item_2", "item_3", "item_4", "item_5"]
    bandit = ThompsonSamplingBandit(item_ids)

    selected = bandit.select_items(k=3)

    assert len(selected) == 3
    assert all(item in item_ids for item in selected)


def test_bandit_update():
    """Test bandit update with reward."""
    item_ids = ["item_1", "item_2"]
    bandit = ThompsonSamplingBandit(item_ids)

    # Update with positive reward
    bandit.update("item_1", reward=1.0)
    assert bandit.alpha["item_1"] == 2.0
    assert bandit.beta["item_1"] == 1.0

    # Update with negative reward
    bandit.update("item_2", reward=0.0)
    assert bandit.alpha["item_2"] == 1.0
    assert bandit.beta["item_2"] == 2.0


def test_coldstart_handler():
    """Test cold-start handler."""
    item_ids = ["item_1", "item_2", "item_3"]
    bandit = ThompsonSamplingBandit(item_ids)
    handler = ColdStartHandler(bandit, threshold=2)

    # Should use cold-start for session length < 2
    assert handler.should_use_coldstart(0) is True
    assert handler.should_use_coldstart(1) is True
    assert handler.should_use_coldstart(2) is False
    assert handler.should_use_coldstart(3) is False

    # Get recommendations
    recommendations = handler.get_recommendations(k=2)
    assert len(recommendations) == 2
