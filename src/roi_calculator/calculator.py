# Author: Jerry Onyango
# Contribution: Implements ROI, payback, and sensitivity-band calculations used in commercial proposal generation.
from __future__ import annotations

from dataclasses import replace

from .models import ROIInput, ROIOutput, SensitivityCase


MATURITY_MULTIPLIER = {
    "low": 0.85,
    "medium": 1.0,
    "high": 1.1,
}

CAPACITY_MULTIPLIER = {
    "low": 0.8,
    "medium": 1.0,
    "high": 1.15,
}

PROFILE_MULTIPLIER = {
    "24_7_heavy_industrial": 1.1,
    "mixed_shift": 1.0,
    "single_shift": 0.9,
}


def _guard_percent(value: float, name: str) -> float:
    if not 0 <= value <= 1:
        raise ValueError(f"{name} must be between 0 and 1")
    return value


def _safe_div(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0
    return numerator / denominator


def calculate_roi(inputs: ROIInput) -> ROIOutput:
    data_availability = _guard_percent(inputs.data_availability_pct, "data_availability_pct")
    adoption_rate = _guard_percent(inputs.adoption_rate_pct, "adoption_rate_pct")
    realization_confidence = _guard_percent(inputs.realization_confidence_pct, "realization_confidence_pct")

    maturity_mult = MATURITY_MULTIPLIER.get(inputs.optimization_maturity, 1.0)
    capacity_mult = CAPACITY_MULTIPLIER.get(inputs.implementation_capacity, 1.0)
    profile_mult = PROFILE_MULTIPLIER.get(inputs.production_profile, 1.0)

    projected_savings = (
        inputs.annual_energy_spend_eur
        * inputs.benchmark_inefficiency_pct
        * data_availability
        * maturity_mult
        * profile_mult
    )

    realized_savings = projected_savings * adoption_rate * realization_confidence * capacity_mult

    first_year_cost = inputs.annual_platform_cost_eur + inputs.annual_implementation_cost_eur
    net_annual_value = realized_savings - first_year_cost
    monthly_realized = realized_savings / 12
    payback_months = _safe_div(first_year_cost, monthly_realized)
    roi_pct = _safe_div(net_annual_value, first_year_cost) * 100 if first_year_cost > 0 else 0

    sensitivity = _build_sensitivity(inputs)

    return ROIOutput(
        projected_savings_eur=round(projected_savings, 2),
        realized_savings_eur=round(realized_savings, 2),
        net_annual_value_eur=round(net_annual_value, 2),
        first_year_cost_eur=round(first_year_cost, 2),
        payback_months=round(payback_months, 2),
        roi_pct=round(roi_pct, 2),
        meets_target_payback=payback_months <= inputs.target_payback_months,
        sensitivity=sensitivity,
    )


def _build_sensitivity(base_input: ROIInput) -> list[SensitivityCase]:
    presets = [
        ("conservative", 0.85, 0.9, 1.05),
        ("expected", 1.0, 1.0, 1.0),
        ("aggressive", 1.15, 1.05, 0.98),
    ]

    cases: list[SensitivityCase] = []
    for name, inefficiency_mult, realization_mult, cost_mult in presets:
        candidate = replace(
            base_input,
            benchmark_inefficiency_pct=base_input.benchmark_inefficiency_pct * inefficiency_mult,
            realization_confidence_pct=min(1.0, base_input.realization_confidence_pct * realization_mult),
            annual_platform_cost_eur=base_input.annual_platform_cost_eur * cost_mult,
            annual_implementation_cost_eur=base_input.annual_implementation_cost_eur * cost_mult,
        )
        result = calculate_roi_without_sensitivity(candidate)
        cases.append(
            SensitivityCase(
                name=name,
                projected_savings_eur=result.projected_savings_eur,
                realized_savings_eur=result.realized_savings_eur,
                net_annual_value_eur=result.net_annual_value_eur,
                payback_months=result.payback_months,
                roi_pct=result.roi_pct,
            )
        )

    return cases


def calculate_roi_without_sensitivity(inputs: ROIInput) -> ROIOutput:
    data_availability = _guard_percent(inputs.data_availability_pct, "data_availability_pct")
    adoption_rate = _guard_percent(inputs.adoption_rate_pct, "adoption_rate_pct")
    realization_confidence = _guard_percent(inputs.realization_confidence_pct, "realization_confidence_pct")

    maturity_mult = MATURITY_MULTIPLIER.get(inputs.optimization_maturity, 1.0)
    capacity_mult = CAPACITY_MULTIPLIER.get(inputs.implementation_capacity, 1.0)
    profile_mult = PROFILE_MULTIPLIER.get(inputs.production_profile, 1.0)

    projected_savings = (
        inputs.annual_energy_spend_eur
        * inputs.benchmark_inefficiency_pct
        * data_availability
        * maturity_mult
        * profile_mult
    )
    realized_savings = projected_savings * adoption_rate * realization_confidence * capacity_mult

    first_year_cost = inputs.annual_platform_cost_eur + inputs.annual_implementation_cost_eur
    net_annual_value = realized_savings - first_year_cost
    monthly_realized = realized_savings / 12
    payback_months = _safe_div(first_year_cost, monthly_realized)
    roi_pct = _safe_div(net_annual_value, first_year_cost) * 100 if first_year_cost > 0 else 0

    return ROIOutput(
        projected_savings_eur=round(projected_savings, 2),
        realized_savings_eur=round(realized_savings, 2),
        net_annual_value_eur=round(net_annual_value, 2),
        first_year_cost_eur=round(first_year_cost, 2),
        payback_months=round(payback_months, 2),
        roi_pct=round(roi_pct, 2),
        meets_target_payback=payback_months <= inputs.target_payback_months,
        sensitivity=[],
    )


def build_proposal(inputs: ROIInput) -> dict:
    result = calculate_roi(inputs)
    return {
        "client_profile": {
            "annual_energy_spend_eur": inputs.annual_energy_spend_eur,
            "facilities_count": inputs.facilities_count,
            "appliances_count": inputs.appliances_count,
            "avg_tariff_eur_per_kwh": inputs.avg_tariff_eur_per_kwh,
            "production_profile": inputs.production_profile,
        },
        "assumptions": {
            "benchmark_inefficiency_pct": inputs.benchmark_inefficiency_pct,
            "adoption_rate_pct": inputs.adoption_rate_pct,
            "realization_confidence_pct": inputs.realization_confidence_pct,
            "optimization_maturity": inputs.optimization_maturity,
            "implementation_capacity": inputs.implementation_capacity,
        },
        "financials": result.to_dict(),
    }
