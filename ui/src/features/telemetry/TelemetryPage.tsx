import React, { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { getTelemetryHistory, getTelemetryLatest } from "../../api/telemetry";
import { queryKeys } from "../../api/queryKeys";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { ErrorBanner } from "../../components/ui/ErrorBanner";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { StatCard } from "../../components/ui/StatCard";
import { TelemetryLineChart } from "../../components/charts/TelemetryLineChart";

export function TelemetryPage() {
  const { siteId } = useParams();
  const [selectedKey, setSelectedKey] = useState("battery_soc");
  const to = useMemo(() => new Date().toISOString(), []);
  const from = useMemo(() => new Date(Date.now() - 24 * 3600 * 1000).toISOString(), []);

  if (!siteId) return <ErrorBanner error={new Error("Missing siteId")} />;

  const latestQuery = useQuery({ queryKey: queryKeys.telemetryLatest(siteId), queryFn: () => getTelemetryLatest(siteId) });
  const historyQuery = useQuery({
    queryKey: queryKeys.telemetryHistory(siteId, selectedKey),
    queryFn: () => getTelemetryHistory(siteId, selectedKey, from, to)
  });

  if (latestQuery.isLoading) return <LoadingSpinner />;
  if (latestQuery.isError) {
    return (
      <div style={{ display: "grid", gap: 12 }}>
        <PageHeader title="Telemetry" subtitle={siteId} />
        <ErrorBanner error={latestQuery.error as Error} />
        <Card title="DEFERRED">
          <div style={{ color: "#ef6c00" }}>
            DEFERRED: GET /api/v1/sites/{"{site_id}"}/telemetry/latest and history endpoints are not implemented in the current backend.
          </div>
        </Card>
      </div>
    );
  }

  const latest = latestQuery.data || {};
  const keys = Object.keys(latest);

  return (
    <div style={{ display: "grid", gap: 12 }}>
      <PageHeader title="Telemetry" subtitle={siteId} />
      <Card title="Latest values">
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(170px,1fr))", gap: 8 }}>
          {Object.entries(latest).map(([key, point]) => (
            <StatCard key={key} label={key} value={point.value} unit={point.unit} ts={point.ts} quality={point.quality} />
          ))}
        </div>
      </Card>
      <Card title="History">
        <div style={{ display: "flex", gap: 8, marginBottom: 10 }}>
          <select value={selectedKey} onChange={(e) => setSelectedKey(e.target.value)}>
            {keys.map((k) => (
              <option key={k} value={k}>
                {k}
              </option>
            ))}
          </select>
        </div>
        {historyQuery.isLoading ? (
          <LoadingSpinner />
        ) : historyQuery.isError ? (
          <ErrorBanner error={historyQuery.error as Error} />
        ) : (
          <TelemetryLineChart points={(historyQuery.data || []).map((p) => ({ ts: p.ts, value: p.value }))} />
        )}
      </Card>
    </div>
  );
}
