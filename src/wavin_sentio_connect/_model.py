"""The Wavin Sentio CCU-208 register map, as a modbus_event_connect model."""
from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from enum import IntEnum, IntFlag
from typing import Any
from types import MappingProxyType

from modbus_event_connect import (
    DataType,
    InstanceScanStep,
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
ITC_COUNT = 2
"""Sentio inlet temperature controllers the address space defines. ITC N's start at 7200 + N * 100."""
VENTILATION_COUNT = 2
"""Ventilation units the address space defines. Unit N's registers start at 60900 + N * 100."""
DEHUMIDIFIER_COUNT = 4
"""Dehumidifiers the address space defines. Dehumidifier N's registers start at 64900 + N * 100."""
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


def itc_base(itc: int) -> int:
    """Base address of a Sentio ITC. ITC 1 -> 7300, ITC 2 -> 7400."""
    return 7200 + itc * 100


def ventilation_base(unit: int) -> int:
    """Base address of a ventilation unit. Unit 1 -> 61000, unit 2 -> 61100."""
    return 60900 + unit * 100


def dehumidifier_base(unit: int) -> int:
    """Base address of a dehumidifier. Dehumidifier 1 -> 65000, 4 -> 65300."""
    return 64900 + unit * 100


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
    """Values of the boiler/heat pump's and the buffer tank's state registers."""
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


class DhwTankState(IntEnum):
    """Values of the DHW tank's state register.

    The manual marks the register changed in address space 3.4 and gives only these values.
    """
    OFF = 0
    IDLE = 1
    HEATING = 2
    CLEANING = 3
    BLOCKED_HEATING = 4
    BLOCKED_CLEANING = 5
    FAILURE = 6


class CirculationState(IntEnum):
    """Values of the DHW tank's circulation state register."""
    NONE = 0
    """Circulation is disabled."""
    IDLE = 1
    ON = 2


class DhwMode(IntEnum):
    """Values of the DHW tank's mode register; the manual gives no value 1."""
    SCHEDULE = 0
    ECO = 2
    """Circulation is disabled."""


class ReturnLimiterFunction(IntEnum):
    """Values of an ITC's return temperature limiter function register."""
    OFF = 0
    MIN = 1
    MAX = 2


class BufferSensorPriority(IntEnum):
    """Values of the buffer tank's sensor priority register."""
    UPPER_SENSOR = 0
    LOWER_SENSOR = 1


class ChargeMode(IntEnum):
    """Values of the buffer tank's charge mode register."""
    CONSUMER_ONLY = 0
    DEMAND_TRIGGERED = 1


class VentilationUnitState(IntEnum):
    """Values of a ventilation unit's state register."""
    STOPPED = 0
    UNOCCUPIED = 1
    ECONOMY = 2
    COMFORT = 3
    BOOST = 4
    BLOCKED_STOPPED = 5
    BLOCKED_UNOCCUPIED = 6
    BLOCKED_ECONOMY = 7
    BLOCKED_COMFORT = 8
    BLOCKED_BOOST = 9
    FAILURE = 10
    MAINTENANCE = 11


class VentilationLevel(IntEnum):
    """Values of a ventilation unit's standby and vacation level registers."""
    STOPPED = 0
    UNOCCUPIED = 1
    ECONOMY = 2


class HeatExchangeMode(IntEnum):
    """Values of a ventilation unit's heat exchange mode (recovery bypass) register."""
    ALWAYS_ON = 0
    AUTOMATIC = 1


class VentilationFeature(IntFlag):
    """The bits of a ventilation unit's feature register, which reads as an `int`:
    `VentilationFeature.TEMP_SUPPLY in VentilationFeature(value)`."""
    ALLOW_UNOCCUPIED = 0x0001
    ALLOW_ECO = 0x0002
    ALLOW_COMFORT = 0x0004
    ALLOW_STOPPED = 0x0008
    ALLOW_BOOST = 0x0010
    ALLOW_BYPASS = 0x0020
    FAN_PWM_CONTROL = 0x0040
    FAN_BINARY_CONTROL = 0x0080
    TEMP_INTAKE = 0x0100
    TEMP_SUPPLY = 0x0200
    TEMP_EXTRACT = 0x0400
    TEMP_EXHAUST = 0x0800
    HUMIDITY_INTAKE = 0x1000
    HUMIDITY_EXTRACT = 0x2000
    FAN_SPEED_FEEDBACK = 0x4000


class DehumidifierType(IntEnum):
    """Values of a dehumidifier's type register."""
    GENERIC = 0
    P300_S300 = 1
    PC300_SC300 = 2


class AllowedInMode(IntEnum):
    """Values of a dehumidifier's drying and thermal integration "allow in mode" registers."""
    IN_COOLING_MODE = 0
    IN_HEATING_MODE = 1
    IN_BOTH = 2


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


class DhwTankPointKey:
    """The key of each point of the domestic hot water (DHW) tank.

    Modelled from the manual alone: no controller that has it has been read.
    """
    TEMP_CURRENT = Key("dhw_tank_temp_current", float)
    TEMP_TARGET = Key("dhw_tank_temp_target", float)
    """The temperature the tank is kept at now, by schedule or setting; the manual notes it differs
    from the temperature at the tap."""
    STATE = Key("dhw_tank_state", DhwTankState)
    BLOCKING_SOURCE = Key("dhw_tank_blocking_source", BlockingSource)
    CIRCULATION_STATE = Key("dhw_tank_circulation_state", CirculationState)
    TEMP_CIRCULATION_RETURN = Key("dhw_tank_temp_circulation_return", float)
    TEMP_SOURCE_INLET = Key("dhw_tank_temp_source_inlet", float)
    TEMP_SOURCE_RETURN = Key("dhw_tank_temp_source_return", float)
    NAME = Key("dhw_tank_name", str)
    MODE = Key("dhw_tank_mode", DhwMode)
    CIRCULATION_COOLDOWN = Key("dhw_tank_circulation_cooldown", int)
    """How long circulation stays off after the stop temperature difference paused it; the manual
    gives no unit."""
    CIRCULATION_STOP_DIFFERENCE = Key("dhw_tank_circulation_stop_difference", float)
    SOURCE_RETURN_TEMP_LIMIT = Key("dhw_tank_source_return_temp_limit", float)
    """Used only in the manual's "advanced tank mode"."""
    TEMP_SET = Key("dhw_tank_temp_set", float)
    TEMP_SET_VACATION = Key("dhw_tank_temp_set_vacation", float)
    TEMP_SET_CLEANING = Key("dhw_tank_temp_set_cleaning", float)
    TEMP_SET_STANDBY = Key("dhw_tank_temp_set_standby", float)
    EXCLUDE_FROM_VACATION = Key("dhw_tank_exclude_from_vacation", int)
    EXCLUDE_FROM_STANDBY = Key("dhw_tank_exclude_from_standby", int)
    WARNING = Key("dhw_tank_warning", bool)
    ERROR = Key("dhw_tank_error", bool)
    CLEANING_FAILED = Key("dhw_tank_cleaning_failed", bool)
    TANK_SENSOR_FAILURE = Key("dhw_tank_tank_sensor_failure", bool)
    CIRCULATION_RETURN_SENSOR_FAILURE = Key("dhw_tank_circulation_return_sensor_failure", bool)
    SOURCE_RETURN_SENSOR_FAILURE = Key("dhw_tank_source_return_sensor_failure", bool)
    SOURCE_INLET_SENSOR_FAILURE = Key("dhw_tank_source_inlet_sensor_failure", bool)
    SOURCE_INLET_TEMP_TOO_LOW = Key("dhw_tank_source_inlet_temp_too_low", bool)
    LOW_BATTERY = Key("dhw_tank_low_battery", bool)
    PERIPHERAL_LOST = Key("dhw_tank_peripheral_lost", bool)

    @classmethod
    def all(cls) -> tuple[Key[Any], ...]:
        """Every key, in the order declared."""
        kind: type[Key[Any]] = Key
        return _members(cls, kind)


class ItcPointKey:
    """The key of each point within an inlet temperature controller (ITC); `itc_key` makes it the
    point's key.

    Modelled from the manual alone: no controller that has it has been read.
    """
    STATE = PointKey("state", RoomState)
    BLOCKING_SOURCE = PointKey("blocking_source", BlockingSource)
    PUMP_DEMAND = PointKey("pump_demand", PumpState)
    PUMP_STATE = PointKey("pump_state", PumpState)
    TEMP_INLET_CURRENT = PointKey("temp_inlet_current", float)
    TEMP_INLET_TARGET = PointKey("temp_inlet_target", float)
    TEMP_RETURN_CURRENT = PointKey("temp_return_current", float)
    TEMP_MAIN_SUPPLIER = PointKey("temp_main_supplier", float)
    SERVO_POSITION_REQUEST = PointKey("servo_position_request", float)
    TEMP_ROOM_TARGET = PointKey("temp_room_target", float)
    NAME = PointKey("name", str)
    REGULATOR_P = PointKey("regulator_p", float)
    REGULATOR_I = PointKey("regulator_i", int)
    """The regulator's integrating time; the manual gives no unit."""
    REGULATOR_HYSTERESIS = PointKey("regulator_hysteresis", float)
    HEAT_CURVE_TYPE = PointKey("heat_curve_type", HeatCurveType)
    HEAT_CURVE_SLOPE = PointKey("heat_curve_slope", float)
    HEAT_CURVE_SHIFT = PointKey("heat_curve_shift", float)
    HEAT_CURVE_INLET_MIN = PointKey("heat_curve_inlet_min", float)
    HEAT_CURVE_INLET_MAX = PointKey("heat_curve_inlet_max", float)
    HEAT_CURVE_GAIN = PointKey("heat_curve_gain", float)
    RETURN_LIMITER_FUNCTION = PointKey("return_limiter_function", ReturnLimiterFunction)
    RETURN_MAX_LIMIT = PointKey("return_max_limit", float)
    RETURN_MAX_GAIN = PointKey("return_max_gain", float)
    RETURN_MAX_PRIORITY = PointKey("return_max_priority", bool)
    """Whether the return limiter may override the heat curve's minimum inlet."""
    RETURN_MIN_LIMIT = PointKey("return_min_limit", float)
    RETURN_MIN_GAIN = PointKey("return_min_gain", float)
    BOOST_ENABLE = PointKey("boost_enable", bool)
    """Raises the desired temperature by the boost flow for an hour, per the manual."""
    BOOST_FLOW = PointKey("boost_flow", int)
    RAMPING_ENABLE = PointKey("ramping_enable", bool)
    RAMPING_TIME = PointKey("ramping_time", int)
    """The manual gives no unit."""
    FROST_PROTECTION_MODE = PointKey("frost_protection_mode", int)
    """The manual gives no values."""
    FROST_PROTECTION_TEMP = PointKey("frost_protection_temp", float)
    HIGH_TEMP_CUTOFF_ENABLE = PointKey("high_temp_cutoff_enable", bool)
    HIGH_TEMP_CUTOFF_TEMP = PointKey("high_temp_cutoff_temp", float)
    COOLING_REGULATOR_P = PointKey("cooling_regulator_p", float)
    COOLING_REGULATOR_I = PointKey("cooling_regulator_i", int)
    COOLING_REGULATOR_HYSTERESIS = PointKey("cooling_regulator_hysteresis", float)
    COOLING_INLET_MIN = PointKey("cooling_inlet_min", float)
    COOLING_INLET_MAX = PointKey("cooling_inlet_max", float)
    WARNING = PointKey("warning", bool)
    ERROR = PointKey("error", bool)
    INLET_SENSOR_FAILURE = PointKey("inlet_sensor_failure", bool)
    SERVO_FAILURE = PointKey("servo_failure", bool)
    RETURN_SENSOR_FAILURE = PointKey("return_sensor_failure", bool)
    OUTDOOR_SENSOR_FAILURE = PointKey("outdoor_sensor_failure", bool)
    HIGH_TEMP_CUTOFF_ACTIVE = PointKey("high_temp_cutoff_active", bool)
    FROST_PROTECTION_ACTIVE = PointKey("frost_protection_active", bool)

    @classmethod
    def all(cls) -> tuple[PointKey[Any], ...]:
        """Every key, in the order declared."""
        kind: type[PointKey[Any]] = PointKey
        return _members(cls, kind)


class BufferTankPointKey:
    """The key of each point of the buffer tank.

    Modelled from the manual alone: no controller that has it has been read.
    """
    STATE = Key("buffer_tank_state", HeatSourceState)
    BLOCKING_SOURCE = Key("buffer_tank_blocking_source", BlockingSource)
    TEMP_SOURCE_INLET = Key("buffer_tank_temp_source_inlet", float)
    TEMP_UPPER = Key("buffer_tank_temp_upper", float)
    TEMP_LOWER = Key("buffer_tank_temp_lower", float)
    NAME = Key("buffer_tank_name", str)
    START_DIFFERENCE = Key("buffer_tank_start_difference", float)
    STOP_DIFFERENCE = Key("buffer_tank_stop_difference", float)
    SENSOR_PRIORITY = Key("buffer_tank_sensor_priority", BufferSensorPriority)
    FLOW_BALANCING_ENABLE = Key("buffer_tank_flow_balancing_enable", bool)
    CHARGE_MODE = Key("buffer_tank_charge_mode", ChargeMode)
    CHARGE_EVALUATION_DELAY = Key("buffer_tank_charge_evaluation_delay", int)
    WARNING = Key("buffer_tank_warning", bool)
    ERROR = Key("buffer_tank_error", bool)
    INLET_SENSOR_FAILURE = Key("buffer_tank_inlet_sensor_failure", bool)
    PRIORITY_SENSOR_FAILURE = Key("buffer_tank_priority_sensor_failure", bool)
    UPPER_SENSOR_FAILURE = Key("buffer_tank_upper_sensor_failure", bool)
    LOWER_SENSOR_FAILURE = Key("buffer_tank_lower_sensor_failure", bool)

    @classmethod
    def all(cls) -> tuple[Key[Any], ...]:
        """Every key, in the order declared."""
        kind: type[Key[Any]] = Key
        return _members(cls, kind)


class VentilationPointKey:
    """The key of each point within a ventilation unit; `ventilation_key` makes it the point's key.

    Modelled from the manual alone: no controller that has it has been read. The manual: ventilation units are connected by the controller's Modbus RTU master.
    """
    DEVICE_MODEL = PointKey("device_model", str)
    WARNING_CODE = PointKey("warning_code", int)
    ERROR_CODE = PointKey("error_code", int)
    FEATURES = PointKey("features", int)
    """The unit's capabilities; `VentilationFeature` names the bits."""
    STATE = PointKey("state", VentilationUnitState)
    BLOCKING_SOURCE = PointKey("blocking_source", BlockingSource)
    SUPPLY_FAN_SPEED = PointKey("supply_fan_speed", int)
    EXHAUST_FAN_SPEED = PointKey("exhaust_fan_speed", int)
    SUPPLY_FAN_SETPOINT = PointKey("supply_fan_setpoint", float)
    EXHAUST_FAN_SETPOINT = PointKey("exhaust_fan_setpoint", float)
    SUPPLY_FLOW_SETPOINT = PointKey("supply_flow_setpoint", int)
    EXHAUST_FLOW_SETPOINT = PointKey("exhaust_flow_setpoint", int)
    TEMP_INTAKE = PointKey("temp_intake", float)
    TEMP_SUPPLY = PointKey("temp_supply", float)
    TEMP_EXTRACT = PointKey("temp_extract", float)
    TEMP_EXHAUST = PointKey("temp_exhaust", float)
    BYPASS_DAMPER_POSITION = PointKey("bypass_damper_position", float)
    FREE_COOLING = PointKey("free_cooling", int)
    """The manual gives no values."""
    AIR_FILTER_LAST_CHANGE = PointKey("air_filter_last_change", int)
    """A timestamp, set when the filter's used lifetime is written to zero."""
    NAME = PointKey("name", str)
    AIR_FILTER_LIFETIME = PointKey("air_filter_lifetime", int)
    AIR_FILTER_LIFETIME_USED = PointKey("air_filter_lifetime_used", int)
    """Writing 0 resets it; the manual gives no unit."""
    EXHAUST_LEVEL_UNOCCUPIED = PointKey("exhaust_level_unoccupied", float)
    EXHAUST_LEVEL_ECO = PointKey("exhaust_level_eco", float)
    EXHAUST_LEVEL_COMFORT = PointKey("exhaust_level_comfort", float)
    EXHAUST_LEVEL_BOOST = PointKey("exhaust_level_boost", float)
    SUPPLY_LEVEL_UNOCCUPIED = PointKey("supply_level_unoccupied", float)
    SUPPLY_LEVEL_ECO = PointKey("supply_level_eco", float)
    SUPPLY_LEVEL_COMFORT = PointKey("supply_level_comfort", float)
    SUPPLY_LEVEL_BOOST = PointKey("supply_level_boost", float)
    EXHAUST_FLOW_UNOCCUPIED = PointKey("exhaust_flow_unoccupied", int)
    EXHAUST_FLOW_ECO = PointKey("exhaust_flow_eco", int)
    EXHAUST_FLOW_COMFORT = PointKey("exhaust_flow_comfort", int)
    EXHAUST_FLOW_BOOST = PointKey("exhaust_flow_boost", int)
    SUPPLY_FLOW_UNOCCUPIED = PointKey("supply_flow_unoccupied", int)
    """The manual names this register "Exhaust Fan Level Boost [m^3/h]", as the one before it, but
    describes it as "Supply Fan Level Unoccupied [m^3/h]", which its place in the table gives."""
    SUPPLY_FLOW_ECO = PointKey("supply_flow_eco", int)
    SUPPLY_FLOW_COMFORT = PointKey("supply_flow_comfort", int)
    SUPPLY_FLOW_BOOST = PointKey("supply_flow_boost", int)
    ALLOW_STOPPED = PointKey("allow_stopped", bool)
    ALLOW_UNOCCUPIED = PointKey("allow_unoccupied", bool)
    STANDBY_LEVEL = PointKey("standby_level", VentilationLevel)
    VACATION_LEVEL = PointKey("vacation_level", VentilationLevel)
    HEAT_EXCHANGE_MODE = PointKey("heat_exchange_mode", HeatExchangeMode)
    WARNING = PointKey("warning", bool)
    ERROR = PointKey("error", bool)
    AIR_FILTER_EXPIRED = PointKey("air_filter_expired", bool)
    AIR_FILTER_YEAR_PASSED = PointKey("air_filter_year_passed", bool)
    DEVICE_WARNING = PointKey("device_warning", bool)
    DEVICE_FAULT = PointKey("device_fault", bool)
    COMMUNICATION_ERROR = PointKey("communication_error", bool)
    NOT_COMPATIBLE = PointKey("not_compatible", bool)
    DEVICE_ERROR = PointKey("device_error", bool)

    @classmethod
    def all(cls) -> tuple[PointKey[Any], ...]:
        """Every key, in the order declared."""
        kind: type[PointKey[Any]] = PointKey
        return _members(cls, kind)


class DehumidifierPointKey:
    """The key of each point within a dehumidifier; `dehumidifier_key` makes it the point's key.

    Modelled from the manual alone: no controller that has it has been read.
    """
    TYPE = PointKey("type", DehumidifierType)
    DRYING_STATE = PointKey("drying_state", DryingState)
    DRYING_BLOCKING_SOURCE = PointKey("drying_blocking_source", BlockingSource)
    THERMAL_INTEGRATION_STATE = PointKey("thermal_integration_state", RoomState)
    THERMAL_INTEGRATION_BLOCKING_SOURCE = PointKey("thermal_integration_blocking_source", BlockingSource)
    THERMAL_INTEGRATION_DEMAND_CONDITION = PointKey("thermal_integration_demand_condition", int)
    """100: in any room, 101: in all rooms, 1-32: the room object at that address, per the manual."""
    AIR_FILTER_LAST_CHANGE = PointKey("air_filter_last_change", int)
    """A timestamp, set when the filter's used lifetime is written to zero."""
    HCW_SUPPLIER = PointKey("hcw_supplier", int)
    """The heating/cooling water supplier's object address - 73 ITC 1, 74 ITC 2, 77-79 HCC 1-3,
    81 the heating/cooling source - or 0 for none, per the manual."""
    NAME = PointKey("name", str)
    AIR_FILTER_LIFETIME = PointKey("air_filter_lifetime", int)
    AIR_FILTER_LIFETIME_USED = PointKey("air_filter_lifetime_used", int)
    """Writing 0 resets it; the manual gives no unit."""
    DRYING_ALLOWED_IN = PointKey("drying_allowed_in", AllowedInMode)
    DRYING_COOLING_WATER_TEMP = PointKey("drying_cooling_water_temp", float)
    THERMAL_INTEGRATION_ALLOWED_IN = PointKey("thermal_integration_allowed_in", AllowedInMode)
    THERMAL_INTEGRATION_HEATING_WATER_TEMP = PointKey("thermal_integration_heating_water_temp", float)
    THERMAL_INTEGRATION_COOLING_WATER_TEMP = PointKey("thermal_integration_cooling_water_temp", float)
    WARNING = PointKey("warning", bool)
    ERROR = PointKey("error", bool)
    AIR_FILTER_EXPIRED = PointKey("air_filter_expired", bool)
    AIR_FILTER_YEAR_PASSED = PointKey("air_filter_year_passed", bool)
    HCW_SUPPLIER_NOT_SET = PointKey("hcw_supplier_not_set", bool)
    DEVICE_FAULT = PointKey("device_fault", bool)

    @classmethod
    def all(cls) -> tuple[PointKey[Any], ...]:
        """Every key, in the order declared."""
        kind: type[PointKey[Any]] = PointKey
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
DHW_TANK = "dhw_tank"
BUFFER_TANK = "buffer_tank"
ITC = "itc"
"""The instance label of an inlet temperature controller: its number, 1 to ITC_COUNT."""
VENTILATION = "ventilation"
"""The instance label of a ventilation unit: its number, 1 to VENTILATION_COUNT."""
DEHUMIDIFIER = "dehumidifier"
"""The instance label of a dehumidifier: its number, 1 to DEHUMIDIFIER_COUNT."""


def itc_key[T](itc: int, point: PointKey[T]) -> Key[T]:
    """The key of `point` in ITC `itc`: `itc_key(1, ItcPointKey.STATE)` is "itc_1_state"."""
    return Key(f"itc_{itc}_{point.name}", point.type)


def ventilation_key[T](unit: int, point: PointKey[T]) -> Key[T]:
    """The key of `point` in ventilation unit `unit`: "ventilation_1_state"."""
    return Key(f"ventilation_{unit}_{point.name}", point.type)


def dehumidifier_key[T](unit: int, point: PointKey[T]) -> Key[T]:
    """The key of `point` in dehumidifier `unit`: "dehumidifier_1_type"."""
    return Key(f"dehumidifier_{unit}_{point.name}", point.type)


def hcc_key[T](hcc: int, point: PointKey[T]) -> Key[T]:
    """The key of `point` in circuit `hcc`: `hcc_key(1, HccPointKey.STATE)` is "hcc_1_state"."""
    return Key(f"hcc_{hcc}_{point.name}", point.type)


def peripheral_key[T](slot: int, point: PointKey[T]) -> Key[T]:
    """The key of `point` in slot `slot`: `peripheral_key(2, PeripheralPointKey.NAME)` is "peripheral_2_name"."""
    return Key(f"peripheral_{slot}_{point.name}", point.type)


UNITS = frozenset({Unit.CELSIUS, Unit.KELVIN, Unit.PERCENT, Unit.SECONDS, Unit.MINUTES, Unit.RPM,
                   Unit.CUBIC_METERS_PER_HOUR})
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


def _text(key: Key[str], read: InputRegister | HoldingRegister, *, write: HoldingRegister | None = None) -> Point[str]:
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


def _setting(key: Key[float], register: int, *, unit: Unit | None = Unit.CELSIUS) -> Point[float]:
    """A val_d2_fp100 setting the manual gives as R/W."""
    return _fp100(key, HoldingRegister(register), write=HoldingRegister(register), unit=unit)


def _switch(key: Key[bool], register: int) -> Point[bool]:
    """A val_u1 setting the manual gives as 0 and 1, read as off and on."""
    return _flag(key, HoldingRegister(register))


def _number[T](key: Key[T], register: int, *, maximum: int = 254, unit: Unit | None = None) -> Point[T]:
    """A val_u1 setting the manual gives as R/W, a number."""
    return _u8(key, HoldingRegister(register), write=HoldingRegister(register), maximum=maximum, unit=unit)


DHW_TANK_POINTS = _labelled([
    _fp100(DhwTankPointKey.TEMP_CURRENT, InputRegister(6601), poll_rate=PollRate.MEDIUM),
    _fp100(DhwTankPointKey.TEMP_TARGET, InputRegister(6602), poll_rate=PollRate.MEDIUM),
    _u8(DhwTankPointKey.STATE, InputRegister(6603), poll_rate=PollRate.FAST),
    _u8(DhwTankPointKey.BLOCKING_SOURCE, InputRegister(6604), poll_rate=PollRate.FAST),
    _u8(DhwTankPointKey.CIRCULATION_STATE, InputRegister(6605), poll_rate=PollRate.FAST),
    _fp100(DhwTankPointKey.TEMP_CIRCULATION_RETURN, InputRegister(6606), poll_rate=PollRate.MEDIUM),
    _fp100(DhwTankPointKey.TEMP_SOURCE_INLET, InputRegister(6607), poll_rate=PollRate.MEDIUM),
    _fp100(DhwTankPointKey.TEMP_SOURCE_RETURN, InputRegister(6608), poll_rate=PollRate.MEDIUM),
    _text(DhwTankPointKey.NAME, HoldingRegister(6601), write=HoldingRegister(6601)),
    _choice(DhwTankPointKey.MODE, HoldingRegister(6617)),
    _u16(DhwTankPointKey.CIRCULATION_COOLDOWN, HoldingRegister(6618), write=HoldingRegister(6618)),
    _setting(DhwTankPointKey.CIRCULATION_STOP_DIFFERENCE, 6619),
    _setting(DhwTankPointKey.SOURCE_RETURN_TEMP_LIMIT, 6620),
    _setting(DhwTankPointKey.TEMP_SET, 6621),
    _setting(DhwTankPointKey.TEMP_SET_VACATION, 6622),
    _setting(DhwTankPointKey.TEMP_SET_CLEANING, 6623),
    _setting(DhwTankPointKey.TEMP_SET_STANDBY, 6624),
    _number(DhwTankPointKey.EXCLUDE_FROM_VACATION, 6625, maximum=1),
    _number(DhwTankPointKey.EXCLUDE_FROM_STANDBY, 6626, maximum=1),
    *(_alarm(key, DiscreteInput(6600 + bit)) for bit, key in enumerate((
        DhwTankPointKey.WARNING, DhwTankPointKey.ERROR, DhwTankPointKey.CLEANING_FAILED,
        DhwTankPointKey.TANK_SENSOR_FAILURE, DhwTankPointKey.CIRCULATION_RETURN_SENSOR_FAILURE,
        DhwTankPointKey.SOURCE_RETURN_SENSOR_FAILURE, DhwTankPointKey.SOURCE_INLET_SENSOR_FAILURE,
        DhwTankPointKey.SOURCE_INLET_TEMP_TOO_LOW, DhwTankPointKey.LOW_BATTERY, DhwTankPointKey.PERIPHERAL_LOST,
    ), start=1)),
], object=DHW_TANK)

BUFFER_TANK_POINTS = _labelled([
    _u8(BufferTankPointKey.STATE, InputRegister(8301), poll_rate=PollRate.FAST),
    _u8(BufferTankPointKey.BLOCKING_SOURCE, InputRegister(8302), poll_rate=PollRate.FAST),
    _fp100(BufferTankPointKey.TEMP_SOURCE_INLET, InputRegister(8303), poll_rate=PollRate.MEDIUM),
    _fp100(BufferTankPointKey.TEMP_UPPER, InputRegister(8304), poll_rate=PollRate.MEDIUM),
    _fp100(BufferTankPointKey.TEMP_LOWER, InputRegister(8305), poll_rate=PollRate.MEDIUM),
    _text(BufferTankPointKey.NAME, HoldingRegister(8301), write=HoldingRegister(8301)),
    # The manual gives both differences in kelvins.
    _setting(BufferTankPointKey.START_DIFFERENCE, 8317, unit=Unit.KELVIN),
    _setting(BufferTankPointKey.STOP_DIFFERENCE, 8318, unit=Unit.KELVIN),
    _choice(BufferTankPointKey.SENSOR_PRIORITY, HoldingRegister(8319)),
    _switch(BufferTankPointKey.FLOW_BALANCING_ENABLE, 8320),
    _choice(BufferTankPointKey.CHARGE_MODE, HoldingRegister(8321)),
    _number(BufferTankPointKey.CHARGE_EVALUATION_DELAY, 8322, unit=Unit.MINUTES),
    *(_alarm(key, DiscreteInput(8300 + bit)) for bit, key in enumerate((
        BufferTankPointKey.WARNING, BufferTankPointKey.ERROR, BufferTankPointKey.INLET_SENSOR_FAILURE,
        BufferTankPointKey.PRIORITY_SENSOR_FAILURE, BufferTankPointKey.UPPER_SENSOR_FAILURE,
        BufferTankPointKey.LOWER_SENSOR_FAILURE,
    ), start=1)),
], object=BUFFER_TANK)


def itc(n: int) -> list[Point[Any]]:
    """One Sentio ITC's points."""
    base = itc_base(n)

    def key[T](point: PointKey[T]) -> Key[T]:
        return itc_key(n, point)

    return [
        _u8(key(ItcPointKey.STATE), InputRegister(base + 1), poll_rate=PollRate.FAST),
        _u8(key(ItcPointKey.BLOCKING_SOURCE), InputRegister(base + 2), poll_rate=PollRate.FAST),
        _u8(key(ItcPointKey.PUMP_DEMAND), InputRegister(base + 3), poll_rate=PollRate.FAST),
        _u8(key(ItcPointKey.PUMP_STATE), InputRegister(base + 4), poll_rate=PollRate.FAST),
        _fp100(key(ItcPointKey.TEMP_INLET_CURRENT), InputRegister(base + 5), poll_rate=PollRate.MEDIUM),
        _fp100(key(ItcPointKey.TEMP_INLET_TARGET), InputRegister(base + 6), poll_rate=PollRate.MEDIUM),
        _fp100(key(ItcPointKey.TEMP_RETURN_CURRENT), InputRegister(base + 7), poll_rate=PollRate.MEDIUM),
        _fp100(key(ItcPointKey.TEMP_MAIN_SUPPLIER), InputRegister(base + 8), poll_rate=PollRate.MEDIUM),
        _fp100(key(ItcPointKey.SERVO_POSITION_REQUEST), InputRegister(base + 9), poll_rate=PollRate.MEDIUM,
               unit=Unit.PERCENT),
        _fp100(key(ItcPointKey.TEMP_ROOM_TARGET), InputRegister(base + 10), poll_rate=PollRate.MEDIUM),
        _text(key(ItcPointKey.NAME), HoldingRegister(base + 1), write=HoldingRegister(base + 1)),
        _fp10(key(ItcPointKey.REGULATOR_P), HoldingRegister(base + 17), write=HoldingRegister(base + 17)),
        _u16(key(ItcPointKey.REGULATOR_I), HoldingRegister(base + 18), write=HoldingRegister(base + 18)),
        _setting(key(ItcPointKey.REGULATOR_HYSTERESIS), base + 19),
        _choice(key(ItcPointKey.HEAT_CURVE_TYPE), HoldingRegister(base + 20)),
        _fp10(key(ItcPointKey.HEAT_CURVE_SLOPE), HoldingRegister(base + 21), write=HoldingRegister(base + 21)),
        _setting(key(ItcPointKey.HEAT_CURVE_SHIFT), base + 22),
        _setting(key(ItcPointKey.HEAT_CURVE_INLET_MIN), base + 23),
        _setting(key(ItcPointKey.HEAT_CURVE_INLET_MAX), base + 24),
        _fp10(key(ItcPointKey.HEAT_CURVE_GAIN), HoldingRegister(base + 25), write=HoldingRegister(base + 25)),
        _choice(key(ItcPointKey.RETURN_LIMITER_FUNCTION), HoldingRegister(base + 26)),
        _setting(key(ItcPointKey.RETURN_MAX_LIMIT), base + 27),
        _fp10(key(ItcPointKey.RETURN_MAX_GAIN), HoldingRegister(base + 28), write=HoldingRegister(base + 28)),
        _switch(key(ItcPointKey.RETURN_MAX_PRIORITY), base + 29),
        _setting(key(ItcPointKey.RETURN_MIN_LIMIT), base + 30),
        _fp10(key(ItcPointKey.RETURN_MIN_GAIN), HoldingRegister(base + 31), write=HoldingRegister(base + 31)),
        _switch(key(ItcPointKey.BOOST_ENABLE), base + 32),
        _number(key(ItcPointKey.BOOST_FLOW), base + 33),
        _switch(key(ItcPointKey.RAMPING_ENABLE), base + 34),
        _number(key(ItcPointKey.RAMPING_TIME), base + 35),
        _number(key(ItcPointKey.FROST_PROTECTION_MODE), base + 36),
        _setting(key(ItcPointKey.FROST_PROTECTION_TEMP), base + 37),
        _switch(key(ItcPointKey.HIGH_TEMP_CUTOFF_ENABLE), base + 38),
        _setting(key(ItcPointKey.HIGH_TEMP_CUTOFF_TEMP), base + 39),
        _fp10(key(ItcPointKey.COOLING_REGULATOR_P), HoldingRegister(base + 40), write=HoldingRegister(base + 40)),
        _u16(key(ItcPointKey.COOLING_REGULATOR_I), HoldingRegister(base + 41), write=HoldingRegister(base + 41)),
        _setting(key(ItcPointKey.COOLING_REGULATOR_HYSTERESIS), base + 42),
        _setting(key(ItcPointKey.COOLING_INLET_MIN), base + 43),
        _setting(key(ItcPointKey.COOLING_INLET_MAX), base + 44),
        *(_alarm(key(point), DiscreteInput(base + bit)) for bit, point in enumerate((
            ItcPointKey.WARNING, ItcPointKey.ERROR, ItcPointKey.INLET_SENSOR_FAILURE, ItcPointKey.SERVO_FAILURE,
            ItcPointKey.RETURN_SENSOR_FAILURE, ItcPointKey.OUTDOOR_SENSOR_FAILURE,
            ItcPointKey.HIGH_TEMP_CUTOFF_ACTIVE, ItcPointKey.FROST_PROTECTION_ACTIVE,
        ), start=1)),
    ]


def ventilation(n: int) -> list[Point[Any]]:
    """One ventilation unit's points."""
    base = ventilation_base(n)

    def key[T](point: PointKey[T]) -> Key[T]:
        return ventilation_key(n, point)

    def level(point: PointKey[float], offset: int) -> Point[float]:
        return _setting(key(point), base + offset, unit=Unit.PERCENT)

    def flow(point: PointKey[int], offset: int) -> Point[int]:
        return _u16(key(point), HoldingRegister(base + offset), write=HoldingRegister(base + offset),
                    unit=Unit.CUBIC_METERS_PER_HOUR)

    return [
        _text(key(VentilationPointKey.DEVICE_MODEL), InputRegister(base + 1)),
        _u32(key(VentilationPointKey.WARNING_CODE), InputRegister(base + 17), poll_rate=PollRate.MEDIUM),
        _u32(key(VentilationPointKey.ERROR_CODE), InputRegister(base + 19), poll_rate=PollRate.MEDIUM),
        _u32(key(VentilationPointKey.FEATURES), InputRegister(base + 21), poll_rate=PollRate.STATIC),
        _u8(key(VentilationPointKey.STATE), InputRegister(base + 23), poll_rate=PollRate.FAST),
        _u8(key(VentilationPointKey.BLOCKING_SOURCE), InputRegister(base + 24), poll_rate=PollRate.FAST),
        _u16(key(VentilationPointKey.SUPPLY_FAN_SPEED), InputRegister(base + 25), poll_rate=PollRate.MEDIUM,
             unit=Unit.RPM),
        _u16(key(VentilationPointKey.EXHAUST_FAN_SPEED), InputRegister(base + 26), poll_rate=PollRate.MEDIUM,
             unit=Unit.RPM),
        _fp100(key(VentilationPointKey.SUPPLY_FAN_SETPOINT), InputRegister(base + 27), poll_rate=PollRate.MEDIUM,
               unit=Unit.PERCENT),
        _fp100(key(VentilationPointKey.EXHAUST_FAN_SETPOINT), InputRegister(base + 28), poll_rate=PollRate.MEDIUM,
               unit=Unit.PERCENT),
        _u16(key(VentilationPointKey.SUPPLY_FLOW_SETPOINT), InputRegister(base + 29), poll_rate=PollRate.MEDIUM,
             unit=Unit.CUBIC_METERS_PER_HOUR),
        _u16(key(VentilationPointKey.EXHAUST_FLOW_SETPOINT), InputRegister(base + 30), poll_rate=PollRate.MEDIUM,
             unit=Unit.CUBIC_METERS_PER_HOUR),
        _fp100(key(VentilationPointKey.TEMP_INTAKE), InputRegister(base + 31), poll_rate=PollRate.MEDIUM),
        _fp100(key(VentilationPointKey.TEMP_SUPPLY), InputRegister(base + 32), poll_rate=PollRate.MEDIUM),
        _fp100(key(VentilationPointKey.TEMP_EXTRACT), InputRegister(base + 33), poll_rate=PollRate.MEDIUM),
        _fp100(key(VentilationPointKey.TEMP_EXHAUST), InputRegister(base + 34), poll_rate=PollRate.MEDIUM),
        _fp100(key(VentilationPointKey.BYPASS_DAMPER_POSITION), InputRegister(base + 35), poll_rate=PollRate.MEDIUM,
               unit=Unit.PERCENT),
        _u8(key(VentilationPointKey.FREE_COOLING), InputRegister(base + 36), poll_rate=PollRate.MEDIUM),
        _u32(key(VentilationPointKey.AIR_FILTER_LAST_CHANGE), InputRegister(base + 37), unit=Unit.SECONDS),
        _text(key(VentilationPointKey.NAME), HoldingRegister(base + 1), write=HoldingRegister(base + 1)),
        _u32(key(VentilationPointKey.AIR_FILTER_LIFETIME), HoldingRegister(base + 17),
             write=HoldingRegister(base + 17), unit=Unit.MINUTES),
        _u32(key(VentilationPointKey.AIR_FILTER_LIFETIME_USED), HoldingRegister(base + 19),
             write=HoldingRegister(base + 19)),
        level(VentilationPointKey.EXHAUST_LEVEL_UNOCCUPIED, 21),
        level(VentilationPointKey.EXHAUST_LEVEL_ECO, 22),
        level(VentilationPointKey.EXHAUST_LEVEL_COMFORT, 23),
        level(VentilationPointKey.EXHAUST_LEVEL_BOOST, 24),
        level(VentilationPointKey.SUPPLY_LEVEL_UNOCCUPIED, 25),
        level(VentilationPointKey.SUPPLY_LEVEL_ECO, 26),
        level(VentilationPointKey.SUPPLY_LEVEL_COMFORT, 27),
        level(VentilationPointKey.SUPPLY_LEVEL_BOOST, 28),
        flow(VentilationPointKey.EXHAUST_FLOW_UNOCCUPIED, 29),
        flow(VentilationPointKey.EXHAUST_FLOW_ECO, 30),
        flow(VentilationPointKey.EXHAUST_FLOW_COMFORT, 31),
        flow(VentilationPointKey.EXHAUST_FLOW_BOOST, 32),
        flow(VentilationPointKey.SUPPLY_FLOW_UNOCCUPIED, 33),
        flow(VentilationPointKey.SUPPLY_FLOW_ECO, 34),
        flow(VentilationPointKey.SUPPLY_FLOW_COMFORT, 35),
        flow(VentilationPointKey.SUPPLY_FLOW_BOOST, 36),
        _switch(key(VentilationPointKey.ALLOW_STOPPED), base + 37),
        _switch(key(VentilationPointKey.ALLOW_UNOCCUPIED), base + 38),
        _choice(key(VentilationPointKey.STANDBY_LEVEL), HoldingRegister(base + 39)),
        _choice(key(VentilationPointKey.VACATION_LEVEL), HoldingRegister(base + 40)),
        _choice(key(VentilationPointKey.HEAT_EXCHANGE_MODE), HoldingRegister(base + 41)),
        *(_alarm(key(point), DiscreteInput(base + bit)) for bit, point in enumerate((
            VentilationPointKey.WARNING, VentilationPointKey.ERROR, VentilationPointKey.AIR_FILTER_EXPIRED,
            VentilationPointKey.AIR_FILTER_YEAR_PASSED, VentilationPointKey.DEVICE_WARNING,
            VentilationPointKey.DEVICE_FAULT, VentilationPointKey.COMMUNICATION_ERROR,
            VentilationPointKey.NOT_COMPATIBLE, VentilationPointKey.DEVICE_ERROR,
        ), start=1)),
    ]


def dehumidifier(n: int) -> list[Point[Any]]:
    """One dehumidifier's points."""
    base = dehumidifier_base(n)

    def key[T](point: PointKey[T]) -> Key[T]:
        return dehumidifier_key(n, point)

    return [
        _u8(key(DehumidifierPointKey.TYPE), InputRegister(base + 1), poll_rate=PollRate.STATIC),
        _u8(key(DehumidifierPointKey.DRYING_STATE), InputRegister(base + 3), poll_rate=PollRate.FAST),
        _u8(key(DehumidifierPointKey.DRYING_BLOCKING_SOURCE), InputRegister(base + 4), poll_rate=PollRate.FAST),
        _u8(key(DehumidifierPointKey.THERMAL_INTEGRATION_STATE), InputRegister(base + 5), poll_rate=PollRate.FAST),
        _u8(key(DehumidifierPointKey.THERMAL_INTEGRATION_BLOCKING_SOURCE), InputRegister(base + 6),
            poll_rate=PollRate.FAST),
        _u8(key(DehumidifierPointKey.THERMAL_INTEGRATION_DEMAND_CONDITION), InputRegister(base + 7)),
        _u32(key(DehumidifierPointKey.AIR_FILTER_LAST_CHANGE), InputRegister(base + 10), unit=Unit.SECONDS),
        _u8(key(DehumidifierPointKey.HCW_SUPPLIER), InputRegister(base + 12)),
        _text(key(DehumidifierPointKey.NAME), HoldingRegister(base + 1), write=HoldingRegister(base + 1)),
        _u32(key(DehumidifierPointKey.AIR_FILTER_LIFETIME), HoldingRegister(base + 17),
             write=HoldingRegister(base + 17), unit=Unit.MINUTES),
        _u32(key(DehumidifierPointKey.AIR_FILTER_LIFETIME_USED), HoldingRegister(base + 19),
             write=HoldingRegister(base + 19)),
        _choice(key(DehumidifierPointKey.DRYING_ALLOWED_IN), HoldingRegister(base + 21)),
        _setting(key(DehumidifierPointKey.DRYING_COOLING_WATER_TEMP), base + 22),
        _choice(key(DehumidifierPointKey.THERMAL_INTEGRATION_ALLOWED_IN), HoldingRegister(base + 23)),
        _setting(key(DehumidifierPointKey.THERMAL_INTEGRATION_HEATING_WATER_TEMP), base + 24),
        _setting(key(DehumidifierPointKey.THERMAL_INTEGRATION_COOLING_WATER_TEMP), base + 25),
        *(_alarm(key(point), DiscreteInput(base + bit)) for bit, point in enumerate((
            DehumidifierPointKey.WARNING, DehumidifierPointKey.ERROR, DehumidifierPointKey.AIR_FILTER_EXPIRED,
            DehumidifierPointKey.AIR_FILTER_YEAR_PASSED, DehumidifierPointKey.HCW_SUPPLIER_NOT_SET,
            DehumidifierPointKey.DEVICE_FAULT,
        ), start=1)),
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
    DHW_TANK: DhwTankPointKey.TEMP_CURRENT,
    BUFFER_TANK: BufferTankPointKey.STATE,
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


def _scan_instance(label: str, key: Callable[[int], Key[Any]], what: str) -> InstanceScanStep:
    """A scan that removes instance n of `label` when the controller refuses `key(n)`."""
    async def scan_it(scan: Scan, n: int) -> None:
        found = key(n)
        if (await scan.read((found,)))[found].quality is Quality.MISSING:
            scan.set_available(Labels(**{label: n}), False, reason=f"the controller has no such {what}")
    return scan_it


scan_itc = _scan_instance(ITC, lambda n: itc_key(n, ItcPointKey.STATE), "ITC")
scan_ventilation = _scan_instance(VENTILATION, lambda n: ventilation_key(n, VentilationPointKey.STATE),
                                  "ventilation unit")
scan_dehumidifier = _scan_instance(DEHUMIDIFIER, lambda n: dehumidifier_key(n, DehumidifierPointKey.TYPE),
                                   "dehumidifier")


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
        Section(DHW_TANK_POINTS),
        RepeatedSection(itc, range(1, ITC_COUNT + 1), label=ITC, scan=scan_itc),
        Section(BUFFER_TANK_POINTS),
        RepeatedSection(ventilation, range(1, VENTILATION_COUNT + 1), label=VENTILATION, scan=scan_ventilation),
        RepeatedSection(dehumidifier, range(1, DEHUMIDIFIER_COUNT + 1), label=DEHUMIDIFIER,
                        scan=scan_dehumidifier),
    ],
    scan_steps=[check_the_controller, find_the_objects],
)
