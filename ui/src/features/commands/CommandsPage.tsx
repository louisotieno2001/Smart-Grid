import React, { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { acknowledgeCommand, listCommands } from "../../api/commands";
import { queryKeys } from "../../api/queryKeys";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { ErrorBanner } from "../../components/ui/ErrorBanner";
import { DataTable } from "../../components/tables/DataTable";
import { Badge } from "../../components/ui/Badge";

export function CommandsPage() {
  const { siteId } = useParams();
  const [statusFilter, setStatusFilter] = useState("");
  const qc = useQueryClient();
  if (!siteId) return <ErrorBanner error={new Error("Missing siteId")} />;

  const commandsQuery = useQuery({
    queryKey: queryKeys.commands(siteId),
    queryFn: () => listCommands(siteId, statusFilter || undefined),
    refetchInterval: 30_000
  });

  const ackMutation = useMutation({
    mutationFn: acknowledgeCommand,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.commands(siteId) });
    }
  });

  return (
    <div style={{ display: "grid", gap: 12 }}>
      <PageHeader title="Commands" subtitle={siteId} />
      <Card title="Command stream">
        <div style={{ marginBottom: 10 }}>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">all</option>
            <option value="queued">queued</option>
            <option value="sent">sent</option>
            <option value="acknowledged">acknowledged</option>
            <option value="executed">executed</option>
            <option value="failed">failed</option>
          </select>
        </div>
        {commandsQuery.isError ? (
          <>
            <ErrorBanner error={commandsQuery.error as Error} />
            <div style={{ marginTop: 8, color: "#ef6c00" }}>
              DEFERRED: `GET /api/v1/sites/{`{site_id}`}/commands` is not implemented in current backend.
            </div>
          </>
        ) : (
          <DataTable
            rows={commandsQuery.data || []}
            getRowKey={(r) => r.id}
            columns={[
              { key: "requested", header: "requested_at", render: (r) => r.requested_at },
              { key: "type", header: "command_type", render: (r) => <Badge kind="plain" value={r.command_type} /> },
              { key: "status", header: "status", render: (r) => <Badge kind="command" value={r.status === "acked" ? "acknowledged" : r.status} /> },
              {
                key: "failure",
                header: "failure_reason",
                render: (r) => (r.failure_reason ? <span style={{ color: "#c62828" }}>{r.failure_reason}</span> : "—")
              },
              {
                key: "ack",
                header: "",
                render: (r) =>
                  r.status === "sent" || r.status === "queued" ? (
                    <button onClick={() => ackMutation.mutate(r.id)}>Acknowledge</button>
                  ) : null
              }
            ]}
          />
        )}
      </Card>
    </div>
  );
}
