# Author: Jerry Onyango
# Contribution: Exposes /api/v1 control-loop endpoints for telemetry ingest, optimization, commanding, savings, and simulation.

# /Users/loan/Desktop/energyallocation/src/energy_api/routers/control_loop.py
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from energy_api.control import CommandDispatcher, ControlRepository, RuleEngine, StateEngine
from energy_api.security import require_roles
from energy_api.savings import SavingsService
from energy_api.simulation import SimulatedSite, run_simulation

router = APIRouter(prefix="/api/v1", tags=["Control Loop"])


class TelemetryPointIn(BaseModel):
    canonical_key: str
    ts: datetime
    value: float
    unit: str | None = None
    quality: Literal["good", "bad", "suspect"] = "good"


class TelemetryBatchIn(BaseModel):
    site_id: str
    gateway_id: str
    points: list[TelemetryPointIn] = Field(min_length=1)


class OptimizeRunIn(BaseModel):
    mode: Literal["live", "simulation", "backtest"] = "live"
    horizon_minutes: int = 60
    step_minutes: int = 5
    allow_export: bool = True
    reserve_soc_min: float = 20.0
    forecast_peak: bool = False


class SiteIn(BaseModel):
    site_id: str
    name: str
    timezone: str = "UTC"
    reserve_soc_min: float = 20.0
    polling_interval_seconds: int = 300


class DeviceIn(BaseModel):
    device_type: str = "battery_inverter"
    protocol: str = "modbus_tcp"
    metadata: dict[str, object] = Field(default_factory=dict)


class CommandIn(BaseModel):
    command_type: Literal["charge", "discharge", "idle", "set_limit", "set_mode"]
    target_power_kw: float | None = None
    target_soc: float | None = None
    reason: str
    idempotency_key: str | None = None


def _score_payload(action) -> dict[str, float]:
    return {
        "energy_cost": action.score.energy_cost,
        "battery_degradation_penalty": action.score.battery_degradation_penalty,
        "reserve_violation_penalty": action.score.reserve_violation_penalty,
        "command_churn_penalty": action.score.command_churn_penalty,
        "device_safety_penalty": action.score.device_safety_penalty,
        "total": action.score.total,
    }


@router.get("/sites")
def list_sites(
    _principal: dict[str, Any] = Depends(require_roles("client_admin", "facility_manager", "energy_analyst", "viewer", "ops_admin", "ml_engineer")),
) -> dict[str, Any]:
    repo = ControlRepository()
    return {"items": repo.list_sites()}


@router.post("/sites", status_code=201)
def create_site(
    payload: SiteIn,
    _principal: dict[str, Any] = Depends(require_roles("client_admin", "ops_admin", "ml_engineer")),
) -> dict[str, Any]:
    repo = ControlRepository()
    created = repo.create_site(
        site_id=payload.site_id,
        name=payload.name,
        timezone=payload.timezone,
        reserve_soc_min=payload.reserve_soc_min,
        polling_interval_seconds=payload.polling_interval_seconds,
    )
    repo.upsert_site_defaults(payload.site_id)
    return created


@router.get("/sites/{site_id}")
def get_site(
    site_id: str,
    _principal: dict[str, Any] = Depends(require_roles("client_admin", "facility_manager", "energy_analyst", "viewer", "ops_admin", "ml_engineer")),
) -> dict[str, Any]:
    repo = ControlRepository()
    site = repo.get_site(site_id)
    if not site:
        raise HTTPException(status_code=404, detail="site not found")
    return site


@router.post("/sites/{site_id}/devices", status_code=201)
def create_device(
    site_id: str,
    payload: DeviceIn,
    _principal: dict[str, Any] = Depends(require_roles("client_admin", "facility_manager", "ops_admin", "ml_engineer")),
) -> dict[str, Any]:
    repo = ControlRepository()
    site = repo.get_site(site_id)
    if not site:
        raise HTTPException(status_code=404, detail="site not found")
    return repo.create_device(
        site_id=site_id,
        device_type=payload.device_type,
        protocol=payload.protocol,
        metadata=payload.metadata,
    )


@router.post("/telemetry/ingest")
def ingest_telemetry(
    payload: TelemetryBatchIn,
    _principal: dict[str, Any] = Depends(require_roles("client_admin", "facility_manager", "ops_admin", "ml_engineer")),
) -> dict[str, Any]:
    repo = ControlRepository()
    repo.upsert_site_defaults(payload.site_id)

    keys = [point.canonical_key for point in payload.points]
    stream_map = repo.resolve_stream_ids(payload.site_id, keys)

    missing = sorted({key for key in keys if key not in stream_map})
    if missing:
        raise HTTPException(status_code=400, detail={"missing_streams": missing})

    rows = []
    for point in payload.points:
        stream = stream_map[point.canonical_key]
        rows.append(
            {
                "stream_id": stream["id"],
                "ts": point.ts.astimezone(UTC),
                "value": point.value,
                "unit": point.unit or stream.get("unit"),
                "quality": point.quality,
            }
        )

    inserted = repo.insert_telemetry_points(rows)
    return {
        "site_id": payload.site_id,
        "gateway_id": payload.gateway_id,
        "received": len(payload.points),
        "inserted": inserted,
        "deduplicated": len(payload.points) - inserted,
    }


@router.post("/sites/{site_id}/optimize/run")
def optimize_run(
    site_id: str,
    payload: OptimizeRunIn,
    _principal: dict[str, Any] = Depends(require_roles("client_admin", "facility_manager", "energy_analyst", "ops_admin", "ml_engineer")),
) -> dict[str, Any]:
    repo = ControlRepository()
    state_engine = StateEngine(repo)
    rule_engine = RuleEngine()
    dispatcher = CommandDispatcher(repo)

    policy = repo.get_active_policy(site_id)
    policy["reserve_soc_min"] = payload.reserve_soc_min

    state = state_engine.build_site_state(site_id)
    action = rule_engine.evaluate(state, policy, forecast_peak=payload.forecast_peak)

    device_id = repo.get_primary_device_id(site_id)
    dispatch_result = dispatcher.dispatch(
        site_id=site_id,
        device_id=device_id,
        action=action,
        reason=f"optimize_run:{action.reason}",
        ack_block_seconds=int(policy.get("pending_ack_block_seconds", 30)),
    )

    run_id = repo.create_optimization_run(
        site_id=site_id,
        mode=payload.mode,
        horizon_minutes=payload.horizon_minutes,
        step_minutes=payload.step_minutes,
        action_type=action.action_type,
        target_power_kw=action.target_power_kw,
        score_json=_score_payload(action),
        explanation=action.explanation,
        state_json={
            "ts": state.ts.isoformat(),
            "pv_kw": state.pv_kw,
            "load_kw": state.load_kw,
            "battery_soc": state.battery_soc,
            "battery_power_kw": state.battery_power_kw,
            "grid_import_kw": state.grid_import_kw,
            "grid_export_kw": state.grid_export_kw,
            "battery_temp_c": state.battery_temp_c,
            "price_import": state.price_import,
            "price_export": state.price_export,
            "online": state.online,
        },
        command_id=dispatch_result.get("command", {}).get("id") if isinstance(dispatch_result.get("command"), dict) else None,
    )

    return {
        "optimization_run_id": run_id,
        "site_id": site_id,
        "mode": payload.mode,
        "state": {
            "ts": state.ts.isoformat(),
            "online": state.online,
        },
        "selected_action": {
            "command_type": action.action_type,
            "target_power_kw": action.target_power_kw,
            "score": _score_payload(action),
            "explanation": action.explanation,
        },
        "dispatch": dispatch_result,
        "mqtt_publish": {
            "topic": f"ems/{site_id}/command/request",
            "qos": 1,
            "status": "published_simulated",
        },
    }


@router.get("/sites/{site_id}/optimize/runs")
def list_optimize_runs(
    site_id: str,
    limit: int = 50,
    _principal: dict[str, Any] = Depends(require_roles("client_admin", "facility_manager", "energy_analyst", "viewer", "ops_admin", "ml_engineer")),
) -> dict[str, Any]:
    repo = ControlRepository()
    return {"items": repo.list_optimization_runs(site_id=site_id, limit=limit)}


@router.post("/sites/{site_id}/commands")
def issue_command(
    site_id: str,
    payload: CommandIn,
    _principal: dict[str, Any] = Depends(require_roles("client_admin", "facility_manager", "ops_admin", "ml_engineer")),
) -> dict[str, Any]:
    repo = ControlRepository()
    policy = repo.get_active_policy(site_id)
    device_id = repo.get_primary_device_id(site_id)
    dispatcher = CommandDispatcher(repo)

    # Build an adapter action-like object for direct commands
    action = RuleEngine().evaluate(
        StateEngine(repo).build_site_state(site_id),
        policy,
        forecast_peak=False,
    )
    action = type(action)(
        action_type=payload.command_type,
        target_power_kw=float(payload.target_power_kw or 0.0),
        score=action.score,
        explanation=action.explanation,
        reason=payload.reason,
    )

    result = dispatcher.dispatch(
        site_id=site_id,
        device_id=device_id,
        action=action,
        reason=payload.reason,
        target_soc=payload.target_soc,
        idempotency_key=payload.idempotency_key,
        ack_block_seconds=int(policy.get("pending_ack_block_seconds", 30)),
    )
    return result


@router.post("/commands/{command_id}/ack")
def acknowledge_command(
    command_id: str,
    _principal: dict[str, Any] = Depends(require_roles("client_admin", "facility_manager", "ops_admin", "ml_engineer")),
) -> dict[str, Any]:
    repo = ControlRepository()
    command = repo.get_command(command_id)
    if not command:
        raise HTTPException(status_code=404, detail="command not found")
    if command.get("status") == "acked":
        return command
    return repo.update_command_status(command_id, "acked")


@router.get("/sites/{site_id}/savings/summary")
def savings_summary(
    site_id: str,
    _principal: dict[str, Any] = Depends(require_roles("client_admin", "facility_manager", "energy_analyst", "viewer", "ops_admin")),
) -> dict[str, Any]:
    service = SavingsService(ControlRepository())
    return service.compute_summary(site_id)


@router.post("/sites/{site_id}/simulation/run")
def run_site_simulation(
    site_id: str,
    _principal: dict[str, Any] = Depends(require_roles("client_admin", "facility_manager", "energy_analyst", "ops_admin", "ml_engineer")),
) -> dict[str, Any]:
    # helper endpoint for local validation of simulation engine without DB coupling
    demand = [3.2, 3.5, 3.0, 2.8, 3.1, 3.7, 3.9, 4.0, 3.8, 3.4, 3.0, 2.9]
    solar = [0.0, 0.1, 0.3, 0.8, 1.4, 2.3, 2.8, 2.6, 2.0, 1.2, 0.4, 0.1]
    tariff = [0.09, 0.09, 0.11, 0.12, 0.15, 0.24, 0.31, 0.34, 0.32, 0.20, 0.14, 0.10]
    result = run_simulation(
        SimulatedSite(
            capacity_kwh=20,
            max_charge_kw=3,
            max_discharge_kw=3,
            round_trip_efficiency=0.92,
            demand_profile=demand,
            solar_profile=solar,
            tariff_profile=tariff,
            initial_soc=50,
        )
    )
    return {
        "site_id": site_id,
        "baseline_cost": result.baseline_cost,
        "optimized_cost": result.optimized_cost,
        "savings_percent": result.savings_percent,
        "battery_cycles": result.battery_cycles,
        "self_consumption_percent": result.self_consumption_percent,
        "peak_demand_reduction": result.peak_demand_reduction,
        "action_history": result.action_history,
    }
