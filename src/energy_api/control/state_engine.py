# Author: Jerry Onyango
# Contribution: Builds a validated site state snapshot from latest telemetry with freshness and online checks.

# /Users/loan/Desktop/energyallocation/src/energy_api/control/state_engine.py
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from .models import SiteState
from .repository import ControlRepository


class StateEngine:
    CRITICAL_KEYS = {
        "pv_kw",
        "load_kw",
        "battery_soc",
        "battery_power_kw",
        "grid_import_kw",
        "grid_export_kw",
        "battery_temp_c",
        "price_import",
        "price_export",
    }

    def __init__(self, repository: ControlRepository | None = None) -> None:
        self.repository = repository or ControlRepository()

    def build_site_state(self, site_id: str) -> SiteState:
        polling_interval = self.repository.get_polling_interval(site_id)
        stale_cutoff = datetime.now(UTC) - timedelta(seconds=polling_interval * 2)
        latest = self.repository.get_latest_state_rows(site_id)

        def _value(key: str, default: float = 0.0) -> float:
            row = latest.get(key)
            if not row or row.get("value") is None:
                return default
            return float(row["value"])

        online = True
        newest_ts: datetime | None = None
        for key in self.CRITICAL_KEYS:
            row = latest.get(key)
            if not row or row.get("ts") is None:
                online = False
                continue
            ts = row["ts"]
            if ts < stale_cutoff:
                online = False
            if newest_ts is None or ts > newest_ts:
                newest_ts = ts

        if newest_ts is None:
            newest_ts = datetime.now(UTC)

        return SiteState(
            ts=newest_ts,
            pv_kw=_value("pv_kw"),
            load_kw=_value("load_kw"),
            battery_soc=_value("battery_soc"),
            battery_power_kw=_value("battery_power_kw"),
            grid_import_kw=_value("grid_import_kw"),
            grid_export_kw=_value("grid_export_kw"),
            battery_temp_c=_value("battery_temp_c", 25.0),
            price_import=_value("price_import", 0.20),
            price_export=_value("price_export", 0.05),
            online=online,
        )
