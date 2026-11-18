"""Using a Sentio: creating a client, and a view of its rooms and peripherals for a consumer."""
from __future__ import annotations

from dataclasses import dataclass

from modbus_event_connect import CircuitBreaker, Client, Clock, Exponential, Key, Retry
from modbus_event_connect.modbus import PORT, ModbusConnection, ModbusDevice, ModbusTcpConnection

from ._model import (
    PERIPHERAL,
    ROOM,
    SENTIO,
    PeripheralPointKey,
    PeripheralType,
    LocationPointKey,
    RoomPointKey,
    RoomType,
    model_name,
    peripheral_key,
    room_key,
)

DEFAULT_PORT = PORT
"""The Modbus TCP port."""
DEFAULT_UNIT_ID = 1
"""The unit id a Sentio answers on over Modbus TCP: the manual gives 255 "if needed", and the
owner's CCU-208 answers on 1."""

_CONNECT_TIMEOUT = 3.0  # guess
_FRAME_GAP = 0.0  # guess
_TIMEOUT_MARGIN = 2.5  # guess: with the Sentio's 0.5 s, a request waits 3.0 s
_RECONNECT = CircuitBreaker(
    after=3,  # guess
    retry=Retry(Exponential(2.0, factor=2.0, max=10.0), None),  # guess
)
_OFFLINE_AFTER_INTERVALS = 3  # guess: 30 s at FAST


def create_client(*, host: str, unit_id: int, port: int = DEFAULT_PORT, read_only: bool = False,
                  clock: Clock | None = None) -> Client:
    """A client for the Sentio at `host`, with its own connection; call `connect()` on it.

    A controller that stops answering is asked again less and less often, and never given up on;
    a request it answers busy is sent again, as its manual asks.

    Args:
        read_only: refuse every write before it reaches the controller.
    """
    connection = ModbusTcpConnection(host, port, connect_timeout=_CONNECT_TIMEOUT, frame_gap=_FRAME_GAP,
                                     clock=clock)
    return _client(connection, unit_id, owns_connection=True, read_only=read_only, clock=clock)


def create_client_on(connection: ModbusConnection, *, unit_id: int, read_only: bool = False,
                     clock: Clock | None = None) -> Client:
    """A client on a connection the host already owns - a gateway shared with other devices.

    It behaves as one from `create_client`, except that its `disconnect()` leaves the connection
    open.
    """
    return _client(connection, unit_id, owns_connection=False, read_only=read_only, clock=clock)


def _client(connection: ModbusConnection, unit_id: int, *, owns_connection: bool, read_only: bool,
            clock: Clock | None) -> Client:
    device = ModbusDevice(connection, unit_id, reconnect=_RECONNECT, models=(SENTIO,),
                          timeout_margin=_TIMEOUT_MARGIN, owns_connection=owns_connection, clock=clock)
    return Client(device, SENTIO, offline_after_intervals=_OFFLINE_AFTER_INTERVALS, read_only=read_only,
                  clock=clock)


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
