# End-to-End System Architecture Blueprint

## Architecture Goals
- Tenant isolation by client and facility across storage, compute, and observability
- Asynchronous processing for imports, feature materialization, and model runs
- Full traceability from recommendation -> model run -> feature snapshot -> data window
- Reliable alerting and escalation with dedupe and correlation

## Core Runtime Components
1. API Gateway
   - OAuth2/JWT verification, API key validation, rate limits, request IDs
   - Routes `/v1/*` to domain services

2. Identity and Access Service
   - RBAC scopes: client_admin, facility_manager, energy_analyst, viewer, ops_admin, ml_engineer
   - Issues short-lived JWTs and supports service accounts

3. Domain API Services
   - Onboarding service (`clients`, `facilities`, `connectors`, `appliances`)
   - Ingestion service (`imports`, stream/batch normalization)
   - Modeling service (`features`, `model runs`, explainability artifacts)
   - Recommendations service (`recommendation lifecycle`, decision, implementation)
   - Monitoring service (`alerts`, `drift`, `savings`)

4. Data Plane
   - Raw telemetry store (time-series + object store)
   - Curated feature store (offline + online views)
   - OLTP metadata store for tenancy, mappings, and workflow state
   - Analytics warehouse for reporting and ROI dashboards

5. Workflow and Orchestration
   - Queue/event bus for long-running jobs
   - Worker pools for ingestion parsing, feature jobs, model training/inference
   - Scheduler for retraining, drift checks, digest generation

6. ML Platform Layer
   - Model registry with versioning and promotion workflow
   - Experiment tracking and artifact storage (SHAP, performance reports)
   - Drift detector with threshold policies and automatic retraining triggers
   - Quality-gate policy using holdout metrics (e.g., holdout MAPE threshold)

7. Alerting and Notification Layer
   - Correlation engine and dedupe keys
   - Routing policy engine and SLA/escalation timers
   - Delivery adapters: in-app, email, Slack/Teams, SMS, outbound webhooks

## Reference Data Flow
1. Connector emits telemetry -> ingestion adapter validates schema and quality
2. Normalized readings land in raw store + quality metrics stream
3. Feature jobs materialize feature snapshots by facility/time window
4. Model run executes and stores metrics/artifacts in registry
4b. Quality gate checks holdout metrics and auto-queues retraining when thresholds are breached
5. Recommendations service publishes ranked actions with confidence/payback
6. Decision + implementation events start realized-savings measurement windows
7. Monitoring service computes realization and emits business/model/data alerts

## Deployment Blueprint
- API services in Kubernetes with HPA and separate worker deployments
- Managed message bus and managed relational DB
- Object storage for artifacts and import files
- Time-series database for high-frequency telemetry
- Warehouse for BI and customer reporting
- Optional region-per-client deployment for strict data residency

## Observability Requirements
Every request/event should carry:
- request ID
- tenant ID (client/facility)
- actor ID or service account
- endpoint and latency
- status code / job state

Metrics:
- ingestion lag and rejection rate
- feature job runtime and failure rate
- model run duration and drift frequency
- recommendation acceptance and implementation latency
- alert MTTA/MTTR and escalation rate

## Security and Compliance
- Encrypt data in transit and at rest
- Secrets in vault with rotation
- Immutable audit logs for config and decision actions
- Least-privilege service identities
- Tenant-level access boundaries enforced in API and storage policies
