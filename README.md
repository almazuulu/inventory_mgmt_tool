# Warehouse Inventory Management Tool

CLI tool for managing warehouse locations and inventory with concurrent access support.

## Quick Start

### Python (venv)

```bash
# Clone and enter directory
cd inventory_mgmt_tool

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install
pip install -e .

# Run
inventory-tool
```

### Docker

```bash
# Build
docker build -t warehouse-tool .

# Run interactive
docker run -it --rm warehouse-tool

# Run with persistent data
mkdir -p warehouse_data
docker run -it --rm \
  -v $(pwd)/warehouse_data:/app/data \
  -e WAREHOUSE_FILE=/app/data/warehouse_state.json \
  warehouse-tool
```

## Commands

| Command | Description |
|---------|-------------|
| `LOCATION REGISTER <id>` | Register new location |
| `LOCATION UNREGISTER <id>` | Remove location (must be empty) |
| `INVENTORY INCREMENT <loc> <item> <qty>` | Add items |
| `INVENTORY DECREMENT <loc> <item> <qty>` | Remove items |
| `INVENTORY TRANSFER <from> <to> <item> <qty>` | Move items |
| `INVENTORY OBSERVE <loc>` | List items at location |

## Usage Examples

### Example 1: Basic Operations

```bash
$ inventory-tool
LOCATION REGISTER WH1
OK
LOCATION REGISTER WH2
OK
INVENTORY INCREMENT WH1 LAPTOP 10
OK
INVENTORY INCREMENT WH1 MOUSE 50
OK
INVENTORY OBSERVE WH1
ITEM LAPTOP 10
ITEM MOUSE 50
INVENTORY TRANSFER WH1 WH2 LAPTOP 5
OK
INVENTORY OBSERVE WH1
ITEM LAPTOP 5
ITEM MOUSE 50
INVENTORY OBSERVE WH2
ITEM LAPTOP 5
```

### Example 2: Error Handling

```bash
$ inventory-tool
LOCATION REGISTER WH1
OK
LOCATION REGISTER WH1
ERR: Location 'WH1' already exists
INVENTORY INCREMENT WH1 ITEM1 10
OK
INVENTORY DECREMENT WH1 ITEM1 15
ERR: Insufficient quantity of item ITEM1 in location WH1 (has 10)
LOCATION UNREGISTER WH1
ERR: Location 'WH1' has inventories
```

### Example 3: Using Input File

Create `commands.txt`:
```
LOCATION REGISTER TOKYO
LOCATION REGISTER OSAKA
INVENTORY INCREMENT TOKYO SKU001 100
INVENTORY INCREMENT TOKYO SKU002 200
INVENTORY TRANSFER TOKYO OSAKA SKU001 50
INVENTORY OBSERVE TOKYO
INVENTORY OBSERVE OSAKA
```

Run:
```bash
# Python
cat commands.txt | inventory-tool

# Docker
cat commands.txt | docker run -i --rm warehouse-tool
```

Output:
```
OK
OK
OK
OK
OK
ITEM SKU001 50
ITEM SKU002 200
ITEM SKU001 50
```

### Example 4: Multiple Warehouses

```bash
$ inventory-tool
LOCATION REGISTER NYC
OK
LOCATION REGISTER LA
OK
LOCATION REGISTER CHI
OK
INVENTORY INCREMENT NYC WIDGET 1000
OK
INVENTORY INCREMENT NYC GADGET 500
OK
INVENTORY TRANSFER NYC LA WIDGET 300
OK
INVENTORY TRANSFER NYC CHI WIDGET 200
OK
INVENTORY TRANSFER NYC CHI GADGET 100
OK
INVENTORY OBSERVE NYC
ITEM GADGET 400
ITEM WIDGET 500
INVENTORY OBSERVE LA
ITEM WIDGET 300
INVENTORY OBSERVE CHI
ITEM GADGET 100
ITEM WIDGET 200
```

## Configuration

Set custom state file:
```bash
export WAREHOUSE_FILE=/path/to/state.json
inventory-tool
```

Default: `warehouse_state.json` in current directory.

## Project Structure

```
src/
├── main.py          # CLI entry point
├── controller.py    # Command parsing
├── service.py       # Business logic
├── storage.py       # JSON persistence + file locking
├── models.py        # Data models
└── exceptions.py    # Error types
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

#
# Testing
#
# Run tests (uses pytest config from pyproject.toml, including coverage)
pytest

# Or run via Makefile (coverage in terminal + html report)
make test

# Format & lint
black src tests
mypy src
ruff check src tests
```
