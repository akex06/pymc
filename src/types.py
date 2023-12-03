import abc
import struct
from io import BytesIO
from typing import Any
from uuid import UUID as _UUID


class Struct(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def pack(self, val: Any) -> bytes:
        pass

    @abc.abstractmethod
    def unpack(self, data: BytesIO) -> Any:
        pass


class VarintStruct(Struct):
    def pack(self, val: int) -> bytes:
        total = b''
        if val < 0:
            val = (1 << 32) + val
        while val >= 0x80:
            bits = val & 0x7F
            val >>= 7
            total += struct.pack('B', (0x80 | bits))
        bits = val & 0x7F
        total += struct.pack('B', bits)
        return total

    def unpack(self, buffer: BytesIO) -> int:
        total = 0
        shift = 0
        val = 0x80
        while val & 0x80:
            val = struct.unpack('B', buffer.read(1))[0]
            total |= ((val & 0x7F) << shift)
            shift += 7
        if total & (1 << 31):
            total = total - (1 << 32)
        return total


VarInt = VarintStruct()


class StringStruct(Struct):
    def pack(self, s: str) -> bytes:
        return VarInt.pack(len(s)) + s.encode("utf-8")

    def unpack(self, data: BytesIO) -> str:
        return data.read(VarInt.unpack(data)).decode("utf-8")


String = StringStruct()


class UShortStruct(Struct):
    def pack(self, val: int) -> bytes:
        return struct.pack(">H", val)

    def unpack(self, data: BytesIO) -> int:
        return struct.unpack(">H", data.read(2))[0]


UShort = UShortStruct()


class LongStruct(Struct):
    def pack(self, val: int) -> bytes:
        return struct.pack(">l", val)

    def unpack(self, data: BytesIO) -> int:
        return struct.unpack(">l", data.read(4))[0]


Long = LongStruct()


class DataStruct(Struct):
    def pack(self, data: bytes) -> bytes:
        return data

    def unpack(self, data: BytesIO) -> bytes:
        return data.read()


Data = DataStruct()


class UUIDStruct(Struct):
    def pack(self, uuid: _UUID) -> bytes:
        return uuid.bytes

    def unpack(self, data: BytesIO) -> _UUID:
        return _UUID(bytes=data.read(16))


UUID = UUIDStruct()


class ByteArrayStruct(Struct):
    def pack(self, val: bytes) -> bytes:
        return VarInt.pack(len(val)) + val

    def unpack(self, data: BytesIO) -> bytes:
        return data.read(VarInt.unpack(data))


ByteArray = ByteArrayStruct()
