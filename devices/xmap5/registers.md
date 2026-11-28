<!-- generated from devices/xmap5/registers.toml by defs-gen - do not edit, change the source -->
<!-- SPDX-License-Identifier: BSD-3-Clause -->
<!-- defs-gen 5 -->
<!-- input sha256 6396c45c31f5677aa6472288571ce1b4f20590c64e4f4e0ac42d11174353cf35 -->

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

Miscellaneous register file, written through one port after the address pair is set; the diagnostic sizes it at six bytes. Init writes 0, 0, 0, 14, 0 after address 0, so the port auto-increments (inferred from five writes to one address). [source] The diagnostic program's XMAP5 test and its header name the first three bytes the blackout red, green and blue, the byte at address 3 a popup page value and the byte at address 4 a cursor value (its colour test sets address 3 and writes those two in turn); the sixth byte is unnamed. The init writes 14 at address 3 and 0 at address 4, while the diagnostic uses 0 and 15. Reads never occur in shipped code.

### Register `mode`

Mode table port. The target entry is chosen by addrlo (byte address 4 * display ID, addrhi 0) before each write; init writes entry 0 and the retrace and display-mode paths write one entry per call. The diagnostic program's mode-table test assumes a write advances the address by 4 (its own comment says to assume it); no shipped driver depends on it, since the driver sets the address before every write, so the advance is a software expectation and not shown by any shipped code. A qtest can discriminate: write 0x82000000 at address 0 through the broadcast window and read nothing back (no read path); write through the broadcast window and check all five chips were updated.

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
| `MODE_WORD` | 32 | established |  |

### Word `MODE_WORD`

Mode table word, one per display ID, written through the mode port at byte address 4 * ID. Field boundaries are [source] the IRIX diagnostic program's XMAP5 test, which composes words from named fields (pixel mode, pixel page, data format, alternate video, overlay and underlay enables, auxiliary page, popup page, popup mode); they are cross-checked in [binary] by the boot word 0x82000000 (page 16, eight-bit bank 0, colour index: the text port's colours live at CLUT index 4096) and by the shipped X server, which builds words as page << 27 | 0x800 | base, forces 0xf00000 when bit 8 is clear and sets or clears bit 24 for the second buffer (disassembly of expValidateMode). The role of each field is read from its name and how the diagnostic pairs values, so the roles are inferred where a field says so.

| Bits | Field | Grade | Values | Source | Description |
|---|---|---|---|---|---|
| 31:27 | `pix_page` | established |  |  | Pixel page: CLUT page of 256 entries used by colour-index pixels; page 16 is the text port. [source] field; [binary] boot word and X server. |
| 26:24 | `pix_mode` | established |  |  | Pixel mode: 0 and 1 four-bit bank 0 and 1, 2 and 3 eight-bit, 4 and 5 twelve-bit, 6 sixteen-bit, 7 twenty-four-bit. [source] codes; the low bit is the bank, which the X server flips for the second buffer of a double-buffered window ([binary]). |
| 23:20 | `overlay_enable` | established |  |  | Overlay enables, four bits. [source] field; [binary] the X server sets all four (0xf00000) when underlay (bit 8) is clear. Which plane each bit enables is inferred. |
| 19:18 | `alt_video` | established |  |  | Alternate video mode: 0 off, 1 over, 2 under, 3 replace. [source] field and codes; the diagnostic defines the field but writes it zero in every word it composes, and no shipped X driver code read here sets it. |
| 17:16 | `pd_mode` | established |  |  | Pixel data format: 0 colour index, 1 direct RGB, 2 colour-index multimode (the diagnostic pairs it with the two four-bit pixel modes only), 3 blackout. [source] field and codes. |
| 15:14 | `popup_flags` | inferred |  |  | Two popup bits named for a popup pixel (bit 15) and a popup override (bit 14). [source] field names only; nothing read sets them. |
| 13:9 | `aux_page` | established |  |  | Auxiliary colour page, five bits. [source] field; [binary] the X server always ORs 0x800, which is page 4. |
| 8 | `underlay_enable` | established |  |  | Underlay enable. [source] field; [binary] the X server forces the four overlay enables on when this bit is clear. The diagnostic header also defines a popup field that spans bits 8:7; it overlaps this bit and the diagnostic never uses it, so that field is inferred to belong to a different view of the word. |
| 7:0 | `popup_mode` | inferred |  |  | Popup page in bits 4:0 and popup mode in bits 6:5 (codes off, eight-bit, four-bit bank 0 and 1). [source] field names and codes; the diagnostic writes the page and never the mode, and no shipped code read sets either. |

## Constants

| Constant | Value | Grade | Source | Description |
|---|---|---|---|---|
| `BOOT_MODE_WORD_DID0` | 0x82000000 | established |  | Mode word written for display ID 0 at init. [binary] _Gr2XMAPInit1 and the PROM. Read with the page field at bits 31:27 it selects CLUT page 16, matching the text port base (inferred reading, see MODE_WORD). |
| `CHIP_COUNT` | 0x5 | established |  | Five XMAP5 chips per board. [public] Elan Graphics Technical Report 4.4.2 and the NetBSD memory map comment; [binary] the driver addresses only chip 0 and the broadcast window. |
| `CLUT_ENTRIES` | 0x2000 | established |  | Colour table entries: 13 address bits, high byte masked with 0x1f. [binary] _Gr2XMAPInit3 clears entries 256 to 8191; Gr2TpMapcolor masks the index to the same five high bits. [public] NetBSD masks the same way. 24 bits per entry written as three bytes. |
| `MODE_ENTRIES` | 0x20 | established |  | Mode table entries, one per display ID. [binary] the retrace handler walks 32 entries and addresses entry n at byte address 4 * n. [public] Elan TR 4.4.1: up to 32 window styles. |
| `TEXTPORT_CLUT_BASE` | 0x1000 | established |  | CLUT index of the text port's eight colours: 4096 plus the colour number. [binary] Gr2TpMapcolor adds 4096; _Gr2XMAPInit2 loads eight defaults at address 4096, which _Gr2XMAPInit3 then clears (the text port reloads through Gr2TpMapcolor). |
| `WINDOW_SIZE` | 0x20 | inferred |  | Bytes per chip window; chip n sits n windows after chip 0 and the broadcast window one step after chip 4. [public] The NetBSD memory map comment gives one span for the five chips. [binary] consistent: the retrace handler saves chip 0's address from its window and restores it through the broadcast window at the same register offsets, and chip 0's status is read at window offset 0x1c. |
