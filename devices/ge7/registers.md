<!-- generated from devices/ge7/registers.toml by defs-gen - do not edit, change the source -->
<!-- defs-gen 3 -->
<!-- input sha256 4b24a0dac5a13b9f43b822999a4bd0e8cfedcb3e360d3db1c332e9bdb57d3ece -->

# GE7 geometry engines: host window and microcode load registers

Host-visible window of the GE7 geometry engines in the Express graphics slot. Provenance tags in item text: [public] published document or public driver, [binary] shipped IRIX or PROM binary (a software expectation), [vendor-derived] upstream headers (none used here). Routine names, addresses and cross-references are in the unit README.

Unit `ge7`, macro prefix `GE7`.

Every item has a grade: established, inferred or unknown. A grade says how the item was derived from its source; it does not claim the item was measured on silicon.

## Registers

| Register | Offset | Access | Width | Count | Space | Reset | Grade | Source |
|---|---|---|---|---|---|---|---|---|
| `shared_ram` | 0x0 | rw | 32 | 32767 |  | unknown | established |  |
| `ucode_ready` | 0x1fffc | rw | 32 |  |  | unknown | established |  |
| `slot0_ram` | 0x68000 | rw | 32 | 248 |  | unknown | inferred |  |
| `ucode_d0` | 0x683e0 | rw | 32 |  |  | unknown | established |  |
| `ucode_d1` | 0x683e4 | rw | 32 |  |  | unknown | established |  |
| `ucode_d2` | 0x683e8 | rw | 32 |  |  | unknown | established |  |
| `ucode_d3` | 0x683ec | rw | 32 |  |  | unknown | established |  |
| `revision` | 0x683f4 | rw | 32 |  |  | unknown | established |  |
| `slot_ram` | 0x68400 | rw | 32 | 1792 |  | unknown | established |  |

### Register `shared_ram`

Shared data RAM below the ready flag. [binary] The microcode loader copies the constants block into its first words and reads them back; its error text calls it shared RAM. [public] NetBSD's memory map names it shared data RAM. qtest: a word written reads back.

Array of 32767 registers, stride 4.

### Register `ucode_ready`

Last word of the shared RAM, used as a flag. [binary] The driver stores 1 after the built-in console microcode loads and 0 when a load fails; the consumer is unread, so the meaning "microcode ready" is inferred. qtest: reads back what was written.

### Register `slot0_ram`

Engine 0 storage below the microcode window. [binary] The engine probe takes slot 0 as present and tests only slots 1 to 7, so ordinary storage here is inferred from the other slots. qtest: the first and the last tested offsets read back a written word.

Array of 248 registers, stride 4.

### Register `ucode_d0`

Microword column 0, lowest. [binary] The loader writes record bytes 20 to 23 here and reads them back unmasked. One window serving every populated engine (broadcast) is inferred. qtest: a full 32-bit value reads back.

### Register `ucode_d1`

Microword column 1. [binary] The loader writes record bytes 16 to 19 here and reads them back unmasked. qtest: a full 32-bit value reads back.

### Register `ucode_d2`

Microword column 2. [binary] The loader writes record bytes 12 to 15 here and reads them back unmasked. qtest: a full 32-bit value reads back.

### Register `ucode_d3`

Microword column 3. [binary] The loader writes record bytes 8 to 11 here; the verify masks both sides to seven bits, so only seven bits are stored. qtest: writing all ones reads back with the low seven bits set.

| Bits | Field | Grade | Values | Source | Description |
|---|---|---|---|---|---|
| 6:0 | `stored` | established |  |  |  |

### Register `revision`

GE7 revision. [binary] The kernel driver and the PROM probe write zero, read the word back and keep bits 7:5 of the low byte. [public] NetBSD reads another offset in slot 0 and keeps bits 7:4; no shipped binary read touches that offset, so this register is taken as the revision. That the three bits are a revision number is inferred. qtest: after a write of zero, bits 7:5 read as the configured revision.

| Bits | Field | Grade | Values | Source | Description |
|---|---|---|---|---|---|
| 7:5 | `rev` | inferred |  |  |  |

### Register `slot_ram`

Engine slots 1 to 7, 1 KiB each. [binary] The engine probe writes five words per slot at slot offsets 0x0, 0x7c, 0xfc, 0x17c and 0x1fc and reads them back; each slot that returns all five sets the count to its index plus one. An absent slot's reply (bus error or data), storage beyond the last probed offset, and whether the load window and revision register repeat in these slots are unknown. qtest: slot n returns the five written words for n below the engine count and not above.

Array of 1792 registers, stride 4.
