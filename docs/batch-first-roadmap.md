# Batch-First Now, Streaming Later

## Current production truth
EnergyAllocation is a batch-first ML platform in v1:
- async imports/backfills
- scheduled feature materialization
- scheduled model runs and scoring
- persisted artifacts and model metrics
- recommendations and monitoring surfaced via API/UI

## Why this is correct for early industrial deployments
- Most pilot customers onboard historical interval data first.
- Governance and auditability are easier with deterministic batch windows.
- Operational teams review recommendations on daily/weekly cadences.
- Reliability and explainability matter more than low-latency inference in v1.

## Near-term batch cadence
- nightly feature jobs
- daily scoring and recommendation refresh
- weekly retraining with quality gate checks
- trigger-based retraining when holdout MAPE threshold is breached

## Streaming roadmap (future)
Not part of current core runtime:
- event-driven ingestion
- incremental feature updates
- online anomaly detection
- low-latency inference APIs

These should be introduced after tenant onboarding, quality baselines, and operational playbooks are stable.
