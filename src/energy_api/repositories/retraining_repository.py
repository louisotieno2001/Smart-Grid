# Author: Jerry Onyango
# Contribution: Encapsulates retraining-job query patterns for service-layer orchestration and future database adapters.
from __future__ import annotations

from typing import Any

from energy_api.store import store


class RetrainingRepository:
    def list_by_facility(self, facility_id: str, status: str | None = None) -> list[dict[str, Any]]:
        return [
            item
            for item in store.retraining_jobs.values()
            if item.get("facility_id") == facility_id and (status is None or item.get("status") == status)
        ]

    def upsert(self, payload: dict[str, Any]) -> dict[str, Any]:
        job_id = payload.get("job_id") or store.make_id("rt")
        output = {"job_id": job_id, **payload}
        store.retraining_jobs[job_id] = output
        return output
