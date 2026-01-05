import io
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from src import main as main_module
from src.storage import FileStorage as RealFileStorage


class TestCLIIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.state_path = Path(self._tmp.name) / "warehouse_state.json"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_cli_flow_observe_multiline(self):
        input_data = "\n".join(
            [
                "LOCATION REGISTER L1",
                "INVENTORY INCREMENT L1 IB 1",
                "INVENTORY INCREMENT L1 IA 2",
                "INVENTORY OBSERVE L1",
                "",
            ]
        )

        stdin = io.StringIO(input_data)
        stdout = io.StringIO()

        # Ensure CLI uses a temp state file (don't touch repo's warehouse_state.json)
        def _storage_factory():
            return RealFileStorage(file_path=self.state_path)

        with patch.object(main_module, "FileStorage", _storage_factory), patch.object(
            main_module.sys, "stdin", stdin
        ), patch.object(main_module.sys, "stdout", stdout):
            main_module.main()

        self.assertEqual(
            stdout.getvalue().splitlines(),
            ["OK", "OK", "OK", "ITEM IA 2", "ITEM IB 1"],
        )


if __name__ == "__main__":
    unittest.main()


