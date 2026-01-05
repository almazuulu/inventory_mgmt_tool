"""Command controller for parsing and executing warehouse operations."""

from src.config import ERR_PREFIX, MSG_EMPTY, MSG_OK
from src.exceptions import InvalidCommandError, WarehouseError
from src.service import WarehouseService


class WarehouseController:
    """Handles parsing of command strings and execution via WarehouseService.
    
    Responsible for:
    - Parsing command strings into operation + parameters
    - Validating parameter types and counts
    - Calling appropriate service methods
    - Formatting responses as "OK" or "ERR: <message>"
    """
    
    def __init__(self, service: WarehouseService):
        """Initialize controller with warehouse service.
        
        Args:
            service: WarehouseService instance for business logic
        """
        self.service = service
    
    def execute_command(self, command_line: str) -> str:
        """Parse and execute a command string, returning formatted response.
        
        Args:
            command_line: Command string (e.g., "LOCATION REGISTER loc1")
            
        Returns:
            Formatted response: "OK", "EMPTY", item list, or "ERR: <message>"
        """
        try:
            # Strip whitespace and skip empty lines
            command_line = command_line.strip()
            if not command_line:
                return ""
            
            # Parse command into tokens
            tokens = command_line.split()
            if len(tokens) < 2:
                raise InvalidCommandError("Command must have at least 2 tokens")
            
            domain = tokens[0].upper()
            operation = tokens[1].upper()
            args = tokens[2:]
            
            # Route to appropriate handler
            if domain == "LOCATION":
                return self._handle_location_command(operation, args)
            elif domain == "INVENTORY":
                return self._handle_inventory_command(operation, args)
            else:
                raise InvalidCommandError(f"Unknown domain: {domain}")
                
        except WarehouseError as e:
            return self._format_error(str(e))
        except ValueError as e:
            return self._format_error(str(e))
        except Exception as e:  # pylint: disable=broad-exception-caught
            return self._format_error(f"Unexpected error: {e}")
    
    def _handle_location_command(self, operation: str, args: list) -> str:
        """Handle LOCATION domain commands (REGISTER, UNREGISTER).
        
        Args:
            operation: Operation name (REGISTER or UNREGISTER)
            args: Command arguments
            
        Returns:
            Formatted response string
        """
        if operation == "REGISTER":
            if len(args) != 1:
                raise InvalidCommandError(
                    f"LOCATION REGISTER requires 1 argument, got {len(args)}"
                )
            location_id = args[0]
            self._validate_identifier(location_id, "location_id")
            self.service.register_location(location_id)
            return MSG_OK
            
        elif operation == "UNREGISTER":
            if len(args) != 1:
                raise InvalidCommandError(
                    f"LOCATION UNREGISTER requires 1 argument, got {len(args)}"
                )
            location_id = args[0]
            self._validate_identifier(location_id, "location_id")
            self.service.unregister_location(location_id)
            return MSG_OK
            
        else:
            raise InvalidCommandError(f"Unknown LOCATION operation: {operation}")
    
    def _handle_inventory_command(self, operation: str, args: list) -> str:
        """Handle INVENTORY domain commands (INCREMENT, DECREMENT, TRANSFER, OBSERVE).
        
        Args:
            operation: Operation name
            args: Command arguments
            
        Returns:
            Formatted response string
        """
        if operation == "INCREMENT":
            if len(args) != 3:
                raise InvalidCommandError(
                    f"INVENTORY INCREMENT requires 3 arguments, got {len(args)}"
                )
            location_id, item_id, qty_str = args
            self._validate_identifier(location_id, "location_id")
            self._validate_identifier(item_id, "item_id")
            quantity = self._parse_quantity(qty_str)
            self.service.increment_inventory(location_id, item_id, quantity)
            return MSG_OK
            
        elif operation == "DECREMENT":
            if len(args) != 3:
                raise InvalidCommandError(
                    f"INVENTORY DECREMENT requires 3 arguments, got {len(args)}"
                )
            location_id, item_id, qty_str = args
            self._validate_identifier(location_id, "location_id")
            self._validate_identifier(item_id, "item_id")
            quantity = self._parse_quantity(qty_str)
            self.service.decrement_inventory(location_id, item_id, quantity)
            return MSG_OK
            
        elif operation == "TRANSFER":
            if len(args) != 4:
                raise InvalidCommandError(
                    f"INVENTORY TRANSFER requires 4 arguments, got {len(args)}"
                )
            src_loc, dest_loc, item_id, qty_str = args
            self._validate_identifier(src_loc, "source_location_id")
            self._validate_identifier(dest_loc, "destination_location_id")
            self._validate_identifier(item_id, "item_id")
            quantity = self._parse_quantity(qty_str)
            self.service.transfer_inventory(src_loc, dest_loc, item_id, quantity)
            return MSG_OK
            
        elif operation == "OBSERVE":
            if len(args) != 1:
                raise InvalidCommandError(
                    f"INVENTORY OBSERVE requires 1 argument, got {len(args)}"
                )
            location_id = args[0]
            self._validate_identifier(location_id, "location_id")
            items = self.service.observe_inventory(location_id)
            return self._format_observe_response(items)
            
        else:
            raise InvalidCommandError(f"Unknown INVENTORY operation: {operation}")
    
    def _validate_identifier(self, identifier: str, param_name: str) -> None:
        """Validate that identifier is non-empty alphanumeric string.
        
        Args:
            identifier: String to validate
            param_name: Parameter name for error messages
            
        Raises:
            InvalidCommandError: If identifier is invalid
        """
        if not identifier:
            raise InvalidCommandError(f"{param_name} cannot be empty")
        if not identifier.replace('_', '').isalnum():
            raise InvalidCommandError(
                f"{param_name} must be alphanumeric (underscores allowed)"
            )
    
    def _parse_quantity(self, qty_str: str) -> int:
        """Parse and validate quantity string.
        
        Args:
            qty_str: String representation of quantity
            
        Returns:
            Parsed integer quantity
            
        Raises:
            InvalidCommandError: If quantity is invalid
        """
        try:
            quantity = int(qty_str)
            if quantity <= 0:
                raise InvalidCommandError("Quantity must be a positive integer")
            return quantity
        except ValueError as exc:
            raise InvalidCommandError(
                f"Invalid quantity: '{qty_str}' is not an integer"
            ) from exc
    
    def _format_observe_response(self, items: list) -> str:
        """Format OBSERVE command response.
        
        Args:
            items: List of InventoryItem objects
            
        Returns:
            Formatted string:
            - "EMPTY" if no items
            - otherwise multi-line output, one line per item:
              "ITEM <item_id> <qty>"
        """
        if not items:
            return MSG_EMPTY

        # PDF spec: one line per item, sorted by item_id
        sorted_items = sorted(items, key=lambda item: item.item_id)
        lines = [f"ITEM {item.item_id} {item.quantity}" for item in sorted_items]
        return "\n".join(lines)
    
    def _format_error(self, message: str) -> str:
        """Format error message with ERR prefix.
        
        Args:
            message: Error message
            
        Returns:
            Formatted error string: "ERR: <message>"
        """
        return f"{ERR_PREFIX}: {message}"


