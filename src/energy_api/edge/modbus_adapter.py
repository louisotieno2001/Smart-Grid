# Author: Jerry Onyango
# Contribution: Provides a Modbus TCP adapter with read/write operations and structured transport error handling.
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from pymodbus.client import ModbusTcpClient


class ModbusAdapterError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass
class ModbusAdapter:
    host: str
    port: int = 502
    timeout_seconds: float = 3.0

    def __post_init__(self) -> None:
        self._client = ModbusTcpClient(host=self.host, port=self.port, timeout=self.timeout_seconds)

    def connect(self) -> None:
        connected = self._client.connect()
        if not connected:
            raise ModbusAdapterError("connect_failed", f"Unable to connect to Modbus device at {self.host}:{self.port}")

    def disconnect(self) -> None:
        self._client.close()

    def is_connected(self) -> bool:
        return bool(getattr(self._client, "connected", False))

    def read_holding_registers(self, address: int, count: int, unit_id: int = 1) -> list[int]:
        try:
            result = self._client.read_holding_registers(address=address, count=count, device_id=unit_id)
        except Exception as exc:
            raise ModbusAdapterError("read_timeout_or_transport", f"Holding register read failed: {exc}") from exc

        if result is None:
            raise ModbusAdapterError("read_empty", "Holding register read returned empty result")
        if result.isError():
            raise ModbusAdapterError("read_error", f"Holding register read returned error: {result}")
        if not hasattr(result, "registers"):
            raise ModbusAdapterError("read_invalid", "Holding register read did not include registers")
        return list(result.registers)

    def read_input_registers(self, address: int, count: int, unit_id: int = 1) -> list[int]:
        try:
            result = self._client.read_input_registers(address=address, count=count, device_id=unit_id)
        except Exception as exc:
            raise ModbusAdapterError("read_timeout_or_transport", f"Input register read failed: {exc}") from exc

        if result is None:
            raise ModbusAdapterError("read_empty", "Input register read returned empty result")
        if result.isError():
            raise ModbusAdapterError("read_error", f"Input register read returned error: {result}")
        if not hasattr(result, "registers"):
            raise ModbusAdapterError("read_invalid", "Input register read did not include registers")
        return list(result.registers)

    def write_single_register(self, address: int, value: int, unit_id: int = 1) -> None:
        try:
            result = self._client.write_register(address=address, value=value, device_id=unit_id)
        except Exception as exc:
            raise ModbusAdapterError("write_timeout_or_transport", f"Single register write failed: {exc}") from exc

        if result is None or result.isError():
            raise ModbusAdapterError("write_error", f"Single register write returned error: {result}")

    def write_multiple_registers(self, address: int, values: Sequence[int], unit_id: int = 1) -> None:
        try:
            result = self._client.write_registers(address=address, values=list(values), device_id=unit_id)
        except Exception as exc:
            raise ModbusAdapterError("write_timeout_or_transport", f"Multiple register write failed: {exc}") from exc

        if result is None or result.isError():
            raise ModbusAdapterError("write_error", f"Multiple register write returned error: {result}")
