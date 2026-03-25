# Author: Jerry Onyango
# Contribution: Dispatches control actions into command records with retry and pending-ack blocking safeguards.

# /Users/loan/Desktop/energyallocation/src/energy_api/control/dispatcher.py
from __future__ import annotations

import os
from typing import Any

from .models import ScoredAction
from .repository import ControlRepository


class CommandDispatcher:
    def __init__(self, repository: ControlRepository | None = None) -> None:
        self.repository = repository or ControlRepository()
        self.max_retries = int(os.getenv("EA_COMMAND_MAX_RETRIES", "3"))

    def dispatch(
        self,
        site_id: str,
        device_id: str,
        action: ScoredAction,
        reason: str,
        target_soc: float | None = None,
        idempotency_key: str | None = None,
        ack_block_seconds: int = 30,
    ) -> dict[str, Any]:
        pending = self.repository.get_last_sent_unacked_command(device_id, ack_block_seconds)
        if pending:
            return {
                "status": "blocked",
                "reason": "pending_unacknowledged_command",
                "command": pending,
            }

        command = self.repository.create_command(
            site_id=site_id,
            device_id=device_id,
            command_type=action.action_type,
            target_power_kw=action.target_power_kw,
            target_soc=target_soc,
            reason=reason,
            idempotency_key=idempotency_key,
        )

        retries = 0
        while retries < self.max_retries:
            retries += 1
            ok, failure_reason = self._send_to_device(device_id=device_id, action=action)
            if ok:
                sent = self.repository.update_command_status(command["id"], "sent")
                return {
                    "status": "sent",
                    "command": sent,
                    "transport": "simulated_modbus_or_mqtt",
                    "retries": retries,
                }

        failed = self.repository.update_command_status(command["id"], "failed", failure_reason=failure_reason)
        return {
            "status": "failed",
            "command": failed,
            "transport": "simulated_modbus_or_mqtt",
            "retries": retries,
            "failure_reason": failure_reason,
        }

    @staticmethod
    def _send_to_device(device_id: str, action: ScoredAction) -> tuple[bool, str | None]:
        if not device_id:
            return False, "missing_device_id"
        if action.target_power_kw < 0:
            return False, "invalid_target_power"
        return True, None
