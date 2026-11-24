# GR2 microcode: image formats and first decode

What `hq2.bin`, `ge7.bin` and the two console images embedded in the 4.0.5D Indigo PROM contain, how far their instruction words have
been decoded, and what each console token's routine does. The loader view of the images (registers, masks, load order) is in
[devices/ge7](../../devices/ge7/README.md) and [devices/hq2](../../devices/hq2/README.md); the token numbering and the GL token
catalogue are in [pipeline.md](pipeline.md). Tool: [tools/ucode-decode.py](../../tools/ucode-decode.py) (`uv run --script`; it checks
the images and prints statistics and per-slot walks, never a listing).

Facts are `[binary]` unless tagged: the shipped images (`usr/gfx/ucode/hq2.bin`, `ge7.bin`, hashes in [references/binaries.md](../../references/binaries.md)),
the 4.0.5D PROM `070-8116-004` (HQ2 image at file offset `0x49840` = `0xbfc49840`, GE7 image at `0x4a6f4`) and the diagnostic program
`ide.IP20`. The field names and widths of the GE7 microword also rest on the GR4 board schematic, tagged `[vendor-derived]` (see
[the schematic sheets](#the-schematic-sheets)); no upstream header was read. Grades as in [AGENTS.md](../../AGENTS.md): **established** is read in the images as stated, **inferred** is a reading checked
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

## The diagnostic program's own images

`ide.IP20` (Diagnostics 5.2, SHA-256 `744fdebc...df14`) carries four microcode images in its data section, found by their magic
(`ucode-decode.py ide`): a **diagnostic GE7 image** of 2203 records (addresses 0 to 2202, build text of August 1992), its HQ2 image
(977 records, addresses 512 to 1456, one record out of order at 69), and a pair of console images of February 1993 (GE7 308 records,
HQ2 150) that match the PROM's token set. `gr2_ucload` selects between them by argument. [binary] The diagnostic images are the
useful ones: each test sends a few words, the microcode computes, and the program compares the result with a value it computes
itself, so the operation of the microcode words is known from the test. All four use the same record format and checksum.

### Known-answer tests

| Test (`ide.IP20`) | What the host sends and expects | Use |
|---|---|---|
| `gr2_FloatOpsTest` (`0x8852e398`) | Three words to HQ2 slot 59 (`+0x400ec`): operand x, operand y, operation 1 to 6. Each engine writes one result word to shared RAM word 255 plus its index. Checked: 1 IADD, 2 ISUB, 3 IMPY (low 24 bits only), 4 FADD, 5 FSUB, 6 FMPY. Inputs: seven positive and seven negative integers (8 to `0xea6a082`), ten floats from 0.512 to 2.46e8 and their negatives; the float result is accepted when the raw bit patterns differ by less than 2. | The six case arms of the GE7 routine reached from HQ2 slot 59: the words that differ between arms name the ALU and multiplier fields below. |
| `gr2_FpuCondTest` (`0x8852dde4`) | One word to slot 57. Each engine returns a count at shared word 255 and then failure records at 256 on: (condition number << 8) \| function number. The program prints names for both. | The 46 ALU function names and numbers (the table in the field map). Condition names are not recovered (the name table is part integer data; unread). |
| `gr2_SpfCondTest` (slot 58) | Same shape for the second condition set. | Not read further. |
| `gr2_GeSeqTest` (`0x8852dc50`) | One word to slot 12. Per engine, nine words of RAM0 must not be `0xffffffff` and the shared word at engine slot offset 0 must be 1. | A straight-line microprogram that reads RAM0 at addresses 0 to 10 and 0x7f, then runs ALU operations followed by conditional branches over a failure path (a stall word and a jump to 0). |
| `gr2_GeFifoTest` (`0x8852d878`) | Five words to slot 8 (into engine input slots 1, 2, 5, 6 and 7): x = 100, y = 100/150/200/250 and a colour as three words (red 255,0,0; green; blue; yellow 255,255,0). The program then reads the pixels back with a DMA from the frame buffer and expects ten pixels equal to `r \| g<<8 \| b<<16` under the plane mask of the installed boards. | The only known-answer test of the raster-engine output: the 16-word routine at GE7 989 must produce a ten-pixel span at (100, y) of that colour, so its output writes are RE3 commands for a span. |
| `gr2_ShramTest`, `Ram12Test`, `SeedRomTest`, `SqRomTest`, `GeBusTest` | One word each to slots 3, 2, 4, 5 and 7; per-engine result words, with messages that name RAM1, RAM2, the register file, the reciprocal seed ROM, the square-root ROM and the ring bus. | Names the units the microword's RAM1, RAM2 and register fields address; the routines themselves are unread. |

Established [binary] for what the host sends and compares (the whole test routines were read for FloatOps, GeSeq and GeFifo). The
microcode side below is inferred from them.

## The GE7 microword

128 bits, loaded as five words. Numbering: C0 to C4 are the five 32-bit words of a record in file order (they go to `+0x6a064`,
`+0x683ec`, `+0x683e8`, `+0x683e4`, `+0x683e0`), and microword bit 0 is C4[0], bit 31 C4[31], bit 63 C3[31], bit 95 C2[31],
bits 102:96 C1[6:0] (7 stored bits) and bits 127:103 the 25 stored bits of C0 (the read-back mask `0x03dfffff` leaves out bit 21).
Bits seen set in `ge7.bin`: C0 `0x03ffffff`, C1 `0x3f`, C2 `0xffffefff`, C3 `0xfffffbef`, C4 all.

### The field map

The map below comes from two independent sources that agree wherever both speak.

1. **The test known answers and the images' statistics** [binary]: the function numbers in the diagnostic program's name table, the six
   case arms of the FloatOps routine, the slot numbers HQ2 stores, the nine console routines, and field statistics over `ge7.bin`.
2. **The GR4 board schematic**, sheet "2GE7 ASIC (cavity up)" (10 of 21), whose symbol lists the microword inputs by name, each with
   a microword bit number (0 to 102), and sheet 9 "GE7 Ucode & Shared RAM" (eight 64K x 16 RAMs on a 128-bit `GEMIC` bus, four 32K x 8
   RAMs for the shared 128 KiB). **[vendor-derived]**: the PDF in `docs/` is an OCR'd scan with no stated origin; a fact that rests only
   on it stays inferred, and published QEMU pages must not cite it. The names and widths are taken from it; every field's position was
   then checked against source 1 as noted.

| Bits (C-word) | Field | Width | Meaning (from the name) | Evidence |
|---|---|---|---|---|
| 0-3 (C4[3:0]) | REGA | 4 | register file select | schematic; GeSeqTest words carry REGC = 1 beside the ALU ops |
| 4-7, 8-11, 12-15, 16-19 | REGB, REGC, REGD, REGE | 4 each | register file selects | schematic |
| 20-23 (C4[23:20]) | REGWR | 4 | register file write select | schematic; counts 1 to 13 through the GeSeq/FpuCond routines |
| 24-30 (C4[30:24]) | RAM0AD | 7 | RAM0 address: the input slot | **binary**: all slot numbers HQ2 stores (0 to 24) and the routine slots match; max value 127; GeSeqTest reads 0 to 10 and 0x7f and reports "Ram0_addr" |
| 31-36 | RAM1AD | 6 | RAM1 address | schematic (C4[31] is set in 3% of words) |
| 37-42 | RAM2AD | 6 | RAM2 address | schematic |
| 43-44 (C3[12:11]) | FMPYOP | 2 | multiplier operation | **binary**: 0 = IMPY, 1 = FMPY in the two multiply arms (value 2 in all add arms and the idle word) |
| 45-50 (C3[18:13]) | FALUOP | 6 | ALU function | **binary**: IADD 0x28, ISUB 0x29, FADD 3, FSUB 8 in the four arms; FPASSA (4, the idle value) is 45% of `ge7.bin` words; the 46 names are below |
| 51-58 (C3[26:19]) | BRCOND | 8 | branch condition select | schematic; nonzero almost only on conditional branches with C0 condition 3, 4, 7, 8 |
| 59-61, 62-64 | MPYA, MPYB | 3 each | multiplier operand selects | schematic; MPYB = 1 in both multiply arms |
| 65-67, 68-70 (C2[3:1], C2[6:4]) | ALUA, ALUB | 3 each | ALU operand selects | schematic; idle 4/4, the add and subtract arms 0/1, multiply arms 4/4 |
| 71 (C2[7]) | BUSEL | 1 | result bus source | schematic; set in both multiply arms only |
| 72, 73 (C2[8], C2[9]) | REGSEL, RESEN | 1 each | register select, result enable | schematic; RESEN set in all six arms |
| 74-82 | RAM0DEST, RAM1DEST, RAM2DEST | 3 each | RAM write destinations | schematic |
| 83-87 | MISCSRC (1), SHFTSRC (2), REGFDEST (2) | | source and destination selects | schematic |
| 88-89 (C2[25:24]) | DSEL | 2 | data select | schematic; value 2 in all six arms |
| 90-93 | QSAM, TSAM, VPSAM, LSAM | 1 each | sample strobes (names only) | schematic |
| 94 (C2[30]) | FIFOEN | 1 | output FIFO enable | **binary**: set only in routines that draw (see the RE3 section) |
| 95-102 (C2[31], C1[6:0]) | READDR | 8 | raster-engine register address | schematic; see the RE3 section |
| 103-127 (C0) | sequencer | 25 | target, control, condition | below |

The earlier readings are folded in: the "input slot" is RAM0AD, and the "C1 register select qualified by C2[31:30]" is READDR with
FIFOEN. The default pair (C3[15:8] = 0x90, C2[7:0] = 0x48) is "FALUOP = FPASSA, FMPYOP = 2, ALUA = ALUB = 4": the engine passes a
value and does nothing else.

**ALU function numbers** [binary] (the diagnostic program's FpuCondTest name table): 3 FADD, 4 FPASSA, 5 FNEGA, 6 FPASSB, 7 FNEGB, 8 FSUB,
9 FRSUB, 10 FMIN, 11 FMAX, 12 FLOATA, 13 FLOATB, 14 FIXA, 15 FIXB, 16 IMPY, 17 FMPY, 18 MPASSA, 19 MPASSB, 20 FABSA, 22 FABSB,
30 FMINABS, 31 FMAXABS, 32 NOTA, 33 AND, 34 OR, 35 XOR, 36 ANDNOTB, 37 ANDNOTA, 38 ORNOTB, 39 ORNOTA, 40 IADD, 41 ISUB, 42 IRSUB,
44 SLRREG, 45 SARREG, 46 SLLREG, 48 IMIN, 49 IMINABS, 50 IMAX, 51 IMAXABS, 52 IPASSA, 53 INEGA, 54 IABSA, 55 IPASSB, 56 INEGB,
57 IABSB. Numbers 60 to 62 occur on 1 to 2% of words and have no name (probably no-operation codes). The FALUOP and FMPYOP positions
are **inferred** with strong support (the four ALU arms and the two multiply arms of one test all fit, every one of the 20 commonest
values but 60 to 62 is a named function, and the positions agree with the schematic's independent numbering); what ALUA/ALUB values 0 and 1
select (probably the two registers or buses the operands arrive on), and the REG fields' exact roles, are unknown.

### Sequencer: C0

- **C0 holds the sequencer fields**: a 16-bit target in C0[15:0], a control value in C0[21:16] and a 4-bit condition in C0[25:22] (the
  grading and statistics of the first decode stand: for every word whose condition is 1 to 8 and whose control is `0x16`, `0x17`,
  `0x36` or `0x37`, the target lands on an existing record, 3194 of 3194). **C0[21] is the bit the read-back mask drops**, so the
  loader cannot read it back; whether the microstore keeps it is unknown (the images use it in 88% of words). The sequencer is
  inside the HQ2, not the GE7: the schematic's GE7 symbol takes no target or control inputs.
- **Idle.** Addresses 0 and 1 are a pair: a word with condition 10 and no target, then a word with control `0x31` and target 0. The
  case arms of the FloatOps routine all end by reaching that pair (arms with condition 5 jump to a common tail that ends in it), and
  the GeSeqTest failure path is the same two words. Inferred: condition 10 stalls until the HQ2 starts the next routine; the jump
  to 0 repeats the stall.
- **Branch conditions are partly outside C0.** BRCOND (C3[26:19]) is the GE7 condition select: of the words with C0 condition 3, 4,
  7 or 8 (about 2500 of 23429) most carry a nonzero BRCOND (values 96 to 107 and 135 to 153 dominate), while conditions 1, 2, 5, 6, 9 and 10
  carry BRCOND = 0 in 80 to 98% of words. So some conditions test GE7 results chosen by BRCOND and others test something outside the
  GE7 (inferred). The control values `0x31` and `0x37` with condition 0 also carry BRCOND values of 224 to 235 on a minority of words, a second
  family of tests (unknown).
- **Still unresolved: the jump chains.** In the PROM image the chain 65, 125, 126, 127, 65 has condition 0, control `0x3f`
  or `0x36` and BRCOND 0 on every word, so it loops if every `0x3f` is a taken jump. The FloatOps routine has the same shape: its
  second word (control `0x31`, target 0) must fall through for the case arms after it to run at all, so a `0x31` word is not an
  unconditional jump to its target. No test known answer pins down the polarity of the conditions or what a `0x3f` or `0x31` word does
  when its target is not wanted. Next: simulate GeSeqTest's straight-line program against its stated outcome (the nine RAM0 words and
  the shared flag).

### The RE3 output path

- **FIFOEN and READDR are the raster-engine write.** The GE7 symbol has 32 `RE` data pins and `REWR`, `RERD`, `REEN` strobes (schematic),
  and the microword supplies an 8-bit address (READDR) and an enable (FIFOEN). Binary support: of the nine console routines only the
  drawing ones carry FIFOEN. COLOR and CMOV2I, which draw nothing, have none; PNT2I (a point), RECTI2D and LINE2I do, and
  PNT2I and RECTI2D end with the same two writes (READDR `0x5f`, then `0x40`) in the condition-10 and jump-to-0 pair. FIFOEN is
  set on 124 of 301 words of the PROM image and 2414 of 23429 of `ge7.bin`. The GeFifoTest span (above) comes from the same kind of words.
  Inferred.
- **READDR values** (READDR = C1 * 2 + C2[31], on the words that carry FIFOEN, in address order within each PROM-image routine;
  execution order and the shared tail at 124 to 127, which adds `0x67`, `0x20` and `0x6f`, are not followed): PNT2I `0x08`, `0x20`, `0x22`,
  `0x21`, `0x5f`, `0x40`; RECTI2D `0x08`, `0x20`, `0x21`, `0x25`, `0x24`, `0x23`, `0x5f`, `0x40`; LINE2I `0x20`, `0x21`, `0x22`, `0x08`, `0x5f`
  and others; RECTCOPY the RECTI2D set plus `0x67`. **INIT** (the routine at GE7 10 to 50) writes about 36 addresses in `0x46` to `0x7e`:
  it initialises a block of raster-engine state. The address range is 0 to 255 words, which is exactly the RE3 window `+0x6c200` to
  `+0x6c5ff` ([devices/re3](../../devices/re3/README.md): a 27-bit bank at `+0x6c200`, a 24-bit bank from `+0x6c280`, which is word `0x20`,
  a 32-bit bank at `+0x6c600`), so READDR is most likely the word index within that window. Which register is x, y, colour or a mode, what
  the closing `0x5f` and `0x40` writes mean, and which source supplies each write's data (DSEL, REGFDEST and the other source fields are
  not decoded) are **unknown**. A model cannot yet produce RE3 command words from the microcode; the console tokens can be modelled
  directly (last section).
- **Next route.** Find the data that reaches the RE pins: follow the register written just before each FIFOEN word in PNT2I from the
  word that reads the operand (RAM0AD = 0 or 1) through REGWR and RAMnDEST, using the diagnostic RAM tests as known answers for
  those destination fields.

### Other observations

- The nine console routines' slot sets, the DRAWCHAR loop and the pre-call described below stand with RAM0AD for the input slot.
- C4's lower three bytes are REGA to REGE and REGWR; "four-bit-aligned" in the first decode was that.

## HQ2 words beyond the console set

New observations from the diagnostic HQ2 image and `hq2.bin` (inferred, from word sequences only):

- **`0x80` control writes are bit masks, and the next branch tests them.** A type-6 or type-7 branch follows a `0x80` word whose
  operand is `0x0060` (the commonest, 36 words), `0x0070`, `0x0064`, `0x0020` or `0x0040`; in the diagnostic image a token polls
  this way before starting the engine (a read, `0x80 0x0060`, a type-7 branch back to the read, then `0x80 0x1000`, then the start).
  So `0x80` selects status bits (and may set flags) and the type-6 and type-7 branches repeat or skip on them. Which bit is which is unknown.
- **The word before a start** is `0x0040` in 105, `0x0020` in 54 and `0x1000` in 34 of about 380 `hq2.bin` starts, and the word after is
  `0x0611` (108), `0x0020` (49), `0x0641` (38), `0x0601` (34) or `0x0060`. In the diagnostic image the pre-start word is `0x0020` for
  24 of 42 starts, and the tokens that read operands (slots 7, 59) use `0x0800`.
- **The diagnostic HQ2 image uses an older word form for the data reads**: the flag form is `0x60`/`0x40` with `0x4000 + 32 * n`
  (slot n of the GE7 input RAM, bit 14 set) instead of `32 * n`, and `0x40 0x0fe4` style words in its reset-wait loop. The two forms are
  the same instruction with an extra target-select bit. Inferred.
- **Not decoded**: the `0x20` operands other than `0x2000` (27 words), the other flag forms of `0x40`/`0x60` and the ops `0x01` to
  `0x06`, `0x10`, `0x22`, `0x81`, `0x90` to `0xd0`. No test known answer reaches them (the diagnostic image uses 20 op values).

## The schematic sheets

The upstream tree carries the GR4 board schematic ("Indy Elan Graphics - GR4 board, fab 034-8234-002", 21 sheets). It is an OCR'd
scan (the PDF producer string is a 2018 paper-capture plug-in); how it came to be published is not stated anywhere in the tree, so it
is **[vendor-derived]** here. The two sheets that matter:

- Sheet 9, "GE7 Ucode & Shared RAM": eight 64K x 16 dynamic RAMs on a 128-bit bus named `GEMIC<127..0>`, one 64K-deep microstore
  shared by all engines (matches the loader's 128-bit, 65536-word store), and four 32K x 8 static RAMs, 128 KiB, for the shared data RAM
  (matches `+0x0` to `+0x1ffff`).
- Sheet 10, "2GE7 ASIC (cavity up)": the field names and microword bit numbers in the map above, 32 `RE` data pins, `REWR/RERD/REEN`,
  `GEIN/GEOUT` ring-bus pins, `FLAGO`/`FLAGPIN` flag lines and `LASTGE`/`SWAPMESH` (names only). Sheet 11 (cavity down) is the other
  package of the pair and was not read. Sheet 12 (RE3 ASIC) was not read; it is the next route for the RE3 register addresses.

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
- A model that runs `hq2.bin` and `ge7.bin` for GL needs the full HQ2 op set (the `0x80` bits and about 10 unknown op values), the
  rest of the GE7 data path (register file, RAM1/RAM2, the source and destination selects, the condition semantics) and the
  RE3 command data. The ALU and multiplier operations, the input RAM address and the raster-engine write strobe and register address
  are now located (graded inferred); with them a first GE7 data-path interpreter can run the FloatOps arms, but not yet control flow.
