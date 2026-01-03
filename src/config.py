import os
from pathlib import Path


# File persistence configuration
WAREHOUSE_FILE = os.environ.get(
    'WAREHOUSE_FILE', 
    'warehouse_state.json'
)

WAREHOUSE_FILE_PATH = Path(WAREHOUSE_FILE)


