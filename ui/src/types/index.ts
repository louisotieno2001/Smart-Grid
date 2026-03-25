export type UUID = string;

export type Site = {
  id: UUID;
  name: string;
  timezone: string;
  reserve_soc_min: number;
  polling_interval_seconds: number;
  created_at: string;
  updated_at: string;
};

export type SiteCreateBody = {
  site_id: string;
  name: string;
  timezone: string;
  reserve_soc_min: number;
  polling_interval_seconds: number;
};

export type AssetType = "battery" | "inverter" | "meter" | "pv_array" | "load" | "gateway";
export type Protocol = "modbus_tcp" | "mqtt" | "rest" | "simulated";
export type DeviceStatus = "active" | "inactive" | "fault";

export type Device = {
  id: UUID;
  site_id: UUID;
  device_type: string;
  protocol: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type DeviceCreateBody = {
  device_type: string;
  protocol: string;
  metadata?: Record<string, unknown>;
};

export type TelemetryPointIn = {
  canonical_key: string;
  ts: string;
  value: number;
  unit: string;
  quality: "good" | "estimated" | "bad";
};

export type TelemetryIngestBody = {
  site_id: UUID;
  gateway_id: UUID;
  points: TelemetryPointIn[];
};

export type TelemetryIngestResponse = {
  site_id: string;
  gateway_id: string;
  received: number;
  inserted: number;
  deduplicated: number;
};

export type CommandType = "charge" | "discharge" | "idle" | "set_limit" | "set_mode";
export type CommandStatus = "queued" | "sent" | "acknowledged" | "executed" | "failed" | "rejected";

export type Command = {
  id: UUID;
  site_id: UUID;
  device_id: UUID | null;
  command_type: CommandType;
  target_power_kw: number | null;
  target_soc: number | null;
  reason: string | null;
  status: "queued" | "sent" | "acked" | "failed";
  failure_reason: string | null;
  requested_at: string;
  sent_at: string | null;
  acked_at: string | null;
};

export type CommandCreateBody = {
  command_type: CommandType;
  target_power_kw?: number;
  target_soc?: number;
  reason: string;
};

export type ExplanationPayload = {
  decision: string;
  target_power_kw: number;
  top_factors: Array<{ factor: string; value: number; effect: string }>;
  summary: string;
};

export type OptimizationRun = {
  id?: UUID;
  optimization_run_id?: UUID;
  site_id: UUID;
  mode: "live" | "simulation" | "backtest";
  action_type?: CommandType;
  target_power_kw?: number;
  created_at?: string;
  explanation?: ExplanationPayload;
  selected_action?: {
    command_type: CommandType;
    target_power_kw: number;
    explanation: ExplanationPayload;
  };
};

export type OptimizationRunBody = {
  mode: "live" | "simulation" | "backtest";
  horizon_minutes: number;
  step_minutes: number;
  allow_export: boolean;
  reserve_soc_min: number;
};

export type SavingsSummary = {
  snapshot_id: string;
  site_id: string;
  window_start: string;
  window_end: string;
  baseline_cost: number;
  optimized_cost: number;
  savings_percent: number;
  battery_cycles: number;
  self_consumption_percent: number;
  peak_demand_reduction: number;
};

export type SimulationRunBody = {
  mode: "simulation" | "backtest";
  horizon_minutes?: number;
  step_minutes?: number;
  allow_export?: boolean;
  reserve_soc_min?: number;
};

export type SimulationRunDetail = {
  site_id: string;
  baseline_cost: number;
  optimized_cost: number;
  savings_percent: number;
  battery_cycles: number;
  self_consumption_percent: number;
  peak_demand_reduction: number;
  action_history: Array<{
    step: number;
    action: CommandType;
    target_power_kw: number;
    soc: number;
    price: number;
  }>;
};

export type User = {
  id: UUID;
  email: string;
  full_name: string;
  role: string;
  organization_id: UUID;
};
