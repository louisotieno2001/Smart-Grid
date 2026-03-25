# Author: Jerry Onyango
# Contribution: Implements baseline train-predict-evaluate-suggest logic for energy usage modeling from tabular readings.
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class PredictionRow:
    timestamp: str
    facility_id: str
    appliance_id: str
    category: str
    runtime_state: str
    ambient_temp_c: float
    tariff_eur_kwh: float
    power_kw: float


class BaselineEnergyPipeline:
    def __init__(self) -> None:
        self.group_means: dict[tuple[str, str], float] = {}
        self.global_mean: float = 0.0
        self.fitted: bool = False

    def fit(self, rows: Iterable[PredictionRow]) -> None:
        rows = list(rows)
        if not rows:
            raise ValueError("No rows provided for training")

        by_group: dict[tuple[str, str], list[float]] = {}
        total = 0.0
        for row in rows:
            key = (row.category, row.runtime_state)
            by_group.setdefault(key, []).append(row.power_kw)
            total += row.power_kw

        self.group_means = {key: sum(values) / len(values) for key, values in by_group.items()}
        self.global_mean = total / len(rows)
        self.fitted = True

    def predict(self, rows: Iterable[PredictionRow]) -> list[float]:
        if not self.fitted:
            raise RuntimeError("Pipeline must be fitted before prediction")

        predictions: list[float] = []
        for row in rows:
            key = (row.category, row.runtime_state)
            predictions.append(self.group_means.get(key, self.global_mean))
        return predictions

    def evaluate(self, rows: Iterable[PredictionRow]) -> dict[str, float]:
        rows = list(rows)
        preds = self.predict(rows)
        mae_total = 0.0
        mape_total = 0.0
        non_zero = 0
        for row, pred in zip(rows, preds, strict=True):
            err = abs(row.power_kw - pred)
            mae_total += err
            if row.power_kw != 0:
                mape_total += err / row.power_kw
                non_zero += 1

        mae = mae_total / len(rows)
        mape = (mape_total / non_zero) if non_zero else 0.0
        return {
            "mae_kw": round(mae, 4),
            "mape": round(mape, 4),
            "training_rows": float(len(rows)),
        }

    def suggest(self, rows: Iterable[PredictionRow]) -> list[dict[str, object]]:
        rows = list(rows)
        preds = self.predict(rows)
        suggestions: list[dict[str, object]] = []
        for row, pred in zip(rows, preds, strict=True):
            if row.runtime_state == "idle" and pred > 90:
                projected_kwh_day = pred * 3.0
                projected_savings_eur = projected_kwh_day * row.tariff_eur_kwh * 365
                suggestions.append(
                    {
                        "appliance_id": row.appliance_id,
                        "title": "Reduce off-shift idle runtime",
                        "projected_annual_savings_eur": round(projected_savings_eur, 2),
                        "confidence": 0.78,
                        "effort": "medium",
                    }
                )

        deduped: dict[str, dict[str, object]] = {}
        for item in suggestions:
            appliance_id = str(item["appliance_id"])
            if appliance_id not in deduped:
                deduped[appliance_id] = item
            else:
                deduped[appliance_id]["projected_annual_savings_eur"] = max(
                    float(deduped[appliance_id]["projected_annual_savings_eur"]),
                    float(item["projected_annual_savings_eur"]),
                )
        return list(deduped.values())


def load_training_rows(path: str | Path) -> list[PredictionRow]:
    rows: list[PredictionRow] = []
    with Path(path).open("r", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                PredictionRow(
                    timestamp=row["timestamp"],
                    facility_id=row["facility_id"],
                    appliance_id=row["appliance_id"],
                    category=row["category"],
                    runtime_state=row["runtime_state"],
                    ambient_temp_c=float(row["ambient_temp_c"]),
                    tariff_eur_kwh=float(row["tariff_eur_kwh"]),
                    power_kw=float(row["power_kw"]),
                )
            )
    return rows
