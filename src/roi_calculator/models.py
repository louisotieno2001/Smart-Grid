# Author: Jerry Onyango
# Contribution: Defines ROI input/output and sensitivity case data models used by financial calculation workflows.
from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ROIInput:
    annual_energy_spend_eur: float
    facilities_count: int
    appliances_count: int
    avg_tariff_eur_per_kwh: float
    production_profile: str
    data_availability_pct: float
    optimization_maturity: str
    implementation_capacity: str
    target_payback_months: float
    benchmark_inefficiency_pct: float
    adoption_rate_pct: float
    realization_confidence_pct: float
    annual_platform_cost_eur: float
    annual_implementation_cost_eur: float


@dataclass(frozen=True)
class SensitivityCase:
    name: str
    projected_savings_eur: float
    realized_savings_eur: float
    net_annual_value_eur: float
    payback_months: float
    roi_pct: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ROIOutput:
    projected_savings_eur: float
    realized_savings_eur: float
    net_annual_value_eur: float
    first_year_cost_eur: float
    payback_months: float
    roi_pct: float
    meets_target_payback: bool
    sensitivity: list[SensitivityCase]

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["sensitivity"] = [case.to_dict() for case in self.sensitivity]
        return payload
