import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.exceptions import (
    InsufficientQuantityError,
    ItemNotFoundError,
    LocationAlreadyExistsError,
    LocationHasInventoryError,
    LocationNotFoundError,
)
from src.service import WarehouseService
from src.storage import FileStorage


class TestWarehouseService(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.state_path = Path(self._tmp.name) / "warehouse_state.json"
        self.storage = FileStorage(file_path=self.state_path)
        self.service = WarehouseService(self.storage)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_register_location_ok_and_duplicate_err(self):
        self.service.register_location("L1")
        self.assertIn("L1", self.service.locations)

        with self.assertRaises(LocationAlreadyExistsError):
            self.service.register_location("L1")

    def test_unregister_location_errors_and_ok(self):
        with self.assertRaises(LocationNotFoundError):
            self.service.unregister_location("NOPE")

        self.service.register_location("L1")
        self.service.increment_inventory("L1", "IA", 1)

        with self.assertRaises(LocationHasInventoryError):
            self.service.unregister_location("L1")

        self.service.decrement_inventory("L1", "IA", 1)
        self.service.unregister_location("L1")
        self.assertNotIn("L1", self.service.locations)

    def test_increment_inventory_location_not_found(self):
        with self.assertRaises(LocationNotFoundError):
            self.service.increment_inventory("NOPE", "IA", 1)

    def test_increment_inventory_add_and_increment(self):
        self.service.register_location("L1")
        self.service.increment_inventory("L1", "IA", 2)
        self.service.increment_inventory("L1", "IA", 3)
        self.assertEqual(self.service.locations["L1"].get_item_quantity("IA"), 5)

    def test_decrement_inventory_item_not_found(self):
        self.service.register_location("L1")
        with self.assertRaises(ItemNotFoundError):
            self.service.decrement_inventory("L1", "IA", 1)

    def test_decrement_inventory_insufficient_quantity(self):
        self.service.register_location("L1")
        self.service.increment_inventory("L1", "IA", 2)
        with self.assertRaises(InsufficientQuantityError) as ctx:
            self.service.decrement_inventory("L1", "IA", 3)
        self.assertIn("(has 2)", str(ctx.exception))

    def test_decrement_inventory_to_zero_removes_item(self):
        self.service.register_location("L1")
        self.service.increment_inventory("L1", "IA", 2)
        self.service.decrement_inventory("L1", "IA", 2)
        self.assertNotIn("IA", self.service.locations["L1"].inventory)

    def test_transfer_inventory_errors_and_ok(self):
        self.service.register_location("SRC")
        self.service.register_location("DST")

        with self.assertRaises(ItemNotFoundError):
            self.service.transfer_inventory("SRC", "DST", "IA", 1)

        self.service.increment_inventory("SRC", "IA", 2)
        with self.assertRaises(InsufficientQuantityError):
            self.service.transfer_inventory("SRC", "DST", "IA", 3)

        self.service.transfer_inventory("SRC", "DST", "IA", 2)
        self.assertEqual(self.service.locations["SRC"].get_item_quantity("IA"), 0)
        self.assertEqual(self.service.locations["DST"].get_item_quantity("IA"), 2)

    def test_observe_inventory_sorted(self):
        self.service.register_location("L1")
        self.service.increment_inventory("L1", "IB", 1)
        self.service.increment_inventory("L1", "IA", 2)
        items = self.service.observe_inventory("L1")
        self.assertEqual([i.item_id for i in items], ["IA", "IB"])


if __name__ == "__main__":
    unittest.main()


