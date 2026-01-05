"""Main entry point for warehouse inventory management CLI."""

import sys
from pathlib import Path

from src.controller import WarehouseController
from src.service import WarehouseService
from src.storage import FileStorage


def main():
    """Main CLI loop: reads commands from stdin and executes them.
    
    Reads commands line by line from stdin, processes each command via
    the controller, and prints responses to stdout.
    
    Exit conditions:
    - EOF (Ctrl+D) or empty input
    - Fatal storage errors
    """
    # Initialize storage, service, and controller
    storage = FileStorage()
    service = WarehouseService(storage)
    controller = WarehouseController(service)
    
    # Read and process commands from stdin
    try:
        for line in sys.stdin:
            # Strip whitespace
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Execute command and print response
            response = controller.execute_command(line)
            if response:  # Don't print empty responses
                print(response)
                sys.stdout.flush()  # Ensure immediate output
                
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\nShutting down...", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        # Handle unexpected errors
        print(f"FATAL ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


