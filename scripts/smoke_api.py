# Author: Jerry Onyango
# Contribution: Executes an authenticated API smoke test across onboarding, ingestion, modeling, and recommendation routes.
import os

from fastapi.testclient import TestClient

os.environ.setdefault("EA_ENV", "development")
os.environ.setdefault("EA_ENABLE_DEV_AUTH", "true")
os.environ.setdefault("EA_JWT_SECRET", "dev-secret-change-me-at-least-32-bytes")
os.environ.setdefault("EA_HOLDOUT_MAPE_RETRAIN_THRESHOLD", "0.005")
os.environ.setdefault("EA_ALLOW_WEAK_JWT_SECRET", "false")
os.environ.setdefault("EA_DATABASE_URL", "postgresql://energyallocation:energyallocation@localhost:5432/energyallocation")
os.environ.setdefault("EA_STORE_BACKEND", "postgres")

from energy_api.main import app


client = TestClient(app)

admin_token = client.post(
    "/v1/auth/dev-token",
    json={"sub": "usr_admin", "roles": ["client_admin", "energy_analyst"], "client_id": "cli_001"},
).json()["access_token"]
auth_headers = {"Authorization": f"Bearer {admin_token}"}

checks = []
checks.append(("health", client.get("/health").status_code))
checks.append(("contract", client.get("/openapi.v1.yaml").status_code))

facility = client.post(
    "/v1/clients/cli_001/facilities",
    json={
        "name": "Duisburg Plant A",
        "country": "DE",
        "site_type": "manufacturing",
        "production_profile": "24_7_heavy_industrial",
        "timezone": "Europe/Berlin",
    },
    headers=auth_headers,
)
checks.append(("create_facility", facility.status_code))
fac_id = facility.json()["facility_id"]

imp = client.post(
    f"/v1/facilities/{fac_id}/ingestion/imports",
    headers={**auth_headers, "Idempotency-Key": "abc12345"},
    json={
        "type": "csv",
        "file_id": "fil_hist_2025q4",
        "schema_hint": "timestamp,power_kw,channel_id",
        "time_column": "timestamp",
    },
)
checks.append(("submit_import", imp.status_code))
imp_id = imp.json()["import_id"]

imp_status = client.get(f"/v1/ingestion/imports/{imp_id}", headers=auth_headers)
checks.append(("import_status", imp_status.status_code))

model = client.post(
    f"/v1/facilities/{fac_id}/models/runs",
    json={
        "feature_set_version": "fs_v12",
        "model_family": "xgboost_iforest_ensemble",
        "objective": "savings_recommendation",
        "explainability": True,
    },
    headers=auth_headers,
)
checks.append(("model_run", model.status_code))

model_detail = client.get(f"/v1/models/runs/{model.json()['model_run_id']}", headers=auth_headers)
checks.append(("model_detail", model_detail.status_code))

recs = client.get(f"/v1/facilities/{fac_id}/recommendations?status=active", headers=auth_headers)
checks.append(("recommendations", recs.status_code))

drift = client.get(f"/v1/facilities/{fac_id}/drift-events", headers=auth_headers)
checks.append(("drift_events", drift.status_code))

alerts = client.get(f"/v1/facilities/{fac_id}/alerts?status=open", headers=auth_headers)
checks.append(("alerts", alerts.status_code))

retraining_jobs = client.get(f"/v1/facilities/{fac_id}/retraining-jobs", headers=auth_headers)
checks.append(("retraining_jobs", retraining_jobs.status_code))

demo_req = client.post(
    "/v1/public/demo-requests",
    json={"company": "Acme Steel", "contact_name": "Jordan Lee", "email": "jordan@acme.example", "facilities_count": 6},
)
checks.append(("demo_request", demo_req.status_code))

pricing_req = client.post(
    "/v1/public/pricing-inquiries",
    json={"company": "Acme Steel", "contact_name": "Jordan Lee", "email": "jordan@acme.example", "requested_plan": "enterprise"},
)
checks.append(("pricing_inquiry", pricing_req.status_code))

print(checks)
print(
    {
        "facility_id": fac_id,
        "import_status": imp_status.json()["status"],
        "model_run_id": model.json()["model_run_id"],
        "training_rows": model_detail.json()["validation"]["training_rows"],
        "holdout_mae_kw": model_detail.json()["validation"]["holdout_mae_kw"],
        "holdout_mape": model_detail.json()["validation"]["holdout_mape"],
        "retraining_triggered": model_detail.json()["retraining_triggered"],
        "retraining_jobs_count": len(retraining_jobs.json()["items"]),
        "drift_events_count": len(drift.json()["items"]),
        "alerts_count": len(alerts.json()["items"]),
        "demo_request_id": demo_req.json()["request_id"],
        "pricing_inquiry_id": pricing_req.json()["inquiry_id"],
        "recommendations_generated": model_detail.json()["recommendations_generated"],
    }
)
