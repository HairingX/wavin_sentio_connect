from enum import auto
from modbus_event_connect import ( # type: ignore
        ModbusDatapoint, 
        ModbusDatapointKey, 
        ModbusDeviceBase, 
        ModbusDeviceInfo, 
        ModbusSetpoint, 
        ModbusSetpointKey,
        VersionInfoKeys,
        Read,
        ValueLimits,
        ModbusValueTypes,
        ) 

class WavinSentioDatapointKey(ModbusDatapointKey):
    """
    Datapoints that can be read.
    """
    DATAPOINT_MAJOR = auto()
    """Major version incremented on incompatible changes."""
    DATAPOINT_MINOR = auto()
    """Minor version incremented on compatible changes."""
    DEVICE_TYPE = auto()
    """1 - CCU-208, 2 - DHW-201 (Calefa)"""
    HARDWARE_MAJOR = auto()
    """Hardware version."""
    SOFTWARE_MAJOR = auto()
    """Major version incremented on incompatible changes."""
    SOFTWARE_MINOR = auto()
    """Minor version incremented on compatible changes."""
    HEATING_COOLING_MODE = auto()
    """0 - HEATING, 1 - COOLING"""
    
    # Room 1
    ROOM_1_TYPE = auto()
    """0 = Normal, 2 = Dummy (ignored)"""
    ROOM_1_STATE = auto()
    """1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED HEATING, 5 = BLOCKED COOLING"""
    ROOM_1_BLOCKING_SOURCE = auto()
    """Blocking source for the room, see WavinSentioBlockingSources for valid values."""
    ROOM_1_TEMP_AIR_TARGET = auto()
    """Target temperature for the room."""
    ROOM_1_TEMP_AIR_CURRENT = auto()
    """Current temperature in the room."""
    ROOM_1_TEMP_FLOOR_TARGET = auto()
    """Target floor temperature for the room."""
    ROOM_1_TEMP_FLOOR_CURRENT = auto()
    """Current floor temperature in the room."""
    ROOM_1_HUMIDITY_CURRENT = auto()
    """Current humidity in the room."""
    ROOM_1_DEW_POINT_CURRENT = auto()
    """Current calculated dew point in the room."""
    ROOM_1_AIR_STATE = auto()
    """1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED HEATING, 5 = BLOCKED COOLING"""
    ROOM_1_FLOOR_STATE = auto()
    """1 = IDLE, 2 = HEATING, 3 = COOLING, 4 = BLOCKED HEATING, 5 = BLOCKED COOLING"""
    
    PERIPHERAL_1_TYPE = auto()
    """ Peripheral type - Sensor, Termostat, .. (product number)."""
    PERIPHERAL_1_SN = auto()
    """Serial number."""
    PERIPHERAL_1_OWNER = auto()
    """ 
    000 - Location 
    001 - Room 1 
    ... 
    016 - Room 16.
    NOTE: Object address in this modbus table is used as owner_id
    """
    PERIPHERAL_1_SIGNAL_STRENGTH = auto()
    """Signal strength."""
    PERIPHERAL_2_TYPE = auto()
    PERIPHERAL_2_SN = auto()
    PERIPHERAL_2_OWNER = auto()
    PERIPHERAL_2_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_3_TYPE = auto()
    PERIPHERAL_3_SN = auto()
    PERIPHERAL_3_OWNER = auto()
    PERIPHERAL_3_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_4_TYPE = auto()
    PERIPHERAL_4_SN = auto()
    PERIPHERAL_4_OWNER = auto()
    PERIPHERAL_4_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_5_TYPE = auto()
    PERIPHERAL_5_SN = auto()
    PERIPHERAL_5_OWNER = auto()
    PERIPHERAL_5_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_6_TYPE = auto()
    PERIPHERAL_6_SN = auto()
    PERIPHERAL_6_OWNER = auto()
    PERIPHERAL_6_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_7_TYPE = auto()
    PERIPHERAL_7_SN = auto()
    PERIPHERAL_7_OWNER = auto()
    PERIPHERAL_7_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_8_TYPE = auto()
    PERIPHERAL_8_SN = auto()
    PERIPHERAL_8_OWNER = auto()
    PERIPHERAL_8_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_9_TYPE = auto()
    PERIPHERAL_9_SN = auto()
    PERIPHERAL_9_OWNER = auto()
    PERIPHERAL_9_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_10_TYPE = auto()
    PERIPHERAL_10_SN = auto()
    PERIPHERAL_10_OWNER = auto()
    PERIPHERAL_10_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_11_TYPE = auto()
    PERIPHERAL_11_SN = auto()
    PERIPHERAL_11_OWNER = auto()
    PERIPHERAL_11_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_12_TYPE = auto()
    PERIPHERAL_12_SN = auto()
    PERIPHERAL_12_OWNER = auto()
    PERIPHERAL_12_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_13_TYPE = auto()
    PERIPHERAL_13_SN = auto()
    PERIPHERAL_13_OWNER = auto()
    PERIPHERAL_13_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_14_TYPE = auto()
    PERIPHERAL_14_SN = auto()
    PERIPHERAL_14_OWNER = auto()
    PERIPHERAL_14_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_15_TYPE = auto()
    PERIPHERAL_15_SN = auto()
    PERIPHERAL_15_OWNER = auto()
    PERIPHERAL_15_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_16_TYPE = auto()
    PERIPHERAL_16_SN = auto()
    PERIPHERAL_16_OWNER = auto()
    PERIPHERAL_16_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_17_TYPE = auto()
    PERIPHERAL_17_SN = auto()
    PERIPHERAL_17_OWNER = auto()
    PERIPHERAL_17_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_18_TYPE = auto()
    PERIPHERAL_18_SN = auto()
    PERIPHERAL_18_OWNER = auto()
    PERIPHERAL_18_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_19_TYPE = auto()
    PERIPHERAL_19_SN = auto()
    PERIPHERAL_19_OWNER = auto()
    PERIPHERAL_19_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_20_TYPE = auto()
    PERIPHERAL_20_SN = auto()
    PERIPHERAL_20_OWNER = auto()
    PERIPHERAL_20_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_21_TYPE = auto()
    PERIPHERAL_21_SN = auto()
    PERIPHERAL_21_OWNER = auto()
    PERIPHERAL_21_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_22_TYPE = auto()
    PERIPHERAL_22_SN = auto()
    PERIPHERAL_22_OWNER = auto()
    PERIPHERAL_22_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_23_TYPE = auto()
    PERIPHERAL_23_SN = auto()
    PERIPHERAL_23_OWNER = auto()
    PERIPHERAL_23_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_24_TYPE = auto()
    PERIPHERAL_24_SN = auto()
    PERIPHERAL_24_OWNER = auto()
    PERIPHERAL_24_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_25_TYPE = auto()
    PERIPHERAL_25_SN = auto()
    PERIPHERAL_25_OWNER = auto()
    PERIPHERAL_25_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_26_TYPE = auto()
    PERIPHERAL_26_SN = auto()
    PERIPHERAL_26_OWNER = auto()
    PERIPHERAL_26_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_27_TYPE = auto()
    PERIPHERAL_27_SN = auto()
    PERIPHERAL_27_OWNER = auto()
    PERIPHERAL_27_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_28_TYPE = auto()
    PERIPHERAL_28_SN = auto()
    PERIPHERAL_28_OWNER = auto()
    PERIPHERAL_28_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_29_TYPE = auto()
    PERIPHERAL_29_SN = auto()
    PERIPHERAL_29_OWNER = auto()
    PERIPHERAL_29_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_30_TYPE = auto()
    PERIPHERAL_30_SN = auto()
    PERIPHERAL_30_OWNER = auto()
    PERIPHERAL_30_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_31_TYPE = auto()
    PERIPHERAL_31_SN = auto()
    PERIPHERAL_31_OWNER = auto()
    PERIPHERAL_31_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_32_TYPE = auto()
    PERIPHERAL_32_SN = auto()
    PERIPHERAL_32_OWNER = auto()
    PERIPHERAL_32_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_33_TYPE = auto()
    PERIPHERAL_33_SN = auto()
    PERIPHERAL_33_OWNER = auto()
    PERIPHERAL_33_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_34_TYPE = auto()
    PERIPHERAL_34_SN = auto()
    PERIPHERAL_34_OWNER = auto()
    PERIPHERAL_34_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_35_TYPE = auto()
    PERIPHERAL_35_SN = auto()
    PERIPHERAL_35_OWNER = auto()
    PERIPHERAL_35_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_36_TYPE = auto()
    PERIPHERAL_36_SN = auto()
    PERIPHERAL_36_OWNER = auto()
    PERIPHERAL_36_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_37_TYPE = auto()
    PERIPHERAL_37_SN = auto()
    PERIPHERAL_37_OWNER = auto()
    PERIPHERAL_37_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_38_TYPE = auto()
    PERIPHERAL_38_SN = auto()
    PERIPHERAL_38_OWNER = auto()
    PERIPHERAL_38_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_39_TYPE = auto()
    PERIPHERAL_39_SN = auto()
    PERIPHERAL_39_OWNER = auto()
    PERIPHERAL_39_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_40_TYPE = auto()
    PERIPHERAL_40_SN = auto()
    PERIPHERAL_40_OWNER = auto()
    PERIPHERAL_40_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_41_TYPE = auto()
    PERIPHERAL_41_SN = auto()
    PERIPHERAL_41_OWNER = auto()
    PERIPHERAL_41_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_42_TYPE = auto()
    PERIPHERAL_42_SN = auto()
    PERIPHERAL_42_OWNER = auto()
    PERIPHERAL_42_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_43_TYPE = auto()
    PERIPHERAL_43_SN = auto()
    PERIPHERAL_43_OWNER = auto()
    PERIPHERAL_43_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_44_TYPE = auto()
    PERIPHERAL_44_SN = auto()
    PERIPHERAL_44_OWNER = auto()
    PERIPHERAL_44_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_45_TYPE = auto()
    PERIPHERAL_45_SN = auto()
    PERIPHERAL_45_OWNER = auto()
    PERIPHERAL_45_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_46_TYPE = auto()
    PERIPHERAL_46_SN = auto()
    PERIPHERAL_46_OWNER = auto()
    PERIPHERAL_46_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_47_TYPE = auto()
    PERIPHERAL_47_SN = auto()
    PERIPHERAL_47_OWNER = auto()
    PERIPHERAL_47_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_48_TYPE = auto()
    PERIPHERAL_48_SN = auto()
    PERIPHERAL_48_OWNER = auto()
    PERIPHERAL_48_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_49_TYPE = auto()
    PERIPHERAL_49_SN = auto()
    PERIPHERAL_49_OWNER = auto()
    PERIPHERAL_49_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_50_TYPE = auto()
    PERIPHERAL_50_SN = auto()
    PERIPHERAL_50_OWNER = auto()
    PERIPHERAL_50_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_51_TYPE = auto()
    PERIPHERAL_51_SN = auto()
    PERIPHERAL_51_OWNER = auto()
    PERIPHERAL_51_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_52_TYPE = auto()
    PERIPHERAL_52_SN = auto()
    PERIPHERAL_52_OWNER = auto()
    PERIPHERAL_52_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_53_TYPE = auto()
    PERIPHERAL_53_SN = auto()
    PERIPHERAL_53_OWNER = auto()
    PERIPHERAL_53_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_54_TYPE = auto()
    PERIPHERAL_54_SN = auto()
    PERIPHERAL_54_OWNER = auto()
    PERIPHERAL_54_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_55_TYPE = auto()
    PERIPHERAL_55_SN = auto()
    PERIPHERAL_55_OWNER = auto()
    PERIPHERAL_55_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_56_TYPE = auto()
    PERIPHERAL_56_SN = auto()
    PERIPHERAL_56_OWNER = auto()
    PERIPHERAL_56_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_57_TYPE = auto()
    PERIPHERAL_57_SN = auto()
    PERIPHERAL_57_OWNER = auto()
    PERIPHERAL_57_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_58_TYPE = auto()
    PERIPHERAL_58_SN = auto()
    PERIPHERAL_58_OWNER = auto()
    PERIPHERAL_58_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_59_TYPE = auto()
    PERIPHERAL_59_SN = auto()
    PERIPHERAL_59_OWNER = auto()
    PERIPHERAL_59_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_60_TYPE = auto()
    PERIPHERAL_60_SN = auto()
    PERIPHERAL_60_OWNER = auto()
    PERIPHERAL_60_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_61_TYPE = auto()
    PERIPHERAL_61_SN = auto()
    PERIPHERAL_61_OWNER = auto()
    PERIPHERAL_61_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_62_TYPE = auto()
    PERIPHERAL_62_SN = auto()
    PERIPHERAL_62_OWNER = auto()
    PERIPHERAL_62_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_63_TYPE = auto()
    PERIPHERAL_63_SN = auto()
    PERIPHERAL_63_OWNER = auto()
    PERIPHERAL_63_SIGNAL_STRENGTH = auto()
    
    PERIPHERAL_64_TYPE = auto()
    PERIPHERAL_64_SN = auto()
    PERIPHERAL_64_OWNER = auto()
    PERIPHERAL_64_SIGNAL_STRENGTH = auto()
    

class WavinSentioSetpointKey(ModbusSetpointKey):
    """
    Setpoints that can be read/written.
    """
    SETPOINT_MAJOR = auto()
    """Major version incremented on incompatible changes."""
    SETPOINT_MINOR = auto()
    """Minor version incremented on compatible changes."""
    MODBUS_MODE = auto()
    """
    - 0 = DISABLED
    - 1 = READ_ONLY
    - 2 = READ_WRITE
    - 3 = WRITE_WITH_PASSWORD
    """
    MODBUS_PASSWORD = auto()
    """Password for write access."""
    LOCATION_NAME = auto()
    """Location name."""
    STANDBY_ENABLE = auto()
    """Standby mode ON/OFF."""
    VACATION_ENABLE = auto()
    """Vacation mode ON/OFF."""
    DATETIME_UNIX = auto()
    """Date and time."""
    DAYLIGHT_SAVING_ENABLE = auto()
    """Daylight saving time."""
    TEMP_OUTDOOR_COOLING_MIN = auto()
    """Cooling is blocked, when outdoor temperature is lower than this value."""
    TEMP_OUTDOOR_HEATING_MAX = auto()
    """Heating is blocked, when outdoor temperature is higher than this value."""
    
    
    ROOM_1_NAME = auto()
    """Room name."""
    ROOM_1_MODE = auto()
    """0 = SCHEDULED, 1 = MANUAL.
    
    In SCHEDULE mode, the “Room temperature setpoint” is not used and the room
temperature is controlled by scheduler."""
    ROOM_1_MODE_OVERRIDE = auto()
    """0 NONE,
    1 TEMPORARY,
    2 VACATION_AWAY,
    3 ADJUST

    In override mode (> NONE), the “Room temperaturesetpoint” is not used. The requested
    temperature is corrected by user via room thermostat or mobile application.
    You can disable the override mode by setting this value to 0 (NONE)
    """
    ROOM_1_TEMP_AIR_TARGET = auto()
    """Temperature requested by user.
This values is not used when
 - Room mode = SCHEDULE (Scheduler temperature is used)
 - Location.Vacation = ON (Vacation temperature is used)
 - Location.Standby = ON (Standby temperature is used)
 - Temporary mode is activated (User defined temperature is used)"""
    ROOM_1_LOCK = auto()
    """Set the lock status for the thermostat.
    8 = LOCKED, 16 = HOTEL, 32 = UNLOCKED"""
    ROOM_1_TEMP_STANDBY = auto()
    """Standby temperature for the room."""
    ROOM_1_TEMP_VACATION = auto()
    """Vacation temperature for the room."""
    ROOM_1_EXCLUDE_FROM_VACATION = auto()
    """Exclude room from vacation mode."""
    ROOM_1_ADAPTIVE_ENABLE = auto()
    """Adaptive control ON/OFF."""
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
    ROOM_1_TEMP_PRESET = auto()
    """0 - ECO,
    1 - COMFORT,
    2 - EXTRA COMFORT
    
    Temperature preset requested by user.
    This value is not used when 
    - Room mode = SCHEDULE (Scheduler temperature is used)
    - Location.Vacation = ON (Vacation temperature is used)
    - Location.Standby = ON (Standby temperature is used)
    - Temporary mode is activated (User defined temperature is used)"""
    
    PERIPHERAL_1_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_2_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_3_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_4_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_5_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_6_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_7_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_8_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_9_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_10_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_11_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_12_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_13_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_14_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_15_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_16_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_17_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_18_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_19_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_20_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_21_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_22_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_23_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_24_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_25_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_26_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_27_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_28_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_29_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_30_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_31_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_32_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_33_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_34_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_35_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_36_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_37_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_38_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_39_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_40_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_41_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_42_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_43_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_44_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_45_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_46_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_47_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_48_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_49_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_50_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_51_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_52_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_53_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_54_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_55_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_56_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_57_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_58_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_59_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_60_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_61_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_62_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_63_NAME = auto()
    """Peripheral name."""
    PERIPHERAL_64_NAME = auto()
    """Peripheral name."""
    
class WavinSentioBlockingSources:
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
    ROOM_WITH_NO_TEMPERATURE = 23

class WavinPeripheralTypes:
    CALEFA_CONTROLLER = 0
    SENTIO_DISPLAY = 4
    SENTIO_WIRED_ROOM_THERMOSTAT = 5
    SENTIO_WIRELESS_ROOM_THERMOSTAT = 6
    SENTIO_WIRED_ROOM_SENSOR = 7
    SENTIO_WIRELESS_ROOM_SENSOR = 8
    SENTIO_WIRELESS_ROOM_THERMOSTAT_IR = 9
    SENTIO_EXTENSION_MODULE_8_ACTUATORS = 10
    SENTIO_EXTENSION_MODULE_6_RELAYS = 11
    SENTIO_WIRELESS_OUTDOOR_TEMP_SENSOR = 12
    SENTIO_WIRED_OUTDOOR_TEMP_SENSOR = 13
    SENTIO_SMART_RADIATOR_THERMOSTAT = 14
    
    
    
DEFAULT_EXTRAS = {
    # SentioModbusDatapointKey.MODBUS_MODE: {"unit_of_measurement": UOM.UNKNOWN},
    # SentioModbusSetpointKey.MODBUS_PASSWORD: {"unit_of_measurement": UOM.UNKNOWN},
}

class WavinSentio(ModbusDeviceBase):
    def __init__(self, device_info: ModbusDeviceInfo):
        super().__init__(device_info)

        self._attr_manufacturer="Wavin"
        self._attr_model_name="Sentio"
        self._attr_version_keys = VersionInfoKeys(datapoint_major=WavinSentioDatapointKey.DATAPOINT_MAJOR, datapoint_minor=WavinSentioDatapointKey.DATAPOINT_MINOR)
        self._attr_default_extras = DEFAULT_EXTRAS
        self._attr_datapoints = [
            ModbusDatapoint(key=WavinSentioDatapointKey.DATAPOINT_MAJOR, read_address=1, max=ValueLimits.UINT8_MAXERR),
            ModbusDatapoint(key=WavinSentioDatapointKey.DATAPOINT_MINOR, read_address=2, max=ValueLimits.UINT8_MAXERR),
            ModbusDatapoint(key=WavinSentioDatapointKey.DEVICE_TYPE,    read_address=10, max=ValueLimits.UINT8_MAXERR), #, extra={"read": Read.STARTUP_ALWAYS} when we want to support attached CALEFA
            ModbusDatapoint(key=WavinSentioDatapointKey.HARDWARE_MAJOR, read_address=11, max=ValueLimits.UINT8_MAXERR),
            ModbusDatapoint(key=WavinSentioDatapointKey.SOFTWARE_MAJOR, read_address=12, max=ValueLimits.UINT8_MAXERR),
            ModbusDatapoint(key=WavinSentioDatapointKey.SOFTWARE_MINOR, read_address=13, max=ValueLimits.UINT8_MAXERR),
            ModbusDatapoint(key=WavinSentioDatapointKey.HEATING_COOLING_MODE, read_address=20, max=ValueLimits.UINT8_MAXERR),
        ]
        self._attr_setpoints = [
            ModbusSetpoint(key=WavinSentioSetpointKey.SETPOINT_MAJOR, read_address=1, max=ValueLimits.UINT8_MAXERR),
            ModbusSetpoint(key=WavinSentioSetpointKey.SETPOINT_MINOR, read_address=2, max=ValueLimits.UINT8_MAXERR),
            ModbusSetpoint(key=WavinSentioSetpointKey.MODBUS_MODE,    read_address=5, max=ValueLimits.UINT8_MAXERR, extra={"read": Read.STARTUP_ALWAYS}), # important to know how to react to writes
            ModbusSetpoint(key=WavinSentioSetpointKey.MODBUS_PASSWORD, write_address=6, extra={"read": Read.STARTUP_ALWAYS}),
            ModbusSetpoint(key=WavinSentioSetpointKey.LOCATION_NAME, read_address=10, read_length=16, write_address=10, write_length=16, value_type=ModbusValueTypes.UTF8),
            ModbusSetpoint(key=WavinSentioSetpointKey.STANDBY_ENABLE, read_address=26, write_address=26, max=1),
            ModbusSetpoint(key=WavinSentioSetpointKey.VACATION_ENABLE, read_address=27, write_address=27, max=1),
            ModbusSetpoint(key=WavinSentioSetpointKey.DATETIME_UNIX, read_address=28, read_length=2, write_address=28, write_length=2, max=ValueLimits.UINT32_MAXERR),
            ModbusSetpoint(key=WavinSentioSetpointKey.DAYLIGHT_SAVING_ENABLE, read_address=30, write_address=30, max=1),
            ModbusSetpoint(key=WavinSentioSetpointKey.TEMP_OUTDOOR_COOLING_MIN, read_address=31, write_address=31, divider=100, max=ValueLimits.INT16_MAXERR),
            ModbusSetpoint(key=WavinSentioSetpointKey.TEMP_OUTDOOR_HEATING_MAX, read_address=32, write_address=32, divider=100, max=ValueLimits.INT16_MAXERR),
            
            ModbusSetpoint(key=WavinSentioSetpointKey.ROOM_1_NAME, read_address=101, read_length=16, write_address=101, write_length=16, value_type=ModbusValueTypes.UTF8),
            ModbusSetpoint(key=WavinSentioSetpointKey.ROOM_1_MODE, read_address=117, write_address=117, max=1),
            ModbusSetpoint(key=WavinSentioSetpointKey.ROOM_1_MODE_OVERRIDE, read_address=118, write_address=118, max=3),
            ModbusSetpoint(key=WavinSentioSetpointKey.ROOM_1_TEMP_AIR_TARGET, read_address=119, write_address=119, divider=100, max=ValueLimits.INT16_MAXERR),
            ModbusSetpoint(key=WavinSentioSetpointKey.ROOM_1_LOCK, read_address=120, write_address=120, max=32),
            ModbusSetpoint(key=WavinSentioSetpointKey.ROOM_1_TEMP_STANDBY, read_address=121, write_address=121, divider=100, max=ValueLimits.INT16_MAXERR),
            ModbusSetpoint(key=WavinSentioSetpointKey.ROOM_1_TEMP_VACATION, read_address=122, write_address=122, divider=100, max=ValueLimits.INT16_MAXERR),
            ModbusSetpoint(key=WavinSentioSetpointKey.ROOM_1_EXCLUDE_FROM_VACATION, read_address=123, write_address=123, max=1),
            ModbusSetpoint(key=WavinSentioSetpointKey.ROOM_1_ADAPTIVE_ENABLE, read_address=124, write_address=124, max=1),
            ModbusSetpoint(key=WavinSentioSetpointKey.ROOM_1_THERMAL_INTEGRATION_HEATING_OFFSET, read_address=125, write_address=125, divider=100, max=ValueLimits.INT16_MAXERR),
            ModbusSetpoint(key=WavinSentioSetpointKey.ROOM_1_THERMAL_INTEGRATION_HYSTERESIS, read_address=126, write_address=126, divider=100, max=ValueLimits.INT16_MAXERR),
            ModbusSetpoint(key=WavinSentioSetpointKey.ROOM_1_HUMIDITY_THRESHOLD_HEATING, read_address=127, write_address=127, divider=100, max=ValueLimits.INT16_MAXERR),
            ModbusSetpoint(key=WavinSentioSetpointKey.ROOM_1_HUMIDITY_THRESHOLD_COOLING, read_address=128, write_address=128, divider=100, max=ValueLimits.INT16_MAXERR),
            ModbusSetpoint(key=WavinSentioSetpointKey.ROOM_1_HUMIDITY_HYSTERESIS, read_address=129, write_address=129, divider=100, max=ValueLimits.INT16_MAXERR),
        ]
        
        # for key in WavinSentioDatapointKey:
        #     if key.find("peripheral") != -1:
        #         parts = key.split("_")
        #         no = int(parts[2]) #point_periphral_NO_xxx
        #         peripheral_start = 51000 + no*100
        #         if key.endswith("_type"): self._attr_datapoints.append(ModbusDatapoint(key=key, read_address=peripheral_start+1, max=ValueLimits.UINT16_MAXERR))
        #         if key.endswith("_sn"): self._attr_datapoints.append(ModbusDatapoint(key=key, read_address=peripheral_start+2, read_length=2, max=ValueLimits.UINT32_MAXERR))
        #         if key.endswith("_owner"): self._attr_datapoints.append(ModbusDatapoint(key=key, read_address=peripheral_start+4, max=ValueLimits.UINT16_MAXERR))
        #         if key.endswith("_signal_strength"): self._attr_datapoints.append(ModbusDatapoint(key=key, read_address=peripheral_start+5, max=ValueLimits.UINT8_MAXERR))
        # for key in WavinSentioSetpointKey:
        #     if key.find("peripheral") != -1:
        #         parts = key.split("_")
        #         no = int(parts[2]) #xpoint_periphral_NO_xxx
        #         peripheral_start = 51000 + no*100
        #         if key.endswith("_name"): self._attr_setpoints.append(ModbusSetpoint(key=key, read_address=peripheral_start+1, read_length=16, value_type=ModbusValueTypes.UTF8))

        #place config modifiers here