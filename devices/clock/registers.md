<!-- generated from devices/clock/registers.toml by defs-gen - do not edit, change the source -->
<!-- defs-gen 3 -->
<!-- input sha256 467273ff471ddf2134ff68f52c6be88c8ce534408f7b0b63cc8677a1cd2e2738 -->

# Express board configuration ports and pixel clock control

The first ports of the display back end form one byte-wide gate-array block that the Indigo boot PROM and kernel driver read to learn the board revision, backend revision, memory slots, Z buffer, colour depth and monitor code, and write to select and load the pixel clock. The read and write sides of a port share one address. Offsets are from the graphics window base (physical 0x1f000000 on the Indigo) and name the byte a big-endian CPU addresses: every port is one byte at the first byte of a 4-byte stride (the most significant lane of the word), and every shipped access is a byte load or store. Grades: established means read in full in the shipped driver or PROM, or stated by a published document; inferred means a reasoned reading; unknown means nothing shipped settles it. [binary] marks a software expectation from a shipped binary, [public] a published document or public driver. Nothing was read on a board. Prose in devices/clock/README.md.

Unit `clock`, macro prefix `GR2_CLK`.

Every item has a grade: established, inferred or unknown. A grade says how the item was derived from its source; it does not claim the item was measured on silicon.

## Registers

| Register | Offset | Access | Width | Count | Space | Reset | Grade | Source |
|---|---|---|---|---|---|---|---|---|
| `port0` | 0x6c000 | rw | 8 |  |  | unknown | established |  |
| `port1` | 0x6c004 | rw | 8 |  |  | unknown | established |  |
| `port2` | 0x6c008 | r | 8 |  |  | unknown | established |  |
| `port3` | 0x6c00c | r | 8 |  |  | unknown | established |  |
| `data` | 0x6c020 | w | 8 |  |  | unknown | established |  |

### Register `port0`

Read: board revision and, on revision 4 and up, the monitor code. Bits 3:0 read back inverted (board revision is the complement, zero means no board). On revision 4 and up bits 7:4, not inverted, are the monitor code. Write: pixel clock select, see the SEL constants. The read and write sides are different functions at one address. [binary] A qtest can discriminate: a byte read returns the board revision complemented in bits 3:0; a word read has the byte in the most significant lane (NetBSD masks the low bits instead, see questions/display.md).

| Bits | Field | Grade | Values | Source | Description |
|---|---|---|---|---|---|
| 7:4 | `monitor_code_rev4` | established |  |  |  |
| 3:0 | `board_rev_n` | established |  |  |  |

### Register `port1`

Read below revision 4: bit 0 is monitor code bit 0; bits 3:2 both set mean no Z buffer. Read at revision 4 and up: bits 1:0 backend revision as read (both set fails the probe), bit 4 set means 24-bit colour (clear means 8), bit 5 set means Z buffer present. Write: pixel clock load control: 0 then 0x40 (0x41 interlaced) below revision 4; 0 then 1 (5 interlaced) at revision 4 and up. The roles of the written bits are inferred. [binary]

| Bits | Field | Grade | Values | Source | Description |
|---|---|---|---|---|---|
| 5 | `z_present_rev4` | established |  |  |  |
| 4 | `depth24_rev4` | established |  |  |  |
| 3:2 | `no_z_rev3` | established |  |  |  |
| 1:0 | `low2` | established |  |  |  |

### Register `port2`

Board revision below 4 only. Bits 3:2 read back inverted as the backend revision (zero fails the probe); bits 1:0 are monitor code bits 2:1. Not read at revision 4 and up. [binary]

| Bits | Field | Grade | Values | Source | Description |
|---|---|---|---|---|---|
| 3:2 | `backend_rev_n` | established |  |  |  |
| 1:0 | `monitor_code_hi` | established |  |  |  |

### Register `port3`

Board revision below 4 only: frame-buffer memory slot presence; a slot is empty when both of its bits are set (slot A bits 1:0, slot B bits 3:2, slot C bits 5:4). Colour depth is 24 with all three populated, 16 with A and B only, otherwise 8. [binary] NetBSD multiplies the populated count by 8 instead [public].

| Bits | Field | Grade | Values | Source | Description |
|---|---|---|---|---|---|
| 5:4 | `slot_c_empty` | established |  |  |  |
| 3:2 | `slot_b_empty` | established |  |  |  |
| 1:0 | `slot_a_empty` | established |  |  |  |

### Register `data`

Pixel clock serial or command port. Board revision below 4: 17 command bytes. Revision 4 and up: 56 single-bit writes (bit 0 is the data bit, bit 1 set on the last). The chip is not identified. [binary] A qtest can discriminate: count the writes between a port1 write of 0 and the next port1 write (17 or 56).

| Bits | Field | Grade | Values | Source | Description |
|---|---|---|---|---|---|
| 1 | `last` | established |  |  |  |
| 0 | `bit` | established |  |  |  |

## Constants

| Constant | Value | Grade | Source | Description |
|---|---|---|---|---|
| `BOARD_REV_SPLIT` | 0x4 | established |  | Board revisions below 4 and 4 and above are decoded and clocked differently. [binary] Gr2Probe and Gr2StartClock both compare the board revision (inverted low nibble of port0) with 4. |
| `COMMAND_BYTES_REV3` | 0x11 | established |  | Board revision below 4: a clock load is 17 command bytes written one at a time to data. [binary] Gr2StartClock; the same table is in the 4.0.5D PROM. |
| `EXTRA_BYTE_REV3` | 0xa5 | established |  | Gr2SetMonitor and Gr2AdjGenlock write 0xa5 to data after loading new timing on board revisions below 4; the byte also sits at index 11 of the 17-byte table. Role unknown. [binary] |
| `LOAD_REV3` | 0x40 | inferred |  | Written to port1 after the 17 command bytes on board revisions below 4 (0x41 when the timing file is interlaced). Role inferred. [binary] Gr2StartClock, Gr2SetMonitor. |
| `SEL_60HZ` | 0x1 | inferred |  | Written to port0 before the clock load on board revisions below 4, for every monitor code except 1 and 6. Role (oscillator or mode select) inferred: the 60 Hz and 72 Hz timing files carry the same 17 command bytes but this selector differs. [binary] Gr2StartClock. |
| `SEL_72HZ` | 0x2 | inferred |  | Selector written to port0 for monitor code 1 on board revisions below 4; the 72 Hz timing file carries 2. [binary] Gr2StartClock. |
| `SEL_OTHER` | 0x4 | inferred |  | Selector carried by the 30 Hz, 50 Hz, ccir, NTSC, PAL, presenter, rs343a and iris3k timing files (the 48 Hz and st492 files carry 1, 60 Hz 1, 72 Hz 2). The 4.0.5D PROM also writes 4 when the backend revision byte is 1. Role inferred. |
| `SEL_REV4` | 0x7 | established |  | Written to port0 before a 56-bit clock load on board revisions 4 and up. [binary] Gr2StartClock and Gr2SetMonitor. |
| `SERIAL_BYTES_REV4` | 0x7 | established |  | Board revision 4 and up: a clock load is 7 bytes sent least significant bit first as 56 single-bit writes to data; the final bit also carries bit 1. [binary] Gr2StartClock and Gr2SetMonitor; the 4.0.5G PROM holds the two 7-byte tables, the 4.0.5D PROM does not. |
