# Author: Jerry Onyango
# Contribution: Decodes Modbus register payloads into typed canonical values with scaling and byte/word-order handling.
from __future__ import annotations

import struct

from .types import DecodedPoint, PointMapping


class DecodeError(ValueError):
    pass


class Decoder:
    @staticmethod
    def decode(mapping: PointMapping, registers: list[int]) -> DecodedPoint:
        if len(registers) != mapping.register_count:
            raise DecodeError(
                f"register count mismatch for {mapping.canonical_key}: expected {mapping.register_count}, got {len(registers)}"
            )

        payload = Decoder._registers_to_bytes(registers, mapping.word_order)

        if mapping.value_type == "uint16":
            raw = Decoder._unpack_int16(payload, mapping.byte_order, signed=False)
            value = float(raw)
        elif mapping.value_type == "int16":
            signed = mapping.signed or True
            raw = Decoder._unpack_int16(payload, mapping.byte_order, signed=signed)
            value = float(raw)
        elif mapping.value_type == "uint32":
            raw = Decoder._unpack_int32(payload, mapping.byte_order, signed=False)
            value = float(raw)
        elif mapping.value_type == "int32":
            signed = mapping.signed or True
            raw = Decoder._unpack_int32(payload, mapping.byte_order, signed=signed)
            value = float(raw)
        elif mapping.value_type == "float32":
            fmt = ">f" if mapping.byte_order == "big" else "<f"
            if len(payload) != 4:
                raise DecodeError(f"float32 decode requires 4 bytes for {mapping.canonical_key}")
            value = float(struct.unpack(fmt, payload)[0])
        else:
            raise DecodeError(f"Unsupported value_type={mapping.value_type} for {mapping.canonical_key}")

        scaled = value * float(mapping.scale_factor)
        return DecodedPoint(canonical_key=mapping.canonical_key, value=scaled, unit=mapping.unit)

    @staticmethod
    def _registers_to_bytes(registers: list[int], word_order: str) -> bytes:
        words = list(registers)
        if word_order == "little" and len(words) > 1:
            words = list(reversed(words))
        return b"".join(int(word & 0xFFFF).to_bytes(2, byteorder="big", signed=False) for word in words)

    @staticmethod
    def _unpack_int16(payload: bytes, byte_order: str, signed: bool) -> int:
        if len(payload) != 2:
            raise DecodeError("int16/uint16 decode requires 2 bytes")
        return int.from_bytes(payload, byteorder=byte_order, signed=signed)

    @staticmethod
    def _unpack_int32(payload: bytes, byte_order: str, signed: bool) -> int:
        if len(payload) != 4:
            raise DecodeError("int32/uint32 decode requires 4 bytes")
        return int.from_bytes(payload, byteorder=byte_order, signed=signed)
