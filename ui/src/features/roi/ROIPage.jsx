import { useMemo, useState } from "react";
import { Card } from "../../components/ui/Card";
import { Collapsible } from "../../components/ui/Collapsible";

function calculate(inputs) {
  const projectedSavings = Math.round(inputs.spend * (inputs.inefficiency / 100));
  const realized = Math.round(projectedSavings * (inputs.adoption / 100));
  const annualCost = inputs.platformCost + inputs.implementationCost;
  const net = realized - annualCost;
  const paybackMonths = Number(((annualCost / Math.max(realized, 1)) * 12).toFixed(1));
  const roiPct = Math.round((net / Math.max(annualCost, 1)) * 100);
  return { projectedSavings, realized, annualCost, net, paybackMonths, roiPct };
}

export default function ROIPage() {
  const [inputs, setInputs] = useState({
    spend: 1480,
    inefficiency: 4.2,
    adoption: 72,
    platformCost: 168,
    implementationCost: 90,
    maturity: "medium",
    capacity: "medium",
  });

  const result = useMemo(() => calculate(inputs), [inputs]);
  const update = (field) => (event) => setInputs((prev) => ({ ...prev, [field]: Number.isNaN(Number(event.target.value)) ? event.target.value : Number(event.target.value) }));

  return (
    <div className="content fade-in">
      <Card title="ROI CALCULATOR">
        <Collapsible
          open={true}
          title="INPUTS"
          style={{ marginBottom: 20 }}
        >
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
            <div className="form-group"><label className="form-label">Annual energy spend (€K)</label><input className="form-input" value={inputs.spend} onChange={update("spend")} /></div>
            <div className="form-group"><label className="form-label">Projected technical opportunity (%)</label><input className="form-input" value={inputs.inefficiency} onChange={update("inefficiency")} /></div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div className="form-group"><label className="form-label">Expected realization (%)</label><input className="form-input" value={inputs.adoption} onChange={update("adoption")} /></div>
            <div className="form-group"><label className="form-label">Annual software cost (€K)</label><input className="form-input" value={inputs.platformCost} onChange={update("platformCost")} /></div>
          </div>
          <div className="form-group"><label className="form-label">Implementation cost (€K)</label><input className="form-input" value={inputs.implementationCost} onChange={update("implementationCost")} /></div>
        </Collapsible>

        <div style={{
          padding: 16,
          background: "var(--bg2)",
          borderRadius: 6,
          marginBottom: 20,
          border: "1px solid var(--accent)",
          borderLeft: "3px solid var(--accent)"
        }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
            <div>
              <div style={{ fontSize: 11, color: "var(--muted)", marginBottom: 6 }}>NET FIRST-YEAR VALUE</div>
              <div style={{ fontSize: 32, fontWeight: 600, color: "var(--accent)" }}>€{result.net}K</div>
            </div>
            <div>
              <div style={{ fontSize: 11, color: "var(--muted)", marginBottom: 6 }}>PAYBACK PERIOD</div>
              <div style={{ fontSize: 32, fontWeight: 600 }}>{result.paybackMonths} months</div>
            </div>
          </div>
          
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
            <div>
              <div style={{ fontSize: 10, color: "var(--muted)", marginBottom: 4 }}>PROJECTED SAVING</div>
              <div style={{ fontSize: 16, fontWeight: 600 }}>€{result.projectedSavings}K</div>
            </div>
            <div>
              <div style={{ fontSize: 10, color: "var(--muted)", marginBottom: 4 }}>REALIZED SAVING</div>
              <div style={{ fontSize: 16, fontWeight: 600 }}>€{result.realized}K</div>
            </div>
            <div>
              <div style={{ fontSize: 10, color: "var(--muted)", marginBottom: 4 }}>TOTAL COST</div>
              <div style={{ fontSize: 16, fontWeight: 600 }}>€{result.annualCost}K</div>
            </div>
            <div>
              <div style={{ fontSize: 10, color: "var(--muted)", marginBottom: 4 }}>ROI %</div>
              <div style={{ fontSize: 16, fontWeight: 600, color: "var(--accent)" }}>{result.roiPct}%</div>
            </div>
          </div>
        </div>

        <Collapsible
          open={false}
          title="API PAYLOAD (for integration)"
          style={{ borderTop: "1px solid var(--border)", paddingTop: 16 }}
        >
          <code style={{
            fontFamily: "var(--mono)",
            fontSize: 10,
            background: "var(--bg2)",
            padding: 10,
            borderRadius: 4,
            display: "block",
            lineHeight: 1.7,
            color: "var(--muted)",
            whiteSpace: "pre-wrap",
            wordBreak: "break-all"
          }}>
            {JSON.stringify({
              annual_energy_spend_eur: inputs.spend * 1000,
              benchmark_inefficiency_pct: inputs.inefficiency / 100,
              adoption_rate_pct: inputs.adoption / 100,
              annual_platform_cost_eur: inputs.platformCost * 1000,
              implementation_cost_eur: inputs.implementationCost * 1000,
            }, null, 2)}
          </code>
        </Collapsible>
      </Card>
    </div>
  );
}
