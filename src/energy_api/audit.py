# Author: Jerry Onyango
# Contribution: Provides consistent audit-event recording helpers for security-sensitive and operational write actions.
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from energy_api.security import Principal
from energy_api.store import store


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def record_audit_event(
    action: str,
    principal: Principal | None,
    resource_type: str,
    resource_id: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    event_id = store.make_id("aud")
    payload = {
        "audit_id": event_id,
        "occurred_at": _now_iso(),
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "actor_id": principal.subject if principal else "system",
        "actor_roles": sorted(list(principal.roles)) if principal else ["system"],
        "metadata": metadata or {},
    }
    store.audit_logs[event_id] = payload
    return payload
