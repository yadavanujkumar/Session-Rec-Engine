"""Item catalog management."""

from typing import List, Dict
import json


class ItemCatalog:
    """Manages the item catalog."""

    def __init__(self):
        """Initialize item catalog."""
        self.items: Dict[str, Dict] = {}
        self.item_to_idx: Dict[str, int] = {}
        self.idx_to_item: Dict[int, str] = {}

    def add_items(self, items: List[Dict]):
        """
        Add items to catalog.

        Args:
            items: List of item dictionaries with 'item_id' and optional metadata
        """
        for item in items:
            item_id = item["item_id"]
            self.items[item_id] = item

            # Create index mappings if not exists
            if item_id not in self.item_to_idx:
                idx = len(self.item_to_idx) + 1  # Start from 1 (0 is padding)
                self.item_to_idx[item_id] = idx
                self.idx_to_item[idx] = item_id

    def get_item_index(self, item_id: str) -> int:
        """Get numeric index for item ID."""
        return self.item_to_idx.get(item_id, 0)  # 0 for unknown items (padding)

    def get_item_id(self, idx: int) -> str:
        """Get item ID from numeric index."""
        return self.idx_to_item.get(idx, "unknown")

    def get_all_item_ids(self) -> List[str]:
        """Get all item IDs."""
        return list(self.items.keys())

    def get_num_items(self) -> int:
        """Get total number of items."""
        return len(self.items)

    def save_catalog(self, filepath: str):
        """Save catalog to file."""
        data = {
            "items": self.items,
            "item_to_idx": self.item_to_idx,
            "idx_to_item": {int(k): v for k, v in self.idx_to_item.items()},
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_catalog(cls, filepath: str):
        """Load catalog from file."""
        with open(filepath, "r") as f:
            data = json.load(f)

        catalog = cls()
        catalog.items = data["items"]
        catalog.item_to_idx = data["item_to_idx"]
        catalog.idx_to_item = {int(k): v for k, v in data["idx_to_item"].items()}
        return catalog

    @classmethod
    def create_sample_catalog(cls, num_items: int = 100):
        """
        Create a sample catalog for testing.

        Args:
            num_items: Number of items to create

        Returns:
            ItemCatalog instance
        """
        catalog = cls()

        categories = ["Electronics", "Clothing", "Books", "Home", "Sports"]
        items = [
            {
                "item_id": f"item_{i:04d}",
                "name": f"Product {i}",
                "category": categories[i % len(categories)],
                "price": 10.0 + (i * 5.0),
            }
            for i in range(num_items)
        ]

        catalog.add_items(items)
        return catalog
