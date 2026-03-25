# Author: Jerry Onyango
# Contribution: Exposes savings, alert, and drift monitoring endpoints with tenant-aware access controls.
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from energy_api.audit import record_audit_event
from energy_api.security import enforce_facility_scope, require_roles
from energy_api.store import store

router = APIRouter(prefix="/v1", tags=["Monitoring"])


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@router.get("/facilities/{facility_id}/savings")
def get_savings(
    facility_id: str,
    from_: str | None = Query(default=None, alias="from"),
    to: str | None = None,
    _principal: dict[str, Any] = Depends(
        require_roles("client_admin", "facility_manager", "energy_analyst", "viewer", "ops_admin")
    ),
) -> dict[str, Any]:
    facility = store.facilities.get(facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="facility not found")
    enforce_facility_scope(_principal, facility_id, facility.get("client_id"))

    return {
        "projected_savings_eur": 71200,
        "realized_savings_eur": 65510,
        "realization_rate": 0.92,
        "by_appliance": [
            {
                "appliance_id": "app_3301",
                "projected_eur": 21000,
                "realized_eur": 18440,
            }
        ],
        "window": {"from": from_, "to": to, "facility_id": facility_id},
    }


@router.get("/facilities/{facility_id}/alerts")
def list_alerts(
    facility_id: str,
    status: str = "open",
    severity: str | None = None,
    limit: int = 50,
    cursor: str | None = None,
    _principal: dict[str, Any] = Depends(
        require_roles("client_admin", "facility_manager", "energy_analyst", "viewer", "ops_admin")
    ),
) -> dict[str, Any]:
    facility = store.facilities.get(facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="facility not found")
    enforce_facility_scope(_principal, facility_id, facility.get("client_id"))

    items = [
        alert
        for alert in store.alerts.values()
        if alert.get("facility_id") == facility_id
        and (status is None or alert.get("state") == status)
        and (severity is None or alert.get("severity") == severity)
    ]
    if not items:
        demo_alert = {
            "alert_id": "alt_8801",
            "source_type": "connector",
            "source_id": "con_444",
            "facility_id": facility_id,
            "client_id": facility.get("client_id", "cli_001"),
            "severity": severity or "high",
            "state": status,
            "owner_role": "facility_manager",
            "routing_policy": "critical_connector_outage_v1",
            "sla_minutes": 30,
            "dedupe_key": f"{facility_id}:con_444:offline",
        }
        store.alerts[demo_alert["alert_id"]] = demo_alert
        items = [demo_alert]
    return {"items": items[:limit], "next_cursor": cursor}


@router.get("/facilities/{facility_id}/drift-events")
def list_drift_events(
    facility_id: str,
    limit: int = 50,
    cursor: str | None = None,
    _principal: dict[str, Any] = Depends(
        require_roles("client_admin", "facility_manager", "energy_analyst", "viewer", "ml_engineer")
    ),
) -> dict[str, Any]:
    facility = store.facilities.get(facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="facility not found")
    enforce_facility_scope(_principal, facility_id, facility.get("client_id"))

    items = [event for event in store.drift_events.values() if event.get("facility_id") == facility_id]
    if not items:
        items = [
            {
                "drift_event_id": "de_9911",
                "feature_distribution_change": "runtime_patterns shifted vs baseline",
                "monitored_segment": "runtime_patterns",
                "threshold_breached": 0.2,
                "affected_model": "mdl_2.7.1",
                "retraining_action": "pending",
                "facility_id": facility_id,
            }
        ]
    return {"items": items[:limit], "next_cursor": cursor}


@router.get("/facilities/{facility_id}/retraining-jobs")
def list_retraining_jobs(
    facility_id: str,
    status: str | None = None,
    limit: int = 50,
    cursor: str | None = None,
    _principal: dict[str, Any] = Depends(
        require_roles("client_admin", "facility_manager", "energy_analyst", "viewer", "ml_engineer", "ops_admin")
    ),
) -> dict[str, Any]:
    facility = store.facilities.get(facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="facility not found")
    enforce_facility_scope(_principal, facility_id, facility.get("client_id"))

    items = [
        job
        for job in store.retraining_jobs.values()
        if job.get("facility_id") == facility_id and (status is None or job.get("status") == status)
    ]
    return {"items": items[:limit], "next_cursor": cursor}


@router.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: str,
    payload: dict[str, Any],
    _principal: dict[str, Any] = Depends(require_roles("facility_manager", "ops_admin", "support_analyst", "ml_engineer")),
) -> dict[str, Any]:
    alert = store.alerts.get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="alert not found")

    facility = store.facilities.get(alert.get("facility_id"))
    if alert.get("facility_id"):
        enforce_facility_scope(_principal, alert["facility_id"], facility.get("client_id") if facility else None)

    alert["state"] = "acknowledged"
    alert["acknowledged_by"] = _principal.subject
    alert["acknowledged_at"] = _now_iso()
    if payload.get("note"):
        alert["acknowledge_note"] = payload["note"]

    record_audit_event(
        action="alert_acknowledged",
        principal=_principal,
        resource_type="alert",
        resource_id=alert_id,
        metadata={"facility_id": alert.get("facility_id"), "note": payload.get("note")},
    )
    return alert


@router.post("/alerts/{alert_id}/incident")
def open_alert_incident(
    alert_id: str,
    payload: dict[str, Any],
    _principal: dict[str, Any] = Depends(require_roles("facility_manager", "ops_admin", "support_analyst", "ml_engineer")),
) -> dict[str, Any]:
    alert = store.alerts.get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="alert not found")

    facility = store.facilities.get(alert.get("facility_id"))
    if alert.get("facility_id"):
        enforce_facility_scope(_principal, alert["facility_id"], facility.get("client_id") if facility else None)

    incident_id = store.make_id("inc")
    alert["incident_id"] = incident_id
    alert["state"] = "investigating"
    alert["incident_opened_by"] = _principal.subject
    alert["incident_opened_at"] = _now_iso()

    record_audit_event(
        action="incident_opened_from_alert",
        principal=_principal,
        resource_type="alert",
        resource_id=alert_id,
        metadata={"incident_id": incident_id, "facility_id": alert.get("facility_id"), "note": payload.get("note")},
    )
    return {"incident_id": incident_id, "alert_id": alert_id, "status": "open"}
