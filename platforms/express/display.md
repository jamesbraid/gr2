# Express display back end: from the frame buffer to the monitor

How the Indigo's Express (GR2) boards turn frame-buffer bits into video, what the PROM and the IRIX IP20 driver do to bring it up, and
what a QEMU model has to implement. Chip pages: [VC1](../../devices/vc1-express/README.md), [XMAP5](../../devices/xmap5/README.md),
[Bt457](../../devices/bt457/README.md), [clock and board ports](../../devices/clock/README.md), [Bt475](../../devices/bt475/README.md).
The survey is [README.md](README.md); the command side (HQ2, GE7, RE3) is elsewhere. Labels: **established**, **inferred**, **unknown**;
sources **[public]**, **[binary]**, **[vendor-derived]** as defined in each chip page. Nothing was read on a board.

## The path

[public] Elan Graphics Technical Report 4.4: frame buffer (five-way interleaved VRAM) feeds the VC1, which generates timing and the
display ID, and the five XMAP5 chips, which turn pixels, display IDs and cursor into 24-bit RGB; three DACs multiplex the five streams
to the monitor. [binary] corroborates the three layers as separately addressed chips: VC1 at `+0x6c040`, five XMAP5 at `+0x6c100` with a
broadcast window at `+0x6c1a0`, three Bt457 at `+0x6c0a0`, `+0x6c0c0` and `+0x6c0e0`, board configuration and clock at `+0x6c000` and
`+0x6c020`. Established as the addresses the shipped driver touches. The framebuffer-to-VC1 hand-off, the five-way pixel split and the
video bus have no host registers (the TR draws them only).

Per pixel (inferred from the chips' roles, [public] TR plus the register evidence):

1. VC1 produces a 5-bit display ID from its run-length line tables (one table per scan line, shared where lines repeat) and the cursor
   bit from its glyph and position registers.
2. Each XMAP5 looks up the mode word at that ID (buffer, pixel format, CLUT page, overlay enables), picks the framebuffer bits (colour
   index versus direct RGB), applies overlay, popup, underlay and cursor with the auxiliary table, and emits 24 bits.
3. Each Bt457 maps its 8 bits through a palette (identity unless a gamma ramp is loaded), gated by the read mask, and the five pixel
   streams are multiplexed 5:1.

## Bring-up order as shipped (established)

`gr2_earlyinit` (`gr2.o` `0x59c`) and `Gr2Initialize` (`0x1988`) call, in order: `Gr2Reset` (pulse MC control register 0 bit 10,
clear then set, 10 microsecond gap), `Gr2StartClock` ([clock](../../devices/clock/README.md)), then `Gr2Init`, which is
`_Gr2RegisterInit` followed by `_Gr2HQ2RegInit`. `_Gr2RegisterInit` does: retrace-latch pulse, three DAC inits (screen black), VC1
interlace and width words, VC1 timing images by monitor code, frame table pointer, display-ID tables, VC1 internal registers, cursor,
`sysctl = 0x0c`, XMAP5 mode entry 0, XMAP5 misc registers, default text-port colours, CLUT clear. The screen is unblanked later by
`Gr2BlankScreen(board, 0)` (Bt457 read mask `0xff`). The PROM's `Gr2Init` equivalent (`0xbfc0ed5c`) differs in using its own timing images
(sizes by monitor code), a cursor glyph at SRAM `0x200`, a final `sysctl = 0x3c` and no CLUT clear.

Rev below 4 and rev 4 and up differ in the probe and in the clock protocol, nothing else in the display chips (every XMAP5, VC1 and
Bt457 access in the shipped objects is revision independent). Established by reading all display register accesses of `gr2.a`
(`gr2_init.o`, `gr2.o`, `gr2_retrace.o`, `gr2_tport.o`, `gr2_tpucode.o`, `gr2_dma.o` touches none): the only offsets used are
`+0x6c000`, `+0x6c004`, `+0x6c008`, `+0x6c00c`, `+0x6c020`, `+0x6c040` to `+0x6c058`, `+0x6c0a0` to `+0x6c0e4`, `+0x6c110`, `+0x6c114`, `+0x6c11c` and `+0x6c1a0` to
`+0x6c1b4`.

## Monitor selection

| Source | Result |
|---|---|
| Board revision below 4 | monitor code 0 to 7 from `port1` bit 0 and `port2` bits 1:0 |
| Board revision 4 and up | monitor code 0 to 15 from `port0` bits 7:4 |
| Code 1 or 9 | built-in 72 Hz 1280 by 1024 timing (byte-identical to `72hz.u`), 72 Hz clock bytes |
| Code 6 or 14 | no built-in timing, no clock load: a timing file must be loaded by `Gr2SetMonitor`; the probe reports 1024 by 768 for code 6 |
| Any other code | built-in 60 Hz 1280 by 1024 timing (byte-identical to `60hz.u`) |

Which cable or monitor each code means is unknown. [public] TR lists the monitors supported (72, 60, 30 Hz at 1280 by 1024 and 1024 by 768,
NTSC, PAL, 120 Hz stereo); the held timing files are in [vc1-express](../../devices/vc1-express/README.md#monitor-codes-and-the-kernels-built-in-tables). The timing file also decides screen size: the driver stores width and height from the
file at `Gr2SetMonitor` (a 1024-class mode is recorded as width 1025).

## What a QEMU model needs, in layers

1. **Board ports**: byte registers with the probe values for the chosen board configuration (depth, Z, monitor code, backend
   revision, revision above or below 4), most significant lane, and a counter of clock writes. Established as the contract the drivers use.
2. **VC1**: address pair with auto-increment, half-word `command` and `sram` ports over a 32 KiB byte-addressed SRAM (the size is
   [vendor-derived] only; all shipped addresses lie below `0x1500` plus the 0x9f0 words, so 8 KiB suffices for shipped use), `testreg` revision read,
   `sysctl` byte. Scan-out needs only: width and height (from SRAM `0x9f2`, the board record, or the monitor code), the display-ID tables
   (frame table at the pointer in register `0x40`, line tables of `(x << 5) | id` entries) and the cursor registers and glyph. The timing
   programs can be stored and ignored (approximation, to be stated).
3. **XMAP5 x5**: 32 mode words, 8192 CLUT entries, misc registers, pointer behaviour, status `0x02`; broadcast fan-out. Scan-out: CLUT
   indexing by page, direct RGB, buffer bit (inferred fields).
4. **Bt457 x3**: address register, 256-entry palette, control registers (read mask, command), overlay entries; the read mask zero must blank
   the output.
5. **Retrace interrupt**: one pulse per frame on INT2 local 1 bit 7 (GIO line 2) while video is enabled; the driver clears it by pulsing the
   INT2 port register bit 3 (the chips repository's `platforms/ip20/interrupts.md`, local 1 bit 7).
6. **Genlock and the NTSC/PAL adjust files**: `Gr2AdjGenlock` reprograms the clock and reloads SRAM from `adjntsc.bin` and `adjpal.bin`
   and sets `sysctl` bit 6; not decoded here, so not modelled (explicitly unsupported).

## Fidelity limits

Timing (line programs) and the pixel clock are not decoded; a model must label any frame-rate generation an approximation. The mode-word
fields beyond the page and buffer bits are inferred. The DAC and XMAP5 reset states, the XMAP5 `crc` and `bytecount` ports, the
VC1 `xmapmode` port, and cursor colour storage are unknown and must stay observable as unimplemented accesses, not silently accepted.

Questions: [xmap5](../../questions/xmap5.md), [vc1-express](../../questions/vc1-express.md), [dac](../../questions/dac.md),
[display](../../questions/display.md).

## Review (2026-11-23)

Independent re-read of `gr2_init.o`, `gr2_retrace.o`, `gr2_tport.o`, `gr2.o` (`Gr2SetMonitor`), PROM 4.0.5D, the 14 held `.u` files, the Bt457 datasheet text and the public NetBSD header. Chip-level findings are in [xmap5](../../devices/xmap5/README.md#review-2026-11-23); the rest is here.

- CONFIRMED, Bt457: three windows `+0x6c0a0`, `c0`, `e0`; ports at +0, +4, +8, +0xc map to the datasheet's C1/C0 selects (Table 3: 00 address, 01 palette, 10 control, 11 overlay); `_Gr2DacInit` order (`4`/0, `5`/0, `6`/`0xc1`, `7`/0, 256 identity palette writes, four overlay writes 0 to 3); command `0xc1` = 5:1 mux, RAM enabled, blink off, OL0 enabled, OL1 disabled per datasheet CR7 to CR0; unblank `0xff` and blank `0` to address 4 on all three, after polling XMAP5 chip 0 status bit 0 (10000 tries of 1 microsecond); the datasheet's "not initialised at power-up" statements. No access to `+0x6c060` or `+0x6c080` in any kernel object.
- CONFIRMED, clock and board ports: `Gr2Probe` decoding (board revision `~port0 & 0xf`, 0 fails; monitor code `port0 >> 4` at revision 4 and up, `(port1 & 1) | (port2 & 3) << 1` below; backend revision `port1 & 3` or `(~port2 & 0xc) >> 2`; depth and Z tables; 1024 by 768 only for code 6); byte loads from the first byte of each word; `Gr2StartClock` both protocols; the 17-byte table (`c4 0f 15 20 30 4c 50 60 70 80 91 a5 b6 d1 e0 f0 c4`, at `.data+0x788`); the two seven-byte sets (`00 00 00 04 05 04 06` for code 1, `00 10 00 15 18 01 0f` for the rest; code 6 skips); 56 serial bits with bit 1 or'ed into the last; `Gr2SetMonitor` writes `port1` 0 then `0x40` or `0x41` (below 4), 0 then 1 or 5 (4 and up) and `0xa5` to data at the end of the old path.
- CONFIRMED, monitor codes to tables: codes 1 and 9 load set B (200, 28, 192, 28 half-words) and 6 and 14 load nothing, all others set A (237, 25, 218, 25 half-words) at SRAM `0x0`, `0x800`, `0x400`, `0x900`. Set A is byte-identical to the four blocks of `60hz.u` and set B to those of `72hz.u` (compared with a script). All 14 `.u` files reproduce the table in [vc1-express](../../devices/vc1-express/README.md) (size 2176, selector, width, height, interlace, cursor adjustments, format id, rev 4 clock bytes).
- CONFIRMED, VC1 init: all stores in `_Gr2RegisterInit` (sysctl 1, register `0x26`, `0x9f0` and `0x9f2`, register 0 = `0x800` or `0x900` by width below 1026, `0x14`, `0x40`, `0x42`, `0x44 = 0xff04`, `0x60`, sysctl `0x0c`); PROM sizes 122/25/128/25 and 165/24/163/24 half-words, cursor at `0x200` with 256 half-words, final sysctl `0x3c`.
- CONFIRMED, offsets list: the set of display offsets touched by the kernel objects equals the list in the page (checked mechanically over every load and store with a `0x7`-based displacement).
- WRONG (fixed in vc1-express): the 72 Hz line-count total. The frame table records sum to 1105 for 60 Hz as stated; for 72 Hz the same parse gives 1101 only up to the 15-line record and 1103 with the two one-line records that follow it. The observation (neither matches 1066 or 1072) stands; the 60 and 72 Hz tables also end in a differently shaped tail, so "count" is not settled.
- GRADE: `Gr2Probe` stores one more field in the board record (offset 56: `~(port2 >> 4) & 3` at revision 4 and up, `~(port1 >> 2) & 3` below) that the clock page does not mention. What it means is unknown; the page should list it as read and unexplained.
- UNVERIFIED: the Elan TR passages (the PDF text was not re-read), the retrace interrupt wiring (INT2 local 1 bit 7), `Gr2AdjGenlock`, `Gr2PositionCursor` arithmetic, the 1 ms and 3 microsecond delays, the PROM's 20000 microsecond wait, PROM 4.0.5G. The ICS1562 attribution is the page's own inference and stays one.
- Provenance: no fact graded established rests on [vendor-derived] alone in these pages or their registers.toml files.
