import { useState } from "react";
import { CONNECTORS } from "../../mocks/data";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Collapsible } from "../../components/ui/Collapsible";
import { attachConnector, createFacility, startBackfill, validateConnector } from "../../lib/api";

const steps = ["Scoping", "Legal", "Integration", "Model run", "Client review", "Steady-state"];
const mappings = [
  { appliance: "Arc Furnace #1", channel: "CH-001", role: "power_kw", quality: 98 },
  { appliance: "Compressed Air Ring", channel: "CH-014", role: "pressure_bar", quality: 95 },
  { appliance: "Preheater A", channel: "CH-022", role: "runtime_state", quality: 92 },
  { appliance: "Floor HVAC", channel: "CH-031", role: "airflow_pct", quality: 89 },
];

export default function IntakePage() {
  const [step, setStep] = useState(3);
  const [selectedConnector, setSelectedConnector] = useState("sentron");
  const [facilityId, setFacilityId] = useState(null);
  const [connectorId, setConnectorId] = useState(null);
  const [status, setStatus] = useState("");
  const [expandedSection, setExpandedSection] = useState("profile");

  async function onSaveProfile() {
    try {
      const facility = await createFacility({
        name: "Steelworks A",
        country: "DE",
        site_type: "manufacturing",
        production_profile: "24_7_heavy_industrial",
        timezone: "Europe/Berlin",
      });
      setFacilityId(facility.facility_id);
      setStatus(`Profile saved as ${facility.facility_id}`);
      setStep(4);
      setExpandedSection("integration");
    } catch {
      setStatus("Failed to save profile to backend.");
    }
  }

  async function onValidateConnector() {
    if (!facilityId) {
      setStatus("Save profile first to create a facility.");
      return;
    }
    try {
      const connector = await attachConnector(facilityId, {
        type: selectedConnector,
        vendor: selectedConnector,
        display_name: `${selectedConnector}-gateway`,
        connection: { host: "10.10.4.22", port: 502, unit_id: 1 },
        credentials_ref: "sec_demo",
      });
      setConnectorId(connector.id);
      const result = await validateConnector(connector.id);
      setStatus(`Connector validated: ${result.channels_detected} channels detected.`);
    } catch {
      setStatus("Connector validation failed.");
    }
  }

  async function onStartBackfill() {
    if (!facilityId) {
      setStatus("Save profile first to create a facility.");
      return;
    }
    try {
      const job = await startBackfill(facilityId, {
        type: "csv",
        file_id: `fil_demo_${Date.now()}`,
        schema_hint: "timestamp,power_kw,channel_id",
        time_column: "timestamp",
      });
      setStatus(`Backfill queued: ${job.import_id}`);
      setStep(5);
      setExpandedSection("mapping");
    } catch {
      setStatus("Unable to start backfill.");
    }
  }

  return (
    <div className="content fade-in">
      <div className="stepper">
        {steps.map((label, index) => (
          <div className="step-item" key={label}>
            <div className={`step-circle ${index < step ? "done" : index === step ? "active" : ""}`}>{index + 1}</div>
            <div className={`step-label ${index === step ? "active" : ""}`}>{label}</div>
            {index < steps.length - 1 ? <div className={`step-line ${index < step ? "done" : ""}`} /> : null}
          </div>
        ))}
      </div>

      <Card title="ONBOARDING WORKFLOW">
        <Collapsible
          open={expandedSection === "profile"}
          title="Step 3 — Facility Profile"
          style={{ marginBottom: 16 }}
        >
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
            <div className="form-group"><label className="form-label">Facility name</label><input className="form-input" defaultValue="Steelworks A" /></div>
            <div className="form-group"><label className="form-label">Country</label><input className="form-input" defaultValue="Germany" /></div>
            <div className="form-group"><label className="form-label">Timezone</label><input className="form-input" defaultValue="Europe/Berlin" /></div>
            <div className="form-group"><label className="form-label">Production profile</label><select className="form-select" defaultValue="24_7"><option value="24_7">24/7 heavy industrial</option></select></div>
          </div>
          <Button tone="accent" onClick={() => { onSaveProfile(); setExpandedSection("integration"); }}>Save profile</Button>
          {facilityId && <div style={{ marginTop: 10, fontSize: 11, color: "var(--accent)" }}>facility_id: {facilityId}</div>}
        </Collapsible>

        <Collapsible
          open={expandedSection === "integration"}
          title="Step 4 — Data Integration"
          style={{ marginBottom: 16 }}
        >
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontSize: 11, color: "var(--muted)", marginBottom: 10 }}>Select your data source</div>
            <div className="connector-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(100px, 1fr))", gap: 8 }}>
              {CONNECTORS.map((connector) => (
                <div 
                  key={connector.id} 
                  className={`connector-card ${selectedConnector === connector.id ? "connected" : ""}`} 
                  onClick={() => setSelectedConnector(connector.id)}
                  style={{ padding: 10, textAlign: "center" }}
                >
                  <div style={{ fontSize: 20, marginBottom: 4 }}>{connector.icon}</div>
                  <div style={{ fontSize: 11, fontWeight: 500 }}>{connector.name}</div>
                </div>
              ))}
            </div>
            <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
              <Button tone="accent" size="sm" onClick={() => { onValidateConnector(); setExpandedSection("mapping"); }}>Validate connector</Button>
              <Button size="sm" onClick={() => { onStartBackfill(); setExpandedSection("mapping"); }}>Start backfill</Button>
            </div>
            {connectorId && <div style={{ marginTop: 8, fontSize: 11, color: "var(--accent)" }}>connector_id: {connectorId}</div>}
          </div>
        </Collapsible>

        <Collapsible
          open={expandedSection === "mapping"}
          title="Step 5 — Channel Mapping & Validation"
          style={{ marginBottom: 16 }}
        >
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontSize: 11, color: "var(--muted)", marginBottom: 8 }}>Import status</div>
            <div className="bar-track" style={{ height: 6, marginBottom: 8 }}><div className="bar-fill" style={{ width: "68%", background: "var(--accent)" }} /></div>
            <div style={{ fontSize: 11, color: "var(--muted)" }}>19,238,011 / 28,344,121 rows processed · 14,921 rejected</div>
            <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 10 }}>Current: Channel normalization and deduplication</div>
          </div>
          <div className="table-wrap" style={{ border: "none", borderRadius: 0, background: "transparent" }}>
            <table style={{ fontSize: 12 }}>
              <thead>
                <tr><th>Appliance</th><th>Channel</th><th>Role</th><th>Quality</th></tr>
              </thead>
              <tbody>
                {mappings.map((row) => (
                  <tr key={row.channel}>
                    <td>{row.appliance}</td>
                    <td style={{ fontFamily: "var(--mono)" }}>{row.channel}</td>
                    <td>{row.role}</td>
                    <td style={{ color: row.quality >= 95 ? "var(--accent)" : row.quality >= 90 ? "var(--amber)" : "var(--red)" }}>{row.quality}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Collapsible>

        {status && <div style={{ marginTop: 12, padding: 10, background: "var(--bg2)", borderRadius: 4, fontSize: 12, color: "var(--accent)" }}>{status}</div>}
      </Card>
    </div>
  );
}
