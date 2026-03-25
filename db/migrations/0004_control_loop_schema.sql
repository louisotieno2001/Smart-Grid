-- /Users/loan/Desktop/energyallocation/db/migrations/0004_control_loop_schema.sql
CREATE TABLE IF NOT EXISTS sites (
  id TEXT PRIMARY KEY,
  organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
  name TEXT NOT NULL,
  timezone TEXT NOT NULL DEFAULT 'UTC',
  polling_interval_seconds INT NOT NULL DEFAULT 300,
  reserve_soc_min NUMERIC(6,2) NOT NULL DEFAULT 20,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS assets (
  id TEXT PRIMARY KEY,
  site_id TEXT NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
  asset_type TEXT NOT NULL,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS devices (
  id TEXT PRIMARY KEY,
  site_id TEXT NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
  asset_id TEXT REFERENCES assets(id) ON DELETE SET NULL,
  device_type TEXT NOT NULL,
  protocol TEXT NOT NULL DEFAULT 'modbus_tcp',
  polling_interval_seconds INT NOT NULL DEFAULT 300,
  timeout_seconds INT NOT NULL DEFAULT 10,
  status TEXT NOT NULL DEFAULT 'online',
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS telemetry_streams (
  id TEXT PRIMARY KEY,
  site_id TEXT NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
  device_id TEXT REFERENCES devices(id) ON DELETE SET NULL,
  canonical_key TEXT NOT NULL,
  unit TEXT,
  is_critical BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(site_id, canonical_key)
);

CREATE TABLE IF NOT EXISTS telemetry_points (
  id BIGSERIAL PRIMARY KEY,
  stream_id TEXT NOT NULL REFERENCES telemetry_streams(id) ON DELETE CASCADE,
  ts TIMESTAMPTZ NOT NULL,
  value DOUBLE PRECISION NOT NULL,
  unit TEXT,
  quality TEXT NOT NULL,
  ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(stream_id, ts)
);

CREATE TABLE IF NOT EXISTS tariffs (
  id TEXT PRIMARY KEY,
  site_id TEXT NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
  import_price_eur_kwh DOUBLE PRECISION NOT NULL,
  export_price_eur_kwh DOUBLE PRECISION NOT NULL,
  valid_from TIMESTAMPTZ,
  valid_to TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS control_policies (
  id TEXT PRIMARY KEY,
  site_id TEXT NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
  active BOOLEAN NOT NULL DEFAULT TRUE,
  reserve_soc_min DOUBLE PRECISION NOT NULL DEFAULT 20,
  high_price_threshold DOUBLE PRECISION NOT NULL DEFAULT 0.30,
  low_price_threshold DOUBLE PRECISION NOT NULL DEFAULT 0.12,
  battery_temp_max_c DOUBLE PRECISION NOT NULL DEFAULT 45,
  max_charge_kw DOUBLE PRECISION NOT NULL DEFAULT 3,
  max_discharge_kw DOUBLE PRECISION NOT NULL DEFAULT 3,
  pending_ack_block_seconds INT NOT NULL DEFAULT 30,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS optimization_runs (
  id TEXT PRIMARY KEY,
  site_id TEXT NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
  mode TEXT NOT NULL,
  horizon_minutes INT NOT NULL,
  step_minutes INT NOT NULL,
  action_type TEXT NOT NULL,
  target_power_kw DOUBLE PRECISION,
  score_json JSONB NOT NULL,
  explanation JSONB NOT NULL,
  state_json JSONB NOT NULL,
  command_id TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS commands (
  id TEXT PRIMARY KEY,
  site_id TEXT NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
  device_id TEXT REFERENCES devices(id) ON DELETE SET NULL,
  command_type TEXT NOT NULL,
  target_power_kw DOUBLE PRECISION,
  target_soc DOUBLE PRECISION,
  reason TEXT,
  status TEXT NOT NULL,
  idempotency_key TEXT,
  failure_reason TEXT,
  requested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  sent_at TIMESTAMPTZ,
  acked_at TIMESTAMPTZ,
  UNIQUE(site_id, idempotency_key)
);

CREATE TABLE IF NOT EXISTS savings_snapshots (
  id TEXT PRIMARY KEY,
  site_id TEXT NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
  window_start TIMESTAMPTZ NOT NULL,
  window_end TIMESTAMPTZ NOT NULL,
  baseline_cost DOUBLE PRECISION NOT NULL,
  optimized_cost DOUBLE PRECISION NOT NULL,
  savings_percent DOUBLE PRECISION NOT NULL,
  battery_cycles DOUBLE PRECISION NOT NULL,
  self_consumption_percent DOUBLE PRECISION NOT NULL,
  peak_demand_reduction DOUBLE PRECISION NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS point_mappings (
  id TEXT PRIMARY KEY,
  device_id TEXT NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
  source_key TEXT NOT NULL,
  canonical_key TEXT NOT NULL,
  value_type TEXT NOT NULL DEFAULT 'float32',
  scale_factor DOUBLE PRECISION NOT NULL DEFAULT 1.0,
  byte_order TEXT NOT NULL DEFAULT 'big',
  word_order TEXT NOT NULL DEFAULT 'big',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(device_id, source_key)
);

CREATE INDEX IF NOT EXISTS idx_telemetry_points_stream_ts ON telemetry_points(stream_id, ts DESC);
