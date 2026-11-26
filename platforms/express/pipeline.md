# Express drawing pipeline after the HQ2

How a drawing command travels from the host to pixels on an Express (GR2) board: the FIFO token encoding, which tokens the PROM
console, the IRIX GL core and the X server push, which geometry-engine routine each token starts, and what the raster engine receives.
The chips are described in [devices/hq2](../../devices/hq2/README.md) (command engine, the host side), [devices/ge7](../../devices/ge7/README.md)
and [devices/re3](../../devices/re3/README.md); the survey of boards is [README.md](README.md).

Provenance tags: `[public]` published or public driver; `[binary]` shipped binary, a software expectation (object or image and address
given); `[vendor-derived]` upstream headers (none used on this page). Grades as in [AGENTS.md](../../AGENTS.md).

Binaries read: PROMs 070-8116-004 (4.0.5D) and 070-8116-005 (4.0.5G); `libGLcore.so` for `IP12GR232` (n32, SHA-256 `b6731da1...`
from the IRIX 6.5 base set) and `IP12GR2` (o32, SHA-256 `8e77dae2...`); the committed disassembly of the GL core under
`libglcore/asm` (it names the same offsets in all but four cases, below); `gr2.so` (the X server's driver, committed disassembly under
`gr2_ddx/asm`); `hq2.bin`, `ge7.bin`; kernel objects of `gr2.a`; the diagnostic program `ide.IP20` (Diagnostics 5.2).

## The path

host stores to the GIO window -> FIFO inside the HQ2 -> HQ2 microcode picks the command and its operand count -> one geometry engine
(or all, for state) runs a microcode routine -> the engine passes parameters to the raster engine (RE3) -> framebuffer and Z (VM2,
ZRB1, RB1) -> XMAP5 (window and colour mode) and the VC1 (display timing and cursor) -> Bt457 DACs. [public] Elan TR 4.

The host writes drawing state and geometry only through the FIFO and never writes a raster-engine register in any shipped program read
(PROM, kernel driver, GL core, X driver, diagnostic program; see [devices/re3](../../devices/re3/README.md)). Inferred [binary]: a
pattern search for stores and loads at `+0x6c200` to `+0x6c7ff` (upper-half load plus offset, and OR-immediate forms) found none in
those programs; base-pointer forms the search cannot see are not excluded.

## FIFO token encoding

The FIFO window is `+0x40000` to `+0x5ffff`. Software never writes it as a plain queue: the address of each store is the command.

- **Slot, bits 10:2 of the offset.** The nine bits index the first 512 words of the HQ2 microstore; the word there is a jump into the
  HQ2 code that handles the command (opcode `0x6000` ORed with a 13-bit target), or the first word of the code itself. Established
  [binary] for the PROM image: its records sit exactly at the slot numbers of the console tokens (401 to 409) and `hq2.bin` has
  the same layout. Read from both images.
- **Operand.** The 32-bit stored value is the first operand; further operands are written to the data port. The PROM's data port is
  **`+0x40000`** (slot 0); the kernel's built-in console image and the X server use **`+0x4077c`** (slot 479); the GL core uses
  `+0x4277c`, `+0x4e77c` and `+0x5277c`, which are the same slot with attribute bits. Established [binary] for each user. Which of
  slot 0 and slot 479 the full HQ2 microcode accepts as a data port is the HQ2 page's question.
- **Attribute bits above bit 10.** The same slot appears with different upper bits for different operand shapes, and the sixteen-word
  attribute jump table at `+0x6a000` has the right size to be indexed by bits 15:12. Observed for slot 99 (vertex): float, four
  components `+0x4298c`, three `+0x4498c`, two `+0x4698c` (bits 15:12 = 2, 4, 6); the same with bit 16 set for short and integer
  components (`+0x5298c`, `+0x5498c`, `+0x5698c`). Colour slot 386: float three `+0x48608`, four `+0x4a608`; bytes `+0x58608`
  and `+0x5a608`. Index slot 254: float `+0x4e3f8`, integer `+0x5e3f8`. Vertex slots have no word in the HQ2 first level
  (slot 99 is empty in `hq2.bin`) and are resolved through the attribute table: in `hq2.bin` its entries for attribute 2, 4 and 6 are
  three different code addresses. Established [binary] for the address forms; the attribute reading is **inferred**.
- **Count and format.** The command engine accepts 16-bit integer, 24-bit integer, 32-bit IEEE and 64-bit IEEE coordinates, packed
  bytes for colour, and converts all to one internal floating-point form. [public] Elan TR 4.1. In the GL core: `Vertex4f`, `Vertex3f`,
  `Vertex2f` store 4, 3 or 2 floats to one address; the double forms convert and store floats (4, 3 and 2 words); the short/integer forms store
  integers (4, 3, 2 words); `Color3ub` stores three words and `Color4ub` four, one per component, as integers 0 to 255. Established
  [binary] `libGLcore.so` `__glexpim_Vertex3f`, `Vertex2i`, `Color3f`, `Color3ub`, `Color4f`, `Indexf`.

## The console tokens

Nine tokens at slots 401 to 409, named by the public NetBSD driver. [public] NetBSD `grtworeg.h`, `grtwo.c`; names are NetBSD's.

| Offset | NetBSD name | Operands (after PROM routine) | Handler in PROM image | GE routine start (PROM image) | In `hq2.bin` |
|---|---|---|---|---|---|
| `+0x40644` | INIT | one word: 0 in 4.0.5D; 4.0.5G writes 0 below board revision 4, 1 at 4, 2 above; the kernel does the same from a table indexed by the board revision, then writes COLOR 0 and a RECTI2D box from (0, 0) to a corner its caller supplies, to blank the screen | yes (slot 401) | 10 | slot 401, GE routine 35931 |
| `+0x40648` | COLOR | one word: the pixel value to draw with (inferred) | yes (402) | 51 | 35979 |
| `+0x4064c` | FINISH | not used by the PROM | none | - | none |
| `+0x40650` | PNT2I | x (token), y (data) | yes (404) | 58 | 35986 |
| `+0x40654` | RECTI2D | x1 (token), then y1, x2, y2 (data) | yes (405) | 69 | 35997 |
| `+0x40658` | CMOV2I | x (token), y (data): set the current position for DRAWCHAR | yes (406) | 107 | 36035 |
| `+0x4065c` | LINE2I | not used by the PROM; NetBSD names it | yes (407) | 89 | 36017 |
| `+0x40660` | DRAWCHAR | see below | yes (408) | 115 | 36043 |
| `+0x40664` | RECTCOPY | see below | yes (409) | 201 | none |

PROM routines are `0xbfc2ccac` (COLOR), `0xbfc2cd68` (RECTI2D), `0xbfc2cdcc` (PNT2I), `0xbfc2ce14` (CMOV2I), `0xbfc2ce5c` (DRAWCHAR) and
`0xbfc2d1fc` (RECTCOPY) in 4.0.5D; 4.0.5G has the same routines at other addresses (token stores at `0xbfc32a94`, `0xbfc32b4c`,
`0xbfc32bb0`, `0xbfc32ca8`, `0xbfc33074`). All six are slots of one function table at `0xbfc54010` (the PROM's text-port interface, the
other four slots being the Bt457 read-mask on and off, the XMAP5 colour table write and the VC1 cursor position and screen-size
helpers). Established [binary], routines read in full. The full `hq2.bin` has no word at slots 403 (FINISH) and 409
(RECTCOPY): the IRIX microcode does not appear to implement RECTCOPY at that token (the GL core copies pixels through other tokens; inferred). The PROM image
has handlers at three further slots, `+0x40684`, `+0x40688`, `+0x4068c`, starting GE routines 245, 287 and 302; nothing read
writes them: unknown.

**FIFO flow control.** Before each token store, every PROM routine polls the byte at `0xbfb801c3` (the INT2 local-0 status register)
and waits until bit 0 is clear; the data words that follow are not checked. Established [binary] (`0xbfc2ccac` onward). The same
bit's mask is bit 0 of `0xbfb801c7`, which the kernel's FIFO handler clears and restores. A model must drive that status bit from the
FIFO fill level (threshold register `+0x6a05c`, written 40 by the PROM and kernel) and leave room for the longest operand run
that follows a clear status: 25 words for a full character strip. The interrupt-controller side is in the chips repository's INT2 page.

**DRAWCHAR operands.** `+0x40660` <- width in pixels, at most 32 (a wider glyph is drawn in 32-pixel columns, `x` offset reduced by
32 for each column); then, on the data port: rows in this strip (18 for a full strip; a final strip has fewer); words per row (1
when the glyph is at most 16 pixels wide, else 2); x offset of the bitmap relative to the current position; y offset; a fifth word
that is 0 in full strips and the glyph's advance in the last strip (NetBSD sends 0); 0; then the row words, one per row for one-word glyphs
or the 32-bit row `(first half << 16) | second half` for two-word glyphs, padded with zero words to 18 rows. The bitmap bytes are
drawn in the colour set by COLOR at the position set by CMOV2I, and the strip loop lowers the y offset by 18 per strip. Established
[binary] for the sequence (`0xbfc2ce5c`); NetBSD's call (`+0x40660` <- font width; data: font height, 2, 0, 0, 0, 0, then rows)
confirms the order [public]. The roles of the fifth and sixth words as advance values are inferred from the glyph structure fields
the PROM loads for them.

**RECTCOPY operands.** `+0x40664` <- `(width + 3) >> 2`; data: `4864 / that` (the number of lines one pass may carry, 4864 being a
budget in words), source x, source y, width, height, destination x, destination y. NetBSD sends the same eight words in the same order.
The PROM subtracts the height from 1024 and flips y (`1024 - y - height`) for the two y operands, so the hardware's y is measured from the bottom; for
other tokens the PROM passes y as given. Established [binary] (`0xbfc2d1fc`). A copy taller than one pass is split by the PROM
into several tokens, whose chunking is not described here.

**What a console also needs outside the FIFO** (each in its own page): the DAC read mask written 0xff or 0 for unblank and blank (the
first table slot, `+0x6c0a8`, `+0x6c0c8`, `+0x6c0e8` after setting each DAC's address byte to 4); XMAP5 colour table writes through the
"all" window (`+0x6c1b0` low and `+0x6c1b4` high byte of the entry index plus 4096, then three data bytes to `+0x6c1a8`), where the PROM loads entries
3073 and 3074 with two colours for the console; and the VC1 cursor (`+0x6c040` and neighbours). [binary] The 4.0.5D routine
at `0xbfc0f590` writes the two colour entries: entry 3073 = bytes `ff 00 00`, entry 3074 = `ff ff ff`, in the order the colour table
write takes its three arguments. The mapping of those bytes to the red, green and blue channels of the DACs is unknown.

## How the PROM brings the console up

All established [binary], 4.0.5D, routines at `0xbfc0e6f0` to `0xbfc0f6a8`; 4.0.5G has the same token stores and the same two image magics at shifted addresses (not read in full).

1. Probe: read `+0x6a07c` (must be `0xdeadbeef`), board revision at `+0x6c000`, backend revision, GE count, GE revision (`+0x683f4`), VC1
   revision. See [devices/ge7](../../devices/ge7/README.md), [devices/hq2](../../devices/hq2/README.md).
2. Pulse the MC graphics reset, initialise the three DACs, the clock, the XMAP5s and the VC1 (other pages).
3. Download the two **built-in console microcode images**, in this order: HQ2 (3752 bytes at `0xbfc49840`, magic `0x965e`), then GE7
   (10104 bytes at `0xbfc4a6f4`, magic `0x966e`). The HQ2 loader copies 16 words from image offset `0xfc` to `+0x6a000`, then writes
   one 32-bit word per record to `+0x60000 + 4 * address`. The GE7 loader copies 512 constants words to shared RAM, verifies them,
   then loads and verifies records as in [devices/ge7](../../devices/ge7/README.md) (no clear of the 64K store first, unlike the kernel).
4. Write 0 to `+0x6a070` (microstore address) and `+0x6a078` (the `UNSTALL` register), then write 0 to `+0x40644` (INIT; board-revision value in 4.0.5G).
5. Load the two console colours into the colour table, then draw: COLOR, CMOV2I, DRAWCHAR for text; RECTI2D for clears and cursor;
   RECTCOPY for scrolling; PNT2I for a point.

The kernel's built-in console image (`gr2_tpucode.o`) has the same job and follows the same steps; its data port is `+0x4077c`
(INIT, then COLOR, box and data writes, then the screen blank). The two images differ in layout and port (PROM: slot 0; kernel: slot 479).

## What the GL core pushes

Every FIFO offset formed in `libGLcore.so` (the n32 and o32 builds name the same offsets, except that the n32 build also uses
`+0x420a4`, `+0x42394`, `+0x42404` and `+0x42438`, listed last, and the o32 build forms some addresses as a base pointer plus an
immediate). The "operand words" column is the number of stores through the token address in the function's first straight
run, so it is a lower bound for loop-driven tokens (matrices count 15 or 16 for a 4x4 matrix) and is **inferred**; `n/a` means
the run was not counted. "Slot" is bits 10:2 of the offset. "GE routine" is the GE7 microstore address the HQ2 starts for that slot
in `hq2.bin` (inferred as described in [devices/ge7](../../devices/ge7/README.md)); `HQ2` means the slot has an HQ2 word that does not start
a GE routine; `-` means the slot has no first-level HQ2 word (vertex, texture-environment). Function names are the shipped symbol
names with their `__glExp` prefix dropped; `im:` and `le:` are the immediate-mode and display-list-compile forms.

| Offset | Slot | GL functions | Operand words | GE routine |
|---|---|---|---|---|
| `+0x42000` | 0 | SwapToPipe4 (see Review: the base address, not a stored token) | 0 | 30 |
| `+0x4200c` | 3 | SetPixWritemask | 0 | 1607 |
| `+0x42010` | 4 | MakeCurrent | 1 | 1628 |
| `+0x42018` | 6 | Flush, MakeCurrent | 1 | 2797 |
| `+0x42028` | 10 | PassDepthMask | 0/1 | 1752 |
| `+0x42038` | 14 | MakeCurrent | 1 | 2115 |
| `+0x4203c` | 15 | EnableStencilTest, PassStencilMode, Store | 1 | 2137 |
| `+0x42040` | 16 | PassStencilMask, Store | 0/1 | 2169 |
| `+0x42044` | 17 | Clear, CZClear, EnableDither | 0/1 | 1662 |
| `+0x4204c` | 19 | PassShadeModel | 1 | 1587 |
| `+0x42050` | 20 | EnableDepthTest | 1 | 1713 |
| `+0x42058` | 22 | PassLineStipple | 0 | 2580 |
| `+0x4205c` | 23 | PassLineWidth | 1 | 2620 |
| `+0x42060` | 24 | PassLineStipple | 0 | 2599 |
| `+0x42068` | 26 | PassLogicOp | 1 | 1655 |
| `+0x4206c` | 27 | PassCullFace | 1 | 2216 |
| `+0x42070` | 28 | PassCullFace, EnableCullFace | 1 | 2201 |
| `+0x42078` | 30 | EnablePolygonStipple | 1 | 2242 |
| `+0x4207c` | 31 | PassPolygonStipple | 1 | 2249 |
| `+0x42080` | 32 | MakeCurrent | 1 | 1669 |
| `+0x42084` | 33 | EnablePointSmooth | 1 | 2665 |
| `+0x42088` | 34 | EnableLineSmooth | 1 | 2632 |
| `+0x42090` | 36 | PassDepthFunc | 1 | 1736 |
| `+0x42094` | 37 | PassBlendFunc | 3 | 2720 |
| `+0x42098` | 38 | PassBlendFunc | 1 | 2736 |
| `+0x4209c` | 39 | EnableFog | 1 | 2743 |
| `+0x420a0` | 40 | PassFog | 6 | 2753 |
| `+0x420a8` | 42 | TextureSpan, TextureStippledSpan | 0 | 31242 |
| `+0x420b4` | 45 | TextureStippledSpan | 0 | 31242 |
| `+0x420b8` | 46 | EnableClipPlanes | 0 | 993 |
| `+0x420bc` | 47 | PassClipPlanes | 0 | 1012 |
| `+0x420dc` | 55 | UpdateMatrixState, PassMatrix | 16 | 355 |
| `+0x420e0` | 56 | UpdateMatrixState, PassMatrix | 16 | 298 |
| `+0x420e4` | 57 | PassMatrix | 9 | 480 |
| `+0x420e8` | 58 | UpdateMatrixState, PassMatrix | 16 | 492 |
| `+0x420ec` | 59 | UpdateViewport | 1 | 501 |
| `+0x420f0` | 60 | ApplyScissor | 0 | 879 |
| `+0x42118` | 70 | BeginTStrip, BeginTFan | 1 | 30210 |
| `+0x42128` | 74 | EndTStrip, EndTFan | 1 | 30210 |
| `+0x42130` | 76 | BeginQStrip | 1 | 28674 |
| `+0x42144` | 81 | EndQStrip | 1 | 30210 |
| `+0x4215c` | 87 | EndLStrip, EndLines | 1 | 15362 |
| `+0x42160` | 88 | BeginLLoop | 1 | 14338 |
| `+0x42168` | 90 | EndLLoop | 1 | 15620 |
| `+0x421c4` | 113 | CopyToPipe4, CopyToPipe1, SwapToPipe1 | 0/1 | 24248 |
| `+0x421d0` | 116 | LoadSpecLUT | 0 | 16268 |
| `+0x421d4` | 117 | LoadAmbientSum | 3 | 16212 |
| `+0x421d8` | 118 | ValidateMaterial, InitLighting | 3 | 16218 |
| `+0x421dc` | 119 | ValidateMaterial | 3 | 16224 |
| `+0x421e0` | 120 | ValidateMaterial, InitLighting | 3 | 16230 |
| `+0x421e4` | 121 | ValidateMaterial | 3 | 16236 |
| `+0x421e8` | 122 | ValidateMaterial | 4 | 16242 |
| `+0x421ec` | 123 | ValidateMaterial | 4 | 16249 |
| `+0x421f0` | 124 | ValidateMaterial | 3 | 16256 |
| `+0x421f4` | 125 | ValidateMaterial, InitLighting | 3 | 16262 |
| `+0x421fc` | 127 | LoadLightSource | 4 | 16312 |
| `+0x42200` | 128 | LoadSpecLUT, LoadSpotLUT, LoadLightSource ... | 0/2/3/6/8 | 15694 |
| `+0x42204` | 129 | ValidateColorMaterial | 3 | 15948 |
| `+0x42208` | 130 | EnableNormalize | 0 | 2187 |
| `+0x4220c` | 131 | LoadLightPath, ValidateMaterial | 1 | 16460 |
| `+0x42210` | 132 | LoadLightSource | 3 | 16418 |
| `+0x42214` | 133 | LoadLightPath, InitLighting | 2 | 16145 |
| `+0x42280` | 160 | CZClear | 1 | 25145 |
| `+0x42284` | 161 | Clear | 1 | 25322 |
| `+0x4228c` | 163 | SwapBuffers, Finish, GetOrigin ... | 1 | 2770 |
| `+0x4229c` | 167 | ReadColor, Fetch, InitPackAndUnpack ... | 1 | 27253 |
| `+0x422a0` | 168 | ReadColor, Fetch, InitPackAndUnpack ... | 0/1 | 27267 |
| `+0x422b4` | 173 | ReadColor, Fetch, ReadPixelsPack1 ... | 0/1 | 26475 |
| `+0x422c4` | 177 | DrawPixelsUnpack4, DrawPixelsUnpack1 | 1 | 26667 |
| `+0x422c8` | 178 | DrawPixelsUnpack4, DrawPixelsUnpack1 | 0 | 26667 |
| `+0x422cc` | 179 | DrawPixelsUnpack4, DrawPixelsUnpack1 | 0 | 26667 |
| `+0x422e8` | 186 | FastCopyPixels | 1 | 26537 |
| `+0x422ec` | 187 | DrawPixelsUnpack4, DrawPixelsUnpack1, DrawPixelsKDMA ... | 3 | 27281 |
| `+0x422f0` | 188 | ReadColor, Fetch, DrawPixelsKDMA ... | 1 | 27323 |
| `+0x422f4` | 189 | Fetch, ReadPixelsPack1, GetOrigin ... | 1 | 27302 |
| `+0x42334` | 205 | GetOrigin | 1 | 1284 |
| `+0x42350` | 212 | LoadLightPath | 0 | 16145 |
| `+0x42388` | 226 | PassPolygonMode | 1 | 2699 |
| `+0x4238c` | 227 | EnableNormalize | 1 | 2194 |
| `+0x42390` | 228 | PassPolygonOffset | 0 | 2713 |
| `+0x42398` | 230 | MakeCurrent | 1 | 206 |
| `+0x423a4` | 233 | GetColor, GetIndex | 1 | 1336 |
| `+0x423a8` | 234 | GetNormal | 1 | 1345 |
| `+0x423c0` | 240 | BeginTriangles | 1 | HQ2 |
| `+0x423c4` | 241 | EndTriangles | 1 | 4610 |
| `+0x423cc` | 243 | BeginQuads | 1 | HQ2 |
| `+0x423d0` | 244 | EndQuads | 1 | 5122 |
| `+0x423d8` | 246 | PassEdgeFlag, im:EdgeFlag, im:EdgeFlagv | 1 | 1336 |
| `+0x423dc` | 247 | BeginPolygon | 1 | 3074 |
| `+0x423f0` | 252 | EndPolygon | 1 | 3074 |
| `+0x423f4` | 253 | EndPolygon | 1 | 3074 |
| `+0x42408` | 258 | LoadLightSource | 0 | 16408 |
| `+0x42410` | 260 | Clear | 1 | 25115 |
| `+0x42414` | 261 | im:RasterPos2dv, im:RasterPos2fv, im:RasterPos2d ... (all 24 `RasterPos` forms) | 1, then 3 on the data port in 6.5; 1 in 6.2 ([slot 261](#slot-261-the-raster-position-token)) | 24366 (6.5), 1374 (6.2) |
| `+0x42418` | 262 | PassRasterPosData | 1 | 1361 |
| `+0x4241c` | 263 | GetRasterPosData | 1 | 1374 |
| `+0x42420` | 264 | PassFrontFace | 1 | 2209 |
| `+0x42424` | 265 | LoadLightSource | 3 | 15847 |
| `+0x42428` | 266 | SetReadSource, SetReadBuffer, Fetch ... | 0/2 | 2062 |
| `+0x4242c` | 267 | SetPixWritemask | 0 | 1614 |
| `+0x42434` | 269 | EvalPassCurrentState, EvalRestoreCurrentState, le:Normal3fv ... | 3 | HQ2 |
| `+0x42474` | 285 | BeginPoints | 1 | 13711 |
| `+0x425a0` | 360 | EndPoints | 1 | 13570 |
| `+0x425f0` | 380 | BeginLStrip, BeginLines | 1 | HQ2 |
| `+0x4263c` | 399 | PassPointSize | 1 | 2684 |
| `+0x4277c` | 479 | RenderBitmap, Store, Store_ND ... | 0/1/2/3/4/11 | HQ2 |
| `+0x4279c` | 487 | SwapBuffers, MakeCurrent | 1 | 13406 |
| `+0x4298c` | 99 | im:Vertex4dv, im:Vertex4fv, im:Vertex4d ... | 4 | - |
| `+0x4311c` | 71 | BeginTStrip | 1 | 30210 |
| `+0x43134` | 77 | BeginQStrip | 1 | 28674 |
| `+0x43158` | 86 | BeginLStrip | 1 | 14338 |
| `+0x43164` | 89 | BeginLLoop | 1 | 14338 |
| `+0x43194` | 101 | EndLLoop, EndLStrip, EndLines ... | 1 | 7940 |
| `+0x433ac` | 235 | BeginLines | 1 | 14338 |
| `+0x433b4` | 237 | BeginTFan | 1 | 30210 |
| `+0x433c8` | 242 | BeginTriangles | 1 | HQ2 |
| `+0x433d4` | 245 | BeginQuads | 1 | HQ2 |
| `+0x433e0` | 248 | BeginPolygon | 1 | 3074 |
| `+0x4348c` | 291 | BeginPoints | 1 | 13570 |
| `+0x4498c` | 99 | le:Vertex3fv, im:Vertex3dv, im:Vertex3fv ... | 3 | - |
| `+0x4698c` | 99 | im:Vertex2dv, im:Vertex2fv, im:Vertex2d ... | 2 | - |
| `+0x48608` | 386 | le:Color3fv, im:Color3d, im:Color3dv ... | 3 | HQ2 |
| `+0x4a608` | 386 | EvalPassCurrentState, PassColor, im:Color4d ... | 0/4 | HQ2 |
| `+0x4e3f8` | 254 | PassIndex, im:Indexd, im:Indexf ... | 1 | 1351 |
| `+0x4e410` | 260 | Clear | 1 | 25115 |
| `+0x4e77c` | 479 | Store, Store_ND, ValidateMaterial ... | 0/1/3 | HQ2 |
| `+0x4ec00` | 256 | __glim_TexEnvfv, __glim_TexEnviv | 0 | - |
| `+0x520ac` | 43 | Store, Store_ND, Store_B | 1 | 31268 |
| `+0x5277c` | 479 | Store, Store_ND, Store_B | 1/2 | HQ2 |
| `+0x5298c` | 99 | im:Vertex4i, im:Vertex4iv, im:Vertex4s ... | 4 | - |
| `+0x5498c` | 99 | im:Vertex3i, im:Vertex3iv, im:Vertex3s ... | 3 | - |
| `+0x5698c` | 99 | im:Vertex2i, im:Vertex2iv, im:Vertex2s ... | 2 | - |
| `+0x58608` | 386 | im:Color3ub, im:Color3ubv, im:Color3b ... | 3 | HQ2 |
| `+0x5a608` | 386 | im:Color4ub, im:Color4ubv, im:Color4b ... | 4 | HQ2 |
| `+0x5c280` | 160 | Clear | 0 | 25145 |
| `+0x5e280` | 160 | CZClear | 1 | 25145 |
| `+0x5e3f8` | 254 | im:Indexi, im:Indexs, im:Indexub ... | 1 | 1351 |
| `+0x420a4` | 41 | TextureSpan, TextureStippledSpan | n/a | 31234 |
| `+0x42394` | 229 | FreeLightLUT | n/a | 15859 |
| `+0x42404` | 257 | FreeLightLUT | n/a | 16398 |
| `+0x42438` | 270 | FreeLightLUT | n/a | 16145 |

Notes on groups, all [binary] unless marked: **Begin and End** tokens send one zero-valued operand each. A Begin sends two
tokens, the primitive-specific Begin (slot 71 and 77 for strips, 235 for lines and so on) and a second token (for example `+0x433c8`
for triangles); End sends the primitive's End token and the generic End `+0x43194` (slot 101). **Colour clear** sends the red value to
`+0x42410` and green, blue, alpha to the data port; **depth clear** sends 0 to `+0x5c280` and the clear depth, scaled by the depth
range, then 0 to the data port; both bracket the operation with `+0x42044` (the dither token, written 0 before and 1 after). Inferred
from the function names for the reading of `+0x42044` as dither. **Pixels:** reads send the origin and size to `+0x422b4`,
`+0x422f0` and `+0x422f4`, then poll a status bit at `+0x6c040` before reading the result from shared RAM at `+0x12088`; the GL core never
reads the framebuffer through a host window. [binary] `ReadColor` (colour index build). The poll reads `+0x6c040`, which NetBSD names the VC1
command port: unresolved, see [questions/re3.md](../../questions/re3.md).

### Slot 261: the raster position token

Slot 261 is not texture or pixel-transfer state. The GL cores of all three releases use it only for raster-position work (`glRasterPos` and the state save and restore around it), and what the board keeps from it is the colour that `glBitmap` and `glDrawPixels` later draw in. How many words it takes depends on the release of the microcode image the host loaded, because the operand count is whatever the HQ2 slot code reads. [binary] `libGLcore.so`, `hq2.bin` and `ge7.bin` of each release (hashes in [binaries.md](../../references/binaries.md)); the HQ2 walk is `tools/ucode-decode.py hq2 IMG 261`.

| Release | Host stores to `+0x42414` | HQ2 slot 261 code | GE7 start |
|---|---|---|---|
| IRIX 5.3 | none: the o32 GL core's `RasterPos` entry points make no store (they call the software raster position code and stop). The microcode still has the slot | one operand read, no other loads | 24459 |
| IRIX 6.2 | one word, the value 0, after the software code has set the position. All 24 `__glexpim_RasterPos` forms; also `__glExpPassRasterPosData` and `__glExpGetMachineState` | no operand read; four loads from the HQ2 attribute store (`0xd3`, `0xf4`, `0x115`, `0x136`) | 1374 |
| IRIX 6.5 (o32 and n32) | four words: the x coordinate to `+0x42414`, then y, z and w on the data port `+0x4277c` (a 2-component form sends z = 0 and w = 1, converting integer and double inputs to float first). All 24 forms | four slot reads (`slot16` to `slot19`), then the same four attribute loads | 24366 |

Word counts: established [binary] for the host stores (every `RasterPos` entry point read in the 6.2 o32 build, the 6.5 n32 assembly and the 6.5 o32 build; a constant-tracking scan of the whole 5.3 o32 core finds no store to slot 261 outside two struct-field false positives). Established [binary] for the HQ2 code of each image.

What the routines do: the four attribute loads are four values of the board's current colour (inferred from the 6.5 caller: it latches the colour at the position). In 6.2 the GE7 routine at 1374 stores four words to shared words `0x147`, `0x148`, `0x149` and `0x8d` (the stepper's run with no inputs, `tools/ge7-step.py run`; the values come from the loads, inferred), and the read-back token 263 (GE7 1384 in 6.2) stores four words to the mailbox words `0x4022` to `0x4024` and `0x8d`, which `__glExpGetRasterPosData` reads as floats at `+0x12088` after polling bit 0 of `+0x6c040` (established [binary] for the host's reads, inferred for the routine's data flow). So the visible effect of 261 is "latch the current colour as the raster colour"; in 6.5 it also carries the object-space position, which the GE transforms. A model that executes no microcode must, for 261, consume exactly the words the loaded image reads (one in 6.2, four in 6.5), latch the current colour, and answer 263 with it. Whether the one word's value matters is not shown: the 6.2 host always stores 0 and the HQ2 code has no read for it.

The Indy and Indigo2 Express GL core stores the same offsets in the same order: [ip22-slot-comparison.md](ip22-slot-comparison.md).

## What the X server pushes

The X driver (`gr2.so`) forms its FIFO addresses as `base + 0x40000 + immediate`. Offsets seen in its drawing, window, glyph, image
and initialisation code (committed disassembly under `gr2_ddx/asm`): `+0x404b0`, `+0x404c0`, `+0x404c4`, `+0x404cc`, `+0x404d4` (most used
in window and solid-fill code), `+0x404dc`, `+0x404e0`, `+0x404e4`, `+0x404e8`, `+0x404ec`, `+0x404f0`, `+0x404f4`, `+0x404f8`, `+0x404fc`,
`+0x40500`, `+0x40510`, `+0x40514`, `+0x4052c`, `+0x40530` (the two most used), `+0x40540`, `+0x40544`, `+0x40550`, `+0x40558`, `+0x40568`,
`+0x40588`, `+0x4058c`, `+0x40590`, and `+0x407a8`; data goes to `+0x4077c`. Their GE routine starts are the range 31835 to 35514 in
`hq2.bin` (the X server has its own routines rather than the GL core's). Established [binary] for the offsets (the token names
are unknown). Operand layouts are not catalogued here.

## What a model needs

- **PROM console.** Probe words (`0xdeadbeef` at `+0x6a07c`, board revision, backend revision, GE count and revision, VC1 revision);
  the microcode load windows for HQ2 and GE7 that accept writes and read back with the verify masks; shared RAM; the INIT / COLOR /
  PNT2I / RECTI2D / CMOV2I / DRAWCHAR / RECTCOPY tokens implemented directly (their operand layouts are above) with a framebuffer
  the colour table and the XMAP5 colour mode map to the screen; the INT2 FIFO status bit. Executing the loaded microcode is not
  required: the images are fixed and the effect of nine tokens is described here. A model that wants to execute them needs the GE7
  and HQ2 instruction sets, which are unknown.
- **IRIX X.** Everything above plus the X server's FIFO tokens (about 30, unnamed), VC1 cursor and window-ID handling, XMAP5 modes, and
  pixel DMA through the MC. The tokens' operand layouts are partly readable from `gr2.so` and not yet catalogued.
- **GL.** The 131 token addresses above with their operand layouts for lighting, matrices, primitives and pixel transfer, plus the **GE7 and
  RE3 behaviour behind them**: the results the engines produce for transform, clip, lighting, setup and rasterisation. Without a
  decoded instruction set the only route is a behavioural reimplementation of each routine, validated against the GL
  specification; the instruction set and the RE3 parameter format remain the open work (see the two question files).

## Review (2026-11-23)

Independent check against `hq2.bin`, `ge7.bin`, the 4.0.5D PROM, `gr2_tpucode.o` and the n32 `libGLcore.so` (SHA-256 `b6731da1...` confirmed; the survey's binaries list carried a different hash for it and is corrected). Details for the GE7 side are in [devices/ge7](../../devices/ge7/README.md#review-2026-11-23).

- CONFIRMED: slot = bits 10:2; console tokens at 401 to 409 with 403 absent in both images and 409 absent in `hq2.bin`; the six console GE starts; `hq2.bin` attribute reading of slot 99 (empty, resolved through the table) as stated; PROM flow control (`0xbfb801c3` bit 0 polled before the token store); RECTI2D and RECTCOPY operand order and the `1024 - y - height` flip; 4864/width budget; entries 3073 and 3074 written by `0xbfc0f590` as (255,0,0) and (255,255,255); data ports `+0x40000` (PROM) and `+0x4077c` (kernel image); HQ2 loader copies 16 words from `0xfc` to `+0x6a000` and writes records to `+0x60000 + 4 * address`; INIT at `+0x40644`.
- CONFIRMED: every row of the table reproduces its slot and GE routine from `hq2.bin` (script, 131 rows). Twelve function names confirmed in the GL core.
- WRONG (fixed): one markdown row had been fused with the last four rows of the n32-only list (`| 1351 || ...`); split.
- WRONG (fixed): the count "140 tokens" is 131 addresses in the table; text corrected.
- WRONG (flagged, not removable by this review): the row `+0x42000` (slot 0, "SwapToPipe4", GE 30). The function stores through a register holding `0x42000` only at displacements `+0x1c4` and `+0x77c`, never at displacement 0, and a constant-tracking scan of the whole n32 GL core finds no store to `+0x42000` at all. The row is the base of the `0x42000` window, so it is not an observed token; the same is probably true of `+0x4ec00` (no store found; a tracking miss in the o32-style path is possible). Both are now unverified, and "30 = buffer swap" is a name guess.
- GRADE (gap, not changed): the same scan finds stores to `+0x40000` (`SlowRenderBitmap`), `+0x420f4` to `+0x42114` (the nine slots 61 to 69, written by `PassMatrix`, evidently the nine elements of a 3 by 3 matrix) and `+0x42218`, none of them in the table. Slots 63 and 64 have no `hq2.bin` word, 65, 66, 68 and 69 have a word that starts no GE routine, 61, 62, 67 start 860, 812, 1565, and `+0x42218` (slot 134) starts 16291. The table is therefore not complete, and "the 131 token addresses above" should not be read as all of them.
- GRADE: "operand words" counts are inferred, as stated; not rechecked.
- UNVERIFIED: the X server offsets list and the o32 build (neither object is held); PROM 4.0.5G INIT value by board revision; DRAWCHAR operand semantics beyond the order; the INT2 status-bit mapping (chips repository).
