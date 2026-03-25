import React from "react";

type Point = { ts: string; value: number };

type Props = {
  points: Point[];
};

export function TelemetryLineChart({ points }: Props) {
  if (!points.length) {
    return <div style={{ color: "#666" }}>No data</div>;
  }

  const width = 600;
  const height = 180;
  const values = points.map((p) => p.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const scaleY = (v: number) => {
    if (max === min) return height / 2;
    return height - ((v - min) / (max - min)) * (height - 20) - 10;
  };

  const d = points
    .map((p, i) => {
      const x = (i / Math.max(points.length - 1, 1)) * (width - 20) + 10;
      const y = scaleY(p.value);
      return `${i === 0 ? "M" : "L"}${x},${y}`;
    })
    .join(" ");

  return (
    <svg width="100%" viewBox={`0 0 ${width} ${height}`}>
      <path d={d} stroke="#1976d2" fill="none" strokeWidth={2} />
    </svg>
  );
}
