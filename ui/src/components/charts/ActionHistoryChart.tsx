import React from "react";

type ActionPoint = {
  ts: string;
  action: string;
  target_power_kw: number;
  score?: number;
};

type Props = {
  points: ActionPoint[];
};

export function ActionHistoryChart({ points }: Props) {
  if (!points.length) return <div style={{ color: "#666" }}>No action history</div>;
  const max = Math.max(...points.map((p) => Math.abs(p.target_power_kw)), 1);
  return (
    <div style={{ display: "grid", gap: 6 }}>
      {points.slice(-12).map((p, idx) => (
        <div key={`${p.ts}-${idx}`} style={{ display: "flex", gap: 8, alignItems: "center", fontSize: 12 }}>
          <span style={{ width: 90 }}>{p.action}</span>
          <div style={{ height: 8, background: "#e3f2fd", width: `${(Math.abs(p.target_power_kw) / max) * 260}px`, borderRadius: 4 }} />
          <span>{p.target_power_kw.toFixed(2)} kW</span>
        </div>
      ))}
    </div>
  );
}
