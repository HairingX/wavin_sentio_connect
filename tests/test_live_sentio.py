"""Read-only tests against a real Wavin Sentio controller.

    Configure it either way:
        set SENTIO_HOST=<device-ip>          (environment variable)
        SENTIO_HOST = "<device-ip>"          (in mysecrets.py, which is gitignored)

    Optional:
        SENTIO_PORT      default 502
        SENTIO_UNIT_ID   default 1   (try 255 if the controller does not answer)

    Run:
        pytest tests/test_live_sentio.py -v -s

NOTHING HERE WRITES TO THE CONTROLLER: the client is created read-only.
"""
from collections import Counter
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any

import pytest
import pytest_asyncio
from modbus_event_connect import Client, DataValue, Key, Quality, ReadOnlyError, Unit
from modbus_event_connect.modbus import FunctionCode, ModbusDevice, ModbusTcpConnection, Request

from conftest import live_or_skip, live_setting
from wavin_sentio_connect import (
    SENTIO,
    LocationPointKey,
    RoomPointKey,
    peripherals,
    room_key,
    rooms,
)

HOST = live_setting("SENTIO_HOST")
PORT = int(live_setting("SENTIO_PORT") or "502")
UNIT_ID = int(live_setting("SENTIO_UNIT_ID") or "1")

pytestmark = [
    pytest.mark.asyncio(loop_scope="module"),
    *live_or_skip("Sentio", SENTIO_HOST=HOST),
]


@dataclass
class Live:
    client: Client
    connection: ModbusTcpConnection


@pytest_asyncio.fixture(scope="module", loop_scope="module")  # pyright: ignore[reportUntypedFunctionDecorator, reportUnknownMemberType]
async def live() -> AsyncGenerator[Live, None]:
    assert HOST is not None   # guarded by the skip above
    connection = ModbusTcpConnection(HOST, PORT)
    client = Client(ModbusDevice(connection, UNIT_ID, owns_connection=True), SENTIO, read_only=True)
    try:
        await client.connect()
    except Exception as err:
        pytest.fail(
            f"Could not connect to the controller at the configured host (unit id {UNIT_ID}): {err!r}\n"
            f"  - Is Modbus TCP enabled? System | Installer settings | Modbus settings\n"
            f"  - The controller restarts after enabling it.\n"
            f"  - Some controllers answer on unit id 255: set SENTIO_UNIT_ID=255")
    yield Live(client=client, connection=connection)
    await client.disconnect()


def _good[T](client: Client, key: Key[T]) -> T | None:
    current = client.value(key)
    assert current is not None and current.quality is Quality.GOOD, f"{key}: {current}"
    return current.value


# ================================================================================ safety

async def test_a_write_is_refused_before_it_reaches_the_controller(live: Live) -> None:
    """The guard itself must work, or every other test here would be a risk."""
    key = next(k for k in live.client.points if live.client.can_write(k))
    with pytest.raises(ReadOnlyError):
        await live.client.write(key, 0)


# ============================================================================ the picture

async def test_connects_and_identifies(live: Live) -> None:
    client = live.client
    print("\n--- controller ---")
    keys: list[Key[Any]] = [
        LocationPointKey.DEVICE_TYPE, LocationPointKey.DATAPOINT_MAJOR, LocationPointKey.DATAPOINT_MINOR,
        LocationPointKey.SOFTWARE_MAJOR, LocationPointKey.SOFTWARE_MINOR, LocationPointKey.HARDWARE_MAJOR,
        LocationPointKey.HEATING_COOLING_MODE, LocationPointKey.MODBUS_MODE]
    for key in keys:
        print(f"  {key:22} {client.value(key)}")
    assert _good(client, LocationPointKey.DEVICE_TYPE) is not None


async def test_the_manuals_numbers_are_the_addresses(live: Live) -> None:
    """The manual documents two constants. Off by one, and these would be other registers."""
    assert _good(live.client, LocationPointKey.DATAPOINT_MAJOR) == 3
    assert _good(live.client, LocationPointKey.SERIAL_NUMBER_PREFIX) == 1530


async def test_text_decodes_without_a_length_prefix(live: Live) -> None:
    name = _good(live.client, LocationPointKey.LOCATION_NAME)
    print(f"\n  location name: {name!r}")
    assert isinstance(name, str)


async def test_the_installed_rooms_are_found(live: Live) -> None:
    client = live.client
    found = rooms(client)
    print("\n--- rooms ---")
    for room in found:
        air = client.value(room_key(room.number, RoomPointKey.TEMP_AIR_CURRENT))
        print(f"  {room.number:>2} {room.name!r:24} {'dummy' if room.is_dummy else 'normal':6} "
              f"air={air.value if air else None} ({air.quality.name if air else '-'})")
    assert found, "no room answered; check that rooms are configured on the controller"
    assert len(client.instances("room")) == len(found)


async def test_every_temperature_decodes_as_a_temperature(live: Live) -> None:
    """A value near 655 would be an unsigned decode of a negative number; 327.67 is the
    no-reading sentinel."""
    client = live.client
    suspicious: list[tuple[str, object]] = []
    for key, point in client.points.items():
        current = client.value(key)
        if point.unit is Unit.CELSIUS and current is not None and current.quality is Quality.GOOD:
            if not isinstance(current.value, (int, float)) or not -50.0 <= current.value <= 120.0:
                suspicious.append((key, current.value))
    assert not suspicious, f"these did not decode as temperatures: {suspicious}"


async def test_every_value_is_good_or_says_why_not(live: Live) -> None:
    """A read that failed would be STALE. After a clean scan, nothing should be."""
    client = live.client
    qualities: Counter[str] = Counter()
    for key in client.points:
        current = client.value(key)
        if current is not None:
            qualities[current.quality.name] += 1
    print(f"\n--- qualities over {len(client.points)} keys --- {dict(qualities)}")
    assert qualities[Quality.STALE.name] == 0


async def test_the_paired_peripherals_are_found(live: Live) -> None:
    print("\n--- peripherals ---")
    found = peripherals(live.client)
    for p in found:
        print(f"  slot {p.slot:>2} {p.model:<10} sn={p.serial_number} owner={p.owner} name={p.name!r}")
    assert [p.slot for p in found] == list(live.client.instances("peripheral"))
    assert all(p.type is not None for p in found), "a paired slot reported no type"


async def test_every_subscriber_hears_its_value(live: Live) -> None:
    client = live.client
    heard: dict[str, DataValue[Any]] = {}

    def listen(key: str, old: DataValue[Any] | None, new: DataValue[Any]) -> None:
        heard[key] = new
    unsubscribers = [client.subscribe(key, listen) for key in client.points if client.can_read(key)]
    for unsubscribe in unsubscribers:
        unsubscribe()
    readable = [k for k in client.points if client.can_read(k)]
    print(f"\n  {len(heard)} of {len(readable)} readable keys delivered a value on subscribe")
    assert set(heard) == set(readable), "a readable key had no value after the scan"


# ============================================================= raw probes, read-only codes

async def test_the_real_request_limit(live: Live) -> None:
    """The manual says 32 registers; 101-135 is the longest run, read as one block to get 0x03
    rather than 0x02 on overflow."""
    print("\n--- request limit ---")
    largest = 0
    for count in (1, 8, 16, 32, 33, 35):
        response = await live.connection.request(
            Request(UNIT_ID, FunctionCode.READ_HOLDING_REGISTERS, 101, count=count))
        verdict = "ok" if response.ok else f"refused, exception {response.exception_code}"
        print(f"  {count:>3} registers -> {verdict}")
        if response.ok:
            largest = count
    print(f"  -> largest accepted: {largest}")
    assert largest >= 1


async def test_the_alarm_inputs_answer(live: Live) -> None:
    """Alarms are discrete inputs (0x02). Not in the model yet; this confirms they are readable."""
    response = await live.connection.request(
        Request(UNIT_ID, FunctionCode.READ_DISCRETE_INPUTS, 1, count=2))
    print(f"\n  location aggregated warning/error (DI 00001-00002): {response}")
    assert response.ok or response.exception_code in (0x02, 0x03)
