# Energy Allocation Platform Foundation

This repository implements the three commercialization layers from your blueprint:
- API specification design (tenant-aware, async-heavy, traceable)
- Alerting and notification system design (taxonomy, lifecycle, routing, playbooks)
- Pricing and ROI calculator (with sensitivity bands)

## What is included
- `openapi/openapi.v1.yaml` — production-style v1 API contract
- `docs/alerting-system.md` — alert taxonomy, severity, lifecycle, dedupe, routing
- `docs/pricing-and-roi.md` — pricing model + calculator logic
- `docs/system-architecture.md` — deployment-ready system architecture blueprint
- `docs/backend-structure.md` — backend module layout and responsibilities
- `docs/data-model-and-migrations.md` — PostgreSQL schema and migration strategy
- `docs/rbac-auth.md` — auth and role model
- `docs/deployment.md` — deployment runbook
- `docs/batch-first-roadmap.md` — batch-now vs streaming-later positioning
- `docs/frontend-integration.md` — frontend-to-backend integration map
- `docs/partner-integration-api.md` — comprehensive third-party partner API guide
- `docs/partner-security-policy.md` — security requirements for partner integrations
- `docs/gap-analysis-and-upgrade.md` — prompt alignment and remaining roadmap gaps
- `src/roi_calculator/*` — runnable ROI calculator engine + CLI
- `src/energy_api/*` — FastAPI backend skeleton with contract-aligned route stubs
- `examples/roi_input_steel_6site.json` — sample six-site steel client inputs
- `ui/` — internal app + public site surfaces (landing, pricing, about, login/signup, request demo)

## ROI CLI usage
Install in editable mode:

```bash
pip install -e .
```

Run:

```bash
energy-roi --input examples/roi_input_steel_6site.json
```

Optional output file:

```bash
energy-roi --input examples/roi_input_steel_6site.json --output output/proposal.json
```

## API scaffold usage
Install dependencies:

```bash
pip install -e .
```

Run API server:

```bash
energy-api
```

Then open:
- `http://localhost:8000/docs` for interactive docs
- `http://localhost:8000/openapi.v1.yaml` to fetch the canonical contract file from this repo

Runtime persistence backend (PostgreSQL required):

The API requires PostgreSQL for all state persistence (entities, async jobs, app state). Docker Compose configuration is provided for local development:

```bash
docker-compose up -d
```

This starts Postgres (port 5432) and the API (port 8000) with automatic schema initialization.

Frontend API base (optional override):

```bash
export VITE_API_BASE_URL=http://localhost:8000
```

## Public business endpoints
- `POST /v1/public/demo-requests`
- `POST /v1/public/pricing-inquiries`

These support landing-page request flows and are audit-logged.

Internal and public UI buttons are wired to backend actions where endpoints exist (facility create, connector validate, import start, alert acknowledge/incident, demo/pricing requests).

Frontend-backend API flow smoke test:

```bash
.venv/bin/python scripts/smoke_frontend_backend.py
```

This validates the same backend routes used by the wired frontend buttons and forms.

## Partner Integration APIs

The platform provides comprehensive APIs for third-party partners to integrate their systems with Energy Allocation.

**Start here:** [Partner Quick Start Guide](PARTNER_QUICK_START.md) — 5-minute intro with copy-paste examples and patterns

**Full reference:** [Partner Integration API Guide](docs/partner-integration-api.md) — complete endpoint documentation

### Partner API Features

- **Partner Registration & Management** — Register partners, manage metadata, view usage
- **API Key Management** — Create, rotate, and revoke API keys with automatic 90-day expiration
- **Webhook Integration** — Register webhooks to receive real-time events (HMAC-SHA256 signed)
- **Client Allocation** — Assign partners to specific clients with granular access control
- **Audit Logging** — Complete audit trail of all partner actions and data access
- **Rate Limiting** — Tier-based rate limits with automatic backoff support

### Partner Test

Validate all partner integration endpoints:

```bash
.venv/bin/python scripts/smoke_partner_integrations.py
```

This test validates:
- Partner registration and deletion
- API key creation, rotation, revocation
- Webhook registration and updates
- Client allocations with scopes
- Audit log tracking
- Usage statistics

### Authorization

Partners must be registered and allocated to specific clients by internal ops_admin users. All partner actions require valid API keys with appropriate scopes. See [Partner Security Policy](docs/partner-security-policy.md) for security requirements.

### Example: Integrate Energy Recommendations

```python
import requests
import hmac
import hashlib
from datetime import datetime, timezone

api_key = "key_xxxxx:secret_yyyyy"
base_url = "https://api.energyallocation.com"

# Get facility recommendations
response = requests.get(
    f"{base_url}/v1/facilities/fac_001/recommendations?status=active",
    headers={"X-API-Key": api_key}
)
recommendations = response.json()["items"]

# Accept high-confidence recommendations
for rec in recommendations:
    if rec["confidence"] > 0.85:
        requests.post(
            f"{base_url}/v1/facilities/{rec['facility_id']}/recommendations/{rec['recommendation_id']}/decision",
            json={"status": "accepted", "note": "Auto-accepted via integration"},
            headers={"X-API-Key": api_key}
        )
```

## Production batch model workflow
Train model in batches and save artifact:

```bash
.venv/bin/python scripts/train_batch_model.py --input data/sample_training_readings.csv --output artifacts/models/prod_model.json --batch-size 4
```

Evaluate/predict from artifact:

```bash
.venv/bin/python scripts/predict_batch_model.py --model artifacts/models/prod_model.json --input data/sample_training_readings.csv
```

Optional retraining trigger threshold (default `0.08` holdout MAPE):

```bash
export EA_HOLDOUT_MAPE_RETRAIN_THRESHOLD=0.08
```

When breached during model-run evaluation, the API auto-creates drift + alert records and a queued retraining job.

## Security runtime controls
- Set `EA_JWT_SECRET` to a strong 32+ byte value in all environments.
- `EA_ENABLE_DEV_AUTH=false` disables `/v1/auth/dev-token` outside local development.
- `EA_CORS_ORIGINS` should be explicit trusted origins only (default is local Vite dev hosts).
- Use `EA_SERVICE_KEYS` for scoped machine access keys and rotate them regularly.

## CI branch protection
- Workflow [`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on pushes to `main` and on all pull requests.
- In GitHub repository settings, enable branch protection for `main` and require these status checks before merge:
	- `API smoke`
	- `Frontend-backend API smoke`
	- `Pipeline smoke`
	- `Frontend build`

## Database and deployment assets
- SQL migrations: `db/migrations/0001_init_schema.sql`, `db/migrations/0002_rls_policies.sql`
- Runtime state migration: `db/migrations/0003_app_state_store.sql`
- Runtime env template: `.env.example`
- Containerization: `Dockerfile`, `docker-compose.yml`

Implementation details: see `docs/model-production-path.md`.

## Pre-commit header enforcement
Install pre-commit and hooks:

```bash
.venv/bin/python -m pip install pre-commit
.venv/bin/pre-commit install
```

Run the header check manually:

```bash
.venv/bin/python scripts/check_file_headers.py
```

## Next implementation step
Wire the OpenAPI contract into a backend framework (FastAPI or NestJS), then map each async endpoint to queue-based workers and persistent stores defined in `docs/system-architecture.md`.
