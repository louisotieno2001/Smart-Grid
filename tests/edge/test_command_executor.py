# Author: Jerry Onyango
# Contribution: Tests explicit command execution and per-command reconciliation rules for charge, discharge, idle, limit, and mode flows.
from __future__ import annotations

import unittest

from energy_api.edge.commands import CommandExecutor


class FakeAdapter:
    def __init__(self) -> None:
        self.registers: dict[int, int] = {}

    def write_single_register(self, address: int, value: int, unit_id: int = 1) -> None:
        self.registers[address] = value & 0xFFFF

    def read_holding_registers(self, address: int, count: int, unit_id: int = 1) -> list[int]:
        return [self.registers.get(address + i, 0) for i in range(count)]


class TestCommandExecutor(unittest.TestCase):
    def test_charge_and_discharge_reconcile_explicitly(self) -> None:
        adapter = FakeAdapter()
        executor = CommandExecutor(adapter=adapter)

        charge = {
            "command_type": "charge",
            "setpoint_register": 10,
            "power_register": 11,
            "target_power_kw": 2.5,
            "setpoint_scale": 10,
            "min_effective_power_kw": 0.1,
        }
        adapter.registers[11] = int(2.6 * 10) & 0xFFFF
        ok, _ = executor.execute_and_reconcile(charge)
        self.assertTrue(ok)

        discharge = {
            "command_type": "discharge",
            "setpoint_register": 10,
            "power_register": 11,
            "target_power_kw": 3.0,
            "setpoint_scale": 10,
            "min_effective_power_kw": 0.1,
        }
        adapter.registers[11] = (-30) & 0xFFFF
        ok, _ = executor.execute_and_reconcile(discharge)
        self.assertTrue(ok)

    def test_idle_set_limit_set_mode_reconcile_explicitly(self) -> None:
        adapter = FakeAdapter()
        executor = CommandExecutor(adapter=adapter)

        idle_payload = {
            "command_type": "idle",
            "setpoint_register": 20,
            "power_register": 21,
            "setpoint_scale": 10,
            "idle_power_threshold_kw": 0.1,
        }
        adapter.registers[21] = 0
        ok, _ = executor.execute_and_reconcile(idle_payload)
        self.assertTrue(ok)

        limit_payload = {
            "command_type": "set_limit",
            "limit_register": 30,
            "target_limit": 75,
        }
        ok, _ = executor.execute_and_reconcile(limit_payload)
        self.assertTrue(ok)

        mode_payload = {
            "command_type": "set_mode",
            "mode_register": 31,
            "target_mode": 2,
        }
        ok, _ = executor.execute_and_reconcile(mode_payload)
        self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
