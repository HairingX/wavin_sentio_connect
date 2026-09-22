"""Wavin Sentio register map.

Addresses come from the Sentio Modbus manual (see docs/sentio-modbus-reference.md). The
manual's "Modbus Address" is the raw wire address, so the numbers below are used unchanged.

Object bases: Room N = N*100, Peripheral N = 51100 + N*100.

This file is generated; see the generator noted in docs/implementation-status.md.
"""
import logging
from enum import auto
from modbus_event_connect import ( # type: ignore
        ModbusDatapoint,
        ModbusDatapointKey,
        ModbusDeviceBase,
        ModbusDeviceInfo,
        ModbusSetpoint,
        ModbusSetpointKey,
        VersionInfo,
        VersionInfoKeys,
        Read,
        ValueLimit,
        ModbusValueType,
        )

_LOGGER = logging.getLogger(__name__)

ADDRESS_SPACE_MAJOR_REQUIRED = 3
ADDRESS_SPACE_MINOR_REQUIRED = 2
"""Oldest Sentio address space version this register map was written against (FWPKG 12)."""

ROOM_COUNT = 16
"""Rooms the Sentio address space defines (Room N base address = N*100)."""
PERIPHERAL_COUNT = 64
"""Peripheral slots the Sentio address space defines (Peripheral N base = 51100 + N*100)."""

def room_base(room: int) -> int:
    """Base address of a room object. Room 1 -> 100, Room 16 -> 1600."""
    return room * 100

def peripheral_base(peripheral: int) -> int:
    """Base address of a peripheral object. Peripheral 1 -> 51200, Peripheral 64 -> 57500."""
    return 51100 + peripheral * 100


class WavinSentioDatapointKey(ModbusDatapointKey):
    """Read-only values (Modbus input registers)."""
    DATAPOINT_MAJOR = auto()
    """Address space major version. Incremented on incompatible changes."""
    DATAPOINT_MINOR = auto()
    """Address space minor version. Incremented on compatible changes."""
    DEVICE_TYPE = auto()
    """1 = CCU-208, 2 = DHW-201 (Calefa)."""
    HARDWARE_MAJOR = auto()
    """Hardware version."""
    SOFTWARE_MAJOR = auto()
    """Software version, major."""
    SOFTWARE_MINOR = auto()
    """Software version, minor."""
    SERIAL_NUMBER_PREFIX = auto()
    """Device serial number prefix. Always 1530 on a Sentio CCU."""
    SERIAL_NUMBER = auto()
    """Device serial number."""
    HEATING_COOLING_MODE = auto()
    """0 = HEATING, 1 = COOLING."""


    # --- Room 1 (input registers 101-128) ---
    ROOM_1_TEMP_AIR_TARGET = auto()
    """Desired temperature in the room, as currently applied by the controller."""
    ROOM_1_STATE = auto()
    """General heating/cooling state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_1_BLOCKING_SOURCE = auto()
    """Why heating/cooling is blocked. See WavinSentioBlockingSources."""
    ROOM_1_TEMP_AIR_CURRENT = auto()
    """Current air temperature measured in the room."""
    ROOM_1_TEMP_FLOOR_CURRENT = auto()
    """Current floor temperature measured in the room."""
    ROOM_1_HUMIDITY_CURRENT = auto()
    """Current relative humidity measured in the room."""
    ROOM_1_DEW_POINT_CURRENT = auto()
    """Current calculated dew point in the room."""
    ROOM_1_ASSOCIATED_RADIATORS = auto()
    """Modbus object address of the associated radiator source. 0 = NONE."""
    ROOM_1_ASSOCIATED_UFHC = auto()
    """Modbus object address of the associated underfloor heating/cooling source. 0 = NONE."""
    ROOM_1_ASSOCIATED_DRYING = auto()
    """Modbus object address of the associated dehumidifier. 0 = NONE."""
    ROOM_1_ASSOCIATED_THERMAL_INTEGRATION = auto()
    """Modbus object address of the associated thermal integration device. 0 = NONE."""
    ROOM_1_ASSOCIATED_VENTILATION = auto()
    """Modbus object address of the associated ventilation device. 0 = NONE."""
    ROOM_1_AIR_STATE = auto()
    """Radiator (air temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_1_FLOOR_STATE = auto()
    """Underfloor heating/cooling (floor temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_1_DRYING_STATE = auto()
    """Drying (relative humidity) state.

    0 = NONE, 1 = IDLE, 2 = DRYING, 3 = BLOCKED_DRYING"""
    ROOM_1_THERMAL_INTEGRATION_STATE = auto()
    """Thermal integration state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_1_VENTILATION_STATE = auto()
    """Ventilation state.

    0 = NONE, 1 = STOPPED, 2 = UNOCCUPIED, 3 = ECONOMY, 4 = COMFORT, 5 = BOOST"""
    ROOM_1_BLOCKING_SOURCE_RADIATORS = auto()
    """Blocking source for radiators. See WavinSentioBlockingSources."""
    ROOM_1_BLOCKING_SOURCE_UFHC = auto()
    """Blocking source for underfloor heating/cooling. See WavinSentioBlockingSources."""
    ROOM_1_BLOCKING_SOURCE_DRYING = auto()
    """Blocking source for drying. See WavinSentioBlockingSources."""
    ROOM_1_BLOCKING_SOURCE_THERMAL_INTEGRATION = auto()
    """Blocking source for thermal integration. See WavinSentioBlockingSources."""
    ROOM_1_BLOCKING_SOURCE_VENTILATION = auto()
    """Blocking source for ventilation. See WavinSentioBlockingSources."""
    ROOM_1_TYPE = auto()
    """Room type.

    0 = NORMAL (default), 1 = DUMMY (no thermostat or sensor installed)"""
    ROOM_1_ASSOCIATED_HEATING_SOURCE = auto()
    """Dummy rooms only. Modbus object address of the heating source. 0 = NONE."""

    # --- Room 2 (input registers 201-228) ---
    ROOM_2_TEMP_AIR_TARGET = auto()
    """Desired temperature in the room, as currently applied by the controller."""
    ROOM_2_STATE = auto()
    """General heating/cooling state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_2_BLOCKING_SOURCE = auto()
    """Why heating/cooling is blocked. See WavinSentioBlockingSources."""
    ROOM_2_TEMP_AIR_CURRENT = auto()
    """Current air temperature measured in the room."""
    ROOM_2_TEMP_FLOOR_CURRENT = auto()
    """Current floor temperature measured in the room."""
    ROOM_2_HUMIDITY_CURRENT = auto()
    """Current relative humidity measured in the room."""
    ROOM_2_DEW_POINT_CURRENT = auto()
    """Current calculated dew point in the room."""
    ROOM_2_ASSOCIATED_RADIATORS = auto()
    """Modbus object address of the associated radiator source. 0 = NONE."""
    ROOM_2_ASSOCIATED_UFHC = auto()
    """Modbus object address of the associated underfloor heating/cooling source. 0 = NONE."""
    ROOM_2_ASSOCIATED_DRYING = auto()
    """Modbus object address of the associated dehumidifier. 0 = NONE."""
    ROOM_2_ASSOCIATED_THERMAL_INTEGRATION = auto()
    """Modbus object address of the associated thermal integration device. 0 = NONE."""
    ROOM_2_ASSOCIATED_VENTILATION = auto()
    """Modbus object address of the associated ventilation device. 0 = NONE."""
    ROOM_2_AIR_STATE = auto()
    """Radiator (air temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_2_FLOOR_STATE = auto()
    """Underfloor heating/cooling (floor temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_2_DRYING_STATE = auto()
    """Drying (relative humidity) state.

    0 = NONE, 1 = IDLE, 2 = DRYING, 3 = BLOCKED_DRYING"""
    ROOM_2_THERMAL_INTEGRATION_STATE = auto()
    """Thermal integration state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_2_VENTILATION_STATE = auto()
    """Ventilation state.

    0 = NONE, 1 = STOPPED, 2 = UNOCCUPIED, 3 = ECONOMY, 4 = COMFORT, 5 = BOOST"""
    ROOM_2_BLOCKING_SOURCE_RADIATORS = auto()
    """Blocking source for radiators. See WavinSentioBlockingSources."""
    ROOM_2_BLOCKING_SOURCE_UFHC = auto()
    """Blocking source for underfloor heating/cooling. See WavinSentioBlockingSources."""
    ROOM_2_BLOCKING_SOURCE_DRYING = auto()
    """Blocking source for drying. See WavinSentioBlockingSources."""
    ROOM_2_BLOCKING_SOURCE_THERMAL_INTEGRATION = auto()
    """Blocking source for thermal integration. See WavinSentioBlockingSources."""
    ROOM_2_BLOCKING_SOURCE_VENTILATION = auto()
    """Blocking source for ventilation. See WavinSentioBlockingSources."""
    ROOM_2_TYPE = auto()
    """Room type.

    0 = NORMAL (default), 1 = DUMMY (no thermostat or sensor installed)"""
    ROOM_2_ASSOCIATED_HEATING_SOURCE = auto()
    """Dummy rooms only. Modbus object address of the heating source. 0 = NONE."""

    # --- Room 3 (input registers 301-328) ---
    ROOM_3_TEMP_AIR_TARGET = auto()
    """Desired temperature in the room, as currently applied by the controller."""
    ROOM_3_STATE = auto()
    """General heating/cooling state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_3_BLOCKING_SOURCE = auto()
    """Why heating/cooling is blocked. See WavinSentioBlockingSources."""
    ROOM_3_TEMP_AIR_CURRENT = auto()
    """Current air temperature measured in the room."""
    ROOM_3_TEMP_FLOOR_CURRENT = auto()
    """Current floor temperature measured in the room."""
    ROOM_3_HUMIDITY_CURRENT = auto()
    """Current relative humidity measured in the room."""
    ROOM_3_DEW_POINT_CURRENT = auto()
    """Current calculated dew point in the room."""
    ROOM_3_ASSOCIATED_RADIATORS = auto()
    """Modbus object address of the associated radiator source. 0 = NONE."""
    ROOM_3_ASSOCIATED_UFHC = auto()
    """Modbus object address of the associated underfloor heating/cooling source. 0 = NONE."""
    ROOM_3_ASSOCIATED_DRYING = auto()
    """Modbus object address of the associated dehumidifier. 0 = NONE."""
    ROOM_3_ASSOCIATED_THERMAL_INTEGRATION = auto()
    """Modbus object address of the associated thermal integration device. 0 = NONE."""
    ROOM_3_ASSOCIATED_VENTILATION = auto()
    """Modbus object address of the associated ventilation device. 0 = NONE."""
    ROOM_3_AIR_STATE = auto()
    """Radiator (air temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_3_FLOOR_STATE = auto()
    """Underfloor heating/cooling (floor temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_3_DRYING_STATE = auto()
    """Drying (relative humidity) state.

    0 = NONE, 1 = IDLE, 2 = DRYING, 3 = BLOCKED_DRYING"""
    ROOM_3_THERMAL_INTEGRATION_STATE = auto()
    """Thermal integration state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_3_VENTILATION_STATE = auto()
    """Ventilation state.

    0 = NONE, 1 = STOPPED, 2 = UNOCCUPIED, 3 = ECONOMY, 4 = COMFORT, 5 = BOOST"""
    ROOM_3_BLOCKING_SOURCE_RADIATORS = auto()
    """Blocking source for radiators. See WavinSentioBlockingSources."""
    ROOM_3_BLOCKING_SOURCE_UFHC = auto()
    """Blocking source for underfloor heating/cooling. See WavinSentioBlockingSources."""
    ROOM_3_BLOCKING_SOURCE_DRYING = auto()
    """Blocking source for drying. See WavinSentioBlockingSources."""
    ROOM_3_BLOCKING_SOURCE_THERMAL_INTEGRATION = auto()
    """Blocking source for thermal integration. See WavinSentioBlockingSources."""
    ROOM_3_BLOCKING_SOURCE_VENTILATION = auto()
    """Blocking source for ventilation. See WavinSentioBlockingSources."""
    ROOM_3_TYPE = auto()
    """Room type.

    0 = NORMAL (default), 1 = DUMMY (no thermostat or sensor installed)"""
    ROOM_3_ASSOCIATED_HEATING_SOURCE = auto()
    """Dummy rooms only. Modbus object address of the heating source. 0 = NONE."""

    # --- Room 4 (input registers 401-428) ---
    ROOM_4_TEMP_AIR_TARGET = auto()
    """Desired temperature in the room, as currently applied by the controller."""
    ROOM_4_STATE = auto()
    """General heating/cooling state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_4_BLOCKING_SOURCE = auto()
    """Why heating/cooling is blocked. See WavinSentioBlockingSources."""
    ROOM_4_TEMP_AIR_CURRENT = auto()
    """Current air temperature measured in the room."""
    ROOM_4_TEMP_FLOOR_CURRENT = auto()
    """Current floor temperature measured in the room."""
    ROOM_4_HUMIDITY_CURRENT = auto()
    """Current relative humidity measured in the room."""
    ROOM_4_DEW_POINT_CURRENT = auto()
    """Current calculated dew point in the room."""
    ROOM_4_ASSOCIATED_RADIATORS = auto()
    """Modbus object address of the associated radiator source. 0 = NONE."""
    ROOM_4_ASSOCIATED_UFHC = auto()
    """Modbus object address of the associated underfloor heating/cooling source. 0 = NONE."""
    ROOM_4_ASSOCIATED_DRYING = auto()
    """Modbus object address of the associated dehumidifier. 0 = NONE."""
    ROOM_4_ASSOCIATED_THERMAL_INTEGRATION = auto()
    """Modbus object address of the associated thermal integration device. 0 = NONE."""
    ROOM_4_ASSOCIATED_VENTILATION = auto()
    """Modbus object address of the associated ventilation device. 0 = NONE."""
    ROOM_4_AIR_STATE = auto()
    """Radiator (air temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_4_FLOOR_STATE = auto()
    """Underfloor heating/cooling (floor temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_4_DRYING_STATE = auto()
    """Drying (relative humidity) state.

    0 = NONE, 1 = IDLE, 2 = DRYING, 3 = BLOCKED_DRYING"""
    ROOM_4_THERMAL_INTEGRATION_STATE = auto()
    """Thermal integration state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_4_VENTILATION_STATE = auto()
    """Ventilation state.

    0 = NONE, 1 = STOPPED, 2 = UNOCCUPIED, 3 = ECONOMY, 4 = COMFORT, 5 = BOOST"""
    ROOM_4_BLOCKING_SOURCE_RADIATORS = auto()
    """Blocking source for radiators. See WavinSentioBlockingSources."""
    ROOM_4_BLOCKING_SOURCE_UFHC = auto()
    """Blocking source for underfloor heating/cooling. See WavinSentioBlockingSources."""
    ROOM_4_BLOCKING_SOURCE_DRYING = auto()
    """Blocking source for drying. See WavinSentioBlockingSources."""
    ROOM_4_BLOCKING_SOURCE_THERMAL_INTEGRATION = auto()
    """Blocking source for thermal integration. See WavinSentioBlockingSources."""
    ROOM_4_BLOCKING_SOURCE_VENTILATION = auto()
    """Blocking source for ventilation. See WavinSentioBlockingSources."""
    ROOM_4_TYPE = auto()
    """Room type.

    0 = NORMAL (default), 1 = DUMMY (no thermostat or sensor installed)"""
    ROOM_4_ASSOCIATED_HEATING_SOURCE = auto()
    """Dummy rooms only. Modbus object address of the heating source. 0 = NONE."""

    # --- Room 5 (input registers 501-528) ---
    ROOM_5_TEMP_AIR_TARGET = auto()
    """Desired temperature in the room, as currently applied by the controller."""
    ROOM_5_STATE = auto()
    """General heating/cooling state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_5_BLOCKING_SOURCE = auto()
    """Why heating/cooling is blocked. See WavinSentioBlockingSources."""
    ROOM_5_TEMP_AIR_CURRENT = auto()
    """Current air temperature measured in the room."""
    ROOM_5_TEMP_FLOOR_CURRENT = auto()
    """Current floor temperature measured in the room."""
    ROOM_5_HUMIDITY_CURRENT = auto()
    """Current relative humidity measured in the room."""
    ROOM_5_DEW_POINT_CURRENT = auto()
    """Current calculated dew point in the room."""
    ROOM_5_ASSOCIATED_RADIATORS = auto()
    """Modbus object address of the associated radiator source. 0 = NONE."""
    ROOM_5_ASSOCIATED_UFHC = auto()
    """Modbus object address of the associated underfloor heating/cooling source. 0 = NONE."""
    ROOM_5_ASSOCIATED_DRYING = auto()
    """Modbus object address of the associated dehumidifier. 0 = NONE."""
    ROOM_5_ASSOCIATED_THERMAL_INTEGRATION = auto()
    """Modbus object address of the associated thermal integration device. 0 = NONE."""
    ROOM_5_ASSOCIATED_VENTILATION = auto()
    """Modbus object address of the associated ventilation device. 0 = NONE."""
    ROOM_5_AIR_STATE = auto()
    """Radiator (air temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_5_FLOOR_STATE = auto()
    """Underfloor heating/cooling (floor temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_5_DRYING_STATE = auto()
    """Drying (relative humidity) state.

    0 = NONE, 1 = IDLE, 2 = DRYING, 3 = BLOCKED_DRYING"""
    ROOM_5_THERMAL_INTEGRATION_STATE = auto()
    """Thermal integration state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_5_VENTILATION_STATE = auto()
    """Ventilation state.

    0 = NONE, 1 = STOPPED, 2 = UNOCCUPIED, 3 = ECONOMY, 4 = COMFORT, 5 = BOOST"""
    ROOM_5_BLOCKING_SOURCE_RADIATORS = auto()
    """Blocking source for radiators. See WavinSentioBlockingSources."""
    ROOM_5_BLOCKING_SOURCE_UFHC = auto()
    """Blocking source for underfloor heating/cooling. See WavinSentioBlockingSources."""
    ROOM_5_BLOCKING_SOURCE_DRYING = auto()
    """Blocking source for drying. See WavinSentioBlockingSources."""
    ROOM_5_BLOCKING_SOURCE_THERMAL_INTEGRATION = auto()
    """Blocking source for thermal integration. See WavinSentioBlockingSources."""
    ROOM_5_BLOCKING_SOURCE_VENTILATION = auto()
    """Blocking source for ventilation. See WavinSentioBlockingSources."""
    ROOM_5_TYPE = auto()
    """Room type.

    0 = NORMAL (default), 1 = DUMMY (no thermostat or sensor installed)"""
    ROOM_5_ASSOCIATED_HEATING_SOURCE = auto()
    """Dummy rooms only. Modbus object address of the heating source. 0 = NONE."""

    # --- Room 6 (input registers 601-628) ---
    ROOM_6_TEMP_AIR_TARGET = auto()
    """Desired temperature in the room, as currently applied by the controller."""
    ROOM_6_STATE = auto()
    """General heating/cooling state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_6_BLOCKING_SOURCE = auto()
    """Why heating/cooling is blocked. See WavinSentioBlockingSources."""
    ROOM_6_TEMP_AIR_CURRENT = auto()
    """Current air temperature measured in the room."""
    ROOM_6_TEMP_FLOOR_CURRENT = auto()
    """Current floor temperature measured in the room."""
    ROOM_6_HUMIDITY_CURRENT = auto()
    """Current relative humidity measured in the room."""
    ROOM_6_DEW_POINT_CURRENT = auto()
    """Current calculated dew point in the room."""
    ROOM_6_ASSOCIATED_RADIATORS = auto()
    """Modbus object address of the associated radiator source. 0 = NONE."""
    ROOM_6_ASSOCIATED_UFHC = auto()
    """Modbus object address of the associated underfloor heating/cooling source. 0 = NONE."""
    ROOM_6_ASSOCIATED_DRYING = auto()
    """Modbus object address of the associated dehumidifier. 0 = NONE."""
    ROOM_6_ASSOCIATED_THERMAL_INTEGRATION = auto()
    """Modbus object address of the associated thermal integration device. 0 = NONE."""
    ROOM_6_ASSOCIATED_VENTILATION = auto()
    """Modbus object address of the associated ventilation device. 0 = NONE."""
    ROOM_6_AIR_STATE = auto()
    """Radiator (air temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_6_FLOOR_STATE = auto()
    """Underfloor heating/cooling (floor temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_6_DRYING_STATE = auto()
    """Drying (relative humidity) state.

    0 = NONE, 1 = IDLE, 2 = DRYING, 3 = BLOCKED_DRYING"""
    ROOM_6_THERMAL_INTEGRATION_STATE = auto()
    """Thermal integration state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_6_VENTILATION_STATE = auto()
    """Ventilation state.

    0 = NONE, 1 = STOPPED, 2 = UNOCCUPIED, 3 = ECONOMY, 4 = COMFORT, 5 = BOOST"""
    ROOM_6_BLOCKING_SOURCE_RADIATORS = auto()
    """Blocking source for radiators. See WavinSentioBlockingSources."""
    ROOM_6_BLOCKING_SOURCE_UFHC = auto()
    """Blocking source for underfloor heating/cooling. See WavinSentioBlockingSources."""
    ROOM_6_BLOCKING_SOURCE_DRYING = auto()
    """Blocking source for drying. See WavinSentioBlockingSources."""
    ROOM_6_BLOCKING_SOURCE_THERMAL_INTEGRATION = auto()
    """Blocking source for thermal integration. See WavinSentioBlockingSources."""
    ROOM_6_BLOCKING_SOURCE_VENTILATION = auto()
    """Blocking source for ventilation. See WavinSentioBlockingSources."""
    ROOM_6_TYPE = auto()
    """Room type.

    0 = NORMAL (default), 1 = DUMMY (no thermostat or sensor installed)"""
    ROOM_6_ASSOCIATED_HEATING_SOURCE = auto()
    """Dummy rooms only. Modbus object address of the heating source. 0 = NONE."""

    # --- Room 7 (input registers 701-728) ---
    ROOM_7_TEMP_AIR_TARGET = auto()
    """Desired temperature in the room, as currently applied by the controller."""
    ROOM_7_STATE = auto()
    """General heating/cooling state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_7_BLOCKING_SOURCE = auto()
    """Why heating/cooling is blocked. See WavinSentioBlockingSources."""
    ROOM_7_TEMP_AIR_CURRENT = auto()
    """Current air temperature measured in the room."""
    ROOM_7_TEMP_FLOOR_CURRENT = auto()
    """Current floor temperature measured in the room."""
    ROOM_7_HUMIDITY_CURRENT = auto()
    """Current relative humidity measured in the room."""
    ROOM_7_DEW_POINT_CURRENT = auto()
    """Current calculated dew point in the room."""
    ROOM_7_ASSOCIATED_RADIATORS = auto()
    """Modbus object address of the associated radiator source. 0 = NONE."""
    ROOM_7_ASSOCIATED_UFHC = auto()
    """Modbus object address of the associated underfloor heating/cooling source. 0 = NONE."""
    ROOM_7_ASSOCIATED_DRYING = auto()
    """Modbus object address of the associated dehumidifier. 0 = NONE."""
    ROOM_7_ASSOCIATED_THERMAL_INTEGRATION = auto()
    """Modbus object address of the associated thermal integration device. 0 = NONE."""
    ROOM_7_ASSOCIATED_VENTILATION = auto()
    """Modbus object address of the associated ventilation device. 0 = NONE."""
    ROOM_7_AIR_STATE = auto()
    """Radiator (air temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_7_FLOOR_STATE = auto()
    """Underfloor heating/cooling (floor temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_7_DRYING_STATE = auto()
    """Drying (relative humidity) state.

    0 = NONE, 1 = IDLE, 2 = DRYING, 3 = BLOCKED_DRYING"""
    ROOM_7_THERMAL_INTEGRATION_STATE = auto()
    """Thermal integration state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_7_VENTILATION_STATE = auto()
    """Ventilation state.

    0 = NONE, 1 = STOPPED, 2 = UNOCCUPIED, 3 = ECONOMY, 4 = COMFORT, 5 = BOOST"""
    ROOM_7_BLOCKING_SOURCE_RADIATORS = auto()
    """Blocking source for radiators. See WavinSentioBlockingSources."""
    ROOM_7_BLOCKING_SOURCE_UFHC = auto()
    """Blocking source for underfloor heating/cooling. See WavinSentioBlockingSources."""
    ROOM_7_BLOCKING_SOURCE_DRYING = auto()
    """Blocking source for drying. See WavinSentioBlockingSources."""
    ROOM_7_BLOCKING_SOURCE_THERMAL_INTEGRATION = auto()
    """Blocking source for thermal integration. See WavinSentioBlockingSources."""
    ROOM_7_BLOCKING_SOURCE_VENTILATION = auto()
    """Blocking source for ventilation. See WavinSentioBlockingSources."""
    ROOM_7_TYPE = auto()
    """Room type.

    0 = NORMAL (default), 1 = DUMMY (no thermostat or sensor installed)"""
    ROOM_7_ASSOCIATED_HEATING_SOURCE = auto()
    """Dummy rooms only. Modbus object address of the heating source. 0 = NONE."""

    # --- Room 8 (input registers 801-828) ---
    ROOM_8_TEMP_AIR_TARGET = auto()
    """Desired temperature in the room, as currently applied by the controller."""
    ROOM_8_STATE = auto()
    """General heating/cooling state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_8_BLOCKING_SOURCE = auto()
    """Why heating/cooling is blocked. See WavinSentioBlockingSources."""
    ROOM_8_TEMP_AIR_CURRENT = auto()
    """Current air temperature measured in the room."""
    ROOM_8_TEMP_FLOOR_CURRENT = auto()
    """Current floor temperature measured in the room."""
    ROOM_8_HUMIDITY_CURRENT = auto()
    """Current relative humidity measured in the room."""
    ROOM_8_DEW_POINT_CURRENT = auto()
    """Current calculated dew point in the room."""
    ROOM_8_ASSOCIATED_RADIATORS = auto()
    """Modbus object address of the associated radiator source. 0 = NONE."""
    ROOM_8_ASSOCIATED_UFHC = auto()
    """Modbus object address of the associated underfloor heating/cooling source. 0 = NONE."""
    ROOM_8_ASSOCIATED_DRYING = auto()
    """Modbus object address of the associated dehumidifier. 0 = NONE."""
    ROOM_8_ASSOCIATED_THERMAL_INTEGRATION = auto()
    """Modbus object address of the associated thermal integration device. 0 = NONE."""
    ROOM_8_ASSOCIATED_VENTILATION = auto()
    """Modbus object address of the associated ventilation device. 0 = NONE."""
    ROOM_8_AIR_STATE = auto()
    """Radiator (air temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_8_FLOOR_STATE = auto()
    """Underfloor heating/cooling (floor temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_8_DRYING_STATE = auto()
    """Drying (relative humidity) state.

    0 = NONE, 1 = IDLE, 2 = DRYING, 3 = BLOCKED_DRYING"""
    ROOM_8_THERMAL_INTEGRATION_STATE = auto()
    """Thermal integration state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_8_VENTILATION_STATE = auto()
    """Ventilation state.

    0 = NONE, 1 = STOPPED, 2 = UNOCCUPIED, 3 = ECONOMY, 4 = COMFORT, 5 = BOOST"""
    ROOM_8_BLOCKING_SOURCE_RADIATORS = auto()
    """Blocking source for radiators. See WavinSentioBlockingSources."""
    ROOM_8_BLOCKING_SOURCE_UFHC = auto()
    """Blocking source for underfloor heating/cooling. See WavinSentioBlockingSources."""
    ROOM_8_BLOCKING_SOURCE_DRYING = auto()
    """Blocking source for drying. See WavinSentioBlockingSources."""
    ROOM_8_BLOCKING_SOURCE_THERMAL_INTEGRATION = auto()
    """Blocking source for thermal integration. See WavinSentioBlockingSources."""
    ROOM_8_BLOCKING_SOURCE_VENTILATION = auto()
    """Blocking source for ventilation. See WavinSentioBlockingSources."""
    ROOM_8_TYPE = auto()
    """Room type.

    0 = NORMAL (default), 1 = DUMMY (no thermostat or sensor installed)"""
    ROOM_8_ASSOCIATED_HEATING_SOURCE = auto()
    """Dummy rooms only. Modbus object address of the heating source. 0 = NONE."""

    # --- Room 9 (input registers 901-928) ---
    ROOM_9_TEMP_AIR_TARGET = auto()
    """Desired temperature in the room, as currently applied by the controller."""
    ROOM_9_STATE = auto()
    """General heating/cooling state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_9_BLOCKING_SOURCE = auto()
    """Why heating/cooling is blocked. See WavinSentioBlockingSources."""
    ROOM_9_TEMP_AIR_CURRENT = auto()
    """Current air temperature measured in the room."""
    ROOM_9_TEMP_FLOOR_CURRENT = auto()
    """Current floor temperature measured in the room."""
    ROOM_9_HUMIDITY_CURRENT = auto()
    """Current relative humidity measured in the room."""
    ROOM_9_DEW_POINT_CURRENT = auto()
    """Current calculated dew point in the room."""
    ROOM_9_ASSOCIATED_RADIATORS = auto()
    """Modbus object address of the associated radiator source. 0 = NONE."""
    ROOM_9_ASSOCIATED_UFHC = auto()
    """Modbus object address of the associated underfloor heating/cooling source. 0 = NONE."""
    ROOM_9_ASSOCIATED_DRYING = auto()
    """Modbus object address of the associated dehumidifier. 0 = NONE."""
    ROOM_9_ASSOCIATED_THERMAL_INTEGRATION = auto()
    """Modbus object address of the associated thermal integration device. 0 = NONE."""
    ROOM_9_ASSOCIATED_VENTILATION = auto()
    """Modbus object address of the associated ventilation device. 0 = NONE."""
    ROOM_9_AIR_STATE = auto()
    """Radiator (air temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_9_FLOOR_STATE = auto()
    """Underfloor heating/cooling (floor temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_9_DRYING_STATE = auto()
    """Drying (relative humidity) state.

    0 = NONE, 1 = IDLE, 2 = DRYING, 3 = BLOCKED_DRYING"""
    ROOM_9_THERMAL_INTEGRATION_STATE = auto()
    """Thermal integration state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_9_VENTILATION_STATE = auto()
    """Ventilation state.

    0 = NONE, 1 = STOPPED, 2 = UNOCCUPIED, 3 = ECONOMY, 4 = COMFORT, 5 = BOOST"""
    ROOM_9_BLOCKING_SOURCE_RADIATORS = auto()
    """Blocking source for radiators. See WavinSentioBlockingSources."""
    ROOM_9_BLOCKING_SOURCE_UFHC = auto()
    """Blocking source for underfloor heating/cooling. See WavinSentioBlockingSources."""
    ROOM_9_BLOCKING_SOURCE_DRYING = auto()
    """Blocking source for drying. See WavinSentioBlockingSources."""
    ROOM_9_BLOCKING_SOURCE_THERMAL_INTEGRATION = auto()
    """Blocking source for thermal integration. See WavinSentioBlockingSources."""
    ROOM_9_BLOCKING_SOURCE_VENTILATION = auto()
    """Blocking source for ventilation. See WavinSentioBlockingSources."""
    ROOM_9_TYPE = auto()
    """Room type.

    0 = NORMAL (default), 1 = DUMMY (no thermostat or sensor installed)"""
    ROOM_9_ASSOCIATED_HEATING_SOURCE = auto()
    """Dummy rooms only. Modbus object address of the heating source. 0 = NONE."""

    # --- Room 10 (input registers 1001-1028) ---
    ROOM_10_TEMP_AIR_TARGET = auto()
    """Desired temperature in the room, as currently applied by the controller."""
    ROOM_10_STATE = auto()
    """General heating/cooling state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_10_BLOCKING_SOURCE = auto()
    """Why heating/cooling is blocked. See WavinSentioBlockingSources."""
    ROOM_10_TEMP_AIR_CURRENT = auto()
    """Current air temperature measured in the room."""
    ROOM_10_TEMP_FLOOR_CURRENT = auto()
    """Current floor temperature measured in the room."""
    ROOM_10_HUMIDITY_CURRENT = auto()
    """Current relative humidity measured in the room."""
    ROOM_10_DEW_POINT_CURRENT = auto()
    """Current calculated dew point in the room."""
    ROOM_10_ASSOCIATED_RADIATORS = auto()
    """Modbus object address of the associated radiator source. 0 = NONE."""
    ROOM_10_ASSOCIATED_UFHC = auto()
    """Modbus object address of the associated underfloor heating/cooling source. 0 = NONE."""
    ROOM_10_ASSOCIATED_DRYING = auto()
    """Modbus object address of the associated dehumidifier. 0 = NONE."""
    ROOM_10_ASSOCIATED_THERMAL_INTEGRATION = auto()
    """Modbus object address of the associated thermal integration device. 0 = NONE."""
    ROOM_10_ASSOCIATED_VENTILATION = auto()
    """Modbus object address of the associated ventilation device. 0 = NONE."""
    ROOM_10_AIR_STATE = auto()
    """Radiator (air temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_10_FLOOR_STATE = auto()
    """Underfloor heating/cooling (floor temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_10_DRYING_STATE = auto()
    """Drying (relative humidity) state.

    0 = NONE, 1 = IDLE, 2 = DRYING, 3 = BLOCKED_DRYING"""
    ROOM_10_THERMAL_INTEGRATION_STATE = auto()
    """Thermal integration state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_10_VENTILATION_STATE = auto()
    """Ventilation state.

    0 = NONE, 1 = STOPPED, 2 = UNOCCUPIED, 3 = ECONOMY, 4 = COMFORT, 5 = BOOST"""
    ROOM_10_BLOCKING_SOURCE_RADIATORS = auto()
    """Blocking source for radiators. See WavinSentioBlockingSources."""
    ROOM_10_BLOCKING_SOURCE_UFHC = auto()
    """Blocking source for underfloor heating/cooling. See WavinSentioBlockingSources."""
    ROOM_10_BLOCKING_SOURCE_DRYING = auto()
    """Blocking source for drying. See WavinSentioBlockingSources."""
    ROOM_10_BLOCKING_SOURCE_THERMAL_INTEGRATION = auto()
    """Blocking source for thermal integration. See WavinSentioBlockingSources."""
    ROOM_10_BLOCKING_SOURCE_VENTILATION = auto()
    """Blocking source for ventilation. See WavinSentioBlockingSources."""
    ROOM_10_TYPE = auto()
    """Room type.

    0 = NORMAL (default), 1 = DUMMY (no thermostat or sensor installed)"""
    ROOM_10_ASSOCIATED_HEATING_SOURCE = auto()
    """Dummy rooms only. Modbus object address of the heating source. 0 = NONE."""

    # --- Room 11 (input registers 1101-1128) ---
    ROOM_11_TEMP_AIR_TARGET = auto()
    """Desired temperature in the room, as currently applied by the controller."""
    ROOM_11_STATE = auto()
    """General heating/cooling state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_11_BLOCKING_SOURCE = auto()
    """Why heating/cooling is blocked. See WavinSentioBlockingSources."""
    ROOM_11_TEMP_AIR_CURRENT = auto()
    """Current air temperature measured in the room."""
    ROOM_11_TEMP_FLOOR_CURRENT = auto()
    """Current floor temperature measured in the room."""
    ROOM_11_HUMIDITY_CURRENT = auto()
    """Current relative humidity measured in the room."""
    ROOM_11_DEW_POINT_CURRENT = auto()
    """Current calculated dew point in the room."""
    ROOM_11_ASSOCIATED_RADIATORS = auto()
    """Modbus object address of the associated radiator source. 0 = NONE."""
    ROOM_11_ASSOCIATED_UFHC = auto()
    """Modbus object address of the associated underfloor heating/cooling source. 0 = NONE."""
    ROOM_11_ASSOCIATED_DRYING = auto()
    """Modbus object address of the associated dehumidifier. 0 = NONE."""
    ROOM_11_ASSOCIATED_THERMAL_INTEGRATION = auto()
    """Modbus object address of the associated thermal integration device. 0 = NONE."""
    ROOM_11_ASSOCIATED_VENTILATION = auto()
    """Modbus object address of the associated ventilation device. 0 = NONE."""
    ROOM_11_AIR_STATE = auto()
    """Radiator (air temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_11_FLOOR_STATE = auto()
    """Underfloor heating/cooling (floor temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_11_DRYING_STATE = auto()
    """Drying (relative humidity) state.

    0 = NONE, 1 = IDLE, 2 = DRYING, 3 = BLOCKED_DRYING"""
    ROOM_11_THERMAL_INTEGRATION_STATE = auto()
    """Thermal integration state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_11_VENTILATION_STATE = auto()
    """Ventilation state.

    0 = NONE, 1 = STOPPED, 2 = UNOCCUPIED, 3 = ECONOMY, 4 = COMFORT, 5 = BOOST"""
    ROOM_11_BLOCKING_SOURCE_RADIATORS = auto()
    """Blocking source for radiators. See WavinSentioBlockingSources."""
    ROOM_11_BLOCKING_SOURCE_UFHC = auto()
    """Blocking source for underfloor heating/cooling. See WavinSentioBlockingSources."""
    ROOM_11_BLOCKING_SOURCE_DRYING = auto()
    """Blocking source for drying. See WavinSentioBlockingSources."""
    ROOM_11_BLOCKING_SOURCE_THERMAL_INTEGRATION = auto()
    """Blocking source for thermal integration. See WavinSentioBlockingSources."""
    ROOM_11_BLOCKING_SOURCE_VENTILATION = auto()
    """Blocking source for ventilation. See WavinSentioBlockingSources."""
    ROOM_11_TYPE = auto()
    """Room type.

    0 = NORMAL (default), 1 = DUMMY (no thermostat or sensor installed)"""
    ROOM_11_ASSOCIATED_HEATING_SOURCE = auto()
    """Dummy rooms only. Modbus object address of the heating source. 0 = NONE."""

    # --- Room 12 (input registers 1201-1228) ---
    ROOM_12_TEMP_AIR_TARGET = auto()
    """Desired temperature in the room, as currently applied by the controller."""
    ROOM_12_STATE = auto()
    """General heating/cooling state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_12_BLOCKING_SOURCE = auto()
    """Why heating/cooling is blocked. See WavinSentioBlockingSources."""
    ROOM_12_TEMP_AIR_CURRENT = auto()
    """Current air temperature measured in the room."""
    ROOM_12_TEMP_FLOOR_CURRENT = auto()
    """Current floor temperature measured in the room."""
    ROOM_12_HUMIDITY_CURRENT = auto()
    """Current relative humidity measured in the room."""
    ROOM_12_DEW_POINT_CURRENT = auto()
    """Current calculated dew point in the room."""
    ROOM_12_ASSOCIATED_RADIATORS = auto()
    """Modbus object address of the associated radiator source. 0 = NONE."""
    ROOM_12_ASSOCIATED_UFHC = auto()
    """Modbus object address of the associated underfloor heating/cooling source. 0 = NONE."""
    ROOM_12_ASSOCIATED_DRYING = auto()
    """Modbus object address of the associated dehumidifier. 0 = NONE."""
    ROOM_12_ASSOCIATED_THERMAL_INTEGRATION = auto()
    """Modbus object address of the associated thermal integration device. 0 = NONE."""
    ROOM_12_ASSOCIATED_VENTILATION = auto()
    """Modbus object address of the associated ventilation device. 0 = NONE."""
    ROOM_12_AIR_STATE = auto()
    """Radiator (air temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_12_FLOOR_STATE = auto()
    """Underfloor heating/cooling (floor temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_12_DRYING_STATE = auto()
    """Drying (relative humidity) state.

    0 = NONE, 1 = IDLE, 2 = DRYING, 3 = BLOCKED_DRYING"""
    ROOM_12_THERMAL_INTEGRATION_STATE = auto()
    """Thermal integration state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_12_VENTILATION_STATE = auto()
    """Ventilation state.

    0 = NONE, 1 = STOPPED, 2 = UNOCCUPIED, 3 = ECONOMY, 4 = COMFORT, 5 = BOOST"""
    ROOM_12_BLOCKING_SOURCE_RADIATORS = auto()
    """Blocking source for radiators. See WavinSentioBlockingSources."""
    ROOM_12_BLOCKING_SOURCE_UFHC = auto()
    """Blocking source for underfloor heating/cooling. See WavinSentioBlockingSources."""
    ROOM_12_BLOCKING_SOURCE_DRYING = auto()
    """Blocking source for drying. See WavinSentioBlockingSources."""
    ROOM_12_BLOCKING_SOURCE_THERMAL_INTEGRATION = auto()
    """Blocking source for thermal integration. See WavinSentioBlockingSources."""
    ROOM_12_BLOCKING_SOURCE_VENTILATION = auto()
    """Blocking source for ventilation. See WavinSentioBlockingSources."""
    ROOM_12_TYPE = auto()
    """Room type.

    0 = NORMAL (default), 1 = DUMMY (no thermostat or sensor installed)"""
    ROOM_12_ASSOCIATED_HEATING_SOURCE = auto()
    """Dummy rooms only. Modbus object address of the heating source. 0 = NONE."""

    # --- Room 13 (input registers 1301-1328) ---
    ROOM_13_TEMP_AIR_TARGET = auto()
    """Desired temperature in the room, as currently applied by the controller."""
    ROOM_13_STATE = auto()
    """General heating/cooling state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_13_BLOCKING_SOURCE = auto()
    """Why heating/cooling is blocked. See WavinSentioBlockingSources."""
    ROOM_13_TEMP_AIR_CURRENT = auto()
    """Current air temperature measured in the room."""
    ROOM_13_TEMP_FLOOR_CURRENT = auto()
    """Current floor temperature measured in the room."""
    ROOM_13_HUMIDITY_CURRENT = auto()
    """Current relative humidity measured in the room."""
    ROOM_13_DEW_POINT_CURRENT = auto()
    """Current calculated dew point in the room."""
    ROOM_13_ASSOCIATED_RADIATORS = auto()
    """Modbus object address of the associated radiator source. 0 = NONE."""
    ROOM_13_ASSOCIATED_UFHC = auto()
    """Modbus object address of the associated underfloor heating/cooling source. 0 = NONE."""
    ROOM_13_ASSOCIATED_DRYING = auto()
    """Modbus object address of the associated dehumidifier. 0 = NONE."""
    ROOM_13_ASSOCIATED_THERMAL_INTEGRATION = auto()
    """Modbus object address of the associated thermal integration device. 0 = NONE."""
    ROOM_13_ASSOCIATED_VENTILATION = auto()
    """Modbus object address of the associated ventilation device. 0 = NONE."""
    ROOM_13_AIR_STATE = auto()
    """Radiator (air temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_13_FLOOR_STATE = auto()
    """Underfloor heating/cooling (floor temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_13_DRYING_STATE = auto()
    """Drying (relative humidity) state.

    0 = NONE, 1 = IDLE, 2 = DRYING, 3 = BLOCKED_DRYING"""
    ROOM_13_THERMAL_INTEGRATION_STATE = auto()
    """Thermal integration state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_13_VENTILATION_STATE = auto()
    """Ventilation state.

    0 = NONE, 1 = STOPPED, 2 = UNOCCUPIED, 3 = ECONOMY, 4 = COMFORT, 5 = BOOST"""
    ROOM_13_BLOCKING_SOURCE_RADIATORS = auto()
    """Blocking source for radiators. See WavinSentioBlockingSources."""
    ROOM_13_BLOCKING_SOURCE_UFHC = auto()
    """Blocking source for underfloor heating/cooling. See WavinSentioBlockingSources."""
    ROOM_13_BLOCKING_SOURCE_DRYING = auto()
    """Blocking source for drying. See WavinSentioBlockingSources."""
    ROOM_13_BLOCKING_SOURCE_THERMAL_INTEGRATION = auto()
    """Blocking source for thermal integration. See WavinSentioBlockingSources."""
    ROOM_13_BLOCKING_SOURCE_VENTILATION = auto()
    """Blocking source for ventilation. See WavinSentioBlockingSources."""
    ROOM_13_TYPE = auto()
    """Room type.

    0 = NORMAL (default), 1 = DUMMY (no thermostat or sensor installed)"""
    ROOM_13_ASSOCIATED_HEATING_SOURCE = auto()
    """Dummy rooms only. Modbus object address of the heating source. 0 = NONE."""

    # --- Room 14 (input registers 1401-1428) ---
    ROOM_14_TEMP_AIR_TARGET = auto()
    """Desired temperature in the room, as currently applied by the controller."""
    ROOM_14_STATE = auto()
    """General heating/cooling state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_14_BLOCKING_SOURCE = auto()
    """Why heating/cooling is blocked. See WavinSentioBlockingSources."""
    ROOM_14_TEMP_AIR_CURRENT = auto()
    """Current air temperature measured in the room."""
    ROOM_14_TEMP_FLOOR_CURRENT = auto()
    """Current floor temperature measured in the room."""
    ROOM_14_HUMIDITY_CURRENT = auto()
    """Current relative humidity measured in the room."""
    ROOM_14_DEW_POINT_CURRENT = auto()
    """Current calculated dew point in the room."""
    ROOM_14_ASSOCIATED_RADIATORS = auto()
    """Modbus object address of the associated radiator source. 0 = NONE."""
    ROOM_14_ASSOCIATED_UFHC = auto()
    """Modbus object address of the associated underfloor heating/cooling source. 0 = NONE."""
    ROOM_14_ASSOCIATED_DRYING = auto()
    """Modbus object address of the associated dehumidifier. 0 = NONE."""
    ROOM_14_ASSOCIATED_THERMAL_INTEGRATION = auto()
    """Modbus object address of the associated thermal integration device. 0 = NONE."""
    ROOM_14_ASSOCIATED_VENTILATION = auto()
    """Modbus object address of the associated ventilation device. 0 = NONE."""
    ROOM_14_AIR_STATE = auto()
    """Radiator (air temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_14_FLOOR_STATE = auto()
    """Underfloor heating/cooling (floor temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_14_DRYING_STATE = auto()
    """Drying (relative humidity) state.

    0 = NONE, 1 = IDLE, 2 = DRYING, 3 = BLOCKED_DRYING"""
    ROOM_14_THERMAL_INTEGRATION_STATE = auto()
    """Thermal integration state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_14_VENTILATION_STATE = auto()
    """Ventilation state.

    0 = NONE, 1 = STOPPED, 2 = UNOCCUPIED, 3 = ECONOMY, 4 = COMFORT, 5 = BOOST"""
    ROOM_14_BLOCKING_SOURCE_RADIATORS = auto()
    """Blocking source for radiators. See WavinSentioBlockingSources."""
    ROOM_14_BLOCKING_SOURCE_UFHC = auto()
    """Blocking source for underfloor heating/cooling. See WavinSentioBlockingSources."""
    ROOM_14_BLOCKING_SOURCE_DRYING = auto()
    """Blocking source for drying. See WavinSentioBlockingSources."""
    ROOM_14_BLOCKING_SOURCE_THERMAL_INTEGRATION = auto()
    """Blocking source for thermal integration. See WavinSentioBlockingSources."""
    ROOM_14_BLOCKING_SOURCE_VENTILATION = auto()
    """Blocking source for ventilation. See WavinSentioBlockingSources."""
    ROOM_14_TYPE = auto()
    """Room type.

    0 = NORMAL (default), 1 = DUMMY (no thermostat or sensor installed)"""
    ROOM_14_ASSOCIATED_HEATING_SOURCE = auto()
    """Dummy rooms only. Modbus object address of the heating source. 0 = NONE."""

    # --- Room 15 (input registers 1501-1528) ---
    ROOM_15_TEMP_AIR_TARGET = auto()
    """Desired temperature in the room, as currently applied by the controller."""
    ROOM_15_STATE = auto()
    """General heating/cooling state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_15_BLOCKING_SOURCE = auto()
    """Why heating/cooling is blocked. See WavinSentioBlockingSources."""
    ROOM_15_TEMP_AIR_CURRENT = auto()
    """Current air temperature measured in the room."""
    ROOM_15_TEMP_FLOOR_CURRENT = auto()
    """Current floor temperature measured in the room."""
    ROOM_15_HUMIDITY_CURRENT = auto()
    """Current relative humidity measured in the room."""
    ROOM_15_DEW_POINT_CURRENT = auto()
    """Current calculated dew point in the room."""
    ROOM_15_ASSOCIATED_RADIATORS = auto()
    """Modbus object address of the associated radiator source. 0 = NONE."""
    ROOM_15_ASSOCIATED_UFHC = auto()
    """Modbus object address of the associated underfloor heating/cooling source. 0 = NONE."""
    ROOM_15_ASSOCIATED_DRYING = auto()
    """Modbus object address of the associated dehumidifier. 0 = NONE."""
    ROOM_15_ASSOCIATED_THERMAL_INTEGRATION = auto()
    """Modbus object address of the associated thermal integration device. 0 = NONE."""
    ROOM_15_ASSOCIATED_VENTILATION = auto()
    """Modbus object address of the associated ventilation device. 0 = NONE."""
    ROOM_15_AIR_STATE = auto()
    """Radiator (air temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_15_FLOOR_STATE = auto()
    """Underfloor heating/cooling (floor temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_15_DRYING_STATE = auto()
    """Drying (relative humidity) state.

    0 = NONE, 1 = IDLE, 2 = DRYING, 3 = BLOCKED_DRYING"""
    ROOM_15_THERMAL_INTEGRATION_STATE = auto()
    """Thermal integration state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_15_VENTILATION_STATE = auto()
    """Ventilation state.

    0 = NONE, 1 = STOPPED, 2 = UNOCCUPIED, 3 = ECONOMY, 4 = COMFORT, 5 = BOOST"""
    ROOM_15_BLOCKING_SOURCE_RADIATORS = auto()
    """Blocking source for radiators. See WavinSentioBlockingSources."""
    ROOM_15_BLOCKING_SOURCE_UFHC = auto()
    """Blocking source for underfloor heating/cooling. See WavinSentioBlockingSources."""
    ROOM_15_BLOCKING_SOURCE_DRYING = auto()
    """Blocking source for drying. See WavinSentioBlockingSources."""
    ROOM_15_BLOCKING_SOURCE_THERMAL_INTEGRATION = auto()
    """Blocking source for thermal integration. See WavinSentioBlockingSources."""
    ROOM_15_BLOCKING_SOURCE_VENTILATION = auto()
    """Blocking source for ventilation. See WavinSentioBlockingSources."""
    ROOM_15_TYPE = auto()
    """Room type.

    0 = NORMAL (default), 1 = DUMMY (no thermostat or sensor installed)"""
    ROOM_15_ASSOCIATED_HEATING_SOURCE = auto()
    """Dummy rooms only. Modbus object address of the heating source. 0 = NONE."""

    # --- Room 16 (input registers 1601-1628) ---
    ROOM_16_TEMP_AIR_TARGET = auto()
    """Desired temperature in the room, as currently applied by the controller."""
    ROOM_16_STATE = auto()
    """General heating/cooling state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_16_BLOCKING_SOURCE = auto()
    """Why heating/cooling is blocked. See WavinSentioBlockingSources."""
    ROOM_16_TEMP_AIR_CURRENT = auto()
    """Current air temperature measured in the room."""
    ROOM_16_TEMP_FLOOR_CURRENT = auto()
    """Current floor temperature measured in the room."""
    ROOM_16_HUMIDITY_CURRENT = auto()
    """Current relative humidity measured in the room."""
    ROOM_16_DEW_POINT_CURRENT = auto()
    """Current calculated dew point in the room."""
    ROOM_16_ASSOCIATED_RADIATORS = auto()
    """Modbus object address of the associated radiator source. 0 = NONE."""
    ROOM_16_ASSOCIATED_UFHC = auto()
    """Modbus object address of the associated underfloor heating/cooling source. 0 = NONE."""
    ROOM_16_ASSOCIATED_DRYING = auto()
    """Modbus object address of the associated dehumidifier. 0 = NONE."""
    ROOM_16_ASSOCIATED_THERMAL_INTEGRATION = auto()
    """Modbus object address of the associated thermal integration device. 0 = NONE."""
    ROOM_16_ASSOCIATED_VENTILATION = auto()
    """Modbus object address of the associated ventilation device. 0 = NONE."""
    ROOM_16_AIR_STATE = auto()
    """Radiator (air temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_16_FLOOR_STATE = auto()
    """Underfloor heating/cooling (floor temperature) state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_16_DRYING_STATE = auto()
    """Drying (relative humidity) state.

    0 = NONE, 1 = IDLE, 2 = DRYING, 3 = BLOCKED_DRYING"""
    ROOM_16_THERMAL_INTEGRATION_STATE = auto()
    """Thermal integration state.

    0 = NONE, 1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED_HEATING, 5 = BLOCKED_COOLING"""
    ROOM_16_VENTILATION_STATE = auto()
    """Ventilation state.

    0 = NONE, 1 = STOPPED, 2 = UNOCCUPIED, 3 = ECONOMY, 4 = COMFORT, 5 = BOOST"""
    ROOM_16_BLOCKING_SOURCE_RADIATORS = auto()
    """Blocking source for radiators. See WavinSentioBlockingSources."""
    ROOM_16_BLOCKING_SOURCE_UFHC = auto()
    """Blocking source for underfloor heating/cooling. See WavinSentioBlockingSources."""
    ROOM_16_BLOCKING_SOURCE_DRYING = auto()
    """Blocking source for drying. See WavinSentioBlockingSources."""
    ROOM_16_BLOCKING_SOURCE_THERMAL_INTEGRATION = auto()
    """Blocking source for thermal integration. See WavinSentioBlockingSources."""
    ROOM_16_BLOCKING_SOURCE_VENTILATION = auto()
    """Blocking source for ventilation. See WavinSentioBlockingSources."""
    ROOM_16_TYPE = auto()
    """Room type.

    0 = NORMAL (default), 1 = DUMMY (no thermostat or sensor installed)"""
    ROOM_16_ASSOCIATED_HEATING_SOURCE = auto()
    """Dummy rooms only. Modbus object address of the heating source. 0 = NONE."""

    # --- Peripheral 1 (base 51200) ---
    PERIPHERAL_1_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_1_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_1_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_1_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 2 (base 51300) ---
    PERIPHERAL_2_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_2_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_2_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_2_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 3 (base 51400) ---
    PERIPHERAL_3_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_3_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_3_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_3_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 4 (base 51500) ---
    PERIPHERAL_4_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_4_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_4_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_4_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 5 (base 51600) ---
    PERIPHERAL_5_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_5_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_5_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_5_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 6 (base 51700) ---
    PERIPHERAL_6_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_6_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_6_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_6_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 7 (base 51800) ---
    PERIPHERAL_7_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_7_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_7_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_7_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 8 (base 51900) ---
    PERIPHERAL_8_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_8_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_8_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_8_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 9 (base 52000) ---
    PERIPHERAL_9_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_9_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_9_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_9_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 10 (base 52100) ---
    PERIPHERAL_10_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_10_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_10_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_10_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 11 (base 52200) ---
    PERIPHERAL_11_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_11_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_11_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_11_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 12 (base 52300) ---
    PERIPHERAL_12_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_12_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_12_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_12_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 13 (base 52400) ---
    PERIPHERAL_13_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_13_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_13_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_13_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 14 (base 52500) ---
    PERIPHERAL_14_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_14_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_14_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_14_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 15 (base 52600) ---
    PERIPHERAL_15_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_15_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_15_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_15_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 16 (base 52700) ---
    PERIPHERAL_16_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_16_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_16_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_16_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 17 (base 52800) ---
    PERIPHERAL_17_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_17_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_17_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_17_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 18 (base 52900) ---
    PERIPHERAL_18_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_18_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_18_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_18_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 19 (base 53000) ---
    PERIPHERAL_19_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_19_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_19_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_19_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 20 (base 53100) ---
    PERIPHERAL_20_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_20_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_20_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_20_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 21 (base 53200) ---
    PERIPHERAL_21_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_21_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_21_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_21_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 22 (base 53300) ---
    PERIPHERAL_22_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_22_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_22_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_22_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 23 (base 53400) ---
    PERIPHERAL_23_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_23_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_23_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_23_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 24 (base 53500) ---
    PERIPHERAL_24_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_24_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_24_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_24_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 25 (base 53600) ---
    PERIPHERAL_25_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_25_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_25_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_25_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 26 (base 53700) ---
    PERIPHERAL_26_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_26_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_26_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_26_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 27 (base 53800) ---
    PERIPHERAL_27_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_27_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_27_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_27_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 28 (base 53900) ---
    PERIPHERAL_28_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_28_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_28_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_28_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 29 (base 54000) ---
    PERIPHERAL_29_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_29_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_29_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_29_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 30 (base 54100) ---
    PERIPHERAL_30_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_30_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_30_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_30_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 31 (base 54200) ---
    PERIPHERAL_31_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_31_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_31_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_31_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 32 (base 54300) ---
    PERIPHERAL_32_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_32_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_32_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_32_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 33 (base 54400) ---
    PERIPHERAL_33_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_33_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_33_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_33_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 34 (base 54500) ---
    PERIPHERAL_34_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_34_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_34_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_34_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 35 (base 54600) ---
    PERIPHERAL_35_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_35_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_35_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_35_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 36 (base 54700) ---
    PERIPHERAL_36_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_36_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_36_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_36_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 37 (base 54800) ---
    PERIPHERAL_37_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_37_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_37_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_37_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 38 (base 54900) ---
    PERIPHERAL_38_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_38_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_38_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_38_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 39 (base 55000) ---
    PERIPHERAL_39_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_39_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_39_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_39_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 40 (base 55100) ---
    PERIPHERAL_40_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_40_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_40_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_40_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 41 (base 55200) ---
    PERIPHERAL_41_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_41_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_41_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_41_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 42 (base 55300) ---
    PERIPHERAL_42_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_42_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_42_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_42_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 43 (base 55400) ---
    PERIPHERAL_43_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_43_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_43_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_43_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 44 (base 55500) ---
    PERIPHERAL_44_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_44_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_44_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_44_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 45 (base 55600) ---
    PERIPHERAL_45_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_45_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_45_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_45_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 46 (base 55700) ---
    PERIPHERAL_46_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_46_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_46_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_46_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 47 (base 55800) ---
    PERIPHERAL_47_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_47_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_47_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_47_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 48 (base 55900) ---
    PERIPHERAL_48_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_48_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_48_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_48_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 49 (base 56000) ---
    PERIPHERAL_49_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_49_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_49_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_49_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 50 (base 56100) ---
    PERIPHERAL_50_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_50_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_50_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_50_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 51 (base 56200) ---
    PERIPHERAL_51_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_51_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_51_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_51_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 52 (base 56300) ---
    PERIPHERAL_52_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_52_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_52_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_52_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 53 (base 56400) ---
    PERIPHERAL_53_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_53_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_53_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_53_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 54 (base 56500) ---
    PERIPHERAL_54_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_54_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_54_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_54_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 55 (base 56600) ---
    PERIPHERAL_55_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_55_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_55_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_55_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 56 (base 56700) ---
    PERIPHERAL_56_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_56_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_56_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_56_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 57 (base 56800) ---
    PERIPHERAL_57_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_57_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_57_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_57_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 58 (base 56900) ---
    PERIPHERAL_58_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_58_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_58_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_58_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 59 (base 57000) ---
    PERIPHERAL_59_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_59_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_59_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_59_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 60 (base 57100) ---
    PERIPHERAL_60_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_60_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_60_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_60_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 61 (base 57200) ---
    PERIPHERAL_61_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_61_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_61_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_61_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 62 (base 57300) ---
    PERIPHERAL_62_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_62_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_62_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_62_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 63 (base 57400) ---
    PERIPHERAL_63_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_63_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_63_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_63_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""

    # --- Peripheral 64 (base 57500) ---
    PERIPHERAL_64_TYPE = auto()
    """Peripheral product type. See WavinPeripheralTypes."""
    PERIPHERAL_64_SN = auto()
    """Serial number. This is the peripheral's stable identity - the slot index is not."""
    PERIPHERAL_64_OWNER = auto()
    """Owning object: 0 = Location, 1..16 = Room 1..16."""
    PERIPHERAL_64_SIGNAL_STRENGTH = auto()
    """Signal strength, 0 (worst) to 6 (best)."""


class WavinSentioSetpointKey(ModbusSetpointKey):
    """Read/write values (Modbus holding registers)."""
    SETPOINT_MAJOR = auto()
    """Address space major version. Incremented on incompatible changes."""
    SETPOINT_MINOR = auto()
    """Address space minor version. Incremented on compatible changes."""
    MODBUS_MODE = auto()
    """0 = DISABLED, 1 = READ_ONLY, 2 = READ_WRITE, 3 = WRITE_WITH_PASSWORD."""
    MODBUS_PASSWORD = auto()
    """Write-only. Enables writes for 11 minutes when mode = WRITE_WITH_PASSWORD."""
    LOCATION_NAME = auto()
    """Location name. 32 bytes, UTF-8."""
    STANDBY_ENABLE = auto()
    """Standby mode on/off."""
    VACATION_ENABLE = auto()
    """Vacation mode on/off."""
    DATETIME_UNIX = auto()
    """Local time as a unix timestamp, including DST when enabled."""
    DAYLIGHT_SAVING_ENABLE = auto()
    """Daylight saving time allowed."""
    TEMP_OUTDOOR_COOLING_MIN = auto()
    """Cooling is blocked while the outdoor temperature is below this value."""
    TEMP_OUTDOOR_HEATING_MAX = auto()
    """Heating is blocked while the outdoor temperature is above this value."""
    UPDATE_MODE = auto()
    """0 = do not allow from mobile app, 1 = enabled, 2 = disabled entirely."""
    HEATING_COOLING_MODE_BMS_OVERRIDE = auto()
    """BMS override of the heating/cooling changeover. Hardware-profile dependent."""
    TIMEZONE = auto()
    """Timezone number; see the manual's timezone list."""


    # --- Room 1 (holding registers 10001-10035) ---
    ROOM_1_NAME = auto()
    """Room name. 32 bytes, UTF-8."""
    ROOM_1_MODE = auto()
    """0 = SCHEDULE, 1 = MANUAL.

    In SCHEDULE mode the room temperature setpoint is ignored and the scheduler decides."""
    ROOM_1_MODE_OVERRIDE = auto()
    """0 = NONE, 1 = TEMPORARY, 2 = VACATION_AWAY, 3 = ADJUST.

    While an override is active (> NONE) the room temperature setpoint is not used.
    Write 0 to clear the override."""
    ROOM_1_TEMP_AIR_TARGET = auto()
    """Temperature requested by the user.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""
    ROOM_1_LOCK = auto()
    """Thermostat user-interface access level.

    8 = LOCKED (read only), 16 = HOTEL, 32 = UNLOCKED.
    Only those three values are valid; the device rejects or clamps anything else."""
    ROOM_1_TEMP_STANDBY = auto()
    """Room temperature used while the location is in standby."""
    ROOM_1_TEMP_VACATION = auto()
    """Room temperature used while the location is in vacation mode."""
    ROOM_1_EXCLUDE_FROM_VACATION = auto()
    """Do not allow vacation mode in this room."""
    ROOM_1_ADAPTIVE_ENABLE = auto()
    """Allow adaptive control."""
    ROOM_1_THERMAL_INTEGRATION_HEATING_OFFSET = auto()
    """Thermal integration heating offset."""
    ROOM_1_THERMAL_INTEGRATION_HYSTERESIS = auto()
    """Thermal integration hysteresis."""
    ROOM_1_HUMIDITY_THRESHOLD_HEATING = auto()
    """Humidity threshold for heating."""
    ROOM_1_HUMIDITY_THRESHOLD_COOLING = auto()
    """Humidity threshold for cooling."""
    ROOM_1_HUMIDITY_HYSTERESIS = auto()
    """Humidity hysteresis."""
    ROOM_1_DRYING_COOLING_WATER_OFFSET = auto()
    """Drying: cooling water offset."""
    ROOM_1_DRYING_COOLING_WATER_OFFSET_HYSTERESIS = auto()
    """Drying: cooling water offset hysteresis."""
    ROOM_1_DEW_POINT_COOLING_THRESHOLD = auto()
    """Dew point threshold temperature when cooling."""
    ROOM_1_DEW_POINT_COOLING_THRESHOLD_HYSTERESIS = auto()
    """Dew point threshold hysteresis when cooling."""
    ROOM_1_HUMIDITY_HIGH_ALARM_LIMIT = auto()
    """Humidity high alarm limit."""
    ROOM_1_TEMP_PRESET = auto()
    """0 = ECO, 1 = COMFORT, 2 = EXTRA COMFORT.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""

    # --- Room 2 (holding registers 20001-20035) ---
    ROOM_2_NAME = auto()
    """Room name. 32 bytes, UTF-8."""
    ROOM_2_MODE = auto()
    """0 = SCHEDULE, 1 = MANUAL.

    In SCHEDULE mode the room temperature setpoint is ignored and the scheduler decides."""
    ROOM_2_MODE_OVERRIDE = auto()
    """0 = NONE, 1 = TEMPORARY, 2 = VACATION_AWAY, 3 = ADJUST.

    While an override is active (> NONE) the room temperature setpoint is not used.
    Write 0 to clear the override."""
    ROOM_2_TEMP_AIR_TARGET = auto()
    """Temperature requested by the user.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""
    ROOM_2_LOCK = auto()
    """Thermostat user-interface access level.

    8 = LOCKED (read only), 16 = HOTEL, 32 = UNLOCKED.
    Only those three values are valid; the device rejects or clamps anything else."""
    ROOM_2_TEMP_STANDBY = auto()
    """Room temperature used while the location is in standby."""
    ROOM_2_TEMP_VACATION = auto()
    """Room temperature used while the location is in vacation mode."""
    ROOM_2_EXCLUDE_FROM_VACATION = auto()
    """Do not allow vacation mode in this room."""
    ROOM_2_ADAPTIVE_ENABLE = auto()
    """Allow adaptive control."""
    ROOM_2_THERMAL_INTEGRATION_HEATING_OFFSET = auto()
    """Thermal integration heating offset."""
    ROOM_2_THERMAL_INTEGRATION_HYSTERESIS = auto()
    """Thermal integration hysteresis."""
    ROOM_2_HUMIDITY_THRESHOLD_HEATING = auto()
    """Humidity threshold for heating."""
    ROOM_2_HUMIDITY_THRESHOLD_COOLING = auto()
    """Humidity threshold for cooling."""
    ROOM_2_HUMIDITY_HYSTERESIS = auto()
    """Humidity hysteresis."""
    ROOM_2_DRYING_COOLING_WATER_OFFSET = auto()
    """Drying: cooling water offset."""
    ROOM_2_DRYING_COOLING_WATER_OFFSET_HYSTERESIS = auto()
    """Drying: cooling water offset hysteresis."""
    ROOM_2_DEW_POINT_COOLING_THRESHOLD = auto()
    """Dew point threshold temperature when cooling."""
    ROOM_2_DEW_POINT_COOLING_THRESHOLD_HYSTERESIS = auto()
    """Dew point threshold hysteresis when cooling."""
    ROOM_2_HUMIDITY_HIGH_ALARM_LIMIT = auto()
    """Humidity high alarm limit."""
    ROOM_2_TEMP_PRESET = auto()
    """0 = ECO, 1 = COMFORT, 2 = EXTRA COMFORT.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""

    # --- Room 3 (holding registers 30001-30035) ---
    ROOM_3_NAME = auto()
    """Room name. 32 bytes, UTF-8."""
    ROOM_3_MODE = auto()
    """0 = SCHEDULE, 1 = MANUAL.

    In SCHEDULE mode the room temperature setpoint is ignored and the scheduler decides."""
    ROOM_3_MODE_OVERRIDE = auto()
    """0 = NONE, 1 = TEMPORARY, 2 = VACATION_AWAY, 3 = ADJUST.

    While an override is active (> NONE) the room temperature setpoint is not used.
    Write 0 to clear the override."""
    ROOM_3_TEMP_AIR_TARGET = auto()
    """Temperature requested by the user.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""
    ROOM_3_LOCK = auto()
    """Thermostat user-interface access level.

    8 = LOCKED (read only), 16 = HOTEL, 32 = UNLOCKED.
    Only those three values are valid; the device rejects or clamps anything else."""
    ROOM_3_TEMP_STANDBY = auto()
    """Room temperature used while the location is in standby."""
    ROOM_3_TEMP_VACATION = auto()
    """Room temperature used while the location is in vacation mode."""
    ROOM_3_EXCLUDE_FROM_VACATION = auto()
    """Do not allow vacation mode in this room."""
    ROOM_3_ADAPTIVE_ENABLE = auto()
    """Allow adaptive control."""
    ROOM_3_THERMAL_INTEGRATION_HEATING_OFFSET = auto()
    """Thermal integration heating offset."""
    ROOM_3_THERMAL_INTEGRATION_HYSTERESIS = auto()
    """Thermal integration hysteresis."""
    ROOM_3_HUMIDITY_THRESHOLD_HEATING = auto()
    """Humidity threshold for heating."""
    ROOM_3_HUMIDITY_THRESHOLD_COOLING = auto()
    """Humidity threshold for cooling."""
    ROOM_3_HUMIDITY_HYSTERESIS = auto()
    """Humidity hysteresis."""
    ROOM_3_DRYING_COOLING_WATER_OFFSET = auto()
    """Drying: cooling water offset."""
    ROOM_3_DRYING_COOLING_WATER_OFFSET_HYSTERESIS = auto()
    """Drying: cooling water offset hysteresis."""
    ROOM_3_DEW_POINT_COOLING_THRESHOLD = auto()
    """Dew point threshold temperature when cooling."""
    ROOM_3_DEW_POINT_COOLING_THRESHOLD_HYSTERESIS = auto()
    """Dew point threshold hysteresis when cooling."""
    ROOM_3_HUMIDITY_HIGH_ALARM_LIMIT = auto()
    """Humidity high alarm limit."""
    ROOM_3_TEMP_PRESET = auto()
    """0 = ECO, 1 = COMFORT, 2 = EXTRA COMFORT.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""

    # --- Room 4 (holding registers 40001-40035) ---
    ROOM_4_NAME = auto()
    """Room name. 32 bytes, UTF-8."""
    ROOM_4_MODE = auto()
    """0 = SCHEDULE, 1 = MANUAL.

    In SCHEDULE mode the room temperature setpoint is ignored and the scheduler decides."""
    ROOM_4_MODE_OVERRIDE = auto()
    """0 = NONE, 1 = TEMPORARY, 2 = VACATION_AWAY, 3 = ADJUST.

    While an override is active (> NONE) the room temperature setpoint is not used.
    Write 0 to clear the override."""
    ROOM_4_TEMP_AIR_TARGET = auto()
    """Temperature requested by the user.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""
    ROOM_4_LOCK = auto()
    """Thermostat user-interface access level.

    8 = LOCKED (read only), 16 = HOTEL, 32 = UNLOCKED.
    Only those three values are valid; the device rejects or clamps anything else."""
    ROOM_4_TEMP_STANDBY = auto()
    """Room temperature used while the location is in standby."""
    ROOM_4_TEMP_VACATION = auto()
    """Room temperature used while the location is in vacation mode."""
    ROOM_4_EXCLUDE_FROM_VACATION = auto()
    """Do not allow vacation mode in this room."""
    ROOM_4_ADAPTIVE_ENABLE = auto()
    """Allow adaptive control."""
    ROOM_4_THERMAL_INTEGRATION_HEATING_OFFSET = auto()
    """Thermal integration heating offset."""
    ROOM_4_THERMAL_INTEGRATION_HYSTERESIS = auto()
    """Thermal integration hysteresis."""
    ROOM_4_HUMIDITY_THRESHOLD_HEATING = auto()
    """Humidity threshold for heating."""
    ROOM_4_HUMIDITY_THRESHOLD_COOLING = auto()
    """Humidity threshold for cooling."""
    ROOM_4_HUMIDITY_HYSTERESIS = auto()
    """Humidity hysteresis."""
    ROOM_4_DRYING_COOLING_WATER_OFFSET = auto()
    """Drying: cooling water offset."""
    ROOM_4_DRYING_COOLING_WATER_OFFSET_HYSTERESIS = auto()
    """Drying: cooling water offset hysteresis."""
    ROOM_4_DEW_POINT_COOLING_THRESHOLD = auto()
    """Dew point threshold temperature when cooling."""
    ROOM_4_DEW_POINT_COOLING_THRESHOLD_HYSTERESIS = auto()
    """Dew point threshold hysteresis when cooling."""
    ROOM_4_HUMIDITY_HIGH_ALARM_LIMIT = auto()
    """Humidity high alarm limit."""
    ROOM_4_TEMP_PRESET = auto()
    """0 = ECO, 1 = COMFORT, 2 = EXTRA COMFORT.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""

    # --- Room 5 (holding registers 50001-50035) ---
    ROOM_5_NAME = auto()
    """Room name. 32 bytes, UTF-8."""
    ROOM_5_MODE = auto()
    """0 = SCHEDULE, 1 = MANUAL.

    In SCHEDULE mode the room temperature setpoint is ignored and the scheduler decides."""
    ROOM_5_MODE_OVERRIDE = auto()
    """0 = NONE, 1 = TEMPORARY, 2 = VACATION_AWAY, 3 = ADJUST.

    While an override is active (> NONE) the room temperature setpoint is not used.
    Write 0 to clear the override."""
    ROOM_5_TEMP_AIR_TARGET = auto()
    """Temperature requested by the user.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""
    ROOM_5_LOCK = auto()
    """Thermostat user-interface access level.

    8 = LOCKED (read only), 16 = HOTEL, 32 = UNLOCKED.
    Only those three values are valid; the device rejects or clamps anything else."""
    ROOM_5_TEMP_STANDBY = auto()
    """Room temperature used while the location is in standby."""
    ROOM_5_TEMP_VACATION = auto()
    """Room temperature used while the location is in vacation mode."""
    ROOM_5_EXCLUDE_FROM_VACATION = auto()
    """Do not allow vacation mode in this room."""
    ROOM_5_ADAPTIVE_ENABLE = auto()
    """Allow adaptive control."""
    ROOM_5_THERMAL_INTEGRATION_HEATING_OFFSET = auto()
    """Thermal integration heating offset."""
    ROOM_5_THERMAL_INTEGRATION_HYSTERESIS = auto()
    """Thermal integration hysteresis."""
    ROOM_5_HUMIDITY_THRESHOLD_HEATING = auto()
    """Humidity threshold for heating."""
    ROOM_5_HUMIDITY_THRESHOLD_COOLING = auto()
    """Humidity threshold for cooling."""
    ROOM_5_HUMIDITY_HYSTERESIS = auto()
    """Humidity hysteresis."""
    ROOM_5_DRYING_COOLING_WATER_OFFSET = auto()
    """Drying: cooling water offset."""
    ROOM_5_DRYING_COOLING_WATER_OFFSET_HYSTERESIS = auto()
    """Drying: cooling water offset hysteresis."""
    ROOM_5_DEW_POINT_COOLING_THRESHOLD = auto()
    """Dew point threshold temperature when cooling."""
    ROOM_5_DEW_POINT_COOLING_THRESHOLD_HYSTERESIS = auto()
    """Dew point threshold hysteresis when cooling."""
    ROOM_5_HUMIDITY_HIGH_ALARM_LIMIT = auto()
    """Humidity high alarm limit."""
    ROOM_5_TEMP_PRESET = auto()
    """0 = ECO, 1 = COMFORT, 2 = EXTRA COMFORT.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""

    # --- Room 6 (holding registers 60001-60035) ---
    ROOM_6_NAME = auto()
    """Room name. 32 bytes, UTF-8."""
    ROOM_6_MODE = auto()
    """0 = SCHEDULE, 1 = MANUAL.

    In SCHEDULE mode the room temperature setpoint is ignored and the scheduler decides."""
    ROOM_6_MODE_OVERRIDE = auto()
    """0 = NONE, 1 = TEMPORARY, 2 = VACATION_AWAY, 3 = ADJUST.

    While an override is active (> NONE) the room temperature setpoint is not used.
    Write 0 to clear the override."""
    ROOM_6_TEMP_AIR_TARGET = auto()
    """Temperature requested by the user.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""
    ROOM_6_LOCK = auto()
    """Thermostat user-interface access level.

    8 = LOCKED (read only), 16 = HOTEL, 32 = UNLOCKED.
    Only those three values are valid; the device rejects or clamps anything else."""
    ROOM_6_TEMP_STANDBY = auto()
    """Room temperature used while the location is in standby."""
    ROOM_6_TEMP_VACATION = auto()
    """Room temperature used while the location is in vacation mode."""
    ROOM_6_EXCLUDE_FROM_VACATION = auto()
    """Do not allow vacation mode in this room."""
    ROOM_6_ADAPTIVE_ENABLE = auto()
    """Allow adaptive control."""
    ROOM_6_THERMAL_INTEGRATION_HEATING_OFFSET = auto()
    """Thermal integration heating offset."""
    ROOM_6_THERMAL_INTEGRATION_HYSTERESIS = auto()
    """Thermal integration hysteresis."""
    ROOM_6_HUMIDITY_THRESHOLD_HEATING = auto()
    """Humidity threshold for heating."""
    ROOM_6_HUMIDITY_THRESHOLD_COOLING = auto()
    """Humidity threshold for cooling."""
    ROOM_6_HUMIDITY_HYSTERESIS = auto()
    """Humidity hysteresis."""
    ROOM_6_DRYING_COOLING_WATER_OFFSET = auto()
    """Drying: cooling water offset."""
    ROOM_6_DRYING_COOLING_WATER_OFFSET_HYSTERESIS = auto()
    """Drying: cooling water offset hysteresis."""
    ROOM_6_DEW_POINT_COOLING_THRESHOLD = auto()
    """Dew point threshold temperature when cooling."""
    ROOM_6_DEW_POINT_COOLING_THRESHOLD_HYSTERESIS = auto()
    """Dew point threshold hysteresis when cooling."""
    ROOM_6_HUMIDITY_HIGH_ALARM_LIMIT = auto()
    """Humidity high alarm limit."""
    ROOM_6_TEMP_PRESET = auto()
    """0 = ECO, 1 = COMFORT, 2 = EXTRA COMFORT.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""

    # --- Room 7 (holding registers 70001-70035) ---
    ROOM_7_NAME = auto()
    """Room name. 32 bytes, UTF-8."""
    ROOM_7_MODE = auto()
    """0 = SCHEDULE, 1 = MANUAL.

    In SCHEDULE mode the room temperature setpoint is ignored and the scheduler decides."""
    ROOM_7_MODE_OVERRIDE = auto()
    """0 = NONE, 1 = TEMPORARY, 2 = VACATION_AWAY, 3 = ADJUST.

    While an override is active (> NONE) the room temperature setpoint is not used.
    Write 0 to clear the override."""
    ROOM_7_TEMP_AIR_TARGET = auto()
    """Temperature requested by the user.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""
    ROOM_7_LOCK = auto()
    """Thermostat user-interface access level.

    8 = LOCKED (read only), 16 = HOTEL, 32 = UNLOCKED.
    Only those three values are valid; the device rejects or clamps anything else."""
    ROOM_7_TEMP_STANDBY = auto()
    """Room temperature used while the location is in standby."""
    ROOM_7_TEMP_VACATION = auto()
    """Room temperature used while the location is in vacation mode."""
    ROOM_7_EXCLUDE_FROM_VACATION = auto()
    """Do not allow vacation mode in this room."""
    ROOM_7_ADAPTIVE_ENABLE = auto()
    """Allow adaptive control."""
    ROOM_7_THERMAL_INTEGRATION_HEATING_OFFSET = auto()
    """Thermal integration heating offset."""
    ROOM_7_THERMAL_INTEGRATION_HYSTERESIS = auto()
    """Thermal integration hysteresis."""
    ROOM_7_HUMIDITY_THRESHOLD_HEATING = auto()
    """Humidity threshold for heating."""
    ROOM_7_HUMIDITY_THRESHOLD_COOLING = auto()
    """Humidity threshold for cooling."""
    ROOM_7_HUMIDITY_HYSTERESIS = auto()
    """Humidity hysteresis."""
    ROOM_7_DRYING_COOLING_WATER_OFFSET = auto()
    """Drying: cooling water offset."""
    ROOM_7_DRYING_COOLING_WATER_OFFSET_HYSTERESIS = auto()
    """Drying: cooling water offset hysteresis."""
    ROOM_7_DEW_POINT_COOLING_THRESHOLD = auto()
    """Dew point threshold temperature when cooling."""
    ROOM_7_DEW_POINT_COOLING_THRESHOLD_HYSTERESIS = auto()
    """Dew point threshold hysteresis when cooling."""
    ROOM_7_HUMIDITY_HIGH_ALARM_LIMIT = auto()
    """Humidity high alarm limit."""
    ROOM_7_TEMP_PRESET = auto()
    """0 = ECO, 1 = COMFORT, 2 = EXTRA COMFORT.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""

    # --- Room 8 (holding registers 80001-80035) ---
    ROOM_8_NAME = auto()
    """Room name. 32 bytes, UTF-8."""
    ROOM_8_MODE = auto()
    """0 = SCHEDULE, 1 = MANUAL.

    In SCHEDULE mode the room temperature setpoint is ignored and the scheduler decides."""
    ROOM_8_MODE_OVERRIDE = auto()
    """0 = NONE, 1 = TEMPORARY, 2 = VACATION_AWAY, 3 = ADJUST.

    While an override is active (> NONE) the room temperature setpoint is not used.
    Write 0 to clear the override."""
    ROOM_8_TEMP_AIR_TARGET = auto()
    """Temperature requested by the user.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""
    ROOM_8_LOCK = auto()
    """Thermostat user-interface access level.

    8 = LOCKED (read only), 16 = HOTEL, 32 = UNLOCKED.
    Only those three values are valid; the device rejects or clamps anything else."""
    ROOM_8_TEMP_STANDBY = auto()
    """Room temperature used while the location is in standby."""
    ROOM_8_TEMP_VACATION = auto()
    """Room temperature used while the location is in vacation mode."""
    ROOM_8_EXCLUDE_FROM_VACATION = auto()
    """Do not allow vacation mode in this room."""
    ROOM_8_ADAPTIVE_ENABLE = auto()
    """Allow adaptive control."""
    ROOM_8_THERMAL_INTEGRATION_HEATING_OFFSET = auto()
    """Thermal integration heating offset."""
    ROOM_8_THERMAL_INTEGRATION_HYSTERESIS = auto()
    """Thermal integration hysteresis."""
    ROOM_8_HUMIDITY_THRESHOLD_HEATING = auto()
    """Humidity threshold for heating."""
    ROOM_8_HUMIDITY_THRESHOLD_COOLING = auto()
    """Humidity threshold for cooling."""
    ROOM_8_HUMIDITY_HYSTERESIS = auto()
    """Humidity hysteresis."""
    ROOM_8_DRYING_COOLING_WATER_OFFSET = auto()
    """Drying: cooling water offset."""
    ROOM_8_DRYING_COOLING_WATER_OFFSET_HYSTERESIS = auto()
    """Drying: cooling water offset hysteresis."""
    ROOM_8_DEW_POINT_COOLING_THRESHOLD = auto()
    """Dew point threshold temperature when cooling."""
    ROOM_8_DEW_POINT_COOLING_THRESHOLD_HYSTERESIS = auto()
    """Dew point threshold hysteresis when cooling."""
    ROOM_8_HUMIDITY_HIGH_ALARM_LIMIT = auto()
    """Humidity high alarm limit."""
    ROOM_8_TEMP_PRESET = auto()
    """0 = ECO, 1 = COMFORT, 2 = EXTRA COMFORT.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""

    # --- Room 9 (holding registers 90001-90035) ---
    ROOM_9_NAME = auto()
    """Room name. 32 bytes, UTF-8."""
    ROOM_9_MODE = auto()
    """0 = SCHEDULE, 1 = MANUAL.

    In SCHEDULE mode the room temperature setpoint is ignored and the scheduler decides."""
    ROOM_9_MODE_OVERRIDE = auto()
    """0 = NONE, 1 = TEMPORARY, 2 = VACATION_AWAY, 3 = ADJUST.

    While an override is active (> NONE) the room temperature setpoint is not used.
    Write 0 to clear the override."""
    ROOM_9_TEMP_AIR_TARGET = auto()
    """Temperature requested by the user.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""
    ROOM_9_LOCK = auto()
    """Thermostat user-interface access level.

    8 = LOCKED (read only), 16 = HOTEL, 32 = UNLOCKED.
    Only those three values are valid; the device rejects or clamps anything else."""
    ROOM_9_TEMP_STANDBY = auto()
    """Room temperature used while the location is in standby."""
    ROOM_9_TEMP_VACATION = auto()
    """Room temperature used while the location is in vacation mode."""
    ROOM_9_EXCLUDE_FROM_VACATION = auto()
    """Do not allow vacation mode in this room."""
    ROOM_9_ADAPTIVE_ENABLE = auto()
    """Allow adaptive control."""
    ROOM_9_THERMAL_INTEGRATION_HEATING_OFFSET = auto()
    """Thermal integration heating offset."""
    ROOM_9_THERMAL_INTEGRATION_HYSTERESIS = auto()
    """Thermal integration hysteresis."""
    ROOM_9_HUMIDITY_THRESHOLD_HEATING = auto()
    """Humidity threshold for heating."""
    ROOM_9_HUMIDITY_THRESHOLD_COOLING = auto()
    """Humidity threshold for cooling."""
    ROOM_9_HUMIDITY_HYSTERESIS = auto()
    """Humidity hysteresis."""
    ROOM_9_DRYING_COOLING_WATER_OFFSET = auto()
    """Drying: cooling water offset."""
    ROOM_9_DRYING_COOLING_WATER_OFFSET_HYSTERESIS = auto()
    """Drying: cooling water offset hysteresis."""
    ROOM_9_DEW_POINT_COOLING_THRESHOLD = auto()
    """Dew point threshold temperature when cooling."""
    ROOM_9_DEW_POINT_COOLING_THRESHOLD_HYSTERESIS = auto()
    """Dew point threshold hysteresis when cooling."""
    ROOM_9_HUMIDITY_HIGH_ALARM_LIMIT = auto()
    """Humidity high alarm limit."""
    ROOM_9_TEMP_PRESET = auto()
    """0 = ECO, 1 = COMFORT, 2 = EXTRA COMFORT.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""

    # --- Room 10 (holding registers 100001-100035) ---
    ROOM_10_NAME = auto()
    """Room name. 32 bytes, UTF-8."""
    ROOM_10_MODE = auto()
    """0 = SCHEDULE, 1 = MANUAL.

    In SCHEDULE mode the room temperature setpoint is ignored and the scheduler decides."""
    ROOM_10_MODE_OVERRIDE = auto()
    """0 = NONE, 1 = TEMPORARY, 2 = VACATION_AWAY, 3 = ADJUST.

    While an override is active (> NONE) the room temperature setpoint is not used.
    Write 0 to clear the override."""
    ROOM_10_TEMP_AIR_TARGET = auto()
    """Temperature requested by the user.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""
    ROOM_10_LOCK = auto()
    """Thermostat user-interface access level.

    8 = LOCKED (read only), 16 = HOTEL, 32 = UNLOCKED.
    Only those three values are valid; the device rejects or clamps anything else."""
    ROOM_10_TEMP_STANDBY = auto()
    """Room temperature used while the location is in standby."""
    ROOM_10_TEMP_VACATION = auto()
    """Room temperature used while the location is in vacation mode."""
    ROOM_10_EXCLUDE_FROM_VACATION = auto()
    """Do not allow vacation mode in this room."""
    ROOM_10_ADAPTIVE_ENABLE = auto()
    """Allow adaptive control."""
    ROOM_10_THERMAL_INTEGRATION_HEATING_OFFSET = auto()
    """Thermal integration heating offset."""
    ROOM_10_THERMAL_INTEGRATION_HYSTERESIS = auto()
    """Thermal integration hysteresis."""
    ROOM_10_HUMIDITY_THRESHOLD_HEATING = auto()
    """Humidity threshold for heating."""
    ROOM_10_HUMIDITY_THRESHOLD_COOLING = auto()
    """Humidity threshold for cooling."""
    ROOM_10_HUMIDITY_HYSTERESIS = auto()
    """Humidity hysteresis."""
    ROOM_10_DRYING_COOLING_WATER_OFFSET = auto()
    """Drying: cooling water offset."""
    ROOM_10_DRYING_COOLING_WATER_OFFSET_HYSTERESIS = auto()
    """Drying: cooling water offset hysteresis."""
    ROOM_10_DEW_POINT_COOLING_THRESHOLD = auto()
    """Dew point threshold temperature when cooling."""
    ROOM_10_DEW_POINT_COOLING_THRESHOLD_HYSTERESIS = auto()
    """Dew point threshold hysteresis when cooling."""
    ROOM_10_HUMIDITY_HIGH_ALARM_LIMIT = auto()
    """Humidity high alarm limit."""
    ROOM_10_TEMP_PRESET = auto()
    """0 = ECO, 1 = COMFORT, 2 = EXTRA COMFORT.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""

    # --- Room 11 (holding registers 110001-110035) ---
    ROOM_11_NAME = auto()
    """Room name. 32 bytes, UTF-8."""
    ROOM_11_MODE = auto()
    """0 = SCHEDULE, 1 = MANUAL.

    In SCHEDULE mode the room temperature setpoint is ignored and the scheduler decides."""
    ROOM_11_MODE_OVERRIDE = auto()
    """0 = NONE, 1 = TEMPORARY, 2 = VACATION_AWAY, 3 = ADJUST.

    While an override is active (> NONE) the room temperature setpoint is not used.
    Write 0 to clear the override."""
    ROOM_11_TEMP_AIR_TARGET = auto()
    """Temperature requested by the user.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""
    ROOM_11_LOCK = auto()
    """Thermostat user-interface access level.

    8 = LOCKED (read only), 16 = HOTEL, 32 = UNLOCKED.
    Only those three values are valid; the device rejects or clamps anything else."""
    ROOM_11_TEMP_STANDBY = auto()
    """Room temperature used while the location is in standby."""
    ROOM_11_TEMP_VACATION = auto()
    """Room temperature used while the location is in vacation mode."""
    ROOM_11_EXCLUDE_FROM_VACATION = auto()
    """Do not allow vacation mode in this room."""
    ROOM_11_ADAPTIVE_ENABLE = auto()
    """Allow adaptive control."""
    ROOM_11_THERMAL_INTEGRATION_HEATING_OFFSET = auto()
    """Thermal integration heating offset."""
    ROOM_11_THERMAL_INTEGRATION_HYSTERESIS = auto()
    """Thermal integration hysteresis."""
    ROOM_11_HUMIDITY_THRESHOLD_HEATING = auto()
    """Humidity threshold for heating."""
    ROOM_11_HUMIDITY_THRESHOLD_COOLING = auto()
    """Humidity threshold for cooling."""
    ROOM_11_HUMIDITY_HYSTERESIS = auto()
    """Humidity hysteresis."""
    ROOM_11_DRYING_COOLING_WATER_OFFSET = auto()
    """Drying: cooling water offset."""
    ROOM_11_DRYING_COOLING_WATER_OFFSET_HYSTERESIS = auto()
    """Drying: cooling water offset hysteresis."""
    ROOM_11_DEW_POINT_COOLING_THRESHOLD = auto()
    """Dew point threshold temperature when cooling."""
    ROOM_11_DEW_POINT_COOLING_THRESHOLD_HYSTERESIS = auto()
    """Dew point threshold hysteresis when cooling."""
    ROOM_11_HUMIDITY_HIGH_ALARM_LIMIT = auto()
    """Humidity high alarm limit."""
    ROOM_11_TEMP_PRESET = auto()
    """0 = ECO, 1 = COMFORT, 2 = EXTRA COMFORT.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""

    # --- Room 12 (holding registers 120001-120035) ---
    ROOM_12_NAME = auto()
    """Room name. 32 bytes, UTF-8."""
    ROOM_12_MODE = auto()
    """0 = SCHEDULE, 1 = MANUAL.

    In SCHEDULE mode the room temperature setpoint is ignored and the scheduler decides."""
    ROOM_12_MODE_OVERRIDE = auto()
    """0 = NONE, 1 = TEMPORARY, 2 = VACATION_AWAY, 3 = ADJUST.

    While an override is active (> NONE) the room temperature setpoint is not used.
    Write 0 to clear the override."""
    ROOM_12_TEMP_AIR_TARGET = auto()
    """Temperature requested by the user.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""
    ROOM_12_LOCK = auto()
    """Thermostat user-interface access level.

    8 = LOCKED (read only), 16 = HOTEL, 32 = UNLOCKED.
    Only those three values are valid; the device rejects or clamps anything else."""
    ROOM_12_TEMP_STANDBY = auto()
    """Room temperature used while the location is in standby."""
    ROOM_12_TEMP_VACATION = auto()
    """Room temperature used while the location is in vacation mode."""
    ROOM_12_EXCLUDE_FROM_VACATION = auto()
    """Do not allow vacation mode in this room."""
    ROOM_12_ADAPTIVE_ENABLE = auto()
    """Allow adaptive control."""
    ROOM_12_THERMAL_INTEGRATION_HEATING_OFFSET = auto()
    """Thermal integration heating offset."""
    ROOM_12_THERMAL_INTEGRATION_HYSTERESIS = auto()
    """Thermal integration hysteresis."""
    ROOM_12_HUMIDITY_THRESHOLD_HEATING = auto()
    """Humidity threshold for heating."""
    ROOM_12_HUMIDITY_THRESHOLD_COOLING = auto()
    """Humidity threshold for cooling."""
    ROOM_12_HUMIDITY_HYSTERESIS = auto()
    """Humidity hysteresis."""
    ROOM_12_DRYING_COOLING_WATER_OFFSET = auto()
    """Drying: cooling water offset."""
    ROOM_12_DRYING_COOLING_WATER_OFFSET_HYSTERESIS = auto()
    """Drying: cooling water offset hysteresis."""
    ROOM_12_DEW_POINT_COOLING_THRESHOLD = auto()
    """Dew point threshold temperature when cooling."""
    ROOM_12_DEW_POINT_COOLING_THRESHOLD_HYSTERESIS = auto()
    """Dew point threshold hysteresis when cooling."""
    ROOM_12_HUMIDITY_HIGH_ALARM_LIMIT = auto()
    """Humidity high alarm limit."""
    ROOM_12_TEMP_PRESET = auto()
    """0 = ECO, 1 = COMFORT, 2 = EXTRA COMFORT.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""

    # --- Room 13 (holding registers 130001-130035) ---
    ROOM_13_NAME = auto()
    """Room name. 32 bytes, UTF-8."""
    ROOM_13_MODE = auto()
    """0 = SCHEDULE, 1 = MANUAL.

    In SCHEDULE mode the room temperature setpoint is ignored and the scheduler decides."""
    ROOM_13_MODE_OVERRIDE = auto()
    """0 = NONE, 1 = TEMPORARY, 2 = VACATION_AWAY, 3 = ADJUST.

    While an override is active (> NONE) the room temperature setpoint is not used.
    Write 0 to clear the override."""
    ROOM_13_TEMP_AIR_TARGET = auto()
    """Temperature requested by the user.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""
    ROOM_13_LOCK = auto()
    """Thermostat user-interface access level.

    8 = LOCKED (read only), 16 = HOTEL, 32 = UNLOCKED.
    Only those three values are valid; the device rejects or clamps anything else."""
    ROOM_13_TEMP_STANDBY = auto()
    """Room temperature used while the location is in standby."""
    ROOM_13_TEMP_VACATION = auto()
    """Room temperature used while the location is in vacation mode."""
    ROOM_13_EXCLUDE_FROM_VACATION = auto()
    """Do not allow vacation mode in this room."""
    ROOM_13_ADAPTIVE_ENABLE = auto()
    """Allow adaptive control."""
    ROOM_13_THERMAL_INTEGRATION_HEATING_OFFSET = auto()
    """Thermal integration heating offset."""
    ROOM_13_THERMAL_INTEGRATION_HYSTERESIS = auto()
    """Thermal integration hysteresis."""
    ROOM_13_HUMIDITY_THRESHOLD_HEATING = auto()
    """Humidity threshold for heating."""
    ROOM_13_HUMIDITY_THRESHOLD_COOLING = auto()
    """Humidity threshold for cooling."""
    ROOM_13_HUMIDITY_HYSTERESIS = auto()
    """Humidity hysteresis."""
    ROOM_13_DRYING_COOLING_WATER_OFFSET = auto()
    """Drying: cooling water offset."""
    ROOM_13_DRYING_COOLING_WATER_OFFSET_HYSTERESIS = auto()
    """Drying: cooling water offset hysteresis."""
    ROOM_13_DEW_POINT_COOLING_THRESHOLD = auto()
    """Dew point threshold temperature when cooling."""
    ROOM_13_DEW_POINT_COOLING_THRESHOLD_HYSTERESIS = auto()
    """Dew point threshold hysteresis when cooling."""
    ROOM_13_HUMIDITY_HIGH_ALARM_LIMIT = auto()
    """Humidity high alarm limit."""
    ROOM_13_TEMP_PRESET = auto()
    """0 = ECO, 1 = COMFORT, 2 = EXTRA COMFORT.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""

    # --- Room 14 (holding registers 140001-140035) ---
    ROOM_14_NAME = auto()
    """Room name. 32 bytes, UTF-8."""
    ROOM_14_MODE = auto()
    """0 = SCHEDULE, 1 = MANUAL.

    In SCHEDULE mode the room temperature setpoint is ignored and the scheduler decides."""
    ROOM_14_MODE_OVERRIDE = auto()
    """0 = NONE, 1 = TEMPORARY, 2 = VACATION_AWAY, 3 = ADJUST.

    While an override is active (> NONE) the room temperature setpoint is not used.
    Write 0 to clear the override."""
    ROOM_14_TEMP_AIR_TARGET = auto()
    """Temperature requested by the user.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""
    ROOM_14_LOCK = auto()
    """Thermostat user-interface access level.

    8 = LOCKED (read only), 16 = HOTEL, 32 = UNLOCKED.
    Only those three values are valid; the device rejects or clamps anything else."""
    ROOM_14_TEMP_STANDBY = auto()
    """Room temperature used while the location is in standby."""
    ROOM_14_TEMP_VACATION = auto()
    """Room temperature used while the location is in vacation mode."""
    ROOM_14_EXCLUDE_FROM_VACATION = auto()
    """Do not allow vacation mode in this room."""
    ROOM_14_ADAPTIVE_ENABLE = auto()
    """Allow adaptive control."""
    ROOM_14_THERMAL_INTEGRATION_HEATING_OFFSET = auto()
    """Thermal integration heating offset."""
    ROOM_14_THERMAL_INTEGRATION_HYSTERESIS = auto()
    """Thermal integration hysteresis."""
    ROOM_14_HUMIDITY_THRESHOLD_HEATING = auto()
    """Humidity threshold for heating."""
    ROOM_14_HUMIDITY_THRESHOLD_COOLING = auto()
    """Humidity threshold for cooling."""
    ROOM_14_HUMIDITY_HYSTERESIS = auto()
    """Humidity hysteresis."""
    ROOM_14_DRYING_COOLING_WATER_OFFSET = auto()
    """Drying: cooling water offset."""
    ROOM_14_DRYING_COOLING_WATER_OFFSET_HYSTERESIS = auto()
    """Drying: cooling water offset hysteresis."""
    ROOM_14_DEW_POINT_COOLING_THRESHOLD = auto()
    """Dew point threshold temperature when cooling."""
    ROOM_14_DEW_POINT_COOLING_THRESHOLD_HYSTERESIS = auto()
    """Dew point threshold hysteresis when cooling."""
    ROOM_14_HUMIDITY_HIGH_ALARM_LIMIT = auto()
    """Humidity high alarm limit."""
    ROOM_14_TEMP_PRESET = auto()
    """0 = ECO, 1 = COMFORT, 2 = EXTRA COMFORT.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""

    # --- Room 15 (holding registers 150001-150035) ---
    ROOM_15_NAME = auto()
    """Room name. 32 bytes, UTF-8."""
    ROOM_15_MODE = auto()
    """0 = SCHEDULE, 1 = MANUAL.

    In SCHEDULE mode the room temperature setpoint is ignored and the scheduler decides."""
    ROOM_15_MODE_OVERRIDE = auto()
    """0 = NONE, 1 = TEMPORARY, 2 = VACATION_AWAY, 3 = ADJUST.

    While an override is active (> NONE) the room temperature setpoint is not used.
    Write 0 to clear the override."""
    ROOM_15_TEMP_AIR_TARGET = auto()
    """Temperature requested by the user.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""
    ROOM_15_LOCK = auto()
    """Thermostat user-interface access level.

    8 = LOCKED (read only), 16 = HOTEL, 32 = UNLOCKED.
    Only those three values are valid; the device rejects or clamps anything else."""
    ROOM_15_TEMP_STANDBY = auto()
    """Room temperature used while the location is in standby."""
    ROOM_15_TEMP_VACATION = auto()
    """Room temperature used while the location is in vacation mode."""
    ROOM_15_EXCLUDE_FROM_VACATION = auto()
    """Do not allow vacation mode in this room."""
    ROOM_15_ADAPTIVE_ENABLE = auto()
    """Allow adaptive control."""
    ROOM_15_THERMAL_INTEGRATION_HEATING_OFFSET = auto()
    """Thermal integration heating offset."""
    ROOM_15_THERMAL_INTEGRATION_HYSTERESIS = auto()
    """Thermal integration hysteresis."""
    ROOM_15_HUMIDITY_THRESHOLD_HEATING = auto()
    """Humidity threshold for heating."""
    ROOM_15_HUMIDITY_THRESHOLD_COOLING = auto()
    """Humidity threshold for cooling."""
    ROOM_15_HUMIDITY_HYSTERESIS = auto()
    """Humidity hysteresis."""
    ROOM_15_DRYING_COOLING_WATER_OFFSET = auto()
    """Drying: cooling water offset."""
    ROOM_15_DRYING_COOLING_WATER_OFFSET_HYSTERESIS = auto()
    """Drying: cooling water offset hysteresis."""
    ROOM_15_DEW_POINT_COOLING_THRESHOLD = auto()
    """Dew point threshold temperature when cooling."""
    ROOM_15_DEW_POINT_COOLING_THRESHOLD_HYSTERESIS = auto()
    """Dew point threshold hysteresis when cooling."""
    ROOM_15_HUMIDITY_HIGH_ALARM_LIMIT = auto()
    """Humidity high alarm limit."""
    ROOM_15_TEMP_PRESET = auto()
    """0 = ECO, 1 = COMFORT, 2 = EXTRA COMFORT.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""

    # --- Room 16 (holding registers 160001-160035) ---
    ROOM_16_NAME = auto()
    """Room name. 32 bytes, UTF-8."""
    ROOM_16_MODE = auto()
    """0 = SCHEDULE, 1 = MANUAL.

    In SCHEDULE mode the room temperature setpoint is ignored and the scheduler decides."""
    ROOM_16_MODE_OVERRIDE = auto()
    """0 = NONE, 1 = TEMPORARY, 2 = VACATION_AWAY, 3 = ADJUST.

    While an override is active (> NONE) the room temperature setpoint is not used.
    Write 0 to clear the override."""
    ROOM_16_TEMP_AIR_TARGET = auto()
    """Temperature requested by the user.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""
    ROOM_16_LOCK = auto()
    """Thermostat user-interface access level.

    8 = LOCKED (read only), 16 = HOTEL, 32 = UNLOCKED.
    Only those three values are valid; the device rejects or clamps anything else."""
    ROOM_16_TEMP_STANDBY = auto()
    """Room temperature used while the location is in standby."""
    ROOM_16_TEMP_VACATION = auto()
    """Room temperature used while the location is in vacation mode."""
    ROOM_16_EXCLUDE_FROM_VACATION = auto()
    """Do not allow vacation mode in this room."""
    ROOM_16_ADAPTIVE_ENABLE = auto()
    """Allow adaptive control."""
    ROOM_16_THERMAL_INTEGRATION_HEATING_OFFSET = auto()
    """Thermal integration heating offset."""
    ROOM_16_THERMAL_INTEGRATION_HYSTERESIS = auto()
    """Thermal integration hysteresis."""
    ROOM_16_HUMIDITY_THRESHOLD_HEATING = auto()
    """Humidity threshold for heating."""
    ROOM_16_HUMIDITY_THRESHOLD_COOLING = auto()
    """Humidity threshold for cooling."""
    ROOM_16_HUMIDITY_HYSTERESIS = auto()
    """Humidity hysteresis."""
    ROOM_16_DRYING_COOLING_WATER_OFFSET = auto()
    """Drying: cooling water offset."""
    ROOM_16_DRYING_COOLING_WATER_OFFSET_HYSTERESIS = auto()
    """Drying: cooling water offset hysteresis."""
    ROOM_16_DEW_POINT_COOLING_THRESHOLD = auto()
    """Dew point threshold temperature when cooling."""
    ROOM_16_DEW_POINT_COOLING_THRESHOLD_HYSTERESIS = auto()
    """Dew point threshold hysteresis when cooling."""
    ROOM_16_HUMIDITY_HIGH_ALARM_LIMIT = auto()
    """Humidity high alarm limit."""
    ROOM_16_TEMP_PRESET = auto()
    """0 = ECO, 1 = COMFORT, 2 = EXTRA COMFORT.

    Not used while room mode = SCHEDULE, during vacation or standby, or while a
    temporary override is active."""
    PERIPHERAL_1_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_2_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_3_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_4_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_5_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_6_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_7_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_8_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_9_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_10_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_11_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_12_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_13_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_14_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_15_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_16_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_17_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_18_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_19_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_20_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_21_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_22_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_23_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_24_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_25_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_26_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_27_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_28_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_29_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_30_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_31_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_32_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_33_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_34_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_35_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_36_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_37_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_38_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_39_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_40_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_41_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_42_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_43_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_44_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_45_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_46_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_47_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_48_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_49_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_50_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_51_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_52_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_53_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_54_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_55_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_56_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_57_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_58_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_59_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_60_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_61_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_62_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_63_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""
    PERIPHERAL_64_NAME = auto()
    """Peripheral name. 32 bytes, UTF-8."""


class WavinSentioBlockingSources:
    """Values of every "blocking source" register.

    The manual states this list is still growing, so treat an unknown value as opaque rather
    than as an error.
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
    """General fault, e.g. missing sensors."""
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


class WavinSentioRoomState:
    """Values of the room state registers (general, radiators, underfloor, integration)."""
    NONE = 0
    """Function not used in this room, or no load detected on any output."""
    IDLE = 1
    HEATING = 2
    COOLING = 3
    BLOCKED_HEATING = 4
    BLOCKED_COOLING = 5


class WavinSentioRoomType:
    NORMAL = 0
    DUMMY = 1
    """No thermostat or sensor installed."""


class WavinSentioRoomLock:
    LOCKED = 8
    """Read only."""
    HOTEL = 16
    UNLOCKED = 32


class WavinPeripheralTypes:
    """Values of the peripheral type register (val_u2)."""
    DHW_201 = 0x0
    """Calefa domestic hot water controller."""
    LCD_200 = 0x4
    """Sentio display."""
    RT_201 = 0x5
    """Wired room thermostat."""
    RT_250 = 0x6
    """Wireless room thermostat."""
    RS_211 = 0x7
    """Wired room sensor."""
    RS_251 = 0x8
    """Wireless room sensor."""
    RT_250IR = 0x9
    """Wireless room thermostat with infrared floor sensor."""
    EU_208_A = 0xA
    """Extension module, 8 actuators."""
    EU_206_VFR = 0xB
    """Extension module, 6 relays."""
    ET_250 = 0xC
    """Wireless outdoor temperature sensor."""
    ET_210 = 0xD
    """Wired outdoor temperature sensor."""
    VH_250 = 0xE
    """Smart radiator thermostat."""
    CCU_208 = 0x11E0
    """The control unit itself. Note this exceeds a byte, hence the u2 register."""


class WavinSentio(ModbusDeviceBase):
    def __init__(self, device_info: ModbusDeviceInfo):
        super().__init__(device_info)

        self._attr_manufacturer = "Wavin"
        self._attr_model_name = "Sentio"
        # The manual caps a single request at 32 registers / 256 bits, well below the
        # Modbus protocol's own 125.
        self._attr_max_request_length = 32
        self._attr_version_keys = VersionInfoKeys(
            datapoint_major=WavinSentioDatapointKey.DATAPOINT_MAJOR,
            datapoint_minor=WavinSentioDatapointKey.DATAPOINT_MINOR,
            hardware_major=WavinSentioDatapointKey.HARDWARE_MAJOR,
            software_major=WavinSentioDatapointKey.SOFTWARE_MAJOR,
            software_minor=WavinSentioDatapointKey.SOFTWARE_MINOR,
            setpoint_major=WavinSentioSetpointKey.SETPOINT_MAJOR,
            setpoint_minor=WavinSentioSetpointKey.SETPOINT_MINOR,
        )

        datapoints = [
            ModbusDatapoint(key=WavinSentioDatapointKey.DATAPOINT_MAJOR, read_address=1, max=ValueLimit.UINT8_MAXERR),
            ModbusDatapoint(key=WavinSentioDatapointKey.DATAPOINT_MINOR, read_address=2, max=ValueLimit.UINT8_MAXERR),
            ModbusDatapoint(key=WavinSentioDatapointKey.DEVICE_TYPE, read_address=10, max=ValueLimit.UINT8_MAXERR),
            ModbusDatapoint(key=WavinSentioDatapointKey.HARDWARE_MAJOR, read_address=11, max=ValueLimit.UINT8_MAXERR),
            ModbusDatapoint(key=WavinSentioDatapointKey.SOFTWARE_MAJOR, read_address=12, max=ValueLimit.UINT8_MAXERR),
            ModbusDatapoint(key=WavinSentioDatapointKey.SOFTWARE_MINOR, read_address=13, max=ValueLimit.UINT8_MAXERR),
            ModbusDatapoint(key=WavinSentioDatapointKey.SERIAL_NUMBER_PREFIX, read_address=14, max=ValueLimit.UINT16_MAXERR),
            ModbusDatapoint(key=WavinSentioDatapointKey.SERIAL_NUMBER, read_address=15, read_length=2, max=ValueLimit.UINT32_MAXERR),
            ModbusDatapoint(key=WavinSentioDatapointKey.HEATING_COOLING_MODE, read_address=20, max=ValueLimit.UINT8_MAXERR),
        ]
        setpoints = [
            ModbusSetpoint(key=WavinSentioSetpointKey.SETPOINT_MAJOR, read_address=1, max=ValueLimit.UINT8_MAXERR),
            ModbusSetpoint(key=WavinSentioSetpointKey.SETPOINT_MINOR, read_address=2, max=ValueLimit.UINT8_MAXERR),
            # Read at startup so the client knows whether writes will be accepted at all.
            ModbusSetpoint(key=WavinSentioSetpointKey.MODBUS_MODE, read_address=5, max=ValueLimit.UINT8_MAXERR, extra={"read": Read.STARTUP_ALWAYS}),
            # Write-only per the manual, so it carries no read flag - it can never hold a value.
            ModbusSetpoint(key=WavinSentioSetpointKey.MODBUS_PASSWORD, write_address=6, max=ValueLimit.UINT16_MAXERR),
            ModbusSetpoint(key=WavinSentioSetpointKey.LOCATION_NAME, read_address=10, read_length=16, write_address=10, write_length=16, value_type=ModbusValueType.UTF8),
            ModbusSetpoint(key=WavinSentioSetpointKey.STANDBY_ENABLE, read_address=26, write_address=26, max=1),
            ModbusSetpoint(key=WavinSentioSetpointKey.VACATION_ENABLE, read_address=27, write_address=27, max=1),
            ModbusSetpoint(key=WavinSentioSetpointKey.DATETIME_UNIX, read_address=28, read_length=2, write_address=28, write_length=2, max=ValueLimit.UINT32_MAXERR),
            ModbusSetpoint(key=WavinSentioSetpointKey.DAYLIGHT_SAVING_ENABLE, read_address=30, write_address=30, max=1),
            ModbusSetpoint(key=WavinSentioSetpointKey.TEMP_OUTDOOR_COOLING_MIN, read_address=31, write_address=31, divider=100, signed=True, max=ValueLimit.INT16_MAXERR),
            ModbusSetpoint(key=WavinSentioSetpointKey.TEMP_OUTDOOR_HEATING_MAX, read_address=32, write_address=32, divider=100, signed=True, max=ValueLimit.INT16_MAXERR),
            ModbusSetpoint(key=WavinSentioSetpointKey.UPDATE_MODE, read_address=33, write_address=33, max=2),
            ModbusSetpoint(key=WavinSentioSetpointKey.HEATING_COOLING_MODE_BMS_OVERRIDE, read_address=34, write_address=34, max=ValueLimit.UINT8_MAXERR),
            ModbusSetpoint(key=WavinSentioSetpointKey.TIMEZONE, read_address=35, write_address=35, max=ValueLimit.UINT16_MAXERR),
        ]

        for room in range(1, ROOM_COUNT + 1):
            base = room_base(room)

            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_TEMP_AIR_TARGET"], read_address=base + 1, divider=100, signed=True, max=ValueLimit.INT16_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_STATE"], read_address=base + 2, max=ValueLimit.UINT8_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_BLOCKING_SOURCE"], read_address=base + 3, max=ValueLimit.UINT8_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_TEMP_AIR_CURRENT"], read_address=base + 4, divider=100, signed=True, max=ValueLimit.INT16_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_TEMP_FLOOR_CURRENT"], read_address=base + 5, divider=100, signed=True, max=ValueLimit.INT16_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_HUMIDITY_CURRENT"], read_address=base + 6, divider=100, signed=True, max=ValueLimit.INT16_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_DEW_POINT_CURRENT"], read_address=base + 7, divider=100, signed=True, max=ValueLimit.INT16_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_ASSOCIATED_RADIATORS"], read_address=base + 11, max=ValueLimit.UINT8_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_ASSOCIATED_UFHC"], read_address=base + 12, max=ValueLimit.UINT8_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_ASSOCIATED_DRYING"], read_address=base + 14, max=ValueLimit.UINT8_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_ASSOCIATED_THERMAL_INTEGRATION"], read_address=base + 15, max=ValueLimit.UINT8_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_ASSOCIATED_VENTILATION"], read_address=base + 16, max=ValueLimit.UINT8_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_AIR_STATE"], read_address=base + 17, max=ValueLimit.UINT8_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_FLOOR_STATE"], read_address=base + 18, max=ValueLimit.UINT8_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_DRYING_STATE"], read_address=base + 19, max=ValueLimit.UINT8_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_THERMAL_INTEGRATION_STATE"], read_address=base + 20, max=ValueLimit.UINT8_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_VENTILATION_STATE"], read_address=base + 21, max=ValueLimit.UINT8_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_BLOCKING_SOURCE_RADIATORS"], read_address=base + 22, max=ValueLimit.UINT8_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_BLOCKING_SOURCE_UFHC"], read_address=base + 23, max=ValueLimit.UINT8_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_BLOCKING_SOURCE_DRYING"], read_address=base + 24, max=ValueLimit.UINT8_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_BLOCKING_SOURCE_THERMAL_INTEGRATION"], read_address=base + 25, max=ValueLimit.UINT8_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_BLOCKING_SOURCE_VENTILATION"], read_address=base + 26, max=ValueLimit.UINT8_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_TYPE"], read_address=base + 27, max=ValueLimit.UINT8_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"ROOM_{room}_ASSOCIATED_HEATING_SOURCE"], read_address=base + 28, max=ValueLimit.UINT8_MAXERR))

            setpoints.append(ModbusSetpoint(key=WavinSentioSetpointKey[f"ROOM_{room}_NAME"], read_address=base + 1, read_length=16, write_address=base + 1, write_length=16, value_type=ModbusValueType.UTF8))
            setpoints.append(ModbusSetpoint(key=WavinSentioSetpointKey[f"ROOM_{room}_MODE"], read_address=base + 17, write_address=base + 17, max=1))
            setpoints.append(ModbusSetpoint(key=WavinSentioSetpointKey[f"ROOM_{room}_MODE_OVERRIDE"], read_address=base + 18, write_address=base + 18, max=3))
            setpoints.append(ModbusSetpoint(key=WavinSentioSetpointKey[f"ROOM_{room}_TEMP_AIR_TARGET"], read_address=base + 19, write_address=base + 19, divider=100, signed=True, max=ValueLimit.INT16_MAXERR))
            setpoints.append(ModbusSetpoint(key=WavinSentioSetpointKey[f"ROOM_{room}_LOCK"], read_address=base + 20, write_address=base + 20, min=8, max=32))
            setpoints.append(ModbusSetpoint(key=WavinSentioSetpointKey[f"ROOM_{room}_TEMP_STANDBY"], read_address=base + 21, write_address=base + 21, divider=100, signed=True, max=ValueLimit.INT16_MAXERR))
            setpoints.append(ModbusSetpoint(key=WavinSentioSetpointKey[f"ROOM_{room}_TEMP_VACATION"], read_address=base + 22, write_address=base + 22, divider=100, signed=True, max=ValueLimit.INT16_MAXERR))
            setpoints.append(ModbusSetpoint(key=WavinSentioSetpointKey[f"ROOM_{room}_EXCLUDE_FROM_VACATION"], read_address=base + 23, write_address=base + 23, max=1))
            setpoints.append(ModbusSetpoint(key=WavinSentioSetpointKey[f"ROOM_{room}_ADAPTIVE_ENABLE"], read_address=base + 24, write_address=base + 24, max=1))
            setpoints.append(ModbusSetpoint(key=WavinSentioSetpointKey[f"ROOM_{room}_THERMAL_INTEGRATION_HEATING_OFFSET"], read_address=base + 25, write_address=base + 25, divider=100, signed=True, max=ValueLimit.INT16_MAXERR))
            setpoints.append(ModbusSetpoint(key=WavinSentioSetpointKey[f"ROOM_{room}_THERMAL_INTEGRATION_HYSTERESIS"], read_address=base + 26, write_address=base + 26, divider=100, signed=True, max=ValueLimit.INT16_MAXERR))
            setpoints.append(ModbusSetpoint(key=WavinSentioSetpointKey[f"ROOM_{room}_HUMIDITY_THRESHOLD_HEATING"], read_address=base + 27, write_address=base + 27, divider=100, signed=True, max=ValueLimit.INT16_MAXERR))
            setpoints.append(ModbusSetpoint(key=WavinSentioSetpointKey[f"ROOM_{room}_HUMIDITY_THRESHOLD_COOLING"], read_address=base + 28, write_address=base + 28, divider=100, signed=True, max=ValueLimit.INT16_MAXERR))
            setpoints.append(ModbusSetpoint(key=WavinSentioSetpointKey[f"ROOM_{room}_HUMIDITY_HYSTERESIS"], read_address=base + 29, write_address=base + 29, divider=100, signed=True, max=ValueLimit.INT16_MAXERR))
            setpoints.append(ModbusSetpoint(key=WavinSentioSetpointKey[f"ROOM_{room}_DRYING_COOLING_WATER_OFFSET"], read_address=base + 30, write_address=base + 30, divider=100, signed=True, max=ValueLimit.INT16_MAXERR))
            setpoints.append(ModbusSetpoint(key=WavinSentioSetpointKey[f"ROOM_{room}_DRYING_COOLING_WATER_OFFSET_HYSTERESIS"], read_address=base + 31, write_address=base + 31, divider=100, signed=True, max=ValueLimit.INT16_MAXERR))
            setpoints.append(ModbusSetpoint(key=WavinSentioSetpointKey[f"ROOM_{room}_DEW_POINT_COOLING_THRESHOLD"], read_address=base + 32, write_address=base + 32, divider=100, signed=True, max=ValueLimit.INT16_MAXERR))
            setpoints.append(ModbusSetpoint(key=WavinSentioSetpointKey[f"ROOM_{room}_DEW_POINT_COOLING_THRESHOLD_HYSTERESIS"], read_address=base + 33, write_address=base + 33, divider=100, signed=True, max=ValueLimit.INT16_MAXERR))
            setpoints.append(ModbusSetpoint(key=WavinSentioSetpointKey[f"ROOM_{room}_HUMIDITY_HIGH_ALARM_LIMIT"], read_address=base + 34, write_address=base + 34, divider=100, signed=True, max=ValueLimit.INT16_MAXERR))
            setpoints.append(ModbusSetpoint(key=WavinSentioSetpointKey[f"ROOM_{room}_TEMP_PRESET"], read_address=base + 35, write_address=base + 35, max=2))

        for peripheral in range(1, PERIPHERAL_COUNT + 1):
            base = peripheral_base(peripheral)
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"PERIPHERAL_{peripheral}_TYPE"], read_address=base + 1, max=ValueLimit.UINT16_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"PERIPHERAL_{peripheral}_SN"], read_address=base + 2, read_length=2, max=ValueLimit.UINT32_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"PERIPHERAL_{peripheral}_OWNER"], read_address=base + 4, max=ValueLimit.UINT16_MAXERR))
            datapoints.append(ModbusDatapoint(key=WavinSentioDatapointKey[f"PERIPHERAL_{peripheral}_SIGNAL_STRENGTH"], read_address=base + 5, max=ValueLimit.UINT8_MAXERR))
            setpoints.append(ModbusSetpoint(key=WavinSentioSetpointKey[f"PERIPHERAL_{peripheral}_NAME"], read_address=base + 1, read_length=16, value_type=ModbusValueType.UTF8))

        self._attr_datapoints = datapoints
        self._attr_setpoints = setpoints

    def _version_changed(self, old_version: VersionInfo, new_version: VersionInfo) -> None:
        """
        Check the device's address space version once it is actually known.

        This cannot be done while the model is being selected: at that point no register has
        been read yet and the version is still all zeros, so the check would always fail.
        """
        if new_version.datapoint_major == 0 and new_version.datapoint_minor == 0:
            return  # nothing read yet
        supported = (new_version.datapoint_major > ADDRESS_SPACE_MAJOR_REQUIRED
                     or (new_version.datapoint_major == ADDRESS_SPACE_MAJOR_REQUIRED
                         and new_version.datapoint_minor >= ADDRESS_SPACE_MINOR_REQUIRED))
        if not supported:
            _LOGGER.warning(
                "Sentio address space %d.%d is older than the %d.%d this register map was "
                "written against. Some registers may be unavailable; update the control unit.",
                new_version.datapoint_major, new_version.datapoint_minor,
                ADDRESS_SPACE_MAJOR_REQUIRED, ADDRESS_SPACE_MINOR_REQUIRED)

