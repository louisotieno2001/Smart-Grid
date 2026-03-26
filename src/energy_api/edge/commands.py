# Author: Jerry Onyango
# Contribution: Executes supported edge commands and applies explicit per-command reconciliation rules against device readback.
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from .modbus_adapter import ModbusAdapter, ModbusAdapterError


CommandType = Literal["charge", "discharge", "idle", "set_limit", "set_mode"]


@dataclass
class CommandExecutor:
    adapter: ModbusAdapter
    unit_id: int = 1

    def execute_and_reconcile(self, payload: dict[str, Any]) -> tuple[bool, str]:
        command_type = self._command_type(payload)

        if command_type in {"charge", "discharge"}:
            self._apply_charge_discharge(command_type, payload)
            ok = self._reconcile_charge_discharge(command_type, payload)
            return ok, "reconciled_power_or_setpoint"

        if command_type == "idle":
            self._apply_idle(payload)
            ok = self._reconcile_idle(payload)
            return ok, "reconciled_near_zero_power"

        if command_type == "set_limit":
            self._apply_set_limit(payload)
            ok = self._reconcile_set_limit(payload)
            return ok, "reconciled_limit_readback"

        if command_type == "set_mode":
            self._apply_set_mode(payload)
            ok = self._reconcile_set_mode(payload)
            return ok, "reconciled_mode_readback"

        return False, "unsupported_command"

    def reconcile_only(self, payload: dict[str, Any]) -> tuple[bool, str]:
        command_type = self._command_type(payload)
        if command_type in {"charge", "discharge"}:
            return self._reconcile_charge_discharge(command_type, payload), "reconcile_only_power_or_setpoint"
        if command_type == "idle":
            return self._reconcile_idle(payload), "reconcile_only_near_zero_power"
        if command_type == "set_limit":
            return self._reconcile_set_limit(payload), "reconcile_only_limit_readback"
        if command_type == "set_mode":
            return self._reconcile_set_mode(payload), "reconcile_only_mode_readback"
        return False, "unsupported_command"

    def _apply_charge_discharge(self, command_type: CommandType, payload: dict[str, Any]) -> None:
        register_address = int(payload["setpoint_register"])
        target_power_kw = float(payload.get("target_power_kw", 0.0))
        scale = float(payload.get("setpoint_scale", 10.0))

        signed_value = int(round(target_power_kw * scale))
        if command_type == "discharge":
            signed_value = -abs(signed_value)
        else:
            signed_value = abs(signed_value)

        encoded = signed_value & 0xFFFF
        self.adapter.write_single_register(register_address, encoded, unit_id=self.unit_id)

    def _reconcile_charge_discharge(self, command_type: CommandType, payload: dict[str, Any]) -> bool:
        power_register = int(payload["power_register"])
        setpoint_register = int(payload["setpoint_register"])
        min_effective_kw = float(payload.get("min_effective_power_kw", 0.1))
        scale = float(payload.get("setpoint_scale", 10.0))

        setpoint_raw = self.adapter.read_holding_registers(setpoint_register, 1, unit_id=self.unit_id)[0]
        power_raw = self.adapter.read_holding_registers(power_register, 1, unit_id=self.unit_id)[0]

        setpoint_kw = self._decode_int16(setpoint_raw) / scale
        power_kw = self._decode_int16(power_raw) / scale

        if command_type == "charge":
            return setpoint_kw > 0 and power_kw >= min_effective_kw
        return setpoint_kw < 0 and power_kw <= (-min_effective_kw)

    def _apply_idle(self, payload: dict[str, Any]) -> None:
        register_address = int(payload["setpoint_register"])
        self.adapter.write_single_register(register_address, 0, unit_id=self.unit_id)

    def _reconcile_idle(self, payload: dict[str, Any]) -> bool:
        power_register = int(payload["power_register"])
        threshold_kw = float(payload.get("idle_power_threshold_kw", 0.05))
        scale = float(payload.get("setpoint_scale", 10.0))

        power_raw = self.adapter.read_holding_registers(power_register, 1, unit_id=self.unit_id)[0]
        power_kw = self._decode_int16(power_raw) / scale
        return abs(power_kw) <= threshold_kw

    def _apply_set_limit(self, payload: dict[str, Any]) -> None:
        register_address = int(payload["limit_register"])
        target_limit = int(payload["target_limit"])
        self.adapter.write_single_register(register_address, target_limit & 0xFFFF, unit_id=self.unit_id)

    def _reconcile_set_limit(self, payload: dict[str, Any]) -> bool:
        register_address = int(payload["limit_register"])
        target_limit = int(payload["target_limit"]) & 0xFFFF
        actual = self.adapter.read_holding_registers(register_address, 1, unit_id=self.unit_id)[0] & 0xFFFF
        return actual == target_limit

    def _apply_set_mode(self, payload: dict[str, Any]) -> None:
        register_address = int(payload["mode_register"])
        target_mode = int(payload["target_mode"])
        self.adapter.write_single_register(register_address, target_mode & 0xFFFF, unit_id=self.unit_id)

    def _reconcile_set_mode(self, payload: dict[str, Any]) -> bool:
        register_address = int(payload["mode_register"])
        target_mode = int(payload["target_mode"]) & 0xFFFF
        actual = self.adapter.read_holding_registers(register_address, 1, unit_id=self.unit_id)[0] & 0xFFFF
        return actual == target_mode

    @staticmethod
    def _command_type(payload: dict[str, Any]) -> CommandType:
        value = str(payload.get("command_type", "")).strip()
        allowed = {"charge", "discharge", "idle", "set_limit", "set_mode"}
        if value not in allowed:
            raise ModbusAdapterError("invalid_command", f"Unsupported command_type={value}")
        return value  # type: ignore[return-value]

    @staticmethod
    def _decode_int16(value: int) -> int:
        unsigned = int(value) & 0xFFFF
        return unsigned - 0x10000 if unsigned & 0x8000 else unsigned
