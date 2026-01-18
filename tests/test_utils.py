"""Tests for item catalog."""
import pytest
from src.utils import ItemCatalog


def test_catalog_initialization():
    """Test catalog initialization."""
    catalog = ItemCatalog()
    
    assert len(catalog.items) == 0
    assert len(catalog.item_to_idx) == 0


def test_add_items():
    """Test adding items to catalog."""
    catalog = ItemCatalog()
    items = [
        {"item_id": "item_1", "name": "Product 1"},
        {"item_id": "item_2", "name": "Product 2"},
    ]
    
    catalog.add_items(items)
    
    assert len(catalog.items) == 2
    assert catalog.get_num_items() == 2
    assert "item_1" in catalog.item_to_idx
    assert "item_2" in catalog.item_to_idx


def test_item_indexing():
    """Test item index mapping."""
    catalog = ItemCatalog()
    items = [
        {"item_id": "item_1"},
        {"item_id": "item_2"},
    ]
    catalog.add_items(items)
    
    # Test forward mapping
    idx1 = catalog.get_item_index("item_1")
    idx2 = catalog.get_item_index("item_2")
    
    assert idx1 != idx2
    assert idx1 > 0  # Should start from 1 (0 is padding)
    assert idx2 > 0
    
    # Test reverse mapping
    assert catalog.get_item_id(idx1) == "item_1"
    assert catalog.get_item_id(idx2) == "item_2"
    
    # Test unknown item
    assert catalog.get_item_index("unknown") == 0
    assert catalog.get_item_id(999) == "unknown"


def test_sample_catalog():
    """Test creating a sample catalog."""
    catalog = ItemCatalog.create_sample_catalog(num_items=50)
    
    assert catalog.get_num_items() == 50
    assert len(catalog.get_all_item_ids()) == 50
    
    # Check that items have proper structure
    item_id = catalog.get_all_item_ids()[0]
    assert item_id in catalog.items
    assert "name" in catalog.items[item_id]
    assert "category" in catalog.items[item_id]
