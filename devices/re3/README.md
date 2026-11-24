# RE3: the raster engine

The third-generation raster engine that turns the geometry engines' line and triangle parameters into pixel writes. This page records
what is published about it, what the host window offers, and the finding that matters most for a model: **no shipped program writes a
raster-engine register**, so the only host-visible way to change what it draws is the FIFO token stream. The register file is
[registers.toml](registers.toml) (three banks, contents unknown); the token streams are in
[platforms/express/pipeline.md](../../platforms/express/pipeline.md); the engines that feed it are [devices/ge7](../ge7/README.md) and the
command front end is [devices/hq2](../hq2/README.md).

Provenance tags: `[public]` published or public driver; `[binary]` shipped binary (software expectation, with object, routine and
address); `[vendor-derived]` upstream headers: none used here (`RE3.h` was not consulted). Grades as in [AGENTS.md](../../AGENTS.md).

## What it is

[public] Elan Graphics Technical Report 4.3 and the hardware table in its introduction (the printed text has a few scan errors):

- 100,000 custom gates, 50 MHz.
- A pipeline of **25 to 40 stages** depending on the mode.
- Front end: **digital differential analysers** that iterate the slopes and start values the geometry subsystem loads, walking a line
  or triangle in whole-pixel steps and producing one pixel value per step.
- **Pixel operations**: if blending or raster operations are enabled, read the destination pixel at the incoming address and merge
  arithmetically or logically; colour compare for colour-index anti-aliased lines; fog and haze attenuation; dithering before the next block.
- **Pixel-update tests**, four at once: two screen masks (each gives window clipping for any arrangement of two overlapping rectangular
  windows), the 4-bit clipping ID plane, Z compare, stencil. All four must pass for the framebuffer and Z write to happen.
- It writes a **5-way interleaved framebuffer**, 56 bits per pixel at 1280 x 1024 including Z.

Fill modes and update rate: the Technical Report states that the raster engine uses the full video RAM bandwidth for every fill mode
and a Z buffer at twice the framebuffer bandwidth; no per-mode fill rate is given.

### Framebuffer layout

[public] Elan TR 4.3.1 to 4.3.5. The 56 planes per pixel are:

| Planes | Use |
|---|---|
| 24 image planes | single-buffered RGB: one 24-bit image. Double-buffered RGB: 12 bits per buffer, 24-bit input dithered to 4-4-4. Colour index: two 12-bit buffers (front, back). |
| 24 depth planes (optional) | signed 24-bit Z; with no Z buffer in use they serve as a second 24-bit colour set. |
| 1 to 4 stencil planes | taken from the low-order bits of the Z planes (so stencil planes cost Z resolution); the engine can conditionally clear, write, increment and decrement them independent of Z. |
| 4 overlay or underlay planes | window manager and menu use. |
| 4 window-clipping (CID) planes | each window gets a 4-bit ID; a pixel writes only where the stored ID matches. |

How those planes are packed into the five interleaved memory banks and the address bits that select a bank are **unknown**: the
Technical Report gives the counts only. The framebuffer and Z RAM boards are the VM2, ZRB1 and RB1 parts; the GR4 board
schematic (a scan of unstated origin) (Indy Elan, fab 034-8234-002) lists three ZRB1 sheets, an RB1 sheet and two Z-buffer sheets for banks A to J. [vendor-derived]
GR4 schematic sheet index.

## How many per board

Most boards carry one RE3. [public] Elan TR 4.3 speaks of one raster engine; [vendor-derived] the GR4 schematic has a single sheet named "RE3 ASIC". The
diagnostic program from Diagnostics 5.2 keeps a count `GBL_RE3Count` and sets it: for board revision 4 or later, **2 when the
engine count is 8, else 1**; for board revisions below 4, from bit 5 of the byte it reads at `+0x6c000`. [binary] `ide.IP20`,
`gr2_boardvers` (`0x8852f118`) and `print_hinv` (`0x8852f470` to `0x8852f4bc`). The value stored for revision 4 and later is
established; that the global at `0x890` is the engine count is inferred (its store was not traced); what bit 5 means for the
older boards is unknown. So an Elan board (four engines) has one RE3, a hypothetical eight-engine board two. Established for the
branch, inferred for the reading.

## The host window

[public] NetBSD's memory map of the board lists three RE3 register banks:

| Offset | NetBSD's description |
|---|---|
| `+0x6c200` | "27-bit registers" |
| `+0x6c280` | "24-bit registers" |
| `+0x6c600` | "32-bit registers" |

[public] NetBSD `grtworeg.h` header comment. No extents, register names or reset values are given, and the driver never reads or writes
any of them. The bit widths suggest parameter registers of the kinds the geometry engines send (coordinates and slopes with fractions, colour
components, 32-bit control and mask words); that is inferred from the widths alone.

**No shipped program touches them.** Searching for accesses to `+0x6c200` to `+0x6c7ff` with the two ways a compiler forms such
an address (an upper-half load of `0x7` and a negative offset, or an upper-half load of `0x6` and an OR-immediate) found none in:
the 4.0.5D PROM (all 512 KiB disassembled), the six IP20 kernel driver objects, the n32 and o32 GL cores, the X server driver and the
diagnostic program. The nearest accesses are to `+0x6c1a0` to `+0x6c1b4` (XMAP5) and, in the diagnostic program only, to `+0x6c1c0`
to `+0x6c1fc` (the two chips NetBSD labels "Kaleidoscope"). Inferred [binary] (negative search; base-pointer forms are not excluded).

What that means: the host reaches the raster engine only through the HQ2 and the geometry engines. Every piece of fixed-function state
the GL core sets (depth test, function and mask, stencil, logic op, blend factors, fog, shade model, dither, line and polygon stipple, line
width, point size, smoothing, cull, polygon mode and offset, scissor, pixel write mask, buffer read and write selection, clear colour,
depth and stencil) is a token to a geometry-engine routine, which holds it and sends it on. The token list is in
[pipeline.md](../../platforms/express/pipeline.md). Inferred from the function names and the absence of a direct path.

## Addresses the microcode writes

[binary] The geometry engines write the raster engine through an 8-bit address and an enable in each microword; the addresses are in
the range 0 to 0x7e (the eighth bit is never set) and, by count, fit the host window above, but how an address maps to a bank at `+0x6c200`, `+0x6c280` or `+0x6c600`
is **unknown**. The console microcode in the 4.0.5D PROM writes: `0x00` and `0x08` at the start of every drawing primitive, `0x20` to
`0x25`, `0x5e`, `0x5f` (written just before each routine's final stall), `0x67`, `0x6f`, and (INIT only) `0x46` to `0x49`, `0x4c` to
`0x4f`, `0x52` to `0x55`, `0x60` to `0x6e`, `0x70` to `0x74`, `0x7b` to `0x7e`. The diagnostic program's GeFifoTest adds `0x40` to `0x42`
for a ten-pixel span. Per-routine order is in [microcode.md](../../platforms/express/microcode.md#the-re3-output-path).

**The values are decoded.** Each write sends the ALU result of the word two before it, and ALUA = 5 on those words reads the image's constants block (not an immediate; the
[data path](../../platforms/express/microcode.md#the-data-path) gives the evidence). Running the routines on that model (`ge7-step.py run`, reproduced by its `selftest`) gives the values below. The earlier statement
here that INIT's constants "differ between builds: build-relative pointers" is withdrawn: they are indices into each build's own constants block, and the values that the two builds write agree at nine addresses.
Grades: the values are observed in the images and the delay and constants-block reading are **inferred** (three independent known answers each); the roles are **inferred** where the diagnostic program's span test fixes them and **unknown** elsewhere.

| Address | Value written | Role |
|---|---|---|
| `0x00` | `0x8000` first, in PNT2I and GeFifoTest | unknown: written first by every primitive (a mode or command word) |
| `0x08` | `0` second | unknown: its pair |
| `0x20` | (x + `0x800`) << 11 | x of the first pixel, biased by 0x800 and shifted left 11 (GeFifoTest: x = 100; PNT2I: the point's x). Inferred: the span test |
| `0x21` | (y + `0x800`) << 11 | y, same form (GeFifoTest, PNT2I). Inferred |
| `0x22` | GeFifoTest: (x + 10 + `0x800`) << 11; PNT2I: y << 11 with no bias | the x of the end of the span in GeFifoTest, where the constant 10 is the host's ten pixels. PNT2I writes y here instead: for a point the word is not an end x, so a model that treats `0x22` as the end must take care. Inferred for the span case only |
| `0x40`, `0x41`, `0x42` | the three colour words, each << 11 (GeFifoTest: slots 5, 6, 7 = red, green, blue of the host) | colour of the span. PNT2I writes the stored colour word, shifted left 11, to `0x40` only. Inferred: the host's red, green, blue order |
| `0x5f` | `2` in PNT2I and GeFifoTest, written after the coordinates and before the last colour word | the draw command, written just before the routine's stall (the cond 11 word of other routines sits on it). Inferred from two routines |
| `0x23` to `0x25`, `0x5e`, `0x67`, `0x6f` | RECTI2D, LINE2I, DRAWCHAR and RECTCOPY (float adds and min/max pairs, loops over the row words) | unknown: those routines need select 7 and the float adds of select 4 resolved |

INIT (PROM image 4.0.5D, GE7 10 to 50; the diagnostic image's own INIT in brackets where it differs), in order of writing:

| Address | Value | Note |
|---|---|---|
| `0x6c` | `0xffffffff` (diag `0x3ff`) | |
| `0x60` | `0xffffffff` | agrees |
| `0x69` | `0` | PROM only |
| `0x61`, `0x62` | `0` | agree |
| `0x63` | `0x402413` (diag `0x401013`) | a mode word: the builds differ in bits 10, 12 and 13 |
| `0x65` | `3` (diag `0x201`) | |
| `0x64` | `1` | agrees |
| `0x6d` | `0xffff01` | agrees |
| `0x67` | `0x8000` (diag `0`) | |
| `0x68`, `0x6b` | `0` | agree |
| `0x66` | `0x100070` | agrees |
| `0x72` | `5` | agrees |
| `0x73` | `0x27f800` = 1279 << 11 | agrees; 1279 is the last pixel of a 1280-wide screen, so probably the x clip limit in the same fixed point as `0x20` |
| `0x74` | `0xffc00` = 1023 << 10 | agrees; 1023 is the last line of a 1024-line screen, probably the y limit (note the shift 10, not 11) |
| `0x6a` | `0x44` | the diagnostic build writes a different value (the model gives `0x807d`; unverified) |
| `0x6e`, `0x70`, `0x71`, `0x7b`, `0x7c`, `0x7d`, `0x7e` | `0` | |
| `0x46` to `0x49`, `0x4c` to `0x4f`, `0x52` to `0x55` | `0` | three groups of four |

Nine addresses (`0x60`, `0x61`, `0x62`, `0x64`, `0x66`, `0x6d`, `0x72`, `0x73`, `0x74`) are written the same by the PROM build and the diagnostic build; two of them (`0x61`, `0x62`) are zero, so seven non-zero values agree. The values are reset or configuration data for the raster engine, so a model that
reads them back should return them after INIT; what each bit of `0x63`, `0x65`, `0x66`, `0x67`, `0x6d` means is **unknown**, and a reset value must not be taken from them (a register read after firmware initialisation is not a reset value).
The `0x5f` write is paired with the condition-11 sequencer word in 13 of the 14 places the full `ge7.bin` uses that condition, so it is the flush
that waits for the output FIFO ([microcode.md](../../platforms/express/microcode.md)); inferred.

## What each stage does to a pixel, from the GL core's tokens

This is the behaviour a model has to reproduce, in the order of the Technical Report's pipeline. Each statement is **inferred** from
the token names in the GL core and the report's text; the operand formats are in the token list.

1. **Iteration.** Lines and triangles arrive as start values and slopes; a pixel is produced for every integer step. Colour is 8-bit
   RGBA or a 12-bit index; depth is 24 bits. Shading mode (flat or Gouraud) is the shade-model token.
2. **Pixel operations.** Blend factors (two tokens), logic op (one), fog (an enable and a six-word parameter token), dither (one),
   texture-environment and a texture span token (the GR2 GL core has texture fallback span code that writes through its own tokens).
3. **Update tests.** Scissor, the window tests (screen masks and clipping ID, set up by the window system through other tokens), depth
   test (enable, function, mask) and stencil (enable, function, mask, operation).
4. **Write.** The pixel write mask token masks the framebuffer planes; the draw and read buffer tokens select front or back and
   the colour or Z or overlay set.
5. **Clears.** Colour, depth and stencil clears are single tokens that fill the window area; the GL core brackets them with the dither token.
6. **Pixel transfers.** DrawPixels, ReadPixels and CopyPixels use the pixel tokens (unpack, pack, copy), with an optional kernel DMA path
   through the MC.

## Grades

**Established**: nothing in this page is read from a raster-engine register. The facts established are the published chip description,
the NetBSD bank addresses as a driver comment, the RE3-count branch in the diagnostic program, and the absence of host accesses
(inferred, negative search). **Inferred**: the engine count reading, the register widths, how state reaches the engine. **Unknown**:
the register layout, reset state, the meaning of most of the addresses the microcode writes (the values are in the table above), the framebuffer bank packing.
The open questions and the routes tried are in [questions/re3.md](../../questions/re3.md).

## Review (2026-11-23)

- CONFIRMED: RE3 count branch in `ide.IP20`: `print_hinv` (`0x8852f434`) stores 2 to the global at `0x860` when board revision is 4 or more and the value at `0x890` is 8, else 1; `0x890` is also written by `Gr2ProbeGEs` (`0x8852ef84`), which supports the engine-count reading (still inferred, as stated).
- CONFIRMED: negative search over `+0x6c200` to `+0x6c7ff` in the six kernel objects, PROM 4.0.5D and `ide.IP20` (independent displacement and immediate scan; the hits were string and table pointers). PROM 4.0.5G, the o32 GL core and the X server driver were not rescanned; the page's "all" list is therefore broader than what was re-verified. `ide.IP20` does access `+0x6c1c0` to `+0x6c1fc` as the page says.
- CONFIRMED: NetBSD bank comments and addresses, read from the public header. No [vendor-derived] source is cited.
- No change to grades. The registers.toml correctly leaves all three banks unknown.
