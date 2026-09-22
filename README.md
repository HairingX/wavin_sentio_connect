# Wavin Sentio Connect

An event-driven Python client for the **Wavin Sentio** floor heating controller over Modbus TCP.

The register map is complete: all 16 rooms, 64 peripheral slots and the location object are
modelled from the official Sentio Modbus manual. You subscribe to the values you care about and
get a callback when one actually changes.

## Installation

```bash
pip install wavin-sentio-connect
```

## Enabling Modbus on the controller

Modbus is **disabled by default**. Enable it from a Sentio Display:

`System | Installer settings | Modbus configuration | Modbus TCP`

The controller restarts afterwards. It uses DHCP; its hostname is
`Wavin Sentio CCU#[last four digits of the serial number]`.

## Usage

```python
import asyncio
from wavin_sentio_connect import WavinSentioTCPConnect, WavinSentioDatapointKey

def on_change(key, old_value, new_value):
    print(f"{key}: {old_value} -> {new_value}")

async def main():
    client = WavinSentioTCPConnect()
    await client.connect("my-sentio", "<device-ip>")

    # connect() discovers what this controller actually has, so subscribe to that
    # rather than to the whole register map.
    print(client.discovery)        # e.g. "13 rooms [1, 2, 4, 5, ...], 15 peripherals"

    for room in client.discovery.rooms:
        for suffix in ("TEMP_AIR_CURRENT", "TEMP_FLOOR_CURRENT", "HUMIDITY_CURRENT"):
            client.subscribe(WavinSentioDatapointKey[f"ROOM_{room}_{suffix}"], on_change)

    # You decide when to poll. Callbacks fire only for values that changed.
    while True:
        await client.request_datapoint_read()
        await client.request_setpoint_read()
        await asyncio.sleep(30)

asyncio.run(main())
```

Connect first, then subscribe. Until `connect()` has run, the client cannot know which of the
16 rooms and 64 peripheral slots this installation uses — asking for a room that was never set
up is how you end up with entities that never hold a value. `provides()` returns `False` for
those, and `subscribe()` refuses them.

Writing a setpoint:

```python
await client.request_setpoint_write(WavinSentioSetpointKey.ROOM_1_TEMP_AIR_TARGET, 21.5)
# The device may clamp or step-align the value, so read it back rather than assuming:
await client.request_setpoint_read()
```

## Writing, and knowing what the controller is doing

The controller answers `SLAVE_DEVICE_BUSY` (`0x06`) while it persists a change — after any
write, and after anyone touches the display.

Writes do **not** wait for the controller to settle:

```python
await client.request_setpoint_write(key, 21.5)   # returns as soon as it is accepted
await coordinator.async_request_refresh()        # your cadence, coalesced by the host
```

This is the pattern Home Assistant's own Modbus integration uses — write, show the new value
optimistically, refresh on your own schedule. Blocking until the controller is ready would
stall every other request for the whole busy period and buys nothing, since the value has to be
read back anyway (the device may clamp or step-align it).

Pass `wait_for_ready=True`, or call `await client.await_device_ready()`, only when the next
step genuinely cannot start until the controller has settled — a scripted sequence of dependent
writes, for example.

What the client *does* do on your behalf is retry a request the controller rejects with `0x06`.
That is not general Modbus practice; it is required by the Sentio manual, which states the
request "shall be repeated again".

### Showing that work is in progress

`WRITE_PENDING` is true from the moment a write starts until it has settled. Use it to show
that something is happening — a spinner, a pending badge — rather than to disable a control.
Disabling a +/- stepper per tap makes it feel broken; debounce the taps and send one write
instead.

```python
from modbus_event_connect import ModbusStatusKey

client.subscribe(ModbusStatusKey.WRITE_PENDING, on_change)
client.subscribe(ModbusStatusKey.DEVICE_BUSY, on_change)
client.subscribe(ModbusStatusKey.CONNECTED, on_change)

if client.accepts_writes:
    await client.request_setpoint_write(key, 21.5)
```

| Key | Meaning |
|---|---|
| `WRITE_PENDING` | `1` from the moment a write starts until the controller has settled |
| `DEVICE_BUSY` | `1` while the controller is answering `0x06` |
| `CONNECTED` | `1` once the transport is open and a model is loaded |
| `LAST_EXCEPTION_CODE` | Modbus exception from the most recent request, `0` if it succeeded |

`WRITE_PENDING` and `DEVICE_BUSY` are not the same thing. `DEVICE_BUSY` only becomes true if
the controller actually reports `0x06`; a controller that answers instantly would show nothing.
`WRITE_PENDING` is true for every write regardless, and is reference-counted, so overlapping
writes only clear it once the last one finishes.

`DEVICE_BUSY` going true **without** `WRITE_PENDING` means someone else changed something — on
the display or in the app. That is a useful cue to refresh early rather than wait for the next
interval. It is a hint, not a guarantee: the manual says the controller *may* go busy on an
external change.

Status keys behave like any other key — `subscribe()`, `get_value()`, change-filtered events —
except that they are pushed by the client rather than read from a register, so they work before
`connect()` and need no device model.

## Polling is the caller's job

This library owns **no timer and no background thread**. It turns register reads into
value-change events; deciding *when* to read is left to whatever scheduler the host already
runs. In Home Assistant that is a `DataUpdateCoordinator`; in a script it is your own loop.

This is deliberate. A library that schedules its own polling fights the host's event loop,
duplicates its backoff and retry policy, and takes the polling interval out of the user's hands.

Reading **everything** is cheap enough that you should not split values into static and dynamic
groups: measured against a real CCU-208 with 13 rooms and 15 peripherals, a full cycle of all
643 available points is **~310 ms across 101 requests**, or about 1% duty cycle at a 30-second
interval. Treating version and serial registers as read-once would save nothing and would leave
them stale after a firmware update.

## Async, and bring your own connection

The client is natively asynchronous end to end: no thread hops, nothing that blocks the caller's
event loop. That follows Home Assistant's [`async-dependency`](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/async-dependency/)
quality-scale rule, which asks libraries to use asyncio rather than pay a context switch per
request.

You can also hand it a connection instead of letting it open one, per the
[`inject-websession`](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/inject-websession/)
rule - useful when the host already talks to the same controller and a second socket would be
waste:

```python
from modbus_event_connect import PymodbusTransport

transport = PymodbusTransport(host="<device-ip>", port=502, unit_id=1)
client = WavinSentioTCPConnect(transport=transport)
```

`PymodbusTransport` is the only transport shipped. Writing another is small - implement the
`ModbusTransport` protocol; the event layer does not care what is underneath.

Calling from a plain synchronous script needs no async code of your own:

```python
asyncio.run(client.request_datapoint_read())
```

## Addressing

The Sentio manual's "Modbus Address" column holds raw wire addresses, so its numbers are used
unchanged. Object base addresses:

| Object | Base | Instances |
|---|---|---|
| Location | `0` | one |
| Room *N* | `N * 100` | 1–16 |
| Peripheral *N* | `51100 + N * 100` | 1–64 |

Helpers `room_base(n)` and `peripheral_base(n)` are exported.

Peripheral slots are **not stable identities** - the controller reorders them when peripherals
are learned or unlearned. Use `PERIPHERAL_n_SN` to identify one, and `PERIPHERAL_n_OWNER`
(`0` = location, `1`–`16` = room) to find which room it belongs to.

## Documentation

- [`docs/sentio-modbus-reference.md`](docs/sentio-modbus-reference.md) — the protocol: register
  tables, data types, error handling, enumerations.
- [`docs/sentio-registers.csv`](docs/sentio-registers.csv) — all 344 documented registers, one
  row each.
- [`docs/temp/implementation-status.md`](docs/temp/implementation-status.md) — what is
  implemented and what is not.

## Known gaps

- **Discrete inputs are not supported yet.** That is every alarm and warning in the system
  (77 registers): per-room aggregated warning/error, low battery, peripheral lost, and all
  DHW/ITC/HCC sensor failures. They need Modbus function code `0x02`.
- Only the location, room and peripheral objects are modelled. Outdoor, DHW, ITC, HCC, buffer
  tank, ventilation and dehumidifier objects are documented in the CSV but not yet wired.

## Disclaimer

Wavin Sentio Connect is provided "as is", without warranty of any kind. The authors and
contributors are not responsible for any damage or data loss that may occur from using this
library. Users are solely responsible for ensuring the proper and safe operation of their
Modbus devices.

This project is not affiliated with or endorsed by Wavin.

## License

MIT. See [LICENSE](LICENSE).
