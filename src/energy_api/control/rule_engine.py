# Author: Jerry Onyango
# Contribution: Evaluates control policies against site state to choose scored actions and human-readable explanations.

# /Users/loan/Desktop/energyallocation/src/energy_api/control/rule_engine.py
from __future__ import annotations

from .models import ScoreBreakdown, ScoredAction, SiteState


class RuleEngine:
    # use a rules engine library or a machine learning model. Currently, we implement a simple rule-based approach for demonstration purposes.
    def evaluate(self, state: SiteState, policy: dict[str, object], forecast_peak: bool = False) -> ScoredAction:
        reserve_min = float(policy.get("reserve_soc_min", 20.0))
        high_price_threshold = float(policy.get("high_price_threshold", 0.30))
        low_price_threshold = float(policy.get("low_price_threshold", 0.12))
        max_charge_kw = float(policy.get("max_charge_kw", 3.0))
        max_discharge_kw = float(policy.get("max_discharge_kw", 3.0))
        battery_temp_max_c = float(policy.get("battery_temp_max_c", 45.0))

        if (not state.online) or (state.battery_temp_c > battery_temp_max_c): # safety halt if telemetry is offline or battery temperature is too high, regardless of other conditions
            score = self._score(
                state=state,
                action_type="idle",
                target_power_kw=0.0,
                reserve_min=reserve_min,
            )
            explanation = {
                "decision": "idle",
                "target_power_kw": 0.0,
                "top_factors": [
                    {"factor": "online", "value": state.online, "effect": "safe_mode"},
                    {"factor": "battery_temp_c", "value": state.battery_temp_c, "effect": "safety_halt"},
                ],
                "summary": "Safe mode: telemetry/device state is not trusted or temperature is high.",
            }
            return ScoredAction("idle", 0.0, score, explanation, "safe_mode")

        if state.pv_kw > state.load_kw and state.battery_soc < 100:
            target = min(max_charge_kw, max(0.0, state.pv_kw - state.load_kw))
            score = self._score(state, "charge", target, reserve_min)
            explanation = {
                "decision": "charge",
                "target_power_kw": round(target, 3),
                "top_factors": [
                    {"factor": "pv_surplus_kw", "value": round(state.pv_kw - state.load_kw, 3), "effect": "surplus_solar"},
                    {"factor": "battery_soc", "value": state.battery_soc, "effect": "store_surplus"},
                ],
                "summary": "Charging from surplus PV to avoid export and increase self-consumption.",
            }
            return ScoredAction("charge", target, score, explanation, "surplus_solar")

        if state.price_import >= high_price_threshold and state.battery_soc > reserve_min:
            target = min(max_discharge_kw, max(0.0, state.load_kw))
            score = self._score(state, "discharge", target, reserve_min)
            explanation = {
                "decision": "discharge",
                "target_power_kw": round(target, 3),
                "top_factors": [
                    {"factor": "import_price", "value": state.price_import, "effect": "high"},
                    {"factor": "battery_soc", "value": state.battery_soc, "effect": "enough_reserve"},
                ],
                "summary": "Discharging battery to reduce expensive grid imports while protecting reserve.",
            }
            return ScoredAction("discharge", target, score, explanation, "expensive_grid")

        if state.price_import <= low_price_threshold and forecast_peak and state.battery_soc < 95:
            target = min(max_charge_kw, 2.0)
            score = self._score(state, "charge", target, reserve_min)
            explanation = {
                "decision": "charge",
                "target_power_kw": round(target, 3),
                "top_factors": [
                    {"factor": "import_price", "value": state.price_import, "effect": "low"},
                    {"factor": "forecast_peak", "value": forecast_peak, "effect": "prepare_discharge"},
                ],
                "summary": "Charging from low-cost grid in anticipation of a forecasted peak period.",
            }
            return ScoredAction("charge", target, score, explanation, "cheap_grid_forecast_peak")

        score = self._score(state, "idle", 0.0, reserve_min)
        explanation = {
            "decision": "idle",
            "target_power_kw": 0.0,
            "top_factors": [
                {"factor": "import_price", "value": state.price_import, "effect": "neutral"},
                {"factor": "battery_soc", "value": state.battery_soc, "effect": "hold"},
            ],
            "summary": "No rule trigger exceeded; holding battery state.",
        }
        return ScoredAction("idle", 0.0, score, explanation, "idle_default")

    def _score(self, state: SiteState, action_type: str, target_power_kw: float, reserve_min: float) -> ScoreBreakdown:
        net_import_after_action = max(
            0.0,
            state.load_kw - state.pv_kw - (target_power_kw if action_type == "discharge" else 0.0),
        )
        energy_cost = net_import_after_action * max(state.price_import, 0.0)
        battery_degradation_penalty = abs(target_power_kw) * 0.01

        projected_soc = state.battery_soc
        if action_type == "charge":
            projected_soc += target_power_kw * 0.8
        elif action_type == "discharge":
            projected_soc -= target_power_kw * 0.8

        reserve_violation_penalty = 0.0 if projected_soc >= reserve_min else (reserve_min - projected_soc) * 0.5
        command_churn_penalty = 0.02 if action_type != "idle" else 0.0
        device_safety_penalty = max(0.0, state.battery_temp_c - 40.0) * 0.05

        return ScoreBreakdown(
            energy_cost=round(energy_cost, 6),
            battery_degradation_penalty=round(battery_degradation_penalty, 6),
            reserve_violation_penalty=round(reserve_violation_penalty, 6),
            command_churn_penalty=round(command_churn_penalty, 6),
            device_safety_penalty=round(device_safety_penalty, 6),
        )
