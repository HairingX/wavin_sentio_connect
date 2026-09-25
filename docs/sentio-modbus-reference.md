# Wavin Sentio — Modbus reference

Condensed, machine-readable extract of `Sentio_ModbusManual_EN_20240809.pdf`
(the manual is the authority; this file is a working summary for implementers and agents).

Companion file: **[`sentio-registers.csv`](sentio-registers.csv)** — all 344 documented registers,
one row each, columns: `object, object_base, table, address, registers, offset, parameter,
access, data_type, fw_3_2, fw_3_3, fw_3_4, description`.

Scope of the manual: Sentio control units with firmware **TM60006.0+**; Modbus TCP/IP requires
**TM60014+**.

---

## 1. Transport

| | Modbus RTU | Modbus TCP |
|---|---|---|
| Physical | RS-485 on RJ-45 port **A** | RJ-45 **LAN** port |
| Endpoint | 9600 / **19200** / 38400 / 57600 bps, 8 data bits, parity none/odd/even | `IP:502`, unit ID **255 (0xFF)** if needed |
| Slave address | 1 (default) – 247 | — |
| Reply timeout | 500 ms | 500 ms |
| **Max read per request** | **32 registers or 256 bits** | **32 registers or 256 bits** |
| Modes | Disabled (default), Read only, Read/write, Write with password, Master | Disabled (default), Read only, Read/write, Write with password |

Modbus is **disabled by default** and can only be enabled from a Sentio Display:
`System | Installer settings | Modbus configuration`. The unit reboots after the mode changes,
and port A can no longer drive a Sentio Display once RTU is enabled.

DHCP hostname: `Wavin Sentio CCU#[last four S/N digits]`.

> The 32-register ceiling is a hard constraint on request batching. A generic Modbus
> client default of 125 registers/request will be rejected by this device.

## 2. Register tables and function codes

| Table | Width | Access | Used for | Read FC | Write FC |
|---|---|---|---|---|---|
| Discrete inputs | 1 bit | R | alarms and warnings | `0x02` | — |
| Input registers | 16 bit | R | state / measured values | `0x04` | — |
| Holding registers | 16 bit | R/W | configuration and setpoints | `0x03` | `0x06` single, `0x10` multiple |

Each table is numbered **independently**: discrete input `00101`, input register `00101` and
holding register `00101` are three unrelated values.

### Address numbering — resolved: the manual's number IS the address

**Send the manual's number unchanged.** The manual's *"Modbus Address"* column holds raw
protocol (PDU) starting addresses, so manual `00104` is address `104`, with no `-1`
adjustment. Manual `00001` is address `1`, and address `0` is unused.

The manual never states this, and its per-table numbering starting at `00001` is also
consistent with 1-based *entity numbers* (where `address = number - 1`). It was settled by
reading a CCU-208: input register address `101` returns `2100`, which fits manual input
register `00101`, room 1's *Desired temp* (`val_d2_fp100`, 21.00 °C). Under the 1-based
reading, address `101` would be manual `00102`, *General Heating/Cooling state*, a `val_u1`
enum whose range is `0..255`, which cannot hold `2100`.

Two registers hold documented constants, read on the same controller as the manual gives them,
and worth reading again on a new firmware:

| Manual address | Value | Meaning |
|---|---|---|
| Input register `00001` | `3` | Address space major version |
| Input register `00014` | `1530` | Device serial number prefix |

A wrong assumption here also fails loudly rather than silently: input registers jump
`00002` to `00010`, so a 1-based client reading address `2` gets **illegal data address**.

## 3. Object address map

Values are grouped into *objects*; the object's base address prefixes the register number
within every table.

| Object | Base | Instances |
|---|---|---|
| Location | `0` | single (`00001`–`00037`) |
| Room *N* | `N * 100` | Room 1–16 -> `100`…`1600` |
| Outdoor 1 | `3300` | single |
| DHW 201 (Calefa) | `6500` | single |
| DHW Tank | `6600` | single |
| Calefa ITC | `6800` | same layout as Sentio ITC |
| Sentio ITC 1–2 | `7300`, `7400` | |
| HCC 1–3 | `7700`, `7800`, `7900` | |
| H/C Source | `8100` | single |
| Boiler / Heat pump | `8200` | single |
| Buffer tank | `8300` | single |
| Thermistor inputs T1–T5 | `12800` | single |
| Peripheral *N* | `51100 + N * 100` | N = 1–64 -> `51200`…`57500` |
| Ventilation 1–2 | `61000`, `61100` | |
| Dehumidifier 1–4 | `65000`…`65300` | |

> **Peripheral base is `51200` for peripheral 1**, not `51100`. The list is *dynamic* —
> a peripheral's slot changes when peripherals are learned or unlearned, so slot index is
> not a stable identity. Use the `SN` register (IR base+2, `val_u4`) as the identity and
> `Owner` (IR base+4) to bind it to a room (`0` = Location, `1`–`16` = Room 1–16).

## 4. Data types

| Type | Width | Range | Invalid sentinel | Decoding |
|---|---|---|---|---|
| `val_enum` | 1 B | 0..255 | `0xFF` | unsigned |
| `val_u` / `val_u1` | 1 B | 0..255 | `0xFF` | unsigned |
| `val_u2` | 2 B | 0..65535 | `0xFFFF` | unsigned |
| `val_u4` | 4 B | 0..4294967295 | `0xFFFFFFFF` | unsigned, 2 registers, big-endian |
| `val_utf8` | var. | max 256 B | `LEN = 0xFFFF` | see section 5 |
| `val_d2_fp100` | 2 B | **−327.68 .. 327.67** | `0x7FFF` | **signed** int16 / 100 |
| `val_d2_fp10` | 2 B | *(not in the manual's type table)* | presumably `0x7FFF` | signed int16 / 10 |
| `val_d2` | 2 B | *(not in the manual's type table)* | presumably `0x7FFF` | signed int16 |

**`val_d2_fp100` is signed.** Its range is explicitly negative-capable and it is the type of
every temperature in the system, including outdoor temperature. Decoding it as unsigned turns
any sub-zero reading into a large positive number.

The register table writes `val_u1` where the type table writes `val_u`; they are the same type.
`val_d2` and `val_d2_fp10` appear only in the register table — the divider is inferred from the
name (`fp10` -> divide by 10) and should be confirmed against hardware.

## 5. Text values (`val_utf8`)

A string occupies 16 consecutive holding registers = **32 bytes, UTF-8, NULL-terminated**.
Bytes are packed two per register, high byte first:

```
"Hello" -> FC 0x03, byte count 0x08
           Reg X   = 'H''e'   Reg X+1 = 'l''l'
           Reg X+2 = 'o' 0x00 Reg X+3 = 0x00 0x00
```

Non-ASCII characters consume multiple bytes (`"Blå Værelse"` = 13 bytes), so 32 bytes is a
**byte** budget, not a character budget. A string too long for the device is silently truncated
by the device.

> **Apparent contradiction in the manual, resolved:** the data-type table describes `val_utf8`
> as `2b LEN + UTF8` with invalid value `LEN = 0xFFFF`, implying a 2-byte length prefix. Take
> the example above instead — there is **no prefix**. Every one of the 13 `val_utf8` fields
> spans exactly 16 registers = 32 bytes, and the manual describes them as *"32 Bytes, UTF8,
> NULL terminated"*; a 2-byte prefix would leave only 30 bytes of payload, and a NULL
> terminator would be redundant alongside a length field. The `2b LEN` row appears to describe
> a generic variable-length form these fixed fields do not use.

## 6. Error handling

| Code | Name | Sentio's meaning |
|---|---|---|
| `01` | Illegal function | unsupported command |
| `02` | Illegal data address | register does not exist — **also returned when one request covers a mix of existing and non-existing registers** |
| `03` | Illegal data value | value not supported for that register |
| `04` | Slave device failure | register belongs to a peripheral that is disconnected (e.g. Calefa) |
| `06` | Server device busy | start-up, or data integrity temporarily not guaranteed |

### `0x06 SLAVE_DEVICE_BUSY` must be retried

From the manual's *Notes for integrators*:

> When data are changed, either by writing to holding registers or due to a change made by
> another user interface (e.g. thermostat), the system may trigger a configuration save
> procedure which prevents the device from retrieving the data requested. In such cases the
> device responds with exception code `0x06 SLAVE_DEVICE_BUSY` … **and the request shall be
> repeated again**.

This is not an edge case: it fires after **any** write and after any change made at a
thermostat. The same code is returned throughout device boot. A client without retry-on-`0x06`
will intermittently drop readings, most often right after it writes something.

### Invalid values

A measurement that is not initialised — failure, or a slow/absent wireless peripheral — reads
back as the type's invalid sentinel (section 4) rather than failing. Sentinels must be mapped
to "no value", and this must happen **after** sign extension, not before.

### Write validation

The device clamps rather than rejects: below minimum -> minimum, above maximum -> maximum,
off-step -> aligned (e.g. 15.2 °C -> 15.0 °C), over-long string -> truncated. A successful write
therefore does **not** mean the value was stored verbatim — read back to confirm.

## 7. Enumerations

### General blocking sources
Used by every `blocking source` register.

```
0  NONE                    9  FAULT_HTCO            17 HCW_SOURCE_NOT_RELEASED
1  UNKNOWN                10 PERIODIC_ACTIVATION    18 ROOM_MODE
2  CONTACT                11 BMS                    19 SYSTEM_IS_INITIALIZING
3  FLOOR_TEMP             12 DEADBAND               20 SYSTEM_IS_SHUTTING_DOWN
4  LOW_ENERGY             13 DRYING                 21 NO_OUTPUT
5  AIR_TEMP               14 HEATING/COOLING MODE   22 FIRST_OPEN_ACTIVATION
6  DEW_POINT              15 INSUFFICIENT_DEMAND    23 ROOM_WITH_NO_TEMP_SOURCE
7  OUTDOOR_TEMP           16 COOLDOWN_PERIOD        24 HCWS_ELEMENTS_BLOCKED
8  FAULT (general, e.g. missing sensors)
```

The manual states the list **is still growing** — treat unknown values as opaque, never assume
the set is closed.

### Peripheral types
Register: input register `base+1`, `val_u2`.

```
0x0    DHW-201    Calefa DHW controller      0x9    RT-250IR   wireless thermostat w/ IR floor sensor
0x4    LCD-200    Sentio display             0xA    EU-208-A   extension module, 8 actuators
0x5    RT-201     wired room thermostat      0xB    EU-206-VFR extension module, 6 relays
0x6    RT-250     wireless room thermostat   0xC    ET-250     wireless outdoor temp sensor
0x7    RS-211     wired room sensor          0xD    ET-210     wired outdoor temp sensor
0x8    RS-251     wireless room sensor       0xE    VH-250     smart radiator thermostat
0x11E0 CCU-208    control unit               0x1-0x3, 0xF: not used
```

Note `0x11E0` = **4576**, far outside a byte — the register is `val_u2`, so a `val_u1`-sized
decode will not see the control unit.

### Heating / cooling state
Used by *General H/C state*, *Radiators state*, *Underfloor H/C state*, ITC/HCC *State*:

```
0 NONE (function unused in this object, or no load detected on any output)
1 IDLE   2 HEATING   3 COOLING   4 BLOCKED_HEATING   5 BLOCKED_COOLING
```

`0 NONE` is absent from the *General* H/C state register but present on the per-emitter ones.

### Room enumerations

| Register | Values |
|---|---|
| Room type (IR `base+27`) | `0` NORMAL (default), **`1` DUMMY** (no thermostat/sensor installed) |
| Room mode (HR `base+17`) | `0` SCHEDULE, `1` MANUAL |
| Room mode override (HR `base+18`) | `0` NONE, `1` TEMPORARY, `2` VACATION_AWAY, `3` ADJUST |
| UI access level (HR `base+20`) | `8` LOCKED (read only), `16` HOTEL, `32` UNLOCKED |
| Room temperature preset (HR `base+35`) | `0` ECO, `1` COMFORT, `2` EXTRA COMFORT |

The three lock values are **not a contiguous range** — `max = 32` does not validate them.

### Location enumerations

| Register | Values |
|---|---|
| Heating/Cooling mode (IR `00020`) | `0` HEATING, `1` COOLING |
| Device type (IR `00010`) | `1` CCU-208, `2` DHW-201 (Calefa) |
| Modbus mode (HR `00005`) | `0` DISABLED, `1` READ_ONLY, `2` READ_WRITE, `3` WRITE_WITH_PASSWORD (default `0`) |
| Update mode (HR `00033`) | `0` do not allow from mobile app, `1` enabled, `2` disabled entirely |
| Daylight saving (HR `00030`) | `0` disabled, `1` enabled |

### Modbus password (HR `00006`, write-only, `val_u2`)

Relevant only when Modbus mode = `WRITE_WITH_PASSWORD`. Writing a valid password enables writes
for **11 minutes**, then it must be written again. Changing it takes two writes: old password,
then new password within 11 minutes. Default `1234`; valid range `1`–`65534`.

This register **cannot be read** — do not place it in a read set.

## 8. Versioning

| Register | Meaning |
|---|---|
| IR `00001` / HR `00001` | Address space **major** — incremented on incompatible change |
| IR `00002` / HR `00002` | Address space **minor** — incremented on compatible change |

The same two numbers are exposed in both the input-register and holding-register tables.

The register list is **not finite**; new values are added over time. Each row in
`sentio-registers.csv` carries `fw_3_2` / `fw_3_3` / `fw_3_4` (address space version mapped to
FWPKG 12 / 14 / 16): `YES` = supported, `-` = not available, `CHA` = changed in that version.
Read the major/minor registers at connect and gate optional registers on them.

The description text in the manual's own rows for these registers (`= 3`, `= 1`) is stale — the
column headers `3.2`, `3.3`, `3.4` carry the real versions.

## 9. Notes that shape a client implementation

1. **Retry on `0x06`.** Mandated by the manual (section 6). Without it, reads fail
   intermittently after every write and during boot.
2. **Batch to at most 32 registers**, and only across genuinely contiguous addresses. Objects
   are sparse (e.g. room input registers jump `00107` to `00111`), and a request spanning a gap
   returns `0x02` for the whole request, losing the valid registers with it.
3. **Sign-extend before range-checking.** `val_d2_fp100` is signed; the invalid sentinel
   `0x7FFF` is the *maximum positive* value, so the valid window is `−32768 .. 32766`.
4. **Peripheral slots are not stable identities** — key on serial number.
5. **Discrete inputs carry every alarm and warning** in the system (77 of the 344 documented
   registers). They need `FC 0x02`, which is a separate code path from register reads.
