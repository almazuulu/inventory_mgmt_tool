import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.exceptions import StorageError
from src.models import Location
from src.storage import FileStorage


class TestFileStorage(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.state_path = Path(self._tmp.name) / "warehouse_state.json"
        self.storage = FileStorage(file_path=self.state_path)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_load_missing_file_returns_empty_dict(self):
        self.assertEqual(self.storage.load(), {})

    def test_load_empty_file_returns_empty_dict(self):
        self.state_path.write_text("", encoding="utf-8")
        self.assertEqual(self.storage.load(), {})

    def test_save_and_load_roundtrip(self):
        loc = Location(location_id="L1")
        loc.add_item("IA", 2)
        loc.add_item("IB", 1)

        self.storage.save({"L1": loc})

        loaded = self.storage.load()
        self.assertIn("L1", loaded)
        self.assertEqual(loaded["L1"].get_item_quantity("IA"), 2)
        self.assertEqual(loaded["L1"].get_item_quantity("IB"), 1)

    def test_load_invalid_json_raises_storage_error(self):
        self.state_path.write_text("{", encoding="utf-8")
        with self.assertRaises(StorageError):
            self.storage.load()


if __name__ == "__main__":
    unittest.main()


