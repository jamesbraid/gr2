<!-- generated from devices/bt457/registers.toml by defs-gen - do not edit, change the source -->
<!-- defs-gen 4 -->
<!-- input sha256 e70d1735c70ebfb40a10bdbfae82173a37248264f8277909d1c208d56f73f0dc -->

# Brooktree Bt457 RAMDAC as wired on the Express board (three chips, one per colour)

Three single-colour 5:1 multiplexed RAMDACs behind the five XMAP5 chips: red, green and blue, each with its own four-port window. Offsets are within one chip's window; the red, green and blue windows are 0x20 bytes apart (addresses in the README). Each port is one byte at the first byte of a 4-byte stride, so a big-endian CPU addresses the most significant lane. The port numbers follow the datasheet's C1 and C0 inputs: the stride bit 2 is C0 and bit 3 is C1. Grades: established means stated by the published Bt457/Bt458 datasheet or read in full in the shipped Indigo driver or PROM; inferred means a reasoned reading; unknown means nothing settles it. [public] marks the datasheet, [binary] a shipped binary. The datasheet says the command, read-mask, blink-mask and test registers are not initialised at power-up; this page gives no reset values. Nothing was read on a board. Prose in devices/bt457/README.md.

Unit `bt457`, macro prefix `BT457`.

Every item has a grade: established, inferred or unknown. A grade says how the item was derived from its source; it does not claim the item was measured on silicon.

## Registers

| Register | Offset | Access | Width | Count | Space | Reset | Grade | Source |
|---|---|---|---|---|---|---|---|---|
| `addr` | 0x0 | rw | 8 |  |  | unknown | established |  |
| `palette` | 0x4 | rw | 8 |  |  | unknown | established |  |
| `ctrl` | 0x8 | rw | 8 |  |  | unknown | established |  |
| `overlay` | 0xc | rw | 8 |  |  | unknown | established |  |

### Register `addr`

Address register. Written before every register or palette access; after a palette or overlay access it advances (palette wraps to 0 after 255, overlay goes to 4 after overlay 3, control registers do not advance it). [public] [binary] A qtest can discriminate: write 255 to addr, write two bytes to palette, check the address wrapped to 0 then 1.

### Register `palette`

Colour palette RAM data. The three chips are addressed separately, so the board uses the datasheet's normal mode: one byte write stores one colour component of the addressed entry and the address advances. [public] [binary]

### Register `ctrl`

Control register data: the register picked by addr (read mask, blink mask, command, test) is read or written here and addr does not advance. [public] [binary] Gr2BlankScreen writes the read mask this way, ctrl 0 to blank and 255 to unblank, after addr 4, in all three chips.

### Register `overlay`

Overlay colour data, entries 0 to 3 selected by addr. Init writes four bytes 0 to 3 after setting addr to 0. [public] [binary]

## Words

| Word | Width | Grade | Source |
|---|---|---|---|
| `COMMAND` | 8 | established |  |

### Word `COMMAND`

Command register fields, from the datasheet. The board writes 0xc1.

| Bits | Field | Grade | Values | Source | Description |
|---|---|---|---|---|---|
| 7 | `mux_select` | established |  |  | [public] 1 selects 5:1 multiplexing, matching the five XMAP5 chips. |
| 6 | `ram_enable` | established |  |  | [public] 1 uses palette RAM when the overlay select bits are 00; 0 uses overlay colour 0. |
| 5:4 | `blink_rate` | established |  |  | [public] 16/48, 16/16, 32/32 or 64/64 retrace intervals. |
| 3 | `overlay1_blink` | established |  |  | [public] |
| 2 | `overlay0_blink` | established |  |  | [public] |
| 1 | `overlay1_display` | established |  |  | [public] 1 enables overlay plane 1 input. |
| 0 | `overlay0_display` | established |  |  | [public] 1 enables overlay plane 0 input. |

## Constants

| Constant | Value | Grade | Source | Description |
|---|---|---|---|---|
| `ADDR_BLINK_MASK` | 0x5 | established |  | Selects the blink mask register. [public] |
| `ADDR_COMMAND` | 0x6 | established |  | Selects the command register. [public] |
| `ADDR_READ_MASK` | 0x4 | established |  | Address register value that selects the read mask register at port ctrl. [public] datasheet Table 3. |
| `ADDR_TEST` | 0x7 | established |  | Selects the control and test register. [public] |
| `INIT_COMMAND` | 0xc1 | established |  | Command register value written at init: 5:1 multiplexing, palette RAM in use, blink off, overlay 0 enabled, overlay 1 disabled. [binary] _Gr2DacInit and the PROM; decode from [public]. |
| `INIT_READ_MASK` | 0x0 | established |  | Read mask written at init: all planes masked, so every pixel reads palette entry 0 and the screen is black until Gr2BlankScreen writes 0xff. [binary] |
| `OVERLAY_ENTRIES` | 0x4 | established |  | Overlay colour registers. Init writes 0, 1, 2, 3 into them. [binary] |
| `PALETTE_ENTRIES` | 0x100 | established |  | Palette RAM entries; init writes the identity ramp (entry n holds n) to all three chips, and Gr2SetGammaRamp overwrites it from three 256-byte arrays. The address register wraps to 0 after entry 255. [binary] [public] |
| `UNBLANK_READ_MASK` | 0xff | established |  | Read mask written to unblank. [binary] Gr2BlankScreen (second argument zero). |
