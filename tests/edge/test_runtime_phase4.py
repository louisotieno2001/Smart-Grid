# Author: Jerry Onyango
# Contribution: Validates runtime idempotency, unresolved-command safety blocking, command reconciliation processing, and health snapshots.
from __future__ import annotations

import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from energy_api.edge.commands import CommandExecutor
from energy_api.edge.replay import ReplayService
from energy_api.edge.runtime import EdgeRuntime
from energy_api.edge.storage.sqlite import EdgeSQLiteStore
from energy_api.edge.types import TelemetryRecord


class FakePoller:
    class FakeAdapter:
        host = "edge-host"
        port = 15020

    def __init__(self) -> None:
        self.adapter = self.FakeAdapter()

    def poll_once(self):
        return [
            TelemetryRecord(
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
        ]


class FakeAdapterForCommands:
    def __init__(self) -> None:
        self.registers = {1: 10, 2: 10}

    def write_single_register(self, address: int, value: int, unit_id: int = 1) -> None:
        self.registers[address] = value & 0xFFFF

    def read_holding_registers(self, address: int, count: int, unit_id: int = 1) -> list[int]:
        return [self.registers.get(address + i, 0) for i in range(count)]


class TestRuntimePhase4(unittest.TestCase):
    def test_idempotency_safety_and_observability(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "edge_runtime.db")
            store = EdgeSQLiteStore(db_path)
            replay = ReplayService(store=store, upload_fn=lambda site_id, payload: None)
            executor = CommandExecutor(adapter=FakeAdapterForCommands())

            runtime = EdgeRuntime(
                store=store,
                replay=replay,
                poller=FakePoller(),
                command_executor=executor,
                site_id="site_x",
                command_reconcile_fn=lambda command: "acked",
            )
            runtime.startup_recovery()

            payload = {
                "command_type": "set_limit",
                "limit_register": 40,
                "target_limit": 66,
            }
            queued = runtime.submit_command("cmd_100", payload, idempotency_key="idem-1")
            self.assertEqual(queued["status"], "queued")

            dedup = runtime.submit_command("cmd_100", payload, idempotency_key="idem-1")
            self.assertEqual(dedup["status"], "deduplicated")

            blocked = runtime.submit_command("cmd_101", payload, idempotency_key="idem-2")
            self.assertEqual(blocked["status"], "blocked")

            processed = runtime.process_command_backlog(limit=10)
            self.assertEqual(processed["acked"], 1)

            runtime.run_poll_cycle()
            health = runtime.health_snapshot()

            self.assertIn("per_device_health", health)
            self.assertIn("poll_latency", health)
            self.assertIn("replay_queue_size", health)
            self.assertIn("command_backlog", health)
            self.assertIn("error_counts", health)
            self.assertIn("last_poll_time", health)
            self.assertIn("last_sync_time", health)


if __name__ == "__main__":
    unittest.main()
