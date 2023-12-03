from io import BytesIO
from struct import Struct
from typing import Type, Callable

from .types import VarInt, String, UShort, Long, Data, UUID, ByteArray

from uuid import UUID as _UUID


class Buffer:
    def __init__(self, data: bytes = b""):
        self.buffer = BytesIO(data)
        self.mapper: dict[Type[Struct], Callable] = {
            VarInt: self.unpack_varint,
            String: self.unpack_string,
            UShort: self.unpack_ushort,
            Long: self.unpack_long,
            Data: self.unpack_data,
            UUID: self.unpack_uuid,
            ByteArray: self.unpack_bytearray
        }

    def pack_varint(self, val: int) -> None:
        self.buffer.write(VarInt.pack(val))

    def unpack_varint(self) -> int:
        return VarInt.unpack(self.buffer)

    def pack_string(self, s: str) -> None:
        self.buffer.write(String.pack(s))

    def unpack_string(self) -> str:
        return String.unpack(self.buffer)

    def pack_ushort(self, val: int) -> None:
        self.buffer.write(UShort.pack(val))

    def unpack_ushort(self) -> int:
        return UShort.unpack(self.buffer)

    def pack_long(self, val: int) -> None:
        self.buffer.write(Long.pack(val))

    def unpack_long(self) -> int:
        return Long.unpack(self.buffer)

    def pack_data(self, data: bytes) -> None:
        self.buffer.write(data)

    def unpack_data(self) -> bytes:
        return Data.unpack(self.buffer)

    def pack_bytearray(self, data: bytes) -> None:
        self.buffer.write(VarInt.pack(len(data)) + data)

    def unpack_bytearray(self) -> bytes:
        return ByteArray.unpack(self.buffer)

    def pack_uuid(self, uuid: _UUID) -> None:
        self.buffer.write(UUID.pack(uuid))

    def unpack_uuid(self) -> _UUID:
        return UUID.unpack(self.buffer)
