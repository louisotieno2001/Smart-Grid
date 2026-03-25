# Author: Jerry Onyango
# Contribution: Implements retraining decision policy and queue record creation logic for model quality operations.
from __future__ import annotations

from dataclasses import dataclass

from energy_api.repositories.retraining_repository import RetrainingRepository


@dataclass(frozen=True)
class RetrainingDecision:
    triggered: bool
    threshold: float
    observed: float


class RetrainingService:
    def __init__(self, repository: RetrainingRepository | None = None) -> None:
        self.repository = repository or RetrainingRepository()

    def evaluate(self, holdout_mape: float, threshold: float) -> RetrainingDecision:
        return RetrainingDecision(
            triggered=holdout_mape > threshold,
            threshold=threshold,
            observed=holdout_mape,
        )

    def queue(self, facility_id: str, model_run_id: str, threshold: float, observed: float, reason: str) -> dict[str, object]:
        return self.repository.upsert(
            {
                "facility_id": facility_id,
                "model_run_id": model_run_id,
                "status": "queued",
                "reason": reason,
                "threshold": threshold,
                "observed_holdout_mape": observed,
            }
        )
