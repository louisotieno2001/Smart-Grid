# Author: Jerry Onyango
# Contribution: Demonstrates healthy, repeated-value, decode-failure, and stale-missing-read edge poll outcomes against the simulator.
from __future__ import annotations

import struct
import time
from dataclasses import asdict
from datetime import datetime

from energy_api.edge.modbus_adapter import ModbusAdapter
from energy_api.edge.poller import EdgePoller
from energy_api.edge.simulation.modbus_server import SimulatedModbusDevice
from energy_api.edge.types import PointMapping


def f32_to_regs(value: float) -> list[int]:
    payload = struct.pack(">f", value)
    return [int.from_bytes(payload[0:2], "big"), int.from_bytes(payload[2:4], "big")]


def u32_to_regs(value: int) -> list[int]:
    payload = int(value).to_bytes(4, byteorder="big", signed=False)
    return [int.from_bytes(payload[0:2], "big"), int.from_bytes(payload[2:4], "big")]


def run_demo() -> dict[str, list[dict[str, object]]]:
    server = SimulatedModbusDevice(port=15020)
    server.start()

    server.set_holding_register(0, 753)
    server.set_holding_register(1, 65416)
    server.set_holding_registers(2, f32_to_regs(12.75))
    server.set_holding_registers(4, u32_to_regs(13450))

    adapter = ModbusAdapter(host="127.0.0.1", port=15020, timeout_seconds=1.0)
    adapter.connect()

    mappings = [
        PointMapping(canonical_key="battery_soc", register_address=0, register_count=1, value_type="uint16", scale_factor=0.1, unit="%", critical=True),
        PointMapping(canonical_key="battery_power", register_address=1, register_count=1, value_type="int16", signed=True, unit="kW", critical=True),
        PointMapping(canonical_key="pv_generation", register_address=2, register_count=2, value_type="float32", unit="kW", critical=True),
        PointMapping(canonical_key="site_load", register_address=4, register_count=2, value_type="uint32", scale_factor=0.01, unit="kW", critical=True),
    ]

    poller = EdgePoller(adapter=adapter, mappings=mappings, polling_interval_seconds=1)
    healthy = poller.poll_once()
    repeated = poller.poll_once()

    decode_failure_poller = EdgePoller(
        adapter=adapter,
        mappings=[
            PointMapping(
                canonical_key="pv_generation",
                register_address=2,
                register_count=1,
                value_type="float32",
                unit="kW",
                critical=True,
            )
        ],
        polling_interval_seconds=1,
    )
    decode_failure = decode_failure_poller.poll_once()

    poller.adapter = ModbusAdapter(host="127.0.0.1", port=15999, timeout_seconds=0.2)
    time.sleep(2.2)
    stale = poller.poll_once()

    def normalize(rows: list[object]) -> list[dict[str, object]]:
        output: list[dict[str, object]] = []
        for row in rows:
            record = asdict(row)
            for key, value in list(record.items()):
                if isinstance(value, datetime):
                    record[key] = value.isoformat()
            output.append(record)
        return output

    return {
        "healthy": normalize(healthy),
        "repeated_value": normalize(repeated),
        "decode_failure": normalize(decode_failure),
        "stale_missing_read": normalize(stale),
    }


if __name__ == "__main__":
    output = run_demo()
    print("HEALTHY")
    for row in output["healthy"]:
        print(row)

    print("REPEATED_VALUE_STILL_HEALTHY")
    for row in output["repeated_value"]:
        print(row)

    print("DECODE_FAILURE_BAD_QUALITY")
    for row in output["decode_failure"]:
        print(row)

    print("STALE_MISSING_READ")
    for row in output["stale_missing_read"]:
        print(row)
