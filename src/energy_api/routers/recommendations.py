# Author: Jerry Onyango
# Contribution: Serves recommendation listing, decision capture, and implementation recording workflows.
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from energy_api.audit import record_audit_event
from energy_api.security import enforce_facility_scope, require_roles
from energy_api.store import store

router = APIRouter(prefix="/v1", tags=["Recommendations"])


@router.get("/facilities/{facility_id}/recommendations")
def list_recommendations(
    facility_id: str,
    status: str = "active",
    sort: str = "projected_savings_desc",
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
        {
            "recommendation_id": "rec_7881",
            "appliance_id": "app_3301",
            "facility_id": facility_id,
            "title": "Reduce off-shift compressor idle runtime",
            "projected_annual_savings_eur": 84200,
            "confidence": 0.91,
            "effort": "medium",
            "payback_months": 4.2,
            "implementation_readiness": 0.82,
            "status": status,
        }
    ]
    for item in items:
        store.recommendations[item["recommendation_id"]] = item

    return {
        "items": items[:limit],
        "total_projected_savings_eur": 284000,
        "next_cursor": cursor,
        "sort": sort,
    }


@router.post("/recommendations/{recommendation_id}/decision")
def decide_recommendation(
    recommendation_id: str,
    payload: dict[str, Any],
    _principal: dict[str, Any] = Depends(require_roles("facility_manager", "client_admin", "ops_admin")),
) -> dict[str, Any]:
    recommendation = store.recommendations.get(recommendation_id)
    if not recommendation:
        recommendation = {
            "recommendation_id": recommendation_id,
            "appliance_id": "app_unknown",
            "title": "Unknown recommendation",
            "status": "active",
        }

    facility_id = recommendation.get("facility_id")
    if facility_id:
        facility = store.facilities.get(facility_id)
        enforce_facility_scope(_principal, facility_id, facility.get("client_id") if facility else None)

    decision = payload.get("decision", "accepted")
    recommendation["status"] = "accepted" if decision == "accepted" else "rejected"
    recommendation["decision"] = payload
    store.recommendations[recommendation_id] = recommendation
    record_audit_event(
        action="recommendation_decision_recorded",
        principal=_principal,
        resource_type="recommendation",
        resource_id=recommendation_id,
        metadata={"decision": decision, "facility_id": recommendation.get("facility_id")},
    )
    return recommendation


@router.post("/recommendations/{recommendation_id}/implementations", status_code=201)
def record_implementation(
    recommendation_id: str,
    payload: dict[str, Any],
    _principal: dict[str, Any] = Depends(require_roles("facility_manager", "client_admin", "ops_admin")),
) -> dict[str, str]:
    if recommendation_id not in store.recommendations:
        raise HTTPException(status_code=404, detail="recommendation not found")

    recommendation = store.recommendations[recommendation_id]
    facility_id = recommendation.get("facility_id")
    if facility_id:
        facility = store.facilities.get(facility_id)
        enforce_facility_scope(_principal, facility_id, facility.get("client_id") if facility else None)

    job = store.make_async_job("impl", {"recommendation_id": recommendation_id, "request": payload})
    record_audit_event(
        action="recommendation_implementation_recorded",
        principal=_principal,
        resource_type="implementation_job",
        resource_id=job["job_id"],
        metadata={"recommendation_id": recommendation_id},
    )
    return {"job_id": job["job_id"], "status": "queued"}
