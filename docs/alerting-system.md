# Alerting and Notification System Design

## Purpose
This system turns platform events into triaged incidents with ownership, SLA, and escalation.

## Alert Taxonomy
- Data alerts: connector offline, backfill failed, null spikes, timestamp disorder, flatline, duplicate bursts
- Model alerts: drift detected, confidence collapse, anomaly-rate spike, feature failures, inference timeout, output-volume anomaly
- Business alerts: under-realized savings, accepted-but-not-implemented recommendations, recommendation aging, worsening site performance
- Security/compliance alerts: failed login burst, unauthorized connector config attempt, API key misuse, audit gap, PII policy breach

## Severity Model
- `info`: informational and trend-only
- `warning`: degradations with low immediate business risk
- `high`: materially affects model quality or operations
- `critical`: high business-impact operational outage

Severity should combine technical signal + business exposure (e.g. production window, tariff period, site criticality).

## Alert Entity
```json
{
  "alert_id": "alt_8801",
  "source_type": "connector",
  "source_id": "con_444",
  "facility_id": "fac_014",
  "client_id": "cli_001",
  "severity": "high",
  "owner_role": "facility_manager",
  "routing_policy": "critical_connector_outage_v1",
  "sla_minutes": 30,
  "dedupe_key": "fac_014:con_444:offline",
  "state": "open"
}
```

## Lifecycle
`open -> acknowledged -> investigating -> resolved -> closed`

Optional suppression path: `open -> suppressed`.

Every transition records actor, timestamp, note, evidence, and linked incident.

## Correlation and Deduplication
Correlate by deterministic keys and collapse noise:
- connector incidents: `facility + connector + error_type`
- drift incidents: `facility + model + drift_dimension`
- recommendation aging: `recommendation + aging_bucket`

Policy examples:
- 120 channel flatlines from one connector collapse into one parent incident.
- Drift repeats in same feature family within 24h merge into one active incident.

## Routing and Escalation
Base routing:
- data quality alerts -> ops_admin; escalate to facility_manager if unresolved over threshold
- drift alerts -> ml_engineer first; then ops_admin
- savings underperformance -> customer_success + energy_analyst
- critical connector outage -> email + Slack/Teams + SMS

Escalation policy:
- warning unresolved 4h -> ops lead
- high unresolved 2h -> facility manager
- critical unresolved 30m -> page on-call and send stakeholder summary

## Notification Channels
- In-app notifications
- Email digest for non-urgent items
- Real-time email for high/critical
- Slack/Teams webhooks
- SMS only for high-confidence critical incidents
- Client API/webhook integration for CMMS/ERP

Alert facts and notifications are separate layers: not every alert emits a notification.

## Playbook Contract
Each alert type links to a playbook with:
1. What happened
2. Likely causes
3. Immediate checks
4. Rollback/fallback
5. Owner and escalation timing

Example `data_quality.channel_flatline`:
1. Confirm connector health
2. Compare neighboring channels
3. Check gateway heartbeat
4. Validate maintenance window
5. Flag inferred downtime when verified

## Client-facing Language Layer
For each alert, maintain two messages:
- technical phrasing for operators/engineers
- business phrasing for client stakeholders

This supports trust and actionability without overloading business users with ML jargon.
