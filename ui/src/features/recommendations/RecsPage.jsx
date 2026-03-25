import { useEffect, useMemo, useState } from "react";
import { RECOMMENDATIONS } from "../../mocks/data";
import { Button } from "../../components/ui/Button";
import { Badge, StatusBadge } from "../../components/ui/Badge";
import { ProgressBar } from "../../components/ui/ProgressBar";
import { StatCard } from "../../components/ui/StatCard";
import { listFacilities, listRecommendations } from "../../lib/api";
import { mapRecommendationToUi } from "../../lib/mappers";

function impactLevel(rec) {
  if (rec.saving >= 80) return "high";
  if (rec.saving >= 30) return "medium";
  return "low";
}

export default function RecsPage() {
  const [filter, setFilter] = useState("all");
  const [recommendations, setRecommendations] = useState(RECOMMENDATIONS);
  const filtered = useMemo(() => filter === "all" ? recommendations : recommendations.filter((rec) => rec.status === filter), [filter, recommendations]);
  const projected = filtered.reduce((sum, rec) => sum + rec.saving, 0);

  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const facilities = await listFacilities("cli_001");
        const facilityId = facilities.items?.[0]?.id;
        if (!facilityId) {
          if (active) setRecommendations(RECOMMENDATIONS);
          return;
        }
        const result = await listRecommendations(facilityId, "active");
        if (!active) return;
        if (result.items?.length) {
          setRecommendations(result.items.map((item, idx) => mapRecommendationToUi(item, idx)));
        } else {
          setRecommendations(RECOMMENDATIONS);
        }
      } catch {
        if (active) setRecommendations(RECOMMENDATIONS);
      }
    }
    load();
    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="content fade-in">
      <div className="stat-grid" style={{ gridTemplateColumns: "repeat(3,1fr)" }}>
        <StatCard label="TOTAL PROJECTED" value={`€${recommendations.reduce((sum, rec) => sum + rec.saving, 0)}K`} valueStyle={{ color: "var(--accent)" }} delta={`${recommendations.length} ranked opportunities`} deltaClass="up" />
        <StatCard label="ACTIVE FILTER" value={filter.toUpperCase()} delta={`${filtered.length} recommendations visible`} />
        <StatCard label="FILTERED SAVING" value={`€${projected}K`} delta="Sorted by expected annual value" />
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: 18, flexWrap: "wrap" }}>
        {["all", "active", "accepted", "implemented"].map((value) => (
          <Button key={value} tone={filter === value ? "accent" : "default"} size="sm" onClick={() => setFilter(value)}>{value}</Button>
        ))}
      </div>

      {filtered.map((rec) => (
        <div className={`rec-card ${impactLevel(rec)}`} key={rec.id}>
          <div className="rec-top">
            <div>
              <div className="rec-title">{rec.title}</div>
              <div className="td-sub" style={{ marginTop: 4 }}>{rec.appliance} · {rec.category}</div>
            </div>
            <div className="rec-saving">€{rec.saving}K / yr</div>
          </div>
          <div className="rec-body">{rec.body}</div>
          <div className="rec-meta">
            <StatusBadge value={rec.status} />
            <Badge tone="blue">effort · {rec.effort}</Badge>
            <Badge tone="dim">payback · {rec.payback_months} mo</Badge>
            <Badge tone="green">confidence · {Math.round(rec.confidence * 100)}%</Badge>
          </div>
          <div className="readiness-row">
            readiness
            <ProgressBar value={Math.round(rec.readiness * 100)} color={impactLevel(rec) === "high" ? "var(--accent)" : impactLevel(rec) === "medium" ? "var(--amber)" : "var(--dim)"} />
            {Math.round(rec.readiness * 100)}%
          </div>
        </div>
      ))}
    </div>
  );
}
