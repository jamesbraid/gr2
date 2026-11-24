# GE7: the geometry engines

The floating-point geometry engines behind the HQ2. This page covers what a host program sees of them (the window, the probe, the
microcode load registers), the microcode image format as the IRIX loader reads it, how many engines each board has, and what the
shipped microcode image does at the level of entry points. The register list is [registers.toml](registers.toml); the pipeline view
(which FIFO token reaches which microcode entry) is [platforms/express/pipeline.md](../../platforms/express/pipeline.md); the host
side of the load registers that live in the HQ2 is [devices/hq2](../hq2/README.md); the raster engine that the GE7 feeds is
[devices/re3](../re3/README.md).

## Conventions

Every fact carries one provenance tag. Grades are the repository's: **established** (read in full), **inferred** (reasoned, reasoning
given), **unknown**.

- `[public]`: published document or public driver (Elan Graphics Technical Report, NetBSD `grtwo`).
- `[binary]`: shipped binary, cited by object, routine and address. A software expectation, not a hardware measurement.
- `[vendor-derived]`: rests on the upstream headers or on the GR4 schematic scan (origin unstated). `GE7.h` was not consulted for this page.

Binaries read (SHA-256 in [references/binaries.md](../../references/binaries.md) except where given): kernel objects `gr2_init.o`
(`_Gr2ProbeGEs` `0x50`, `_Gr2ProbeChipRev` `0x108`, `Gr2DownloadGE7` `0xbc0`) and `gr2_tpucode.o`; PROM 070-8116-004 (4.0.5D, SHA-256
`e6e1f1ed...f82f`) and 070-8116-005 (4.0.5G, SHA-256 `ae35c097...39bd`); the diagnostic program `ide.IP20` from Diagnostics 5.2
(SHA-256 `744fdebc...df14`; ECOFF, symbols present); `ge7.bin` and `hq2.bin`. No microcode bytes and no disassembly are committed.

## What it is

- A custom 32-bit floating-point datapath with one multiplier and one adder, 32 MFLOPS each, four of them on an Elan board for a
  128 MFLOPS peak. The four execute as a SIMD machine under one sequencer inside the HQ2, which addresses a wide microinstruction
  memory whose contents go to every GE7 at once. Each engine works on its own primitive, four primitives at a time. [public] Elan TR 4.2.
- What it computes: model-view and normal transforms, up to eight lights with material terms, clipping against six planes plus
  user planes (Cohen-Sutherland when needed), perspective divide, polygon decomposition into triangles, and the per-triangle or
  per-line parameters the raster engine iterates (lowest pixel centre, edge slopes, parameter slopes in X and Y). [public] Elan TR 4.2.
- On the Indy Elan board (GR4, fab 034-8234-002) the published schematic has sheets named "GE7 Ucode & Shared RAM", "2GE7 ASIC (cavity
  up)" and "2GE7 ASIC (cavity down)": two packages of two engines each, which fits four on the board. [vendor-derived] GR4 schematic, sheet index (an OCR'd scan of unstated origin, so not tagged public)
  (the scan text is poor; the page names are legible). The package count is inferred from the names.

## Engines per variant

| Variant | GE7 count | Grade and source |
|---|---|---|
| Indigo Elan | 4 | established [public] Elan TR 1, 4.2; consistent with the GR4 sheet names above |
| Indigo XZ | 2 | inferred: a third-party parts list names a two-engine board; no binary or manual states it |
| Indigo XS, XS24 | 1 | inferred: same parts list; the TR gives no XS count |
| any board | 1, 2, 4 or 8 | established [binary]: the kernel counts engines by probe (below) and branches on 1, 2, 4 and 8 in `gr2_init` (`gr2.o` `0x778`); the diagnostic program reports a count of 8 for a revision 4 or later board by comparing the stored count with 8 (`print_hinv`, `ide.IP20` `0x8852f470` onward). That an eight-engine Indigo board shipped is unknown. |

The engine count reaches the HQ2 through the `NUMGE` register (`+0x6a044`): the driver writes the count, or the count with bit 4
set when it is 8. [binary] `_Gr2HQ2RegInit` `0xb70`. Registers in the HQ2 are documented in [devices/hq2](../hq2/README.md).

**How work is shared between engines.** The TR says the command engine delegates primitives to the geometry engines and fills in
parameters not supplied by the program, one primitive per engine, four at once. [public] Elan TR 4.1, 4.2. Whether the choice is
round-robin, first-free or by a vertex counter, and where a strip or fan stays on one engine, is decided by HQ2 microcode and
is **unknown**: it is not visible from the host (no engine select register is written by any shipped software read). A model that
runs the geometry work on one engine and returns the same pixels loses nothing a program can observe, unless it reads back
per-engine RAM.

## The host window

Offsets from the board base (`0x1f000000` on the Indigo). Slot `n` (0 to 7) is `+0x68000 + 0x400 * n`, 1 KiB each.

### Probe

`_Gr2ProbeGEs` (`gr2_init.o` `0x50`) takes slot 0 as present and tests slots 1 to 7 in turn: it stores `0x1f1f1f1f`, `0x2e2e2e2e`,
`0x3d3d3d3d`, `0x4c4c4c4c` and `0x5b5b5b5b` at slot offsets `+0x0`, `+0x7c`, `+0xfc`, `+0x17c` and `+0x1fc`, reads the five back in
that order. A failing slot does not end the loop: slots 1 to 7 are all tried, and each slot that returns all five rewrites the count
byte to its index plus one, so the count is the highest responding slot plus one (equal to one plus the run of responding slots
only when the responding slots are contiguous). Established [binary], whole routine read. The diagnostic program's `Gr2ProbeGEs` (`ide.IP20` `0x8852ef84`) uses the same five addresses. Each slot
therefore has at least 0x200 bytes of ordinary read/write storage. An absent slot answers with a bus error or other data: unknown
(plain loads, no fault catcher). qtest discriminator: slot `n` returns what was written at the five offsets when it is present and not when it is absent, and
the reported count is the highest present slot plus one.

### Microcode load registers

The microcode image is written one microstore word at a time through registers that exist once and reach every populated engine.
Established [binary] `Gr2DownloadGE7` (`gr2_init.o` `0xbc0`), `ide.IP20` `gr2_ucload`, and the 4.0.5D PROM's embedded loader
(`0xbfc0f308`).

| Offset | Role | Access seen |
|---|---|---|
| `+0x6a070` | microstore address (HQ2 register, `GEPC` in NetBSD) | write; the loader counts it 0 to `0xffff` to clear, then writes each record's address |
| `+0x683e0` | microword bits, lowest column | write, read back unmasked |
| `+0x683e4` | microword bits | write, read back unmasked |
| `+0x683e8` | microword bits | write, read back unmasked |
| `+0x683ec` | microword bits, highest column | write; read back masked with `0x7f` (only 7 bits kept) |
| `+0x6a064` | microword bits, fifth column (HQ2 register) | write; read back masked with `0x03dfffff` |

Order within a word: set the address, write `+0x683e0`, `+0x683e4`, `+0x683e8`, `+0x683ec`, then `+0x6a064` last. The `+0x6a064`
write being last is **inferred** as the commit: the clear loop and both loaders use that order and no source states which write
latches the word. The five columns hold 32 + 32 + 32 + 7 + 25 = 128 stored bits, a 128-bit microword; the unstored bits read as zero on the
masked registers. The microstore is 65536 words deep (the clear loop runs to `0x10000`). The assignment of microword bit
fields to functions (op codes, register selects, immediate and branch fields) is **unknown**; see
[questions/ge7.md](../../questions/ge7.md).

### Revision

The GE7 revision is the register at **`+0x683f4`**: write zero, read it back, keep bits 7:5 of the low byte. Established [binary]: the
kernel does this in `_Gr2ProbeChipRev` (`gr2_init.o` `0x108`, store at `0x130`, load at `0x134`) and the PROM does the same in the
4.0.5D probe (`0xbfc0ecec`, store `0xbfc0ed0c`, load `0xbfc0ed14`); both keep the three bits as a record byte. That the three bits
are a revision number rather than a feature code is inferred from the record layout.

NetBSD reads `+0x680fc` and keeps bits 7:4. [public] NetBSD `grtworeg.h` (`GE7_REVISION 0x680fc`, mask `0xf0`). No shipped
binary read here touches `+0x680fc` (slot 0 offset `0xfc`; the probe skips slot 0, so it never writes there either). The kernel
and the PROM agree with each other and the NetBSD source stands alone, so the revision register is `+0x683f4` and NetBSD's address is
an unconfirmed second reading of slot 0 offset `0xfc`, which is one of the five probe-word offsets in the other slots and is not shown to
be plain storage in slot 0. This settles the question previously filed as "where is the
GE7 revision": use `+0x683f4`. qtest discriminator: after writing 0 to `+0x683f4`, reading returns the configured revision in
bits 7:5.

### Shared data RAM

`+0x0` to `+0x1ffff` (128 KiB) is RAM shared between the CPU and the engines. [binary] the loader's error text names it. Its first 512
words are loaded from the microcode image's constants block (below) and verified; its last word `+0x1fffc` holds a flag the driver
sets to 1 when the built-in text-port microcode has loaded and to 0 when a load fails (`Gr2TpSetup`, `gr2_tpucode.o` `0x9c`;
`Gr2Download`, `gr2.o` `0x1ab4`); the flag's consumer is unread. The rest of the RAM is used for context save and DMA descriptors:
that is the HQ2 page's.

## Microcode image format

Read from the loader (`Gr2DownloadGE7`, established [binary]) and checked against `ge7.bin` (611432 bytes) and the 4.0.5D PROM's
embedded text-port image (10104 bytes). All fields big-endian. The HQ2 image shares the header and record layout with a four-byte
data field instead of twenty.

| Offset | Size | Content | Grade |
|---|---|---|---|
| `0x00` | u16 | magic `0x966e` (the HQ2 image uses `0x965e`); the kernel's download ioctl tells the images apart by it | established [binary] `Gr2Download` |
| `0x02` | u16 | version, 1 | established value; role inferred |
| `0x04` | u32 | `0x1c`: offset of the version text (`"v1.0"` here, `"V1.0"` in the HQ2 image) | inferred |
| `0x08` | u32 | `0xe0`: end of the text area; zero fill to `0xfc` | inferred |
| `0x0c` | u32 | offset of the record table (`0x8cc` in both images); the loader reads it | established [binary] |
| `0x10` | u32 | `0x14`: record data bytes (twenty), the same value the loader reads from the half-word at `0xf8` | established [binary] for the half-word at `0xf8` |
| `0x14` | u32 | `0xfc`: offset of the constants block; the loader hard-codes `0xfc` | established as used; header role inferred |
| `0x18` | u32 | `0xfd` in `ge7.bin`, `0xeb` in the PROM image: matches the index of the last non-zero constant (252 in `ge7.bin`) plus one, so a count of constants in use | inferred |
| `0x1c` onward | text | version text, a build date in 1996, and build host and directory strings; not reproduced | established that they are text |
| `0xf8` | u16 | `0x0014`, record data bytes (see `0x10`) | established [binary] |
| `0xfc` | 2000 bytes | constants block, 500 words; the loader copies 512 words from here to shared RAM `+0x0`, which reaches 12 words into the record table (those 12 words are harmless extra data) | established [binary] for the copy and verify |
| record table | records of 26 bytes | see below; ends at an address word of `0xffff` | established [binary] |

**Record layout** (length is `((u16 at 0xf8) + 6) rounded down to even`, 26 bytes here): a u16 microstore address; a u16 the loader
never reads (value 1 in every record of both images); five 32-bit words at record offsets 4, 8, 12, 16 and 20; a u16 the loader never
reads: a checksum, the sum modulo 65536 of the record's address, its second half-word and every byte of its five data words (holds for every record of both PROM images, `hq2.bin` and `ge7.bin`; established [binary], `tools/ucode-decode.py info`; see [microcode.md](../../platforms/express/microcode.md)). Each 32-bit word is two half-words, high first. The
words go to `+0x6a064` (offset 4), `+0x683ec` (8), `+0x683e8` (12), `+0x683e4` (16) and `+0x683e0` (20). Established [binary].
The loader then walks the table a second time, sets the address, and compares all five registers with the table under the masks
above, counting mismatches.

In `ge7.bin` the table has 23429 records in strictly ascending address order, address 0 to 36194, with 101 contiguous runs. The gaps are
page-shaped: runs after the first start at addresses of the form `n * 0x100 + 2` (0x102, 0x302, 0x502, 0x602, 0x802, 0xa02, 0xc02,
...), which suggests 256-word code pages whose first two words are not used by the image, with only the first run starting at 0.
Inferred from the address list.

The 4.0.5D PROM carries a second, much smaller image of the same format (HQ2 3752 bytes at `0xbfc49840`, GE7 10104 bytes at
`0xbfc4a6f4`) that implements only the console tokens; see [pipeline.md](../../platforms/express/pipeline.md). Established [binary]
for location and size (the PROM routine at `0xbfc0f1b0` returns the GE7 pointer).

### The constants block

The block is read-only data the microcode uses from shared RAM, described here in words. It opens with a 63-entry table of
single-precision values falling geometrically from 1.0 to about 0.0047, each step a factor of about 0.917 (close to the eighth root
of one half), so every eighth entry is nearly half the one before: a lookup for an exponential, spot-light or fog attenuation
curve. After that sit floating-point scalars the geometry code needs (one half, two, three, sixteen, sixty-four, powers of two up to
`2^23`, the integers 255, 1023, 1279, 1280, 2047, 2048 as floats, the screen width 1280, small epsilons around `1e-6`), then
integer constants: small enumerations, bit masks (`0xffff`, `0x3ffff`, `0x7fffff`), a count `10000`, loop counts, and the initial
values the console microcode writes to the raster engine (mode words, the clip limits `1279 << 11` and `1023 << 10`; the table is
in [devices/re3](../re3/README.md#addresses-the-microcode-writes)). They are data, not jump targets: the microcode reads them with
the ALU operand select that names the shared word at the microword's 16-bit field on control `0x3f` words, and that field is a branch
target only on branch words ([microcode.md](../../platforms/express/microcode.md#the-data-path)). The state words that store and read-back words name (the drawing colour at `0x1d`, the position at `0x3c` and `0x3d`) are numerically inside this block but are not these constants: `ge7.bin` reads 44 constants that stores also name, so state accesses use a separate namespace, mechanism unknown (second memory or base offset). The diagnostic image's block carries
a table of small numbers (`C[27 + n] = n`) that its function test loads as ALU function numbers. Each image has its own block: the
console INIT in the PROM image and in the diagnostic image load the same values from indices that differ by `0x2d`. The split between
float and integer data and the screen-size constants is established [binary] by inspection of the block; that the microcode reads the
block as data is **inferred** (known answers of the diagnostic program); what each value means to the hardware is **inferred** or
unknown.

## What the shipped microcode does

This is the functional level that the tools support without decoding the instruction set.

1. **A token reaches a handler.** A write to the HQ2 FIFO selects an HQ2 microcode entry by nine address bits; for most tokens that
   entry ends by starting a GE7 routine at a 16-bit microstore address. In `hq2.bin`, of the 426 occupied words among the first 512 microstore addresses, 363 lead (following the HQ2 jump words) to a
   GE7 start and reach 233 distinct addresses; 63 do not and are handled inside the HQ2. In the PROM text-port image all eight tokens
   that have a handler start a routine in the same way, and those start addresses are the first word of consecutive routines in the
   GE7 table. The start instruction is the HQ2 word whose opcode byte is `0xd8`; its low sixteen bits are the address. Inferred from
   the structure of both images; the HQ2 instruction set is the HQ2 page's. The complete token-to-entry map is in
   [pipeline.md](../../platforms/express/pipeline.md).
2. **State tokens set engine state.** The GL core sends one token per piece of fixed-function state: depth test, depth function and mask,
   stencil test, function and mask, logic op, blend factors, fog, shade model, line and polygon stipple, line width, point size,
   cull, polygon mode and offset, clip planes, scissor, viewport, matrices, light sources and materials. Each of these tokens
   starts its own short GE7 routine. Since the GE7 is the only unit between the FIFO and the raster engine, and the host never writes raster
   registers (see [devices/re3](../re3/README.md)), these routines both keep state for later geometry and push it to the raster
   engine. Inferred.
3. **Vertex tokens run per-primitive code.** The Begin and End tokens for points, lines, line strips and loops, triangles, triangle
   strips and fans, quads, quad strips and polygons start the routines that gather vertices and run the pipeline. The vertex, colour,
   normal and index tokens carry no first-level GE7 start of their own (their dispatch slot is empty or goes through the attribute
   jump table at `+0x6a000`); they feed the engine that the current primitive was assigned to. Inferred.
4. **Address-space layout.** Entry addresses grouped by role: 30 (buffer swap), 206 to 1012 (matrix, viewport, clip and
   state), 1284 to 2797 (state setters and queries), 3074 (polygons), 4610 to 7940 (triangle and quad ends, generic end), 13406 to 13711
   (point and swap), 14338 to 15620 (lines), 15694 to 16460 (lighting), 24248 to 25322 (pixel copy and clears), 26475 to 27323 (pixel
   reads and writes), 28674 and 30210 (strips and fans), 31242 (texture span), 31835 to 35514 (X server entries), and the console
   text-port routines at the top, 35931 to 36194 (init, colour, point, rectangle, line, cursor move, character draw). Established
   [binary] for the addresses (HQ2 dispatch); the roles come from the GL function names that use each token and are inferred.
5. **The console routines are the smallest self-contained set.** The PROM-embedded GE7 image contains 301 words in two runs (0 to 1 and
   10 to 308) and serves the eight console tokens; see [pipeline.md](../../platforms/express/pipeline.md).

The instruction set is partly decoded (operand selects, the register file, result delays, flags: [microcode.md](../../platforms/express/microcode.md#the-data-path),
inferred from the diagnostic program's known answers). The way the four engines are kept in step and the meaning of most RE3 addresses
the microcode writes are **unknown**; see [questions/ge7.md](../../questions/ge7.md) and [questions/microcode.md](../../questions/microcode.md).

## Summary of grades

**Established**: probe, load registers and masks, record format, image sizes, revision register location. **Inferred**: engine
counts other than Elan, work distribution, constants block roles, dispatch-to-entry rule, page structure, microword commit order.
**Unknown**: microword field layout, per-engine RAM size, absent-slot behaviour, what `+0x683f8` to `+0x683ff` do.

## Review (2026-11-23)

Independent re-read of `gr2_init.o` (disassembly), PROMs 4.0.5D, `ge7.bin`, `hq2.bin` and `ide.IP20` (hashes match [references/binaries.md](../../references/binaries.md)).

- CONFIRMED: probe loop (five words, slots 1 to 7 all tried, count is highest responding slot plus one, `_Gr2ProbeGEs` `0x50` to `0x104`).
- CONFIRMED: revision at `+0x683f4`: `sw zero` at `0x130`, `lw` at `0x134`, `andi 0xff`, `srl 5`; same sequence in PROM 4.0.5D at `0xbfc0ed0c` and `0xbfc0ed14`. NetBSD `GE7_REVISION 0x680fc`, mask `0xf0` read from the public header.
- CONFIRMED: load registers and order (`+0x683e0`, `e4`, `e8`, `ec`, then `+0x6a064`), mask `0x03dfffff` (25 bits) on `+0x6a064`, `0x7f` on `+0x683ec`, so the stored microword is 32 + 32 + 32 + 7 + 25 = 128 bits. Clear loop runs `0` to `0xffff` through `+0x6a070`.
- CONFIRMED: `ge7.bin` header words, 23429 records, addresses 0 to 36194 ascending, 101 runs starting `0, 0x102, 0x302, 0x502, ...`, second half-word always 1, constants block 500 words, header `0x18` = 253 = last non-zero constant index plus one. The build date text is 1996 in `ge7.bin` and 1992 in the PROM images.
- CONFIRMED: both PROM console images are plain (uncompressed): HQ2 at `0xbfc49840` (magic `0x965e`, 149 records), GE7 at `0xbfc4a6f4` (magic `0x966e`, 301 records, two runs 0 to 1 and 10 to 308). The stated sizes 3752 and 10104 are the record table plus terminator (3744, 10080 bytes) plus an 8 and a 24 byte trailer, the same trailer length `hq2.bin` and `ge7.bin` carry. The routines at `0xbfc0f180` and `0xbfc0f1b0` return the image start after calling a helper with the version text, so they also check the version string.
- CONFIRMED: HQ2 slot is bits 10:2 of the FIFO offset (`+0x40644` is slot 401 and so on); PROM image records sit at 401, 402, 404 to 409 (403 has no handler; 417 to 419 are the three unexplained ones); `hq2.bin` has 426 occupied words below 512, 363 reach a word whose byte at bits 23:16 is `0xd8`, 233 distinct addresses (recomputed with a separate script, same rule). Console GE starts 35931, 35979, 35986, 35997, 36017, 36035 read directly from the `0xd8` words.
- CONFIRMED: "no shipped program accesses `+0x6c200` to `+0x6c7ff`" for the six kernel objects and PROM 4.0.5D (displacement scan, zero hits); `ide.IP20` has no access in that range (its nearby accesses are `+0x6c1c0` to `+0x6c1fc`). Same caveat as the page: base-pointer forms are not excluded. PROM 4.0.5G was not scanned.
- CONFIRMED: data ports: PROM RECTI2D stores data to `+0x40000` and the token to `+0x40654`; `gr2_tpucode.o` stores INIT at `+0x40644` and data at `+0x4077c`. GL core stores through `0x42000 + 0x77c` (n32 build). The X server's `+0x4077c` was not checked (the object is not held).
- Token to routine table: all 131 addresses in pipeline.md reproduce their slot and GE routine (or `HQ2`/`-`) from `hq2.bin`. Twelve entries were also checked against `libGLcore.so` (n32): PassBlendFunc, PassFog, PassMatrix, UpdateMatrixState, PassLineWidth, EnableDepthTest, PassPointSize, EndLLoop, GetOrigin, UpdateViewport, PassLogicOp, EnableStencilTest, BeginPolygon all contain the named offset. Two defects: see [pipeline.md](../../platforms/express/pipeline.md#review-2026-11-23).
- WRONG (small): the page's role label "30 (buffer swap)" rests on the `+0x42000` table row, which is a base address, not a stored token; the label is inferred from a name and is weaker than the page says. Slot 0 is also the PROM's data port, so what routine 30 does is unknown.
- GRADE: `slot_ram` in registers.toml is graded established for 1792 words, but only five words per slot are read back; established is true for the first `0x200` bytes of each slot and inferred beyond. `ucode_ready` is established as the store only (the page already says so).
- UNVERIFIED: the n32 `libGLcore.so` is the only GL core held here; the o32 build, the X server driver and PROM 4.0.5G were not read.
- No fact graded established rests on [vendor-derived] alone in this page or its registers.toml.
