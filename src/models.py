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
    
    def add_item(self, item_id: str, quantity: int) -> None:
        """Add or increment item quantity in location."""
        if item_id in self.inventory:
            self.inventory[item_id].quantity += quantity
        else:
            self.inventory[item_id] = InventoryItem(item_id=item_id, quantity=quantity)
    
    def remove_item(self, item_id: str, quantity: int) -> None:
        """Remove or decrement item quantity from location.
        
        Raises:
            KeyError: If item doesn't exist in location
            ValueError: If quantity to remove exceeds available quantity
        """
        if item_id not in self.inventory:
            raise KeyError(f"Item '{item_id}' not found in location '{self.location_id}'")
        
        current_quantity = self.inventory[item_id].quantity
        if quantity > current_quantity:
            raise ValueError(
                f"Insufficient quantity: trying to remove {quantity}, "
                f"but only {current_quantity} available"
            )
        
        new_quantity = current_quantity - quantity
        if new_quantity == 0:
            del self.inventory[item_id]
        else:
            self.inventory[item_id].quantity = new_quantity
    
    def get_sorted_items(self) -> list[InventoryItem]:
        """Get list of items sorted alphabetically by item_id."""
        return sorted(self.inventory.values(), key=lambda item: item.item_id)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "location_id": self.location_id,
            "inventory": {
                item_id: item.to_dict() 
                for item_id, item in self.inventory.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Location":
        """Create Location from dictionary."""
        location = cls(location_id=data["location_id"])
        location.inventory = {
            item_id: InventoryItem.from_dict(item_data)
            for item_id, item_data in data.get("inventory", {}).items()
        }
        return location

