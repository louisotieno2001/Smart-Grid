# Frontend Integration Contract

## Existing internal app surfaces (preserved)
- portfolio
- facilities
- recommendations
- alerts and monitoring
- data intake/onboarding
- ROI calculator
- API explorer

## Public-site surfaces
- landing page
- pricing
- about
- login
- signup
- request demo

## API endpoints to wire
Internal:
- `/v1/clients/{client_id}/facilities`
- `/v1/facilities/{facility_id}/connectors`
- `/v1/facilities/{facility_id}/ingestion/imports`
- `/v1/ingestion/imports/{import_id}`
- `/v1/facilities/{facility_id}/features/materialize`
- `/v1/facilities/{facility_id}/models/runs`
- `/v1/models/runs/{model_run_id}`
- `/v1/facilities/{facility_id}/recommendations`
- `/v1/facilities/{facility_id}/alerts`
- `/v1/facilities/{facility_id}/drift-events`
- `/v1/facilities/{facility_id}/retraining-jobs`
- `/v1/alerts/{alert_id}/acknowledge`
- `/v1/alerts/{alert_id}/incident`

Public:
- `/v1/public/demo-requests`
- `/v1/public/pricing-inquiries`

## Implemented button/action wiring
- Topbar `Refresh` reloads runtime surface.
- Topbar `Settings` opens backend API docs (`/docs`).
- Portfolio/Facilities `Add/New facility` calls facility-creation API.
- Intake `Save profile`, `Validate connector`, `Start backfill` call onboarding/ingestion endpoints.
- Alerts `Acknowledge` and `Open incident` call monitoring action endpoints.
- Public-site CTAs submit demo requests and pricing inquiries.
- Login/Signup forms now submit and return operator feedback states.

## Integration behavior
- Keep long-running actions async and poll job/status endpoints.
- Preserve idempotency headers on import/model trigger calls.
- Respect role scopes in UI controls and action permissions.
- Surface model quality and retraining-trigger state in monitoring views.
