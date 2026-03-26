# Author: Jerry Onyango
# Contribution: Exposes edge simulation helpers for local Modbus integration and fault-injection testing.
from .modbus_server import SimulatedModbusDevice

__all__ = ["SimulatedModbusDevice"]
