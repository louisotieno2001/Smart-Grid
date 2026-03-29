from __future__ import annotations

import json
import os
from dataclasses import dataclass

from .types import PointMapping


DEFAULT_POINT_MAPPINGS: list[PointMapping] = [
    PointMapping(canonical_key="battery_soc", register_address=0, register_count=1, value_type="uint16", scale_factor=0.1, unit="%", critical=True),
    PointMapping(canonical_key="battery_power_kw", register_address=1, register_count=1, value_type="int16", signed=True, scale_factor=0.1, unit="kW", critical=True),
    PointMapping(canonical_key="pv_kw", register_address=2, register_count=2, value_type="float32", unit="kW", critical=True),
    PointMapping(canonical_key="load_kw", register_address=4, register_count=2, value_type="float32", unit="kW", critical=True),
    PointMapping(canonical_key="grid_import_kw", register_address=6, register_count=2, value_type="float32", unit="kW", critical=True),
    PointMapping(canonical_key="grid_export_kw", register_address=8, register_count=2, value_type="float32", unit="kW", critical=True),
    PointMapping(canonical_key="battery_temp_c", register_address=10, register_count=1, value_type="int16", signed=True, scale_factor=0.1, unit="C", critical=True),
    PointMapping(canonical_key="price_import", register_address=11, register_count=2, value_type="float32", unit="EUR/kWh", critical=True),
    PointMapping(canonical_key="price_export", register_address=13, register_count=2, value_type="float32", unit="EUR/kWh", critical=True),
]


@dataclass(frozen=True)
class EdgeServiceSettings:
    runtime_mode: str
    log_level: str
    site_id: str
    gateway_id: str
    sqlite_path: str
    status_file_path: str
    api_base_url: str
    api_timeout_seconds: float
    api_bearer_token: str | None
    modbus_host: str
    modbus_port: int
    modbus_timeout_seconds: float
    modbus_unit_id: int
    poll_interval_seconds: int
    command_interval_seconds: int
    status_interval_seconds: int
    replay_limit: int
    replay_base_backoff_seconds: int
    replay_max_backoff_seconds: int
    shutdown_grace_seconds: int
    continue_on_poll_error: bool
    point_mappings: list[PointMapping]

    @staticmethod
    def from_env() -> "EdgeServiceSettings":
        return EdgeServiceSettings(
            runtime_mode=os.getenv("EDGE_RUNTIME_MODE", "service"),
            log_level=os.getenv("EDGE_LOG_LEVEL", "INFO"),
            site_id=os.getenv("EDGE_SITE_ID", "site_001"),
            gateway_id=os.getenv("EDGE_GATEWAY_ID", "gw_edge_01"),
            sqlite_path=os.getenv("EDGE_SQLITE_PATH", "./data/edge/edge_runtime.db"),
            status_file_path=os.getenv("EDGE_STATUS_FILE", "./data/edge/status.json"),
            api_base_url=os.getenv("EA_API_BASE_URL", "http://localhost:8000"),
            api_timeout_seconds=float(os.getenv("EDGE_API_TIMEOUT_SECONDS", "10.0")),
            api_bearer_token=os.getenv("EDGE_API_BEARER_TOKEN"),
            modbus_host=os.getenv("EDGE_MODBUS_HOST", "127.0.0.1"),
            modbus_port=int(os.getenv("EDGE_MODBUS_PORT", "15020")),
            modbus_timeout_seconds=float(os.getenv("EDGE_MODBUS_TIMEOUT_SECONDS", "3.0")),
            modbus_unit_id=int(os.getenv("EDGE_MODBUS_UNIT_ID", "1")),
            poll_interval_seconds=max(1, int(os.getenv("EDGE_POLL_INTERVAL_SECONDS", "5"))),
            command_interval_seconds=max(1, int(os.getenv("EDGE_COMMAND_INTERVAL_SECONDS", "5"))),
            status_interval_seconds=max(1, int(os.getenv("EDGE_STATUS_INTERVAL_SECONDS", "10"))),
            replay_limit=max(1, int(os.getenv("EDGE_REPLAY_LIMIT", "500"))),
            replay_base_backoff_seconds=max(1, int(os.getenv("EDGE_REPLAY_BASE_BACKOFF_SECONDS", "2"))),
            replay_max_backoff_seconds=max(1, int(os.getenv("EDGE_REPLAY_MAX_BACKOFF_SECONDS", "60"))),
            shutdown_grace_seconds=max(1, int(os.getenv("EDGE_SHUTDOWN_GRACE_SECONDS", "10"))),
            continue_on_poll_error=_as_bool(os.getenv("EDGE_CONTINUE_ON_POLL_ERROR", "true")),
            point_mappings=_load_point_mappings(),
        )


def _as_bool(raw: str | None) -> bool:
    return str(raw or "").strip().lower() in {"1", "true", "yes", "on"}


def _load_point_mappings() -> list[PointMapping]:
    raw = os.getenv("EDGE_POINT_MAPPINGS_JSON")
    if not raw:
        return DEFAULT_POINT_MAPPINGS

    try:
        payload = json.loads(raw)
        if not isinstance(payload, list):
            return DEFAULT_POINT_MAPPINGS
        output: list[PointMapping] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            output.append(
                PointMapping(
                    canonical_key=str(item["canonical_key"]),
                    register_address=int(item.get("register_address", 0)),
                    register_count=int(item.get("register_count", 1)),
                    value_type=str(item.get("value_type", "float32")),
                    scale_factor=float(item.get("scale_factor", 1.0)),
                    signed=bool(item.get("signed", False)),
                    byte_order=str(item.get("byte_order", "big")),
                    word_order=str(item.get("word_order", "big")),
                    unit=item.get("unit"),
                    critical=bool(item.get("critical", False)),
                )
            )
        return output or DEFAULT_POINT_MAPPINGS
    except Exception:
        return DEFAULT_POINT_MAPPINGS
