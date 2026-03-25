import React from "react";
import type { CommandStatus, DeviceStatus } from "../../types";

const commandStatusColors: Record<CommandStatus, string> = {
  queued: "#9e9e9e",
  sent: "#1976d2",
  acknowledged: "#f9a825",
  executed: "#2e7d32",
  failed: "#c62828",
  rejected: "#ef6c00"
};

const deviceStatusColors: Record<DeviceStatus, string> = {
  active: "#2e7d32",
  inactive: "#9e9e9e",
  fault: "#c62828"
};

type BadgeProps = {
  kind: "command" | "device" | "plain";
  value: string;
};

export function Badge({ kind, value }: BadgeProps) {
  let color = "#607d8b";
  if (kind === "command") {
    color = commandStatusColors[value as CommandStatus] || color;
  }
  if (kind === "device") {
    color = deviceStatusColors[value as DeviceStatus] || color;
  }
  return (
    <span style={{ background: `${color}22`, color, borderRadius: 999, padding: "2px 8px", fontSize: 12, fontWeight: 600 }}>
      {value}
    </span>
  );
}
