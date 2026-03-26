# Author: Jerry Onyango
# Contribution: Exercises simulated Modbus fault modes and verifies edge runtime behavior under bad data, frozen values, and disconnects.
from __future__ import annotations

import struct
import unittest

from energy_api.edge.modbus_adapter import ModbusAdapter
from energy_api.edge.poller import EdgePoller
from energy_api.edge.simulation.modbus_server import SimulatedModbusDevice
from energy_api.edge.types import PointMapping


def f32_to_regs(value: float) -> list[int]:
    payload = struct.pack(">f", value)
    return [int.from_bytes(payload[0:2], "big"), int.from_bytes(payload[2:4], "big")]


class TestSimulatedModbusFaults(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = SimulatedModbusDevice(port=15031)
        cls.server.start()

    def test_bad_data_and_frozen_values(self) -> None:
        self.server.configure_register_map({0: 500, 2: f32_to_regs(5.5)})

        adapter = ModbusAdapter(host="127.0.0.1", port=15031, timeout_seconds=0.5)
        adapter.connect()

        mappings = [
            PointMapping(canonical_key="battery_soc", register_address=0, register_count=1, value_type="uint16", scale_factor=0.1),
            PointMapping(canonical_key="pv_generation", register_address=2, register_count=2, value_type="float32"),
        ]
        poller = EdgePoller(adapter=adapter, mappings=mappings, polling_interval_seconds=1)

        healthy = poller.poll_once()
        self.assertEqual(healthy[0].quality, "good")

        self.server.inject_bad_data(True)
        bad = poller.poll_once()
        self.assertEqual(bad[0].quality, "good")
        self.assertNotEqual(bad[0].value, healthy[0].value)

        self.server.inject_bad_data(False)
        self.server.freeze_values(True)
        self.server.set_holding_register(0, 900)
        frozen = poller.poll_once()
        self.assertEqual(frozen[0].value, healthy[0].value)
        self.assertFalse(frozen[0].stale)

    def test_disconnect_marks_missing_read_stale(self) -> None:
        adapter = ModbusAdapter(host="127.0.0.1", port=15031, timeout_seconds=0.2)
        adapter.connect()
        mapping = [PointMapping(canonical_key="battery_soc", register_address=0, register_count=1, value_type="uint16")]
        poller = EdgePoller(adapter=adapter, mappings=mapping, polling_interval_seconds=1)

        self.server.inject_disconnect(True)
        row = poller.poll_once()[0]
        self.assertEqual(row.quality, "suspect")
        self.assertTrue(row.stale)
        self.assertEqual(row.stale_reason, "missing_read")
        self.server.inject_disconnect(False)


if __name__ == "__main__":
    unittest.main()
