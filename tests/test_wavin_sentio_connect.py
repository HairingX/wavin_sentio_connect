from dataclasses import dataclass
from typing import Any
import asyncio
import logging
from modbus_event_connect import ( # type: ignore
    MODBUS_VALUE_TYPES,
    ModbusPointKey,
    )
import pytest

from credentials import Credentials
from src.wavin_sentio_connect import (
    WavinSentioTCPConnect,
    WavinSentioDatapointKey,
    WavinSentioSetpointKey
)

_LOGGER = logging.getLogger(__name__)

@dataclass
class TestData:
    client: WavinSentioTCPConnect
    data = dict[str, Any]()
    credentials: Credentials
    
@pytest.fixture
async def testdata():
    #setup
    credentials = Credentials(["hostname"])
    client = WavinSentioTCPConnect()
    await client.connect("DEVICE_ID", credentials.hostname)
    # 
    yield TestData(client=client, credentials=credentials)
    #teardown
    client.stop()

async def test_connect(testdata: TestData):
    client = testdata.client
    assert client.is_connected
    await client.request_initial_data()
    datapoints = client._attr_adapter._get_loaded_model().get_initial_datapoints_for_read() # type: ignore
    for point in datapoints:
        _LOGGER.debug(f"{point.key}: {client.get_value(point.key)}")
        assert client.get_value(point.key) is not None
    setpoints = client._attr_adapter._get_loaded_model().get_initial_setpoints_for_read() # type: ignore
    for point in setpoints:
        _LOGGER.debug(f"{point.key}: {client.get_value(point.key)}")
        assert client.get_value(point.key) is not None
    
    assert client.get_value(WavinSentioDatapointKey.DATAPOINT_MAJOR) is not None

# async def test_request_setpoint_value_type_bigint(testdata: TestData):
#     key = WavinSentioSetpointKey.LOCATION_NAME
#     client = testdata.client
#     event = asyncio.Event()
#     def callback(key: ModbusPointKey, oldval:MODBUS_VALUE_TYPES|None, newval:MODBUS_VALUE_TYPES|None):
#         _LOGGER.debug(f"{key}: {oldval if oldval is not None else 'None'} -> {newval if newval is not None else 'None'}")
#         event.set()
#     client.subscribe(key, callback)
#     await client.request_setpoint_read()
#     assert await asyncio.wait_for(event.wait(), 5)
#     value = client.get_value(key)
#     assert value is not None
#     assert isinstance(value, int)
#     assert value > ValueLimit.INT16_MAX, f"Expected value greater than {ValueLimit.INT16_MAX}, got {value}"
#     _LOGGER.debug(f"fromtimestamp(UTC): {datetime.fromtimestamp(value, UTC)}")
    
# async def test_request_setpoint_value_type_int(testdata: TestData):
#    pass # no need, MAJOR_VERSION is an int, and is already tested in test_connect

# async def test_request_point_value_type_float(testdata: TestData):
#     key = ModbusTestDatapointKey.TEMPERATURE
#     client = testdata.client
#     event = asyncio.Event()
#     def callback(key: ModbusPointKey, oldval:MODBUS_VALUE_TYPES|None, newval:MODBUS_VALUE_TYPES|None):
#         _LOGGER.debug(f"{key}: {oldval if oldval is not None else 'None'} -> {newval if newval is not None else 'None'}")
#         event.set()
#     client.subscribe(key, callback)
#     await client.request_datapoint_read()
#     assert await asyncio.wait_for(event.wait(), 5)
#     value = client.get_value(key)
#     assert value is not None
#     assert isinstance(value, float), f"Expected float, got {type(value)} (value = {value})"
    
async def test_setpoint_location_name(testdata: TestData):
    key = WavinSentioSetpointKey.LOCATION_NAME
    client = testdata.client
    event = asyncio.Event()
    def callback(key: ModbusPointKey, oldval:MODBUS_VALUE_TYPES|None, newval:MODBUS_VALUE_TYPES|None):
        _LOGGER.debug(f"{key}: {oldval if oldval is not None else 'None'} -> {newval if newval is not None else 'None'}")
        event.set()
    client.subscribe(key, callback)
    await client.request_setpoint_read()
    assert await asyncio.wait_for(event.wait(), 5)
    value = client.get_value(key)
    assert value is not None
    assert isinstance(value, str)
    _LOGGER.debug(f"Location name: {value}")
    
class EventValue:
    value: MODBUS_VALUE_TYPES|None = None
    event: asyncio.Event
    def __init__(self):
        self.event = asyncio.Event()
    def set_value(self, value: MODBUS_VALUE_TYPES|None):
        self.value = value
        self.event.set()

async def test_all_points(testdata: TestData):
    client = testdata.client
    values = dict[ModbusPointKey, EventValue]()
    def callback(key: ModbusPointKey, oldval:MODBUS_VALUE_TYPES|None, newval:MODBUS_VALUE_TYPES|None):
        values[key].set_value(newval)
    for key in WavinSentioDatapointKey:
        values[key] = EventValue()
        client.subscribe(key, callback)
    for key in WavinSentioSetpointKey:
        values[key] = EventValue()
        client.subscribe(key, callback)
    await client.request_setpoint_read()
    await client.request_datapoint_read()
    try:
        await asyncio.wait_for(asyncio.gather(*[item.event.wait() for item in values.values()]), 5)
    except asyncio.TimeoutError:
        _LOGGER.error("Timeout, not all values received")
    _LOGGER.debug("Values:")
    for key, item in values.items():
        _LOGGER.debug(f"{key}: {item.value if item.value is not None else 'None'}")
# # async def test_request_datapoint_data_invalid_address(testdata: TestData):
# #     client = testdata.client
# #     event1 = asyncio.Event()
# #     event2 = asyncio.Event()
# #     events = {ModbusTestDatapointKey.INVALID: event1, ModbusTestDatapointKey.TEMPERATURE: event2}
# #     def callback(key: ModbusPointKey, oldval:MODBUS_VALUE_TYPES|None, newval:MODBUS_VALUE_TYPES|None):
# #         _LOGGER.debug(f"{key}: {oldval if oldval is not None else 'None'} -> {newval if newval is not None else 'None'}")
# #         if key in events: events[key].set()
# #     client.subscribe(ModbusTestDatapointKey.INVALID, callback)
# #     client.subscribe(ModbusTestDatapointKey.TEMPERATURE, callback)
# #     await client.request_datapoint_data()
# #     await asyncio.wait_for(asyncio.gather(event1.wait(), event2.wait()), 15)
# #     assert client.get_value(ModbusTestDatapointKey.INVALID) is None
# #     assert client.get_value(ModbusTestDatapointKey.TEMPERATURE) is not None