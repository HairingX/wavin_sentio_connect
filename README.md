# Wavin Sentio Connect

An event-driven Python client for the **Wavin Sentio** floor heating controller over Modbus TCP,
built on [modbus_event_connect](https://github.com/HairingX/modbus_event_connect).

The register map is complete for the location, all 16 rooms and all 64 peripheral slots,
modelled from the official Sentio Modbus manual. Connecting finds out which rooms and
peripherals your installation actually has; you subscribe to the values you care about and are
told when one changes - with its quality, so "offline", "no reading" and a real value never look
alike.

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
from wavin_sentio_connect import create_client, rooms

def on_change(key, old, new):
    print(f"{key}: {new.value} ({new.quality.name})")

async def main():
    client = create_client("<device-ip>")
    await client.connect()              # finds the installed rooms and peripherals

    for room in rooms(client):
        print(room.number, room.name, "dummy" if room.is_dummy else "")
        client.subscribe(f"room_{room.number}_temp_air_current", on_change)

    while True:                         # you own the clock; the library owns the plan
        await client.poll()      # reads only what is due - free when nothing is
        await asyncio.sleep(1)

asyncio.run(main())
```

When `connect()` returns, `client.keys` holds exactly what this installation has - a room that
was never set up is not there, so no entity is built for it. `rooms(client)` and
`peripherals(client)` describe the installation from values already read, with no extra
requests.

Every value is a `DataValue`: `value`, `quality` and `timestamp` (UTC).

| Quality | Meaning |
|---|---|
| `GOOD` | the controller answered with a valid value |
| `NO_DATA` | it answered "no reading" - a missing sensor, an unconfigured limit, a wired peripheral's signal strength |
| `OFFLINE` | the register exists but what is behind it is not answering |
| `STALE` | the last read failed; the value is the last good one |

## How often values are read

Every point has a poll rate, and the library reads it when it is due:

| Poll rate | Default | Sentio uses it for |
|---|---|---|
| `FAST` | 10 s | room states and blocking sources |
| `MEDIUM` | 30 s | temperatures, humidity, dew point |
| `SLOW` | 60 s | settings |
| `RARE` | 15 min | peripheral signal strength |
| `STATIC` | at connect | versions, serial numbers, names, room types |

Override any of them, or a single key:

```python
from modbus_event_connect import PollRate
client.set_poll_interval(PollRate.FAST, 5)
client.set_poll_interval("room_4_temp_air_current", 2)
await client.refresh(PollRate.STATIC)        # re-read the static values now
```

Only what something wants is read: a subscriber, or `client.set_polling(key)`. Measured against a
real CCU-208 with 13 rooms and 15 peripherals, connecting - scanning every room and slot and
reading all 643 values once - takes under a second.

## Writing

```python
await client.write("room_1_temp_air_target", 21.5)
await client.write("room_1_lock", "hotel")        # locked / hotel / unlocked
```

- A value is checked before anything is sent: its type, its range, and the controller's
  "no reading" sentinel, which could never be read back.
- Writes are sent in order. Tapping + five times sends the first value and the last, not all
  five.
- The written point is read back a moment later, since the controller may clamp a value.
- The controller answers `SERVER_DEVICE_BUSY` (`0x06`) while it stores a change; the manual says
  such a request "shall be repeated again", and the library does, with backoff.
- `client.write_pending` - and the subscribable `Status.WRITE_PENDING` - is true from the moment
  a write is asked for until the last one has finished.

For monitoring only, create the client read-only; every write is then refused before it reaches
the controller:

```python
client = create_client("<device-ip>", read_only=True)
```

## Sharing a connection

To put the controller on a connection the host already owns - a gateway shared with other
devices - use `create_client_on`:

```python
from modbus_event_connect.modbus import ModbusTcpConnection
from wavin_sentio_connect import create_client_on

connection = ModbusTcpConnection("<device-ip>")
client = create_client_on(connection, unit_id=1)
```

The client is asynchronous end to end - no threads, nothing that blocks the event loop - and
owns no timer. In Home Assistant, call `poll()` from the integration's own tick.

## Keys and addressing

Keys are plain strings: `room_{n}_...` for rooms 1-16 and `peripheral_{n}_...` for slots 1-64.
The model is in [`model.py`](src/wavin_sentio_connect/model.py); every key is declared there
with its address and encoding.

The manual's "Modbus Address" column holds the addresses themselves, so its numbers are used unchanged:

| Object | Base | Instances |
|---|---|---|
| Location | `0` | one |
| Room *N* | `N * 100` | 1–16 |
| Peripheral *N* | `51100 + N * 100` | 1–64 |

Peripheral slots are **not stable identities** - the controller reorders them when peripherals
are learned or unlearned. Use `peripheral_{n}_serial_number` to recognise a device, and
`peripheral_{n}_owner` (`0` = location, `1`–`16` = room) to find the room it belongs to.

Two room values are easy to confuse: `room_{n}_temp_air_target` is the user's setting, and
`room_{n}_temp_air_target_active` is the target the controller is regulating to right now -
different under standby, vacation or a schedule.

## Documentation

- [`docs/sentio-modbus-reference.md`](docs/sentio-modbus-reference.md) - the protocol: register
  tables, data types, error handling, enumerations.
- [`docs/sentio-registers.csv`](docs/sentio-registers.csv) - all 344 documented registers, one
  row each.

## Known gaps

- **Alarms are not modelled yet.** They are discrete inputs (77 registers: per-room warnings,
  low battery, peripheral lost, sensor failures). The library reads discrete inputs, and the
  controller has been verified to answer them; they still need adding to the model.
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
