import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.controller import WarehouseController
from src.service import WarehouseService
from src.storage import FileStorage


class TestWarehouseController(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.state_path = Path(self._tmp.name) / "warehouse_state.json"
        storage = FileStorage(file_path=self.state_path)
        service = WarehouseService(storage)
        self.controller = WarehouseController(service)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_empty_line_returns_empty_string(self):
        self.assertEqual(self.controller.execute_command("   "), "")

    def test_invalid_command_too_few_tokens(self):
        resp = self.controller.execute_command("LOCATION")
        self.assertTrue(resp.startswith("ERR: "))

    def test_unknown_domain(self):
        resp = self.controller.execute_command("FOO BAR baz")
        self.assertEqual(resp, "ERR: Invalid command: Unknown domain: FOO")

    def test_register_and_observe_empty(self):
        self.assertEqual(self.controller.execute_command("LOCATION REGISTER L1"), "OK")
        self.assertEqual(self.controller.execute_command("INVENTORY OBSERVE L1"), "EMPTY")

    def test_observe_format_multiline_sorted(self):
        self.controller.execute_command("LOCATION REGISTER L1")
        self.controller.execute_command("INVENTORY INCREMENT L1 IB 1")
        self.controller.execute_command("INVENTORY INCREMENT L1 IA 2")

        resp = self.controller.execute_command("INVENTORY OBSERVE L1")
        self.assertEqual(resp.splitlines(), ["ITEM IA 2", "ITEM IB 1"])

    def test_argument_count_validation(self):
        resp = self.controller.execute_command("LOCATION REGISTER")
        self.assertTrue(resp.startswith("ERR: "))

        resp = self.controller.execute_command("INVENTORY TRANSFER A B C")
        self.assertTrue(resp.startswith("ERR: "))

    def test_quantity_validation(self):
        self.controller.execute_command("LOCATION REGISTER L1")

        resp = self.controller.execute_command("INVENTORY INCREMENT L1 IA 0")
        self.assertEqual(resp, "ERR: Invalid command: Quantity must be a positive integer")

        resp = self.controller.execute_command("INVENTORY INCREMENT L1 IA nope")
        self.assertEqual(resp, "ERR: Invalid command: Invalid quantity: 'nope' is not an integer")


if __name__ == "__main__":
    unittest.main()


