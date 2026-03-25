# Author: Jerry Onyango
# Contribution: Orchestrates feature jobs and model runs, and exposes model details from the training-prediction pipeline.
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from energy_api.audit import record_audit_event
from energy_api.security import enforce_facility_scope, require_roles
from energy_api.services.retraining_service import RetrainingService
from energy_api.store import store
from ml_pipeline import ProductionBatchEnergyModel, load_training_rows

router = APIRouter(prefix="/v1", tags=["Modeling"])


@router.post("/facilities/{facility_id}/features/materialize", status_code=202)
def materialize_features(
    facility_id: str,
    payload: dict[str, Any],
    _principal: dict[str, Any] = Depends(require_roles("facility_manager", "energy_analyst", "ml_engineer")),
) -> dict[str, str]:
    facility = store.facilities.get(facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="facility not found")
    enforce_facility_scope(_principal, facility_id, facility.get("client_id"))

    job = store.make_async_job("feat", {"facility_id": facility_id, "request": payload})
    store.feature_jobs[job["job_id"]] = job
    return {"job_id": job["job_id"], "status": "queued"}


@router.post("/facilities/{facility_id}/models/runs", status_code=202)
def start_model_run(
    facility_id: str,
    payload: dict[str, Any],
    _principal: dict[str, Any] = Depends(require_roles("energy_analyst", "facility_manager", "ml_engineer")),
) -> dict[str, Any]:
    facility = store.facilities.get(facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail="facility not found")
    enforce_facility_scope(_principal, facility_id, facility.get("client_id"))

    model_run_id = store.make_id("mr")
    model_run = {
        "model_run_id": model_run_id,
        "facility_id": facility_id,
        "request": payload,
        "status": "queued",
        "feature_rows": 118240,
        "model_version": "mdl_prod_batch_1.0.0",
        "pipeline": None,
    }
    store.model_runs[model_run_id] = model_run
    record_audit_event(
        action="model_run_started",
        principal=_principal,
        resource_type="model_run",
        resource_id=model_run_id,
        metadata={"facility_id": facility_id, "model_family": payload.get("model_family")},
    )
    return model_run


@router.get("/models/runs/{model_run_id}")
def get_model_run(
    model_run_id: str,
    _principal: dict[str, Any] = Depends(require_roles("energy_analyst", "facility_manager", "viewer", "ml_engineer")),
) -> dict[str, Any]:
    model_run = store.model_runs.get(model_run_id)
    if not model_run:
        raise HTTPException(status_code=404, detail="model run not found")

    facility = store.facilities.get(model_run["facility_id"])
    enforce_facility_scope(_principal, model_run["facility_id"], facility.get("client_id") if facility else None)

    if model_run["status"] == "queued":
        root = Path(__file__).resolve().parents[3]
        rows = load_training_rows(root / "data" / "sample_training_readings.csv")
        split_idx = max(1, int(len(rows) * 0.8))
        train_rows = rows[:split_idx]
        holdout_rows = rows[split_idx:] if split_idx < len(rows) else rows

        pipeline = ProductionBatchEnergyModel()
        pipeline.fit_in_batches(train_rows, batch_size=4)

        train_metrics = pipeline.evaluate(train_rows)
        holdout_metrics = pipeline.evaluate(holdout_rows)
        suggestions = pipeline.suggest(holdout_rows)

        artifact_dir = root / "artifacts" / "models"
        artifact_path = pipeline.save(artifact_dir / f"{model_run_id}.json")

        holdout_mape = float(holdout_metrics["mape"])
        retrain_threshold = float(os.getenv("EA_HOLDOUT_MAPE_RETRAIN_THRESHOLD", "0.08"))
        retraining_service = RetrainingService()
        retraining_decision = retraining_service.evaluate(holdout_mape=holdout_mape, threshold=retrain_threshold)
        retraining_triggered = retraining_decision.triggered
        drift_event_id = None
        retraining_job_id = None
        if retraining_triggered:
            drift_event_id = store.make_id("de")
            store.drift_events[drift_event_id] = {
                "drift_event_id": drift_event_id,
                "facility_id": model_run["facility_id"],
                "feature_distribution_change": "holdout_error_elevated",
                "monitored_segment": "model_quality",
                "threshold_breached": retrain_threshold,
                "affected_model": model_run["model_version"],
                "retraining_action": "triggered",
                "holdout_mape": holdout_mape,
            }

            alert_id = store.make_id("alt")
            store.alerts[alert_id] = {
                "alert_id": alert_id,
                "source_type": "model",
                "source_id": model_run_id,
                "facility_id": model_run["facility_id"],
                "client_id": facility.get("client_id") if facility else "unknown",
                "severity": "high",
                "state": "open",
                "owner_role": "ml_engineer",
                "routing_policy": "retraining_threshold_breach_v1",
                "sla_minutes": 120,
                "dedupe_key": f"{model_run['facility_id']}:{model_run_id}:retraining",
            }

            retraining_job = retraining_service.queue(
                facility_id=model_run["facility_id"],
                model_run_id=model_run_id,
                threshold=retrain_threshold,
                observed=holdout_mape,
                reason="holdout_mape_threshold_breached",
            )
            retraining_job["drift_event_id"] = drift_event_id
            store.retraining_jobs[retraining_job["job_id"]] = retraining_job
            retraining_job_id = str(retraining_job["job_id"])

        model_run["status"] = "completed"
        model_run["pipeline"] = {
            "train_metrics": train_metrics,
            "holdout_metrics": holdout_metrics,
            "suggestions": suggestions,
            "artifact_path": str(artifact_path),
            "retraining_triggered": retraining_triggered,
            "retraining_job_id": retraining_job_id,
            "drift_event_id": drift_event_id,
            "retraining_threshold": retrain_threshold,
            "training_window": {
                "start": rows[0].timestamp,
                "end": rows[-1].timestamp,
            },
        }
        record_audit_event(
            action="model_run_completed",
            principal=_principal,
            resource_type="model_run",
            resource_id=model_run_id,
            metadata={
                "facility_id": model_run["facility_id"],
                "holdout_mape": holdout_mape,
                "retraining_triggered": retraining_triggered,
                "artifact_path": str(artifact_path),
            },
        )

    return {
        "model_run_id": model_run_id,
        "model_version": model_run["model_version"],
        "training_window": {
            "start": model_run["pipeline"]["training_window"]["start"],
            "end": model_run["pipeline"]["training_window"]["end"],
        },
        "validation": {
            "train_mae_kw": model_run["pipeline"]["train_metrics"]["mae_kw"],
            "train_mape": model_run["pipeline"]["train_metrics"]["mape"],
            "holdout_mae_kw": model_run["pipeline"]["holdout_metrics"]["mae_kw"],
            "holdout_mape": model_run["pipeline"]["holdout_metrics"]["mape"],
            "training_rows": model_run["pipeline"]["train_metrics"]["rows"],
        },
        "selected_hyperparameters": {
            "strategy": "hierarchical_batch_means",
            "fallback": "global_mean_backoff",
            "batch_size": 4,
        },
        "drift_baseline_id": "db_2025q4_v3",
        "shap_artifacts": [
            "https://artifacts.energyallocation.local/shap/mr_001_top_features.json"
        ],
        "anomaly_summary": {
            "total_anomalies": 0,
            "top_segment": "none",
        },
        "model_artifact_path": model_run["pipeline"]["artifact_path"],
        "retraining_triggered": model_run["pipeline"]["retraining_triggered"],
        "retraining_job_id": model_run["pipeline"]["retraining_job_id"],
        "drift_event_id": model_run["pipeline"]["drift_event_id"],
        "retraining_threshold": model_run["pipeline"]["retraining_threshold"],
        "recommendations_generated": len(model_run["pipeline"]["suggestions"]),
    }
