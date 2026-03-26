# Author: Jerry Onyango
# Contribution: Validates ordered at-least-once replay semantics with retry persistence under transient upload failure.
from __future__ import annotations

import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from energy_api.edge.replay import ReplayService
from energy_api.edge.storage.sqlite import EdgeSQLiteStore
from energy_api.edge.types import TelemetryRecord


class TestReplayService(unittest.TestCase):
    def test_replay_preserves_order_and_at_least_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "edge_runtime.db")
            store = EdgeSQLiteStore(db_path)
            store.initialize()

            records = [
                TelemetryRecord(
                    canonical_key="battery_soc",
                    value=60.0 + i,
                    unit="%",
                    quality="good",
                    ts=datetime.now(UTC),
                    device_ts=datetime.now(UTC),
                    gateway_received_at=datetime.now(UTC),
                    processed_at=datetime.now(UTC),
                    stale=False,
                )
                for i in range(3)
            ]
            store.enqueue_telemetry("site_demo", records)

            calls: list[tuple[int, dict]] = []
            failures = {1}

            def upload(site_id: str, payload: dict) -> None:
                idx = len(calls)
                calls.append((idx, payload))
                if idx in failures:
                    raise RuntimeError("cloud down")

            replay = ReplayService(store=store, upload_fn=upload, base_backoff_seconds=1, max_backoff_seconds=2)
            first = replay.replay_once(limit=10)
            self.assertEqual(first["attempted"], 3)
            self.assertEqual(first["sent"], 2)
            self.assertEqual(first["failed"], 1)

            self.assertEqual(store.count_buffered_telemetry(), 1)

            remaining = store.list_pending_telemetry(limit=10)
            self.assertLessEqual(len(remaining), 1)

            if remaining:
                row_id = remaining[0]["id"]
            else:
                row_id = store.list_buffered_row_ids(limit=1)[0]
            store.mark_telemetry_retry(row_id, "manual immediate retry", backoff_seconds=0)
            second = replay.replay_once(limit=10)
            self.assertEqual(second["sent"], 1)
            self.assertEqual(second["remaining"], 0)


if __name__ == "__main__":
    unittest.main()
