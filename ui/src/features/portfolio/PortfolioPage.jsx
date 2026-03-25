import { useEffect, useState } from "react";
import { FACILITIES } from "../../mocks/data";
import { pct } from "../../lib/format";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { DriftBadge, StatusBadge } from "../../components/ui/Badge";
import { ProgressBar } from "../../components/ui/ProgressBar";
import { SectionHeader } from "../../components/ui/SectionHeader";
import { StatCard } from "../../components/ui/StatCard";
import { Icon } from "../../lib/icons";
import { BarSeries } from "../../components/charts/BarSeries";
import { createFacility, listFacilities } from "../../lib/api";
import { mapFacilityToUi } from "../../lib/mappers";

export default function PortfolioPage() {
  const [status, setStatus] = useState("");
  const [facilities, setFacilities] = useState(FACILITIES);
  const totalSaving = facilities.reduce((sum, facility) => sum + facility.saving, 0);
  const totalRealized = facilities.reduce((sum, facility) => sum + facility.realized, 0);
  const months = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar"];
  const trend = [14200, 13800, 12900, 13400, 12600, 12100];

  async function refreshFacilities() {
    try {
      const result = await listFacilities("cli_001");
      if (result.items?.length) {
        setFacilities(result.items.map((item, idx) => mapFacilityToUi(item, idx)));
      } else {
        setFacilities(FACILITIES);
      }
    } catch {
      setFacilities(FACILITIES);
    }
  }

  useEffect(() => {
    refreshFacilities();
  }, []);

  async function handleAddFacility() {
    const name = window.prompt("Facility name", "New Industrial Site");
    if (!name) return;

    try {
      const created = await createFacility({
        name,
        country: "DE",
        site_type: "manufacturing",
        production_profile: "24_7_heavy_industrial",
        timezone: "Europe/Berlin",
      });
      setStatus(`Facility created: ${created.facility_id}`);
      await refreshFacilities();
    } catch {
      setStatus("Unable to create facility right now.");
    }
  }

  return (
    <div className="content fade-in">
      <div className="stat-grid">
        <StatCard label="PORTFOLIO SAVING / YR" value={`€${totalSaving}K`} valueStyle={{ color: "var(--accent)" }} delta="↑ 18% vs last run" deltaClass="up" />
        <StatCard label="REALIZED YTD" value={`€${totalRealized}K`} delta={`${pct(totalRealized, totalSaving)}% of projection`} />
        <StatCard label="ACTIVE FACILITIES" value={String(facilities.length)} delta="live facility count" deltaClass="up" />
        <StatCard label="OPEN ALERTS" value="4" valueStyle={{ color: "var(--amber)" }} delta="1 critical" deltaClass="down" />
      </div>

      <div className="two-col" style={{ marginBottom: 24 }}>
        <Card title="CONSUMPTION TREND — portfolio MWh/month">
          <BarSeries values={trend} labels={months} />
          <div style={{ fontSize: 11, color: "var(--muted)", fontFamily: "var(--mono)", marginTop: 10 }}>
            ↓ 14.8% YoY — driven by Casting Plant D and Compressed Air initiatives
          </div>
        </Card>
        <Card title="SAVING BY FACILITY">
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {facilities.map((facility) => (
              <div key={facility.id} style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 12 }}>
                <div style={{ width: 110, fontWeight: 600, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{facility.name}</div>
                <ProgressBar value={Math.round((facility.saving / 312) * 100)} />
                <div style={{ minWidth: 48, textAlign: "right", fontFamily: "var(--mono)", fontSize: 11, color: "var(--muted)" }}>€{facility.saving}K</div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <SectionHeader
        title="ALL FACILITIES"
        action={<Button tone="accent" size="sm" onClick={handleAddFacility}><Icon name="plus" size={12} /> Add facility</Button>}
      />
      {status ? <div style={{ marginBottom: 10, color: "var(--accent)", fontSize: 12 }}>{status}</div> : null}

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Facility</th>
              <th>Annual spend</th>
              <th>Saving / yr</th>
              <th>Realized</th>
              <th>kWh / tonne</th>
              <th>Open recs</th>
              <th>Model</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {facilities.map((facility) => (
              <tr key={facility.id}>
                <td>
                  <div className="td-name">{facility.name}</div>
                  <div className="td-sub">{facility.city}, {facility.country}</div>
                </td>
                <td style={{ fontFamily: "var(--mono)" }}>€{facility.spend}K</td>
                <td>
                  <div style={{ fontWeight: 600, color: "var(--accent)" }}>€{facility.saving}K</div>
                  <div style={{ marginTop: 4 }}><ProgressBar value={Math.round((facility.saving / 312) * 100)} width={80} /></div>
                </td>
                <td>
                  <div style={{ fontFamily: "var(--mono)", fontSize: 12 }}>{pct(facility.realized, facility.saving)}%</div>
                  <div style={{ marginTop: 4 }}><ProgressBar value={pct(facility.realized, facility.saving)} width={80} color={pct(facility.realized, facility.saving) > 60 ? "var(--accent)" : "var(--amber)"} /></div>
                </td>
                <td style={{ fontFamily: "var(--mono)", fontSize: 12 }}>{facility.intensity}</td>
                <td>{facility.recs}</td>
                <td><DriftBadge value={facility.drift} /></td>
                <td><StatusBadge value={facility.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
