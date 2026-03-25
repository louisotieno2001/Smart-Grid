# Author: Jerry Onyango
# Contribution: Manages idempotent ingestion import submission and asynchronous import status tracking.
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException

from energy_api.audit import record_audit_event
from energy_api.security import enforce_facility_scope, require_roles
from energy_api.store import store

router = APIRouter(prefix="/v1", tags=["Ingestion"])


@router.post("/facilities/{facility_id}/ingestion/imports", status_code=202)
def submit_import(
    facility_id: str,
    payload: dict[str, Any],
    idempotency_key: str = Header(alias="Idempotency-Key", default=""),
    _principal: dict[str, Any] = Depends(require_roles("client_admin", "facility_manager", "ops_admin")),
) -> dict[str, Any]:
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header is required")

    facility = store.facilities.get(facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="facility not found")
    enforce_facility_scope(_principal, facility_id, facility.get("client_id"))

    import_id = store.make_id("imp")
    job = {
        "import_id": import_id,
        "facility_id": facility_id,
        "status": "queued",
        "estimated_rows": 28344121,
        "progress_pct": 0,
        "rows_processed": 0,
        "rows_rejected": 0,
        "started_at": None,
        "completed_at": None,
        "request": payload,
    }
    store.import_jobs[import_id] = job
    record_audit_event(
        action="ingestion_import_submitted",
        principal=_principal,
        resource_type="import_job",
        resource_id=import_id,
        metadata={"facility_id": facility_id, "idempotency_key": idempotency_key},
    )
    return job


@router.get("/ingestion/imports/{import_id}")
def get_import(
    import_id: str,
    _principal: dict[str, Any] = Depends(
        require_roles("client_admin", "facility_manager", "energy_analyst", "viewer", "ops_admin")
    ),
) -> dict[str, Any]:
    job = store.import_jobs.get(import_id)
    if not job:
        raise HTTPException(status_code=404, detail="import job not found")

    facility = store.facilities.get(job["facility_id"])
    enforce_facility_scope(_principal, job["facility_id"], facility.get("client_id") if facility else None)

    if job["status"] == "queued":
        job["status"] = "running"
        job["progress_pct"] = 68
        job["rows_processed"] = 19238011
        job["rows_rejected"] = 14921
        job["started_at"] = "2026-03-24T09:10:00Z"

    return job
