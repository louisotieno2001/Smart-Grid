CREATE TABLE IF NOT EXISTS app_state (
  entity TEXT NOT NULL,
  key TEXT NOT NULL,
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (entity, key)
);

CREATE INDEX IF NOT EXISTS idx_app_state_entity_updated ON app_state(entity, updated_at DESC);
