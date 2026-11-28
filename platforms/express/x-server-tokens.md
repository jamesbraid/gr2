# Express: the 2D tokens the X server sends

What the shipped X server driver writes to the FIFO for rectangles, spans, points, lines, copies, image transfers, clip IDs and a few housekeeping
steps, in the order it writes them, with the operand layout of each token. The token catalogue is [pipeline.md](pipeline.md), the flow control
and kernel contract [host-contract.md](host-contract.md), the GL stream [icd-sequences.md](icd-sequences.md). This page fills the gap the first two
leave: "operand layouts are not catalogued".

## Sources and grades

- **X driver.** `usr/lib/X11/dyDDX/gr2.so` of the IRIX 6.5 base set (SHA-256 `eb5aa0c91259fd1d7186e146f0b62ae172b1bfa609ed0c60debd6bd54dd10fa2`, n32, `.dynsym` kept). Addresses
  are its virtual addresses. Every function named here was disassembled from this file; the committed listing under `gr2_ddx/asm` names argument registers
  in a way that does not fit this ABI (its `$a4` to `$a7` are `$t0` to `$t3`), so it was not used. A function's FIFO base is a register holding the
  board mapping plus `0x40000`; the sections below give offsets from that base.
- **Kernel side.** `IP20boot/gr2.a`, `gr2.o` and `gr2_dma.o` of the same set, for the clip words, the DMA record and the context tokens.
- **Grades** as in [AGENTS.md](../../AGENTS.md). **Established** means the stores, their order and the value sources were read in the function body
  named. A role (what a word means to the hardware) is **inferred** from the sender's arguments unless a row says otherwise: no source decodes the
  microcode instruction set, so no layout here is confirmed on the receiving side. Nothing was run.

Notation: `[S309 <- 0]` is one 32-bit store to slot 309 (`+0x404d4`); `D <- a, b` is stores to the data port `+0x4077c` (slot 479); `base + 0x40000`
is written as the offset. "Window code" is the word at offset `0x14` of the X driver's per-window record, which the functions read first.

## Slot map

Offsets from the window base; slot = offset >> 2 & 0x1ff. Walk counts are from [hq2-slot-table.md](hq2-slot-table.md) (6.5 image; the token word counts as the
first operand where the sender stores a value there).

| Slot | Offset | Used for | Operands as sent | Grade |
|---|---|---|---|---|
| 304 | `+0x404c0` | rectangle list | token 0; then 4-word rectangles; list closed by slot 490 | Established |
| 305 | `+0x404c4` | span list | token 0; then 3-word spans; closed by slot 490 with -1 | Established |
| 303 | `+0x404bc` | point list | token 0; then (x, y) pairs; closed by slot 490 | Established |
| 301 | `+0x404b4` | line, fewer than 5 engines | token 0; 4 data words per segment | Established for the choice; word roles inferred |
| 355 | `+0x4058c` | line, 5 or more engines | token 0 | Established for the choice; layout not read |
| 309 | `+0x404d4` | plane-bit select for small windows | one word: 0, or the plane mask limited to the window's plane bits | Established values, role inferred |
| 331 | `+0x4052c` | pixel mode | one word: the window code, usually with `0x1000` set | Established values, role inferred |
| 332 | `+0x40530` | draw state | token = colour; data = plane mask (24 bits), raster op, display-ID word | Established stores, roles inferred |
| 336 | `+0x40540` | clip-ID write value | one word: `(CID << 8) \| 0xf000`, or 0 to end | Established stores, role inferred |
| 337 | `+0x40544` | pixel packing | token = packing code; one data word (alignment or 0) | Established stores, role inferred |
| 340 | `+0x40550` | rectangle copy | token = words per row; 7 data words | Established |
| 342 | `+0x40558` | image write by FIFO | token = x; 6 data words, then up to 16 payload words | Established |
| 327 | `+0x4051c` | image write by DMA (board command) | token = x; 5 data words from the kernel | Established |
| 344 | `+0x40560` | image read | token = words per row; 4 data words | Established |
| 341 | `+0x40554` | wait for idle | one word, 0 | Established stores, role inferred |
| 490 | `+0x407a8` | list terminator | one word: 0, or -1 after spans | Established stores, role inferred |

Slot 490 has **no first-level HQ2 word** in the 6.5 `hq2.bin` (`tools/ucode-decode.py hq2 IMG 490` prints none), yet every list above ends with a store to
it: stores to a slot with no word are part of ordinary shipped operation (see [host-contract.md](host-contract.md#the-fifo-rules-a-driver-has-to-obey)).

## The preamble every drawing function sends

Established in `expDrawSolidRects` (`0x5ef39a54`), `expSolidSpans` (`0x5ef351f4`), `expCopyRect` (`0x5ef52280`), `expDrawImage` (`0x5ef4d5f4`), `expReadImage`
(`0x5ef4df8c`) and `expDrawPoints` (`0x5ef4d28c`), each read to its last store:

1. `[S331 <- window code | 0x1000]`, then `[S309 <- 0]`. Solid rectangles store the window code **without** `0x1000`; the screen clears in `expInitHW` and
   `expValidateVisual` store 8 or 4 without it too. For three window codes the pair differs: code `0xc` stores 331 = 8 and 309 = plane mask & `0xf`;
   code `0xd` stores `0xb` and mask & 3; code `0xe` stores `0xb` and mask & `0xc` (each with `0x1000` set, except in solid rectangles). All six functions branch on exactly these three codes. Inferred: the window code is a pixel-mode code from the same code space the GL core uses for
   [slot 4](icd-sequences.md#12-first-make-current) (RGB 24-bit 4, colour-index 8-bit 9, and so on): the clears use 4 for 24-bit RGB and 8 for four-bit index
   planes, which are those GL values. Codes `0xc` to `0xe` look like the four-bit overlay planes, whole and as two halves; that reading is inferred.
2. `[S332 <- colour]`, then `D <- plane mask & 0xffffff, raster op, display-ID word`. The colour is the GC's foreground pixel for fills, spans and points and 0 for
   copy, image and read. The raster op is the X alu function (the screen clears send 3, which is GXcopy). The display-ID word is the window's display ID shifted
   left by 3 for ordinary windows, 0 for 24-bit image functions, and the constants 1 (codes `0xc`, `0xd`) or 9 (code `0xe`) for the overlay windows; the plane-mask
   word is 0 for those three codes. Established for the values; the names plane mask, raster op and display ID are inferred from the X server's own GC
   fields (offsets `0x40`, `0x48`, `0x4c` of the GC record) and from the clear's 3.

Which of these state tokens a function needs first: all of them, in this order, before the drawing token. The three drawing families that add a fourth state token
are copy, image write and image read (slot 337), and clip-ID draw (slot 336).

## Rectangles, spans, points

- **Solid rectangles** (`expDrawSolidRects`): preamble, then `[S304 <- 0]`, then **four data words per rectangle: x1, y1, x2, y2** as signed 16-bit values
  taken from the clip box array (the caller `nfbPolyFillRect` builds each clipped box from an `xRectangle` by adding the width, `0x5ef8b540` to `0x5ef8b554`; that
  every box comes through that path was not traced), then `[S490 <- 0]` once after the last rectangle. The rectangle list is therefore one token and a run of four-word groups, not one token each.
  Whether the second corner is inclusive is unknown: the senders pass the X server's half-open box unchanged, while the PROM sends the console `RECTI2D` inclusive (it
  sends width - 1 and height - 1), so the two tokens may not take their corners the same way.
- **Spans** (`expSolidSpans`): preamble, `[S305 <- 0]`, then **three words per span: x, y (signed 16-bit) and the span width (a 32-bit word from a separate
  array)**, then `[S490 <- -1]`.
- **Points** (`expDrawPoints`): preamble with the fill colour, `[S303 <- 0]`, then **x and y of each point, with the drawable's origin added**, then `[S490 <- 0]`.
  Slot 303's operand count in the microcode is 2, which matches one pair.
- **Clears at start-up** (`expInitHW` `0x5ef567b0`, and the first block of `expValidateVisual`): `[S300 <- 0]` first (role unknown), then box fills in the layout above: pixel mode 8 with
  309 = `0xf` and display-ID word 1 for the four-bit planes, then pixel mode 4 for 24-bit RGB with plane mask `0xffffff` and a box from (0, 0) to the screen size, each with colour 0
  and raster op 3 and closed by 490, then a clip-ID clear (`[S336 <- value]`, one box, `[S490 <- 0]`, `[S336 <- 0]`) and the slot 354 call described in [pipeline.md](pipeline.md#thirteen-tokens-per-command). The boxes of the four-bit and clip-ID clears were not read.

## Rectangle copy

`expCopyRect` (`0x5ef52280`) takes a destination box (x1, y1, x2, y2), a source point, the raster op and the plane mask (the box and point order follow X's copy-area convention; the stores below
show the box's size and its corner go after the point), and returns at once if the width or height is zero:

1. Preamble (colour 0), then `[S337 <- packing code]` and `D <- 0`.
2. `[S340 <- words per row]`, then `D <-` **4864 / words per row, source x, source y, width, height, destination x, destination y**.

Words per row is `(width + 3) >> 2` for depths 2, 4 and 8, `(width + 1) >> 1` for depth 12, and `width` for depth 24; the packing code is 2, 1 and 0 for those three
(the depth-2 and depth-4 cases share the 8-bit value). This is the same layout as the console `RECTCOPY` token ([pipeline.md](pipeline.md#the-console-tokens)), including the
budget of 4864 words, so slot 340 is the full image's version of the copy the full `hq2.bin` lacks at slot 409. Established for the stores. Unlike the console token, the X path
passes y unchanged: there is no `1024 - y - height` flip in `expCopyRect`, `expDrawSolidRects`, `expSolidSpans`, `expDrawImage` or `expReadImage`. Inferred: for these tokens the
board's y runs down the screen as X's does (the shipped server draws correctly sending it so); the console copy and the GL clip words ([below](#per-window-clip-words)) are the bottom-origin ones.

## Image write

`expDrawImage` (8-bit, `0x5ef4d5f4`), `expDrawImage24` (`0x5ef514cc`) and the 12-bit forms share this shape:

1. Preamble, then `[S337 <- packing code]` and `D <- alignment` (the source pointer's low two bits for 8-bit data, 0 for 24-bit).
2. Images below about 20000 bytes (8-bit) or 5000 pixels (24-bit) go by FIFO: for each group of rows, `[S342 <- x1]`, then `D <-` **y, width, rows in this group, words per row,
   packing code (2 in the 8-bit function), alignment**, then the pixel words (rows times words per row), then filler words `0xdeadbeef` up to a total of 16 payload words, and finally `[S490 <- 0]`.
   Words per row is `(width + alignment + 3) >> 2` for 8-bit and `width` for 24-bit: **8-bit pixels are packed four to a word, 24-bit pixels one to a word.** The group size is 16 divided
   by words per row; rows wider than 16 words take a branch (`0x5ef4d7d4`) that was not read.
3. Larger images go by DMA: the same state tokens, then repeated `ioctl(fd, 0x3aa2, record)` calls of at most `0x20000` bytes (at most 68 rows) with the record below, which the kernel
   turns into the board command in slot 327 and an MC transfer ([host-contract.md](host-contract.md#3-pixel-dma-gr2_dmao)).

The kernel's record (`_Gr2MCDMAtrigger`, `gr2_dma.o` `0xad4`, and `Gr2MCPixDma`, `0xd0c`; filled by `expDrawImage` and, for GL, by `__glExpDrawPixelsKDMA`): word 0 the board slot (327 here; 181 or 184
for GL), word 1 the token operand (x), word 2 the width, word 3 the first y (advanced by word 7 for each row sent), word 4 the row count, a half-word at `0x14` of flags (bit 0 host to board, bit 1
strided, bit 2 bottom-up, bit 3 puts a 1 in the last data word, bit 4 a second flag), word 6 the memory pitch in words, word 7 the y step, word 9 the words per row, word 10 the user address.
The board command is `[S slot <- x]`, then `D <-` **first y, width, rows in this transfer, words per row, flag (bit 3 of the flags)**, queued after `dmasync` is set to 2 and `fin2` cleared and before the MC
starts. Established for the record fields read (the kernel reads them in `Gr2MCPixDma` and `_Gr2MCDMAtrigger`; the sender fills them in `expDrawImage`), inferred for the names.

## Image read

`expReadImage` (`0x5ef4df8c`), for results up to 4096 bytes: preamble with raster op 3 and a mask of `0xffffff`, `[S337 <- 2]` and `D <- alignment`, then per group of rows:
store 0 to `+0x6b000` (clear finish flag 3), `[S344 <- words per row]`, `D <- x1, y, width, rows`, poll HQ2 status bit 0 (finish flag 3, [host-contract.md](host-contract.md#finish-flags-and-the-finish--sync-mechanism)), and copy the
words from shared RAM starting at `+0x1b000`. Larger reads take another branch (`0x5ef4e354`) that was not read; it presumably uses the DMA path. The server unpacks the four-to-a-word bytes itself.

## Clip ID draw

`expDrawCID` (`0x5ef4d4b4`) draws a list of clip boxes into the clip-ID planes: `[S331 <- 0x100b]`, `[S309 <- 0]`, `[S332 <- 0]`, `D <- 0, 3, 1`, `[S336 <- (CID << 8) | 0xf000]`, then for each box
`[S304 <- 0]`, `D <- x1, y1, x2, y2` and `[S490 <- 0]`, and last `[S336 <- 0]`. Established for the stores. Inferred: pixel mode `0xb` with the constants 3 (copy) and 1 is the two-bit plane window
form, 336 carries a four-bit write enable in bits 15:12 and the clip ID in bits 11:8, and the planes written are the four clip-ID planes the board lists. The XMAP5 mode word has no clip-ID
field ([xmap5](../../devices/xmap5/README.md#mode-word)).

## Lines

`expLineSS` (`0x5ef64460`) picks the token from the geometry-engine count in the board record: a count below 5 stores 0 to slot 301, anything else stores 0 to slot 355 (`0x5ef64570` to `0x5ef64594`);
that selects the line routine of the one-to-four-engine boards or of the eight-engine Extreme, and is established. The segment data that follows is four words per segment (the end points, window
origin added, at `0x5ef647d0` to `0x5ef647dc` and `0x5ef64d8c` to `0x5ef64d9c`); the clipped and wide forms send other groups that were not decoded, and each list ends with a store to slot 490. The roles and order
of the four words are inferred, not read from a named source.

## Wait for idle

`expDisplayCursor` (`0x5ef6115c`, the poll read in full) and `expStoreNormalColors` (`0x5ef36718`, the token store only) store `[S341 <- 0]` and wait on HQ2 status bit 0 before they write XMAP colour-table entries, then store 0 to `+0x6b000`. So
slot 341 plays the part of the GL core's slot 163 for the X path: a finish token that raises finish flag 3. Inferred: the walk (one operand, a GE7 start at 33688) says nothing about the flag.

## Per-window clip words

The kernel's window set-up for GL windows, `Gr2ValidateClip` (`gr2.o` `0x22d0`, established), sends `[S6 <- 0]` (flush) and then `[S485 <- window x]` followed by `D <-` **1024 - (y + height), width, height, two window words from
the record (`0x20`, `0x24`), the clip-rectangle count, and eight clip words**: for each of up to four rectangles one word `((x2 - 1) << 11) | x1` and one word `((1023 - y1) << 10) | (1023 - y1 - h + 1)`, the rest zero-padded to eight.
With zero rectangles or more than four it sends the window's bounding box instead. This is the 15-word operand set that slot 485's microcode walk shows. Here y is flipped to bottom-origin. See
[host-contract.md](host-contract.md#2-context-save-and-swap-_gr2cxsaverestore-gr2pcxswap) for 480, 486 and 496.

## Not decoded here

Tokens 300, 302, 306 to 308, 310 to 330, 335, 338, 339, 345 to 353, 356 to 362 (stipples, tiles, glyph blits, mono images, the 12-bit read token 338, the clipped line forms) are catalogued by sender and data-store count in [host-contract.md](host-contract.md#x-driver-tokens)
and not decoded. Unknowns:

| Unknown | What would settle it |
|---|---|
| Whether the second corner of slot 304 is inclusive | the RE3 writes caused by a one-rectangle draw, or the arithmetic of the GE7 routine at 33026 once the RE3 parameter format is known ([arithmetic.md](arithmetic.md)) |
| What the `0x1000` flag in the pixel-mode word does | the HQ2 code of slot 331 (`op40 5006`) once the HQ2 instruction set is decoded, or a run that draws with and without it |
| The 8-bit and 12-bit pixel-mode code values for window codes other than `0xc` to `0xe` | the code that fills the window record's `0x14` word (`expValidateVisual` branches, not fully read) |
| Roles of the clipped, wide and stippled line forms and of slot 355's operands | read `expLineSD`, `expFastLineSD` and `expSegmentSS` to their last store |
