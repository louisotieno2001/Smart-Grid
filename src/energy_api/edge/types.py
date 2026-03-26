# Author: Jerry Onyango
# Contribution: Defines shared edge runtime types for mappings, timestamps, decoded values, and telemetry records.
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


ValueType = Literal["uint16", "int16", "uint32", "int32", "float32"]
ByteOrder = Literal["big", "little"]
WordOrder = Literal["big", "little"]
Quality = Literal["good", "bad", "suspect"]


@dataclass(frozen=True)
class TimestampBundle:
    ts: datetime
    device_ts: datetime
    gateway_received_at: datetime
    processed_at: datetime


@dataclass(frozen=True)
class PointMapping:
    canonical_key: str
    register_address: int
    register_count: int
    value_type: ValueType
    scale_factor: float = 1.0
    signed: bool = False
    byte_order: ByteOrder = "big"
    word_order: WordOrder = "big"
    unit: str | None = None
    critical: bool = False


@dataclass(frozen=True)
class TelemetryRecord:
    canonical_key: str
    value: float | None
    unit: str | None
    quality: Quality
    ts: datetime
    device_ts: datetime
    gateway_received_at: datetime
    processed_at: datetime
    stale: bool
    stale_reason: str | None = None
    error: str | None = None


@dataclass(frozen=True)
class DecodedPoint:
    canonical_key: str
    value: float
    unit: str | None
