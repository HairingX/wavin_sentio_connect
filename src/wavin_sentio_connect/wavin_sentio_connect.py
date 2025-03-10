import logging
from collections.abc import Callable
from modbus_event_connect import (  # type: ignore
    ModbusDevice,
    ModbusDeviceInfo,
    ModbusTCPEventConnect,
    ModbusDeviceAdapter,
 )
from .devices import *

_LOGGER = logging.getLogger(__name__)

MAJOR_REQUIRED = 3
MINOR_REQUIRED = 2

class WavinSentioDeviceAdapter(ModbusDeviceAdapter):

    def _translate_to_model(self, device_info: ModbusDeviceInfo) -> Callable[[ModbusDeviceInfo], ModbusDevice]|None:
        if (device_info.version.datapoint_major < MAJOR_REQUIRED or 
            (device_info.version.datapoint_major == MAJOR_REQUIRED and device_info.version.datapoint_minor < MINOR_REQUIRED)):
            _LOGGER.error(f"Update your device firmware. Version {MAJOR_REQUIRED}.{MINOR_REQUIRED} required. Current version: {device_info.version.datapoint_major}.{device_info.version.datapoint_minor}")
        return WavinSentio

class WavinSentioTCPConnect(ModbusTCPEventConnect):
   _attr_adapter = WavinSentioDeviceAdapter()