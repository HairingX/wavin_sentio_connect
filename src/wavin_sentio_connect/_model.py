"""The Wavin Sentio CCU-208 register map, as a modbus_event_connect model."""
from __future__ import annotations

import logging
from collections.abc import Mapping
from enum import IntEnum, StrEnum
from types import MappingProxyType

from modbus_event_connect import (
    DataType,
    Instances,
    Labels,
    Limits,
    Model,
    Point,
    PollRate,
    Quality,
    Refresh,
    Scan,
    Section,
    Unit,
    WriteKind,
)
from modbus_event_connect.modbus import DiscreteInput, HoldingRegister, InputRegister, ModbusOptions, plain

_LOGGER = logging.getLogger(__name__)

ADDRESS_SPACE_REQUIRED = (3, 2)
"""Oldest Sentio address space this register map was written against (FWPKG 12)."""

ROOM_COUNT = 16
"""Rooms the address space defines. Room N's registers start at N * 100."""
PERIPHERAL_COUNT = 64
"""Peripheral slots the address space defines. Slot N's registers start at 51100 + N * 100."""

MAX_REGISTERS = 32
"""The manual caps one request at 32 registers - well below the Modbus protocol's 125."""


def room_base(room: int) -> int:
    """Base address of a room. Room 1 -> 100, room 16 -> 1600."""
    return room * 100


def peripheral_base(slot: int) -> int:
    """Base address of a peripheral slot. Slot 1 -> 51200, slot 64 -> 57500."""
    return 51100 + slot * 100


# ======================================================================= value vocabularies


class RoomType(IntEnum):
    NORMAL = 0
    DUMMY = 1
    """No thermostat or sensor installed, so the room reports no measurements."""


class RoomState(IntEnum):
    """Values of the room state registers (general, radiators, underfloor, integration)."""
    NONE = 0
    """Function not used in this room, or no load detected on any output."""
    IDLE = 1
    HEATING = 2
    COOLING = 3
    BLOCKED_HEATING = 4
    BLOCKED_COOLING = 5


class BlockingSource(IntEnum):
    """Values of the blocking-source registers.

    Kept as plain integers, since an unknown code is still a real reading.
    """
    NONE = 0
    UNKNOWN = 1
    CONTACT = 2
    FLOOR_TEMP = 3
    LOW_ENERGY = 4
    AIR_TEMP = 5
    DEW_POINT = 6
    OUTDOOR_TEMP = 7
    FAULT = 8
    FAULT_HTCO = 9
    PERIODIC_ACTIVATION = 10
    BMS = 11
    DEADBAND = 12
    DRYING = 13
    HEATING_COOLING_MODE = 14
    INSUFFICIENT_DEMAND = 15
    COOLDOWN_PERIOD = 16
    HCW_SOURCE_NOT_RELEASED = 17
    ROOM_MODE = 18
    SYSTEM_IS_INITIALIZING = 19
    SYSTEM_IS_SHUTTING_DOWN = 20
    NO_OUTPUT = 21
    FIRST_OPEN_ACTIVATION = 22
    ROOM_WITH_NO_TEMP_SOURCE = 23
    HCWS_ELEMENTS_BLOCKED = 24


class PeripheralType(IntEnum):
    """Values of the peripheral type register."""
    DHW_201 = 0x0
    """Calefa domestic hot water controller."""
    LCD_200 = 0x4
    RT_201 = 0x5
    RT_250 = 0x6
    RS_211 = 0x7
    RS_251 = 0x8
    RT_250IR = 0x9
    EU_208_A = 0xA
    EU_206_VFR = 0xB
    ET_250 = 0xC
    ET_210 = 0xD
    VH_250 = 0xE
    CCU_208 = 0x11E0
    """The control unit itself. Wider than a byte, hence a 16-bit register."""


# ==================================================================================== keys
#
# Every point has its key in one of these enums. A location point's is its whole key; a room's
# or a peripheral's becomes one through `room_key` or `peripheral_key`. The key strings never change.


class LocationPointKey(StrEnum):
    """The key of each point the location has; it is the whole key."""
    DATAPOINT_MAJOR = "datapoint_major"
    DATAPOINT_MINOR = "datapoint_minor"
    DEVICE_TYPE = "device_type"
    HARDWARE_MAJOR = "hardware_major"
    SOFTWARE_MAJOR = "software_major"
    SOFTWARE_MINOR = "software_minor"
    SERIAL_NUMBER_PREFIX = "serial_number_prefix"
    SERIAL_NUMBER = "serial_number"
    HEATING_COOLING_MODE = "heating_cooling_mode"
    SETPOINT_MAJOR = "setpoint_major"
    SETPOINT_MINOR = "setpoint_minor"
    MODBUS_MODE = "modbus_mode"
    MODBUS_PASSWORD = "modbus_password"
    LOCATION_NAME = "location_name"
    STANDBY_ENABLE = "standby_enable"
    VACATION_ENABLE = "vacation_enable"
    DATETIME_UNIX = "datetime_unix"
    DAYLIGHT_SAVING_ENABLE = "daylight_saving_enable"
    TEMP_OUTDOOR_COOLING_MIN = "temp_outdoor_cooling_min"
    TEMP_OUTDOOR_HEATING_MAX = "temp_outdoor_heating_max"
    UPDATE_MODE = "update_mode"
    HEATING_COOLING_MODE_BMS_OVERRIDE = "heating_cooling_mode_bms_override"
    TIMEZONE = "timezone"
    SYSTEM_WARNING = "system_warning"
    SYSTEM_ERROR = "system_error"


class RoomPointKey(StrEnum):
    """The key of each point within a room; `room_key` makes it the point's key."""
    TEMP_AIR_TARGET_ACTIVE = "temp_air_target_active"
    STATE = "state"
    BLOCKING_SOURCE = "blocking_source"
    TEMP_AIR_CURRENT = "temp_air_current"
    TEMP_FLOOR_CURRENT = "temp_floor_current"
    HUMIDITY_CURRENT = "humidity_current"
    DEW_POINT_CURRENT = "dew_point_current"
    ASSOCIATED_RADIATORS = "associated_radiators"
    ASSOCIATED_UFHC = "associated_ufhc"
    ASSOCIATED_DRYING = "associated_drying"
    ASSOCIATED_THERMAL_INTEGRATION = "associated_thermal_integration"
    ASSOCIATED_VENTILATION = "associated_ventilation"
    RADIATORS_STATE = "radiators_state"
    UFHC_STATE = "ufhc_state"
    DRYING_STATE = "drying_state"
    THERMAL_INTEGRATION_STATE = "thermal_integration_state"
    VENTILATION_STATE = "ventilation_state"
    BLOCKING_SOURCE_RADIATORS = "blocking_source_radiators"
    BLOCKING_SOURCE_UFHC = "blocking_source_ufhc"
    BLOCKING_SOURCE_DRYING = "blocking_source_drying"
    BLOCKING_SOURCE_THERMAL_INTEGRATION = "blocking_source_thermal_integration"
    BLOCKING_SOURCE_VENTILATION = "blocking_source_ventilation"
    TYPE = "type"
    ASSOCIATED_HEATING_SOURCE = "associated_heating_source"
    NAME = "name"
    MODE = "mode"
    MODE_OVERRIDE = "mode_override"
    TEMP_AIR_TARGET = "temp_air_target"
    LOCK = "lock"
    TEMP_STANDBY = "temp_standby"
    TEMP_VACATION = "temp_vacation"
    EXCLUDE_FROM_VACATION = "exclude_from_vacation"
    ADAPTIVE_ENABLE = "adaptive_enable"
    THERMAL_INTEGRATION_HEATING_OFFSET = "thermal_integration_heating_offset"
    THERMAL_INTEGRATION_HYSTERESIS = "thermal_integration_hysteresis"
    HUMIDITY_THRESHOLD_HEATING = "humidity_threshold_heating"
    HUMIDITY_THRESHOLD_COOLING = "humidity_threshold_cooling"
    HUMIDITY_HYSTERESIS = "humidity_hysteresis"
    DRYING_COOLING_WATER_OFFSET = "drying_cooling_water_offset"
    DRYING_COOLING_WATER_OFFSET_HYSTERESIS = "drying_cooling_water_offset_hysteresis"
    DEW_POINT_COOLING_THRESHOLD = "dew_point_cooling_threshold"
    DEW_POINT_COOLING_THRESHOLD_HYSTERESIS = "dew_point_cooling_threshold_hysteresis"
    HUMIDITY_HIGH_ALARM_LIMIT = "humidity_high_alarm_limit"
    TEMP_PRESET = "temp_preset"
    WARNING = "warning"
    ERROR = "error"
    LOW_BATTERY = "low_battery"
    PERIPHERAL_LOST = "peripheral_lost"


class PeripheralPointKey(StrEnum):
    """The key of each point within a peripheral slot; `peripheral_key` makes it the point's key."""
    TYPE = "type"
    SERIAL_NUMBER = "serial_number"
    OWNER = "owner"
    SIGNAL_STRENGTH = "signal_strength"
    NAME = "name"
    WARNING = "warning"
    ERROR = "error"
    LOW_BATTERY = "low_battery"
    LOST = "lost"


ROOM = "room"
"""The instance label of a room: its number, 1 to ROOM_COUNT."""
PERIPHERAL = "peripheral"
"""The instance label of a peripheral slot: its number, 1 to PERIPHERAL_COUNT."""


def room_key(room: int, point: RoomPointKey) -> str:
    """The key of `point` in room `room`: `room_key(4, RoomPointKey.STATE)` is "room_4_state"."""
    return f"room_{room}_{point}"


def peripheral_key(slot: int, point: PeripheralPointKey) -> str:
    """The key of `point` in slot `slot`: `peripheral_key(2, PeripheralPointKey.NAME)` is "peripheral_2_name"."""
    return f"peripheral_{slot}_{point}"


UNITS = frozenset({Unit.CELSIUS, Unit.PERCENT, Unit.SECONDS})
"""Every unit a Sentio value has."""

ALARM = Labels(kind="alarm")
"""Every alarm and warning bit."""

SENSOR = "sensor"
"""The label kind of a room's measurements, which a room without a sensor does not have."""

ROOM_FUNCTIONS: Mapping[str, RoomPointKey] = MappingProxyType({
    "radiators": RoomPointKey.ASSOCIATED_RADIATORS,
    "ufhc": RoomPointKey.ASSOCIATED_UFHC,
    "drying": RoomPointKey.ASSOCIATED_DRYING,
    "thermal_integration": RoomPointKey.ASSOCIATED_THERMAL_INTEGRATION,
    "ventilation": RoomPointKey.ASSOCIATED_VENTILATION,
})
"""What a room can be associated with, and the point saying whether it is.

Each also has a state and a blocking source, labelled `function` with its name.
"""


# ======================================================================= what a write changes
#
# A value other writes change belongs to a group: a `group` label its point carries. A write
# names the groups it changes with `on_write=rereads(...)`, so each group is listed once, here.

ROOM_TARGET = "room_target"
"""The target a room is regulating to right now (`room_{n}_temp_air_target_active`).

Measured on a CCU-208 (address space 3.7): writing `vacation_enable` changed every room's, and
a room's `mode` changed that room's; nothing else in the location or the rooms changed while
watched. Per the manual, standby and a room's setpoint, override, preset and vacation and
standby temperatures decide it too.
"""

REREAD_AFTER_WRITE = 0.5
"""Seconds after a write before the groups it changes are read. Measured with the above."""


def rereads(group: str, **where: int) -> Refresh:
    """Read `group` again after a write: all of it, or the part `where` selects, as `room=n`."""
    return Refresh(Labels(group=group, **where), after=REREAD_AFTER_WRITE)


ROOM_LOCK = DataType.enum({8: "locked", 16: "hotel", 32: "unlocked"})
"""A closed set: only 8, 16 and 32 are valid lock modes."""


# ================================================================================ encodings
#
# How the manual's value types map to points, and which raw value means "no reading".

def _u8(key: str, read: InputRegister | HoldingRegister, *, write: HoldingRegister | None = None, maximum: int = 254,
        poll_rate: PollRate = PollRate.SLOW, unit: Unit | None = None, on_write: Refresh | None = None,
        labels: Mapping[str, str] | None = None) -> Point:
    """val_u1: 0 to `maximum`; anything above - 255 in particular - means no value."""
    return Point(key, read=read, write=write, data_type=DataType.UINT16, raw_range=(0, maximum), poll_rate=poll_rate,
                 unit=unit, limits=Limits(0, maximum, step=1) if write is not None else None, on_write=on_write,
                 labels=labels or {})


def _u16(key: str, read: InputRegister | HoldingRegister | None, *, write: HoldingRegister | None = None,
         poll_rate: PollRate = PollRate.SLOW, write_kind: WriteKind = WriteKind.STATE) -> Point:
    """val_u2: 0xFFFF means no value."""
    return Point(key, read=read, write=write, data_type=DataType.UINT16, poll_rate=poll_rate, write_kind=write_kind,
                 no_data=(0xFFFF,) if read is not None else ())


def _u32(key: str, read: InputRegister | HoldingRegister, *, write: HoldingRegister | None = None,
         poll_rate: PollRate = PollRate.SLOW, unit: Unit | None = None) -> Point:
    """val_u4: 0xFFFFFFFF means no value."""
    return Point(key, read=read, write=write, data_type=DataType.UINT32, no_data=(0xFFFFFFFF,),
                 poll_rate=poll_rate, unit=unit)


def _fp100(key: str, read: InputRegister | HoldingRegister, *, write: HoldingRegister | None = None,
           poll_rate: PollRate = PollRate.SLOW, unit: Unit | None = Unit.CELSIUS, on_write: Refresh | None = None,
           labels: Mapping[str, str] | None = None) -> Point:
    """val_d2_fp100: signed hundredths; 0x7FFF means no reading."""
    return Point(key, read=read, write=write, data_type=DataType.INT16, scale=0.01, no_data=(0x7FFF,),
                 poll_rate=poll_rate, unit=unit, on_write=on_write, labels=labels or {})


def _alarm(key: str, read: DiscreteInput) -> Point:
    """An alarm bit: read rarely by itself, and at once whenever the system's summary changes."""
    return Point(key, read=read, data_type=DataType.BOOL, poll_rate=PollRate.RARE, labels={"kind": "alarm"})


def _summary(key: str, read: DiscreteInput) -> Point:
    """One of the system's two aggregated alarm bits.

    Polled even when nobody asks for it, since its change is what sets off reading every
    other alarm bit that is subscribed to.
    """
    return Point(key, read=read, data_type=DataType.BOOL, poll_rate=PollRate.FAST, poll_always=True,
                 on_change=Refresh(ALARM))


def _text(key: str, read: HoldingRegister, *, write: HoldingRegister | None = None) -> Point:
    """val_utf8: 32 bytes over 16 registers, NUL terminated, no length prefix."""
    return Point(key, read=read, write=write, data_type=DataType.string(16), poll_rate=PollRate.STATIC)


# ================================================================================== points

LOCATION = [
    _u8(LocationPointKey.DATAPOINT_MAJOR, InputRegister(1), poll_rate=PollRate.STATIC),
    _u8(LocationPointKey.DATAPOINT_MINOR, InputRegister(2), poll_rate=PollRate.STATIC),
    _u8(LocationPointKey.DEVICE_TYPE, InputRegister(10), poll_rate=PollRate.STATIC),
    _u8(LocationPointKey.HARDWARE_MAJOR, InputRegister(11), poll_rate=PollRate.STATIC),
    _u8(LocationPointKey.SOFTWARE_MAJOR, InputRegister(12), poll_rate=PollRate.STATIC),
    _u8(LocationPointKey.SOFTWARE_MINOR, InputRegister(13), poll_rate=PollRate.STATIC),
    _u16(LocationPointKey.SERIAL_NUMBER_PREFIX, InputRegister(14), poll_rate=PollRate.STATIC),
    _u32(LocationPointKey.SERIAL_NUMBER, InputRegister(15), poll_rate=PollRate.STATIC),
    _u8(LocationPointKey.HEATING_COOLING_MODE, InputRegister(20)),

    _u8(LocationPointKey.SETPOINT_MAJOR, HoldingRegister(1), poll_rate=PollRate.STATIC),
    _u8(LocationPointKey.SETPOINT_MINOR, HoldingRegister(2), poll_rate=PollRate.STATIC),
    # Whether the controller will accept writes at all, so it is always kept current.
    Point(LocationPointKey.MODBUS_MODE, read=HoldingRegister(5), data_type=DataType.UINT16, raw_range=(0, 254),
          poll_always=True),
    # Write-only per the manual: it can never be read back.
    _u16(LocationPointKey.MODBUS_PASSWORD, None, write=HoldingRegister(6), write_kind=WriteKind.COMMAND),
    _text(LocationPointKey.LOCATION_NAME, HoldingRegister(10), write=HoldingRegister(10)),
    _u8(LocationPointKey.STANDBY_ENABLE, HoldingRegister(26), write=HoldingRegister(26), maximum=1,
        on_write=rereads(ROOM_TARGET)),
    _u8(LocationPointKey.VACATION_ENABLE, HoldingRegister(27), write=HoldingRegister(27), maximum=1,
        on_write=rereads(ROOM_TARGET)),
    _u32(LocationPointKey.DATETIME_UNIX, HoldingRegister(28), write=HoldingRegister(28), unit=Unit.SECONDS),
    _u8(LocationPointKey.DAYLIGHT_SAVING_ENABLE, HoldingRegister(30), write=HoldingRegister(30), maximum=1),
    _fp100(LocationPointKey.TEMP_OUTDOOR_COOLING_MIN, HoldingRegister(31), write=HoldingRegister(31)),
    _fp100(LocationPointKey.TEMP_OUTDOOR_HEATING_MAX, HoldingRegister(32), write=HoldingRegister(32)),
    _u8(LocationPointKey.UPDATE_MODE, HoldingRegister(33), write=HoldingRegister(33), maximum=2),
    _u8(LocationPointKey.HEATING_COOLING_MODE_BMS_OVERRIDE, HoldingRegister(34), write=HoldingRegister(34)),
    _u16(LocationPointKey.TIMEZONE, HoldingRegister(35), write=HoldingRegister(35)),

    # The manual: "A problem is pending in whole system" / "A critical problem is pending".
    _summary(LocationPointKey.SYSTEM_WARNING, DiscreteInput(1)),
    _summary(LocationPointKey.SYSTEM_ERROR, DiscreteInput(2)),
]


def room(n: int) -> list[Point]:
    """One room's points."""
    base = room_base(n)

    def state(point: RoomPointKey, offset: int, function: str | None = None) -> Point:
        return _u8(room_key(n, point), InputRegister(base + offset), poll_rate=PollRate.FAST,
                   labels={"function": function} if function else None)

    def sensor(point: RoomPointKey, offset: int, unit: Unit = Unit.CELSIUS) -> Point:
        return _fp100(room_key(n, point), InputRegister(base + offset), poll_rate=PollRate.MEDIUM, unit=unit,
                      labels={"kind": SENSOR})

    def associated(point: RoomPointKey, offset: int) -> Point:
        return _u8(room_key(n, point), InputRegister(base + offset), poll_rate=PollRate.STATIC)

    retarget = rereads(ROOM_TARGET, room=n)

    def setting(point: RoomPointKey, offset: int, unit: Unit = Unit.CELSIUS, on_write: Refresh | None = None) -> Point:
        return _fp100(room_key(n, point), HoldingRegister(base + offset), write=HoldingRegister(base + offset),
                      unit=unit, on_write=on_write)

    def switch(point: RoomPointKey, offset: int, maximum: int, on_write: Refresh | None = None) -> Point:
        return _u8(room_key(n, point), HoldingRegister(base + offset), write=HoldingRegister(base + offset),
                   maximum=maximum, on_write=on_write)

    return [
        # --- input registers: what the room is doing
        # The target the controller is actually regulating to. Differs from `temp_air_target`
        # (the user's setting, below) under standby, vacation or a schedule.
        _fp100(room_key(n, RoomPointKey.TEMP_AIR_TARGET_ACTIVE), InputRegister(base + 1), poll_rate=PollRate.MEDIUM,
               labels={"group": ROOM_TARGET}),
        state(RoomPointKey.STATE, 2),
        state(RoomPointKey.BLOCKING_SOURCE, 3),
        sensor(RoomPointKey.TEMP_AIR_CURRENT, 4),
        sensor(RoomPointKey.TEMP_FLOOR_CURRENT, 5),
        sensor(RoomPointKey.HUMIDITY_CURRENT, 6, Unit.PERCENT),
        sensor(RoomPointKey.DEW_POINT_CURRENT, 7),
        associated(RoomPointKey.ASSOCIATED_RADIATORS, 11),
        associated(RoomPointKey.ASSOCIATED_UFHC, 12),
        associated(RoomPointKey.ASSOCIATED_DRYING, 14),
        associated(RoomPointKey.ASSOCIATED_THERMAL_INTEGRATION, 15),
        associated(RoomPointKey.ASSOCIATED_VENTILATION, 16),
        state(RoomPointKey.RADIATORS_STATE, 17, "radiators"),
        state(RoomPointKey.UFHC_STATE, 18, "ufhc"),
        state(RoomPointKey.DRYING_STATE, 19, "drying"),
        state(RoomPointKey.THERMAL_INTEGRATION_STATE, 20, "thermal_integration"),
        state(RoomPointKey.VENTILATION_STATE, 21, "ventilation"),
        state(RoomPointKey.BLOCKING_SOURCE_RADIATORS, 22, "radiators"),
        state(RoomPointKey.BLOCKING_SOURCE_UFHC, 23, "ufhc"),
        state(RoomPointKey.BLOCKING_SOURCE_DRYING, 24, "drying"),
        state(RoomPointKey.BLOCKING_SOURCE_THERMAL_INTEGRATION, 25, "thermal_integration"),
        state(RoomPointKey.BLOCKING_SOURCE_VENTILATION, 26, "ventilation"),
        _u8(room_key(n, RoomPointKey.TYPE), InputRegister(base + 27), poll_rate=PollRate.STATIC),
        associated(RoomPointKey.ASSOCIATED_HEATING_SOURCE, 28),

        # --- holding registers: what the user has set
        _text(room_key(n, RoomPointKey.NAME), HoldingRegister(base + 1), write=HoldingRegister(base + 1)),
        switch(RoomPointKey.MODE, 17, 1, on_write=retarget),
        switch(RoomPointKey.MODE_OVERRIDE, 18, 3, on_write=retarget),
        setting(RoomPointKey.TEMP_AIR_TARGET, 19, on_write=retarget),
        Point(room_key(n, RoomPointKey.LOCK), read=HoldingRegister(base + 20), write=HoldingRegister(base + 20),
              data_type=ROOM_LOCK),
        setting(RoomPointKey.TEMP_STANDBY, 21, on_write=retarget),
        setting(RoomPointKey.TEMP_VACATION, 22, on_write=retarget),
        switch(RoomPointKey.EXCLUDE_FROM_VACATION, 23, 1, on_write=retarget),
        switch(RoomPointKey.ADAPTIVE_ENABLE, 24, 1),
        setting(RoomPointKey.THERMAL_INTEGRATION_HEATING_OFFSET, 25),
        setting(RoomPointKey.THERMAL_INTEGRATION_HYSTERESIS, 26),
        setting(RoomPointKey.HUMIDITY_THRESHOLD_HEATING, 27, Unit.PERCENT),
        setting(RoomPointKey.HUMIDITY_THRESHOLD_COOLING, 28, Unit.PERCENT),
        setting(RoomPointKey.HUMIDITY_HYSTERESIS, 29, Unit.PERCENT),
        setting(RoomPointKey.DRYING_COOLING_WATER_OFFSET, 30),
        setting(RoomPointKey.DRYING_COOLING_WATER_OFFSET_HYSTERESIS, 31),
        setting(RoomPointKey.DEW_POINT_COOLING_THRESHOLD, 32),
        setting(RoomPointKey.DEW_POINT_COOLING_THRESHOLD_HYSTERESIS, 33),
        setting(RoomPointKey.HUMIDITY_HIGH_ALARM_LIMIT, 34, Unit.PERCENT),
        switch(RoomPointKey.TEMP_PRESET, 35, 2, on_write=retarget),

        # --- discrete inputs: its alarms
        _alarm(room_key(n, RoomPointKey.WARNING), DiscreteInput(base + 1)),
        _alarm(room_key(n, RoomPointKey.ERROR), DiscreteInput(base + 2)),
        _alarm(room_key(n, RoomPointKey.LOW_BATTERY), DiscreteInput(base + 3)),
        _alarm(room_key(n, RoomPointKey.PERIPHERAL_LOST), DiscreteInput(base + 4)),
    ]


def peripheral(slot: int) -> list[Point]:
    """One peripheral slot's points."""
    base = peripheral_base(slot)

    def key(point: PeripheralPointKey) -> str:
        return peripheral_key(slot, point)

    return [
        _u16(key(PeripheralPointKey.TYPE), InputRegister(base + 1), poll_rate=PollRate.STATIC),
        _u32(key(PeripheralPointKey.SERIAL_NUMBER), InputRegister(base + 2), poll_rate=PollRate.STATIC),
        _u16(key(PeripheralPointKey.OWNER), InputRegister(base + 4), poll_rate=PollRate.STATIC),
        _u8(key(PeripheralPointKey.SIGNAL_STRENGTH), InputRegister(base + 5), poll_rate=PollRate.RARE),
        _text(key(PeripheralPointKey.NAME), HoldingRegister(base + 1)),
        _alarm(key(PeripheralPointKey.WARNING), DiscreteInput(base + 1)),
        _alarm(key(PeripheralPointKey.ERROR), DiscreteInput(base + 2)),
        _alarm(key(PeripheralPointKey.LOW_BATTERY), DiscreteInput(base + 3)),
        _alarm(key(PeripheralPointKey.LOST), DiscreteInput(base + 4)),
    ]


# ==================================================================================== scan


async def find_installed_rooms_and_peripherals(scan: Scan) -> None:
    """Remove every room and peripheral slot this installation does not use."""
    numbers = range(1, ROOM_COUNT + 1)
    rooms = await scan.read(tuple(room_key(n, RoomPointKey.TYPE) for n in numbers))
    for n in numbers:
        if rooms[room_key(n, RoomPointKey.TYPE)].quality is Quality.MISSING:
            scan.set_available(Labels(room=n), False, reason="room not configured")

    slots = range(1, PERIPHERAL_COUNT + 1)
    found = await scan.read(tuple(peripheral_key(s, PeripheralPointKey.TYPE) for s in slots))
    for s in slots:
        if found[peripheral_key(s, PeripheralPointKey.TYPE)].quality is Quality.MISSING:
            scan.set_available(Labels(peripheral=s), False, reason="no peripheral in this slot")


async def find_what_each_room_uses(scan: Scan) -> None:
    """Remove what a room states it does not have.

    The manual: a DUMMY room has "no thermostat or sensor installed", and an association of 0
    is NONE. An unknown or unread value removes nothing.
    """
    types = await scan.read(tuple(room_key(n, RoomPointKey.TYPE) for n in range(1, ROOM_COUNT + 1)))
    rooms = [n for n in range(1, ROOM_COUNT + 1) if types[room_key(n, RoomPointKey.TYPE)].quality is Quality.GOOD]
    found = await scan.read(tuple(room_key(n, point) for n in rooms for point in ROOM_FUNCTIONS.values()))
    for n in rooms:
        if types[room_key(n, RoomPointKey.TYPE)].value == RoomType.DUMMY:
            scan.set_available(Labels(room=n, kind=SENSOR), False, reason="a dummy room has no sensor")
        for function, point in ROOM_FUNCTIONS.items():
            association = found[room_key(n, point)]
            if association.quality is Quality.GOOD and association.value == 0:
                scan.set_available(Labels(room=n, function=function), False,
                                   reason=f"the room is not associated with {function}")


async def check_address_space(scan: Scan) -> None:
    """Warn when the controller's address space is older than this map was written against."""
    found = await scan.read((LocationPointKey.DATAPOINT_MAJOR, LocationPointKey.DATAPOINT_MINOR))
    major, minor = found[LocationPointKey.DATAPOINT_MAJOR].value, found[LocationPointKey.DATAPOINT_MINOR].value
    if isinstance(major, int) and isinstance(minor, int) and (major, minor) < ADDRESS_SPACE_REQUIRED:
        _LOGGER.warning("Sentio address space %d.%d is older than the %d.%d this register map was "
                        "written against. Some registers may be unavailable; update the control unit.",
                        major, minor, *ADDRESS_SPACE_REQUIRED)


SENTIO = Model(
    name="Sentio",
    manufacturer="Wavin",
    options=ModbusOptions(numbering=plain(first_address=1), max_registers=MAX_REGISTERS),  # verified live
    read_back_after=0.5,  # measured with testing.measure_read_back on a CCU-208, address space 3.7
    sections=[
        Section(LOCATION),
        Instances(room, range(1, ROOM_COUNT + 1), label=ROOM),
        Instances(peripheral, range(1, PERIPHERAL_COUNT + 1), label=PERIPHERAL),
    ],
    scan_steps=[check_address_space, find_installed_rooms_and_peripherals, find_what_each_room_uses],
)
