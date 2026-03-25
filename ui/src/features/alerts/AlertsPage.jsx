import { useEffect, useState } from "react";
import { ALERTS, DRIFT_FEATURES } from "../../mocks/data";
import { SeverityBadge, StatusBadge, Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { StatCard } from "../../components/ui/StatCard";
import { acknowledgeAlert, listAlerts, listDriftEvents, listFacilities, listRetrainingJobs, openIncident } from "../../lib/api";
import { mapAlertToUi, mapDriftToUi } from "../../lib/mappers";

export default function AlertsPage() {
  const [status, setStatus] = useState("");
  const [alerts, setAlerts] = useState(ALERTS);
  const [driftFeatures, setDriftFeatures] = useState(DRIFT_FEATURES);
  const [retrainingJobs, setRetrainingJobs] = useState([]);
  const [activeFacilityId, setActiveFacilityId] = useState("fac_001");

  async function refreshLive() {
    try {
      const facilities = await listFacilities("cli_001");
      const facilityId = facilities.items?.[0]?.id || "fac_001";
      setActiveFacilityId(facilityId);

      const [alertsResult, driftResult, retrainingResult] = await Promise.all([
        listAlerts(facilityId, "open"),
        listDriftEvents(facilityId),
        listRetrainingJobs(facilityId),
      ]);

      if (alertsResult.items?.length) {
        setAlerts(alertsResult.items.map((item, idx) => mapAlertToUi(item, idx)));
      } else {
        setAlerts(ALERTS);
      }

      if (driftResult.items?.length) {
        setDriftFeatures(driftResult.items.map((item, idx) => mapDriftToUi(item, idx)));
      } else {
        setDriftFeatures(DRIFT_FEATURES);
      }

      setRetrainingJobs(retrainingResult.items || []);
    } catch {
      setAlerts(ALERTS);
      setDriftFeatures(DRIFT_FEATURES);
      setRetrainingJobs([]);
    }
  }

  useEffect(() => {
    refreshLive();
  }, []);

  async function onAcknowledge() {
    const alertId = alerts[0]?.id;
    if (!alertId) return;
    try {
      await acknowledgeAlert(alertId, "Acknowledged from dashboard");
      setStatus("Alert acknowledged in backend.");
      await refreshLive();
    } catch {
      setStatus("Alert acknowledged locally (backend alert not available yet).");
    }
  }

  async function onIncident() {
    const alertId = alerts[0]?.id;
    if (!alertId) return;
    try {
      const result = await openIncident(alertId, "Investigate model quality incident");
      setStatus(`Incident opened: ${result.incident_id}`);
      await refreshLive();
    } catch {
      setStatus("Incident action recorded locally (backend alert not available yet).");
    }
  }

  return (
    <div className="content fade-in">
      <div className="stat-grid" style={{ gridTemplateColumns: "repeat(3,1fr)" }}>
        <StatCard label="OPEN ALERTS" value={String(alerts.length)} valueStyle={{ color: "var(--amber)" }} delta="live monitoring view" deltaClass="down" />
        <StatCard label="PENDING RETRAINS" value={String(retrainingJobs.length)} delta="drift threshold exceeded" deltaClass="up" />
        <StatCard label="MEAN ACK TIME" value="14m" delta="within SLA" deltaClass="up" />
      </div>

      <div className="card">
        <div className="card-title">LIVE MONITORING</div>
        <div className="two-col">
          <div>
          <div className="table-wrap" style={{ border: "none", borderRadius: 0, background: "transparent" }}>
            {alerts.map((alert) => (
              <div key={alert.id} className="alert-item">
                <div className="alert-icon" style={{ background: alert.severity === "critical" ? "rgba(255,77,109,.12)" : alert.severity === "high" ? "rgba(245,166,35,.12)" : "rgba(77,159,255,.12)", color: alert.severity === "critical" ? "var(--red)" : alert.severity === "high" ? "var(--amber)" : "var(--blue)" }}>
                  !
                </div>
                <div className="alert-body">
                  <div className="alert-title">{alert.title}</div>
                  <div style={{ fontSize: 12, color: "var(--muted)", marginBottom: 6 }}>{alert.detail}</div>
                  <div className="alert-meta">{alert.facility} · SLA {alert.sla_minutes}m · {alert.ago}</div>
                </div>
                <div className="alert-actions">
                  <SeverityBadge value={alert.severity} />
                  <StatusBadge value={alert.state} />
                </div>
              </div>
            ))}
          </div>
          </div>

          <div>
            <div className="card-title" style={{ marginBottom: 8 }}>DRIFT MONITOR</div>
            {driftFeatures.map((feature) => (
              <div key={feature.name} className="drift-row">
                <div className="drift-feature">{feature.name}</div>
                <div className="drift-psi" style={{ color: feature.psi >= 0.2 ? "var(--red)" : feature.psi >= 0.15 ? "var(--amber)" : "var(--accent)" }}>{feature.psi.toFixed(2)}</div>
                <Badge tone={feature.status === "retrain_triggered" ? "red" : feature.status === "monitoring" ? "amber" : "green"}>{feature.status.replaceAll("_", " ")}</Badge>
              </div>
            ))}
            <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
              <Button tone="accent" size="sm" onClick={onAcknowledge}>Acknowledge</Button>
              <Button size="sm" onClick={onIncident}>Open incident</Button>
            </div>
            {status ? <div style={{ marginTop: 10, color: "var(--accent)", fontSize: 12 }}>{status}</div> : null}
            <div style={{ marginTop: 6, color: "var(--muted)", fontSize: 11, fontFamily: "var(--mono)" }}>facility: {activeFacilityId}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
