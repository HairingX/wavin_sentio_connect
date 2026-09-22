import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Dict, List
from modbus_event_connect import (  # type: ignore
    MODBUS_VALUE_TYPES,
    ModbusDevice,
    ModbusDeviceInfo,
    ModbusTCPEventConnect,
    ModbusDeviceAdapter,
    ModbusPointKey,
    ModbusTransport,
 )
from .devices import *
from .devices.wavin_sentio import (
    PERIPHERAL_COUNT, ROOM_COUNT, WavinSentio, WavinSentioDatapointKey,
    WavinSentioSetpointKey, peripheral_base, room_base,
)

_LOGGER = logging.getLogger(__name__)


class WavinSentioDeviceAdapter(ModbusDeviceAdapter):

    def _translate_to_model(self, device_info: ModbusDeviceInfo) -> Callable[[ModbusDeviceInfo], ModbusDevice]|None:
        # No firmware check here: _translate_to_model runs during connect(), before any
        # register has been read, so device_info.version is still all zeros. The check belongs
        # in WavinSentio._version_changed(), which runs once the version registers arrive.
        return WavinSentio


@dataclass
class SentioRoom:
    """One room, as a consumer would turn it into a device."""

    number: int
    """Room number, 1-16. Also its Modbus object index."""
    name: str
    """Room name as configured on the controller, e.g. "Kitchen"."""
    is_dummy: bool = False
    """A DUMMY room has no thermostat or sensor, so it reports no measurements."""

    @property
    def base(self) -> int:
        """Modbus base address of this room's registers."""
        return room_base(self.number)

    def datapoint_keys(self) -> List[WavinSentioDatapointKey]:
        """Every readable key belonging to this room."""
        prefix = f"datapoint_room_{self.number}_"
        return [k for k in WavinSentioDatapointKey if str(k).startswith(prefix)]

    def setpoint_keys(self) -> List[WavinSentioSetpointKey]:
        """Every writable key belonging to this room."""
        prefix = f"setpoint_room_{self.number}_"
        return [k for k in WavinSentioSetpointKey if str(k).startswith(prefix)]

    def __str__(self) -> str:
        return f"Room {self.number} '{self.name}'{' (dummy)' if self.is_dummy else ''}"


@dataclass
class SentioPeripheral:
    """One paired peripheral - a thermostat, display or extension module."""

    slot: int
    """Position in the controller's peripheral list, 1-64.

    **Not a stable identity.** The controller reorders slots when peripherals are learned or
    unlearned; use `serial` to identify a physical device across restarts.
    """
    name: str
    """Name reported by the peripheral, e.g. "RT-250IR"."""
    type: int
    """Product type; compare against WavinPeripheralTypes."""
    serial: int
    """Serial number. The stable identity."""
    owner: int
    """Which object it belongs to: 0 = the location itself, 1-16 = that room."""

    @property
    def base(self) -> int:
        return peripheral_base(self.slot)

    @property
    def model(self) -> str:
        """Human-readable model name, or the raw type if unrecognised."""
        for attribute, value in vars(WavinPeripheralTypes).items():
            if isinstance(value, int) and value == self.type and not attribute.startswith("_"):
                return attribute.replace("_", "-")
        return f"type {self.type}"

    def datapoint_keys(self) -> List[WavinSentioDatapointKey]:
        prefix = f"datapoint_peripheral_{self.slot}_"
        return [k for k in WavinSentioDatapointKey if str(k).startswith(prefix)]

    def __str__(self) -> str:
        owner = "location" if self.owner == 0 else f"room {self.owner}"
        return f"Peripheral {self.slot} {self.model} sn={self.serial} ({owner})"


@dataclass
class SentioDiscovery:
    """
    What this particular controller is made of.

    Shaped for a consumer that builds one device per room and per peripheral: each entry
    carries the name, identity and register keys needed to create it, and peripherals record
    which room they belong to so they can be linked to it.
    """

    rooms: List[SentioRoom] = field(default_factory=list)
    peripherals: List[SentioPeripheral] = field(default_factory=list)

    def room(self, number: int) -> SentioRoom|None:
        """The room with this number, or None if the controller does not have it."""
        return next((r for r in self.rooms if r.number == number), None)

    def peripherals_for_room(self, number: int) -> List[SentioPeripheral]:
        """The peripherals assigned to a room, for linking them to its device."""
        return [p for p in self.peripherals if p.owner == number]

    @property
    def room_numbers(self) -> List[int]:
        return [r.number for r in self.rooms]

    def __str__(self) -> str:
        return (f"{len(self.rooms)} rooms ({', '.join(r.name or str(r.number) for r in self.rooms)}), "
                f"{len(self.peripherals)} peripherals")


class WavinSentioTCPConnect(ModbusTCPEventConnect):
    """
    Event-driven client for a Wavin Sentio CCU over Modbus TCP.

    Owns no timer and no polling thread. Call `request_datapoint_read()` /
    `request_setpoint_read()` from whatever scheduler the host already runs, and subscribe to
    the keys you care about; callbacks fire only when a value actually changes.

    Args:
        transport: an existing connection to use. Pass one to share a connection the host
            already manages instead of opening a second socket to the same controller.
            When omitted, `connect()` opens its own.
    """

    ROOM_PROBE_OFFSET = 27
    """Room type register. Present on both NORMAL and DUMMY rooms, so it proves existence."""
    PERIPHERAL_PROBE_OFFSET = 1
    """Peripheral type register."""

    def __init__(self, transport: ModbusTransport|None = None) -> None:
        super().__init__(transport=transport)
        # Per instance, so two controllers in one process do not share a device model.
        self._attr_adapter = WavinSentioDeviceAdapter()
        self._discovery = SentioDiscovery()
        self._absent_keys: set[ModbusPointKey] = set()

    @property
    def discovery(self) -> SentioDiscovery:
        """What the last discover() found. Empty until discover() has run."""
        return self._discovery

    def provides(self, key: ModbusPointKey) -> bool:
        """
        Whether this controller has the point at all.

        After discovery this is False for every room and peripheral the installation does not
        have, so a consumer can ask before building an entity rather than creating one that
        will never hold a value.
        """
        if key in self._absent_keys:
            return False
        return super().provides(key)

    async def _discover_device(self) -> None:
        """Run discovery as part of connect(), so a consumer never sees the full 1046 keys."""
        await self.discover()

    async def discover(self, *, apply: bool = True) -> SentioDiscovery:
        """
        Find out which rooms and peripherals this controller actually has.

        The register map covers everything a Sentio *can* have - 16 rooms, 64 peripheral
        slots - but a given installation has far fewer. A register belonging to something
        that has not been set up is answered with ILLEGAL_DATA_ADDRESS, and that is the only
        way the controller reports it: there is no "which rooms exist" register.

        Probing explicitly costs one single-register read per candidate (about 70 ms for all
        80 on a real CCU-208), and it gives the answer *before* anything is built on top of
        it. Leaving it to be discovered by failed reads instead costs an order of magnitude
        more and only produces the answer after the first full poll - too late for a consumer
        that has to decide which entities to create.

        Re-running it picks up rooms or peripherals added or removed since, which is what
        makes a reload enough and a restart unnecessary.

        Args:
            apply: also stop reading the points belonging to whatever was not found.
        """
        transport = self._transport
        if transport is None:
            _LOGGER.warning("Cannot discover, not connected")
            return self._discovery

        found = SentioDiscovery()
        for number in range(1, ROOM_COUNT + 1):
            base = room_base(number)
            probe = await transport.read_input_registers(base + self.ROOM_PROBE_OFFSET, 1)
            if probe is None:
                continue
            found.rooms.append(SentioRoom(
                number=number,
                name=await self._read_string(base + 1),
                is_dummy=probe[0] == WavinSentioRoomType.DUMMY,
            ))

        for slot in range(1, PERIPHERAL_COUNT + 1):
            base = peripheral_base(slot)
            probe = await transport.read_input_registers(base + self.PERIPHERAL_PROBE_OFFSET, 1)
            if probe is None:
                continue
            # Serial (base+2..+3) and owner (base+4) sit next to each other, so one request.
            identity = await transport.read_input_registers(base + 2, 3)
            serial = ((identity[0] << 16) | identity[1]) if identity else 0
            owner = identity[2] if identity else 0
            found.peripherals.append(SentioPeripheral(
                slot=slot,
                name=await self._read_string(base + 1),
                type=probe[0],
                serial=serial,
                owner=owner,
            ))

        self._discovery = found
        _LOGGER.info(f"Discovered {found}")
        if apply:
            self._apply_discovery(found)
        return found

    async def _read_string(self, address: int) -> str:
        """Read one val_utf8 field: 16 registers, 32 bytes, NUL terminated."""
        transport = self._transport
        if transport is None:
            return ""
        registers = await transport.read_holding_registers(address, 16)
        if registers is None:
            return ""
        raw = b"".join(r.to_bytes(2, "big") for r in registers)
        return raw.split(b"\x00")[0].decode("utf-8", errors="replace")

    def _apply_discovery(self, found: SentioDiscovery) -> None:
        """
        Mark every point belonging to an absent room or peripheral as not provided.

        Both halves matter: the read flag stops them being polled, and `provides()` stops a
        consumer from subscribing to something that can never hold a value. Recorded rather
        than only flagged, because subscribing would otherwise turn the read flag back on.
        """
        absent_rooms = set(range(1, ROOM_COUNT + 1)) - {r.number for r in found.rooms}
        absent_slots = set(range(1, PERIPHERAL_COUNT + 1)) - {p.slot for p in found.peripherals}
        absent: set[ModbusPointKey] = set()
        for keys in (WavinSentioDatapointKey, WavinSentioSetpointKey):
            for key in keys:
                name = str(key)
                for prefix, missing in (("room_", absent_rooms), ("peripheral_", absent_slots)):
                    marker = f"_{prefix}"
                    if marker not in name:
                        continue
                    number = int(name.split(marker, 1)[1].split("_", 1)[0])
                    if number in missing:
                        absent.add(key)
                        self._attr_adapter.set_read(key, False, force=True)
                    break
        self._absent_keys = absent
        _LOGGER.debug(f"Discovery marked {len(absent)} points as not provided by this unit")

    def subscribe(self, key: ModbusPointKey, update_method: Callable[[ModbusPointKey, MODBUS_VALUE_TYPES|None, MODBUS_VALUE_TYPES|None], None]):
        """Subscribe, refusing keys discovery proved this controller does not have."""
        if key in self._absent_keys:
            _LOGGER.warning(f"Ignoring subscription to '{key}': this controller has no such "
                            f"room or peripheral")
            return
        super().subscribe(key, update_method)
