<!-- generated from devices/xmap5/registers.toml by defs-gen - do not edit, change the source -->
<!-- defs-gen 4 -->
<!-- input sha256 16b6070bb233d1af1da4ef209d70365aa464954f82eda820d7ca338b5819fb36 -->

# XMAP5 multimode colour mapper (five per Express board)

Per-pixel window-mode and colour-index mapper between the VC1 and the DACs. Five identical chips each handle one pixel in five; software addresses chip 0 to 4 through five 32-byte windows and all five at once through a broadcast window one step after chip 4 (addresses in the README), with the same eight-register layout in each window. Offsets here are within one window. Each register is one byte (the mode port is a word) on a 4-byte stride; a big-endian CPU addresses the first byte of the stride, so the data sits in the most significant lane. Grades: established means read in full in the shipped Indigo driver archive or PROM, or stated by a published document; inferred means a reasoned reading; unknown means nothing shipped settles it. [binary] marks a software expectation from a shipped binary, [public] a published document or public driver, [vendor-derived] a fact that rests on the upstream headers and never supports an established grade. Nothing was read on a board. Prose in devices/xmap5/README.md.

Unit `xmap5`, macro prefix `XMAP5`.

Every item has a grade: established, inferred or unknown. A grade says how the item was derived from its source; it does not claim the item was measured on silicon.

## Registers

| Register | Offset | Access | Width | Count | Space | Reset | Grade | Source |
|---|---|---|---|---|---|---|---|---|
| `misc` | 0x0 | w | 8 |  |  | unknown | inferred |  |
| `mode` | 0x4 | w | 32 |  |  | unknown | established |  |
| `clut` | 0x8 | w | 8 |  |  | unknown | established |  |
| `crc` | 0xc | rw | 8 |  |  | unknown | unknown |  |
| `addrlo` | 0x10 | rw | 8 |  |  | unknown | established |  |
| `addrhi` | 0x14 | rw | 8 |  |  | unknown | established |  |
| `bytecount` | 0x18 | rw | 8 |  |  | unknown | unknown |  |
| `fifostatus` | 0x1c | r | 8 |  |  | unknown | established |  |

### Register `misc`

Miscellaneous register file, written through one port after the address pair is set to 0. Init writes 0, 0, 0, 14, 0 in order, so the port auto-increments over five internal registers (inferred from five writes to one address). Meaning of each is [vendor-derived] only: blackout red, green, blue; a four-bit overlay and popup page value; a cursor index. Reads never occur in shipped code.

### Register `mode`

Mode table port. The target entry is chosen by addrlo (byte address 4 * display ID, addrhi 0) before each write; init writes entry 0 and the retrace and display-mode paths write one entry per call. Whether the address advances by 4 after a write is not shown (the driver sets it before every write). A qtest can discriminate: write 0x82000000 at address 0 through the broadcast window and read nothing back (no read path); write through the broadcast window and check all five chips were updated.

### Register `clut`

Colour table data port. Entry n is selected by addrhi = (n >> 8) & 0x1f and addrlo = n & 0xff; three byte writes (red, green, blue) store one entry and the address then advances to the next entry (the init clear writes 7936 entries from address 256 without resetting the address). [binary] Writes while the status busy bit is set are avoided by the callers. A qtest can discriminate: set address 4096, write three bytes, set address 4096 again, write three more and check entry 4097 was not touched.

### Register `crc`

Named CRC by NetBSD. Never accessed by the Indigo driver or PROM. Unknown.

### Register `addrlo`

Low address byte for the mode, colour table and misc ports. Readable: the retrace handler reads chip 0's pair and writes it back through the broadcast pair. A write through the broadcast window sets all five chips. [binary]

### Register `addrhi`

High address byte (five bits used for the colour table). Same rules as addrlo. [binary]

### Register `bytecount`

Named byte count by NetBSD. Never accessed by shipped drivers. Unknown.

### Register `fifostatus`

Status of the write FIFO in front of the chip (name from NetBSD [public]). Bit 0 set means busy: callers poll until it clears before mode, colour table and DAC writes (Gr2BlankScreen, Gr2SetGammaRamp, the retrace swap; 10 ms bound in the first). Bit 1 set means room for a burst: _Gr2XMAPInit3 waits up to 10 ms for it to be set before each 256-entry block. An idle FIFO therefore reads bit 1 set and bit 0 clear. [binary] Bit 2 (overflow) is [vendor-derived] only. A qtest can discriminate: read after reset has bit 0 clear and bit 1 set; during a burst of colour writes bit 0 may be observed set.

| Bits | Field | Grade | Values | Source | Description |
|---|---|---|---|---|---|
| 2 | `overflow` | unknown |  |  |  |
| 1 | `room` | established |  |  |  |
| 0 | `busy` | established |  |  |  |

## Words

| Word | Width | Grade | Source |
|---|---|---|---|
| `MODE_WORD` | 32 | inferred |  |

### Word `MODE_WORD`

Mode table word, one per display ID, written through the mode port at byte address 4 * ID. Bit meaning is inferred: [binary] two points tie it to shipped code (the boot word 0x82000000 selects page 16 which is where the text port's colours live; the shipped X server builds words as page << 27 | 0x800 | base, forces 0xf00000 when bit 8 is clear, and toggles bit 24 for the second buffer, read from an upstream decompilation not re-checked here); the remaining fields rest on [vendor-derived] notes.

| Bits | Field | Grade | Values | Source | Description |
|---|---|---|---|---|---|
| 31:27 | `pix_page` | inferred |  |  | CLUT page (256 entries each) for colour-index pixels; page 16 is the text port. |
| 26:24 | `pix_mode` | inferred |  |  | Pixel format: 0 and 1 four-bit bank 0 and 1, 2 and 3 eight-bit, 4 and 5 twelve-bit, 6 sixteen, 7 twenty-four; odd values select bank 1 (double buffer). [vendor-derived] except that bit 24 toggles with the buffer ([binary], X server). |
| 23:20 | `overlay_enable` | inferred |  |  | Overlay plane enables; the X server sets all four (0xf00000) when underlay is off. |
| 19:18 | `alt_video` | unknown |  |  | Alternate video (live video) mode. [vendor-derived] only. |
| 17:16 | `pd_mode` | inferred |  |  | Pixel display mode: colour index, direct RGB, multimode, blackout. [vendor-derived] only. |
| 15:14 | `popup_flags` | unknown |  |  | [vendor-derived] only. |
| 13:9 | `aux_page` | inferred |  |  | Page of the 16-entry auxiliary colour block for overlay and popup planes; the X server always sets 4 (value 0x800). |
| 8 | `underlay_enable` | inferred |  |  | Underlay enable; clear makes the X server force the four overlay enables on. |
| 7:0 | `popup_mode` | unknown |  |  | Popup mode and page. [vendor-derived] only. |

## Constants

| Constant | Value | Grade | Source | Description |
|---|---|---|---|---|
| `BOOT_MODE_WORD_DID0` | 0x82000000 | established |  | Mode word written for display ID 0 at init. [binary] _Gr2XMAPInit1 and the PROM. Read with the page field at bits 31:27 it selects CLUT page 16, matching the text port base (inferred reading, see MODE_WORD). |
| `CHIP_COUNT` | 0x5 | established |  | Five XMAP5 chips per board. [public] Elan Graphics Technical Report 4.4.2 and the NetBSD memory map comment; [binary] the driver addresses only chip 0 and the broadcast window. |
| `CLUT_ENTRIES` | 0x2000 | established |  | Colour table entries: 13 address bits, high byte masked with 0x1f. [binary] _Gr2XMAPInit3 clears entries 256 to 8191; Gr2TpMapcolor masks the index to the same five high bits. [public] NetBSD masks the same way. 24 bits per entry written as three bytes. |
| `MODE_ENTRIES` | 0x20 | established |  | Mode table entries, one per display ID. [binary] the retrace handler walks 32 entries and addresses entry n at byte address 4 * n. [public] Elan TR 4.4.1: up to 32 window styles. |
| `TEXTPORT_CLUT_BASE` | 0x1000 | established |  | CLUT index of the text port's eight colours: 4096 plus the colour number. [binary] Gr2TpMapcolor adds 4096; _Gr2XMAPInit2 loads eight defaults at address 4096, which _Gr2XMAPInit3 then clears (the text port reloads through Gr2TpMapcolor). |
| `WINDOW_SIZE` | 0x20 | inferred |  | Bytes per chip window; chip n sits n windows after chip 0 and the broadcast window one step after chip 4. [public] The NetBSD memory map comment gives one span for the five chips. [binary] consistent: the retrace handler saves chip 0's address from its window and restores it through the broadcast window at the same register offsets, and chip 0's status is read at window offset 0x1c. |
