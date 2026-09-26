"""The Wavin Sentio CCU-208 register map, as a modbus_event_connect model."""
from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass, replace
from enum import IntEnum
from typing import Any
from types import MappingProxyType

from modbus_event_connect import (
    DataType,
    Key,
    Labels,
    Limits,
    Model,
    Point,
    PollRate,
    Quality,
    Refresh,
    RepeatedSection,
    Scan,
    Section,
    Unit,
    WriteKind,
)
from modbus_event_connect.modbus import (
    DiscreteInput,
    HoldingRegister,
    InputRegister,
    ModbusOptions,
    plain,
)

_LOGGER = logging.getLogger(__name__)

ADDRESS_SPACE_REQUIRED = (3, 2)
"""Oldest Sentio address space this register map was written against (FWPKG 12)."""

ROOM_COUNT = 16
"""Rooms the address space defines. Room N's registers start at N * 100."""
HCC_COUNT = 3
"""Heating/cooling circuits the address space defines. HCC N's registers start at 7600 + N * 100."""
PERIPHERAL_COUNT = 64
"""Peripheral slots the address space defines. Slot N's registers start at 51100 + N * 100."""

MAX_REGISTERS = 32
"""The manual caps one request at 32 registers - well below the Modbus protocol's 125."""


def room_base(room: int) -> int:
    """Base address of a room. Room 1 -> 100, room 16 -> 1600."""
    return room * 100


def hcc_base(hcc: int) -> int:
    """Base address of a heating/cooling circuit. HCC 1 -> 7700, HCC 3 -> 7900."""
    return 7600 + hcc * 100


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


class DryingState(IntEnum):
    """Values of a room's drying state register."""
    NONE = 0
    """Drying is not used in this room."""
    IDLE = 1
    DRYING = 2
    BLOCKED_DRYING = 3


class VentilationState(IntEnum):
    """Values of a room's ventilation state register."""
    NONE = 0
    """Ventilation is not used in this room."""
    STOPPED = 1
    UNOCCUPIED = 2
    ECONOMY = 3
    COMFORT = 4
    BOOST = 5
    BLOCKED = 6


class BlockingSource(IntEnum):
    """Values of the blocking-source registers."""
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


class RoomMode(IntEnum):
    """Values of a room's mode register."""
    SCHEDULE = 0
    """The scheduler's temperature is used, not the room's setpoint."""
    MANUAL = 1


class RoomModeOverride(IntEnum):
    """Values of a room's mode override register; above NONE, the room's setpoint is not used."""
    NONE = 0
    TEMPORARY = 1
    VACATION_AWAY = 2
    ADJUST = 3


class TemperaturePreset(IntEnum):
    """Values of a room's temperature preset register."""
    ECO = 0
    COMFORT = 1
    EXTRA_COMFORT = 2


class HeatingCoolingMode(IntEnum):
    """Values of the location's heating/cooling mode register."""
    HEATING = 0
    COOLING = 1


class HeatingCoolingModeOverride(IntEnum):
    """Values of the heating/cooling mode BMS override register.

    Only hardware profiles with a manual change-over offer it; in others it is DISABLED.
    """
    DISABLED = 0
    HEATING = 1
    COOLING = 2
    EXTERNAL_SWITCH = 3
    """Set by an external switch, only where the hardware input is available."""


class DeviceType(IntEnum):
    """Values of the location's device type register."""
    CCU_208 = 1
    DHW_201 = 2
    """Calefa domestic hot water controller."""


class ModbusMode(IntEnum):
    """Values of the Modbus mode register."""
    DISABLED = 0
    READ_ONLY = 1
    READ_WRITE = 2
    WRITE_WITH_PASSWORD = 3


class UpdateMode(IntEnum):
    """Values of the update mode register."""
    DONT_ALLOW_FROM_MOBILE_APP = 0
    ENABLED = 1
    DISABLED_ENTIRELY = 2


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


class PumpState(IntEnum):
    """Values of a heating/cooling circuit's pump demand and pump state registers."""
    IDLE = 1
    ON = 2


class HeatCurveType(IntEnum):
    """Values of a heating/cooling circuit's heat curve type register."""
    MANUAL = 0
    """The curve's slope is the manual slope."""
    CALCULATED = 1
    UNDERFLOOR = 2
    RADIATORS = 3


class HeatSourceState(IntEnum):
    """Values of the boiler/heat pump state register."""
    IDLE = 1
    HEATING_PREPARE = 2
    HEATING_ACTIVE = 3
    HEATING_TERMINATE = 4
    COOLING_PREPARE = 5
    COOLING_ACTIVE = 6
    COOLING_TERMINATE = 7
    BLOCKED_HEATING = 8
    BLOCKED_COOLING = 9
    FAILURE = 10


# ==================================================================================== keys
#
# Every point has its key here, with the type of its value. A location point's key is its
# whole key; a room's or a peripheral's becomes one through `room_key` or `peripheral_key`.
# The key strings never change.


class RoomLock(IntEnum):
    """Values of a room's lock register; no other value can be written."""
    LOCKED = 8
    HOTEL = 16
    UNLOCKED = 32


@dataclass(frozen=True)
class PointKey[T]:
    """The key of a point every room, or every peripheral slot, has, and the type of its value."""
    name: str
    type: type[T]


def _members[K](namespace: type, kind: type[K]) -> tuple[K, ...]:
    return tuple(value for value in vars(namespace).values() if isinstance(value, kind))


class LocationPointKey:
    """The key of each point the location has."""
    DATAPOINT_MAJOR = Key("datapoint_major", int)
    DATAPOINT_MINOR = Key("datapoint_minor", int)
    DEVICE_TYPE = Key("device_type", DeviceType)
    HARDWARE_MAJOR = Key("hardware_major", int)
    SOFTWARE_MAJOR = Key("software_major", int)
    SOFTWARE_MINOR = Key("software_minor", int)
    SERIAL_NUMBER_PREFIX = Key("serial_number_prefix", int)
    SERIAL_NUMBER = Key("serial_number", int)
    HEATING_COOLING_MODE = Key("heating_cooling_mode", HeatingCoolingMode)
    SETPOINT_MAJOR = Key("setpoint_major", int)
    SETPOINT_MINOR = Key("setpoint_minor", int)
    MODBUS_MODE = Key("modbus_mode", ModbusMode)
    MODBUS_PASSWORD = Key("modbus_password", int)
    LOCATION_NAME = Key("location_name", str)
    STANDBY_ENABLE = Key("standby_enable", bool)
    VACATION_ENABLE = Key("vacation_enable", bool)
    DATETIME_UNIX = Key("datetime_unix", int)
    DAYLIGHT_SAVING_ENABLE = Key("daylight_saving_enable", bool)
    TEMP_OUTDOOR_COOLING_MIN = Key("temp_outdoor_cooling_min", float)
    TEMP_OUTDOOR_HEATING_MAX = Key("temp_outdoor_heating_max", float)
    UPDATE_MODE = Key("update_mode", UpdateMode)
    HEATING_COOLING_MODE_BMS_OVERRIDE = Key("heating_cooling_mode_bms_override", HeatingCoolingModeOverride)
    TIMEZONE = Key("timezone", int)
    SYSTEM_WARNING = Key("system_warning", bool)
    SYSTEM_ERROR = Key("system_error", bool)

    @classmethod
    def all(cls) -> tuple[Key[Any], ...]:
        """Every key, in the order declared."""
        kind: type[Key[Any]] = Key
        return _members(cls, kind)


class RoomPointKey:
    """The key of each point within a room; `room_key` makes it the point's key."""
    TEMP_AIR_TARGET_ACTIVE = PointKey("temp_air_target_active", float)
    STATE = PointKey("state", RoomState)
    BLOCKING_SOURCE = PointKey("blocking_source", BlockingSource)
    TEMP_AIR_CURRENT = PointKey("temp_air_current", float)
    TEMP_FLOOR_CURRENT = PointKey("temp_floor_current", float)
    HUMIDITY_CURRENT = PointKey("humidity_current", float)
    DEW_POINT_CURRENT = PointKey("dew_point_current", float)
    ASSOCIATED_RADIATORS = PointKey("associated_radiators", int)
    ASSOCIATED_UFHC = PointKey("associated_ufhc", int)
    ASSOCIATED_DRYING = PointKey("associated_drying", int)
    ASSOCIATED_THERMAL_INTEGRATION = PointKey("associated_thermal_integration", int)
    ASSOCIATED_VENTILATION = PointKey("associated_ventilation", int)
    RADIATORS_STATE = PointKey("radiators_state", RoomState)
    UFHC_STATE = PointKey("ufhc_state", RoomState)
    DRYING_STATE = PointKey("drying_state", DryingState)
    THERMAL_INTEGRATION_STATE = PointKey("thermal_integration_state", RoomState)
    VENTILATION_STATE = PointKey("ventilation_state", VentilationState)
    BLOCKING_SOURCE_RADIATORS = PointKey("blocking_source_radiators", BlockingSource)
    BLOCKING_SOURCE_UFHC = PointKey("blocking_source_ufhc", BlockingSource)
    BLOCKING_SOURCE_DRYING = PointKey("blocking_source_drying", BlockingSource)
    BLOCKING_SOURCE_THERMAL_INTEGRATION = PointKey("blocking_source_thermal_integration", BlockingSource)
    BLOCKING_SOURCE_VENTILATION = PointKey("blocking_source_ventilation", BlockingSource)
    TYPE = PointKey("type", RoomType)
    ASSOCIATED_HEATING_SOURCE = PointKey("associated_heating_source", int)
    NAME = PointKey("name", str)
    MODE = PointKey("mode", RoomMode)
    MODE_OVERRIDE = PointKey("mode_override", RoomModeOverride)
    TEMP_AIR_TARGET = PointKey("temp_air_target", float)
    LOCK = PointKey("lock", RoomLock)
    TEMP_STANDBY = PointKey("temp_standby", float)
    TEMP_VACATION = PointKey("temp_vacation", float)
    EXCLUDE_FROM_VACATION = PointKey("exclude_from_vacation", int)
    ADAPTIVE_ENABLE = PointKey("adaptive_enable", int)
    THERMAL_INTEGRATION_HEATING_OFFSET = PointKey("thermal_integration_heating_offset", float)
    THERMAL_INTEGRATION_HYSTERESIS = PointKey("thermal_integration_hysteresis", float)
    HUMIDITY_THRESHOLD_HEATING = PointKey("humidity_threshold_heating", float)
    HUMIDITY_THRESHOLD_COOLING = PointKey("humidity_threshold_cooling", float)
    HUMIDITY_HYSTERESIS = PointKey("humidity_hysteresis", float)
    DRYING_COOLING_WATER_OFFSET = PointKey("drying_cooling_water_offset", float)
    DRYING_COOLING_WATER_OFFSET_HYSTERESIS = PointKey("drying_cooling_water_offset_hysteresis", float)
    DEW_POINT_COOLING_THRESHOLD = PointKey("dew_point_cooling_threshold", float)
    DEW_POINT_COOLING_THRESHOLD_HYSTERESIS = PointKey("dew_point_cooling_threshold_hysteresis", float)
    HUMIDITY_HIGH_ALARM_LIMIT = PointKey("humidity_high_alarm_limit", float)
    TEMP_PRESET = PointKey("temp_preset", TemperaturePreset)
    WARNING = PointKey("warning", bool)
    ERROR = PointKey("error", bool)
    LOW_BATTERY = PointKey("low_battery", bool)
    PERIPHERAL_LOST = PointKey("peripheral_lost", bool)

    @classmethod
    def all(cls) -> tuple[PointKey[Any], ...]:
        """Every key, in the order declared."""
        kind: type[PointKey[Any]] = PointKey
        return _members(cls, kind)


class PeripheralPointKey:
    """The key of each point within a peripheral slot; `peripheral_key` makes it the point's key."""
    TYPE = PointKey("type", PeripheralType)
    SERIAL_NUMBER = PointKey("serial_number", int)
    OWNER = PointKey("owner", int)
    SIGNAL_STRENGTH = PointKey("signal_strength", int)
    NAME = PointKey("name", str)
    WARNING = PointKey("warning", bool)
    ERROR = PointKey("error", bool)
    LOW_BATTERY = PointKey("low_battery", bool)
    LOST = PointKey("lost", bool)

    @classmethod
    def all(cls) -> tuple[PointKey[Any], ...]:
        """Every key, in the order declared."""
        kind: type[PointKey[Any]] = PointKey
        return _members(cls, kind)


NOT_SUPPORTED: Mapping[PeripheralType, frozenset[PointKey[Any]]] = MappingProxyType({
    PeripheralType.RT_201: frozenset({PeripheralPointKey.SIGNAL_STRENGTH}),
    PeripheralType.RS_211: frozenset({PeripheralPointKey.SIGNAL_STRENGTH}),
    PeripheralType.ET_210: frozenset({PeripheralPointKey.SIGNAL_STRENGTH}),
    PeripheralType.LCD_200: frozenset({PeripheralPointKey.SIGNAL_STRENGTH}),
    PeripheralType.EU_208_A: frozenset({PeripheralPointKey.SIGNAL_STRENGTH}),
})
"""The points a peripheral of each known type does not have, which a scan removes; a type not
listed has every peripheral point.

Sources: the manual's component table calls the RT-201, RS-211 and ET-210 wired. The LCD-200 is
wired and the EU-208-A has no antenna, and a CCU-208 answers "no reading" for the signal strength
of both.
"""

class OutdoorPointKey:
    """The key of each point of the outdoor zone."""
    AIR_TEMP = Key("outdoor_air_temp", float)
    """Used to switch between heating and cooling and to block them, per the manual."""
    AIR_TEMP_FILTERED = Key("outdoor_air_temp_filtered", float)
    """Used in heat curve calculations and frost protection, per the manual."""
    AIR_TEMP_GEOMETRICAL = Key("outdoor_air_temp_geometrical", float)
    """The manual: "Not yet used"."""
    NAME = Key("outdoor_name", str)
    AIR_TEMP_BMS_OVERRIDE = Key("outdoor_air_temp_bms_override", float)
    """Takes the place of the measured air temperature; no value means no override."""
    WARNING = Key("outdoor_warning", bool)
    ERROR = Key("outdoor_error", bool)
    LOW_BATTERY = Key("outdoor_low_battery", bool)
    PERIPHERAL_LOST = Key("outdoor_peripheral_lost", bool)

    @classmethod
    def all(cls) -> tuple[Key[Any], ...]:
        """Every key, in the order declared."""
        kind: type[Key[Any]] = Key
        return _members(cls, kind)


class HccPointKey:
    """The key of each point within a heating/cooling circuit (HCC); `hcc_key` makes it the
    point's key."""
    STATE = PointKey("state", RoomState)
    BLOCKING_SOURCE = PointKey("blocking_source", BlockingSource)
    PUMP_DEMAND = PointKey("pump_demand", PumpState)
    PUMP_STATE = PointKey("pump_state", PumpState)
    TEMP_INLET_CURRENT = PointKey("temp_inlet_current", float)
    TEMP_INLET_TARGET = PointKey("temp_inlet_target", float)
    """The inlet temperature the circuit's regulator wants to meet."""
    TEMP_ROOM_TARGET = PointKey("temp_room_target", float)
    """The room temperature the circuit's consumers want."""
    NAME = PointKey("name", str)
    HEAT_CURVE_TYPE = PointKey("heat_curve_type", HeatCurveType)
    HEAT_CURVE_SLOPE = PointKey("heat_curve_slope", float)
    """Used only with the MANUAL heat curve type."""
    HEAT_CURVE_SHIFT = PointKey("heat_curve_shift", float)
    """The manual's parallel displacement: shifts the calculated temperature up or down."""
    HEAT_CURVE_INLET_MIN = PointKey("heat_curve_inlet_min", float)
    HEAT_CURVE_INLET_MAX = PointKey("heat_curve_inlet_max", float)
    HEAT_CURVE_GAIN = PointKey("heat_curve_gain", float)
    HIGH_TEMP_CUTOFF_ENABLE = PointKey("high_temp_cutoff_enable", bool)
    """Blocks heating and stops the pump when the inlet exceeds `HIGH_TEMP_CUTOFF_TEMP`."""
    HIGH_TEMP_CUTOFF_TEMP = PointKey("high_temp_cutoff_temp", float)
    WARNING = PointKey("warning", bool)
    ERROR = PointKey("error", bool)
    INLET_SENSOR_FAILURE = PointKey("inlet_sensor_failure", bool)
    HIGH_TEMP_CUTOFF_ACTIVE = PointKey("high_temp_cutoff_active", bool)

    @classmethod
    def all(cls) -> tuple[PointKey[Any], ...]:
        """Every key, in the order declared."""
        kind: type[PointKey[Any]] = PointKey
        return _members(cls, kind)


class HeatingCoolingSourcePointKey:
    """The key of each point of the heating/cooling source."""
    STATE = Key("hc_source_state", RoomState)
    WARNING = Key("hc_source_warning", bool)
    ERROR = Key("hc_source_error", bool)
    FAILURE = Key("hc_source_failure", bool)

    @classmethod
    def all(cls) -> tuple[Key[Any], ...]:
        """Every key, in the order declared."""
        kind: type[Key[Any]] = Key
        return _members(cls, kind)


class BoilerHeatPumpPointKey:
    """The key of each point of the boiler or heat pump."""
    STATE = Key("boiler_heat_pump_state", HeatSourceState)
    BLOCKING_SOURCE = Key("boiler_heat_pump_blocking_source", BlockingSource)
    TEMP_INLET_CURRENT = Key("boiler_heat_pump_temp_inlet_current", float)
    TEMP_REQUESTED = Key("boiler_heat_pump_temp_requested", float)
    NAME = Key("boiler_heat_pump_name", str)
    MIN_RUNTIME = Key("boiler_heat_pump_min_runtime", int)
    MIN_CYCLE_DELAY = Key("boiler_heat_pump_min_cycle_delay", int)
    DEMAND_START_DELAY = Key("boiler_heat_pump_demand_start_delay", int)
    DEMAND_STOP_DELAY = Key("boiler_heat_pump_demand_stop_delay", int)
    WARNING = Key("boiler_heat_pump_warning", bool)
    ERROR = Key("boiler_heat_pump_error", bool)
    INLET_SENSOR_FAILURE = Key("boiler_heat_pump_inlet_sensor_failure", bool)
    FAILURE = Key("boiler_heat_pump_failure", bool)

    @classmethod
    def all(cls) -> tuple[Key[Any], ...]:
        """Every key, in the order declared."""
        kind: type[Key[Any]] = Key
        return _members(cls, kind)


class ThermistorPointKey:
    """The key of each of the controller's thermistor inputs, T1 to T5."""
    TEMP_T1 = Key("thermistor_t1_temp", float)
    TEMP_T2 = Key("thermistor_t2_temp", float)
    TEMP_T3 = Key("thermistor_t3_temp", float)
    TEMP_T4 = Key("thermistor_t4_temp", float)
    TEMP_T5 = Key("thermistor_t5_temp", float)

    @classmethod
    def all(cls) -> tuple[Key[Any], ...]:
        """Every key, in the order declared."""
        kind: type[Key[Any]] = Key
        return _members(cls, kind)


ROOM = "room"
"""The instance label of a room: its number, 1 to ROOM_COUNT."""
PERIPHERAL = "peripheral"
"""The instance label of a peripheral slot: its number, 1 to PERIPHERAL_COUNT."""


def room_key[T](room: int, point: PointKey[T]) -> Key[T]:
    """The key of `point` in room `room`: `room_key(4, RoomPointKey.STATE)` is "room_4_state"."""
    return Key(f"room_{room}_{point.name}", point.type)


HCC = "hcc"
"""The instance label of a heating/cooling circuit: its number, 1 to HCC_COUNT."""

OBJECT = "object"
"""The label naming which of the controller's single objects a point belongs to."""
OUTDOOR = "outdoor"
HEATING_COOLING_SOURCE = "hc_source"
BOILER_HEAT_PUMP = "boiler_heat_pump"
THERMISTOR_INPUTS = "thermistor_inputs"


def hcc_key[T](hcc: int, point: PointKey[T]) -> Key[T]:
    """The key of `point` in circuit `hcc`: `hcc_key(1, HccPointKey.STATE)` is "hcc_1_state"."""
    return Key(f"hcc_{hcc}_{point.name}", point.type)


def peripheral_key[T](slot: int, point: PointKey[T]) -> Key[T]:
    """The key of `point` in slot `slot`: `peripheral_key(2, PeripheralPointKey.NAME)` is "peripheral_2_name"."""
    return Key(f"peripheral_{slot}_{point.name}", point.type)


UNITS = frozenset({Unit.CELSIUS, Unit.PERCENT, Unit.SECONDS, Unit.MINUTES})
"""Every unit a Sentio value has."""

_ALARM_KIND = "alarm"
ALARM = Labels(kind=_ALARM_KIND)
"""Every alarm and warning bit."""

SENSOR = "sensor"
"""The label kind of a room's measurements, which a room without a sensor does not have."""

ROOM_FUNCTIONS: Mapping[str, PointKey[int]] = MappingProxyType({
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


# ================================================================================ encodings
#
# How the manual's value types map to points. Its data type table gives each type's range and
# its "invalid value", which is no reading; a register may give fewer values than its type.

def _u8[T](key: Key[T], read: InputRegister | HoldingRegister, *, write: HoldingRegister | None = None,
           maximum: int = 254, poll_rate: PollRate = PollRate.SLOW, unit: Unit | None = None,
           on_write: Refresh | None = None, labels: Mapping[str, str] | None = None) -> Point[T]:
    """val_u1: 0 to `maximum`; anything above - its invalid 0xFF in particular - is no value."""
    return Point(key, read=read, write=write, data_type=DataType.UINT16, valid_raw=range(0, maximum + 1),
                 poll_rate=poll_rate,
                 unit=unit, limits=Limits(0, maximum, step=1) if write is not None else None, on_write=on_write,
                 labels=labels or {})


def _flag(key: Key[bool], register: HoldingRegister, *, on_write: Refresh | None = None) -> Point[bool]:
    """val_u1 given as "0 OFF, 1 ON"; anything else - its invalid 0xFF in particular - is no value."""
    return Point(key, read=register, write=register, data_type=DataType.BOOL, valid_raw=range(0, 2),
                 poll_rate=PollRate.SLOW, on_write=on_write)


def _choice[T](key: Key[T], register: HoldingRegister, *, on_write: Refresh | None = None) -> Point[T]:
    """val_u1 naming a state, written as one of them; its invalid 0xFF is no value."""
    return Point(key, read=register, write=register, data_type=DataType.UINT16, valid_raw=range(0, 0xFF),
                 poll_rate=PollRate.SLOW, on_write=on_write)


def _u16[T](key: Key[T], read: InputRegister | HoldingRegister, *, write: HoldingRegister | None = None,
            poll_rate: PollRate = PollRate.SLOW, write_kind: WriteKind = WriteKind.STATE,
            unit: Unit | None = None) -> Point[T]:
    """val_u2: 0 to 0xFFFE; its invalid 0xFFFF is no value."""
    return Point(key, read=read, write=write, data_type=DataType.UINT16, poll_rate=poll_rate, write_kind=write_kind,
                 valid_raw=range(0, 0xFFFF), unit=unit)


def _u32(key: Key[int], read: InputRegister | HoldingRegister, *, write: HoldingRegister | None = None,
         poll_rate: PollRate = PollRate.SLOW, unit: Unit | None = None) -> Point[int]:
    """val_u4: 0 to 0xFFFFFFFE; its invalid 0xFFFFFFFF is no value."""
    return Point(key, read=read, write=write, data_type=DataType.UINT32, valid_raw=range(0, 0xFFFFFFFF),
                 poll_rate=poll_rate, unit=unit)


def _fp100(key: Key[float], read: InputRegister | HoldingRegister, *, write: HoldingRegister | None = None,
           poll_rate: PollRate = PollRate.SLOW, unit: Unit | None = Unit.CELSIUS, on_write: Refresh | None = None,
           labels: Mapping[str, str] | None = None) -> Point[float]:
    """val_d2_fp100: signed hundredths, -327.68 to 327.66; its invalid 0x7FFF is no reading."""
    return Point(key, read=read, write=write, data_type=DataType.INT16, scale=0.01, valid_raw=range(-0x8000, 0x7FFF),
                 poll_rate=poll_rate, unit=unit, on_write=on_write, labels=labels or {})


def _fp10(key: Key[float], read: HoldingRegister, *, write: HoldingRegister | None = None) -> Point[float]:
    """val_d2_fp10: signed tenths; 0x7FFF is taken as no reading, as for val_d2_fp100.

    The manual's type table does not give this type. Its name gives tenths, and a CCU-208's heat
    curve slope and gain, both read as 10, are 1.0 that way.
    """
    return Point(key, read=read, write=write, data_type=DataType.INT16, scale=0.1, valid_raw=range(-0x8000, 0x7FFF),
                 poll_rate=PollRate.SLOW)


def _labelled(points: list[Point[Any]], **labels: str) -> list[Point[Any]]:
    """`points`, each also carrying `labels`."""
    return [replace(point, labels={**point.labels, **labels}) for point in points]


def _alarm(key: Key[bool], read: DiscreteInput) -> Point[bool]:
    """An alarm bit: read rarely by itself, and at once whenever the system's summary changes."""
    return Point(key, read=read, data_type=DataType.BOOL, poll_rate=PollRate.RARE, labels={"kind": _ALARM_KIND})


def _summary(key: Key[bool], read: DiscreteInput) -> Point[bool]:
    """One of the system's two aggregated alarm bits.

    Polled even when nobody asks for it, since its change is what sets off reading every
    other alarm bit that is subscribed to.
    """
    return Point(key, read=read, data_type=DataType.BOOL, poll_rate=PollRate.FAST, poll_always=True,
                 on_change=Refresh(ALARM))


def _text(key: Key[str], read: HoldingRegister, *, write: HoldingRegister | None = None) -> Point[str]:
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
    Point(LocationPointKey.MODBUS_MODE, read=HoldingRegister(5), data_type=DataType.UINT16, valid_raw=range(0, 0xFF),
          poll_always=True),
    # Write-only per the manual: it can never be read back. The manual: "range for password is 1 - 65534".
    Point(LocationPointKey.MODBUS_PASSWORD, write=HoldingRegister(6), data_type=DataType.UINT16,
          write_kind=WriteKind.COMMAND, valid_raw=range(1, 0xFFFF)),
    _text(LocationPointKey.LOCATION_NAME, HoldingRegister(10), write=HoldingRegister(10)),
    _flag(LocationPointKey.STANDBY_ENABLE, HoldingRegister(26), on_write=rereads(ROOM_TARGET)),
    _flag(LocationPointKey.VACATION_ENABLE, HoldingRegister(27), on_write=rereads(ROOM_TARGET)),
    _u32(LocationPointKey.DATETIME_UNIX, HoldingRegister(28), write=HoldingRegister(28), unit=Unit.SECONDS),
    _flag(LocationPointKey.DAYLIGHT_SAVING_ENABLE, HoldingRegister(30)),
    _fp100(LocationPointKey.TEMP_OUTDOOR_COOLING_MIN, HoldingRegister(31), write=HoldingRegister(31)),
    _fp100(LocationPointKey.TEMP_OUTDOOR_HEATING_MAX, HoldingRegister(32), write=HoldingRegister(32)),
    _choice(LocationPointKey.UPDATE_MODE, HoldingRegister(33)),
    _choice(LocationPointKey.HEATING_COOLING_MODE_BMS_OVERRIDE, HoldingRegister(34)),
    _u16(LocationPointKey.TIMEZONE, HoldingRegister(35), write=HoldingRegister(35)),

    # The manual: "A problem is pending in whole system" / "A critical problem is pending".
    _summary(LocationPointKey.SYSTEM_WARNING, DiscreteInput(1)),
    _summary(LocationPointKey.SYSTEM_ERROR, DiscreteInput(2)),
]


OUTDOOR_ZONE = _labelled([
    _fp100(OutdoorPointKey.AIR_TEMP, InputRegister(3301), poll_rate=PollRate.MEDIUM),
    _fp100(OutdoorPointKey.AIR_TEMP_FILTERED, InputRegister(3302), poll_rate=PollRate.MEDIUM),
    _fp100(OutdoorPointKey.AIR_TEMP_GEOMETRICAL, InputRegister(3303), poll_rate=PollRate.MEDIUM),
    _text(OutdoorPointKey.NAME, HoldingRegister(3301)),
    # The manual: 327.67, the invalid value, "means override is disabled"; so writing a number
    # sets an override, and no value can be written to clear it.
    _fp100(OutdoorPointKey.AIR_TEMP_BMS_OVERRIDE, HoldingRegister(3317), write=HoldingRegister(3317)),
    _alarm(OutdoorPointKey.WARNING, DiscreteInput(3301)),
    _alarm(OutdoorPointKey.ERROR, DiscreteInput(3302)),
    _alarm(OutdoorPointKey.LOW_BATTERY, DiscreteInput(3303)),
    _alarm(OutdoorPointKey.PERIPHERAL_LOST, DiscreteInput(3304)),
], object=OUTDOOR)

HEATING_COOLING_SOURCE_POINTS = _labelled([
    _u8(HeatingCoolingSourcePointKey.STATE, InputRegister(8101), poll_rate=PollRate.FAST),
    _alarm(HeatingCoolingSourcePointKey.WARNING, DiscreteInput(8101)),
    _alarm(HeatingCoolingSourcePointKey.ERROR, DiscreteInput(8102)),
    _alarm(HeatingCoolingSourcePointKey.FAILURE, DiscreteInput(8103)),
], object=HEATING_COOLING_SOURCE)

BOILER_HEAT_PUMP_POINTS = _labelled([
    _u8(BoilerHeatPumpPointKey.STATE, InputRegister(8201), poll_rate=PollRate.FAST),
    _u8(BoilerHeatPumpPointKey.BLOCKING_SOURCE, InputRegister(8202), poll_rate=PollRate.FAST),
    _fp100(BoilerHeatPumpPointKey.TEMP_INLET_CURRENT, InputRegister(8203), poll_rate=PollRate.MEDIUM),
    _fp100(BoilerHeatPumpPointKey.TEMP_REQUESTED, InputRegister(8204), poll_rate=PollRate.MEDIUM),
    _text(BoilerHeatPumpPointKey.NAME, HoldingRegister(8201), write=HoldingRegister(8201)),
    _u16(BoilerHeatPumpPointKey.MIN_RUNTIME, HoldingRegister(8217), write=HoldingRegister(8217), unit=Unit.MINUTES),
    _u16(BoilerHeatPumpPointKey.MIN_CYCLE_DELAY, HoldingRegister(8218), write=HoldingRegister(8218),
         unit=Unit.MINUTES),
    _u16(BoilerHeatPumpPointKey.DEMAND_START_DELAY, HoldingRegister(8219), write=HoldingRegister(8219),
         unit=Unit.MINUTES),
    _u16(BoilerHeatPumpPointKey.DEMAND_STOP_DELAY, HoldingRegister(8220), write=HoldingRegister(8220),
         unit=Unit.MINUTES),
    _alarm(BoilerHeatPumpPointKey.WARNING, DiscreteInput(8201)),
    _alarm(BoilerHeatPumpPointKey.ERROR, DiscreteInput(8202)),
    _alarm(BoilerHeatPumpPointKey.INLET_SENSOR_FAILURE, DiscreteInput(8203)),
    _alarm(BoilerHeatPumpPointKey.FAILURE, DiscreteInput(8204)),
], object=BOILER_HEAT_PUMP)

THERMISTOR_INPUT_POINTS = _labelled([
    _fp100(key, InputRegister(12800 + number), poll_rate=PollRate.MEDIUM)
    for number, key in enumerate(ThermistorPointKey.all(), start=1)
], object=THERMISTOR_INPUTS)


def hcc(n: int) -> list[Point[Any]]:
    """One heating/cooling circuit's points."""
    base = hcc_base(n)

    def setting(point: PointKey[float], offset: int) -> Point[float]:
        return _fp100(hcc_key(n, point), HoldingRegister(base + offset), write=HoldingRegister(base + offset))

    return [
        _u8(hcc_key(n, HccPointKey.STATE), InputRegister(base + 1), poll_rate=PollRate.FAST),
        _u8(hcc_key(n, HccPointKey.BLOCKING_SOURCE), InputRegister(base + 2), poll_rate=PollRate.FAST),
        _u8(hcc_key(n, HccPointKey.PUMP_DEMAND), InputRegister(base + 3), poll_rate=PollRate.FAST),
        _u8(hcc_key(n, HccPointKey.PUMP_STATE), InputRegister(base + 4), poll_rate=PollRate.FAST),
        _fp100(hcc_key(n, HccPointKey.TEMP_INLET_CURRENT), InputRegister(base + 5), poll_rate=PollRate.MEDIUM),
        _fp100(hcc_key(n, HccPointKey.TEMP_INLET_TARGET), InputRegister(base + 6), poll_rate=PollRate.MEDIUM),
        _fp100(hcc_key(n, HccPointKey.TEMP_ROOM_TARGET), InputRegister(base + 8), poll_rate=PollRate.MEDIUM),
        _text(hcc_key(n, HccPointKey.NAME), HoldingRegister(base + 1), write=HoldingRegister(base + 1)),
        _choice(hcc_key(n, HccPointKey.HEAT_CURVE_TYPE), HoldingRegister(base + 17)),
        _fp10(hcc_key(n, HccPointKey.HEAT_CURVE_SLOPE), HoldingRegister(base + 18), write=HoldingRegister(base + 18)),
        setting(HccPointKey.HEAT_CURVE_SHIFT, 19),
        setting(HccPointKey.HEAT_CURVE_INLET_MIN, 20),
        setting(HccPointKey.HEAT_CURVE_INLET_MAX, 21),
        _fp10(hcc_key(n, HccPointKey.HEAT_CURVE_GAIN), HoldingRegister(base + 22), write=HoldingRegister(base + 22)),
        _flag(hcc_key(n, HccPointKey.HIGH_TEMP_CUTOFF_ENABLE), HoldingRegister(base + 23)),
        setting(HccPointKey.HIGH_TEMP_CUTOFF_TEMP, 24),
        _alarm(hcc_key(n, HccPointKey.WARNING), DiscreteInput(base + 1)),
        _alarm(hcc_key(n, HccPointKey.ERROR), DiscreteInput(base + 2)),
        _alarm(hcc_key(n, HccPointKey.INLET_SENSOR_FAILURE), DiscreteInput(base + 3)),
        _alarm(hcc_key(n, HccPointKey.HIGH_TEMP_CUTOFF_ACTIVE), DiscreteInput(base + 4)),
    ]


def room(n: int) -> list[Point[Any]]:
    """One room's points."""
    base = room_base(n)

    def state[T](point: PointKey[T], offset: int, function: str | None = None) -> Point[T]:
        return _u8(room_key(n, point), InputRegister(base + offset), poll_rate=PollRate.FAST,
                   labels={"function": function} if function else None)

    def sensor(point: PointKey[float], offset: int, unit: Unit = Unit.CELSIUS) -> Point[float]:
        return _fp100(room_key(n, point), InputRegister(base + offset), poll_rate=PollRate.MEDIUM, unit=unit,
                      labels={"kind": SENSOR})

    def associated(point: PointKey[int], offset: int) -> Point[int]:
        return _u8(room_key(n, point), InputRegister(base + offset), poll_rate=PollRate.STATIC)

    retarget = rereads(ROOM_TARGET, room=n)

    def setting(point: PointKey[float], offset: int, unit: Unit = Unit.CELSIUS,
                on_write: Refresh | None = None) -> Point[float]:
        return _fp100(room_key(n, point), HoldingRegister(base + offset), write=HoldingRegister(base + offset),
                      unit=unit, on_write=on_write)

    def switch(point: PointKey[int], offset: int, maximum: int, on_write: Refresh | None = None) -> Point[int]:
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
        _choice(room_key(n, RoomPointKey.MODE), HoldingRegister(base + 17), on_write=retarget),
        _choice(room_key(n, RoomPointKey.MODE_OVERRIDE), HoldingRegister(base + 18), on_write=retarget),
        setting(RoomPointKey.TEMP_AIR_TARGET, 19, on_write=retarget),
        Point(room_key(n, RoomPointKey.LOCK), read=HoldingRegister(base + 20), write=HoldingRegister(base + 20)),
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
        _choice(room_key(n, RoomPointKey.TEMP_PRESET), HoldingRegister(base + 35), on_write=retarget),

        # --- discrete inputs: its alarms
        _alarm(room_key(n, RoomPointKey.WARNING), DiscreteInput(base + 1)),
        _alarm(room_key(n, RoomPointKey.ERROR), DiscreteInput(base + 2)),
        _alarm(room_key(n, RoomPointKey.LOW_BATTERY), DiscreteInput(base + 3)),
        _alarm(room_key(n, RoomPointKey.PERIPHERAL_LOST), DiscreteInput(base + 4)),
    ]


def peripheral(slot: int) -> list[Point[Any]]:
    """One peripheral slot's points."""
    base = peripheral_base(slot)
    return [
        _u16(peripheral_key(slot, PeripheralPointKey.TYPE), InputRegister(base + 1), poll_rate=PollRate.STATIC),
        _u32(peripheral_key(slot, PeripheralPointKey.SERIAL_NUMBER), InputRegister(base + 2), poll_rate=PollRate.STATIC),
        _u16(peripheral_key(slot, PeripheralPointKey.OWNER), InputRegister(base + 4), poll_rate=PollRate.STATIC),
        _u8(peripheral_key(slot, PeripheralPointKey.SIGNAL_STRENGTH), InputRegister(base + 5), poll_rate=PollRate.RARE),
        _text(peripheral_key(slot, PeripheralPointKey.NAME), HoldingRegister(base + 1)),
        _alarm(peripheral_key(slot, PeripheralPointKey.WARNING), DiscreteInput(base + 1)),
        _alarm(peripheral_key(slot, PeripheralPointKey.ERROR), DiscreteInput(base + 2)),
        _alarm(peripheral_key(slot, PeripheralPointKey.LOW_BATTERY), DiscreteInput(base + 3)),
        _alarm(peripheral_key(slot, PeripheralPointKey.LOST), DiscreteInput(base + 4)),
    ]


# ==================================================================================== scan


async def check_the_controller(scan: Scan) -> None:
    """Warn when the controller's address space is older than this map was written against.

    The software version and serial number are read too, though never polled: new firmware, or
    another controller, then changes what this scan read, and everything is scanned again.
    """
    found = await scan.read((LocationPointKey.DATAPOINT_MAJOR, LocationPointKey.DATAPOINT_MINOR,
                             LocationPointKey.SOFTWARE_MAJOR, LocationPointKey.SOFTWARE_MINOR,
                             LocationPointKey.SERIAL_NUMBER_PREFIX, LocationPointKey.SERIAL_NUMBER))
    major, minor = found[LocationPointKey.DATAPOINT_MAJOR].value, found[LocationPointKey.DATAPOINT_MINOR].value
    if isinstance(major, int) and isinstance(minor, int) and (major, minor) < ADDRESS_SPACE_REQUIRED:
        _LOGGER.warning("Sentio address space %d.%d is older than the %d.%d this register map was "
                        "written against. Some registers may be unavailable; update the control unit.",
                        major, minor, *ADDRESS_SPACE_REQUIRED)


SINGLE_OBJECTS: Mapping[str, Key[Any]] = MappingProxyType({
    OUTDOOR: OutdoorPointKey.AIR_TEMP,
    HEATING_COOLING_SOURCE: HeatingCoolingSourcePointKey.STATE,
    BOILER_HEAT_PUMP: BoilerHeatPumpPointKey.STATE,
    THERMISTOR_INPUTS: ThermistorPointKey.TEMP_T1,
})
"""Each of the controller's single objects, and the point whose register it has when it has it."""


async def find_the_objects(scan: Scan) -> None:
    """Remove each of the controller's single objects whose register it refuses.

    A register the controller answers, even with "no reading", is taken as the object's: the
    manual gives "no reading" also for a wireless peripheral that is late to answer.
    """
    found = await scan.read(tuple(SINGLE_OBJECTS.values()))
    for name, key in SINGLE_OBJECTS.items():
        if found[key].quality is Quality.MISSING:
            scan.set_available(Labels(**{OBJECT: name}), False, reason=f"the controller has no {name}")


async def scan_hcc(scan: Scan, n: int) -> None:
    """Remove heating/cooling circuit `n` if the controller refuses its registers."""
    state = hcc_key(n, HccPointKey.STATE)
    if (await scan.read((state,)))[state].quality is Quality.MISSING:
        scan.set_available(Labels(**{HCC: n}), False, reason="the controller has no such circuit")


async def scan_room(scan: Scan, n: int) -> None:
    """Remove room `n` if it is not configured, and what it states it does not have.

    The manual: a DUMMY room has "no thermostat or sensor installed", and an association of 0
    is NONE. An unknown or unread value removes nothing.
    """
    kind = (await scan.read((room_key(n, RoomPointKey.TYPE),)))[room_key(n, RoomPointKey.TYPE)]
    if kind.quality is Quality.MISSING:
        scan.set_available(Labels(room=n), False, reason="room not configured")
    if kind.quality is not Quality.GOOD:
        return
    if kind.value == RoomType.DUMMY:
        scan.set_available(Labels(room=n, kind=SENSOR), False, reason="a dummy room has no sensor")
    found = await scan.read(tuple(room_key(n, point) for point in ROOM_FUNCTIONS.values()))
    for function, point in ROOM_FUNCTIONS.items():
        association = found[room_key(n, point)]
        if association.quality is Quality.GOOD and association.value == 0:
            scan.set_available(Labels(room=n, function=function), False,
                               reason=f"the room is not associated with {function}")


async def scan_peripheral(scan: Scan, slot: int) -> None:
    """Remove peripheral slot `slot` if nothing is paired in it, and the points its type does
    not have.

    The serial number and owner are read too, though never polled: another peripheral in the
    slot, or one moved to another room, then changes what this scan read, and the slot is read
    afresh.
    """
    kind = peripheral_key(slot, PeripheralPointKey.TYPE)
    found = (await scan.read((kind,)))[kind]
    if found.quality is Quality.MISSING:
        scan.set_available(Labels(peripheral=slot), False, reason="no peripheral in this slot")
        return
    if found.quality is Quality.GOOD and isinstance(found.value, PeripheralType):
        model = found.value.name.replace("_", "-")
        for point in NOT_SUPPORTED.get(found.value, frozenset()):
            scan.set_available((peripheral_key(slot, point),), False,
                               reason=f"{model} has no {point.name.replace('_', ' ')}")
    await scan.read((peripheral_key(slot, PeripheralPointKey.SERIAL_NUMBER),
                     peripheral_key(slot, PeripheralPointKey.OWNER)))


SENTIO = Model(
    name="Sentio",
    manufacturer="Wavin",
    options=ModbusOptions(numbering=plain(first_address=1), max_registers=MAX_REGISTERS),  # verified live
    read_back_after=0.5,  # measured with testing.measure_read_back on a CCU-208, address space 3.7
    sections=[
        Section(LOCATION),
        RepeatedSection(room, range(1, ROOM_COUNT + 1), label=ROOM, scan=scan_room),
        RepeatedSection(peripheral, range(1, PERIPHERAL_COUNT + 1), label=PERIPHERAL, scan=scan_peripheral),
        Section(OUTDOOR_ZONE),
        RepeatedSection(hcc, range(1, HCC_COUNT + 1), label=HCC, scan=scan_hcc),
        Section(HEATING_COOLING_SOURCE_POINTS),
        Section(BOILER_HEAT_PUMP_POINTS),
        Section(THERMISTOR_INPUT_POINTS),
    ],
    scan_steps=[check_the_controller, find_the_objects],
)
