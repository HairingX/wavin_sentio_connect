"""Using a Sentio: creating a client, and a view of its rooms and peripherals for a consumer."""
from __future__ import annotations

from dataclasses import dataclass

from modbus_event_connect import Client, Clock, Key
from modbus_event_connect.modbus import ModbusConnection, ModbusDevice

from ._model import (
    PERIPHERAL,
    ROOM,
    SENTIO,
    PeripheralPointKey,
    PeripheralType,
    RoomPointKey,
    RoomType,
    peripheral_key,
    room_key,
)

DEFAULT_PORT = 502
"""The Modbus TCP port, per the manual."""
DEFAULT_UNIT_ID = 1
"""The manual gives 255 for Modbus TCP "if needed"."""


def create_client(host: str, *, port: int = DEFAULT_PORT, unit_id: int = DEFAULT_UNIT_ID,
                  read_only: bool = False, clock: Clock | None = None, write_retry_for: float = 0.0) -> Client:
    """A client for the Sentio at `host`, with its own connection; call `connect()` on it.

    Args:
        read_only: refuse every write before it reaches the controller.
        write_retry_for: seconds after its first sending that a write the controller answered
            busy is still sent again; 0 sends every write once.
    """
    return Client(ModbusDevice.tcp(host, port, unit_id, clock=clock), SENTIO,
                  clock=clock, read_only=read_only, write_retry_for=write_retry_for)


def create_client_on(connection: ModbusConnection, *, unit_id: int = DEFAULT_UNIT_ID, read_only: bool = False,
                     clock: Clock | None = None, write_retry_for: float = 0.0) -> Client:
    """A client on a connection the host already owns - a gateway shared with other devices.

    `read_only` and `write_retry_for` are as for `create_client`.
    """
    return Client(ModbusDevice(connection, unit_id, clock=clock), SENTIO,
                  clock=clock, read_only=read_only, write_retry_for=write_retry_for)


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


@dataclass(frozen=True)
class SentioPeripheral:
    """One paired peripheral - a thermostat, a display, an extension module."""
    slot: int
    """1-64; not stable across relearns - use `serial_number` to recognise a device."""
    name: str
    type: PeripheralType | None
    """None if the controller reported no type, or one this map does not name."""
    serial_number: int | None
    owner: int | None
    """0 = the location itself, 1-16 = that room."""

    @property
    def model(self) -> str:
        """A readable model name, such as "RT-250", or "unknown"."""
        return self.type.name.replace("_", "-") if self.type is not None else "unknown"


def rooms(client: Client) -> list[SentioRoom]:
    """The rooms this installation has, from values read during connect()."""
    return [SentioRoom(number=n,
                       name=_value(client, room_key(n, RoomPointKey.NAME)) or "",
                       is_dummy=_value(client, room_key(n, RoomPointKey.TYPE)) is RoomType.DUMMY)
            for n in client.instances(ROOM)]


def peripherals(client: Client) -> list[SentioPeripheral]:
    """The peripherals paired with this installation, from values read during connect()."""
    return [SentioPeripheral(slot=slot,
                             name=_value(client, peripheral_key(slot, PeripheralPointKey.NAME)) or "",
                             type=_value(client, peripheral_key(slot, PeripheralPointKey.TYPE)),
                             serial_number=_value(client, peripheral_key(slot, PeripheralPointKey.SERIAL_NUMBER)),
                             owner=_value(client, peripheral_key(slot, PeripheralPointKey.OWNER)))
            for slot in client.instances(PERIPHERAL)]


def _value[T](client: Client, key: Key[T]) -> T | None:
    current = client.value(key)
    return current.value if current is not None else None
