# Author: Jerry Onyango
# Contribution: Handles onboarding flows for facilities, connectors, channels, and appliance mappings.
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from energy_api.audit import record_audit_event
from energy_api.security import enforce_client_scope, enforce_facility_scope, require_roles
from energy_api.store import store

router = APIRouter(prefix="/v1", tags=["Onboarding"])


@router.get("/clients/{client_id}/facilities")
def list_facilities(
    client_id: str,
    status: str | None = None,
    limit: int = 50,
    cursor: str | None = None,
    _principal: dict[str, Any] = Depends(
        require_roles("client_admin", "facility_manager", "energy_analyst", "viewer", "ops_admin")
    ),
) -> dict[str, Any]:
    enforce_client_scope(_principal, client_id)
    items = [
        item
        for item in store.facilities.values()
        if item.get("client_id") == client_id and (status is None or item.get("status") == status)
    ]
    return {"items": items[:limit], "next_cursor": cursor}


@router.post("/clients/{client_id}/facilities", status_code=201)
def create_facility(
    client_id: str,
    payload: dict[str, Any],
    _principal: dict[str, Any] = Depends(require_roles("client_admin", "ops_admin")),
) -> dict[str, str]:
    enforce_client_scope(_principal, client_id)
    facility_id = store.make_id("fac")
    store.facilities[facility_id] = {
        "id": facility_id,
        "client_id": client_id,
        "status": "draft",
        **payload,
    }
    record_audit_event(
        action="facility_created",
        principal=_principal,
        resource_type="facility",
        resource_id=facility_id,
        metadata={"client_id": client_id, "name": payload.get("name")},
    )
    return {
        "facility_id": facility_id,
        "status": "draft",
        "next_step": "attach_connectors",
    }


@router.post("/facilities/{facility_id}/connectors", status_code=201)
def attach_connector(
    facility_id: str,
    payload: dict[str, Any],
    _principal: dict[str, Any] = Depends(require_roles("client_admin", "facility_manager", "ops_admin")),
) -> dict[str, Any]:
    facility = store.facilities.get(facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="facility not found")
    enforce_facility_scope(_principal, facility_id, facility.get("client_id"))

    connector_id = store.make_id("con")
    connector = {
        "id": connector_id,
        "facility_id": facility_id,
        "type": payload.get("type", "unknown"),
        "vendor": payload.get("vendor"),
        "source_name": payload.get("display_name", payload.get("source_name")),
        "status": "healthy",
        "last_sync_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    store.connectors[connector_id] = connector
    record_audit_event(
        action="connector_attached",
        principal=_principal,
        resource_type="connector",
        resource_id=connector_id,
        metadata={"facility_id": facility_id, "type": connector.get("type")},
    )
    return connector


@router.post("/connectors/{connector_id}/validate")
def validate_connector(
    connector_id: str,
    _principal: dict[str, Any] = Depends(require_roles("client_admin", "facility_manager", "ops_admin")),
) -> dict[str, Any]:
    connector = store.connectors.get(connector_id)
    if connector:
        facility_id = connector.get("facility_id")
        facility = store.facilities.get(facility_id)
        if facility_id:
            enforce_facility_scope(_principal, facility_id, facility.get("client_id") if facility else None)

    return {
        "connector_id": connector_id,
        "status": "healthy",
        "channels_detected": 148,
        "sample_window_minutes": 15,
        "issues": [],
    }


@router.get("/connectors/{connector_id}/channels")
def list_channels(
    connector_id: str,
    limit: int = 50,
    cursor: str | None = None,
    _principal: dict[str, Any] = Depends(
        require_roles("client_admin", "facility_manager", "energy_analyst", "viewer", "ops_admin")
    ),
) -> dict[str, Any]:
    connector = store.connectors.get(connector_id)
    if connector:
        facility_id = connector.get("facility_id")
        facility = store.facilities.get(facility_id)
        if facility_id:
            enforce_facility_scope(_principal, facility_id, facility.get("client_id") if facility else None)

    items = [
        {
            "channel_id": "chn_9001",
            "label": "Main Compressor Line 3 Power",
            "unit": "kW",
            "quality_score": 0.97,
            "sampling_interval_sec": 60,
        },
        {
            "channel_id": "chn_9002",
            "label": "Main Compressor Line 3 Runtime",
            "unit": "state",
            "quality_score": 0.94,
            "sampling_interval_sec": 60,
        },
    ]
    return {"items": items[:limit], "next_cursor": cursor}


@router.post("/facilities/{facility_id}/appliances", status_code=201)
def create_appliance(
    facility_id: str,
    payload: dict[str, Any],
    _principal: dict[str, Any] = Depends(require_roles("client_admin", "facility_manager", "ops_admin")),
) -> dict[str, Any]:
    facility = store.facilities.get(facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="facility not found")
    enforce_facility_scope(_principal, facility_id, facility.get("client_id"))

    appliance_id = store.make_id("app")
    appliance = {
        "id": appliance_id,
        "facility_id": facility_id,
        "name": payload.get("name"),
        "category": payload.get("category"),
        "subtype": payload.get("subtype"),
        "rated_power_kw": payload.get("rated_power_kw", 0),
        "control_mode": payload.get("control_mode", "unknown"),
        "zone": payload.get("zone"),
        "status": "active",
    }
    store.appliances[appliance_id] = appliance
    record_audit_event(
        action="appliance_created",
        principal=_principal,
        resource_type="appliance",
        resource_id=appliance_id,
        metadata={"facility_id": facility_id, "category": appliance.get("category")},
    )
    return appliance
