"""Using a Sentio: creating a client, and a view of its rooms and peripherals for a consumer."""
from __future__ import annotations

from dataclasses import dataclass

from modbus_event_connect import Client, Clock, Labels
from modbus_event_connect.modbus import ModbusConnection, ModbusDevice

from ._model import (
    PERIPHERAL,
    ROOM,
    SENTIO,
    PeripheralType,
    PeripheralPointKey,
    RoomType,
    RoomPointKey,
    peripheral_key,
    room_key,
)

DEFAULT_PORT = 502
"""The Modbus TCP port, per the manual."""
DEFAULT_UNIT_ID = 1
"""The manual gives 255 for Modbus TCP "if needed"."""


def create_client(host: str, *, port: int = DEFAULT_PORT, unit_id: int = DEFAULT_UNIT_ID,
                  read_only: bool = False, clock: Clock | None = None) -> Client:
    """A client for the Sentio at `host`, with its own connection; call `connect()` on it.

    `read_only=True` refuses every write before it reaches the controller.
    """
    return Client(ModbusDevice.tcp(host, port, unit_id, clock=clock), SENTIO,
                  clock=clock, read_only=read_only)


def create_client_on(connection: ModbusConnection, *, unit_id: int = DEFAULT_UNIT_ID,
                     read_only: bool = False, clock: Clock | None = None) -> Client:
    """A client on a connection the host already owns - a gateway shared with other devices."""
    return Client(ModbusDevice(connection, unit_id, clock=clock), SENTIO,
                  clock=clock, read_only=read_only)


# ============================================================================ installation


@dataclass(frozen=True)
class SentioRoom:
    """One room, as a consumer turns it into a device."""
    number: int
    """1-16. Also the room's object index in the address space."""
    name: str
    """As configured on the controller, e.g. "Kitchen". Empty if never named."""
    is_dummy: bool
    """A dummy room has no thermostat or sensor, so it reports no measurements."""
    keys: tuple[str, ...]
    """Every key this room has on this unit."""


@dataclass(frozen=True)
class SentioPeripheral:
    """One paired peripheral - a thermostat, a display, an extension module."""
    slot: int
    """1-64; not stable across relearns - use `serial_number` to recognise a device."""
    name: str
    type: int | None
    """Compare with PeripheralType. None if the controller reported no type."""
    serial_number: int | None
    owner: int | None
    """0 = the location itself, 1-16 = that room."""
    keys: tuple[str, ...]

    @property
    def model(self) -> str:
        """A readable model name, or the raw type when this map does not know it."""
        if self.type is None:
            return "unknown"
        try:
            return PeripheralType(self.type).name.replace("_", "-")
        except ValueError:
            return f"type {self.type}"


def rooms(client: Client) -> list[SentioRoom]:
    """The rooms this installation has, from values read during connect()."""
    found: list[SentioRoom] = []
    for n in client.instances(ROOM):
        name = client.value(room_key(n, RoomPointKey.NAME))
        room_type = client.value(room_key(n, RoomPointKey.TYPE))
        found.append(SentioRoom(
            number=n,
            name=name.value if name is not None and isinstance(name.value, str) else "",
            is_dummy=room_type is not None and room_type.value == RoomType.DUMMY,
            keys=tuple(p.key for p in client.select(Labels(room=n))),
        ))
    return found


def peripherals(client: Client) -> list[SentioPeripheral]:
    """The peripherals paired with this installation, from values read during connect()."""
    found: list[SentioPeripheral] = []
    for slot in client.instances(PERIPHERAL):
        found.append(SentioPeripheral(
            slot=slot,
            name=_text(client, peripheral_key(slot, PeripheralPointKey.NAME)),
            type=_integer(client, peripheral_key(slot, PeripheralPointKey.TYPE)),
            serial_number=_integer(client, peripheral_key(slot, PeripheralPointKey.SERIAL_NUMBER)),
            owner=_integer(client, peripheral_key(slot, PeripheralPointKey.OWNER)),
            keys=tuple(p.key for p in client.select(Labels(peripheral=slot))),
        ))
    return found


def _text(client: Client, key: str) -> str:
    current = client.value(key)
    return current.value if current is not None and isinstance(current.value, str) else ""


def _integer(client: Client, key: str) -> int | None:
    current = client.value(key)
    if current is None or isinstance(current.value, bool) or not isinstance(current.value, int):
        return None
    return current.value
