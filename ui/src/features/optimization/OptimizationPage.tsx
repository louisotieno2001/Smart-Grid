import React, { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { getOptimizationRuns, runOptimization } from "../../api/optimization";
import { queryKeys } from "../../api/queryKeys";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { ErrorBanner } from "../../components/ui/ErrorBanner";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { OptimizationForm } from "../../components/forms/OptimizationForm";
import { ExplanationPanel } from "./ExplanationPanel";
import { DataTable } from "../../components/tables/DataTable";

export function OptimizationPage() {
  const { siteId } = useParams();
  const qc = useQueryClient();
  const [latestResultId, setLatestResultId] = useState<string | null>(null);
  if (!siteId) return <ErrorBanner error={new Error("Missing siteId")} />;

  const runsQuery = useQuery({
    queryKey: queryKeys.optimizationRuns(siteId),
    queryFn: () => getOptimizationRuns(siteId),
    refetchInterval: 60_000
  });
  const runMutation = useMutation({
    mutationFn: ({ siteId, body }: { siteId: string; body: import("../../types").OptimizationRunBody }) =>
      runOptimization(siteId, body),
    onSuccess: (result) => {
      setLatestResultId(result.optimization_run_id || result.id || null);
      qc.invalidateQueries({ queryKey: queryKeys.optimizationRuns(siteId) });
      qc.invalidateQueries({ queryKey: queryKeys.telemetryLatest(siteId) });
      qc.invalidateQueries({ queryKey: queryKeys.commands(siteId) });
    }
  });

  return (
    <div style={{ display: "grid", gap: 12 }}>
      <PageHeader title="Optimization" subtitle={siteId} />
      <Card title="Run optimization">
        <OptimizationForm onSubmit={(body) => runMutation.mutate({ siteId, body })} loading={runMutation.isPending} />
        {runMutation.isError ? <ErrorBanner error={runMutation.error as Error} /> : null}
        {runMutation.data ? (
          <div style={{ marginTop: 10 }}>
            <ExplanationPanel explanation={runMutation.data.selected_action?.explanation || runMutation.data.explanation} />
          </div>
        ) : null}
      </Card>
      <Card title="Optimization runs history">
        {runsQuery.isLoading ? (
          <LoadingSpinner />
        ) : runsQuery.isError ? (
          <ErrorBanner error={runsQuery.error as Error} />
        ) : (
          <DataTable
            rows={runsQuery.data || []}
            getRowKey={(r) => r.id || r.optimization_run_id || Math.random().toString()}
            columns={[
              { key: "id", header: "Run", render: (r) => r.id || r.optimization_run_id || "—" },
              { key: "mode", header: "Mode", render: (r) => r.mode },
              { key: "decision", header: "Decision", render: (r) => r.explanation?.decision || r.selected_action?.command_type || "—" },
              { key: "summary", header: "Summary", render: (r) => r.explanation?.summary || r.selected_action?.explanation?.summary || "—" }
            ]}
          />
        )}
        <div style={{ marginTop: 8, color: "#666", fontSize: 12 }}>
          DEFERRED: `GET /api/v1/optimization-runs/{`{run_id}`}` detail endpoint is not implemented.
        </div>
        {latestResultId ? <div style={{ marginTop: 4, fontSize: 12 }}>Latest run: {latestResultId}</div> : null}
      </Card>
    </div>
  );
}
