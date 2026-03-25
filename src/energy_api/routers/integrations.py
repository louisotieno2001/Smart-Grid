# Author: Jerry Onyango
# Contribution: Manages outbound webhook subscription creation for client integrations.
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends

from energy_api.security import enforce_client_scope, require_roles
from energy_api.store import store

router = APIRouter(prefix="/v1", tags=["Integrations"])


@router.post("/webhooks/subscriptions", status_code=201)
def create_webhook_subscription(
    payload: dict[str, Any],
    _principal: dict[str, Any] = Depends(require_roles("client_admin", "ops_admin", "customer_success")),
) -> dict[str, str]:
    client_id = payload.get("client_id")
    if client_id:
        enforce_client_scope(_principal, client_id)

    webhook_id = store.make_id("wh")
    store.webhooks[webhook_id] = {
        "id": webhook_id,
        "status": "active",
        "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "payload": payload,
    }
    return {
        "webhook_id": webhook_id,
        "status": "active",
        "created_at": store.webhooks[webhook_id]["created_at"],
    }
