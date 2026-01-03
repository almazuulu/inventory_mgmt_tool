"""Data models for warehouse management system."""
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class InventoryItem:
    """Represents an inventory item with its quantity.
    
    Attributes:
        item_id: Unique identifier for the item (alphanumeric string)
        quantity: Positive integer representing item count (must be > 0)
    """
    item_id: str
    quantity: int
    
    def __post_init__(self):
        """Validate inventory item data."""
        if not self.item_id or not isinstance(self.item_id, str):
            raise ValueError("item_id must be a non-empty string")
        if not self.item_id.replace('_', '').isalnum():
            raise ValueError("item_id must be alphanumeric")
        if not isinstance(self.quantity, int) or self.quantity <= 0:
            raise ValueError("quantity must be a positive integer")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "item_id": self.item_id,
            "quantity": self.quantity
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "InventoryItem":
        """Create InventoryItem from dictionary."""
        return cls(
            item_id=data["item_id"],
            quantity=data["quantity"]
        )


@dataclass
class Location:
    """Represents a warehouse location with its inventory.
    
    Attributes:
        location_id: Globally unique location name (alphanumeric string)
        inventory: Dictionary mapping item_id to InventoryItem
    """
    location_id: str
    inventory: Dict[str, InventoryItem] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate location data."""
        if not self.location_id or not isinstance(self.location_id, str):
            raise ValueError("location_id must be a non-empty string")
        if not self.location_id.replace('_', '').isalnum():
            raise ValueError("location_id must be alphanumeric")
    
    def has_inventory(self) -> bool:
        """Check if location has any inventory items."""
        return len(self.inventory) > 0
    
    def get_item_quantity(self, item_id: str) -> int:
        """Get quantity of specific item, returns 0 if item doesn't exist."""
        if item_id in self.inventory:
            return self.inventory[item_id].quantity
        return 0
    
    