# Author: Jerry Onyango
# Contribution: Validates frontend-wired API flows against backend endpoints for auth, onboarding, intake, monitoring, and public requests.
from __future__ import annotations

import os

os.environ.setdefault("EA_ENV", "development")
os.environ.setdefault("EA_ENABLE_DEV_AUTH", "true")
os.environ.setdefault("EA_JWT_SECRET", "dev-secret-change-me-at-least-32-bytes")
os.environ.setdefault("EA_ALLOW_WEAK_JWT_SECRET", "false")
os.environ.setdefault("EA_DATABASE_URL", "postgresql://energyallocation:energyallocation@localhost:5432/energyallocation")
os.environ.setdefault("EA_STORE_BACKEND", "postgres")

from fastapi.testclient import TestClient

from energy_api.main import app

client = TestClient(app)


def _auth_headers() -> dict[str, str]:
    token_response = client.post(
        "/v1/auth/dev-token",
        json={
            "sub": "ui_operator",
            "roles": ["client_admin", "facility_manager", "energy_analyst", "ops_admin", "ml_engineer"],
            "client_id": "cli_001",
        },
    )
    token_response.raise_for_status()
    token = token_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def main() -> None:
    headers = _auth_headers()
    checks: list[tuple[str, int]] = []

    facilities = client.get("/v1/clients/cli_001/facilities", headers=headers)
    checks.append(("list_facilities", facilities.status_code))
    facilities.raise_for_status()

    create_facility = client.post(
        "/v1/clients/cli_001/facilities",
        headers=headers,
        json={
            "name": "Frontend Smoke Facility",
            "country": "DE",
            "site_type": "manufacturing",
            "production_profile": "24_7_heavy_industrial",
            "timezone": "Europe/Berlin",
        },
    )
    checks.append(("create_facility", create_facility.status_code))
    create_facility.raise_for_status()
    facility_id = create_facility.json()["facility_id"]

    connector = client.post(
        f"/v1/facilities/{facility_id}/connectors",
        headers=headers,
        json={
            "type": "sentron",
            "vendor": "sentron",
            "display_name": "sentron-gateway",
            "connection": {"host": "10.10.4.22", "port": 502, "unit_id": 1},
            "credentials_ref": "sec_demo",
        },
    )
    checks.append(("attach_connector", connector.status_code))
    connector.raise_for_status()
    connector_id = connector.json()["id"]

    connector_validation = client.post(f"/v1/connectors/{connector_id}/validate", headers=headers)
    checks.append(("validate_connector", connector_validation.status_code))
    connector_validation.raise_for_status()

    import_job = client.post(
        f"/v1/facilities/{facility_id}/ingestion/imports",
        headers={**headers, "Idempotency-Key": "ui-smoke-backfill-key"},
        json={
            "type": "csv",
            "file_id": "fil_demo_ui_smoke",
            "schema_hint": "timestamp,power_kw,channel_id",
            "time_column": "timestamp",
        },
    )
    checks.append(("start_backfill", import_job.status_code))
    import_job.raise_for_status()

    recs = client.get(f"/v1/facilities/{facility_id}/recommendations?status=active", headers=headers)
    checks.append(("list_recommendations", recs.status_code))
    recs.raise_for_status()

    alerts = client.get(f"/v1/facilities/{facility_id}/alerts?status=open", headers=headers)
    checks.append(("list_alerts", alerts.status_code))
    alerts.raise_for_status()
    alert_id = alerts.json()["items"][0]["alert_id"]

    acknowledge = client.post(
        f"/v1/alerts/{alert_id}/acknowledge",
        headers=headers,
        json={"note": "Acknowledged from frontend smoke"},
    )
    checks.append(("acknowledge_alert", acknowledge.status_code))
    acknowledge.raise_for_status()

    incident = client.post(
        f"/v1/alerts/{alert_id}/incident",
        headers=headers,
        json={"note": "Open incident from frontend smoke"},
    )
    checks.append(("open_incident", incident.status_code))
    incident.raise_for_status()

    drift = client.get(f"/v1/facilities/{facility_id}/drift-events", headers=headers)
    checks.append(("list_drift_events", drift.status_code))
    drift.raise_for_status()

    retraining = client.get(f"/v1/facilities/{facility_id}/retraining-jobs", headers=headers)
    checks.append(("list_retraining_jobs", retraining.status_code))
    retraining.raise_for_status()

    demo_request = client.post(
        "/v1/public/demo-requests",
        json={
            "company": "Frontend Smoke Co",
            "contact_name": "Frontend Operator",
            "email": "frontend@example.com",
            "facilities_count": 3,
            "annual_energy_spend_eur": 1200000,
            "message": "frontend flow check",
        },
    )
    checks.append(("create_demo_request", demo_request.status_code))
    demo_request.raise_for_status()

    pricing_inquiry = client.post(
        "/v1/public/pricing-inquiries",
        json={
            "company": "Frontend Smoke Co",
            "contact_name": "Frontend Operator",
            "email": "frontend@example.com",
            "requested_plan": "multi-site",
        },
    )
    checks.append(("create_pricing_inquiry", pricing_inquiry.status_code))
    pricing_inquiry.raise_for_status()

    docs_response = client.get("/docs")
    checks.append(("open_docs", docs_response.status_code))
    docs_response.raise_for_status()

    print(checks)
    print(
        {
            "facility_id": facility_id,
            "connector_id": connector_id,
            "import_id": import_job.json()["import_id"],
            "alert_id": alert_id,
            "incident_id": incident.json().get("incident_id"),
            "recommendations": len(recs.json().get("items", [])),
            "drift_events": len(drift.json().get("items", [])),
            "retraining_jobs": len(retraining.json().get("items", [])),
            "demo_request_id": demo_request.json()["request_id"],
            "pricing_inquiry_id": pricing_inquiry.json()["inquiry_id"],
        }
    )


if __name__ == "__main__":
    main()