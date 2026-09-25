"""The Wavin Sentio CCU-208 register map, as a modbus_event_connect model."""
from __future__ import annotations

import logging
from enum import IntEnum

from modbus_event_connect.data_type import DataType
from modbus_event_connect.modbus import HoldingRegister, InputRegister, ModbusOptions, plain
from modbus_event_connect.model import Instances, Model, Scan, Section
from modbus_event_connect.point import Labels, Limits, Point, PollRate, WriteKind
from modbus_event_connect.unit import Unit
from modbus_event_connect.value import Quality

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


ROOM_LOCK = DataType.enum({8: "locked", 16: "hotel", 32: "unlocked"})
"""A closed set: only 8, 16 and 32 are valid lock modes."""


# ================================================================================ encodings
#
# How the manual's value types map to points, and which raw value means "no reading".

def _u8(key: str, read: InputRegister | HoldingRegister, *, write: HoldingRegister | None = None, maximum: int = 254,
        poll_rate: PollRate = PollRate.SLOW, unit: Unit | None = None) -> Point:
    """val_u1: 0 to `maximum`; anything above - 255 in particular - means no value."""
    return Point(key, read=read, write=write, data_type=DataType.UINT16, raw_range=(0, maximum), poll_rate=poll_rate,
                 unit=unit, limits=Limits(0, maximum, step=1) if write is not None else None)


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
           poll_rate: PollRate = PollRate.SLOW, unit: Unit | None = Unit.CELSIUS) -> Point:
    """val_d2_fp100: signed hundredths; 0x7FFF means no reading."""
    return Point(key, read=read, write=write, data_type=DataType.INT16, scale=0.01, no_data=(0x7FFF,),
                 poll_rate=poll_rate, unit=unit)


def _text(key: str, read: HoldingRegister, *, write: HoldingRegister | None = None) -> Point:
    """val_utf8: 32 bytes over 16 registers, NUL terminated, no length prefix."""
    return Point(key, read=read, write=write, data_type=DataType.string(16), poll_rate=PollRate.STATIC)


# ================================================================================== points

LOCATION = [
    _u8("datapoint_major", InputRegister(1), poll_rate=PollRate.STATIC),
    _u8("datapoint_minor", InputRegister(2), poll_rate=PollRate.STATIC),
    _u8("device_type", InputRegister(10), poll_rate=PollRate.STATIC),
    _u8("hardware_major", InputRegister(11), poll_rate=PollRate.STATIC),
    _u8("software_major", InputRegister(12), poll_rate=PollRate.STATIC),
    _u8("software_minor", InputRegister(13), poll_rate=PollRate.STATIC),
    _u16("serial_number_prefix", InputRegister(14), poll_rate=PollRate.STATIC),
    _u32("serial_number", InputRegister(15), poll_rate=PollRate.STATIC),
    _u8("heating_cooling_mode", InputRegister(20)),

    _u8("setpoint_major", HoldingRegister(1), poll_rate=PollRate.STATIC),
    _u8("setpoint_minor", HoldingRegister(2), poll_rate=PollRate.STATIC),
    # Whether the controller will accept writes at all, so it is always kept current.
    Point("modbus_mode", read=HoldingRegister(5), data_type=DataType.UINT16, raw_range=(0, 254), poll_always=True),
    # Write-only per the manual: it can never be read back.
    _u16("modbus_password", None, write=HoldingRegister(6), write_kind=WriteKind.COMMAND),
    _text("location_name", HoldingRegister(10), write=HoldingRegister(10)),
    _u8("standby_enable", HoldingRegister(26), write=HoldingRegister(26), maximum=1),
    _u8("vacation_enable", HoldingRegister(27), write=HoldingRegister(27), maximum=1),
    _u32("datetime_unix", HoldingRegister(28), write=HoldingRegister(28), unit=Unit.SECONDS),
    _u8("daylight_saving_enable", HoldingRegister(30), write=HoldingRegister(30), maximum=1),
    _fp100("temp_outdoor_cooling_min", HoldingRegister(31), write=HoldingRegister(31)),
    _fp100("temp_outdoor_heating_max", HoldingRegister(32), write=HoldingRegister(32)),
    _u8("update_mode", HoldingRegister(33), write=HoldingRegister(33), maximum=2),
    _u8("heating_cooling_mode_bms_override", HoldingRegister(34), write=HoldingRegister(34)),
    _u16("timezone", HoldingRegister(35), write=HoldingRegister(35)),
]


def room(n: int) -> list[Point]:
    """One room's points."""
    base = room_base(n)

    def key(name: str) -> str:
        return f"room_{n}_{name}"

    def state(name: str, offset: int) -> Point:
        return _u8(key(name), InputRegister(base + offset), poll_rate=PollRate.FAST)

    def associated(name: str, offset: int) -> Point:
        return _u8(key(f"associated_{name}"), InputRegister(base + offset), poll_rate=PollRate.STATIC)

    def setting(name: str, offset: int, unit: Unit = Unit.CELSIUS) -> Point:
        return _fp100(key(name), HoldingRegister(base + offset), write=HoldingRegister(base + offset), unit=unit)

    def switch(name: str, offset: int, maximum: int) -> Point:
        return _u8(key(name), HoldingRegister(base + offset), write=HoldingRegister(base + offset), maximum=maximum)

    return [
        # --- input registers: what the room is doing
        # The target the controller is actually regulating to. Differs from `temp_air_target`
        # (the user's setting, below) under standby, vacation or a schedule.
        _fp100(key("temp_air_target_active"), InputRegister(base + 1), poll_rate=PollRate.MEDIUM),
        state("state", 2),
        state("blocking_source", 3),
        _fp100(key("temp_air_current"), InputRegister(base + 4), poll_rate=PollRate.MEDIUM),
        _fp100(key("temp_floor_current"), InputRegister(base + 5), poll_rate=PollRate.MEDIUM),
        _fp100(key("humidity_current"), InputRegister(base + 6), poll_rate=PollRate.MEDIUM,
               unit=Unit.PERCENT),
        _fp100(key("dew_point_current"), InputRegister(base + 7), poll_rate=PollRate.MEDIUM),
        associated("radiators", 11),
        associated("ufhc", 12),
        associated("drying", 14),
        associated("thermal_integration", 15),
        associated("ventilation", 16),
        state("air_state", 17),
        state("floor_state", 18),
        state("drying_state", 19),
        state("thermal_integration_state", 20),
        state("ventilation_state", 21),
        state("blocking_source_radiators", 22),
        state("blocking_source_ufhc", 23),
        state("blocking_source_drying", 24),
        state("blocking_source_thermal_integration", 25),
        state("blocking_source_ventilation", 26),
        _u8(key("type"), InputRegister(base + 27), poll_rate=PollRate.STATIC),
        associated("heating_source", 28),

        # --- holding registers: what the user has set
        _text(key("name"), HoldingRegister(base + 1), write=HoldingRegister(base + 1)),
        switch("mode", 17, 1),
        switch("mode_override", 18, 3),
        setting("temp_air_target", 19),
        Point(key("lock"), read=HoldingRegister(base + 20), write=HoldingRegister(base + 20), data_type=ROOM_LOCK),
        setting("temp_standby", 21),
        setting("temp_vacation", 22),
        switch("exclude_from_vacation", 23, 1),
        switch("adaptive_enable", 24, 1),
        setting("thermal_integration_heating_offset", 25),
        setting("thermal_integration_hysteresis", 26),
        setting("humidity_threshold_heating", 27, Unit.PERCENT),
        setting("humidity_threshold_cooling", 28, Unit.PERCENT),
        setting("humidity_hysteresis", 29, Unit.PERCENT),
        setting("drying_cooling_water_offset", 30),
        setting("drying_cooling_water_offset_hysteresis", 31),
        setting("dew_point_cooling_threshold", 32),
        setting("dew_point_cooling_threshold_hysteresis", 33),
        setting("humidity_high_alarm_limit", 34, Unit.PERCENT),
        switch("temp_preset", 35, 2),
    ]


def peripheral(slot: int) -> list[Point]:
    """One peripheral slot's points."""
    base = peripheral_base(slot)

    def key(name: str) -> str:
        return f"peripheral_{slot}_{name}"

    return [
        _u16(key("type"), InputRegister(base + 1), poll_rate=PollRate.STATIC),
        _u32(key("serial_number"), InputRegister(base + 2), poll_rate=PollRate.STATIC),
        _u16(key("owner"), InputRegister(base + 4), poll_rate=PollRate.STATIC),
        _u8(key("signal_strength"), InputRegister(base + 5), poll_rate=PollRate.RARE),
        _text(key("name"), HoldingRegister(base + 1)),
    ]


# ==================================================================================== scan


async def find_installed_rooms_and_peripherals(scan: Scan) -> None:
    """Remove every room and peripheral slot this installation does not use."""
    rooms = await scan.read(tuple(f"room_{n}_type" for n in range(1, ROOM_COUNT + 1)))
    for n in range(1, ROOM_COUNT + 1):
        if rooms[f"room_{n}_type"].quality is Quality.MISSING:
            scan.set_available(Labels(room=n), False, reason="room not configured")

    slots = await scan.read(tuple(f"peripheral_{s}_type" for s in range(1, PERIPHERAL_COUNT + 1)))
    for s in range(1, PERIPHERAL_COUNT + 1):
        if slots[f"peripheral_{s}_type"].quality is Quality.MISSING:
            scan.set_available(Labels(peripheral=s), False, reason="no peripheral in this slot")


async def check_address_space(scan: Scan) -> None:
    """Warn when the controller's address space is older than this map was written against."""
    found = await scan.read(("datapoint_major", "datapoint_minor"))
    major, minor = found["datapoint_major"].value, found["datapoint_minor"].value
    if isinstance(major, int) and isinstance(minor, int) and (major, minor) < ADDRESS_SPACE_REQUIRED:
        _LOGGER.warning("Sentio address space %d.%d is older than the %d.%d this register map was "
                        "written against. Some registers may be unavailable; update the control unit.",
                        major, minor, *ADDRESS_SPACE_REQUIRED)


SENTIO = Model(
    name="Sentio",
    manufacturer="Wavin",
    options=ModbusOptions(numbering=plain(first_address=1), max_registers=MAX_REGISTERS),  # verified live
    read_back_after=1.0,  # not measured: measuring writes to the device
    sections=[
        Section(LOCATION),
        Instances(room, range(1, ROOM_COUNT + 1), label="room"),
        Instances(peripheral, range(1, PERIPHERAL_COUNT + 1), label="peripheral"),
    ],
    scan_steps=[check_address_space, find_installed_rooms_and_peripherals],
)
