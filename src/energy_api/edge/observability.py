# Author: Jerry Onyango
# Contribution: Collects and exposes edge runtime health metrics for device status, latency, queues, errors, and sync timing.
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class RuntimeObservability:
    # Centralized place to track and report on the health 
    # and performance of the edge runtime. Collects metrics on device health, 
    # communication latencies, error counts, and timing of key events like telemetry 
    # polls and state syncs. The snapshot method can be called to get a current 
    # view of these metrics for monitoring or debugging purposes.
    device_health: dict[str, dict[str, Any]] = field(default_factory=dict)
    error_counts: dict[str, int] = field(default_factory=dict)
    poll_latencies_ms: list[float] = field(default_factory=list)
    last_poll_time: datetime | None = None
    last_sync_time: datetime | None = None

    def mark_device_health(self, device_id: str, healthy: bool, reason: str | None = None) -> None:
        self.device_health[device_id] = {
            "healthy": healthy,
            "reason": reason,
            "updated_at": datetime.now(UTC).isoformat(),
        }

    def record_poll_latency(self, milliseconds: float) -> None:
        self.poll_latencies_ms.append(float(milliseconds))
        if len(self.poll_latencies_ms) > 200:
            self.poll_latencies_ms = self.poll_latencies_ms[-200:]
        self.last_poll_time = datetime.now(UTC)

    # This can be called after a successful state sync to track when the 
    # last successful synchronization with the control loop occurred. 
    # This is useful for monitoring the health of the data pipeline and 
    # ensuring that the edge runtime is operating on fresh data.
    def record_sync(self) -> None:
        self.last_sync_time = datetime.now(UTC)

    # Called whenever an error occurs in the edge 
    # runtime, with a key that categorizes the type of error 
    # (e.g., "modbus_timeout", "mqtt_publish_failure", etc.).
    # This allows for tracking the frequency of different error types 
    # over time, which can be useful
    def increment_error(self, key: str) -> None:
        self.error_counts[key] = self.error_counts.get(key, 0) + 1

    # The snapshot method provides a structured view of the current observability metrics,
    # which can be used for logging, monitoring dashboards, or debugging. It includes
    # the health status of each device, recent poll latencies, error counts, and timestamps
    def snapshot(self, replay_queue_size: int, command_backlog: int) -> dict[str, Any]:
        avg_latency = 0.0
        if self.poll_latencies_ms:
            avg_latency = sum(self.poll_latencies_ms) / len(self.poll_latencies_ms)
        return {
            "per_device_health": self.device_health,
            "poll_latency": {
                "latest_ms": self.poll_latencies_ms[-1] if self.poll_latencies_ms else 0.0,
                "avg_ms": round(avg_latency, 3),
                "samples": len(self.poll_latencies_ms),
            },
            "replay_queue_size": int(replay_queue_size),
            "command_backlog": int(command_backlog),
            "error_counts": self.error_counts,
            "last_poll_time": self.last_poll_time.isoformat() if self.last_poll_time else None,
            "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time else None,
        }
