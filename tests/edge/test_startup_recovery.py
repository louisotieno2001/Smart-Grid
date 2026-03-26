# Author: Jerry Onyango
# Contribution: Confirms startup recovery reconciles unresolved commands and rebuilds replay state before poll cycles run.
from __future__ import annotations

import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from energy_api.edge.replay import ReplayService
from energy_api.edge.runtime import EdgeRuntime
from energy_api.edge.storage.sqlite import EdgeSQLiteStore
from energy_api.edge.types import TelemetryRecord


class FakePoller:
    def poll_once(self):
        return []


class FakeCommandExecutor:
    def execute_and_reconcile(self, payload: dict):
        return True, "ok"

    def reconcile_only(self, payload: dict):
        return True, "ok"


class TestStartupRecovery(unittest.TestCase):
    def test_startup_recovery_reconciles_before_poll(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "edge_runtime.db")
            store = EdgeSQLiteStore(db_path)
            store.initialize()

            record = TelemetryRecord(
                canonical_key="site_load",
                value=100.0,
                unit="kW",
                quality="good",
                ts=datetime.now(UTC),
                device_ts=datetime.now(UTC),
                gateway_received_at=datetime.now(UTC),
                processed_at=datetime.now(UTC),
                stale=False,
            )
            store.enqueue_telemetry("site_x", [record])
            store.upsert_command("cmd_1", "site_x", {"command_type": "charge"}, status="queued")

            replay = ReplayService(store=store, upload_fn=lambda site_id, payload: None)
            runtime = EdgeRuntime(
                store=store,
                replay=replay,
                poller=FakePoller(),
                command_executor=FakeCommandExecutor(),
                site_id="site_x",
                command_reconcile_fn=lambda command: "acked",
            )

            result = runtime.startup_recovery()
            self.assertEqual(result.pending_telemetry, 1)
            self.assertEqual(result.unresolved_commands, 1)
            self.assertEqual(result.reconciled_commands, 1)
            self.assertEqual(result.replay_queue_rebuilt, 1)

            cycle = runtime.run_poll_cycle()
            self.assertTrue(cycle["recovery_done"])


if __name__ == "__main__":
    unittest.main()
