from typing import Dict, List

from src.exceptions import (
    InsufficientQuantityError,
    ItemNotFoundError,
    LocationAlreadyExistsError,
    LocationHasInventoryError,
    LocationNotFoundError,
)
from src.models import InventoryItem, Location
from src.storage import FileStorage


class WarehouseService:
    """Core business logic for warehouse location and inventory management."""
    
    def __init__(self, storage: FileStorage):
        """Initialize WarehouseService with storage backend"""
        self.storage = storage
        self.locations: Dict[str, Location] = {}
        self._load_state()
    
    def _load_state(self) -> None:
        """Load warehouse state from storage."""
        self.locations = self.storage.load()
    
    def _save_state(self) -> None:
        """Save current warehouse state to storage."""
        self.storage.save(self.locations)
    
    def register_location(self, location_id: str) -> None:
        """Register a new warehouse location."""
        if location_id in self.locations:
            raise LocationAlreadyExistsError(location_id)
        
        # Create new location with empty inventory
        self.locations[location_id] = Location(location_id=location_id)
        self._save_state()
    
    def unregister_location(self, location_id: str) -> None:
        """Unregister a warehouse location.
        """
        if location_id not in self.locations:
            raise LocationNotFoundError(location_id)
        
        location = self.locations[location_id]
        if location.has_inventory():
            raise LocationHasInventoryError(location_id)
        
        # Remove location from warehouse
        del self.locations[location_id]
        self._save_state()
    
    def increment_inventory(self, location_id: str, item_id: str, quantity: int) -> None:
        """Add quantity of an item to a location's inventory. """
        if location_id not in self.locations:
            raise LocationNotFoundError(location_id)
        
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        # Add or increment item in location
        location = self.locations[location_id]
        location.add_item(item_id, quantity)
        self._save_state()
    
    def decrement_inventory(self, location_id: str, item_id: str, quantity: int) -> None:
        """Subtract quantity of an item from a location's inventory."""
        if location_id not in self.locations:
            raise LocationNotFoundError(location_id)
        
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        location = self.locations[location_id]
        
        # Check if item exists in location
        if item_id not in location.inventory:
            raise ItemNotFoundError(item_id, location_id)
        
        # Check if sufficient quantity available
        available = location.get_item_quantity(item_id)
        if quantity > available:
            raise InsufficientQuantityError(item_id, location_id, quantity, available)
        
        # Remove or decrement item quantity
        try:
            location.remove_item(item_id, quantity)
            self._save_state()
        except (KeyError, ValueError) as e:
            # These should have been caught above, but handle just in case
            if isinstance(e, KeyError):
                raise ItemNotFoundError(item_id, location_id) from e
            raise InsufficientQuantityError(
                item_id, location_id, quantity, available
            ) from e
    
    def transfer_inventory(
        self, 
        src_location_id: str, 
        dest_location_id: str, 
        item_id: str, 
        quantity: int
    ) -> None:
        """Transfer quantity of an item from source to destination location."""
        # Validate both locations exist
        if src_location_id not in self.locations:
            raise LocationNotFoundError(src_location_id)
        if dest_location_id not in self.locations:
            raise LocationNotFoundError(dest_location_id)
        
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        src_location = self.locations[src_location_id]
        dest_location = self.locations[dest_location_id]
        
        # Check if item exists in source
        if item_id not in src_location.inventory:
            raise ItemNotFoundError(item_id, src_location_id)
        
        # Check if sufficient quantity in source
        available = src_location.get_item_quantity(item_id)
        if quantity > available:
            raise InsufficientQuantityError(
                item_id, src_location_id, quantity, available
            )
        
        # Perform transfer: remove from source, add to destination
        src_location.remove_item(item_id, quantity)
        dest_location.add_item(item_id, quantity)
        self._save_state()
    
    def observe_inventory(self, location_id: str) -> List[InventoryItem]:
        """Retrieve all inventory items from a location, sorted by item_id."""
        if location_id not in self.locations:
            raise LocationNotFoundError(location_id)
        
        location = self.locations[location_id]
        return location.get_sorted_items()

