# Author: Jerry Onyango
# Contribution: Runs one polling cycle to read device registers, decode telemetry, assign timestamps, and apply staleness logic.
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from .decoder import DecodeError, Decoder
from .modbus_adapter import ModbusAdapter, ModbusAdapterError
from .staleness import StalenessTracker
from .types import PointMapping, TelemetryRecord

# The EdgePoller class is responsible for performing a single polling cycle of 
# the edge runtime. It reads data from devices using the ModbusAdapter, 
# decodes the raw register values into meaningful telemetry using 
# the Decoder, and applies staleness logic to determine the freshness 
# of the data. The poll_once method returns a list of TelemetryRecord 
# objects that encapsulate the results of the polling cycle, 
# including any errors or quality issues encountered during reading or decoding.
@dataclass
class EdgePoller:
    adapter: ModbusAdapter
    mappings: list[PointMapping]
    polling_interval_seconds: int = 5
    unit_id: int = 1

    def __post_init__(self) -> None:
        self.decoder = Decoder()
        self.staleness = StalenessTracker(stale_after_seconds=self.polling_interval_seconds * 2)

    def poll_once(self) -> list[TelemetryRecord]:
        gateway_received_at = datetime.now(UTC)
        records: list[TelemetryRecord] = []

        for mapping in self.mappings:
            read_failed = False
            decode_failed = False
            decoded_value: float | None = None
            error: str | None = None

            try:
                registers = self.adapter.read_holding_registers(
                    address=mapping.register_address,
                    count=mapping.register_count,
                    unit_id=self.unit_id,
                )
            except ModbusAdapterError as exc:
                read_failed = True
                registers = []
                error = f"{exc.code}:{exc}"

            if not read_failed:
                try:
                    decoded = self.decoder.decode(mapping, registers)
                    decoded_value = decoded.value
                except DecodeError as exc:
                    decode_failed = True
                    error = str(exc)

            processed_at = datetime.now(UTC)
            device_ts = processed_at if decoded_value is not None else gateway_received_at
            stale, stale_reason = self.staleness.evaluate(
                key=mapping.canonical_key,
                now=processed_at,
                value=decoded_value,
                missing_read=read_failed,
                decode_failed=decode_failed,
            )

            quality = "good"
            if decode_failed:
                quality = "bad"
            elif read_failed:
                quality = "suspect"

            ts = device_ts
            records.append(
                TelemetryRecord(
                    canonical_key=mapping.canonical_key,
                    value=decoded_value,
                    unit=mapping.unit,
                    quality=quality,
                    ts=ts,
                    device_ts=device_ts,
                    gateway_received_at=gateway_received_at,
                    processed_at=processed_at,
                    stale=stale,
                    stale_reason=stale_reason,
                    error=error,
                )
            )

        return records
