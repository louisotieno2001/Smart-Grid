# Author: Jerry Onyango
# Contribution: Provides production-oriented batch training, artifact persistence, and hierarchical fallback prediction for energy modeling.
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable, Iterator

from .pipeline import PredictionRow, load_training_rows


@dataclass
class _Agg:
    total: float = 0.0
    count: int = 0

    def update(self, value: float) -> None:
        self.total += value
        self.count += 1

    @property
    def mean(self) -> float:
        return self.total / self.count if self.count else 0.0


class ProductionBatchEnergyModel:
    def __init__(self) -> None:
        self.global_agg = _Agg()
        self.segment_aggs: dict[str, _Agg] = {}
        self.fitted = False
        self.training_rows = 0
        self.training_mape = 0.0

    @staticmethod
    def _hour(timestamp: str) -> int:
        return int(timestamp[11:13])

    @staticmethod
    def _make_keys(row: PredictionRow) -> list[str]:
        hour = ProductionBatchEnergyModel._hour(row.timestamp)
        return [
            f"appliance_hour::{row.facility_id}::{row.appliance_id}::{row.runtime_state}::{hour}",
            f"appliance::{row.facility_id}::{row.appliance_id}::{row.runtime_state}",
            f"facility_category_hour::{row.facility_id}::{row.category}::{row.runtime_state}::{hour}",
            f"category_hour::{row.category}::{row.runtime_state}::{hour}",
            f"category::{row.category}::{row.runtime_state}",
        ]

    def fit_batch(self, rows: Iterable[PredictionRow]) -> None:
        for row in rows:
            self.global_agg.update(row.power_kw)
            self.training_rows += 1
            for key in self._make_keys(row):
                if key not in self.segment_aggs:
                    self.segment_aggs[key] = _Agg()
                self.segment_aggs[key].update(row.power_kw)

    def fit_in_batches(self, rows: list[PredictionRow], batch_size: int = 5000) -> None:
        if not rows:
            raise ValueError("No rows provided for training")

        for idx in range(0, len(rows), batch_size):
            self.fit_batch(rows[idx : idx + batch_size])

        self.fitted = True
        train_eval = self.evaluate(rows)
        self.training_mape = float(train_eval["mape"])

    def predict_one(self, row: PredictionRow) -> float:
        if not self.fitted:
            raise RuntimeError("Model must be trained before prediction")

        for key in self._make_keys(row):
            agg = self.segment_aggs.get(key)
            if agg and agg.count >= 2:
                return agg.mean

        return self.global_agg.mean

    def predict(self, rows: Iterable[PredictionRow]) -> list[float]:
        return [self.predict_one(row) for row in rows]

    def evaluate(self, rows: Iterable[PredictionRow]) -> dict[str, float]:
        rows_list = list(rows)
        preds = self.predict(rows_list)
        mae_total = 0.0
        mape_total = 0.0
        non_zero = 0

        for row, pred in zip(rows_list, preds, strict=True):
            err = abs(row.power_kw - pred)
            mae_total += err
            if row.power_kw > 0:
                mape_total += err / row.power_kw
                non_zero += 1

        mae = mae_total / len(rows_list) if rows_list else 0.0
        mape = mape_total / non_zero if non_zero else 0.0
        return {
            "mae_kw": round(mae, 4),
            "mape": round(mape, 4),
            "rows": float(len(rows_list)),
        }

    def suggest(self, rows: Iterable[PredictionRow]) -> list[dict[str, object]]:
        rows_list = list(rows)
        preds = self.predict(rows_list)

        confidence = max(0.5, min(0.95, 1.0 - self.training_mape))
        deduped: dict[str, dict[str, object]] = {}

        for row, pred in zip(rows_list, preds, strict=True):
            if row.runtime_state != "idle" or pred <= 90:
                continue

            projected_kwh_day = pred * 3.0
            projected_savings_eur = projected_kwh_day * row.tariff_eur_kwh * 365
            suggestion = {
                "appliance_id": row.appliance_id,
                "title": "Reduce off-shift idle runtime",
                "projected_annual_savings_eur": round(projected_savings_eur, 2),
                "confidence": round(confidence, 2),
                "effort": "medium",
            }

            existing = deduped.get(row.appliance_id)
            if not existing or float(suggestion["projected_annual_savings_eur"]) > float(existing["projected_annual_savings_eur"]):
                deduped[row.appliance_id] = suggestion

        return list(deduped.values())

    def to_artifact(self) -> dict[str, object]:
        if not self.fitted:
            raise RuntimeError("Cannot serialize an unfitted model")

        return {
            "version": "prod_batch_v1",
            "trained_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "training_rows": self.training_rows,
            "training_mape": self.training_mape,
            "global_mean": self.global_agg.mean,
            "segments": {key: {"count": agg.count, "mean": agg.mean} for key, agg in self.segment_aggs.items()},
        }

    def save(self, path: str | Path) -> Path:
        payload = self.to_artifact()
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return output_path

    @classmethod
    def from_artifact(cls, payload: dict[str, object]) -> "ProductionBatchEnergyModel":
        model = cls()
        model.global_agg = _Agg(total=float(payload.get("global_mean", 0.0)), count=1)
        model.training_rows = int(payload.get("training_rows", 0))
        model.training_mape = float(payload.get("training_mape", 0.0))

        segments = payload.get("segments", {})
        if isinstance(segments, dict):
            for key, value in segments.items():
                if not isinstance(value, dict):
                    continue
                mean = float(value.get("mean", 0.0))
                count = int(value.get("count", 0))
                model.segment_aggs[str(key)] = _Agg(total=mean * max(count, 1), count=max(count, 1))

        model.fitted = True
        return model

    @classmethod
    def load(cls, path: str | Path) -> "ProductionBatchEnergyModel":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_artifact(payload)


def iter_training_rows_in_batches(path: str | Path, batch_size: int) -> Iterator[list[PredictionRow]]:
    rows = load_training_rows(path)
    for idx in range(0, len(rows), batch_size):
        yield rows[idx : idx + batch_size]


def train_model_from_csv_batches(path: str | Path, batch_size: int = 5000) -> ProductionBatchEnergyModel:
    model = ProductionBatchEnergyModel()
    seen = 0
    for batch in iter_training_rows_in_batches(path, batch_size):
        model.fit_batch(batch)
        seen += len(batch)

    if seen == 0:
        raise ValueError("No training rows loaded")

    model.fitted = True
    model.training_rows = seen
    rows = load_training_rows(path)
    model.training_mape = float(model.evaluate(rows)["mape"])
    return model
