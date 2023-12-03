import abc
import json
from dataclasses import dataclass
from struct import Struct
from typing import Callable, Type, Any, Optional

from twisted.internet import protocol
from twisted.python import failure

from .buffer import Buffer
from .types import VarInt, UShort, String, Data, UUID, ByteArray


class Manager(protocol.Protocol):
    def __init__(self) -> None:
        self.stage = HandShake(self)

    def connectionMade(self) -> None:
        print("Connection made")

    def dataReceived(self, data: bytes) -> None:
        print("-------")
        print(data)
        self.stage.process(data)

    def connectionLost(self, reason: failure.Failure = protocol.connectionDone) -> None:
        print(f"Connection lost {reason}")


class ManagerFactory(protocol.ServerFactory):
    def buildProtocol(self, addr):
        return Manager()


def decode_args(buffer: Buffer, field_types: tuple[Type[Struct], ...]) -> list[Any]:
    args = list()
    for field_type in field_types:
        # noinspection PyArgumentList
        args.append(buffer.mapper[field_type]())
    return args


class Stage(metaclass=abc.ABCMeta):
    listeners: dict[int, tuple[Callable, tuple[Type[Struct]]]]

    @property
    @abc.abstractmethod
    def mapper(self):
        pass

    @abc.abstractmethod
    def __init__(self, manager: Manager) -> None:
        pass

    @abc.abstractmethod
    def process(self, data: bytes) -> None:
        pass


@dataclass
class listen_wrap:
    packet_id: int
    fn: Callable
    owner: Stage = None

    def __set_name__(self, owner, name):
        self.owner = owner
        self.owner.listeners[self.packet_id] = (self.fn, self.owner.mapper[self.packet_id])

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


def listen(packet_id: int):
    return lambda func: listen_wrap(packet_id, func)


class HandShake(Stage):
    listeners = dict()
    mapper = {
        0: (VarInt, String, UShort, VarInt)
    }

    def __init__(self, manager: Manager) -> None:
        self.manager = manager

    def process(self, data: bytes) -> None:
        buffer = Buffer(data)
        packet_length = buffer.unpack_varint()
        packet_id = buffer.unpack_varint()

        func, field_types = self.listeners[packet_id]
        args = decode_args(buffer, self.mapper[packet_id])

        func(self, *args)

        extra_packet = buffer.buffer.read()
        if extra_packet:
            self.manager.stage.process(extra_packet)

    @listen(0)
    def on_handshake(self, protocol_version: int, server_address: str, port: int, next_state: int):
        if next_state == 1:
            self.manager.stage = Status(self.manager)
        elif next_state == 2:
            self.manager.stage = Login(self.manager)


status_response = {
    "version": {
        "name": "1.20.2",
        "protocol": 764
    },
    "players": {
        "max": 100,
        "online": 69,
        "sample": [
            {
                "name": "thinkofdeath",
                "id": "4566e69f-c907-48ee-8d71-d7ba5aa00d20"
            }
        ]
    },
    "description": {
        "text": "Hello world"
    },
    # "favicon": "data:image/png;base64,<data>",
    "enforcesSecureChat": True,
    "previewsChat": True
}


class Status(Stage):
    listeners = dict()
    mapper = {
        0: (),
        1: (Data,)
    }

    def __init__(self, manager: Manager) -> None:
        self.manager = manager

    def process(self, data: bytes) -> None:
        buffer = Buffer(data)
        packet_length = buffer.unpack_varint()
        packet_id = buffer.unpack_varint()

        func, field_types = self.listeners[packet_id]
        args = decode_args(buffer, self.mapper[packet_id])
        return_packet = func(self, *args)
        self.manager.transport.write(return_packet)

    @listen(0)
    def on_status_request(self) -> bytes:
        status = VarInt.pack(0) + VarInt.pack(len(json.dumps(status_response))) + json.dumps(status_response).encode(
            "utf-8")
        packet = VarInt.pack(len(status)) + status
        return packet

    @listen(1)
    def on_ping_request(self, payload: bytes) -> bytes:
        return VarInt.pack(len(payload) + 1) + VarInt.pack(1) + payload


class Login(Stage):
    listeners = dict()
    mapper = {
        0: (String, UUID),
        1: (VarInt, ByteArray, VarInt, ByteArray)
    }

    def __init__(self, manager: Manager) -> None:
        self.manager = manager

    def process(self, data: bytes) -> None:
        print(11111111111111)
        print(data)
        buffer = Buffer(data)
        packet_length = buffer.unpack_varint()
        packet_id = buffer.unpack_varint()

        func, field_types = self.listeners[packet_id]
        args = decode_args(buffer, self.mapper[packet_id])
        print(func, field_types, args)
        return_packet = func(self, *args)
        if return_packet:
            self.manager.transport.write(return_packet)

    @listen(0)
    def on_login_start(self, name: str, uuid: UUID) -> Optional[None]:
        print(name, uuid)
        buffer = Buffer()
        buffer.pack_string("")
        buffer.pack_bytearray()
