import os
from pathlib import Path


# File persistence configuration
WAREHOUSE_FILE = os.environ.get(
    'WAREHOUSE_FILE', 
    'warehouse_state.json'
)

WAREHOUSE_FILE_PATH = Path(WAREHOUSE_FILE)

# File locking configuration
LOCK_TIMEOUT = 5.0
LOCK_RETRY_DELAY = 0.01

# Command parsing configuration
VALID_COMMANDS = {
    'LOCATION': ['REGISTER', 'UNREGISTER'],
    'INVENTORY': ['INCREMENT', 'DECREMENT', 'TRANSFER', 'OBSERVE']
}

# Output messages
MSG_OK = "OK"
MSG_EMPTY = "EMPTY"

# Error message prefix
ERR_PREFIX = "ERR"

