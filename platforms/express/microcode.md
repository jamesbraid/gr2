# GR2 microcode: image formats and first decode

What `hq2.bin`, `ge7.bin` and the two console images embedded in the 4.0.5D Indigo PROM contain, how far their instruction words have
been decoded, and what each console token's routine does. The loader view of the images (registers, masks, load order) is in
[devices/ge7](../../devices/ge7/README.md) and [devices/hq2](../../devices/hq2/README.md); the token numbering and the GL token
catalogue are in [pipeline.md](pipeline.md). Tool: [tools/ucode-decode.py](../../tools/ucode-decode.py) (`uv run --script`; it checks
the images and prints statistics and per-slot walks, never a listing).

All facts are `[binary]`: the shipped images (`usr/gfx/ucode/hq2.bin`, `ge7.bin`, hashes in [references/binaries.md](../../references/binaries.md))
and the 4.0.5D PROM `070-8116-004` (HQ2 image at file offset `0x49840` = `0xbfc49840`, GE7 image at `0x4a6f4`). No upstream header was
read. Grades as in [AGENTS.md](../../AGENTS.md): **established** is read in the images as stated, **inferred** is a reading checked
against known behaviour, **unknown** is not decoded. No microcode bytes or listings are committed here; values quoted are field values.

## Image format additions

The header and record layout are in [devices/ge7](../../devices/ge7/README.md#microcode-image-format). Two things that page lists as
unread are settled by this decode.

- **The trailing half-word of each record is a checksum.** It equals the sum, modulo 65536, of the record's address, its second
  half-word (always 1) and every byte of its data words. Established: it holds for all 149 + 301 records of the two PROM images, 5642
  records of `hq2.bin` and 23429 of `ge7.bin`, with no exception (`ucode-decode.py info`). The loaders never read it; it is a build-time
  check. This answers [questions/ge7.md](../../questions/ge7.md) item 3 for that half-word (the header words are still open).
- **Sizes.** PROM HQ2 image: 149 records, addresses 0 to 648, record length 10 (one 32-bit word), 3752 bytes. PROM GE7 image: 301
  records, addresses 0 to 308, record length 26 (five words), 10104 bytes. `hq2.bin`: 5642 records, addresses 0 to 5910.
  `ge7.bin`: 23429 records, addresses 0 to 36194. All four are in ascending address order with gaps.

## The HQ2 instruction word

One 32-bit word per microstore address, written to `+0x60000 + 4 * address`. All used words have bits 31:24 clear, so the word is a
**24-bit op field (bits 23:16) and a 16-bit operand (bits 15:0)** (inferred from the value statistics: 21 op values occur in
`hq2.bin`, the six commonest cover 92% of words). The FIFO token address selects a word at address 0 to 511 by bits 10:2; of the 426
populated ones, 324 are plain jumps and the rest hold an op directly (a read or a start), 86 are empty.

| Op (23:16) | Operand | Reading | Grade |
|---|---|---|---|
| `0x00` | bits 15:13 = 3: jump to bits 12:0; 4: call (subroutine) to bits 12:0; 5: return (the operand is always `0xa000`); 6 and 7: other branches, 12:0 is a target | Branch family. All 372 jumps, all 245 type-4 and all type-5/6/7 targets in `hq2.bin` land on an existing word (and 12 of 12 in the PROM image); that is the evidence for the 13-bit target and for which words are branches. Which condition a type-6 or type-7 branch tests is unknown; the call and return meanings are inferred from a call whose callee ends in the return word and whose caller continues at the next word. | jump established; the rest inferred |
| `0x60` | slot number in bits 9:5 when bits 4:0 are 0 and the value is below `0x400` (788 words); 674 more carry other flag forms such as `0x2600` | Take the next FIFO data word and store it as input slot *n* of the geometry engine. | inferred, see the walk-through |
| `0x40` | same (146 words) | Same, and the last operand read of the token. 921 `0x40` words carry other operands (`0x1101`, `0x3661`, `0xa660` and so on) that are not slot numbers; `0x3661` alone appears 206 times. | inferred; the other forms unknown |
| `0xd8` | GE7 microstore address | Start a GE7 routine at that address. All 380 operands in `hq2.bin` and all 12 in the PROM image are addresses of a record in the matching GE7 image; 88 of 380 end in `0x02`, the page-start-plus-two of the GE7 code pages. | established that it is a GE7 address; role inferred |
| `0x80` | small bit masks (`0x0020`, `0x0040`, `0x0611`, `0x0601`, `0x0641`, `0x1000`, ...) | Control write; the value after a start is `0x0611` in 108 of 380 cases. Nothing says which register or what it waits for. | unknown |
| `0x20` | `0x2000` in 391 words | The word that ends a routine; the next FIFO token's slot word is fetched after it. Eighteen other operands (`0x4f9b`, `0x512c` and similar) occur on 27 words: unknown. | inferred for `0x2000` |
| others (`0x01` to `0x06`, `0x10`, `0x22`, `0x81`, `0x90` to `0xd0`) | | Present in `hq2.bin` only (about 400 words); not decoded. | unknown |

Cross-checks run: (1) the HQ2 words of the console tokens are the same in the PROM image and in `hq2.bin` apart from the GE7 address
and the word numbers (the full image's INIT additionally reads one operand into slot 0); (2) the number of operand reads of each token
equals the number of words its PROM caller writes (below); (3) every branch target lands on a word.

## The GE7 microword

128 bits, loaded as five words. Numbering used here: C0 to C4 are the five 32-bit words of a record in file order (they go to
`+0x6a064`, `+0x683ec`, `+0x683e8`, `+0x683e4`, `+0x683e0`), and the microword is bit 127 down to bit 0 as C0, C1, C2, C3, C4 with C0 holding
bits 127:102 (26 bits), C1 bits 101:96 (6 bits), C2 bits 95:64, C3 bits 63:32, C4 bits 31:0. This is an assumption about concatenation
order (the register names are "lowest column" for `+0x683e0`); it does not matter for field boundaries inside one word. Bits seen set
in `ge7.bin`: C0 `0x03ffffff` (bit 21 of C0 is not kept by the read-back mask `0x03dfffff` but is used), C1 `0x3f`, C2 `0xffffefff`,
C3 `0xfffffbef`, C4 all. So 125 of the 128 bits are used.

### Sequencer: C0

- **C0[15:0] is a 16-bit microstore address.** For every word whose C0[25:22] is 1 to 8 and whose C0 low six bits of the control
  field are `0x16`, `0x17`, `0x36` or `0x37`, the address lands on an existing record: 3183 of 3183 words (3194 of 3194 counting all
  such words). For the words with C0[25:22] zero and a control value of `0x31` to `0x35`, `0x3f` or `0x11` to `0x13`, the address lands
  on a record in 5317 of 5909 cases; nearly all misses are addresses just above the first loaded run (addresses 215 to 255 in the part
  that is not stored) or the unstored first two words of the next page (256, 257, 768): inferred as jumps into code the image does
  not carry (page-start words, or a fixed store; unknown). In the PROM image the targets that many routines share (`0x40`, `0x7c`,
  `0x98`) are common tails.
- **C0[21:16] (6 bits) and C0[25:22] (4 bits) are the sequencer opcode and a condition field** (inferred). Words with C0[25:22] = 0 and
  C0[21:16] = `0x36` are plain (7861 words) and `0x37` plain (2966); `0x31` to `0x35` and `0x3f` carry a target (6000 words) and are
  jumps; `0x36`/`0x37`/`0x16`/`0x17` with a condition value 1 to 8 carry a target and are conditional branches (about 3200 words, 82%
  forward); condition values 9 to 11 with `0x36`/`0x37` carry no target. Bit 0 of the control value (`0x36` against `0x37`) is
  orthogonal to the jump/plain split and its meaning is unknown.
- **The routine epilogue and idle loop.** Addresses 0 and 1 in both GE7 images are a pair (a word with condition value 10 and no
  target, then a word with control `0x31` and target 0): a two-word idle loop the engine returns to. Routines end in a shared
  tail that jumps to address `0x40` (the PROM image) and the tail ends in the same pair. Inferred from structure; nothing was run.
- **Not resolved.** In the PROM image several jump chains return to themselves with no exit visible in the sequencer field (for example
  address 65 to 125 to 127 and back). Either such a jump is conditional on something outside C0 (a wait on the FIFO, on the raster
  engine or on a flag) or the control values `0x31`/`0x3f` are not plain jumps. The count of 5279 jump words with C1 = 0 against 630
  with C1 nonzero shows C1 is not the condition. Unknown.

### Input slot: C4[31:24]

**C4[31:24] is the input slot number the word reads** (inferred, strong). The HQ2 reads each console token's operands into slot numbers
(next section). Taking each PROM-image routine's own address range up to the next routine start, the nonzero values of C4[31:24] in
its words are exactly the slots its token's operands go to:

| Routine (start address) | Slots HQ2 stores | Values of C4[31:24] in the routine's words |
|---|---|---|
| COLOR (51) | 0 | 0 |
| PNT2I (58) | 0, 1 | 0, 1 |
| RECTI2D (69), LINE2I (89) | 0 to 3 | 0 to 3 |
| CMOV2I (107) | 0, 1 | 0, 1 |
| DRAWCHAR (115) | 0 to 24 (rows in 24 down to 7) | 0, 1, 3 to 24 (slot 2 unused) |
| RECTCOPY (201) | 14, 13, 0 to 5 | 0 to 5, 13, 14 |
| routine at 245 (HQ2 slot 417) | 8, 1 to 4 | 0 to 4, 8 |

Within DRAWCHAR the 18 row slots 7 to 24 appear as 18 consecutive values in C4[31:24] on every other word of one run (addresses 142 to
176), each followed by a conditional branch whose target steps by one: the loop that tests the 18 row words of a glyph strip.
The lower three bytes of C4 hold four-bit-aligned fields (bits 19:16 are almost never set, the others are 4 to 8%): purpose unknown.

### Other fields (hypotheses, weak)

- **C1[5:0] with C2[31:30].** C2[31:30] is nonzero exactly when C1 is nonzero, except for 138 words of 21153 with C1 = 0 (the
  value pair 1 and 3 in C2[31:30], in the PROM image alternating in adjacent words). C1 is a 6-bit register or constant select and
  C2[31:30] qualifies it. Inferred; the most common nonzero C1 values are `0x2f` (817 words) and `0x10` (235).
- **C2[25] tracks C0[21].** C2[25] is set in 88% of words, in exactly the words whose C0 control value has bit 5 set (the `0x3x` family),
  and clear for `0x17`, `0x16`, `0x11`, `0x01`. Reading: two instruction forms. Unknown what the second form does; it carries the
  other 12% of words (about 2700, including 1370 of control `0x17`).
- **Default values.** C3[15:8] is `0x90` in 12405 of 23429 words and C2[7:0] is `0x48` in 8271, the same words that do nothing but
  sequence (the four do-nothing words at the start of COLOR carry exactly these): presumably the idle value of those fields. C2[7:0] and C3[15:8] are small enumerations (135 and 59 values). Unknown.

### The RE3 output path

**Not found.** A word that writes the raster engine is not identified: the sequencer, input-slot and select fields account for
about 43 of the 128 bits and the remaining bits (the C2 low half, all of C3, the lower three bytes of C4) have no decoded
meaning. Routes tried: the structure above; comparison of PNT2I, RECTI2D and DRAWCHAR against CMOV2I (which draws nothing) for bit
patterns that only drawing routines carry. Next: question 1 in [questions/microcode.md](../../questions/microcode.md).

## The console tokens

The HQ2 side below is read directly from the PROM image and checked against `hq2.bin`; the GE7 side is a structural reading only.
"Slots" are the GE7 input slot numbers HQ2 stores operand words into. Established for the word counts and slot numbers; the role of
a slot (x, y and so on) comes from the PROM caller and is inferred for the GE7 side.

| Slot (token) | HQ2 sequence | PROM caller sends | GE7 routine (PROM image) |
|---|---|---|---|
| 401 INIT | control writes (`0x001f`, `0x0800`), one flag-form read, start GE7 at 10. The full image first reads one operand into slot 0. | one word, 0 in 4.0.5D | 10, which jumps to 160, inside the slot-7-to-24 test run described above; the words 11 to 50 that follow it hold no slot numbers (C4[31:24] = 0) and are reached by other paths. Purpose of the routine unknown: the PROM only ever sends the one zero word. |
| 402 COLOR | one read-last into slot 0, one control write (`0x0020`), start GE7 at 51 | the colour value | 51 to 57. Four do-nothing words, then a jump to a shared routine that walks the slot-9-to-24 block and returns to idle. Inferred: it stores the colour where the later primitives find it. |
| 404 PNT2I | reads slots 0 (x) and 1 (y), the control write, start at 58 | x token, y data | 58 to 68. Jumps to the shared tail (address 124 to 127, then 64 to 68). Slot 1 is read at address 63. Inferred: plots one pixel at (x, y) by handing it to the raster engine through that tail. |
| 405 RECTI2D | reads slots 0 to 3, the control write, start at 69 | x1, y1, x2, y2 | 69 to 88. A start word that jumps to the shared tail at 64, then a 19-word body that reads slots 2, 1 and 3 and ends at idle. Inferred: it draws the filled box. |
| 406 CMOV2I | reads slots 0 and 1, control write, start at 107 | x, y | 107 to 114. Four do-nothing words, a jump to the shared tail. Reads slot 1 at 112. Inferred: stores the current position; slot 0 and 1 are consumed into engine state, which is why no draw follows. |
| 407 LINE2I | reads slots 0 to 3, control write, start at 89 | x1, y1, x2, y2 (not sent by the PROM) | 89 to 106. Reads slots 0 to 3; ends at idle. Inferred: draws a line. |
| 408 DRAWCHAR | seven reads into slots 0 to 6, then 17 reads into slots 24 down to 8, then a read-last into slot 7; control write; start at 115 | width token, six parameters and 18 row words (25 words, matches the PROM caller) | 115 to 200. A chain of conditional jumps (115 to 117) selects the glyph width case, then a loop over the 18 row slots testing them in turn (142 to 176) and a block of 16 words storing per-row values (180 to 195). Inferred. |
| 409 RECTCOPY | call to a subroutine (the one at 600) first, reads into slot 14, then 13, then slots 0 to 5 (the last one read-last); start at 201 | `(width+3)>>2`, the 4864/n line count, six more words (8 words, matches the PROM caller) | 201 to 244. A jump to 233 then 152, which runs the slot-9-to-24 block like INIT; reads slots 0 to 5, 13 and 14. Inferred: it moves rectangle words through the register block, then the raster engine. |
| 417, 418, 419 (no PROM caller) | 417: the pre-call, then 5 reads (slots 8, 1 to 4); 418: 1 read into slot 0; 419: a flag-form read and a branch that loops to itself | not sent | 245 to 286, 287 to 295 and 302 to 308 (296 to 301 is the pre-call's target). Unknown purpose; the full `hq2.bin` has no words at these slots. |

One shared structure is the **pre-call**: slots 417 and 409 both begin with a call to HQ2 address 600, a 21-word subroutine that
starts a GE7 routine at 296 (a one-word jump to the epilogue) and returns. Reading: a "wait until the engine is idle" step before the
operands are taken. Inferred from the word shape only.

## What a QEMU model needs from this, and what it does not yet get

- A model that accepts the console tokens and draws their effect directly (the plan in [pipeline.md](pipeline.md)) needs none of this
  beyond the slot counts above: nine tokens, operand counts and their order. These are established.
- A model that runs `hq2.bin` and `ge7.bin` for GL needs the full HQ2 op set (about 10 unknown op values and the 0x80 control
  register bits), the GE7 data-path fields and the RE3 output path. None of that is decoded. A first HQ2 interpreter is within reach
  (the FIFO read, jump, call, return and start ops are known); the GE7 is not.
