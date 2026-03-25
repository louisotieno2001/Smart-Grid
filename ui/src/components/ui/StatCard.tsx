import React from "react";
import { formatStatValue } from "../../utils/format";
import { formatTimestamp } from "../../utils/time";

type StatCardProps = {
  label: string;
  value: number | null;
  unit: string;
  ts?: string;
  quality?: "good" | "estimated" | "bad";
  stale?: boolean;
};

export function StatCard({ label, value, unit, ts, quality, stale }: StatCardProps) {
  const color = quality === "bad" ? "#c62828" : quality === "estimated" ? "#ef6c00" : "#1b1b1b";
  return (
    <div style={{ background: "#fff", border: "1px solid #e0e0e0", borderRadius: 8, padding: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ color: "#555", fontSize: 13 }}>{label}</div>
        {stale ? <span style={{ color: "#f9a825", fontSize: 12 }}>● stale</span> : null}
      </div>
      <div style={{ marginTop: 8, fontSize: 22, fontWeight: 700, color }}>{formatStatValue(value, unit)}</div>
      {ts ? <div style={{ marginTop: 4, color: "#666", fontSize: 12 }}>{formatTimestamp(ts)}</div> : null}
    </div>
  );
}
