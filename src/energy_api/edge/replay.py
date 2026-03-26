# Author: Jerry Onyango
# Contribution: Implements ordered at-least-once telemetry replay with persisted retry/backoff handling.
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .storage.sqlite import EdgeSQLiteStore


UploadFn = Callable[[str, dict], None]


@dataclass
class ReplayService:
    store: EdgeSQLiteStore
    upload_fn: UploadFn
    base_backoff_seconds: int = 2
    max_backoff_seconds: int = 60

    def buffer_telemetry(self, site_id: str, records: list[object]) -> int:
        return self.store.enqueue_telemetry(site_id=site_id, records=records)

    def replay_once(self, limit: int = 100) -> dict[str, int]:
        pending = self.store.list_pending_telemetry(limit=limit)
        sent = 0
        failed = 0

        for row in pending:
            try:
                self.upload_fn(row["site_id"], row["payload"])
                self.store.ack_telemetry(row["id"])
                sent += 1
            except Exception as exc:
                backoff = self._backoff_seconds(row["attempt_count"] + 1)
                self.store.mark_telemetry_retry(row["id"], str(exc), backoff_seconds=backoff)
                failed += 1

        return {
            "attempted": len(pending),
            "sent": sent,
            "failed": failed,
            "remaining": len(self.store.list_pending_telemetry(limit=100000)),
        }

    def rebuild_queue_snapshot(self, limit: int = 100000) -> list[dict]:
        return self.store.list_pending_telemetry(limit=limit)

    def _backoff_seconds(self, attempt: int) -> int:
        value = self.base_backoff_seconds * (2 ** max(0, attempt - 1))
        return min(self.max_backoff_seconds, value)
