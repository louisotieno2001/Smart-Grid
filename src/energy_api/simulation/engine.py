# Author: Jerry Onyango
# Contribution: Runs deterministic battery/solar/load simulation and returns baseline-vs-optimized savings metrics.

# /Users/loan/Desktop/energyallocation/src/energy_api/simulation/engine.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


ActionType = Literal["charge", "discharge", "idle"]


@dataclass(frozen=True)
class SimulatedSite:
    capacity_kwh: float
    max_charge_kw: float
    max_discharge_kw: float
    round_trip_efficiency: float
    demand_profile: list[float]
    solar_profile: list[float]
    tariff_profile: list[float]
    initial_soc: float = 50.0


@dataclass(frozen=True)
class SimulationResult:
    baseline_cost: float
    optimized_cost: float
    savings_percent: float
    battery_cycles: float
    self_consumption_percent: float
    peak_demand_reduction: float
    action_history: list[dict[str, float | str]]


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def run_simulation(site: SimulatedSite, step_minutes: int = 5) -> SimulationResult:
    if not (len(site.demand_profile) == len(site.solar_profile) == len(site.tariff_profile)):
        raise ValueError("demand_profile, solar_profile, and tariff_profile must have same length")

    dt_hours = step_minutes / 60.0
    efficiency = max(0.01, site.round_trip_efficiency)

    soc = site.initial_soc
    baseline_soc = site.initial_soc

    baseline_cost = 0.0
    optimized_cost = 0.0
    baseline_peak = 0.0
    optimized_peak = 0.0
    charge_throughput_kwh = 0.0
    pv_used_baseline = 0.0
    pv_used_optimized = 0.0

    action_history: list[dict[str, float | str]] = []

    for idx, (load_kw, pv_kw, price) in enumerate(zip(site.demand_profile, site.solar_profile, site.tariff_profile, strict=True)):
        # Baseline policy: solar serves load, then charges battery, excess curtailed.
        baseline_charge_kw = 0.0
        if pv_kw > load_kw and baseline_soc < 100.0:
            baseline_charge_kw = min(site.max_charge_kw, pv_kw - load_kw)
        baseline_discharge_kw = 0.0

        baseline_soc = _clamp(
            baseline_soc + (baseline_charge_kw * efficiency * dt_hours / site.capacity_kwh * 100.0)
            - (baseline_discharge_kw / efficiency * dt_hours / site.capacity_kwh * 100.0),
            0.0,
            100.0,
        )

        baseline_net_kw = load_kw - pv_kw - baseline_discharge_kw + baseline_charge_kw
        baseline_import_kw = max(0.0, baseline_net_kw)
        baseline_cost += baseline_import_kw * price * dt_hours
        baseline_peak = max(baseline_peak, baseline_import_kw)
        pv_used_baseline += min(load_kw + baseline_charge_kw, pv_kw)

        # Optimized simple strategy
        action: ActionType = "idle"
        charge_kw = 0.0
        discharge_kw = 0.0
        if pv_kw > load_kw and soc < 100.0:
            action = "charge"
            charge_kw = min(site.max_charge_kw, pv_kw - load_kw)
        elif price > 0.28 and soc > 25.0:
            action = "discharge"
            discharge_kw = min(site.max_discharge_kw, load_kw)
        elif price < 0.12 and soc < 95.0:
            action = "charge"
            charge_kw = min(site.max_charge_kw, 2.0)

        soc = _clamp(
            soc + (charge_kw * efficiency * dt_hours / site.capacity_kwh * 100.0)
            - (discharge_kw / efficiency * dt_hours / site.capacity_kwh * 100.0),
            0.0,
            100.0,
        )

        net_kw = load_kw - pv_kw - discharge_kw + charge_kw
        import_kw = max(0.0, net_kw)
        optimized_cost += import_kw * price * dt_hours
        optimized_peak = max(optimized_peak, import_kw)
        charge_throughput_kwh += (charge_kw + discharge_kw) * dt_hours
        pv_used_optimized += min(load_kw + charge_kw, pv_kw)

        action_history.append(
            {
                "step": idx,
                "action": action,
                "target_power_kw": round(charge_kw if action == "charge" else discharge_kw, 4),
                "soc": round(soc, 4),
                "price": round(price, 4),
            }
        )

    savings_percent = 0.0
    if baseline_cost > 0:
        savings_percent = ((baseline_cost - optimized_cost) / baseline_cost) * 100.0

    battery_cycles = charge_throughput_kwh / (2.0 * max(site.capacity_kwh, 0.1))
    total_pv = max(sum(site.solar_profile), 0.1)
    self_consumption_percent = (pv_used_optimized / total_pv) * 100.0
    peak_demand_reduction = max(0.0, baseline_peak - optimized_peak)

    return SimulationResult(
        baseline_cost=round(baseline_cost, 4),
        optimized_cost=round(optimized_cost, 4),
        savings_percent=round(savings_percent, 4),
        battery_cycles=round(battery_cycles, 4),
        self_consumption_percent=round(self_consumption_percent, 4),
        peak_demand_reduction=round(peak_demand_reduction, 4),
        action_history=action_history,
    )
