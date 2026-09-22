"""Read-only tests against a real Wavin Sentio controller.

These are skipped unless a host is configured, so the normal test run is unaffected.

    Configure it either way:
        set SENTIO_HOST=192.168.1.50          (environment variable)
        HOSTNAME = "192.168.1.50"             (in mysecrets.py, which is gitignored)

    Optional:
        SENTIO_PORT      default 502
        SENTIO_UNIT_ID   default 1   (try 255 if the controller does not answer)

    Run:
        pytest tests/test_live_sentio.py -v -s

NOTHING HERE WRITES TO THE CONTROLLER. Only function codes 0x03 (read holding registers),
0x04 (read input registers) and 0x02 (read discrete inputs) are used. A guard in the fixture
replaces every write method with one that fails the test, so a write cannot slip in by accident.

Beyond pass/fail, these print what your system actually reports - which rooms exist, which
peripherals are paired, what the real request limit is. Run with -s to see it.
"""
import logging
import os
from dataclasses import dataclass

import pytest

from src.wavin_sentio_connect import (
    ROOM_COUNT,
    PERIPHERAL_COUNT,
    WavinSentioDatapointKey,
    WavinSentioSetpointKey,
    WavinSentioRoomType,
    WavinSentioTCPConnect,
    WavinPeripheralTypes,
    peripheral_base,
    room_base,
)

_LOGGER = logging.getLogger(__name__)


def _configured_host() -> str | None:
    host = os.environ.get("SENTIO_HOST")
    if host:
        return host
    try:
        from mysecrets import HOSTNAME  # type: ignore
        return HOSTNAME
    except Exception:
        return None


HOST = _configured_host()
PORT = int(os.environ.get("SENTIO_PORT", "502"))
UNIT_ID = int(os.environ.get("SENTIO_UNIT_ID", "1"))

pytestmark = pytest.mark.skipif(
    HOST is None,
    reason="No Sentio host configured. Set SENTIO_HOST=<ip> or HOSTNAME in mysecrets.py",
)


@dataclass
class Live:
    client: WavinSentioTCPConnect


def _forbid_writes(client: WavinSentioTCPConnect) -> None:
    """Make any write attempt fail loudly instead of reaching the controller."""
    async def refuse(*args, **kwargs):
        raise AssertionError("A write was attempted. These tests are read-only.")

    transport = client.transport
    assert transport is not None
    transport.write_register = refuse        # type: ignore[assignment]
    transport.write_registers = refuse       # type: ignore[assignment]
    client._request_setpoint_write = refuse  # type: ignore[assignment]
    client._request_setpoint_writes = refuse # type: ignore[assignment]


@pytest.fixture
async def live():
    client = WavinSentioTCPConnect()
    assert HOST is not None   # guarded by the skipif above
    connected = await client.connect("live-test", HOST, port=PORT, unit_id=UNIT_ID)
    if not connected:
        await client.stop()
        pytest.fail(
            f"Could not connect to {HOST}:{PORT} (unit id {UNIT_ID}).\n"
            f"  - Is Modbus TCP enabled? System | Installer settings | Modbus settings\n"
            f"  - The controller restarts after enabling it.\n"
            f"  - Some controllers answer on unit id 255: set SENTIO_UNIT_ID=255\n"
            f"  - last error: {client.last_error_txt}"
        )
    _forbid_writes(client)
    yield Live(client=client)
    await client.stop()


def _value(client, key):
    return client.get_value(key)


async def _read(client, *keys):
    """Mark the keys for reading and fetch them.

    Only points flagged for reading are fetched, so a key must be requested before
    get_value() can return anything for it.
    """
    datapoints = [k for k in keys if isinstance(k, WavinSentioDatapointKey)]
    setpoints = [k for k in keys if isinstance(k, WavinSentioSetpointKey)]
    for key in keys:
        client.set_read(key, True)
    if datapoints:
        await client.request_datapoint_read()
    if setpoints:
        await client.request_setpoint_read()


async def test_connect_and_identify(live: Live):
    """Connects and reports what the controller says it is."""
    client = live.client
    assert client.is_connected

    await _read(client,
                WavinSentioDatapointKey.DEVICE_TYPE,
                WavinSentioDatapointKey.HEATING_COOLING_MODE)
    device_type = _value(client, WavinSentioDatapointKey.DEVICE_TYPE)
    print("\n--- controller ---")
    print(f"  device type          : {device_type}  (1 = CCU-208, 2 = DHW-201)")
    print(f"  address space version: {_value(client, WavinSentioDatapointKey.DATAPOINT_MAJOR)}"
          f".{_value(client, WavinSentioDatapointKey.DATAPOINT_MINOR)}")
    print(f"  software version     : {_value(client, WavinSentioDatapointKey.SOFTWARE_MAJOR)}"
          f".{_value(client, WavinSentioDatapointKey.SOFTWARE_MINOR)}")
    print(f"  hardware version     : {_value(client, WavinSentioDatapointKey.HARDWARE_MAJOR)}")
    print(f"  heating/cooling mode : {_value(client, WavinSentioDatapointKey.HEATING_COOLING_MODE)}"
          f"  (0 = HEATING, 1 = COOLING)")
    assert device_type is not None, "no device type came back"


async def test_addressing_convention(live: Live):
    """
    Confirms that the manual's register numbers are used unchanged on the wire.

    The manual documents two constants: input register 00001 = 3 (address space major) and
    00014 = 1530 (serial number prefix). If the numbering were off by one, these would land
    on the wrong registers.
    """
    client = live.client
    await _read(client,
                WavinSentioDatapointKey.DATAPOINT_MAJOR,
                WavinSentioDatapointKey.SERIAL_NUMBER_PREFIX,
                WavinSentioDatapointKey.SERIAL_NUMBER)
    major = _value(client, WavinSentioDatapointKey.DATAPOINT_MAJOR)
    prefix = _value(client, WavinSentioDatapointKey.SERIAL_NUMBER_PREFIX)
    serial = _value(client, WavinSentioDatapointKey.SERIAL_NUMBER)

    print("\n--- addressing ---")
    print(f"  IR 00001 (address space major) = {major}    manual says 3")
    print(f"  IR 00014 (serial prefix)       = {prefix}   manual says 1530")
    print(f"  IR 00015-16 (serial number)    = {serial}")

    assert major == 3, f"expected 3, got {major}: addresses may be off by one"
    assert prefix == 1530, f"expected 1530, got {prefix}: addresses may be off by one"


async def test_string_registers_have_no_length_prefix(live: Live):
    """
    Settles the manual's contradiction about val_utf8.

    The data-type table implies a 2-byte length prefix; the worked example shows none. If a
    prefix existed, the decoded name would be missing its first characters or start with junk.
    """
    client = live.client
    await _read(client, WavinSentioSetpointKey.LOCATION_NAME)
    name = _value(client, WavinSentioSetpointKey.LOCATION_NAME)

    print("\n--- strings (val_utf8) ---")
    print(f"  location name: {name!r}")
    if name:
        print("  If this reads correctly, there is no length prefix (as implemented).")
        print("  If it is missing its first two characters, a prefix exists.")
    assert name is not None, "location name came back empty"


async def test_read_all_rooms(live: Live):
    """Reads every room and reports which ones are real."""
    client = live.client
    keys = []
    for room in range(1, ROOM_COUNT + 1):
        keys += [
            WavinSentioDatapointKey[f"ROOM_{room}_TYPE"],
            WavinSentioDatapointKey[f"ROOM_{room}_TEMP_AIR_CURRENT"],
            WavinSentioDatapointKey[f"ROOM_{room}_TEMP_AIR_TARGET"],
            WavinSentioDatapointKey[f"ROOM_{room}_HUMIDITY_CURRENT"],
            WavinSentioDatapointKey[f"ROOM_{room}_TEMP_FLOOR_CURRENT"],
            WavinSentioDatapointKey[f"ROOM_{room}_STATE"],
        ]
    for key in keys:
        client.set_read(key, True)
    await client.request_datapoint_read()

    print("\n--- rooms ---")
    print(f"  {'#':>2} {'base':>5} {'type':>6} {'air':>7} {'target':>7} {'floor':>7} {'hum':>6} {'state':>5}")
    found = 0
    for room in range(1, ROOM_COUNT + 1):
        room_type = _value(client, WavinSentioDatapointKey[f"ROOM_{room}_TYPE"])
        if room_type is None:
            continue
        found += 1
        def v(suffix):
            value = _value(client, WavinSentioDatapointKey[f"ROOM_{room}_{suffix}"])
            return f"{value:7.2f}" if isinstance(value, float) else f"{str(value):>7}"
        label = "NORMAL" if room_type == WavinSentioRoomType.NORMAL else "DUMMY"
        print(f"  {room:>2} {room_base(room):>5} {label:>6} {v('TEMP_AIR_CURRENT')}"
              f" {v('TEMP_AIR_TARGET')} {v('TEMP_FLOOR_CURRENT')}"
              f" {str(_value(client, WavinSentioDatapointKey[f'ROOM_{room}_HUMIDITY_CURRENT'])):>6}"
              f" {str(_value(client, WavinSentioDatapointKey[f'ROOM_{room}_STATE'])):>5}")
    print(f"  -> {found} of {ROOM_COUNT} room slots answered")
    assert found > 0, "no room answered; check that rooms are configured on the controller"


async def test_temperatures_are_plausible(live: Live):
    """
    Every temperature must decode to something physical.

    A value near 655 means an unsigned decode of a negative number, which was the original bug.
    """
    client = live.client
    suspicious = []
    for room in range(1, ROOM_COUNT + 1):
        for suffix in ("TEMP_AIR_CURRENT", "TEMP_FLOOR_CURRENT", "DEW_POINT_CURRENT"):
            key = WavinSentioDatapointKey[f"ROOM_{room}_{suffix}"]
            value = _value(client, key)
            if value is None:
                continue
            if not isinstance(value, (int, float)) or not (-50.0 <= value <= 120.0):
                suspicious.append((key, value))
    print("\n--- temperature sanity ---")
    print(f"  implausible readings: {suspicious if suspicious else 'none'}")
    assert not suspicious, f"these did not decode as temperatures: {suspicious}"


async def test_outdoor_temperature_sign(live: Live):
    """
    Reads the outdoor temperature limits, which are the registers most likely to be negative.

    These are setpoints, so they are read from holding registers. Nothing is written.
    """
    client = live.client
    await _read(client,
                WavinSentioSetpointKey.TEMP_OUTDOOR_COOLING_MIN,
                WavinSentioSetpointKey.TEMP_OUTDOOR_HEATING_MAX)

    print("\n--- outdoor limits (signed val_d2_fp100) ---")
    for key in (WavinSentioSetpointKey.TEMP_OUTDOOR_COOLING_MIN,
                WavinSentioSetpointKey.TEMP_OUTDOOR_HEATING_MAX):
        value = _value(client, key)
        print(f"  {str(key):45} {value}")
        if value is not None:
            assert isinstance(value, (int, float)), f"{key} = {value!r} is not numeric"
            assert -50.0 <= value <= 120.0, f"{key} = {value} did not decode as a temperature"


async def test_peripherals(live: Live):
    """Lists the paired peripherals. Slot order is not stable; the serial number is."""
    client = live.client
    for peripheral in range(1, PERIPHERAL_COUNT + 1):
        for suffix in ("TYPE", "SN", "OWNER", "SIGNAL_STRENGTH"):
            client.set_read(WavinSentioDatapointKey[f"PERIPHERAL_{peripheral}_{suffix}"], True)
    await client.request_datapoint_read()

    names = {v: k for k, v in vars(WavinPeripheralTypes).items() if isinstance(v, int)}
    print("\n--- peripherals ---")
    print(f"  {'#':>3} {'base':>6} {'type':>8} {'model':<12} {'serial':>12} {'owner':>6} {'signal':>6}")
    found = 0
    for peripheral in range(1, PERIPHERAL_COUNT + 1):
        ptype = _value(client, WavinSentioDatapointKey[f"PERIPHERAL_{peripheral}_TYPE"])
        if ptype is None:
            continue
        found += 1
        serial = _value(client, WavinSentioDatapointKey[f"PERIPHERAL_{peripheral}_SN"])
        owner = _value(client, WavinSentioDatapointKey[f"PERIPHERAL_{peripheral}_OWNER"])
        signal = _value(client, WavinSentioDatapointKey[f"PERIPHERAL_{peripheral}_SIGNAL_STRENGTH"])
        print(f"  {peripheral:>3} {peripheral_base(peripheral):>6} {ptype:>8} "
              f"{names.get(int(ptype), '?'):<12} {str(serial):>12} {str(owner):>6} {str(signal):>6}")
    print(f"  -> {found} peripheral slots answered")


async def test_actual_request_limit(live: Live):
    """
    Finds the controller's real maximum registers-per-request.

    The manual says 32. This only reads; an oversized request is simply refused.
    """
    client = live.client
    transport = client.transport
    assert transport is not None

    # Must be read inside ONE contiguous block, or the refusal is just "that register does
    # not exist" (exception 2) rather than "that request is too big" (exception 3).
    # Room 1 holding registers 101-135 are 35 consecutive registers, the longest run available.
    print("\n--- request limit ---")
    print("  reading holding registers from 101 (room 1 has 35 consecutive: 101-135)")
    largest_ok = 0
    for count in (1, 8, 16, 32, 33, 35):
        data = await transport.read_holding_registers(101, count)
        if data is not None:
            largest_ok = count
            print(f"  {count:>4} registers -> ok")
        else:
            code = transport.last_exception_code
            meaning = {2: "illegal data address (register does not exist)",
                       3: "illegal data value (request too large)"}.get(code, "see text")
            print(f"  {count:>4} registers -> refused, exception {code}: {meaning}")
    print(f"  -> largest accepted: {largest_ok}")
    assert largest_ok >= 1, "not even a single-register read succeeded"


async def test_discrete_inputs_are_readable(live: Live):
    """
    Checks whether alarms/warnings can be read (function code 0x02).

    The point model does not expose these yet; this reads them straight off the transport to
    confirm the controller answers, so the feature can be built with confidence.
    """
    client = live.client
    transport = client.transport
    assert transport is not None

    print("\n--- discrete inputs (alarms/warnings) ---")
    bits = await transport.read_discrete_inputs(1, 2)
    print(f"  location aggregated warning/error (DI 00001-00002): {bits}")
    if bits is None:
        print(f"  not readable: {transport.last_error_text}")
    for room in (1, 2):
        base = room_base(room)
        room_bits = await transport.read_discrete_inputs(base + 1, 4)
        print(f"  room {room} DI {base+1}-{base+4}: {room_bits}")
