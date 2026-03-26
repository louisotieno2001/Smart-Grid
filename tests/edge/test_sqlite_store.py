# Author: Jerry Onyango
# Contribution: Verifies SQLite edge store initialization, WAL mode, and telemetry buffering behavior.
from __future__ import annotations

import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from energy_api.edge.storage.sqlite import EdgeSQLiteStore
from energy_api.edge.types import TelemetryRecord


class TestSQLiteStore(unittest.TestCase):
    def test_initializes_wal_and_tables(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "edge_runtime.db")
            store = EdgeSQLiteStore(db_path)
            store.initialize()

            self.assertEqual(store.get_wal_mode(), "wal")

            record = TelemetryRecord(
                canonical_key="battery_soc",
                value=50.0,
                unit="%",
                quality="good",
                ts=datetime.now(UTC),
                device_ts=datetime.now(UTC),
                gateway_received_at=datetime.now(UTC),
                processed_at=datetime.now(UTC),
                stale=False,
            )
            inserted = store.enqueue_telemetry("site_1", [record])
            self.assertEqual(inserted, 1)

            pending = store.list_pending_telemetry(limit=10)
            self.assertEqual(len(pending), 1)
            self.assertEqual(pending[0]["site_id"], "site_1")


if __name__ == "__main__":
    unittest.main()
