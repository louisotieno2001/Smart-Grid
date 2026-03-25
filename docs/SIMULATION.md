<!-- /Users/loan/Desktop/energyallocation/docs/SIMULATION.md -->
# Simulation

## Implementation location
- `src/energy_api/simulation/engine.py::run_simulation`

## Physics equations (implemented)
Battery SOC update:
```text
soc_next = soc_current
           + (charge_kw * efficiency * dt_hours / capacity_kwh * 100)
           - (discharge_kw / efficiency * dt_hours / capacity_kwh * 100)
clamped to [0, 100]
```

Grid equation:
```text
net_kw = load_kw - pv_kw - battery_discharge_kw + battery_charge_kw
net_kw > 0 => grid import
net_kw < 0 => export/curtail (only import tracked in current outputs)
```

## Baseline policy (implemented)
- No tariff-aware discharge.
- Solar serves load first.
- Surplus solar charges battery up to max charge rate.
- Remaining surplus is effectively curtailed.

## Simulation step sequence
1. Compute baseline action and update baseline SOC.
2. Compute optimized action from simple rules.
3. Update optimized SOC with physics equations.
4. Compute import cost and peaks.
5. Append `action_history` record.

## Output metrics
- `baseline_cost`
- `optimized_cost`
- `savings_percent`
- `battery_cycles`
- `self_consumption_percent`
- `peak_demand_reduction`
- `action_history`

## Assumptions and limitations
- No database dependency; pure in-memory function.
- No feeder export tariff settlement in result cost.
- No degradation model beyond throughput-derived cycles.
