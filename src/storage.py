import json
from pathlib import Path
from typing import Dict

from filelock import FileLock, Timeout

from src.config import LOCK_TIMEOUT, WAREHOUSE_FILE_PATH
from src.exceptions import StorageError
from src.models import Location


class FileStorage:
    """Handles persistent storage of warehouse state with file locking for concurrent access.
    
    This class manages reading and writing warehouse state to/from a JSON file,
    ensuring thread-safety and process-safety through file locking.
    
    Attributes:
        file_path: Path to the JSON file storing warehouse state
        lock_path: Path to the lock file for synchronization
        lock_timeout: Maximum time to wait for file lock acquisition
    """
    
    def __init__(
        self, 
        file_path: Path = WAREHOUSE_FILE_PATH, 
        lock_timeout: float = LOCK_TIMEOUT
    ):
        """Initialize FileStorage with specified file path and lock timeout.
        
        Args:
            file_path: Path to the storage file (default from config)
            lock_timeout: Timeout in seconds for lock acquisition
        """
        self.file_path = file_path
        self.lock_path = Path(str(file_path) + ".lock")
        self.lock_timeout = lock_timeout
        self._lock = FileLock(self.lock_path, timeout=self.lock_timeout)
    
    def load(self) -> Dict[str, Location]:
        """Load warehouse state from file with proper locking.
        
        Returns:
            Dictionary mapping location_id to Location objects
            
        Raises:
            StorageError: If file reading or deserialization fails
        """
        try:
            with self._lock:
                # If file doesn't exist or is empty, return empty state
                if not self.file_path.exists() or self.file_path.stat().st_size == 0:
                    return {}
                
                # Read and parse JSON file
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Deserialize locations from JSON
                locations = {}
                for location_id, location_data in data.get('locations', {}).items():
                    locations[location_id] = Location.from_dict(location_data)
                
                return locations
                
        except Timeout as e:
            raise StorageError(
                f"Failed to acquire file lock within {self.lock_timeout}s"
            ) from e
        except json.JSONDecodeError as e:
            raise StorageError(f"Invalid JSON in storage file: {e}") from e
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to read storage file: {e}") from e
        except Exception as e:
            raise StorageError(f"Unexpected error loading state: {e}") from e
    
    def save(self, locations: Dict[str, Location]) -> None:
        """Save warehouse state to file with proper locking.
        
        Args:
            locations: Dictionary mapping location_id to Location objects
            
        Raises:
            StorageError: If file writing or serialization fails
        """
        try:
            with self._lock:
                # Serialize locations to JSON-compatible format
                data = {
                    'locations': {
                        location_id: location.to_dict()
                        for location_id, location in locations.items()
                    }
                }
                
                # Ensure parent directory exists
                self.file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write to temporary file first, then atomic rename
                temp_path = self.file_path.with_suffix('.tmp')
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                # Atomic replace to prevent corruption
                temp_path.replace(self.file_path)
                
        except Timeout as e:
            raise StorageError(
                f"Failed to acquire file lock within {self.lock_timeout}s"
            ) from e
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to write storage file: {e}") from e
        except Exception as e:
            raise StorageError(f"Unexpected error saving state: {e}") from e

