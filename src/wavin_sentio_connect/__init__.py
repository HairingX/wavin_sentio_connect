"""Wavin Sentio over Modbus TCP, built on modbus_event_connect."""
from .model import (
    ADDRESS_SPACE_REQUIRED,
    MAX_REGISTERS,
    PERIPHERAL_COUNT,
    ROOM_COUNT,
    SENTIO,
    BlockingSource,
    PeripheralType,
    RoomState,
    RoomType,
    peripheral_base,
    room_base,
)
from .sentio import (
    SentioPeripheral,
    SentioRoom,
    create_client,
    create_client_on,
    peripherals,
    rooms,
)

__version__ = "0.2.0"
__all__ = [
    "ADDRESS_SPACE_REQUIRED",
    "MAX_REGISTERS",
    "PERIPHERAL_COUNT",
    "ROOM_COUNT",
    "SENTIO",
    "BlockingSource",
    "PeripheralType",
    "RoomState",
    "RoomType",
    "SentioPeripheral",
    "SentioRoom",
    "create_client",
    "create_client_on",
    "peripheral_base",
    "peripherals",
    "room_base",
    "rooms",
]
