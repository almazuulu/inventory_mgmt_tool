"""Custom exceptions for warehouse management system."""


class WarehouseError(Exception):
    """Base exception for all warehouse-related errors."""
    pass


class LocationAlreadyExistsError(WarehouseError):
    """Raised when attempting to register a location that already exists."""
    
    def __init__(self, location_id: str):
        self.location_id = location_id
        super().__init__(f"Location '{location_id}' already exists")


class LocationNotFoundError(WarehouseError):
    """Raised when attempting to access a location that doesn't exist."""
    
    def __init__(self, location_id: str):
        self.location_id = location_id
        super().__init__(f"Location '{location_id}' does not exist")


class LocationHasInventoryError(WarehouseError):
    """Raised when attempting to unregister a location that still has inventory."""
    
    def __init__(self, location_id: str):
        self.location_id = location_id
        super().__init__(f"Location '{location_id}' has inventories")


class ItemNotFoundError(WarehouseError):
    """Raised when attempting to access an item that doesn't exist in a location."""
    
    def __init__(self, item_id: str, location_id: str):
        self.item_id = item_id
        self.location_id = location_id
        super().__init__(f"Item '{item_id}' not found in location '{location_id}'")


class InsufficientQuantityError(WarehouseError):
    """Raised when attempting to remove more items than available."""
    
    def __init__(self, item_id: str, location_id: str, requested: int, available: int):
        self.item_id = item_id
        self.location_id = location_id
        self.requested = requested
        self.available = available
        super().__init__(
            f"Insufficient quantity of item {item_id} in location {location_id} "
            f"(has {available})"
        )


class InvalidCommandError(WarehouseError):
    """Raised when a command cannot be parsed or is invalid."""
    
    def __init__(self, message: str):
        super().__init__(f"Invalid command: {message}")


class StorageError(WarehouseError):
    """Raised when there's an error with file storage operations."""
    
    def __init__(self, message: str):
        super().__init__(f"Storage error: {message}")

