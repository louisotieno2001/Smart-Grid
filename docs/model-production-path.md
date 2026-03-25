# Model Production Path

## Goal
Move from prototype prediction to repeatable, batch-trainable model operations with reusable artifacts.

## Current Production Workflow
1. Ingest rows into CSV/object storage partitions by facility/date.
2. Train model in batches using:
   - `scripts/train_batch_model.py`
   - chunked updates via `fit_batch`/`fit_in_batches`
3. Persist versioned artifact JSON in `artifacts/models/`.
4. Load artifact for prediction/evaluation with:
   - `scripts/predict_batch_model.py`
5. API model runs in `GET /v1/models/runs/{model_run_id}` train on first access, save artifact, and return holdout metrics.
6. Automatic retraining trigger fires when holdout MAPE exceeds configured threshold.

## Automatic Retraining Trigger
- Threshold setting: `EA_HOLDOUT_MAPE_RETRAIN_THRESHOLD` (default `0.08`).
- Trigger condition: `holdout_mape > threshold`.
- On trigger, the system automatically:
   - creates a drift event (`feature_distribution_change=holdout_error_elevated`)
   - opens a high-severity model alert owned by `ml_engineer`
   - creates a queued retraining job record
- Trigger outputs are visible via:
   - `GET /v1/models/runs/{model_run_id}` (`retraining_triggered`, `retraining_job_id`, `drift_event_id`)
   - `GET /v1/facilities/{facility_id}/drift-events`
   - `GET /v1/facilities/{facility_id}/alerts`

## Why this is production-oriented
- Incremental batch training supports larger datasets.
- Artifact persistence decouples training from inference.
- Hierarchical fallback keys reduce prediction failures for sparse segments.
- Holdout metrics are surfaced for runtime quality checks.

## Suggested Batch Strategy
- Nightly retrain per facility with full last-90-day data window.
- Hourly mini-batch update for recent operational drift signals.
- Weekly champion-challenger comparison before promotion.

## Data Inputs That Improve Accuracy
- Meter/channel power and runtime state
- Tariff schedule by time-of-use
- Ambient and process temperature
- Shift calendar and maintenance windows
- Production throughput/load indicators

## Promotion Guardrails
Promote only when all pass:
- holdout MAPE below threshold (e.g. < 10-12%)
- no severe drift events in monitored feature groups
- recommendation acceptance quality stable or improving
