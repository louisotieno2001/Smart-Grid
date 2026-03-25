# Author: Jerry Onyango
# Contribution: Exposes public business endpoints for request-demo and pricing inquiry capture with audit trails.
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter

from energy_api.audit import record_audit_event
from energy_api.store import store

router = APIRouter(prefix="/v1/public", tags=["Public"])


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@router.post("/demo-requests", status_code=201)
def request_demo(payload: dict[str, Any]) -> dict[str, Any]:
    request_id = store.make_id("demo")
    item = {
        "request_id": request_id,
        "status": "new",
        "created_at": _now_iso(),
        "payload": payload,
    }
    store.demo_requests[request_id] = item
    record_audit_event(
        action="demo_request_created",
        principal=None,
        resource_type="demo_request",
        resource_id=request_id,
        metadata={"company": payload.get("company"), "email": payload.get("email")},
    )
    return item


@router.post("/pricing-inquiries", status_code=201)
def request_pricing(payload: dict[str, Any]) -> dict[str, Any]:
    inquiry_id = store.make_id("price")
    item = {
        "inquiry_id": inquiry_id,
        "status": "new",
        "created_at": _now_iso(),
        "payload": payload,
    }
    store.pricing_inquiries[inquiry_id] = item
    record_audit_event(
        action="pricing_inquiry_created",
        principal=None,
        resource_type="pricing_inquiry",
        resource_id=inquiry_id,
        metadata={"company": payload.get("company"), "email": payload.get("email")},
    )
    return item
