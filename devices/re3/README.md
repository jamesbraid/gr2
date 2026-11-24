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
the register layout, reset state, the interface between the geometry engines and the raster engine, the framebuffer bank packing.
The open questions and the routes tried are in [questions/re3.md](../../questions/re3.md).

## Review (2026-11-23)

- CONFIRMED: RE3 count branch in `ide.IP20`: `print_hinv` (`0x8852f434`) stores 2 to the global at `0x860` when board revision is 4 or more and the value at `0x890` is 8, else 1; `0x890` is also written by `Gr2ProbeGEs` (`0x8852ef84`), which supports the engine-count reading (still inferred, as stated).
- CONFIRMED: negative search over `+0x6c200` to `+0x6c7ff` in the six kernel objects, PROM 4.0.5D and `ide.IP20` (independent displacement and immediate scan; the hits were string and table pointers). PROM 4.0.5G, the o32 GL core and the X server driver were not rescanned; the page's "all" list is therefore broader than what was re-verified. `ide.IP20` does access `+0x6c1c0` to `+0x6c1fc` as the page says.
- CONFIRMED: NetBSD bank comments and addresses, read from the public header. No [vendor-derived] source is cited.
- No change to grades. The registers.toml correctly leaves all three banks unknown.
