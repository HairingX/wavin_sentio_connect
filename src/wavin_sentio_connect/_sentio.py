"""Using a Sentio: creating a client, and a view of its rooms and peripherals for a consumer."""
from __future__ import annotations

from dataclasses import dataclass

from modbus_event_connect import NO_RETRY, CircuitBreaker, Client, Clock, Exponential, Key, Retry
from modbus_event_connect.modbus import ModbusConnection, ModbusDevice, ModbusTcpConnection

from ._model import (
    PERIPHERAL,
    ROOM,
    SENTIO,
    SENTIO_MODBUS,
    LocationPointKey,
    PeripheralPointKey,
    PeripheralType,
    RoomPointKey,
    RoomType,
    model_name,
    peripheral_key,
    room_key,
)

PROFILES = [SENTIO_MODBUS]
"""The profile of every model a Sentio controller may be."""

DEFAULT_PORT = 502
"""The Modbus TCP port, per the manual."""
DEFAULT_UNIT_ID = 1
"""The manual gives 255 for Modbus TCP "if needed"."""


def create_client(host: str, *, port: int = DEFAULT_PORT, unit_id: int = DEFAULT_UNIT_ID,
                  read_only: bool = False, clock: Clock | None = None) -> Client:
    """A client for the Sentio at `host`, with its own connection; call `connect()` on it.

    Once three requests in a row went unanswered, the controller is asked again after 2, 4 and
    8 s, then every 10 s, which opens its link again. A write is sent once.

    Args:
        read_only: refuse every write before it reaches the controller.
    """
    return _client(ModbusTcpConnection(host, port, clock=clock), unit_id, owns_connection=True,
                   read_only=read_only, clock=clock)


def create_client_on(connection: ModbusConnection, *, unit_id: int = DEFAULT_UNIT_ID, read_only: bool = False,
                     clock: Clock | None = None) -> Client:
    """A client on a connection the host already owns - a gateway shared with other devices.

    The controller is asked again, a write is sent, and `read_only` is, as for `create_client`;
    the client's `disconnect()` leaves the connection open.
    """
    return _client(connection, unit_id, owns_connection=False, read_only=read_only, clock=clock)


def _client(connection: ModbusConnection, unit_id: int, *, owns_connection: bool, read_only: bool,
            clock: Clock | None) -> Client:
    # Every 10 s at most is as often as the controller is read while it answers.
    reconnect = CircuitBreaker(after=3, retry=Retry(Exponential(2.0, max=10.0)))
    device = ModbusDevice(connection, unit_id, reconnect=reconnect, profiles=PROFILES,
                          owns_connection=owns_connection, clock=clock)
    return Client(device, SENTIO, write_retry=NO_RETRY, clock=clock, read_only=read_only)


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
        return model_name(self.type) if self.type is not None else "unknown"


def controller_model(client: Client) -> str | None:
    """The controller's model as it reports it, such as "CCU-208", from the value read during
    connect(); None if it reported none."""
    found = _value(client, LocationPointKey.DEVICE_TYPE)
    return model_name(found) if found is not None else None


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
