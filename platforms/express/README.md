# Express graphics (GR2) on the Indigo: survey

What the Express family is, which chips each board carries, how the Indigo host reaches and probes it, and what the shipped
software can tell us about each chip. This is a survey and a reading plan, not a register map. The host-visible window the PROM
and kernel touch is started in [devices/hq2](../../devices/hq2/README.md).

Labels follow [AGENTS.md](../../AGENTS.md): **established** (read in full, with object, address or page), **inferred** (reasoned,
reasoning given), **unknown**. The upstream headers in this repository are notes from another project and are not cited as
evidence; where one of them disagrees with a finding the disagreement is in [questions](../../questions/README.md).

Sources, in order used:

- *IP20 kernel objects*: `usr/cpu/sysgen/IP20boot/gr2.a` from the IRIX 6.5 base media and its members (`gr2_init.o`, `gr2.o`,
  `gr2_dma.o`, `gr2_retrace.o`, `gr2_tport.o`, `gr2_tpucode.o`), read as disassembly with relocations. Offsets below are
  object offsets within the member. SHA-256 in [references/binaries.md](../../references/binaries.md).
- *Microcode*: `usr/gfx/ucode/hq2.bin` and `ge7.bin`, header words only.
- *Elan TR*: SGI, Elan Graphics Technical Report 1.0, 1992 (`docs/ElanTR - Elan Graphics Technical Report.html`). Published.
- *NetBSD*: `sys/arch/sgimips/gio/grtwo.c` and `grtworeg.h` (public driver, tree revision `07004b2a9dac`). A driver's expectation.
- *chips gio page*: `platforms/ip20/gio.md` in the chips workspace (reviewed; covers the PROM probe).
- *Parts list*: a third-party SGI part-number listing (`4dwm-partnumbers`, in the Library cache). Secondary: board names and
  geometry-engine counts only.

## The family

Elan Graphics Technical Report, sections 1 and 4 (established, published): the subsystem has 25 custom chips of seven designs
(GE7, RE3, HQ2, VC1, ZRB1, RB1, XMAP5), five daughterboards plugged into a base motherboard, five pipelined stages (command
engine, geometry subsystem, raster engine, framebuffer, display subsystem), a 1280 by 1024 screen at 60 or 72 Hz, a 5-way
interleaved framebuffer of 56 bits per pixel including Z, a separate Z buffer with twice the framebuffer bandwidth, and a GIO-32
host connection with a graphics FIFO inside the HQ2.

| Product | Host | Geometry engines | Colour | Z buffer | Grade and source |
|---|---|---|---|---|---|
| Indigo XS | Indigo | one | 8-bit (Virtual24) | optional 24-bit | **Shipped.** Colour and Z: established, Elan TR section 1. One GE7: **established**: the IRIX inventory code names a one-engine board without the 24-plane flag "GR2-XS" (the hinv source, and the kernel sets the one-engine flag from the probe count at `gr2.o` `0x10000820`); eight `hinv` captures of "Graphics board: GR2-XS" on R4000 and R3000 Indigos are in the Library mail archive (below); an SGI engineer's posting says XS24Z has one GE7 and XZ two. No `gfxinfo` capture of an XS is held, so the plane count rests on the TR and the name. |
| Indigo XS24 | Indigo | one | 24-bit | optional 24-bit | One GE7 established by the same decode and by `gfxinfo` captures ("1 GE, 1 RE, 24 bitplanes"). |
| Indigo XZ | Indigo | two | 24-bit | required (the inventory adds " missing Z" without it) | Two GE7: established by `gfxinfo` captures ("2 GEs") and the inventory decode; the parts list (GR2-2 board) agrees. The TR predates XZ. |
| Indigo Elan | Indigo | four | 24-bit | standard 24-bit, 4 stencil planes | Established, Elan TR section 1 and 4.2 ("four geometry engines"). |
| Extreme, XZ, Elan on Indigo2 | Indigo2 | unknown | unknown | unknown | **Unknown.** The driver names `-XS`, `-XZ`, `-Elan` and `-Extreme` as renderer-name suffixes (see below). Topology is not transferable from Indigo. |

Board-name suffix strings: `-XS`, `-XZ` and `-Elan` sit together in the n32 GL core for the Indigo GR2
(`usr/gfx/arch/IP12GR232/libGLcore.so`, near file offset `0x112028`); `-Extreme` is a separate string in the same file (`0x10b068`).
Established as strings; which board value selects which suffix is **unknown** (not read).

The kernel driver counts geometry engines itself (`_Gr2ProbeGEs`, below) and `gr2_init` (`gr2.o` `0x778`) has a four-way branch
on the count for 1, 2, 4 and 8, each setting a different flag in the inventory entry (any other count sets none). So the software
handles eight-engine boards. Established that the code handles eight; that an eight-engine Indigo board shipped is **unknown**.

Boards named in the parts list (secondary, names only): GR2 base board, VM2 video memory, VB1.1 video buffer, a Z-buffer board
and GE7 jumper boards, which fits the TR's five daughterboards. Which daughterboard carries which chip is **unknown**. Photographs
of an XS24-Z board set are held in the Library cache (`photos/bukosek-indigo/express/`) and have not been read for chip markings.

## Chips and what is known

Per chip, grades are for what a model needs. "Host window" means what the PROM and IP20 kernel touch.

| Chip | Role | Established | Inferred | Unknown |
|---|---|---|---|---|
| HQ2 | Command engine, graphics FIFO, microcode sequencer for itself and the GE7 array, GIO interface and DMA | Exists, in the TR, with FIFO inside it. Host window offsets at `+0x6a000`..`+0x6b004` (the 16-word attribute jump table, status word, GE count, FIFO thresholds, microstore address and load registers, probe word): see [hq2](../../devices/hq2/README.md). Probe word `0xdeadbeef` at `+0x6a07c`. Microcode load procedure and image magic. | Meaning of the status word's bit 5 and of the level field; the `+0x6a06c` upper half as a revision. | Instruction set, token numbering, what generates the two interrupts, DMA engine registers, everything not touched by the IP20 driver. |
| GE7 | 32-bit floating point geometry engine, SIMD under HQ2's sequencer | Count 1 to 8 from the probe, 1, 2, 4 or 8 handled by the driver (software). Presence probe: write-and-read-back of five words at `+0x0, +0x7c, +0xfc, +0x17c, +0x1fc` inside a 1 KiB slot, slot `n` at `+0x68000 + 0x400 * n`. The ucode load window at `+0x683e0`..`+0x683ec` plus `+0x6a064`. | One GE7 per slot; slot 0 always assumed present. | Microcode word layout (128-bit assumed by the TR's "wide microinstruction memory" only), data RAM map, the register at `+0x683f4` (revision read) versus NetBSD's `+0x680fc`. |
| RE3 | Raster engine, 25 to 40 stage pipeline | One per board (TR). NetBSD maps register banks at `+0x6c200`, `+0x6c280`, `+0x6c600`. | The IP20 driver does not touch these directly except through the FIFO and microcode. | All register content. |
| VC1 | Video timing generator, cursor, display-ID tables (run-length windows) | Registers at `+0x6c040`..`+0x6c058`: half-word command and SRAM ports, byte address low and high at `+0x6c050`, `+0x6c054`, a control byte at `+0x6c058`, an internal-register read at `+0x6c04c`. An internal register 5 low three bits are read as the chip revision. SRAM loaded at SRAM offsets `0x0`, `0x800`, `0x400` and `0x900` from per-monitor-code images (`_Gr2RegisterInit`, two sets of sizes chosen by monitor code), the cursor glyph at `0xa00` (`initGr2Cursor`, 128 half-words), and two generated tables at `0x1400` and `0xb00` (the second sized by screen height). | Timing images are per monitor code and are not the `vof` files. | Command set, SRAM format, cursor encoding, which monitor code is which timing. |
| XMAP5 | Per-pixel window and colour mode mapper, five on a board | A broadcast ("all") window at `+0x6c1a0` with the five per-chip windows below it; the kernel writes its address registers at `+0x6c1b0` and `+0x6c1b4` (window base plus `0x10`, `0x14`, matching NetBSD's per-chip offsets). NetBSD's `XMAPALL_ADDRLO`, `ADDRHI`, `BYTECOUNT` and `FIFOSTATUS` constants at `+0x6c190`..`+0x6c19c` are chip 4's registers (window base `0x6c180`), inferred an error in that header; init sequence at `_Gr2XMAPInit1` to `3`; chip 0 status byte at `+0x6c11c`, bits 0 and 1 polled as "busy". | Five instances (NetBSD's address span `0x6c100`..`0x6c19f` is 5 x 0x20). | Mode word format, colour table RAM layout beyond 8192 entries of three bytes written in `_Gr2XMAPInit3`. |
| Colour DAC | Bt457 (three, one per colour) per the datasheet shipped upstream; a Bt479 triple DAC appears in NetBSD's map | The IP20 driver initialises three single-colour DACs at `+0x6c0a0`, `+0x6c0c0`, `+0x6c0e0` (`_Gr2DacInit`) and blanks through them (`Gr2BlankScreen`). | The three are the Bt457 parts (identity from NetBSD's map and the datasheet in `docs/`, not from the driver). | Whether any Indigo board carries a Bt479 (`+0x6c060`, `+0x6c080`: not touched by the IP20 driver). |
| Z buffer (ZRB1, RB1, VM2/Z boards) | Z read-write and read blocks, video RAM | Present on boards by TR; the probe reads two or three board-configuration bits for Z presence. | -- | Everything behind the RE3. |
| Clock | Pixel clock generator | Bit-serial programming through byte writes at `+0x6c020`, with control bytes at `+0x6c000` and `+0x6c004` (`Gr2StartClock`), values from a table in `.sdata`. The write side of `+0x6c000` is the same address as the board revision read. | -- | Which part, what the table values select. |

## The GIO window and the PROM probe

From the chips gio page (reviewed): the graphics slot is `0x1f000000`..`0x1f3fffff` (4 MiB) and has no product ID word. The
PROM probes it by reading the word at base `+0x6a07c`, which must read `0xdeadbeef`. Board version is the low nibble of the
inverted byte at base `+0x6c000`; zero means no board. The same two facts, re-read in the IP20 kernel object `gr2_init.o`,
`Gr2Probe` at `0x16c`: `badaddr` on `base + 0x6a07c`, then a word read compared with `0xdeadbeef`, which the object holds as a
64-bit constant `0xffffffffdeadbeef` compared against the sign-extended load (established).

`Gr2Probe` then fills a probe record (offsets within it, from the stores; named by role, record layout **inferred**):

| Record byte | Value | Source |
|---|---|---|
| 46 | board revision: `~byte(+0x6c000) & 0xf`, probe fails if 0 | established |
| 52 | backend revision: the inverted bits 3:2 of `+0x6c008` (below 4), probe fails if 0; bits 1:0 of `+0x6c004` stored as read (4 and up), probe fails if both are set | established |
| 41 | colour depth: 8, 16 or 24 from three memory-slot presence bits at `+0x6c00c` (revisions below 4), or 24 / 8 from bit 4 of `+0x6c004` (revision 4 and up) | established |
| 44 | Z buffer present: from bits 2 and 3 of `+0x6c004` (below 4) or bit 5 (4 and up) | established |
| 45 | monitor code: `(+0x6c004 bit 0) \| (+0x6c008 bits 1:0) << 1` below 4; high nibble of `+0x6c000` at 4 and up | established |
| 54 | geometry-engine count from `_Gr2ProbeGEs` | established |
| 32, 34 | width and height: 1280 by 1024, or 1024 by 768 when the monitor code is 6 | established |
| 47, 48, 49, 51 | MC revision flag (`mc_rev_level` or `0x80`), a half-word read from `+0x6a06c` shifted down 16, bits 7:5 of a word read from `+0x683f4` after writing zero there, and the VC1 revision | established that these are read; naming as revisions is inferred |

The register reads in `Gr2Probe` are byte loads at `+0x6c000`, `+0x6c004`, `+0x6c008`, `+0x6c00c`, so the data sits in the most significant
byte lane of each word on this big-endian host, while NetBSD masks low bits of a word read. Which is right is a question for
the hardware contract: see [questions](../../questions/README.md).

Before probing, the kernel pulses the MC graphics reset (`Gr2Reset`, `gr2_init.o` `0x0`): clear bit 10 of the MC's control
register 0 at `0xbfa00004`, wait 10 microseconds, set it (established; the polarity is the MC page's, where a set bit releases reset).
The PROM does the same in its graphics check.

Interrupts, as the kernel wires them (`gr2.o` `gr2_init` at `0x778`, calls `setgiovector` twice): GIO line 0 gets `Gr2FIFOInterrupt`
and GIO line 2 gets the retrace handler `gr2_retr_intr`, both for slot 2 (graphics). The argument roles (line, slot) are inferred from the
routing table on the chips interrupts page, which agrees. The FIFO handler clears, then restores, bit 0 of the INT2 byte at
`0xbfb801c7` (a mask bit) around its work (established: `Gr2FIFOHandler` at `0x2a0`).

## What the shipped software gives, and where

| Object | What it tells | State |
|---|---|---|
| `gr2.a` in `IP20boot` | The whole host-side driver: probe, reset, clock, DAC, VC1 and XMAP init, microcode download and verify, FIFO interrupt handler, retrace handler, DMA triggers, context switch. Six members; no Corona I2C member (that one exists only for later hosts). | Symbols and relocations read for every function; `gr2_init.o` and `Gr2Download*` read in full for the window offsets in this survey. Other routines unread. |
| `hq2.bin` | HQ2 microcode: magic half-word `0x965e`, version 1, then header words `0x1c, 0xe0, 0x8cc, 0x4, 0xfc, 0, "V1.0"`. 58682 bytes. | Header only. Loader reads it: 16 words from image offset `0xfc` into the `+0x6a000` jump table, then records of an address half-word and one 32-bit word (at record offset 4) written to `+0x60000 + 4 * address`, then a read-back verify. Established for the loader (`Gr2DownloadHQ2`, `gr2_init.o` `0xeac`); the record length rule is inferred as for the GE7 image. |
| `ge7.bin` | GE7 microcode: magic `0x966e`, version 1, header words `0x1c, 0xe0, 0x8cc, 0x14, 0xfc, 0xfd, "v1.0"`. 611432 bytes. | Header only. Loader (`Gr2DownloadGE7`, `0xbc0`): copies 512 words from image offset `0xfc` into shared data RAM at `+0x0` and verifies them (its error text calls them constants and names the shared RAM), clears the 64K-entry microstore by writing zeros through `+0x683e0`..`+0x683ec` and `+0x6a064` with the address in `+0x6a070`, then loads records and verifies them. A record is an address half-word at offset 0, then five 32-bit words at offsets 4, 8, 12, 16 and 20 (each two half-words); the address goes to `+0x6a070`, the word at 4 to `+0x6a064`, 8 to `+0x683ec`, 12 to `+0x683e8`, 16 to `+0x683e4` and 20 to `+0x683e0`, and the read-back masks `+0x683ec` to 7 bits and `+0x6a064` with `0x03dfffff`. Record length is taken from the half-word at image offset `0xf8` plus 6, rounded to even (inferred). Established for the loader's accesses. |
| Built-in text-port microcode | A small image held in `gr2_tpucode.o` (`Gr2TpHQUcodeSetup`, `Gr2TpGEUcodeSetup`, `Gr2TpSetup`) is downloaded for console text before the full images, then the FIFO window is initialised (`+0x40644` from a table indexed by board revision) and the screen blanked. | Setup read; image not decoded. |
| `Gr2Download` ioctl | The kernel takes either image from user space (size at most 1 MiB), tells them apart by the magic, and writes 0 to the word at `+0x1fffc` on failure; `Gr2TpSetup` writes 1 there on success. That word is a microcode-ready flag in the last word of the 128 KiB shared RAM (inferred: `_Gr2UcodeReady` unread). User space loads the images. | Established for the routine (`gr2.o` `0x1ab4`). The user-space caller is unread. |
| `gr2_tport.o` | Text-port primitives (`Gr2TpDrawBitmap`, colour, point, box fill). Register-poke level glue. | Names only. Pair with NetBSD's console routines, which use the same FIFO offsets. |
| `gr2_dma.o` | Pixel DMA through the MC virtual DMA engine (`MCdma`, `Gr2MCDMAtrigger`, `fakePICdma`), strided and rectangular. | Names and imports only. |
| `gr2_retrace.o` | Retrace handler with a VC1 shadow, cursor position and hotspot, gamma ramp, swap scheduling. | Names only. |
| `libGLcore.so`, `libgl.so` in `IP12GR2` and `IP12GR232` | The user-space GL and IrisGL drivers. They write FIFO tokens. The n32 build is for GR2 on the Indigo family; no `IP20GR2` directory exists on the media (`IP20LG1MC` is the LG1 board's). | Only the suffix strings read. DWARF present in the upstream's copy per its notes; unconfirmed here. |
| `vof/*.u`, `adjntsc.bin`, `adjpal.bin` | Video output format and genlock adjustment tables, 2176 bytes per `.u` file. | Not read. The VC1 SRAM images the kernel loads are in `gr2_init.o`'s data, not here. |
| `sbin/stand/ide.IP20` | The diagnostic program, which has graphics tests. | Not read. |
| PROM 4.0.5D `0xbfc0e6f0`, `0xbfc0f6a8` | Probe and GR2 loop; reviewed on the chips gio page. | Reviewed there. The PROM's console drawing path to the board is unread. |
| NetBSD `grtwo.c` | Console: FIFO offsets `+0x40644`..`+0x40664`, data port `+0x4077c`, XMAP "all" CLUT writes, VC1 cursor. Probe accepts `0x1f000000`, `0x1f400000`, `0x1f600000`. | Read in full. A driver expectation. |
| Elan TR | Architecture only; no registers. | Read in full. |

The FIFO window: NetBSD's token offsets (`+0x40644` init, `+0x40648` colour, `+0x4064c` finish, `+0x40650` point, `+0x40654` rectangle,
`+0x40658` character move, `+0x4065c` line, `+0x40660` character draw, `+0x40664` rectangle copy, `+0x4077c` data) are touched
by the kernel for four of them: `Gr2TpSetup` writes `+0x40644`, zeros `+0x40648` and `+0x40654`, and addresses `+0x4077c`
(`gr2_tpucode.o` `0x9c`). The meaning of a token write (the low offset bits select a microcode entry, the written word is its
first operand) is **inferred** from the pattern; the dispatch is microcode.

## Reading plan

Order matters: the host window is closed first, then the microcode that sits behind it.

1. **`gr2_init.o` remainder** (small, high yield). `_Gr2RegisterInit` and its `.data` images (per monitor code VC1 SRAM
   contents at SRAM offsets `0x0`, `0x800`, `0x400`, `0x900`, `0xa00`); `Gr2StartClock` table; `_Gr2DacInit`;
   `_Gr2XMAPInit1`..`3`; `Gr2BlankScreen`; `initGr2Cursor`. Output: device pages for VC1, XMAP5, DAC and clock.
2. **`gr2.o`**: `Gr2FIFOHandler` rest, `gr2_earlyinit`, `Gr2SetMonitor`, `Gr2AdjGenlock`, `Gr2PcxSwap` and `_Gr2CXSaveRestore`
   (context save through the shared RAM at `+0x0`..`+0x1ffff`), `Gr2Private` (ioctl surface), `_Gr2UcodeReady`. Output: HQ2 status,
   interrupt and shared-RAM contract.
3. **`gr2_retrace.o`**, then **`gr2_dma.o`** and **`gr2_tport.o`**: VC1 shadow, gamma and cursor write sequences; DMA descriptor
   shapes and the MC virtual DMA interface (cross-read with the MC page).
4. **`hq2.bin`** with the HQ2 sequencer: decode the header, record table and instruction word using the loader as the oracle
   (every word the loader writes must read back). Then the attribute jump table (16 words) to name the first microcode entries.
5. **`ge7.bin`**: same, then the token entries matching NetBSD's FIFO offsets.
6. **`libGLcore.so` (`IP12GR232`)**: FIFO token numbers, data formats (16-bit, 24-bit, float, double in the TR), the 0x77c data
   port, and which RE3 registers the GL writes directly. Use its DWARF types if present.
7. **`ide.IP20`** graphics tests and **PROM 4.0.5G** console path: register touches that the kernel does not make.
8. **Elan TR sections 4.3 and 5**: read the rest (the pixel pipeline) for RE3 and framebuffer grades.

Boards to reconcile once 1 and 2 are done: revision below 4 versus 4 and up probe branches (two board generations, both
handled by the IP20 driver), and what the extra bytes of the probe record mean for Elan, XZ and XS.

## Review (2026-11-23)

Independent review of this survey against the shipped objects (`gr2.a` sha256 `c768b3a4...`, every member hash matches
[references/binaries.md](../../references/binaries.md), re-disassembled with relocations), PROM 4.0.5D, NetBSD `grtwo.c` and
`grtworeg.h`, and the Elan TR. PROM 4.0.5G was not re-read.

| Claim | Result |
|---|---|
| `Gr2Probe`: `badaddr` then `+0x6a07c == 0xdeadbeef`; board revision `~byte(+0x6c000) & 0xf`, zero fails | CONFIRMED (`gr2_init.o` `0x16c`; PROM 4.0.5D `0xbfc0e6f0` and `0xbfc0e720` do the same with plain loads and `lbu`). The rest of the probe record table also matches the code, including the 1024 by 768 case for monitor code 6. |
| MC reset: clear bit 10 of `0xbfa00004`, 10 microseconds, set | CONFIRMED against the MC page (`grr`, active low, resets to clear). The PROM does the same (`0xbfc03674`, `0xbfc0f5ec`) with a delay argument of 5; the unit of the PROM's delay routine was not checked, so "the same" holds for the sequence, not the 10 microsecond figure. UNVERIFIED for the PROM duration. |
| `_Gr2ProbeGEs` | WRONG as written, fixed above. Slots 1 to 7 are all tried and the count is the highest responding slot plus one; a failing slot does not stop the loop. Slot stride, slot 0 assumed, the five offsets and the five values are CONFIRMED. The driver's four-way flag branch handles 1, 2, 4, 8 and sets nothing for other counts. |
| HQ2 init values | CONFIRMED (`_Gr2HQ2RegInit` `0xb70`): NUMGE at `+0x6a044` (count, or count with bit 4 for 8), `+0x6a054` 100, `+0x6a058` 255, `+0x6a05c` 40, `+0x6a060` 1, `+0x6a080` 16. |
| HQ2 loader | CONFIRMED: magic `0x965e`, 16 words from image offset `0xfc` to `+0x6a000`, records of an address half-word and a word at record offset 4 to `+0x60000 + 4 * address`, terminator `0xffff`, read-back verify. |
| GE7 loader | CONFIRMED except the `+0x6a064` read-back mask, which is `0x03dfffff`, not `0x003dffff` (WRONG, fixed). Magic `0x966e`, 512 constants to `+0x0`, microstore clear of 64K entries, the register mapping and the `+0x683ec` 7-bit mask match. Flag word `+0x1fffc`: written 0 on a failed download and 1 by `Gr2TpSetup` on success, CONFIRMED. |
| Interrupt wiring | CONFIRMED: `setgiovector` with line 0 and `Gr2FIFOInterrupt`, line 2 and `gr2_retr_intr`, both slot 2; agrees with the chips interrupt page. The FIFO handler clears bit 0 of `0xbfb801c7` on entry and restores it on exit. |
| Grades: Elan four GE7 | CONFIRMED, established (published): the TR names four geometry engines in the configuration list of section 1 and in sections 2.2, 4.1 and 4.2. The file is HTML without page numbers, so the section number is the citation. |
| Grades: XS one, XZ two | Superseded: both are now established, see the product table and [host contract section 4](host-contract.md#4-probe-answers-per-indigo-variant). The parts listing (`GR2-1 ... with 1 GE-7 (XS,XS24)`, `GR2-2 ... with 2 GE-7's (XZ)`) agrees. |
| The four filed disagreements | See [questions](../../questions/README.md): the XMAP5 window is settled and removed; the `+0x6a040` entry is reduced (disjoint bit fields, not a conflict); the byte-lane entry gained the PROM route (the PROM agrees with the kernel); the GE7 revision entry stays open. |
| Scaffold | `retools` is pinned at `b1e357ba`, the same as newport; retools main is now `b75bedf2` (noted, not bumped). The workflow is identical to newport's; gr4's differs only in leading comments. `retools/tools/defs/ci-check` prints "no decode headers" and passes; `docs-index --check` and `check-links` pass. `AGENTS.md` has no internal hosts or paths (the only matches are the branch name), and techomancer's original text is intact apart from trailing blank lines. |
