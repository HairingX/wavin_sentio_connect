"""The Sentio model and client against a simulated controller: rooms 1 and 3 (3 a dummy),
peripherals 1 and 2, nothing else - exactly what the scan must find."""
import asyncio
import logging

import pytest
from modbus_event_connect import (
    Client,
    DataType,
    DataTypeKind,
    InvalidValueError,
    Labels,
    PollRate,
    Quality,
    ReadOnlyError,
    Unit,
)
from modbus_event_connect.modbus import FunctionCode
from modbus_event_connect.testing import (
    FakeClock,
    SimulatedModbusDevice,
    SimulatedModbusGateway,
    assert_models_valid,
    resolve,
)

from src.wavin_sentio_connect import (
    SENTIO,
    UNITS,
    LocationPointKey,
    PeripheralPointKey,
    PeripheralType,
    RoomPointKey,
    create_client_on,
    peripheral_key,
    peripherals,
    room_key,
    rooms,
)
from src.wavin_sentio_connect import _model as sentio_model
from src.wavin_sentio_connect._model import PERIPHERAL_COUNT, ROOM_COUNT, peripheral_base, room_base


def _text(text: str, registers: int = 16) -> list[int]:
    raw = text.encode().ljust(registers * 2, b"\x00")
    return [int.from_bytes(raw[i:i + 2], "big") for i in range(0, len(raw), 2)]


def _installation(*, address_space: tuple[int, int] = (3, 2)) -> SimulatedModbusDevice:
    alarms: dict[int, int] = {1: 0, 2: 0}
    inputs: dict[int, int] = {1: address_space[0], 2: address_space[1], 10: 1, 11: 1, 12: 1,
                              13: 0, 14: 1530, 15: 0, 16: 1234, 20: 0}
    holding: dict[int, int] = {1: 3, 2: 2, 5: 1, 26: 0, 27: 0, 28: 0, 29: 0, 30: 1,
                               31: 0xFE0C, 32: 2000, 33: 0, 34: 0, 35: 60}
    holding.update(dict(enumerate(_text("Home"), start=10)))
    for n, (name, air, dummy) in {1: ("Kitchen", 2150, 0), 3: ("Hall", 0x7FFF, 1)}.items():
        base = room_base(n)
        for offset in (1, 2, 3, 4, 5, 6, 7, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,
                       24, 25, 26, 27, 28):
            inputs[base + offset] = 0
        inputs[base + 1], inputs[base + 4], inputs[base + 27] = 2100, air, dummy
        holding.update(dict(enumerate(_text(name), start=base + 1)))
        for offset in range(17, 36):
            holding[base + offset] = 0
        holding[base + 19], holding[base + 20] = 2100, 32
        alarms.update({base + bit: 0 for bit in (1, 2, 3, 4)})
    for slot, (kind, serial, owner) in {1: (PeripheralType.CCU_208, 111, 0),
                                        2: (PeripheralType.RT_250, 222, 1)}.items():
        base = peripheral_base(slot)
        inputs.update({base + 1: kind, base + 2: 0, base + 3: serial, base + 4: owner, base + 5: 80})
        holding.update(dict(enumerate(_text(kind.name), start=base + 1)))
        alarms.update({base + bit: 0 for bit in (1, 2, 3, 4)})
    return SimulatedModbusDevice(input_registers=inputs, holding_registers=holding, discrete_inputs=alarms,
                                 max_registers=32)


def _connected(*, read_only: bool = False,
               unit: SimulatedModbusDevice | None = None) -> tuple[Client, SimulatedModbusGateway]:
    gateway = SimulatedModbusGateway({1: unit or _installation()})
    client = create_client_on(gateway, read_only=read_only)
    asyncio.run(client.connect())
    return client, gateway


# ================================================================================== model

def test_the_model_is_valid() -> None:
    assert_models_valid(SENTIO, identities=[{}])


def test_the_model_has_every_room_and_slot_the_address_space_defines() -> None:
    resolved = resolve(SENTIO, {})
    assert resolved.instances["room"] == tuple(range(1, 17))
    assert resolved.instances["peripheral"] == tuple(range(1, 65))


def test_every_key_is_one_named_value_and_every_named_value_is_a_key() -> None:
    named = [*LocationPointKey,
             *(room_key(n, value) for n in range(1, ROOM_COUNT + 1) for value in RoomPointKey),
             *(peripheral_key(slot, value) for slot in range(1, PERIPHERAL_COUNT + 1) for value in PeripheralPointKey)]
    assert len(set(named)) == len(named)
    assert set(named) == set(resolve(SENTIO, {}).points)


def test_the_key_strings_never_change() -> None:
    assert (LocationPointKey.VACATION_ENABLE, room_key(4, RoomPointKey.HUMIDITY_CURRENT),
            peripheral_key(2, PeripheralPointKey.LOW_BATTERY)) == \
           ("vacation_enable", "room_4_humidity_current", "peripheral_2_low_battery")


def test_units_are_exactly_the_units_the_model_uses() -> None:
    assert UNITS == {point.unit for point in resolve(SENTIO, {}).points.values() if point.unit is not None}


def test_the_regulated_target_and_the_users_setting_are_two_points() -> None:
    """Only a datapoint/setpoint prefix distinguishes the regulated target from the user's setting."""
    resolved = resolve(SENTIO, {})
    active, setting = resolved.point("room_1_temp_air_target_active"), resolved.point("room_1_temp_air_target")
    assert active.read != setting.read
    assert not active.writable and setting.writable


@pytest.mark.parametrize("key,unit", [
    ("room_1_temp_air_current", Unit.CELSIUS),
    ("room_1_humidity_current", Unit.PERCENT),
    ("room_1_humidity_threshold_heating", Unit.PERCENT),
    ("room_1_humidity_high_alarm_limit", Unit.PERCENT),
    ("room_1_dew_point_cooling_threshold", Unit.CELSIUS),
    ("datetime_unix", Unit.SECONDS),
])
def test_every_value_carries_the_right_unit(key: str, unit: Unit) -> None:
    assert resolve(SENTIO, {}).point(key).unit is unit


def test_text_is_sixteen_registers_and_temperatures_are_signed_hundredths() -> None:
    resolved = resolve(SENTIO, {})
    assert resolved.point("location_name").data_type.kind is DataTypeKind.STRING
    assert resolved.point("location_name").registers == 16
    temp = resolved.point("room_1_temp_air_current")
    assert (temp.data_type.kind, temp.scale, 0x7FFF in temp.no_data) == (DataTypeKind.INT16, 0.01, True)


def test_the_room_lock_is_a_closed_set() -> None:
    lock = resolve(SENTIO, {}).point("room_1_lock").data_type
    assert lock.kind is DataTypeKind.ENUM and lock.mapping is not None
    assert dict(lock.mapping) == {8: "locked", 16: "hotel", 32: "unlocked"}
    assert DataType.UINT16.kind is not lock.kind


@pytest.mark.parametrize("name,poll_rate", [
    ("state", PollRate.FAST), ("blocking_source", PollRate.FAST),
    ("temp_air_current", PollRate.MEDIUM), ("humidity_current", PollRate.MEDIUM),
    ("temp_air_target", PollRate.SLOW), ("type", PollRate.STATIC),
])
def test_what_a_room_is_doing_is_read_faster_than_how_warm_it_is(name: str, poll_rate: PollRate) -> None:
    assert resolve(SENTIO, {}).point(f"room_1_{name}").poll_rate is poll_rate


def test_every_alarm_is_a_bit_read_rarely_by_itself() -> None:
    resolved = resolve(SENTIO, {})
    alarms = resolved.select(sentio_model.ALARM)
    assert {p.key for p in alarms if p.key.startswith("room_1_")} == {
        "room_1_warning", "room_1_error", "room_1_low_battery", "room_1_peripheral_lost"}
    assert {p.key for p in alarms if p.key.startswith("peripheral_1_")} == {
        "peripheral_1_warning", "peripheral_1_error", "peripheral_1_low_battery", "peripheral_1_lost"}
    assert all(p.data_type is DataType.BOOL and p.poll_rate is PollRate.RARE for p in alarms)


def test_the_systems_summary_is_always_polled_and_reads_the_alarms_when_it_changes() -> None:
    resolved = resolve(SENTIO, {})
    for key in ("system_warning", "system_error"):
        summary = resolved.point(key)
        assert summary.poll_always and summary.poll_rate is PollRate.FAST
        assert summary.on_change is not None and summary.on_change.targets == sentio_model.ALARM


def test_a_raised_alarm_is_reported_without_waiting_for_its_own_schedule() -> None:
    unit = _installation()
    clock = FakeClock()
    client = create_client_on(SimulatedModbusGateway({1: unit}), clock=clock)
    asyncio.run(client.connect())
    seen: list[object] = []
    client.subscribe("room_1_low_battery", lambda key, old, new: seen.append(new.value))
    unit.discrete_inputs[1] = unit.discrete_inputs[room_base(1) + 3] = 1
    clock.advance(10)
    asyncio.run(client.poll())
    asyncio.run(client.poll())
    assert seen == [False, True]


@pytest.mark.parametrize("key,targets", [
    ("vacation_enable", Labels(group="room_target")),
    ("standby_enable", Labels(group="room_target")),
    ("room_1_temp_air_target", Labels(group="room_target", room=1)),
    ("room_1_temp_vacation", Labels(group="room_target", room=1)),
    ("room_1_mode", Labels(group="room_target", room=1)),
])
def test_a_write_that_changes_room_targets_reads_them_again(key: str, targets: Labels) -> None:
    resolved = resolve(SENTIO, {})
    effect = resolved.point(key).on_write
    assert effect is not None and effect.targets == targets
    assert [p.key for p in resolved.select(targets)][:1] == ["room_1_temp_air_target_active"]


def test_writing_vacation_updates_every_rooms_target_without_waiting_for_its_poll() -> None:
    unit = _installation()
    clock = FakeClock()
    client = create_client_on(SimulatedModbusGateway({1: unit}), clock=clock)
    asyncio.run(client.connect())
    seen: list[object] = []
    client.subscribe("room_1_temp_air_target_active", lambda key, old, new: seen.append(new.value))
    unit.input_registers[room_base(1) + 1] = 1600          # what the controller does on vacation
    asyncio.run(client.write("vacation_enable", 1))
    clock.advance(sentio_model.REREAD_AFTER_WRITE)
    asyncio.run(client.poll())
    assert seen == [21.0, 16.0]


def test_a_peripherals_signal_strength_is_read_rarely() -> None:
    assert resolve(SENTIO, {}).point("peripheral_1_signal_strength").poll_rate is PollRate.RARE


# ================================================================================== scan

def test_only_what_is_installed_becomes_keys() -> None:
    client, _ = _connected()
    assert client.instances("room") == (1, 3)
    assert client.instances("peripheral") == (1, 2)
    assert not any(k.startswith("room_2_") or k.startswith("peripheral_3_") for k in client.points)


def test_an_absent_room_costs_its_probe_and_nothing_more() -> None:
    _, gateway = _connected()
    base = room_base(2)
    touched = [r for _, r in gateway.requests
               if r.address < base + 36 and r.address + r.count > base]
    assert [(r.function, r.address, r.count) for r in touched] == \
           [(FunctionCode.READ_INPUT_REGISTERS, base + 27, 1)], "only the room type is asked for"


def test_no_request_exceeds_the_controllers_limit() -> None:
    _, gateway = _connected()
    assert all(r.count <= 32 for _, r in gateway.requests if r.function.is_read)


def test_the_rooms_describe_the_installation() -> None:
    client, _ = _connected()
    found = {r.number: r for r in rooms(client)}
    assert (found[1].name, found[1].is_dummy) == ("Kitchen", False)
    assert (found[3].name, found[3].is_dummy) == ("Hall", True)


def test_the_peripherals_describe_the_installation() -> None:
    client, _ = _connected()
    found = {p.slot: p for p in peripherals(client)}
    assert (found[1].model, found[1].serial_number, found[1].owner) == ("CCU-208", 111, 0)
    assert (found[2].model, found[2].serial_number, found[2].owner) == ("RT-250", 222, 1)


def test_an_old_address_space_is_warned_about() -> None:
    records: list[logging.LogRecord] = []

    class Keep(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record)
    logger = logging.getLogger(sentio_model.__name__)
    handler = Keep(level=logging.WARNING)
    logger.addHandler(handler)
    try:
        _connected(unit=_installation(address_space=(3, 1)))
    finally:
        logger.removeHandler(handler)
    assert any("3.1 is older" in r.getMessage() for r in records)


# ================================================================================ values

def test_a_room_temperature_is_read_in_degrees() -> None:
    client, _ = _connected()
    current = client.value("room_1_temp_air_current")
    assert current is not None and (current.value, current.quality) == (21.5, Quality.GOOD)


def test_a_missing_reading_is_no_data_not_327_degrees() -> None:
    unit = _installation()
    unit.input_registers[room_base(1) + 5] = 0x7FFF
    client, _ = _connected(unit=unit)
    current = client.value("room_1_temp_floor_current")
    assert current is not None and (current.value, current.quality) == (None, Quality.NO_DATA)


def test_a_dummy_room_has_no_sensor_keys() -> None:
    client, _ = _connected()
    sensors = ("temp_air_current", "temp_floor_current", "humidity_current", "dew_point_current")
    assert not any(client.has(f"room_3_{name}") for name in sensors)
    assert all(client.has(f"room_1_{name}") for name in sensors)
    assert client.has("room_3_temp_air_target_active")


def test_a_function_a_room_is_not_associated_with_has_no_state_keys() -> None:
    unit = _installation()
    unit.input_registers[room_base(1) + 12] = 77                     # underfloor heating, on HCC1
    client, _ = _connected(unit=unit)
    assert client.has("room_1_ufhc_state") and client.has("room_1_blocking_source_ufhc")
    assert not client.has("room_1_radiators_state") and not client.has("room_1_blocking_source_radiators")
    assert client.has("room_1_associated_radiators"), "the association itself says NONE, and stays"


def test_a_negative_outdoor_limit_is_negative() -> None:
    client, _ = _connected()
    current = client.value("temp_outdoor_cooling_min")
    assert current is not None and current.value == -5.0


def test_names_decode() -> None:
    client, _ = _connected()
    location = client.value("location_name")
    assert location is not None and location.value == "Home"


# ================================================================================ writes

def test_a_target_temperature_is_written_in_hundredths() -> None:
    client, gateway = _connected()
    assert asyncio.run(client.write("room_1_temp_air_target", 22.5)) is True
    assert gateway.units[1].holding_registers[room_base(1) + 19] == 2250
    [write] = [r for _, r in gateway.requests if not r.function.is_read]
    assert (write.function, write.address) == (FunctionCode.WRITE_SINGLE_REGISTER, room_base(1) + 19)


def test_a_lock_mode_is_written_by_name_and_only_those_three() -> None:
    client, gateway = _connected()
    assert asyncio.run(client.write("room_1_lock", "hotel")) is True
    assert gateway.units[1].holding_registers[room_base(1) + 20] == 16
    with pytest.raises(InvalidValueError):
        asyncio.run(client.write("room_1_lock", "open"))


@pytest.mark.parametrize("key,value", [("room_1_mode", 2), ("room_1_temp_preset", 3),
                                       ("standby_enable", 5)])
def test_a_switch_outside_its_range_is_refused(key: str, value: int) -> None:
    client, gateway = _connected()
    with pytest.raises(InvalidValueError):
        asyncio.run(client.write(key, value))
    assert not [r for _, r in gateway.requests if not r.function.is_read]


def test_writing_the_no_reading_sentinel_is_refused() -> None:
    """327.67 °C encodes to 0x7FFF, which the controller would read back as "no reading"."""
    client, _ = _connected()
    with pytest.raises(InvalidValueError):
        asyncio.run(client.write("room_1_temp_air_target", 327.67))


def test_a_read_only_client_never_writes() -> None:
    client, gateway = _connected(read_only=True)
    with pytest.raises(ReadOnlyError):
        asyncio.run(client.write("room_1_temp_air_target", 22.0))
    assert not [r for _, r in gateway.requests if not r.function.is_read]
