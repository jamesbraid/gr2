<!-- generated from devices/vc1-express/registers.toml by defs-gen - do not edit, change the source -->
<!-- SPDX-License-Identifier: BSD-3-Clause -->
<!-- defs-gen 5 -->
<!-- input sha256 25734a17818e96cd0d8d228db9bbafb76b5aba73b4daabd22058b0bf5bc47127 -->

# VC1 video timing, cursor and display-ID controller on the Express board

The same LSI Logic part as the Indigo Entry board's VC1 (see the newport repository's VC1 page for shared facts) reached through a different port set: seven word-strided ports in the graphics window instead of the REX1 function selector. It runs video timing programs from an external SRAM, generates the hardware cursor, and produces a per-pixel display ID from run-length tables in the same SRAM. Offsets are from the graphics window base (physical 0x1f000000 on the Indigo); each port is the first byte of a 4-byte stride, the command and SRAM ports are half-words. Grades: established means read in full in the shipped Indigo driver archive or PROM, or stated by a published document; inferred means a reasoned reading; unknown means nothing shipped settles it. [binary] marks a software expectation from a shipped binary, [public] a published document or public driver, [vendor-derived] a fact resting on the upstream headers only. Nothing was read on a board. Prose in devices/vc1-express/README.md.

Unit `vc1_express`, macro prefix `VC1X`.

Every item has a grade: established, inferred or unknown. A grade says how the item was derived from its source; it does not claim the item was measured on silicon.

## Registers

| Register | Offset | Access | Width | Count | Space | Reset | Grade | Source |
|---|---|---|---|---|---|---|---|---|
| `command` | 0x6c040 | rw | 16 |  |  | unknown | established |  |
| `xmapmode` | 0x6c044 | rw | 8 |  |  | unknown | unknown |  |
| `sram` | 0x6c048 | rw | 16 |  |  | unknown | established |  |
| `testreg` | 0x6c04c | r | 8 |  |  | unknown | established |  |
| `addrlo` | 0x6c050 | rw | 8 |  |  | unknown | established |  |
| `addrhi` | 0x6c054 | rw | 8 |  |  | unknown | established |  |
| `sysctl` | 0x6c058 | rw | 8 |  |  | unknown | established |  |

### Register `command`

Internal register data port. Set the address pair to an internal register number, then write half-words; the address advances by two after each (cursor x then y are written back to back from address 0x22). Reads of this port never occur in shipped code (revision comes through testreg). [binary] A qtest can discriminate: address 0x22, write two half-words, check the address pair reads back advanced by 4 (inferred).

### Register `xmapmode`

Window to a display-mode table inside the VC1 (the Entry board's equivalent holds the mode words). Express keeps display modes in the XMAP5 chips instead. Unaccessed. Unknown.

### Register `sram`

External SRAM data port. The SRAM is addressed by byte; each half-word transfer advances the address pair by two. Written from timing images and display-ID tables; read back by the dummy-ID builder and Gr2SetMonitor. [binary]

### Register `testreg`

Revision read: after addrhi = 0 and addrlo = 5, the low three bits are stored as the VC1 revision. gfxinfo decodes 1 as A and 2 as B and every captured Indigo prints B, so the Indigo's part reads 2 (inferred from the decode and the captures; no direct read). [binary]

| Bits | Field | Grade | Values | Source | Description |
|---|---|---|---|---|---|
| 2:0 | `revision` | established |  |  |  |

### Register `addrlo`

Low byte of the 16-bit address pair used by command and sram. Readable: the retrace shadow reads it back to save and restore the pair around interrupt-time use. [binary]

### Register `addrhi`

High byte of the address pair. Readable. [binary]

### Register `sysctl`

System control byte; readable (read-modify-write by the retrace handler and Gr2SetMonitor). Bit roles are NetBSD names [public] except as noted: 0 interrupt, 1 timing generator, 2 VC1 core, 3 display IDs, 4 cursor logic, 5 cursor display (established: toggled at retrace), 6 genlock (inferred), 7 video. Values seen: 1 at start, 3 during table loads, 0x0c final in the kernel, 0x3c final in the PROM. Bit 0 is the vertical-interrupt disable: set blocks the retrace latch, clear lets it set (the final values clear it; a comment on the value 1 in the IRIX source says it disables the interrupt) [binary][source]. qtest: with bit 0 set no retrace latch sets over a frame, with it clear one does.

| Bits | Field | Grade | Values | Source | Description |
|---|---|---|---|---|---|
| 7 | `video` | unknown |  |  |  |
| 6 | `genlock` | inferred |  |  |  |
| 5 | `cursor_display` | established |  |  |  |
| 4 | `cursor` | inferred |  |  |  |
| 3 | `did` | inferred |  |  |  |
| 2 | `core` | inferred |  |  |  |
| 1 | `timing` | unknown |  |  |  |
| 0 | `interrupt` | inferred |  |  |  |

## Constants

| Constant | Value | Grade | Source | Description |
|---|---|---|---|---|
| `CURSOR_X_THRESHOLD` | 0x20 | established |  | Cursor x minus hotspot below this selects the standard frame table and adds the board's x adjustment; at or above it selects the cursor-workaround frame table. [binary] constant in the retrace and cursor code. |
| `REG_BLACKOUT` | 0x60 | inferred |  | Internal register 0x60: written 0 at init (colour index 0 on blackout); role inferred. |
| `REG_CURSOR_EP` | 0x20 | established |  | Internal register 0x20: SRAM address of the cursor glyph. [binary] initGr2Cursor, PROM. |
| `REG_CURSOR_MODE` | 0x26 | inferred |  | Internal register 0x26: zeroed at init (a third and fourth half-word zero written after 0x20 point at 0x22 to 0x26). Role inferred. |
| `REG_CURSOR_X` | 0x22 | established |  | Internal register 0x22: cursor x coordinate, followed by 0x24 for y, written as two consecutive half-words. [binary] retrace handler, Gr2PositionCursor. |
| `REG_CURSOR_Y` | 0x24 | established |  | Internal register 0x24: cursor y coordinate. [binary] |
| `REG_DID_DIV` | 0x44 | established |  | Internal register 0x44: horizontal grouping, (width-1)/5 in the high byte and (width-1)%5 in the low byte for a 1280-wide screen (the constant 65284). [binary] Gr2SetMonitor, _Gr2RegisterInit. |
| `REG_DID_END` | 0x42 | established |  | Internal register 0x42: address of the end of the display-ID frame table, 2 * lines past its start. [binary] |
| `REG_DID_EP` | 0x40 | established |  | Internal register 0x40: SRAM address of the display-ID frame table. [binary] |
| `REG_REVISION` | 0x5 | established |  | Internal register 5: address written before reading the revision through testreg. [binary] Gr2ProbeVC1. |
| `REG_VID_ENABLE` | 0x14 | inferred |  | Internal register 0x14: written 0 at init and 8192 by Gr2SetMonitor for a loaded timing file. Role inferred from its name in [vendor-derived] notes. |
| `REG_VID_EP` | 0x0 | established |  | Internal register 0: pointer to the active frame table, 0x800 or 0x900. [binary] _Gr2RegisterInit, Gr2SetMonitor, retrace handler. |
| `SRAM_CURSOR_FRAME_TABLE` | 0x900 | established |  | Frame table for the cursor workaround. [binary] loaded here; NetBSD VIDTIM_CURSFRMT_BASE. |
| `SRAM_CURSOR_GLYPH` | 0xa00 | established |  | Kernel cursor glyph, 128 half-words (256 bytes). The PROM places its glyph at 512 instead and points the cursor pointer register there. [binary] initGr2Cursor; NetBSD CURSOR0_BASE. |
| `SRAM_CURSOR_LINE_LIST` | 0x400 | established |  | Second line-program list used with the cursor workaround frame table. [binary] loaded here; NetBSD VIDTIM_CURSLST_BASE. |
| `SRAM_DID_FRAME_TABLE` | 0xb00 | established |  | Display-ID frame table: one half-word per screen line, each the SRAM address of that line's display-ID line table. [binary] _Gr2RegisterInit. |
| `SRAM_DID_LINE_DEFAULT` | 0x1400 | established |  | Default display-ID line table used for every line at init, and the lowest byte address the kernel's dummy-ID builder accepts. [binary] |
| `SRAM_FRAME_TABLE` | 0x800 | established |  | Frame table (standard). [binary] loaded here; NetBSD VIDTIM_FRMT_BASE. |
| `SRAM_INTERLACED` | 0x9f0 | established |  | Half-word: zero when progressive, 16 when the timing file is interlaced. [binary] _Gr2RegisterInit writes 0, Gr2SetMonitor writes 16 for interlaced files; the name is NetBSD's. |
| `SRAM_LINE_LIST` | 0x0 | established |  | SRAM byte address of the line-program list (standard). [binary] loaded here by _Gr2RegisterInit and Gr2SetMonitor; the name is [public] NetBSD VIDTIM_LST_BASE. |
| `SRAM_SCREENWIDTH` | 0x9f2 | established |  | Half-word: screen width in pixels, written right after the interlace half-word. [binary] |
| `SYSCTL_CURSOR_DISPLAY` | 0x20 | established |  | Bit toggled by the retrace handler to show or hide the cursor at vertical retrace. [binary] |
| `SYSCTL_GENSYNC` | 0x40 | inferred |  | Bit 6: Gr2GetMonitor reports it as the genlock state and Gr2AdjGenlock sets it while reprogramming the clock; Gr2SetMonitor clears it afterwards. NetBSD names it GENSYNC. |
| `SYSCTL_LOAD` | 0x3 | established |  | Written to sysctl while Gr2SetMonitor loads timing tables, with the previous value restored (bits 1:0 cleared) afterwards. Roles inferred. [binary] |
| `SYSCTL_VC1_DID` | 0xc | established |  | Final value the kernel writes to sysctl at init (VC1 and display-ID enable in NetBSD's names). The PROM finishes with 0x3c (adds cursor logic and cursor display). [binary] |
