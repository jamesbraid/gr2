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
HQ2 150) that match the PROM's token set but are a different build: its routine start addresses are those of the PROM image plus 7 (COLOR 58, PNT2I 65, RECTI2D 76 against 51, 58, 69), so the PROM image, not this one, is the one the console-token statements below read. `gr2_ucload` selects between them by argument. [binary] The diagnostic images are the
useful ones: each test sends a few words, the microcode computes, and the program compares the result with a value it computes
itself, so the operation of the microcode words is known from the test. All four use the same record format and checksum.

### Known-answer tests

| Test (`ide.IP20`) | What the host sends and expects | Use |
|---|---|---|
| `gr2_FloatOpsTest` (`0x8852e398`) | Three words to HQ2 slot 59 (`+0x400ec`): operand x, operand y, operation 1 to 6. Each engine writes one result word to shared RAM word 255 plus its index. Checked: 1 IADD, 2 ISUB, 3 IMPY (low 24 bits only), 4 FADD, 5 FSUB, 6 FMPY. Inputs: seven positive and seven negative integers (8 to `0xea6a082`), ten floats from 0.512 to 2.46e8 and their negatives; the float result is accepted when the raw bit patterns differ by less than 2. | The six case arms of the GE7 routine reached from HQ2 slot 59: the words that differ between arms name the ALU and multiplier fields below. |
| `gr2_FpuCondTest` (`0x8852dde4`) | One word to slot 57. Each engine returns a count at shared word 255 and then failure records at 256 on: (condition number << 8) \| function number. The program prints "GE7[n], Fpu Cond: FUNCTION did not set FLAG flag". | The 49 ALU function names and numbers (the table in the field map). The flag names are zero (1), neg (2) and pass (4). |
| `gr2_SpfCondTest` (slot 58) | Same shape for the second condition set: it compares 8, 36, 4 and 2 result words against tables in the program and reports "SPF cond. QSAM / TSAM / VPSAM1 / VPSAM2 failed on N value". | Names the four sample strobes (the QSAM, TSAM, VPSAM and LSAM fields). Table contents not read. |
| `gr2_GeSeqTest` (`0x8852dc50`) | One word to slot 12. Per engine, nine words of its RAM0 window must not be `0xffffffff` and shared word 255 + engine must be 1. | GE7 1354 to 1455: writes RAM0 addresses 0 to 10 and `0x7f`, then runs integer ALU operations each followed by a conditional branch over a failure word (a stall with a RAM0 write). Decoded in [the GeSeqTest section](#geseqtest-as-a-known-answer). |
| `gr2_GeFifoTest` (`0x8852d878`) | Five words to slot 8 (into engine input slots 1, 2, 5, 6 and 7): x = 100, y = 100/150/200/250 and a colour as three words (red 255,0,0; green; blue; yellow 255,255,0). The program then reads the pixels back with a DMA from the frame buffer and expects ten pixels equal to `r \| g<<8 \| b<<16` under the plane mask of the installed boards. | The only known-answer test of the raster-engine output: the 16-word routine at GE7 989 must produce a ten-pixel span at (100, y) of that colour, so its output writes are RE3 commands for a span. |
| `gr2_ShramTest`, `Ram12Test`, `SeedRomTest`, `SqRomTest`, `GeBusTest` | One word each to slots 3, 2, 4, 5 and 7. ShramTest: shared word 255 + n must equal n. Ram12Test: six words per engine at shared 255 + 6n on, each non-zero (two for RAM1, two for RAM2, two for the register file). The others compare an expected value with an actual one. | Names the units the microword's RAM1, RAM2 and register fields address. ShramTest is decoded (conditions 14 and 15, below). Ram12 (GE7 395 on) writes RAM1 addresses 0 to 31 (RAM1DEST = 3), then reads each back as ISUB with ALUB = 1 and ORs the differences with ALUA = 7, ALUB = 6, which suggests ALUB = 1 selects the RAM1 output; inferred. The SeedRom, SqRom and GeBus routines are unread. |

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
| 65-67, 68-70 (C2[3:1], C2[6:4]) | ALUA, ALUB | 3 each | ALU operand selects | **binary**: ALUA = 5 reads C0[15:0] as an immediate (see the sequencer section); ALUB is never 5. Idle 4/4, the add and subtract arms 0/1, multiply arms 4/4 |
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
57 IABSB, and from the same table 60 SLRBR, 61 SARBR, 62 SLLBR (barrel shifts; 62 is on 409 words of `ge7.bin` and in every console routine that builds a coordinate). The FALUOP and FMPYOP positions
are **inferred** with strong support (the four ALU arms and the two multiply arms of one test all fit, every one of the 20 commonest
values is a named function, and the positions agree with the schematic's independent numbering); what ALUA/ALUB values 0 and 1
select (probably the two registers or buses the operands arrive on), and the REG fields' exact roles, are unknown.

### Sequencer: C0

The third decode corrects the first two. The 16-bit field C0[15:0] is **not always a branch target**: it is also the immediate
constant of the ALU (below), and the first decode read immediates as jump targets. Everything that followed from that (the "jump
chain 65, 125, 126, 127", INIT "jumping to 160", RECTCOPY "jumping to 233 then 152", the "shared tail at 124 to 127") was an artefact and
is withdrawn. Tool: [tools/ge7-step.py](../../tools/ge7-step.py), whose `selftest` re-checks the statements marked "(test)".

- **ALUA = 5 selects C0[15:0] as the ALU's A operand (a 16-bit immediate).** [binary] Inferred, strong. ALUB is never 5 in any of
  the 23429 + 2203 + 301 words of `ge7.bin`, the diagnostic image and the PROM image (test); ALUA is 5 on 4777 words of `ge7.bin`, of which
  3233 carry a non-zero field and all but 221 have condition 0. The console INIT routine is a run of
  words of the form "IPASSA, ALUA = 5, RESEN, FIFOEN, READDR = r" (below): constants such as `0xb1` to `0xbd` that no jump could use. The
  immediate words are mostly control `0x3f` (`0x3f` with a non-zero field: 3142 words of `ge7.bin`, 2586 of them with ALUA = 5), but
  ALUA = 5 also occurs with `0x31`, `0x34` and `0x35`.
- **Conditions 1 to 8 with control `0x36` (and the older `0x16`/`0x17`/`0x37` forms) are conditional jumps to the field.** [binary]
  All 3194 of 3194 targets land on a record in `ge7.bin`, 22 of 22 in the PROM image; in the diagnostic routines the targets are
  failure entries and the words after failure blocks. Established that the field is the target on these words; what makes each jump taken is below.
- **Condition 0 with control `0x36` falls through** (the target is 0). Control `0x3f` falls through too: it is the immediate carrier.
- **Control `0x31` with target 0 is not a jump.** [binary] Established as a software expectation: FloatOps (HQ2 slot 59, GE7 1533) works
  on the machine, and its third word (1535) is a `0x31` word with target 0 that reads the operation number (RAM0AD = 2) and starts the
  subtraction chain that dispatches to the six arms; if it jumped to 0 no arm could run. Five more `0x31` target-0 words are the first
  word of a routine the host starts (GE7 388, 395, 917, 933, 960 in the diagnostic image, all doing ALU work), and 86 of the 114
  `0x31` target-0 words of `ge7.bin` do not follow a stall word (test), most of them with ALU work in the word. So the earlier "idle = condition 10, then
  jump to 0" was wrong in its second half: a `0x31` word does not return to 0 and the stall is the only stop. Every routine in the
  images ends in a condition-10 word; what releases it is the HQ2 loading the next start address (inferred; consistent with HQ2 start
  words being the only entry).
- **Control `0x31` with a non-zero field** (2144 words of `ge7.bin`, 1819 with a field that is a record address, 1624 below 256, 141 alone 272
  times) is a *deferred or call-like* use of the field, not an immediate jump. [binary] Inferred. In the PROM image the routines COLOR,
  PNT2I, RECTI2D and LINE2I each hold one such word with field `0x1d` (29), the first word of the block that writes
  RE3 registers `0x73`, `0x74`, `0x6a`, `0x6e`, `0x70`, `0x71`, `0x7b`, `0x7c`, `0x52` to `0x55`, `0x46` to `0x49`, `0x4c` to `0x4f`, `0x7d`, `0x7e` (the second half of INIT).
  The word in PNT2I is word 63, followed by five words that write `0x20`, `0x22`, `0x21`, `0x5f` and `0x40`, which are the draw (the
  same address family as the GeFifoTest span, below); an immediate jump at 63 would skip them. So the jump is delayed, conditional on
  something not in C0, or the field is data that happens to equal 29. Discriminator: whether an RE3 write trace of a console
  point shows the `0x73` ... `0x7e` block after the draw. Unknown.
- **Condition 10 with no target is the stall** (`0x02b6....`): the word waits, the next word is the `0x31` word of the pair. Seen as the
  idle pair at address 0 and 1, as the end of every routine, and in the failure words of GeSeqTest. In the drawing routines the stall word
  and the word after it carry FIFOEN writes (READDR `0x5f`, then `0x40`, `0x08` or `0x7e`): a flush write, the wait, a closing write. Inferred.
- **Conditions 14 then 15 with control `0x17` and SHFTSRC = 3 write the ALU result to the shared RAM; this is the one transfer with a
  known answer.** [binary] Inferred from a whole small routine: ShramTest (HQ2 slot 3, GE7 388 to 393 in the diagnostic image) is a condition-14 word, an
  IPASSA word with ALUA = 0 and RESEN, a condition-15 word with control `0x17`, then the stall, and the host
  (`gr2_ShramTest`, function at `0x8852cff0`) then requires shared word 255 + n to equal the engine number n for each engine n. So the
  value stored is the ALU result, and one of the operand selects delivers a per-engine number (which select carries it is unknown: ALUA = 0 is the
  only operand select in the word). FloatOps' tail (1549, 1550) and GeSeqTest's words 1418 and 1421 are the same pair, and the shared
  results of FloatOps (word 255 + n) come from it. The shared address (255 + n) is not in the microword, so the HQ2 or the engine supplies it.
- **Conditions 9, 11, 12 and 13 never carry a target** (11 once, with an immediate). Condition 9 words with an ALU add sit in FpuCondTest's
  failure-record writer (GE7 1900 on) and GeSeqTest's last words (1442, 1444, 1446, 1448) are four condition-9 words each followed by a RAM0 address 3
  to 6. Reading: they too are transfers with the shared RAM (a store at an incrementing address, as the failure records need). Inferred; unverified.
- **C0[21] is probably not stored.** The stored microword is 128 bits ([devices/ge7](../../devices/ge7/README.md): 32 + 32 + 32 + 7 + 25), so
  the 25 stored bits of C0 cannot cover the 26 bits (25:0) that the records use, and the read-back mask `0x03dfffff` drops exactly bit 21.
  Inferred. The images set it in 88% of words (control `0x36` and `0x37`; `0x16` and `0x17` are the clear forms). It correlates with SHFTSRC: 2610 of the 2810 words
  with the bit clear have SHFTSRC = 3, against 108 of 20619 with it set. The correlation is not exact, so the bit is not simply
  derived from SHFTSRC. A model should treat `0x16`/`0x17` and `0x36`/`0x37` as the same control value; no test distinguishes them.

### GeSeqTest as a known answer

The routine is GE7 1354 to 1455 in the diagnostic image (HQ2 slot 12 starts it at 1354). The host (`gr2_GeSeqTest`) checks nine RAM0 words of each
engine (addresses 0 to 8 of its input RAM window) against `0xffffffff` and the shared word 255 + engine against 1; the messages name
"Ram0_addr" and "shram_addr". [binary]

Words 1354 to 1367 load the immediate 28 (`0x1c`) and write it to RAM0 addresses 0 to 10 and `0x7f` (RAM0DEST = 3): the RAM0 address test. The
rest is a chain of integer ALU operations (IPASSA, INEGA, ISUB of a register with itself) each followed by a branch, laid out in
blocks: a block of "operate, branch over the failure, failure = a condition-10 word with a RAM0 write to the block's own address, a
`0x31` word". Seven failure words write RAM0 addresses 0, 1, 1, 7, 8, 9 and `0x7f`, and a corrupted branch would stall in one of them. The
stepper enumerates every outcome of the thirteen condition 1 to 8 branches between 1368 and the final writes at 1450 that avoids all
seven failure words (`ge7-step.py paths`): **four outcome sets**, and the branches that are the same in all four are the known answers:

| Word | Condition | BRCOND | Target | Required outcome | Context |
|---|---|---|---|---|---|
| 1369 | 5 | 0 | 1374 (past failure at 1372) | taken | previous ALU result IPASSA of +28 |
| 1375 | 1 | 0 | 1381 (past failure at 1379) | taken | same |
| 1383 | 3 | `0x60` | 1438 (into failure at 1440) | not taken | after ISUB of a register with itself (zero result) |
| 1387 | 3 | `0x62` | 1393 (past failure at 1391) | taken | after a second ISUB x - x |
| 1400, 1407 | 8, 4 | `0x60` | 1438 | not taken | after ISUB x - x |

So, as inferred readings: **BRCOND is a flag select that works together with the condition**, because one condition number (3) is
true for `0x62` and false for `0x60` over the same zero result; conditions 1 and 5 with BRCOND 0 are true for a positive non-zero result.
The remaining branches (1394 condition 6, 1396 condition 2, 1403 condition 8 and 1410 condition 4) differ among the four sets, so their
polarity is **unknown**; which flag value each needs depends on the flag latency and the INEGA-before-branch order, which the tests
do not pin down. What writes the shared word's value 1, and what makes a failure word's RAM0 write differ from the load at the start, are also unknown:
the block has no word that stores to the shared RAM except the condition 9, 14 and 15 words, whose operands are not decoded. The flag names the diagnostic program prints for
FpuCondTest ("Fpu Cond: %s did not set %s flag": zero, neg and a third called pass, numbered 1, 2 and 4) are the flags these
conditions test; their mapping to condition numbers is unknown. SpfCondTest's messages name the four sample strobes (QSAM, TSAM,
VPSAM1, VPSAM2) and loop 8, 36, 4 and 2 values against a table in the program.

### The RE3 output path

- **FIFOEN and READDR are the raster-engine write.** The GE7 symbol has 32 `RE` data pins and `REWR`, `RERD`, `REEN` strobes (schematic),
  and the microword supplies an 8-bit address (READDR) and an enable (FIFOEN). Binary support: of the nine console routines only the
  drawing ones carry FIFOEN. COLOR and CMOV2I, which draw nothing, have none. FIFOEN is set on 124 of 301 words of the PROM image and
  2414 of 23429 of `ge7.bin`. Inferred.
- **Data source (inferred).** The written word is the ALU result of the same cycle, held in the result register between RESEN words.
  Binary evidence: INIT writes a run of constants `0xb1` to `0xbd` with the writing word's own IPASSA-immediate (the first three registers
  `0x61`, `0x62`, `0x63` take `0xb1`, `0xb2`, `0xb3`), and twenty following FIFOEN words that pass A idle (ALUA = ALUB = 4,
  FPASSA, no RESEN) write the value `0x40` that the last immediate left, which needs a held result; in PNT2I and GeFifoTest the FIFOEN
  words carry ALU operations on RAM0 slot data (OR, IADD of an immediate, SLLBR) in the word that writes. The
  alternative (the previous word's result) is not excluded by anything here.
- **RE3 write sequence of the PROM image routines**, in execution order with every condition 1 to 8 branch not taken and `0x31` as fall-through (`ge7-step.py step`).
  The last address of each row is written by the word after the stall:

  | Routine (GE7 start) | READDR values in order |
  |---|---|
  | INIT (10) | `6c 60 69 61 62 63 65 64 6d 67 68 6b 66 72 73 74 6a 6e 70 71 7b 7c 52 53 54 55 46 47 48 49 4c 4d 4e 4f 7d`, then after the stall `7e` |
  | COLOR (51), CMOV2I (107) | none |
  | PNT2I (58) | `00 08 20 22 21 5f`, then after the stall `40` |
  | RECTI2D (69) | `00 08 20 21 25 24 23 5f`, then `40` |
  | LINE2I (89) | `20 40 21 22 22 00 5f`, then `08` (not sent by the PROM) |
  | DRAWCHAR (115) | `00 08 67 20 6f 21 24 23 5f 25 5e` and then a loop of writes to `00` over the 18 row words |
  | RECTCOPY (201) | `08 20 21 25 23 24 67 5f 00` and a repeat of `20 21 25 23 24 67 5f 00` |

  RE3 addresses written, grouped as the routines group them: `0x00` and `0x08` open every primitive that draws, `0x20` to `0x25` are written per primitive, `0x40` to `0x42` follow the colour reads in GeFifoTest, `0x46` to `0x49`, `0x4c` to `0x4f`
  and `0x52` to `0x55` are three groups of four that INIT fills with the same value (`0x40`: probably four components of three
  parameter sets), `0x5e` and `0x5f` are flush or end markers, `0x60` to `0x6f` and `0x72` to `0x74` are mode and control words INIT sets to constants, and
  `0x7b` to `0x7e` close INIT. The meaning of each address is **unknown**: it needs the RE3 side (schematic sheet 12, or a software reader of the
  registers; none ships).
- **GeFifoTest** (GE7 989 to 1003) reads RAM0 slots 1 and 2 (x and y), then 5, 6 and 7 (the colour words) and writes `00 08 20 21 22 40 41 5f 42`
  with a flush `5f` and a closing `42`: the same set of addresses as PNT2I plus `41` and `42`. The pixel span that the host reads back is
  therefore RE3's response to those writes. The three colour slots are consumed by SLLBR words that precede the writes of `22`, `40`
  and `41`. Inferred, with the colour-to-address assignment unknown.
- **INIT's state.** About 36 addresses `0x46` to `0x7e` are initialised: the 20 registers set to the held value, 12 set to `0xb1` to `0xbd`,
  and four to `0xa0` and `0x40`. It is a block of raster-engine state, and nothing in the microcode names
  it. The PROM sends INIT with one zero word and the full image's INIT reads that word first.
- **Next route.** The RE3 sheet and the diagnostic RE3 tests: no diagnostic test pins an RE3 register address to a meaning (the program reads
  back only a pixel span), so the per-address meaning needs either schematic sheet 12 (vendor-derived: inferred at best) or a software
  reader of the registers.

### Other observations

- The nine console routines' slot sets and the pre-call described below stand with RAM0AD for the input slot.
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
| 401 INIT | control writes (`0x001f`, `0x0800`), one flag-form read, start GE7 at 10. The full image first reads one operand into slot 0. | one word, 0 in 4.0.5D | 10 to 50. Straight-line: loads constants and writes 36 raster-engine addresses (the table in [the RE3 section](#the-re3-output-path)), ending at the stall at 49. The old reading "jumps to 160" took the immediate `0xa0` of word 10 for a target. Established as the RE3 state initialiser by the write list; the PROM sends one zero word that INIT does not read. |
| 402 COLOR | one read-last into slot 0, one control write (`0x0020`), start GE7 at 51 | the colour value | 51 to 57. Four do-nothing words, a `0x31` word with field `0x1d`, the stall, no raster-engine write and no RAM0 read in the words the stepper reaches. Inferred: the colour is consumed by the `0x31` word's target path, whatever that is; see the `0x31` item in the sequencer section. |
| 404 PNT2I | reads slots 0 (x) and 1 (y), the control write, start at 58 | x token, y data | 58 to 68. Three immediate loads (`0x7c`, `0x7c`, `0x40`), writes RE3 `00 08 20 22 21 5f` and after the stall `40`; slot 1 is read at word 63, the `0x31` word with field `0x1d`. Inferred: plots one pixel at (x, y). |
| 405 RECTI2D | reads slots 0 to 3, the control write, start at 69 | x1, y1, x2, y2 | 69 to 88. Reads slots 2, 1 and 3 (RAM0AD) in words 70 to 80, writes RE3 `00 08 20 21 25 24 23 5f` then `40`, one `0x31` word with field `0x1d` at 84. Inferred: draws the filled box. |
| 406 CMOV2I | reads slots 0 and 1, control write, start at 107 | x, y | 107 to 114. Five do-nothing words, a `0x31` word with field `0x3c` (60) at 112 that reads slot 1, the stall; no raster-engine write. Inferred: stores the current position; slots 0 and 1 are consumed into engine state, which is why no draw follows. |
| 407 LINE2I | reads slots 0 to 3, control write, start at 89 | x1, y1, x2, y2 (not sent by the PROM) | 89 to 106. Reads slots 0 to 3; writes RE3 `20 40 21 22 22 00 5f` and after the stall `08`; one `0x31` word with field `0x1d` at 90. Inferred: draws a line. |
| 408 DRAWCHAR | seven reads into slots 0 to 6, then 17 reads into slots 24 down to 8, then a read-last into slot 7; control write; start at 115 | width token, six parameters and 18 row words (25 words, matches the PROM caller) | 115 to 200. Three `0x31` words at 115, 116, 117 (fields `0x3c`, `0x3d`, `0x3c`) with ALU work and RAM0 reads 5 and 6, then writes RE3 `00 08 67 20 6f 21 24 23 5f 25 5e`, then a chain of condition 3 and 7 branches over the 18 row slots (138 to 179) and a block of writes to RE3 `00` (180 on). Inferred. |
| 409 RECTCOPY | call to a subroutine (the one at 600) first, reads into slot 14, then 13, then slots 0 to 5 (the last one read-last); start at 201 | `(width+3)>>2`, the 4864/n line count, six more words (8 words, matches the PROM caller) | 201 to 244. Immediate loads (`0x40`, `0x96`, `0x7c`, `0x98` ...), writes RE3 `08 20 21 25 23 24 67 5f 00` twice, one branch (241, condition 7), the stall at 243. Inferred: it moves rectangle words through the raster engine twice (two passes). The old "jump to 233 then 152" took immediates `0xe9` and `0x98` for targets. |
| 417, 418, 419 (no PROM caller) | 417: the pre-call, then 5 reads (slots 8, 1 to 4); 418: 1 read into slot 0; 419: a flag-form read and a branch that loops to itself | not sent | 245 to 286, 287 to 295 and 302 to 308 (296 to 301 is the pre-call's target). Unknown purpose; the full `hq2.bin` has no words at these slots. |

One shared structure is the **pre-call**: slots 417 and 409 both begin with a call to HQ2 address 600, a 21-word subroutine that
starts a GE7 routine at 296 (a one-word jump to the epilogue) and returns. Reading: a "wait until the engine is idle" step before the
operands are taken. Inferred from the word shape only.

## What a QEMU model needs from this, and what it does not yet get

- A model that accepts the console tokens and draws their effect directly (the plan in [pipeline.md](pipeline.md)) needs none of this
  beyond the slot counts above: nine tokens, operand counts and their order. These are established.
- A model that runs `hq2.bin` and `ge7.bin` for GL needs the full HQ2 op set (the `0x80` bits and about 10 unknown op values), the
  rest of the GE7 data path (register file, RAM1/RAM2, the source and destination selects, the condition semantics) and the
  RE3 command data. The ALU and multiplier operations, the input RAM address, the immediate select and the raster-engine write strobe and
  register address are now located (graded inferred), and the control flow of conditions 1 to 8 is a conditional jump to the field; with them a
  first GE7 data-path interpreter can run the FloatOps arms. It cannot yet run the polarity of every condition (GeSeqTest fixes four
  of the thirteen branches), the `0x31` words with a target, or the shared-RAM transfers (conditions 9 to 15), and it does not know what any
  RE3 address means.
