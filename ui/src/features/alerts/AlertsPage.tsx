import React, { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { acknowledgeAlert, getAlertCounts, getAlerts, resolveAlert } from "../../api/alerts";
import { queryKeys } from "../../api/queryKeys";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { ErrorBanner } from "../../components/ui/ErrorBanner";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { Badge } from "../../components/ui/Badge";
import "../../styles/features.css";

export function AlertsPage() {
  const { siteId } = useParams();
  const [stateFilter, setStateFilter] = useState<string>("");
  const qc = useQueryClient();

  if (!siteId) return <ErrorBanner error={new Error("Missing siteId")} />;

  const alertsQuery = useQuery({
    queryKey: queryKeys.alerts(siteId),
    queryFn: () => getAlerts(siteId, stateFilter || undefined),
    refetchInterval: 30_000
  });

  const countsQuery = useQuery({
    queryKey: queryKeys.alertCounts(siteId),
    queryFn: () => getAlertCounts(siteId),
    refetchInterval: 60_000
  });

  const ackMutation = useMutation({
    mutationFn: acknowledgeAlert,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.alerts(siteId) });
      qc.invalidateQueries({ queryKey: queryKeys.alertCounts(siteId) });
    }
  });

  const resolveMutation = useMutation({
    mutationFn: resolveAlert,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.alerts(siteId) });
      qc.invalidateQueries({ queryKey: queryKeys.alertCounts(siteId) });
    }
  });

  const counts = countsQuery.data;

  return (
    <div className="page-content">
      <PageHeader title="Alerts" subtitle={siteId} />
      
      {counts && (
        <div className="stats-grid" style={{ marginBottom: 16 }}>
          <div className="stat-card" style={{ background: "#c6282822", border: "1px solid #c62828" }}>
            <div className="stat-label">Open Critical</div>
            <div className="stat-value" style={{ color: "#c62828" }}>{counts.by_severity.critical}</div>
          </div>
          <div className="stat-card" style={{ background: "#f9a82522", border: "1px solid #f9a825" }}>
            <div className="stat-label">Open Warnings</div>
            <div className="stat-value" style={{ color: "#f9a825" }}>{counts.by_severity.warning}</div>
          </div>
          <div className="stat-card" style={{ background: "#1976d222", border: "1px solid #1976d2" }}>
            <div className="stat-label">Open Info</div>
            <div className="stat-value" style={{ color: "#1976d2" }}>{counts.by_severity.info}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Total Open</div>
            <div className="stat-value">{counts.open}</div>
          </div>
        </div>
      )}

      <Card title="Alert history">
        <div style={{ marginBottom: 16 }}>
          <select value={stateFilter} onChange={(e) => setStateFilter(e.target.value)} className="form-input">
            <option value="">all</option>
            <option value="open">open</option>
            <option value="acknowledged">acknowledged</option>
            <option value="resolved">resolved</option>
          </select>
        </div>
        {alertsQuery.isLoading ? (
          <LoadingSpinner />
        ) : alertsQuery.isError ? (
          <ErrorBanner error={alertsQuery.error as Error} />
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {(!alertsQuery.data?.items || alertsQuery.data.items.length === 0) ? (
              <div className="deferred-box">No alerts found.</div>
            ) : (
              alertsQuery.data.items.map((alert) => (
                <div
                  key={alert.id}
                  style={{
                    border: "1px solid #ddd",
                    borderRadius: 8,
                    padding: 12,
                    background: alert.state === "open" ? "#fff8f8" : "#fafafa"
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                    <Badge kind="severity" value={alert.severity} />
                    <Badge kind="state" value={alert.state} />
                    <span style={{ fontWeight: 600, flex: 1 }}>{alert.title}</span>
                    <span style={{ fontSize: 12, color: "#666" }}>
                      {new Date(alert.created_at).toLocaleString()}
                    </span>
                  </div>
                  <div style={{ color: "#333", marginBottom: 8 }}>{alert.message}</div>
                  {alert.source_key && (
                    <div style={{ fontSize: 12, color: "#666" }}>Source: {alert.source_key}</div>
                  )}
                  {alert.state !== "resolved" && (
                    <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
                      {alert.state === "open" && (
                        <button
                          onClick={() => ackMutation.mutate(alert.id)}
                          className="logout-button"
                          style={{ width: "auto" }}
                        >
                          Acknowledge
                        </button>
                      )}
                      <button
                        onClick={() => resolveMutation.mutate(alert.id)}
                        className="logout-button"
                        style={{ width: "auto", background: "#2e7d32" }}
                      >
                        Resolve
                      </button>
                    </div>
                  )}
                  {(alert.acknowledged_at || alert.resolved_at) && (
                    <div style={{ fontSize: 11, color: "#666", marginTop: 8 }}>
                      {alert.acknowledged_at && `Acknowledged: ${new Date(alert.acknowledged_at).toLocaleString()}`}
                      {alert.acknowledged_at && alert.resolved_at && " | "}
                      {alert.resolved_at && `Resolved: ${new Date(alert.resolved_at).toLocaleString()}`}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </Card>
    </div>
  );
}
