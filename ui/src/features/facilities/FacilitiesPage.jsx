import { useEffect, useState } from "react";
import { FACILITIES } from "../../mocks/data";
import { Button } from "../../components/ui/Button";
import { DriftBadge, StatusBadge } from "../../components/ui/Badge";
import { ProgressBar } from "../../components/ui/ProgressBar";
import { SectionHeader } from "../../components/ui/SectionHeader";
import { Icon } from "../../lib/icons";
import { pct } from "../../lib/format";
import { createFacility, listFacilities } from "../../lib/api";
import { mapFacilityToUi } from "../../lib/mappers";

export default function FacilitiesPage() {
  const [status, setStatus] = useState("");
  const [facilities, setFacilities] = useState(FACILITIES);

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

  async function handleNewFacility() {
    const name = window.prompt("Facility name", "Facility X");
    if (!name) return;
    try {
      const created = await createFacility({
        name,
        country: "DE",
        site_type: "manufacturing",
        production_profile: "24_7_heavy_industrial",
        timezone: "Europe/Berlin",
      });
      setStatus(`Created ${created.facility_id}`);
      await refreshFacilities();
    } catch {
      setStatus("Creation failed.");
    }
  }

  return (
    <div className="content fade-in">
      <SectionHeader title="FACILITY ROSTER" action={<Button tone="accent" size="sm" onClick={handleNewFacility}><Icon name="plus" size={12} /> New facility</Button>} />
      {status ? <div style={{ marginBottom: 10, color: "var(--accent)", fontSize: 12 }}>{status}</div> : null}
      <div className="table-wrap">
        <table>
          <thead>
            <tr><th>Name</th><th>Location</th><th>Appliances</th><th>MAPE</th><th>Saving /yr</th><th>Realized</th><th>Intensity</th><th>Drift</th><th>Status</th></tr>
          </thead>
          <tbody>
            {facilities.map((facility) => (
              <tr key={facility.id}>
                <td><div className="td-name">{facility.name}</div><div className="td-sub">{facility.id}</div></td>
                <td>{facility.city}, {facility.country}</td>
                <td>{facility.appliances}</td>
                <td style={{ fontFamily: "var(--mono)", fontSize: 12, color: facility.mape <= 4.5 ? "var(--accent)" : "var(--amber)" }}>{facility.mape}%</td>
                <td style={{ fontFamily: "var(--mono)", fontWeight: 600, color: "var(--accent)" }}>€{facility.saving}K</td>
                <td>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <ProgressBar value={pct(facility.realized, facility.saving)} width={60} color={pct(facility.realized, facility.saving) > 60 ? "var(--accent)" : "var(--amber)"} />
                    <span style={{ fontSize: 11, fontFamily: "var(--mono)" }}>{pct(facility.realized, facility.saving)}%</span>
                  </div>
                </td>
                <td style={{ fontFamily: "var(--mono)", fontSize: 12 }}>{facility.intensity} kWh/t</td>
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
