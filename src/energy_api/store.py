# Author: Jerry Onyango
# Contribution: Provides PostgreSQL-backed state persistence for all entities (facilities, ingestion, modeling, recommendations, integrations).
from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import psycopg
from psycopg.types.json import Jsonb


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _get_db_url() -> str:
    return os.getenv(
        "EA_DATABASE_URL",
        "postgresql://energyallocation:energyallocation@localhost:5432/energyallocation",
    )


class PostgresEntityMap:
    """Dict-like interface wrapping PostgreSQL entity queries."""
    
    def __init__(self, store: PostgresStore, entity: str) -> None:
        self._store = store
        self._entity = entity

    def get(self, key: str, default: Any = None) -> Any:
        value = self._store.get_value(self._entity, key)
        return default if value is None else value

    def __getitem__(self, key: str) -> dict[str, Any]:
        value = self._store.get_value(self._entity, key)
        if value is None:
            raise KeyError(key)
        return value

    def __setitem__(self, key: str, value: dict[str, Any]) -> None:
        self._store.upsert_value(self._entity, key, value)

    def __contains__(self, key: str) -> bool:
        return self._store.get_value(self._entity, key) is not None

    def values(self) -> list[dict[str, Any]]:
        return self._store.list_values(self._entity)


class PostgresStore:
    """PostgreSQL-backed domain entity store using JSONB state table."""
    
    ENTITY_NAMES = {
        "organizations",
        "users",
        "facilities",
        "connectors",
        "appliances",
        "import_jobs",
        "feature_jobs",
        "model_runs",
        "recommendations",
        "alerts",
        "drift_events",
        "retraining_jobs",
        "demo_requests",
        "pricing_inquiries",
        "audit_logs",
        "webhooks",
        "partners",
        "partner_api_keys",
        "partner_webhooks",
        "partner_allocations",
        "integration_audit_logs",
    }

    def __init__(self, db_url: str) -> None:
        self._db_url = db_url
        self._ensure_schema()

        self.organizations = PostgresEntityMap(self, "organizations")
        self.users = PostgresEntityMap(self, "users")
        self.facilities = PostgresEntityMap(self, "facilities")
        self.connectors = PostgresEntityMap(self, "connectors")
        self.appliances = PostgresEntityMap(self, "appliances")
        self.import_jobs = PostgresEntityMap(self, "import_jobs")
        self.feature_jobs = PostgresEntityMap(self, "feature_jobs")
        self.model_runs = PostgresEntityMap(self, "model_runs")
        self.recommendations = PostgresEntityMap(self, "recommendations")
        self.alerts = PostgresEntityMap(self, "alerts")
        self.drift_events = PostgresEntityMap(self, "drift_events")
        self.retraining_jobs = PostgresEntityMap(self, "retraining_jobs")
        self.demo_requests = PostgresEntityMap(self, "demo_requests")
        self.pricing_inquiries = PostgresEntityMap(self, "pricing_inquiries")
        self.audit_logs = PostgresEntityMap(self, "audit_logs")
        self.webhooks = PostgresEntityMap(self, "webhooks")
        self.partners = PostgresEntityMap(self, "partners")
        self.partner_api_keys = PostgresEntityMap(self, "partner_api_keys")
        self.partner_webhooks = PostgresEntityMap(self, "partner_webhooks")
        self.partner_allocations = PostgresEntityMap(self, "partner_allocations")
        self.integration_audit_logs = PostgresEntityMap(self, "integration_audit_logs")

    def _connect(self):
        return psycopg.connect(self._db_url, autocommit=True)

    def _ensure_schema(self) -> None:
        """Create app_state table if missing."""
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS app_state (
                      entity TEXT NOT NULL,
                      key TEXT NOT NULL,
                      payload JSONB NOT NULL,
                      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                      updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                      PRIMARY KEY (entity, key)
                    );
                    CREATE INDEX IF NOT EXISTS idx_app_state_entity_updated 
                      ON app_state(entity, updated_at DESC);
                    """
                )

    def get_value(self, entity: str, key: str) -> dict[str, Any] | None:
        if entity not in self.ENTITY_NAMES:
            raise KeyError(entity)
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT payload FROM app_state WHERE entity = %s AND key = %s",
                    (entity, key),
                )
                row = cur.fetchone()
                return row[0] if row else None

    def upsert_value(self, entity: str, key: str, value: dict[str, Any]) -> None:
        if entity not in self.ENTITY_NAMES:
            raise KeyError(entity)
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO app_state (entity, key, payload)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (entity, key)
                    DO UPDATE SET payload = EXCLUDED.payload, updated_at = now()
                    """,
                    (entity, key, Jsonb(value)),
                )

    def list_values(self, entity: str) -> list[dict[str, Any]]:
        if entity not in self.ENTITY_NAMES:
            raise KeyError(entity)
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT payload FROM app_state WHERE entity = %s ORDER BY updated_at DESC",
                    (entity,),
                )
                return [row[0] for row in cur.fetchall()]

    def make_id(self, prefix: str) -> str:
        return f"{prefix}_{uuid4().hex[:8]}"

    def make_async_job(self, prefix: str, seed: dict[str, Any]) -> dict[str, Any]:
        job_id = self.make_id(prefix)
        payload = {"job_id": job_id, "status": "queued", "created_at": _now_iso(), **seed}
        return payload


# Initialize global store with Postgres backend (required, no fallback).
store = PostgresStore(_get_db_url())
