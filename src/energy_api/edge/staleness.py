# Author: Jerry Onyango
# Contribution: Tracks per-signal freshness and classifies stale conditions for missing reads and decode failures.
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class SignalState:
    last_ok_at: datetime | None = None
    last_value: float | None = None


class StalenessTracker:
    def __init__(self, stale_after_seconds: int) -> None:
        self.stale_after = timedelta(seconds=stale_after_seconds)
        self._state: dict[str, SignalState] = {}

    def evaluate(
        self,
        key: str,
        now: datetime,
        value: float | None,
        *,
        missing_read: bool,
        decode_failed: bool,
    ) -> tuple[bool, str | None]:
        signal_state = self._state.setdefault(key, SignalState())

        if decode_failed:
            return True, "decode_failure"

        if missing_read:
            if signal_state.last_ok_at is None:
                return True, "missing_read"
            stale = now - signal_state.last_ok_at > self.stale_after
            return stale, "missing_read" if stale else None

        if value is None:
            if signal_state.last_ok_at is None:
                return True, "missing_value"
            stale = now - signal_state.last_ok_at > self.stale_after
            return stale, "missing_value" if stale else None

        repeated = signal_state.last_value is not None and value == signal_state.last_value
        signal_state.last_ok_at = now
        signal_state.last_value = value

        if repeated:
            return False, None
        return False, None
