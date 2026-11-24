# GR2 microcode: image formats and first decode

What `hq2.bin`, `ge7.bin` and the two console images embedded in the 4.0.5D Indigo PROM contain, how far their instruction words have
been decoded, and what each console token's routine does. The loader view of the images (registers, masks, load order) is in
[devices/ge7](../../devices/ge7/README.md) and [devices/hq2](../../devices/hq2/README.md); the token numbering and the GL token
catalogue are in [pipeline.md](pipeline.md). Tool: [tools/ucode-decode.py](../../tools/ucode-decode.py) (`uv run --script`; it checks
the images and prints statistics, per-slot walks and constants-block entries, never a listing) and [tools/ge7-step.py](../../tools/ge7-step.py) (control-flow stepper, the data-path model `run` and the regression `selftest`).

**Status after the eighth pass (2026-11-24).** The pixel-DMA routines separate the zero reading of select 4 from the other two: each routine parks the right edge `((x1 + 0x800) << 11) | 1` in register 15 and reads it back through select 4 for RE3 `0x21`, so with select 4 as the constant zero the right edge never reaches RE3 ([select 4](#the-data-path)). The previous-result and held-register readings remain, and no known answer separates those two. PROM 4.0.5G's copy of `pix_dma` is read: an unreferenced test whose rectangles agree. GE7 1250 is the host's Z-plane DMA (`pix_dma_zb`, called by `gr2_chkzplanes` and `gr2_chkzoffset`) and RE3 `0x6b` is the Z-plane transfer's mode value, 2, which the host's slot 53 token also writes (the mode tokens are under [the pixel-DMA routines](#the-pixel-dma-routines-as-known-answers)). The multiplier selects MPYA = 4, 6, 7 and MPYB = 7, the senses of conditions 4 and 8, and the negative cases for `0x63`, `0x6b`, `0x68` and `0x69` are still without a host answer; the routes tried this pass are in [questions](../../questions/microcode.md).

**Status after the seventh pass (2026-11-24).** The host-side code of the pixel-DMA tests (`pix_dma`, `gr2_shramre3dma`, `gr2_stridedma`, `gr2_re3dma` in `ide.IP20`) turned out to run three of the diagnostic image's routines (GE7 1208, 1250, 1294) and gave the first host-derived expectation for the multiplier: they form width times height with `IMPY` (MPYA = 3, MPYB = 6) and read it back through select 7, which makes **MPYB = 6 the previous ALU result** (inferred, strong; the host never reads the stored count, see below) ([the pixel-DMA routines](#the-pixel-dma-routines-as-known-answers)). The same routines write the rectangle edge registers of RE3, and they show that select 4 has a third reading, the constant zero, which passes every known answer that the other two readings pass and removes RECTI2D's unexplained doubling; select 4 is still not separated by a host answer. MPYA = 4, 6 (as a multiplier source), 7 and MPYB = 7 still have no known answer. No second known answer for conditions 4 and 8 exists in the images: the routine with the cond 8 words is started by a token that no host program in `ide.IP20` or PROM 4.0.5D sends. LINE2I's y1 does reach an RE3 write (corrected below), and DRAWCHAR and RECTCOPY have no branch on an unknown line (corrected below).

**Status after the sixth pass (2026-11-24).** The data path runs the diagnostic program's known answers ([the data path](#the-data-path)): ALUA = 5 is a read of the image's constants block (not an immediate), results have fixed tap delays, and the ALU flags behind `0x63`, `0x64`, `0x6b`, `0x68`, `0x69` are fixed except as listed there. The sixth pass settles three things: select 7 is the multiplier output (the SeedRom and SqRom loops now reproduce the host's 256 table words, and RECTI2D's min/max pairs read), the multiplier B selects 4 and 5 are the two ROMs, and the shared-RAM words that stores name are not the constants block. It also proves that the cond 4 and cond 8 outcomes in GeSeqTest cannot be explained by any line polarity. Earlier statements that this contradicts are corrected in place.

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
  `ge7.bin`: 23429 records, addresses 0 to 36194. The two GE7 images are in strictly ascending order with gaps; the HQ2 images are not (1 descent in the PROM image, 103 in `hq2.bin`).

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
| `0x20` | `0x2000` in 391 words | The word that ends a routine; the next FIFO token's slot word is fetched after it. Seventeen other operands besides `0x0000` (`0x6464`, `0x4f9b`, `0x512c` and similar) occur on 36 words: unknown. | inferred for `0x2000` |
| others (`0x01` to `0x06`, `0x10`, `0x22`, `0x81`, `0x90` to `0xd0`) | | Present in `hq2.bin` only (about 400 words); not decoded. | unknown |

Cross-checks run: (1) the HQ2 words of the seven console tokens that `hq2.bin` has (RECTCOPY, 409, is not in it) are the same in the PROM image and in `hq2.bin` apart from the GE7 address
and the word numbers (the full image's INIT additionally reads one operand into slot 0); (2) the number of operand reads of each token
equals the number of words its PROM caller writes (below); (3) every branch target lands on a word.

## The diagnostic program's own images

`ide.IP20` (Diagnostics 5.2, SHA-256 `744fdebc...df14`) carries four microcode images in its data section, found by their magic
(`ucode-decode.py ide`): a **diagnostic GE7 image** of 2203 records (addresses 0 to 2202, build text of August 1992), its HQ2 image
(977 records, addresses 0 to 1456: a run from 512 to 1456, then four short runs in 0 to 511), and a pair of console images of February 1993 (GE7 308 records,
HQ2 150) that match the PROM's token set but are a different build: its routine start addresses are those of the PROM image plus 7, except INIT, which stays at 10 (COLOR 58, PNT2I 65, RECTI2D 76 against 51, 58, 69), so the PROM image, not this one, is the one the console-token statements below read. `gr2_ucload` selects between them by argument. [binary] The diagnostic images are the
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
| `gr2_ShramTest`, `Ram12Test`, `SeedRomTest`, `SqRomTest`, `GeBusTest` | One word each to slots 3, 2, 4, 5 and 7. ShramTest: shared word 255 + n must equal n. Ram12Test: six words per engine at shared 255 + 6n on, each non-zero (two for RAM1, two for RAM2, two for the register file). The others compare an expected value with an actual one. | Names the units the microword's RAM1, RAM2 and register fields address. ShramTest is decoded (conditions 14 and 15, below). Ram12 (GE7 395 on) writes RAM1 addresses 0 to 31 (RAM1DEST = 3), then reads each back as ISUB with ALUB = 1 and ORs the differences with ALUA = 7, ALUB = 6, which suggests ALUB = 1 selects the RAM1 output; inferred. The SeedRom, SqRom and GeBus routines are read in [their own section](#seedrom-sqrom-and-gebus). |

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
   case arms of the FloatOps routine, the slot numbers HQ2 stores, the eight console routines, and field statistics over `ge7.bin`.
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
| 45-50 (C3[18:13]) | FALUOP | 6 | ALU function | **binary**: IADD 0x28, ISUB 0x29, FADD 3, FSUB 8 in the four arms; FPASSA (4, the idle value) is 49% of `ge7.bin` words; the 46 names are below |
| 51-58 (C3[26:19]) | BRCOND | 8 | branch condition select | schematic; nonzero almost only on conditional branches with C0 condition 3, 4, 7, 8; the flags `0x62` to `0x6b` are decoded in [the data path](#the-data-path) |
| 59-61, 62-64 | MPYA, MPYB | 3 each | multiplier operand selects | schematic; **binary**: 0 RAM0, 1 RAM1, 3 register REGA / REGB (FloatOps arms use MPYA 0, MPYB 1; FpuCondTest's multiplier tests use 3) |
| 65-67, 68-70 (C2[3:1], C2[6:4]) | ALUA, ALUB | 3 each | ALU operand selects | **binary**: 0 RAM0, 1 RAM1, 3 register (REGC, REGD), 4 and 6 the previous result, 5 the constants block at C0[15:0] (A only: ALUB is never 5), 7 the result two words back; see [the data path](#the-data-path). Idle 4/4, the add and subtract arms 0/1, multiply arms 4/4 |
| 71 (C2[7]) | BUSEL | 1 | result bus source | schematic; set in both multiply arms only |
| 72, 73 (C2[8], C2[9]) | REGSEL, RESEN | 1 each | register select, result enable | schematic; RESEN set in all six arms; no known answer needs it (7099 of 23429 words set it) |
| 74-82 | RAM0DEST, RAM1DEST, RAM2DEST | 3 each | RAM write destinations | schematic; **binary** (inferred): 3 writes the previous word's result (GeSeqTest's failure marker, Ram12Test's fill), RAM1DEST = 1 writes the RAM0 output (FloatOps copies y), 4 copies a RAM0 slot at a four-word offset (GeBusTest) |
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
select, see [the data path](#the-data-path) for the operand selects, the register file and the result taps.

### The data path

Decoded in the fifth pass from the diagnostic program's known answers, with a data-flow model, `Engine` in [tools/ge7-step.py](../../tools/ge7-step.py)
(`ge7-step.py run`, and the "data path" checks of `selftest`). Everything here is **inferred**: each rule is checked against known
host-side answers (the numbers are given), none is read from a document. It corrects the earlier reading that ALUA = 5 is a 16-bit immediate.

**A constants block, not an immediate.** On a control `0x3f` word, ALUA = 5 selects shared-RAM word C0[15:0], which the loader filled from the
image's constants block ([devices/ge7](../../devices/ge7/README.md#the-constants-block): 500 words copied to shared RAM `+0x0`). Evidence, all in
the diagnostic image: (1) the 45 loads that precede the FpuCondTest tests hold the ALU function number at that index (`C[index]` = number, 45 of
45; the old "function + 27" is the index offset); the three loads at 1571 to 1573 hold `0x100`, `0x200`, `0x400`, the flag index shifted left 8 that
the host decodes from the failure record (`sra 8`); (2) GeSeqTest's register 1 comes from `C[0x1c]` = 1 and the host expects 1; the SeedRom and
SqRom loops load `C[0x5d]` = 128, the host's stride; (3) GeFifoTest loads `C[0x62]` = `0x800`, `C[0x25]` = 10 and `C[0x1d]` = 2 and writes a ten-pixel span
(below); (4) the console INIT in the PROM image and the diagnostic INIT write the same values to nine RE3 addresses although their load indices differ (the old "shifted
by `0x2d`, build-relative pointers" reading is withdrawn: the indices differ because the two images' constants blocks differ); (5) every one of the 3142
nonzero `0x3f` fields of `ge7.bin` is below `0xfc` (max `0xfb`), inside the 253 constants in use. On other control values ALUA = 5 with field 0 (1544 words of `ge7.bin`, 1499 of them control `0x36` or `0x37`) reads
the shared word at an address register that a control `0x31` word loaded earlier (PNT2I word 66 reads the stored colour at `0x1d` that word 63 named); the distance
between the two words is not fixed (1 to 7), so the exact timing is open.

**Operand selects.** ALUA, ALUB: 0 RAM0\[RAM0AD\] (the input slots), 1 RAM1\[RAM1AD\], 3 register REGC (A) or REGD (B), 4 and 6 the result of the previous word, 5
the shared word above (A only), 7 the multiplier output of the previous word. Established by function: FloatOps adds x (ALUA = 0, slot 0) and y (ALUB = 1, RAM1\[0\], which words 1533
and 1534 fill from slot 1 with RAM1DEST = 1) in all six arms (checked on six operand pairs); the dispatch (1535 to 1542) is a chain of ISUB with ALUA = 6, ALUB = 3
decrementing the operation number.

**Select 7 is the multiplier output, not "two words back"** (sixth pass; inferred, checked by `selftest` with controls). The multiplier runs on every word. Its operation is FMPYOP (0 IMPY, 1 FMPY, 2 MPASSA, 3 MPASSB), the idle value 2 passes operand A, and A is RAM0\[RAM0AD\] unless MPYA says otherwise, so an
idle word leaves "the RAM0 word named by this word" in the multiplier output. Three independent sites read it with select 7 on the next word:
(1) **SeedRom and SqRom.** Word 923 (939) is MPASSB with MPYB = 4 (5) and REGB holding the float built by 916 to 921; word 924 shifts select 7 right by 16 and 925 masks it with 0x7f, and the store at 927 writes the
result. With the multiplier output as select 7 and the ROM tables below, the engine stores exactly the host's 128 + 128 words; with "result two words back", with the two ROM selects exchanged or
with the seed ROM addressed one bit low, it does not. (2) **RECTI2D**, PROM image 70 to 83: `IMIN A = RAM0[2], B = 7` follows word 69, whose RAM0AD names slot 0, so it takes min(x2, x1); the other three pairs
(words 73, 77, 80) give max x, max y, min y; run with both operand orders. The earlier "result two words back" reading made those nonsense. (3) **Ram12Test**: the 154 `OR A = 7, B = 6` words follow an `ISUB` whose MPYA is 6, so the multiplier
passes the previous ALU result on: the OR accumulator, which the old reading also gave. MPYA and MPYB values: 0 RAM0, 1 RAM1, 3 REGA / REGB (these have known answers),
MPYB = 6 is the previous ALU result (seventh pass; inferred, strong: the three pixel-DMA routines, [below](#the-pixel-dma-routines-as-known-answers); with it read as the previous multiplier output no host rectangle gets its count). MPYA = 6 (the previous ALU result; the 173 diagnostic words with it include Ram12Test's, which pass the OR accumulator on, and no word of the diagnostic image multiplies with it), MPYA = 4 (the shared word that ALUA = 5 reads), MPYA = 7 and MPYB = 7 (the previous multiplier output) are structural guesses: no known answer fixes them. In the diagnostic image only words 138 and 147 multiply with MPYA = 4 and read the product through select 7, in a copy of a console routine that no host test sends; replacing MPYA = 4, 6 or 7 or MPYB = 7 by 0 in the `Engine` leaves every `selftest` check passing.

**MPYB = 4 and 5 are the seed and square-root ROMs, addressed by REGB** (sixth pass; inferred, strong). The ROM output is read in bits 22:16 (7 bits). The seed ROM address is REGB bits 22:16 (the seven mantissa bits), the square-root ROM address is bit 23 and bits 22:17
(exponent low bit and six mantissa bits). The loops build the address as `0x3f800000 | (i << 16)` (seed) and `0x3f000000 | (i << 17)` (square root), `i` = 0 to 127, and the host's tables are the closed forms of
[SeedRom, SqRom and GeBus](#seedrom-sqrom-and-gebus); `Engine.rom` uses those forms, so the check is of the addressing and the output position, not of the table values. What the other output bits (31:23 and 15:0) are is unknown:
the 199 GL words with FMPY and MPYB = 4 (27 MPASSB words with MPYB = 5) probably use the whole word as a float, which no known answer shows. MPYA = 4 has no data check: it is the same shared word as ALUA = 5 on all 556 control `0x3f` words that ALUA does not read (field statistics only), and no known answer consumes such a multiplier output.
BUSEL = 1 puts the multiplier on the result bus
(FloatOps IMPY and FMPY arms), and the COLOR word (BUSEL = 1, no multiplier operand) takes the host's data word, as the HQ2 `read-last` delivers it (inferred).

**Select 4: the zero reading is refuted, two readings fit** (eighth pass, inferred; the seventh pass found three that fit every known answer). Select 4 as the previous result, as a register held by RESEN, and as the constant zero (`Engine.HELD`, `Engine.ZERO4`) all pass every known answer (`selftest` runs FloatOps, FpuCondTest, SeedRom, SqRom, GeFifoTest and the DMA counts under each). What speaks for each:
the doubling and the history. (1) The zero reading makes RECTI2D write the pixel coordinates themselves: `0x20` = xmin, `0x21` = xmax with bit 0 set, `0x25` = ymax, `0x24` = ymin - 1 and `0x23` = 0.0, which are the roles that the pixel-DMA routine gives the same four registers in fixed point (`0x20` = x0, `0x21` = x1 with bit 0 set, `0x24` = y0 - 1, `0x25` = y1), and the `FADD A = 4, B = 6` idiom is then `0 + x`; with the previous result every value is twice that, which nothing explains. (2) 185 of the 263 routine starts of `hq2.bin` read select 4 for real work (an operation that uses the operand, not an idle pass) before any RESEN word has run in the routine, so under either of the other readings they would use whatever the routine before left; the zero reading has no such dependence. Neither argument is a host answer, and the two RECTI2D checks below still take the previous result as the model. What would settle it: a routine with a host-checked output whose first word reads select 4.

*Eighth pass, against the zero reading.* The three pixel-DMA routines (GE7 1208, 1294, 1250) compute `((x1 + 0x800) << 11) | 1` from the host's x1, write it to register 15 (REGFDEST = 3, start + 17) and read register 15 once, 9 words later (start + 26: IPASSA of register 15 with RESEN). That word's result is not stored; it reaches RE3 `0x21` only through the select 4 reads that follow. With select 4 as the previous result or as the RESEN-held register `0x21` is the right edge (for x1 = 131, `0x441801`) and moves with x1; with select 4 as the constant zero `0x21` is 0 whatever x1 is and no RE3 write depends on x1, so the register-15 round trip would be dead code and the rectangle would have a right edge of 0 (checked by `selftest`, both flags, all three routines). The host's pixel compare ([the rectangles](#the-pixel-dma-routines-as-known-answers)) needs the transfer to stay inside its rectangle, so the zero reading is refuted for these routines: **inferred, strong**. It is not **established**: the host never reads `0x21`, and that RE3 uses `0x21` as the right edge is itself the inferred role. The two arguments above for the zero reading (RECTI2D's doubling, the history of routine starts) now stand as unexplained observations about the other two readings, not as evidence for zero; the 185 of 263 starts that read select 4 first remain unexplained under both.
The earlier case for the previous result follows.

**Select 4 as the previous result (sixth pass; inferred, weak).** RECTI2D separated it from a held register: its four coordinate chains are `FLOATA`, `FADD A = 4, B = 6`. With select 4 = previous result the five RE3 values each depend on one coordinate (0x20 on min x, 0x21 on max x, 0x25 on max y, 0x23 and 0x24 on min y; see
[the RE3 values of RECTI2D](#recti2d-the-values-it-writes)), with a held register every value is a running sum of the coordinates. The first can describe a rectangle, the second cannot; but the first doubles each coordinate, which is not understood.

**Result taps.** The ALU result of word N is used at fixed delays by its consumers: a register write (REGWR with REGFDEST = 3) at N+1; select 6 at N+1; select 7 at N+2; a shared-RAM
store (SHFTSRC = 3) at N+2; a raster-engine write (FIFOEN, READDR) at N+2; the flags for the conditional branches at N+2; RAM0DEST = 3 and RAM1DEST = 3 at N+1. Evidence: FpuCondTest loads
each function number one word before the register write that keeps it, and every flag test branches two words after its operation (92 of 92); FloatOps' store at 1550 is two words after the arm
that computes (six operand pairs); GeFifoTest and PNT2I load the value `2` two words before the write to RE `0x5f`, and the x, y and x end words sit two words before theirs (the
shifted forms appear where the write is; with a delay of one word the same words give unshifted x and y and the colour at `0x5f`); GeSeqTest's failure words write the result of the INEGA that precedes
them to RAM0 and the host reads `0xffffffff` there. Not separated: RESEN (set on 7099 of 23429 words) is not needed by the model, which passes every known answer without it; the idle words that follow a RESEN word repeat its result,
so INIT cannot tell "the previous result passes through" from "a result register holds the last RESEN result" (the same open point as select 4).

**Shared-RAM stores.** A store takes its address from a counter that a `0x31` word (or `0x32`, `0x33`) loads from its field and that counts up by one after each store: COLOR (word 55 names `0x1d`, the
store at 57 writes the host's colour there), CMOV2I (word 112 names `0x3c`, the stores at 113 and 114 write x and y to `0x3c` and `0x3d`, the words DRAWCHAR reads back with fields
`0x3c`, `0x3d`, `0x3c`), and FpuCondTest's count at shared word 255 followed by records at 256 on (the window itself is set by the cond 14 word and the engine number). Checked on COLOR and CMOV2I; the cond 14
window base is not modelled.

**The state words are not the constants block** (sixth pass; inferred, strong for the negative, open for the mechanism). `0x1d`, `0x3c` and `0x3d` are numerically inside the 253 constants the loader put at shared word 0, but the two sets cannot be one memory at one base. In `ge7.bin`
293 store words with an explicit address (control `0x11` to `0x13`, SHFTSRC = 3; they carry the address exactly as `0x31` to `0x33` do, bit 21 of C0 being clear on store words) name 126 addresses, and 44 of those are also read as constants through control `0x3f`:
`K[0x41]` = 0.5 is read 111 times and named by a store once, `K[0x8d]` = 5 (an immediate stand-in, like `K[0x89]` to `K[0x90]` = 1 to 8) is read 66 times and named by 55 stores (in 54 of them the word right after a condition-10 stall, the end of a routine),
`K[0x3d]` is read 17 times (the Clear routine, GE7 25322, and the routine of HQ2 slot 13 add it to and subtract it from float coordinates: the float 0.0051) and named by 6 stores (GE7 1366, 23870, 23990, 24088, 24258, 24464, where it is updated with `0x3b` and `0x3c`; CMOV2I's y store at GE7 36042, addressed by the counter that 36040 loads, is a seventh). A single namespace would have the 55 routine tails clobber the constant 5 that 66 words read: what they store is a computed result (an OR or a passed register), not 5. The Engine therefore keeps two namespaces: control `0x3f` reads the constants block (`sh`), every other control reads and
writes `state`. The diagnostic program's own images show it too: its slot-51 routine (GE7 1042) reads and rewrites `0x67` and `0x68`, which SeedRom and SqRom read as constants (`K[0x67]` = 0x7e, `K[0x68]` = 0x7f). What this does **not** settle is the mechanism: a second memory, or a base offset that puts state above the
constants. No diagnostic known answer reads a shared word through a state address: every host-visible store is a window store whose address is not in the microword, and the console routines are self-consistent either way. The host-visible results start at shared word 255, and the diagnostic image
has a `0x33` word with field `0xff` at word 2; whether that field is a host word index is not shown. The diagnostic program's `gr2_shramre3dma` writes 1 to 1024 into shared words 255 on and expects them in the frame buffer, so the host's shared word 255 is the address its DMA uses; nothing ties it to a state address.
A QEMU model that models the host-visible shared RAM and the engines' state as one array can run the console routines but would corrupt the constants in `ge7.bin`.

**Control-field classes.** The control value says how C0[15:0] is used, measured over `ge7.bin` (maximum field, count): `0x3f` a constants index (`0xfb`, 3142 words); `0x31` a small state address
(`0x380`, 2144; `0x11` is the same with C0[21] clear, 369 words with a field, 287 of them a store: sixth pass); `0x32` and `0x33` (and `0x12`, `0x13`) a wide state address (`0x7d00` and `0x7fdf`, 99 and 16, none with a condition; fields below `0x8000` words = 128 KiB; 8 of the 99 `0x32` fields are not records);
`0x34` a one-hot code (2, 4, 8 or 16, 81 words); `0x36`, `0x37` and the older `0x16`, `0x17` a branch target (`0x8d44`); `0x35` up to `0xf280`, 63 words, unknown.

**Flags and conditions.** The line that a conditional branch (conditions 3, 4, 7, 8, BRCOND non-zero) tests comes from the word two back. The known answers fix these lines (the `Engine` passes
92 of 92 FpuCondTest tests, the six FloatOps dispatches, the two ROM-loop counts, and the PNT2I and GeFifoTest runs):

| BRCOND | Line, and when it is low | What decides it | Evidence |
|---|---|---|---|
| `0x64` | zero: low when the ALU result is zero (a float zero of either sign) | the result | FpuCondTest: 45 first tests, one per function; SeedRom and SqRom loop back on it while their counter is not zero |
| `0x63` | neg: low when the selected operand is negative | the sign of the value the function selects or passes before any final negate or absolute value; for the adders the sign of the result | the second tests: INEGA, IABSA, FNEGA, FABSA, INEGB, IABSB, FNEGB, FABSB of a negative operand set it although the result is positive; FMIN, FMAX, FMINABS, FMAXABS and IMIN to IMAXABS test the selected operand |
| `0x6b` | pass: low when the selected operand is B | which operand a pass or select function takes | the third tests: every B function (IPASSB, INEGB, IABSB, FPASSB, FNEGB, FABSB) of a positive operand, and FMIN, FMAX, FMINABS, FMAXABS, IMIN, IMAX, IMINABS, IMAXABS when B wins; the identical-operand pairs (IMIN of 1 and -1 tested with `0x63` then `0x6b`, FMAXABS of 0 and -1.0) need both low |
| `0x69` | multiplier zero: low when the multiplier result is zero | the multiplier result | FpuCondTest IMPY and FMPY first tests |
| `0x68` | multiplier neg: low when it is negative | the sign bit of the multiplier result | the six second tests (IMPY, FMPY, MPASSA, MPASSB) |
| `0x62` | high when A equals B | the ISUB compare | FloatOps dispatch (6 of 6 arms, cond 7), GeSeqTest 1387 (cond 3); not separated from `0x64`, because ISUB gives the same for both |
| `0x60`, `0x61` | compare, unknown | in `ge7.bin` they follow ISUB, IRSUB, FSUB at N-2 (`0x61` after IRSUB on 198 of 289) | unknown |

The known answers for `0x63`, `0x6b`, `0x68` and `0x69` are positive only: FpuCondTest requires the line to be active, so a decode that asserted the line always would pass it. The lines that also have negative cases (`0x62` in FloatOps, `0x64` in the ROM loops) are the better supported; the rules for `0x63`, `0x6b`, `0x68` and `0x69` say when the line must be active, not when it must be inactive.

**No polarity explains the cond 4 and cond 8 sites** (sixth pass; a negative result under the premises below, graded inferred, `selftest`). The six GeSeqTest sites that decide it are conds 3, 8 and 4 on `0x60` (1383, 1400, 1407, none taken) and conds 3, 8 and 4 on `0x62` (1387 taken, 1403 and 1410 not taken). Each is the
same pattern, `ISUB` of register 0 with itself, an idle word, the branch, and the diagnostic engine's ALU flags (equal, zero, neg, A < B, A > B) are identical at the branch word, one word back and two words back for the three sites of each line. Any rule that is a function of a line value, a polarity per
condition and those flags therefore gives conds 4 and 8 the same outcome as cond 3 on the same line. The data need different ones: write the lines' truth value after x - x as L60 and L62 and the
polarity of cond c as p(c) (taken when L = p): cond 3 gives L60 != p(3) and L62 = p(3), conds 4 and 8 give L60 != p(c) and L62 != p(c); the first two make L60 != L62, the last make L60 = L62. No assignment exists (checked by enumeration; it also fails when the line value may differ for every distinct flag vector, at each of stages 0 to 2, and with select 4 read as a RESEN-held register, so it does not rest on those two choices). It does rest on the six outcomes, which come from the passing-path analysis and its assumption that a stall ends a routine. So
either conds 4 and 8 read a different flag source than cond 3 (the FpuCondTest cond 8 sites read the ALU and multiplier flags, so a third source is possible), or one of the six outcomes of the unique-path analysis is wrong. The second means a stall does not end a routine, which the start statistic and the host's finish flag argue against.
`0x60` has 20 more cond 8 uses in the diagnostic image (GE7 1098 to 1142, every one an `ISUB A = 7, B = 3` after a shift or mask, all targeting 1145), in a routine whose host test has not been read.

The three names the host prints (zero, neg, pass, its flag numbers 1, 2, 4) belong to `0x64`, `0x63` and `0x6b` by the failure writers (`0x64` and `0x69` to 1900, `0x63` and `0x68` to 1903, `0x6b` to 1906, which
OR in `0x100`, `0x200`, `0x400`); a healthy engine takes none of the 92 branches, so the host's message "did not set the flag" means the line stayed high. Reading **R2**, the one that fits best: all four
conditions 3, 4, 7 and 8 branch when the selected line is high, and the lines of `0x63`, `0x64`, `0x68`, `0x69`, `0x6b` are active low (low when the named condition holds). R2 reproduces FpuCondTest (cond 8), FloatOps (cond 7 on `0x62`), the SeedRom and
SqRom loops (cond 7 on `0x64` branches back while the counter is not zero: 128 passes), the three `0x60` sites and the three `0x77` sites of GeSeqTest, and misses two sites, the cond 4 and cond 8 branches on `0x62` at 1410 and 1403. Reading
**R1**, the host-name reading (cond 7 and 3 branch when the flag is set, cond 8 and 4 when it is clear, flags active high) reproduces FpuCondTest, FloatOps and the `0x62` sites of GeSeqTest but not the ROM loops (they would exit after one pass), not the three `0x60` sites and not the
`0x77` sites. The two readings differ only in the sense of the branch; both give the same flags. Conditions 1 and 5 always branch (the six arm words of FloatOps all end with cond 5 to the common tail at 1549; GeSeqTest takes 1369 and 1375), conditions
2 and 6 never (GeSeqTest 1394, 1396).

**What stays open.** (1) Why the `0x62` branches of conditions 4 and 8 at 1403 and 1410 fall through, and the `0x60` ones: see the negative result above. Seventh pass: the diagnostic image has no other cond 4 word and no cond 8 word outside GeSeqTest, FpuCondTest and the slot 51 routine (GE7 1042 to 1152, cond 8 on `0x60` at 1092 to 1142); the host never sends slot 51 (`+0x400cc`): no store with that offset or load of the constant 0x33 as a slot number anywhere in `ide.IP20`'s code (text addresses `0x88510000` to `0x8858ffff`: the only hits are unrelated), none in PROM 4.0.5D below its HQ2 image, and the only generic sender is the interactive `gr2_wrFIFO` command (token number typed by the user). So no second known answer exists in the held programs; GE7 24623 on (cond 4 with `0x69`) has none either. PROM 4.0.5G (`070-8116-005`) is scanned the same way and has no such store either. Not checked: callers of the interactive menu's slot-taking helpers (`FIFOcheckpat` and the like) one by one, stores built from computed offsets in the PROMs, and the PROMs' non-code data. PROM 4.0.5G does send slot 9 from a copy of `pix_dma` at `0xbfc07aec`; eighth pass: that copy is read in [the pixel-DMA routines](#the-pixel-dma-routines-as-known-answers) and is not a source for the console image's routine. (2) What `0x60`, `0x61`, `0x77`, `0x6f`, `0x67` and the values above `0x77` select.
(3) RESEN, REGFDEST 1 and 2, RAM2DEST, the other RAM destination codes (RAM1DEST = 4 copies RAM0 slots in GeBusTest at a four-word offset), REGE, REGSEL. (4) The upper bits of the ROM outputs (see the ROM paragraph in the data path). (5) DRAWCHAR's 18-word loop, LINE2I (its y1 never reaches an RE write in the engine, so the model of its multiplier words is incomplete), RECTCOPY and the doubling in RECTI2D's `FADD A = 4, B = 6`.

### The pixel-DMA routines as known answers

Seventh pass. The host side is `pix_dma` (flag 1 and a write with its second argument 0, flag 0 and a readback with 2; `gr2_chkpixels` and `gr2_re3dma` write a pattern and read it back), `gr2_shramre3dma`, `gr2_stridedma` (first phase) and `gr2_re3dma` in `ide.IP20`. Each sends a direction flag and x0, y0, x1, y1 as five words to HQ2 slot 9, 11 or 56 (tokens at `+0x40024`, `+0x4002c`, `+0x400e0`; the HQ2 words `read slot8, 1, 2, 3, 4` put them in RAM0 slots 8, 1, 2, 3, 4) and then waits for finish flag 1. Slots 9, 11 and 56 start GE7 1208, 1294 and 1250 (the diagnostic image; the console image has the same words at 245). [binary] for the host's sends and checks.

- **The host cases.** `gr2_shramre3dma` fills shared words 255 to 1278 with 1 to 1024, sends the rectangle (100, 100) to (131, 131) through slot 11, reads it back through slot 9 and compares every pixel with its index: 1024 words must move, in row-major order. `gr2_stridedma` first moves 441 (0x1b9) words into (10, 10) to (30, 30). `gr2_re3dma` writes one row of 0x500 words per line at x = 0 to 0x4ff and reads it back. If the stored word is the count the transfer uses (inferred, not shown), a routine that gets it wrong moves too few or too many words, and the compare fails.
- **The count.** Words 1231, 1274 and 1317 (245's twin is 268) are `IMPY` with MPYA = 3 (REGA, which holds the width the two words before it computed with ISUB and IADD) and MPYB = 6 (the previous ALU result, the height); the next word is an IRSUB with select 7 and the constant 1, and the result is stored: 0x3ff for 32 x 32, 0x1b8 for 21 x 21, 0x4ff for 1280 x 1. The product equals the word count of the rectangle in every case: 12 of 12 pairs of routine and rectangle in `selftest`, which runs each of the three routines on the three host rectangles and one made-up one (7, 3) to (20, 12); the host itself drives each routine with only some of them. With MPYB = 6 read as the previous multiplier output the count is wrong in all 12. Graded: **inferred, strong** for MPYB = 6 and for select 7 as the product; the minus one is the usual count-minus-one form and is **unknown** (the host never reads the stored word). 1294 then stores `C[0xee]` = 0xff, the shared word where `gr2_shramre3dma` put its data.
- **The rectangle edges.** All three routines write `0x20` = (x0 + 0x800) << 11, `0x21` = ((x1 + 0x800) << 11) | 1, `0x24` = (y0 - 1 + 0x800) << 11, `0x25` = (y1 + 0x800) << 11, `0x23` = 0x200000, `0x5f` = 0x200000 and `0x67` = 0x180000 (flag 1, the host's write into the bitplanes) or 0x100000 (flag 0, the readback), cleared at the end; the dependency of each write on each operand is one to one. The host sends flag 1 for a write (`pix_dma` with a1 = 0, `gr2_shramre3dma`'s own slot 11 send) and flag 0 for a readback; flag 1 takes the branch at 1235 (cond 7 on the zero line of the flag word: taken, so the line is high for a non-zero flag, as for the ROM loops) and flag 0 falls through. The host's pixel compare puts the rectangle where the host says, so these are the edge registers of a rectangle; the roles are **inferred** (nothing names the registers). RECTI2D's registers `0x20`, `0x21`, `0x24`, `0x25` take the same roles ([RECTI2D](#recti2d-the-values-it-writes)).

- **The 4.0.5G PROM's copy of `pix_dma`.** Eighth pass. [binary] PROM 4.0.5G (`070-8116-005`) holds the function at `0xbfc07aec` (the store near `0xbfc07b74` is its slot 9 flag, `+0x40024`), called twice from the "CPU to bitplanes DMA test" at `0xbfc066e8`. Read in full: it takes the GIO base, a mode (0 or 2), x0, y0, x1, y1 and a buffer; it builds an MC descriptor of `((y1 - y0 + 1) << 16) | (4 * (x1 - x0) + 4)` (lines, bytes per line, with no minus one: the host's word count is exactly width times height), stores the flag (1 for mode 0, a write; 0 otherwise, a readback), then x0, y0, x1, y1 to the data port `+0x40000`, as `ide.IP20`'s copy does, and polls for the DMA to finish. The test writes a ramp of 256 words to the row y = 0 and again to y = 1023 (x = 0 to 255), reads both back and counts mismatches. Nothing refers to the test: no `jal` or `j`, no data word and no `lui` pair with an `addiu` or `ori` forms `0xbfc066e8` (a computed address is not excluded), and the PROM's two console images are the same bytes as 4.0.5D's, with no handler at slot 9 (its pixel-DMA token is slot 417, GE7 245), so the test cannot run against its own microcode: it is the diagnostic's code carried along (inferred). What it adds is two host rectangles, 256 x 1 at y = 0 and y = 1023, which `selftest` runs on the console routine at 245: count 255, `0x24` = `0x3ff800` for y0 - 1 = -1 (the bias wraps without a sign problem) and `0x25` = `0x5ff800`. It gives no new host answer for the stored count's minus one: the host's own sizes are unbiased, so the minus one is internal to the engine's count word (**unknown**, as before).
- **The Z-plane DMA (GE7 1250, HQ2 slot 56).** Eighth pass. The host function is `pix_dma_zb`, called by `gr2_chkzplanes` (`gr2_zb` runs it over (0, 0) to (1279, 1022), one row at a time) and by `gr2_chkzoffset` (rows of 1280 words, y = 0 to 1023, with the same slot 52 and slot 53 tokens). [binary] Around the rows it sends two mode tokens: 1 to slot 52 (`+0x400d0`, GE7 1161) before the Z rows are written and 0 after, and 2 to slot 53 (`+0x400d4`, GE7 1199) before they are read back and 0 after. The word reaches the routine through the bus: slot 52 with 1 writes RE3 `0x66` = 0, `0x65` = `0x40`, `0x61` = `0xffffffff` and `0x60` = 0, and with 0 writes `0x65` = 0 and swaps the pair (`0x60` = `0xffffffff`, `0x61` = 0); slot 53 writes `0x6b` = the host word (2, then 0). Both also write `0x6a` = `0x44`. Routine 1250 makes the same RE3 writes as 1208 plus two to `0x6b`: `C[0x1d]` = 2 right after `0x67` and before the rectangle, and a second at the end. On the write path (flag 1) the second `0x6b` is 0; on the readback path (flag 0) it takes the right-edge word, 0x441801 for x1 = 131 under the previous-result and held readings of select 4, so the readback leaves `0x6b` holding a stale value that the host then clears with its slot 53 token (inferred; the zero reading would give 0, but is refuted above). Roles: `0x6b` is written 2 for the Z-plane transfer, which fits a plane or bank select (the host's own function names the Z planes), and `0x60`, `0x61` and `0x65` change with the write mode token; what each bit means is **unknown**. The count and edge checks of the other two routines hold unchanged for 1250 ([count](#the-pixel-dma-routines-as-known-answers): `gr2_re3dma`'s 1280-word row and the Z rows are the same 1280 x 1 case, count 0x4ff).

### Sequencer: C0

The third decode corrects the first two. The 16-bit field C0[15:0] is **not always a branch target**: it is also a read address of the
shared RAM and its constants block (below and [the data path](#the-data-path)), and the first decode read those as jump targets. Everything that followed from that (the "jump
chain 65, 125, 126, 127", INIT "jumping to 160", RECTCOPY "jumping to 233 then 152", the "shared tail at 124 to 127") was an artefact and
is withdrawn. Tool: [tools/ge7-step.py](../../tools/ge7-step.py), whose `selftest` re-checks the statements marked "(test)".

- **ALUA = 5 selects shared-RAM word C0[15:0] as the ALU's A operand; on a control `0x3f` word that is a constants-block index.** [binary] Inferred,
  strong; evidence in [the data path](#the-data-path). ALUB is never 5 in any of the 23429 + 2203 + 301 words of `ge7.bin`, the diagnostic image and the PROM image (test);
  ALUA is 5 on 4777 words of `ge7.bin`, of which 3233 carry a non-zero field (3026 of those with condition 0; 221 of all 4777 words carry a condition). The console INIT routine is a run of
  words of the form "IPASSA, ALUA = 5, RESEN, FIFOEN, READDR = r" (below) that load RE3 initial values from the constants block (`C[0xb1]` and so on). The
  words are mostly control `0x3f` (`0x3f` with a non-zero field: 3142 words of `ge7.bin`, 2586 of them with ALUA = 5), but
  ALUA = 5 also occurs with `0x31` (488 non-zero fields), `0x36` and `0x37` (152) and `0x32` and `0x33` (7), never with `0x34` or `0x35` (whose fields are small one-hot codes and not targets).
- **Conditions 1 to 8 with control `0x36` (and the older `0x16`/`0x17`/`0x37` forms) are conditional jumps to the field.** [binary]
  All 3194 of 3194 targets land on a record in `ge7.bin` (3183 with those controls, 11 more with other control values), 22 of 22 in the PROM image; in the diagnostic routines the targets are
  failure entries and the words after failure blocks. Established that the field is the target on these words; what makes each jump taken is below.
- **Condition 0 with control `0x36` falls through** (the target is 0). Control `0x3f` falls through too: it carries a constants-block index.
- **Control `0x31` with target 0 is not a jump.** [binary] Inferred (a software expectation): FloatOps (HQ2 slot 59, GE7 1533) works
  on the machine, and its third word (1535) is a `0x31` word with target 0 that reads the operation number (RAM0AD = 2) and starts the
  subtraction chain that dispatches to the six arms; if it jumped to 0 no arm could run. Five more `0x31` target-0 words are the first
  word of a routine the host starts (GE7 388, 395, 917, 933, 960 in the diagnostic image; the last three do ALU work, 388 and 395 pass A idle), and 86 of the 114
  `0x31` target-0 words of `ge7.bin` do not follow a stall word (test), most of them with ALU work in the word. So the earlier "idle = condition 10, then
  jump to 0" was wrong in its second half: a `0x31` word does not return to 0 and the stall is the only stop. Every routine in the
  images ends in a condition-10 word; what releases it is the HQ2 loading the next start address (inferred; consistent with HQ2 start
  words being the only entry).
- **Control `0x31`, `0x32` and `0x33` with a non-zero field carry a shared-RAM address, not a branch target.** [binary] Inferred, with the access settled by the console
  routines. Measurements over `ge7.bin` (`ge7-step.py selftest` with the full image): (1) all 3194 conditional-branch targets
  are records, but 325 of the 2144 non-zero `0x31` fields are not (239, 245, 225, 251, 252 and others, 20 to 76 times each), and a
  jump into an empty word could not run; (2) only 22 of the 2144 equal an HQ2 start address (1.0%, the same as the 1.1% of records
  that are starts); (3) `0x31` fields never exceed `0x380`, `0x32` fields (99 words) stay below `0x8000` = the 32768 words of the shared RAM while branch targets reach `0x8d44`,
  8 of the 99 `0x32` fields are not records, and none of them has a condition; (4) in the small routines a `0x32` word with field `0x4022` sits one to four words before the
  SHFTSRC = 3 stores and the routine's stall (GE7 1288, 1357, 1381, 1392) and the routine ends exactly as it would without it; a jump to `0x4022` would skip the stores.
  What the access is: the field **loads the shared-RAM store address**, which then counts up by one per store (SHFTSRC = 3): COLOR (word 55, field `0x1d`) takes the host's data word
  through the data bus and the store two words later (57) writes it to shared word `0x1d`; CMOV2I (word 112, field `0x3c`) has its x and y stored at `0x3c` and `0x3d` by words 113 and 114
  (checked by `ge7-step.py run`); DRAWCHAR's words 115 to 117 carry `0x3c`, `0x3d`, `0x3c` and read the position back (ALUA = 5 on a `0x31` word reads the word named by its own field, so 116 and 117, which also add, are
  reads, not counterexamples); PNT2I (63), RECTI2D (84), LINE2I (90) and DRAWCHAR (123) carry `0x1d` and read the colour back (PNT2I word 66, control `0x36`, ALUA = 5, field 0, reads the word named
  at 63). The same pairing holds in `hq2.bin`/`ge7.bin` (COLOR, PNT2I, RECTI2D, LINE2I `0x1d`, CMOV2I `0x3c`, DRAWCHAR `0x3c 0x3d 0x3c ... 0x1d`). So `0x1d` is the current drawing colour and
  `0x3c`/`0x3d` the current position, in a state namespace that is not the constants block ([the data path](#the-data-path), sixth pass). The 0x31 word of RECTCOPY (244, field `0x8d`) names a constants-block word (PROM `C[0x8d]` = 0x17, an
  enumeration), the field being a read address there. `0x32` fields (15218 to 16418 on most words, 32000 and 24550 on two) name a wider area, probably the output or feedback buffer that the 
  stores of the vertex routines fill; the field `0x4022` words are followed by two stores of result words. The `0x34` words carry a one-hot code (2, 4, 8, 16): see the stall bullet.
- **BRCOND is a flag select for conditions 3, 4, 7 and 8 only.** [binary] Established as an encoding fact: of the 2535 words with those conditions
  in `ge7.bin` none has BRCOND 0 (`ucode-decode.py cond`), while conditions 1, 2, 5 and 6 have BRCOND 0 on 606 of 659. So 1, 2, 5, 6
  test fixed conditions and 3, 4, 7, 8 test the flag that BRCOND names. The flags `0x63`, `0x64`, `0x6b`, `0x68`, `0x69` and `0x62` are decoded in [the data path](#the-data-path);
  `0x60`, `0x61`, `0x77` and the rest are open. The field has other uses on
  words that do not branch: the shift count of SLLBR/SLRBR/SARBR (SeedRom words 916, 920, 924: `0x17`, `0x10`, `0x10`; GeFifoTest: `0xb`,
  `0xf`) and strobe-like values (`0x7a` to `0x7e`, `0x72`, `0x73`) next to FIFOEN writes and the sample strobes.
- **Polarity.** Inferred. The branch sense of conditions 3, 4, 7 and 8 and the lines of `0x62`, `0x63`, `0x64`, `0x68`, `0x69`, `0x6b` are in [the data path](#the-data-path) (reading R2: all four branch when the line is high,
  the five named lines are active low); conditions 1 and 5 always branch, 2 and 6 never. The test word for each ALU function is built from the constants block: the number loaded before it is the function number (`C[index]` = number; the doc's
  earlier "function + 27" is the index offset), which also fixes the multiplier operations: FMPYOP 0 IMPY, 1 FMPY, 2 MPASSA, 3 MPASSB (the tests numbered 16 to 19). The earlier statement that no sign predicate fits `0x63` and `0x6b` is
  withdrawn: they test the sign of the selected operand before a negate or absolute value, and "B was selected", not the sign of the result. The earlier "condition 8 is taken when its flag is clear" (R1) is one of two readings that fit FpuCondTest.
- **Condition 10 with no target is the stall, and it ends a routine.** [binary] Inferred (a software expectation), now with three independent supports. The word waits, the next word is the `0x31`
  or `0x11` word of the pair. Seen as the idle pair at address 0 and 1, as the end of every routine, and in the failure words of GeSeqTest. In the drawing routines the stall word
  and the word after it carry FIFOEN writes (READDR `0x5f`, then `0x40`, `0x08` or `0x7e`): the closing write after the stall. (1) Routine boundaries: of the 263 distinct start addresses of `hq2.bin`, 167 sit exactly two
  words after a stall (stall, release word, entry) and 251 reach a stall by falling through (selftest), so no routine runs into the next one's code. (2) The host side: `diag_finish`
  clears finish flag 2, sends HQ2 slot 1, waits 1000 us and reads status bit 1 (`+0x6a040`); slot 1 starts GE7 routine 48, which is six idle words, a control `0x34` word with field 8 (word 53) and a stall (54). The flag
  is raised by the `0x34` word, so the host learns of the end of the routine through that word, and the stall is what holds the engine afterwards. The DMA tokens (HQ2 slots 9, 10, 11, 47, 49, 54, 56: `pix_dma`,
  `gr2_dma_cpu_ge7`, `gr2_shramre3dma`, `gr2_stridedma`, the context switch) end in `0x34` words with fields 2 and 4 and the host polls status bit 2 (finish flag 1) after them. So the `0x34` field is a one-hot completion code
  (8 for flag 2; 4 and 2 for the DMA completions, which of the status bits each sets is not fixed). (3) The failure words of GeSeqTest (a stall with a RAM0 write) and the routine's own end at 1440 behave as ends. What no
  host-side answer shows is whether the engine merely pauses until the next start; GeSeqTest's passing-path argument needs the end reading and still gets a contradiction on the `0x60` sites (see [the data path](#the-data-path)).
- **Conditions 14 and 15 bracket a window of shared-RAM stores; the stores are the SHFTSRC = 3 words inside it.** [binary] Inferred, with
  five independent known answers. The host reads engine n's results at shared word 255 + stride * n + i, and the stride is the number of
  SHFTSRC = 3 words between a cond 14 word and the next cond 15 word: ShramTest (389 to 392) 1, FloatOps (1549, 1550) 1, GeSeqTest
  (1418 to 1421) 1, GeBusTest (974 to 986) 10, Ram12Test (396 to 913) 6, each equal to the host's stride (selftest). So the engines take
  turns (cond 14 requests the shared RAM, cond 15 releases it) and the block of each engine starts after the blocks of the engines
  before it; the address is not in the microword. The routine that the host starts for SeedRomTest and SqRomTest has a one-store loop
  (words 920 to 928 and 936 to 944, cond 7 with BRCOND `0x64` back to its head) with the host's stride 128, so about 128 passes. What is stored is the ALU result of the word
  two back (ShramTest: a per-engine number; GeSeqTest: the value 1 from register 1; GeBusTest: the ten words that the host sent).
  FpuCondTest does not use the window: the engines run one at a time (the host starts slot 57 once per engine), the count goes to word
  255 (word 1899, SHFTSRC = 3 after the stall at 1898) and the failure writers store the records at 256 on.
- **Condition 11 is tied to the raster-engine flush write.** [binary] 13 of the 14 cond 11 words in `ge7.bin` carry FIFOEN with READDR `0x5f`
  (the other sits between cond 3 words of a test sequence); the word before often carries BRCOND `0x7d` or `0x7e` and the word after
  often READDR `0x4b`. Reading (inferred): cond 11 is the wait for the output FIFO to drain before the flush; nothing in the
  diagnostic images runs it except GeSeqTest's word 1436, which is only a placeholder immediate carrier. Conditions 12 and 13 occur twice and
  four times (GE7 6526 to 6666, one bracketing a cond 3 branch with BRCOND `0xe9`): unknown. Condition 9 (679 words, BRCOND 0 on 630)
  precedes a store: the next word has a RAM0 destination in 17% of cases against 7% of all words, and in FpuCondTest's
  three failure writers (1901, 1904, 1907) it is the IADD that the SHFTSRC = 3 store (1902, 1905, 1908) follows; reading: it sets the
  address of the next store (inferred, unverified; the store counter of the data path counts up by itself, and CMOV2I has no cond 9 word, so cond 9 is not needed for that). Its FpuCondTest instance, word 1901, is also the IADD that increments the failure count in register `0xd`.
- **C0[21] is probably not stored.** The stored microword is 128 bits ([devices/ge7](../../devices/ge7/README.md): 32 + 32 + 32 + 7 + 25), so
  the 25 stored bits of C0 cannot cover the 26 bits (25:0) that the records use, and the read-back mask `0x03dfffff` drops exactly bit 21.
  Inferred. The images set it in 88% of words (control `0x36` and `0x37`; `0x16` and `0x17` are the clear forms). It correlates with SHFTSRC: 2610 of the 2810 words
  with the bit clear have SHFTSRC = 3, against 108 of 20619 with it set. The correlation is not exact, so the bit is not simply
  derived from SHFTSRC. A model should treat `0x16`/`0x17` and `0x36`/`0x37` as the same control value; no test distinguishes them.

### GeSeqTest as a known answer

The routine is GE7 1354 to 1455 in the diagnostic image (HQ2 slot 12 starts it at 1354). The host (`gr2_GeSeqTest`) checks nine RAM0 words of each
engine (addresses 0 to 8 of its input RAM window) against `0xffffffff` and the shared word 255 + engine against 1; the messages name
"Ram0_addr" and "shram_addr". [binary]

Words 1354 to 1367 load the constant `C[0x1c]` = 1 (register 1 gets it through word 1356's register write) and write the previous word's result to RAM0 addresses 0 to 10 and `0x7f`
(RAM0DEST = 3): the RAM0 address test, which leaves 1 and then 0, never `0xffffffff`. The
rest is a chain of integer ALU operations (IPASSA, INEGA, ISUB of a register with itself) each followed by a branch, laid out in
blocks: "operate, branch over the failure, failure = a condition-10 word with a RAM0 write to the block's own address, a `0x31` word". A failure word writes the result of the INEGA that
precedes it (register 1 negated, `0xffffffff`) to its RAM0 address, which is what the host looks for; seven
failure words write RAM0 addresses 0, 1, 1, 7, 8, 9 and `0x7f`. The word 1438 that three `0x60` branches target is not a failure word: it is the routine's normal tail
(1436 to 1440, which a passing run also executes), so those branches skip the shared store and the 1.

**The passing path is unique.** The only shared-RAM store in the routine is word 1421 (cond 15, SHFTSRC = 3, after IPASSA of
register 1 at 1419; the value 1 is register 1), so a run passes only if it reaches 1421 without stopping in a failure word. The earlier
reading enumerated the paths to the last word (1450) and found four outcome sets; those sets are the four early exits (1394, 1396, 1403,
1410 jump to the cond 9 tail at 1442 to 1448, which never stores the 1), and every one of them fails the shared-word check. Enumerating
the paths to 1421 (`ge7-step.py paths`, which now treats a stall as the end of the routine) gives exactly one set, and it continues
through the cond 3 and cond 8 branches of the tail (1423, 1431) to the last test word 1436 before the routine ends at the stall in 1440:

| Word | Cond | BRCOND | Target | Outcome | Reading |
|---|---|---|---|---|---|
| 1369 | 5 | 0 | 1374 | taken | register 1 passed through IPASSA |
| 1375 | 1 | 0 | 1381 | taken | register 1 negated (INEGA) |
| 1383 | 3 | `0x60` | 1438 (the tail, past the store) | not taken | after ISUB x - x |
| 1387 | 3 | `0x62` | 1393 | taken | same |
| 1394 | 6 | 0 | 1442 (exit) | not taken | |
| 1396 | 2 | 0 | 1444 (exit) | not taken | |
| 1400 | 8 | `0x60` | 1438 (the tail) | not taken | |
| 1403 | 8 | `0x62` | 1446 (exit) | not taken | |
| 1407 | 4 | `0x60` | 1438 (the tail) | not taken | |
| 1410 | 4 | `0x62` | 1448 (exit) | not taken | |
| 1412 | 7 | `0x77` | 1417 | taken | skips the failure at 1415 |
| 1423 | 3 | `0x77` | 1429 | taken | skips the failure at 1427 |
| 1431 | 8 | `0x77` | 1436 | taken | skips the failure at 1434 |

What this fixes [binary, inferred]: all thirteen outcomes (the earlier text fixed four). Under reading R2 of [the data path](#the-data-path) the table is explained except at 1403 and 1410: ISUB of a register with itself
sets the equal line high, so cond 3 on `0x62` is taken (1387); cond 5 and cond 1 are the always-taken pair and cond 6 and cond 2 the never-taken pair (the two senses are
fixed conditions, not a sign flag as this section first suggested); the three `0x60` sites (1383, 1400, 1407) fall through as the line is low for equal operands, and `0x77` is high at all three of its sites . The two sites that R2 gets wrong are the cond 8 and cond 4 branches on `0x62` (1403, 1410), which would be taken. A model should run GeSeqTest by taking exactly the branches the table lists as taken
rather than by evaluating `0x62`, `0x60` and `0x77`, until those two sites are explained.
SpfCondTest's messages name the four sample strobes (QSAM, TSAM, VPSAM1, VPSAM2) and loop 8, 36, 4 and 2 values against tables in the program.

### SeedRom, SqRom and GeBus

All three are small routines of the diagnostic image started by HQ2 slots 4, 5 and 7; the host compares the stored words
with tables of its own, so their contents are known answers for the ROMs, not for the sequencer. [binary]

- **SeedRom** (slot 4, GE7 916 to 931): a cond 14 to cond 15 window (919 to 929) around a loop (920 to 928, cond 7 with BRCOND `0x64` back to
  920) that shifts a constant (`C[0x68]`) with SLLBR and SLRBR, ANDs it with another constant and stores one value per pass; the pass counter starts at `C[0x5d]` = 128 and counts down to zero, and the host
  expects 128 words per engine at shared word 255 + 128n. **The expected table is the reciprocal seed:
  entry i = round(128 * (2 / (1 + i/128) - 1)), clamped to 127** (0x7f, 0x7e, 0x7c, ... 1; matches all 128 words; `ucode-decode.py roms`).
  So the seed ROM maps the top seven mantissa bits of x to about 1/x in 7 bits. The engine now reproduces all 128 words from the microcode: 916 builds `0x3f800000` (`C[0x68]` = 0x7f shifted left 23), each pass ORs the counter shifted left 16, REGB takes the float, the MPASSB word 923 with MPYB = 4
  reads the seed ROM at its bits 22:16, and 924 to 927 shift the multiplier output (select 7) right by 16, mask it with 0x7f and store it ([the data path](#the-data-path)).
- **SqRom** (slot 5, 932 to 947): the same shape (constants `C[0x67]`, `C[0x68]`); the table is the reciprocal square root seed over the 128 entries addressed
  by an exponent-parity bit and six mantissa bits (the loop ORs the counter shifted left 17 into `0x3f000000`, so the counter's top bit is the exponent bit; MPYB = 5; the engine reproduces all 128 words): for i < 64, floor(256 * (1/sqrt(2 (1 + i/64)) - 1/2)); for i >= 64,
  min(127, floor(256 * (1/sqrt(1 + (i-64)/64) - 1/2))). All 128 entries match.
- **GeBusTest** (slot 7, 948 to 987): HQ2 loads the ten words the host sent into engine slots 0 to 9; the engine copies each through RAM0 into
  RAM1 and RAM2, reads RAM1 back with ALUA = 1 and stores the ten words in a cond 14 to cond 15 window (stride 10). The host's pattern
  is ten words (0x12345678, 0x9abcdef0, 0x0fedcba9, 0x87654321 and the alternating-nibble words 0xbb44bb44 down to 0x66996699); a model passes
  by moving them unchanged. ALUA = 1 (and ALUB = 1 in Ram12Test) therefore selects the RAM1 output; the shift forms take their operand from the constants block (ALUA = 5)
  and BRCOND as the shift count.

### The RE3 output path

- **FIFOEN and READDR are the raster-engine write.** The GE7 symbol has 32 `RE` data pins and `REWR`, `RERD`, `REEN` strobes (schematic),
  and the microword supplies an 8-bit address (READDR) and an enable (FIFOEN). Binary support: of the eight console routines only the
  drawing ones carry FIFOEN. COLOR and CMOV2I, which draw nothing, have none. FIFOEN is set on 124 of 301 words of the PROM image and
  2414 of 23429 of `ge7.bin`. Inferred.
- **Data source: the ALU result two words back.** [binary] Inferred, with three known answers ([the data path](#the-data-path)). The word that carries FIFOEN and READDR writes the result computed by the word
  two before it, not its own: GeFifoTest and PNT2I load the constant `2` two words before the write to `0x5f`, and with that delay the writes give the clean values
  of the table in [devices/re3](../../devices/re3/README.md#addresses-the-microcode-writes) (start x, y and end x biased and shifted, the colour components shifted), where a delay of one word would give unshifted coordinates
  and the colour at `0x5f`. INIT writes a run of values loaded from the constants block with the same delay, and the idle words that follow
  (FPASSA of the previous result, no RESEN) repeat the last value, which is how the twenty registers `0x46` to `0x7e` are zeroed.
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
  and `0x52` to `0x55` are three groups of four that INIT zeroes, `0x5e` and `0x5f` are flush or end markers, `0x60` to `0x6f` and `0x70` to `0x74` are mode and control words INIT sets (the values and the roles that the known answers fix are in
  [devices/re3](../../devices/re3/README.md#addresses-the-microcode-writes)), and `0x7b` to `0x7e` close INIT.
- **GeFifoTest** (GE7 989 to 1003) reads RAM0 slots 1 and 2 (x and y), then 5, 6 and 7 (the colour words) and writes `00 08 20 21 22 40 41 5f 42`
  with a flush `5f` and a closing `42`: the same set of addresses as PNT2I plus `41` and `42`. With the two-word delay the writes are `0x8000`, `0`, x, y and x + 10 (each plus `0x800`, shifted left 11),
  the three colour words shifted left 11, and `2` to `0x5f`: a ten-pixel horizontal span of the host's colour, which is exactly what the host reads back (`ge7-step.py run` and the selftest reproduce the values). Inferred; the
  component order of the colour (slot 5 to `0x40`) follows the host's red, green, blue order.
- **INIT's state.** 36 addresses `0x46` to `0x7e` are initialised, 13 of them (`0x60` to `0x6d`, `0x72` to `0x74`) to non-zero values that two builds of the microcode agree on at nine addresses. The values are in [devices/re3](../../devices/re3/README.md#addresses-the-microcode-writes). The PROM sends INIT with one zero word and the full image's INIT reads that word first.
- **Next route.** The RE3 sheet and the diagnostic RE3 tests: no diagnostic test pins an RE3 register address to a meaning beyond the span (the program reads
  back only a pixel span), so the remaining per-address meaning needs either schematic sheet 12 (vendor-derived: inferred at best), the RECTI2D, LINE2I, DRAWCHAR and RECTCOPY data flows (which need select 7 and the float adds of select 4 resolved), or a software
  reader of the registers.

### RECTI2D: the values it writes

PROM image 69 to 88, run in the engine with the host's four operands in slots 0 to 3 (x1, y1, x2, y2) and the stored colour at state word `0x1d`. The routine has no conditional branch, so the values depend only on the data path. Inferred; select 4 as the previous result (see
[the data path](#the-data-path)) is the weaker part, and every value that goes through a `FADD A = 4, B = 6` carries its doubling. With select 4 as the constant zero (seventh pass; refuted for the pixel-DMA routines in the eighth) the doubling would go: for the same operands `0x20` = 100.0, `0x21` = 150.0 with bit 0 set, `0x25` = 260.0, `0x24` = 199.0, `0x23` = 0.0, the roles the pixel-DMA routines give those registers; the table below is the previous-result reading that `selftest` checks as the model.
Words 70, 73, 77 and 80 are the min and max pairs (select 7), so the routine accepts either corner order: xmin, xmax, ymax, ymin.

| RE3 address | Value for x1, y1, x2, y2 = 100, 200, 150, 260 | Depends on |
|---|---|---|
| `0x00` | `0` (`K[0x40]`) | nothing (PNT2I writes `0x8000` here) |
| `0x08` | `0x64` = xmin as an integer | xmin |
| `0x20` | float 200.0 = 2 xmin | xmin |
| `0x21` | float 300.0 with bit 0 set (`0x43960001`) = 2 xmax, OR 1 | xmax |
| `0x25` | float 520.0 = 2 ymax | ymax |
| `0x24`, `0x23` | float 398.0 = 2 (ymin - 1), the same word to both | ymin |
| `0x5f` | `0` (PNT2I and GeFifoTest write `2`) | nothing |
| `0x40` | the stored colour shifted left 11, as for PNT2I | colour |

Varying one operand by 7 changes exactly those RE values (x1: `0x08` and `0x20`; y1: `0x23` and `0x24`; x2: `0x21`; y2: `0x25`), which is the evidence for the per-coordinate roles; with select 4 as a RESEN-held register every value is a running sum of all four coordinates. The roles are
therefore inferred as: `0x20` and `0x21` the low and high x edge, `0x25` the high y edge and `0x23` and `0x24` the low y edge less one line, in a float form that is twice the pixel coordinate. Whether the factor of two is real (half-pixel units) or an artefact of select 4 is not settled.
The first RE3 write is `0x00`, as in PNT2I; the command written to `0x5f` differs (0 against 2), which fits `0x5f` being a command or operation code. LINE2I, DRAWCHAR and RECTCOPY are not tabulated: LINE2I: the statement that y1 reaches no RE3 address no longer holds in the current engine (seventh pass). `ge7-step.py run` on the PROM image from 89 writes `0x20` = x0, `0x40` = the colour, `0x21`, `0x22` twice (x1, then y1 as it came), `0x00` = `0x8000`, `0x5f` = 2 and `0x08`; y1 reaches the second `0x22` through word 100 (an FPASSA of RAM0 slot 3), and the slope path does not reach any write except `0x08`, which stays 0: the multiplier words 98 to 104 (MPYA = 3, 4 and 6, MPYB = 3, 4 and 7: a seed-ROM Newton step) need the ROM output's upper bits and select 4, 6 and 7 for MPYA and MPYB, which no known answer fixes, so `0x08` is **unknown**. LINE2I is not used by the PROM, so the format of its operands is not known; run on raw integers its FADD words give `0x21` a meaningless sum under the previous-result reading and y0 under the zero reading. DRAWCHAR and RECTCOPY: the earlier "branches on `0x61`, `0x6f`, `0x67`, `0x77`" was a misreading; `0x6f` and `0x67` are RE3 write addresses in those routines and the BRCOND values on their branch words are `0x61`, `0x62` and `0x64` only (PROM image 115 to 244). RECTCOPY (201 to 244) has one branch, cond 7 on `0x64` at 241 back to 208 (the second cond 7 on `0x64`, at 272, is in the pixel-DMA routine), and runs to its stall in the engine; DRAWCHAR has one cond 3 on `0x61` at word 138 and 19 branches on `0x62`, the equal line (17 of cond 3 at 143 to 175, 2 of cond 7 at 177 and 179) (a dispatch on the glyph row, in the style of FloatOps). Neither routine has a host answer. The words from 245 are the pixel-DMA routine described above, not a part of RECTCOPY.

### Other observations

- The eight console routines' slot sets and the pre-call described below stand with RAM0AD for the input slot.
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
- **Ops other than 0x00 with a branch-shaped operand are conditional branches.** [binary] Inferred from the structure. The diagnostic image has two
  runs (HQ2 680 to 710) of sixteen words alternating "op `0x06` or `0x07`, operand `(k << 13) | (address + 2)`" with a `0x40` read of slot
  `16 + k`: k counts 0 to 7 under op `0x06` and again under `0x07`, so bits 15:13 are a selector (one of eight conditions) and the low 13 bits
  are the target, which here skips the read that follows. `hq2.bin` has the same runs under op `0x02` (7 words with selectors 7 to 1, targets
  2 apart) and the other branch ops (`0x01`: 91 words, 26 with `0x2257`; `0x04`: 56 words; `0x05`: 22 words). The poll loops in the
  diagnostic image show how they are used: "`0x40` read, `0x80 0x1000`, `0x80 0x0020`, op `0x01` operand `0x4353`, `jump` back to the read"
  (846 to 850): the loop exits through the conditional branch when the condition holds, so op `0x00` types 6 and 7 may be the same selector
  form with op 0 as the condition code. Which condition each selector and each op number is stays unknown (no host test exercises it).
- **`0x40`/`0x60` operand fields.** [binary] Inferred from the distributions over `hq2.bin`: bits 9:5 are the slot, bits 4:0 a small number
  (`0x40`: 0 to 4 on 1021 of 1067 words, 1 on 505; `0x60`: 0 on 1454 of 1462) and bits 15:10 a code (`0x60`: 0 on 788, 9 on 364, 1 on 181;
  `0x40`: 13 on 318, 4 on 227, 0 on 182). In the long reads of the diagnostic image the slot counts up one word at a time while bits 4:0
  cycle 1, 2 and 0, or stay 1 or 2 for sixteen slots (HQ2 660 to 711), so bits 4:0 are not part of the slot number. The ops `0x48`, `0x50`
  and `0x70` (operand `0x3660` each, in the diagnostic image only) are the same read with op bits 3 or 4 set: a read mode. The `0x20` operand
  `0x0000` (10 words in the diagnostic image, and 11 in `hq2.bin`) sits between the first operand reads and the last one of tokens such as
  FloatOps (HQ2 slot 59: slots 0 and 1, `0x20 0x0000`, slot 2), so it looks like a "commit what has been read so far" step; `0x6464` and
  the 16 other `0x20` operands are unknown.
- **`0x80` operands, with their contexts.** [binary] Inferred. `0x0060` is the poll mask (bits 5 and 6): "read, `0x80 0x0060`, type-7
  branch back" waits (ShramTest, slot 3), and "`0x80 0x0060`, type-6 branch over `0x20 0x6464`" (GeFifoTest, slot 8, after the five
  operand reads) skips the `0x6464` word when the condition holds. `0x1000` is the last control write before a start in the diagnostic image
  (slots 3 and 8) and `0x0800` the one before a start that has read operands (slots 7 and 59), as in the console set; `0x0020` precedes
  24 of 42 diagnostic starts; `0x0100` pairs with op `0xd0 0x0000` ("`0xd0`, `0x80 0x0100`" repeated, HQ2 1031 to 1042), and `0x0001`, `0x0601`
  and `0x0641` follow starts. Bit meanings (which of 5 and 6 is empty or busy) are unknown. The remaining ops are in the diagnostic image only
  and form self-test sequences of the HQ2 itself: `0x81 0x0000` after each read of a run of slots (718 to 723), `0xa0 0x0004`
  before a read-last (768), `0xc8` and `0xd0` around `0x80 0x0100` (1031 to 1045, 1230 to 1236), `0x10 0x0000` before a call (1291). Their
  effects are **unknown**.

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
| 401 INIT | control writes (`0x001f`, `0x0800`), one flag-form read, start GE7 at 10. The full image first reads one operand into slot 0. | one word, 0 in 4.0.5D | 10 to 50. Straight-line: loads constants and writes 36 raster-engine addresses (the table in [the RE3 section](#the-re3-output-path)), ending at the stall at 49. The old reading "jumps to 160" took the immediate `0xa0` of word 10 for a target. Inferred as the RE3 state initialiser from the write list; the PROM sends one zero word that INIT does not read. |
| 402 COLOR | one read-last into slot 0, one control write (`0x0020`), start GE7 at 51 | the colour value | 51 to 57. Four do-nothing words, a `0x31` word with field `0x1d`, the stall, no raster-engine write and no RAM0 read in the words the stepper reaches. Inferred: the colour is passed on the data bus at the `0x31` word (55) and stored after the stall (57, SHFTSRC = 3) at the state address in its field (`0x1d`); see the `0x31` item in the sequencer section. |
| 404 PNT2I | reads slots 0 (x) and 1 (y), the control write, start at 58 | x token, y data | 58 to 68. Three constants-block loads (`C[0x7c]` = 1 twice, `C[0x40]` = 0: the bias `1 << 22` and the `0x8000` of the first write), writes RE3 `00 08 20 22 21 5f` and after the stall `40`; slot 1 is read at word 63, the `0x31` word with field `0x1d`. Inferred: plots one pixel at (x, y). |
| 405 RECTI2D | reads slots 0 to 3, the control write, start at 69 | x1, y1, x2, y2 | 69 to 88. Reads slots 2, 1 and 3 (RAM0AD) in words 70 to 80, writes RE3 `00 08 20 21 25 24 23 5f` then `40`, one `0x31` word with field `0x1d` at 84. Inferred: draws the filled box. |
| 406 CMOV2I | reads slots 0 and 1, control write, start at 107 | x, y | 107 to 114. Five do-nothing words, a `0x31` word with field `0x3c` (60) at 112 that reads slot 1, the stall; no raster-engine write. Inferred: stores the current position; slots 0 and 1 are consumed into engine state, which is why no draw follows. |
| 407 LINE2I | reads slots 0 to 3, control write, start at 89 | x1, y1, x2, y2 (not sent by the PROM) | 89 to 106. Reads slots 0 to 3; writes RE3 `20 40 21 22 22 00 5f` and after the stall `08`; one `0x31` word with field `0x1d` at 90. Inferred: draws a line. |
| 408 DRAWCHAR | seven reads into slots 0 to 6, then 17 reads into slots 24 down to 8, then a read-last into slot 7; control write; start at 115 | width token, six parameters and 18 row words (25 words, matches the PROM caller) | 115 to 200. Three `0x31` words at 115, 116, 117 (fields `0x3c`, `0x3d`, `0x3c`) with ALU work and RAM0 reads 5 and 6, then writes RE3 `00 08 67 20 6f 21 24 23 5f 25 5e`, then a chain of condition 3 and 7 branches over the 18 row slots (138 to 179) and a block of writes to RE3 `00` (180 on). Inferred. |
| 409 RECTCOPY | call to a subroutine (the one at 600) first, reads into slot 14, then 13, then slots 0 to 5 (the last one read-last); start at 201 | `(width+3)>>2`, the 4864/n line count, six more words (8 words, matches the PROM caller) | 201 to 244. Constants-block loads (indices `0x40`, `0x96`, `0x7c`, `0x98` ...), writes RE3 `08 20 21 25 23 24 67 5f 00` twice, one branch (241, condition 7), the stall at 243. Inferred: it moves rectangle words through the raster engine twice (two passes). The old "jump to 233 then 152" took immediates `0xe9` and `0x98` for targets. |
| 417, 418, 419 (no PROM caller) | 417: the pre-call, then 5 reads (slots 8, 1 to 4); 418: 1 read into slot 0; 419: a flag-form read and a branch that loops to itself | not sent | 245 to 286, 287 to 295 and 302 to 308 (296 to 301 is the pre-call's target). Unknown purpose; the full `hq2.bin` has no words at these slots. |

One shared structure is the **pre-call**: slots 417 and 409 both begin with a call to HQ2 address 600, a 21-word subroutine that
starts a GE7 routine at 296 (a one-word jump to the epilogue) and returns. Reading: a "wait until the engine is idle" step before the
operands are taken. Inferred from the word shape only.

## What a QEMU model needs from this, and what it does not yet get

- A model that accepts the console tokens and draws their effect directly (the plan in [pipeline.md](pipeline.md)) needs none of this
  beyond the slot counts above: eight tokens, operand counts and their order. These are established.
- A model that runs `hq2.bin` and `ge7.bin` for GL needs the full HQ2 op set (the `0x80` bits, the branch selectors and about 10 unknown op
  values), the GE7 data path and the RE3 command data. The data path is now specified to the point of running the diagnostic known answers
  ([the data path](#the-data-path), `Engine` in [tools/ge7-step.py](../../tools/ge7-step.py)): operand selects 0, 1, 3, 4, 5, 6, 7 (7 is the multiplier output) and the seed and square-root ROMs, the register file with its one-word write delay, the two-word taps for shared stores, RE writes and flags, the
  constants block, the state namespace of the `0x11` to `0x13` and `0x31` to `0x33` words (separate from the constants block), the lines `0x62`, `0x63`, `0x64`, `0x68`, `0x69`, `0x6b`, conditions 1 to 8, and the RE3 write values of INIT, PNT2I and GeFifoTest. It cannot yet run
  LINE2I, DRAWCHAR and RECTCOPY (the multiplier words of LINE2I and the flags `0x61`, `0x6f`, `0x67`, `0x77` are not settled; RECTI2D now runs), the ROM outputs' upper bits, flags `0x60`, `0x61`, `0x77` and above and the cond 4 and 8 senses, the cond 9, 12 and 13 words, RAM2 and the other
  RAM destination codes, and it knows the RE3 meaning of only the addresses listed in [devices/re3](../../devices/re3/README.md#addresses-the-microcode-writes).

## The IRIX 5.3 images

Round 9 read the IRIX 5.3 disc ([references/binaries.md](../../references/binaries.md#irix-53-install-disc-round-9)). Release 5.3 ships `hq2.bin` and `ge7.bin` as files and they are a different build from the 6.5 ones. [binary]; every count below is checked by `ge7-step.py selftest` when the 5.3 images and the R3000 Indigo's `ide` are given.

**Format and size.** Same header (magic `0x965e` and `0x966e`, version 1, record lengths 10 and 26, `V1.0`) and good record checksums. `ge7.bin` has 23312 records over addresses 0 to 36194 (611432 bytes and 23429 records in 6.5); `hq2.bin` 5513 records over 0 to 5784 (5642 over 0 to 5910 in 6.5). Established.

**GE7: 23043 of 23312 words equal the 6.5 word at the same address.** 269 words differ at the same address, 117 exist only in 6.5 and none only in 5.3, so 5.3 is a strict subset in address terms. Every difference sits at or above GE7 1363: runs of changed words 1363 to 1401, 1785, 1787 to 1792, 1857, 2577, 2766, 24072 to 24186, 24351, 24355, 24360, 24362 and 24366 to 24466; runs present only in 6.5 at 1402 to 1403, 24187 to 24265 and 24467 to 24502. The first 1362 words are identical. The known answers do not come from this image: the diagnostic and console images are separate programs (at the same addresses their words equal none of the full image's), and the R4000 `ide` of 5.3 carries the same four diagnostic and console images as the 5.2 one (equal as images). So the 5.3 full image adds no known answer. Established.

**HQ2: 364 of the 367 slots that reach a GE7 start reach the same start address; 355 are equal.** (A slot reaches a start by following the HQ2 jump words from the slot number to the `start-ge` word; this is the count `ge7-step.py` makes.) Changed starts: slots 111 to 115 (24164 and 24248 in 6.5, 24085 and 24169 in 5.3: the same routines moved down by the 79 words only 6.5 has), 206 (1386 against 1384), 208 (1397, 1395), 261 (24366, 24459) and 263 (1374, 1376). Slots 396 to 398 reach GE7 24072 in 6.5 and do not exist in 5.3; no shipped host code of either release sends them. Established for the counts.

**Which routines changed (by the 6.5 starts):** slots 262 and 263 (the raster position pass and read-back, GE7 1361 and 1374: in 6.5 the routine at 1374 makes four shared-RAM stores of the transformed position and the 5.3 routine at 1376 one other store, from the engine run with no inputs), slot 13 (GE7 1778: six MPYA fields and two other words), slots 51 and 52 (2562), 40 (2753) and 102 (24324) (one to five words each), slots 111, 112 and 114 (24164: 79 words precede it in 6.5 only, and after the shift it differs in 51 words; slots 113 and 115 at 24248, the `CopyToPipe` and `SwapToPipe` tokens, are word-identical but moved), and slot 261 (the RasterPos routine, 24366 against 24459: 44 words only in 6.5, six replaced and eight added in 5.3). The 5.3 GL core's `__glExpGetRasterPosData` and `__glExpPassRasterPosData` are empty stubs and its `RasterPos` entry points make no `+0x42414` store, so 5.3 host code starts slots 261 and 263 never and slot 262 only from `__glExpRenderBitmap`; the 6.5 core starts all three from the raster-position functions. Established for the counts, the stubs and the missing stores; the reading that 6.5 moved raster-position work onto the GE is inferred.

**The statistics that settled earlier questions hold on the second build.** BRCOND is non-zero on every cond 3, 4, 7 and 8 word, zero on 605 of 658 of the cond 1, 2, 5 and 6 words (606 of 659 in 6.5), all 3152 conditional targets are records, 13 of 14 cond 11 words write RE3 `0x5f`, the 547 control `0x3f` words that ALUA does not read all have MPYA = 4 (556 in 6.5), and the 81 control `0x34` fields are the same one-hot codes. The branch sites on the lines the open questions name are the same in both builds: `0x63` 33, `0x68` 2, `0x69` 83, `0x6b` 72, with the same (condition, line) pairs for conditions 4 and 8. So the second build supplies no new site and no second answer for cond 4, cond 8 or the negative cases. Established.

**The older diagnostic image.** The R3000 Indigo's `ide` (`hw_field.ide`, in 5.3) carries a diagnostic GE7 image of 2187 records against 2203 in the 5.2 R4000 `ide`, and an HQ2 diagnostic image of 976 against 977. After masking branch targets the two GE7 images differ in nine runs, starting at 19, 34, 36, 1018, 1161, 1173, 1199, 1204 and 1205 (IP20 numbering): the earliest are the test-driver prologue, the later ones the Z-plane token routines. The older slot 52 and slot 53 routines (GE7 1153 and 1185, 38 words against 46) are other words doing the same job: the engine writes the same RE3 values from both for the host words 1 and 0 (`0x60`, `0x61`, `0x65`, `0x66`) and 2 and 0 (`0x6b`), a second build agreeing on the Z-plane known answer. The R4000 routines open with two ALU compare words (FALUOP `0x3c` and `0x3e`, BRCOND `0xe`) that the older ones lack; the RE3 writes agree regardless. Established for the agreement; no select is settled by it.

**The kernel console images.** The 5.3 and 6.5 `gr2_tpucode.o` objects carry byte-identical console images (264 GE7 and 129 HQ2 records), and the 5.3 R3000 `ide` carries the same pair. The kernel's own strings name them "IP12/GR2 PROM GE Microcode" and "IP12/GR2 PROM HQ Microcode"; they are not the 4.0.5D/4.0.5G PROM's pair (301 and 149 records) nor the R4000 `ide`'s (308 and 150). Established.

## Review (2026-11-23)

Independent check of the decode above, against the PROM 4.0.5D images, `hq2.bin`, `ge7.bin` and the four images in `ide.IP20` (hashes as
in [references/binaries.md](../../references/binaries.md)), with a separate parser and field decoder written from the format and field map,
not from the tools. The in-place corrections made by this review are listed first; the rest of the claims were reproduced.

**Corrected in the text above.** The HQ2 images are not in ascending order (only the GE7 images are); the diagnostic HQ2 image spans
addresses 0 to 1456 with four descents, not "512 to 1456 with one out of order"; INIT keeps start address 10 in the February 1993 console
images; `0x31` target-0 words at GE7 388 and 395 pass A idle and do no ALU work; ALUA = 5 never occurs with control `0x34` or `0x35`
(it occurs with `0x31`, `0x36`, `0x37`, `0x32`, `0x33`); the console set is eight tokens, not nine; FPASSA is 49%, not 45%, of `ge7.bin`
words; cond 12 and 13 words run to GE7 6666; the `0x20` operand counts; INIT also writes RE3 `0x70` and `0x71` (the address set in
[devices/re3](../../devices/re3/README.md) omitted them); RECTCOPY (409) is not in `hq2.bin`; the "20% against 24%" nearby-store
statistic is 24% against 24% (the conclusion, that it does not separate, stands). Two grades were lowered from established to inferred:
"`0x31` with target 0 is not a jump" (it is an argument from a working routine, not a reading) and INIT as the RE3 state initialiser.

**Reproduced, with the numbers.** Checksum rule over all 5642, 23429, 149, 301 records and the four diagnostic images (2203, 977, 308,
150), no exception. HQ2: 21 op values (top six 91.6%), 372 jumps, 245 calls, 20 returns (operand `0xa000`), 89 and 14 type-6/7 words, every
target on a populated word; 380 `0xd8` operands all GE7 records (88 end in `0x02`), 12 of 12 in the PROM image; `0x60`/`0x40` slot forms 788
and 146; the sixteen-word selector sweep (diagnostic HQ2 680 to 711, selector 0 to 7 under op `0x06` then `0x07`, target = address + 2) and the
`0x01` 8791 (`0x2257`) count; the diagnostic poll loop at 846 to 850. GE7: set-bit masks; ALUB never 5 (0 of 25933 words), ALUA = 5 on
4777; 3194 of 3194 cond 1 to 8 targets are records, and no control `0x31` word has cond 1 to 8; BRCOND zero on 0 of 2535 words with cond 3, 4,
7, 8 and on 606 of 659 with 1, 2, 5, 6; cond 11 with `0x5f` on 13 of 14. RAM0AD (C4[30:24]) values in each console routine are a subset of
the slots its HQ2 token reads, for all eight, and equal for seven (DRAWCHAR never reads slot 2); C4[31] is never set in them. FloatOps
arms 1543 to 1548 are IADD, ISUB, IMPY (FMPYOP 0), FADD, FSUB, FMPY (FMPYOP 1) in the host's operation order, and every ALU value that occurs in
`ge7.bin` is a named function. The function-name table in the diagnostic program is a ten-byte-stride array indexed by the function number
(FADD at index 3) and its flag-name table is a six-byte-stride array with zero at 1, neg at 2, pass at 4, so the host's numbering and the doc's
agree. The failure number loaded before each FpuCondTest operation is function + 27 in 44 tests plus MPASSA and MPASSB (immediates 45 and
46 with FMPYOP 2 and 3). Cond 8 is the only conditional in FpuCondTest (92 words). FIFOEN is C2[30]: 2414 and 124 words; READDR is non-zero
only on FIFOEN words in all 23429 (the strongest binary support for the pairing: the schematic is not needed). The write order of INIT,
PNT2I, RECTI2D, LINE2I, DRAWCHAR and RECTCOPY, and the diagnostic INIT's constants shifted by `0x2d` (`0x2c` for two), reproduce. C0[21]:
clear on 2810 words, 2610 of them SHFTSRC = 3 (108 of 20619 when set).

**GeSeqTest, re-derived.** A depth-first enumeration of every taken/not-taken choice of the cond 1 to 8 branches from 1354, treating a
cond-10 word with no target as the end, gives 14 terminal paths. Exactly one reaches the only SHFTSRC = 3 word (1421), with the outcomes in the table
above, and from there 1423 and 1431 not taken end at the failure stalls 1427 and 1434; the other 11 end at the early failure stalls (1372, 1379,
1391, 1415), at 1440 through the failure at 1438 (three) or at 1454 through the four early exits (four). Caveat: this rests on "a stall ends the routine". The failure blocks
sit inline in the main line (1369 branches over 1370 to 1373, and so on), so if a stall only paused, every failing run would resume at the next
main-line word and reach 1421. The claim is therefore inferred, which the page says; what the host reads is established: engine n's RAM0
window words 0 to 8 must not be `0xffffffff` and shared word 255 + n must be 1.

**SeedRom and SqRom.** The 128-word tables in the program's data (the two the host routines compare against) match both closed forms on all
128 entries each. A third 128-word table follows the SqRom table; it is a different rounding of a reciprocal and is not used by the two
tests read here.

**Added evidence.** The diagnostic program's microstore writer (`GE7URAMwr`, `0x8853652c`) masks the word with `0x03dfffff` before it writes
`+0x6a064`, not only when it reads back: the host never sends bit 21, which supports "not stored" but would equally fit a bit with another
use in that HQ2 register. ALUA = 5 with a non-zero field also occurs on `0x31` words at about the base rate (488 of 2144, 23% against 20% of
all words).

**Open items found.** (1) DRAWCHAR words 116 and 117 are `0x31` words with ALUA = 5 and IADD, so their fields (`0x3d`, `0x3c`) are also
ALU immediates; the pairing evidence for "`0x31` field is a state address" is therefore equivocal, and it stays inferred, with "not a
branch" the only part the measurements settle (325 of 2144 fields are not records, 22 are start addresses). The `0x1d`, `0x3c` and `0x3d`
values also land on records trivially, as low addresses are dense. RECTCOPY's `0x31` word (244) carries `0x8d`, a value no other routine
uses. (2) `0x32` (99 words, field values near 15200 and 16418) is a control value the page does not discuss and the stepper falls through
it; it is unchecked whether it is a jump. (3) The schematic-only rows of the field map (RAM1AD and RAM2AD widths, MPYA, MPYB, BUSEL, the
DEST fields, the sample strobes) have no binary support for their bit boundaries beyond top bits that no image sets (C3 bits 4 and 10, C2
bit 12, C1 bit 6); they are inferred and vendor-derived. (4) READDR observed values stop at `0x7e`: the eighth bit is never set.

**Dispositions (fifth pass, 2026-11-23).** (1) DRAWCHAR words 116 and 117 read shared words `0x3d` and `0x3c` into the ALU (ALUA = 5 on a `0x31` word reads the word its own field names), so they are readers of the position CMOV2I stores at `0x3c`, `0x3d`; the pairing is not equivocal
(`ge7-step.py run` reproduces the stores of COLOR and CMOV2I). RECTCOPY's `0x8d` is a constants-block index (PROM `C[0x8d]` = 0x17). (2) `0x32` does not jump: it loads a wide shared-RAM address
(fields below `0x8000`, 8 of 99 not records, never with a condition, followed by stores and the routine's stall). (3) MPYA and MPYB values 0, 1 and 3 now have binary support (FloatOps arms, FpuCondTest multiplier tests); BUSEL, REGWR with REGFDEST = 3, RAM1DEST = 1 and 3 and SHFTSRC = 3 have it too, as the data path
describes; the sample strobes, REGE and RAM2 still do not. (4) Unchanged.

## Review (round 5, 2026-11-23)

Independent check of the fifth pass (`8fb4d42` to `f5cfc9c`) against the four images in `ide.IP20` (Diagnostics 5.2, SHA-256 `744fdebc...df14`), the 4.0.5D PROM image, `hq2.bin` and `ge7.bin`, with a separate parser and field extractor written from the format and field map (not from `tools/`), plus the host routines in `ide.IP20` read from a disassembly. Grades stay **inferred**: every rule below is a fit to the diagnostic program's known answers, none is read from a document.

**Confirmed.**
- *Constants block behind ALUA = 5.* The diagnostic loader copies 512 words from image offset `0xfc` to shared word 0 (`gr2_load_ge_ucode`, same loop as the console loader). The 45 loads before FpuCondTest's tests (41 ALU functions, 4 multiplier operations) hold the function number at `C[index]`, and the word that follows the load runs exactly that function (41 of 41; FMPYOP 0 to 3 for the four multiplier tests). `C[27 + n] = n` in the diagnostic block, so a 16-bit immediate would give the host `n + 27`; the host indexes its name table by the low byte of the record. The flag loads at 1571 to 1573 are `0x100`, `0x200`, `0x400`; the host decodes the record with `sra 8` for the flag name and `andi 0xff` for the function (`gr2_FpuCondTest`), and the failure writers at 1900, 1903 and 1906 OR in registers 9, 10 and 11, which the register-write delay of one word fills with those three values. GeSeqTest register 1 is `C[0x1c]` = 1; SeedRom and SqRom load `C[0x5d]` = 128 (words 918 and 934) as their counter, one pass per count; GeFifoTest loads `C[0x62]` = `0x800`, `C[0x25]` = 10, `C[0x1d]` = 2. INIT's `0x6d`, `0x73` and `0x74` values (`0xffff01`, `0x27f800`, `0xffc00`) cannot be 16-bit immediates.
- *Result taps.* Register write N+1, shared store and RE write N+2, flags N+2, as stated. Mutating each tap in `Engine` breaks known answers (register write: four tests; RE write: three; flags: two; store: one, COLOR and CMOV2I only, because FloatOps' idle word repeats the arm's result). FloatOps' dispatch is the discriminating site for the flag delay: with one word the first branch would test operation 2, not 1.
- *Statistics.* Control classes reproduce (`0x3f`: 3142 words, max `0xfb`; `0x31`: 2144, max `0x380`; `0x32`: 99, max `0x7d00`, 8 not records; `0x33`: 16, max `0x7fdf`; `0x34`: 81 words, fields 2, 4, 8, 16; `0x36`/`0x37` targets: all of 3194 conditional targets are records; BRCOND zero on 0 of 2535 and 606 of 659). 167 of 263 routine starts sit two words after a stall (a chance rate would give 3 to 4; 1.3% of words follow a stall at that distance) and 251 of 263 reach a stall by falling through. `diag_finish` clears `+0x6a04c`, writes slot 1, waits and tests bit 1 of `+0x6a040`; the routine at 48 ends in a `0x34` word with field 8 and a stall.
- *RE3 span path.* GeFifoTest and PNT2I, worked by hand: with a two-word delay the writes are `0x00` = `0x8000`, `0x08` = 0, `0x20`, `0x21` = (x, y + `0x800`) << 11, `0x22` = (x + 10 + `0x800`) << 11, `0x40` to `0x42` = the colour words << 11, `0x5f` = 2. With a one-word delay they are not (unshifted y, colour at `0x5f`).
- Select 7 as the result two words back: Ram12Test's 154 OR words (A = 7, B = 6) each follow an ISUB, which is an accumulate-and-diff alternation. No test in `selftest` covered it (replacing select 7 by "previous result" left every check passing); a check now does.

**Corrected.** "All but 221 have condition 0" counted all 4777 ALUA = 5 words; for the 3233 with a field it is 3026. The 1499 words with ALUA = 5 and field 0 are the control `0x36`/`0x37` ones; with the 39 `0x31`, 3 `0x21` and 3 `0x38` it is 1544. The INIT agreement is "identical at nine RE3 addresses": two of the nine (`0x61`, `0x62`) are zero, so seven non-zero values agree between the PROM image and the diagnostic image (`0x60`, `0x64`, `0x66`, `0x6d`, `0x72`, `0x73`, `0x74`); the console images of the PROM and of `ide.IP20` agree with each other at eleven of thirteen (`0x6a` and `0x7d` differ), and the diagnostic image writes `0x6a` and `0x7d` itself (the model gives `0x807d` and `0x7d`), so `0x6a` is "PROM only" only in the sense of its value. The superseded statements in the first review above (function + 27 as an immediate, constants "shifted by `0x2d`") stand as history; the data path section is current.

**Added.** MPYA = 4 is on all 556 control `0x3f` words with a field that ALUA does not read (and on 3889 words in all), so the multiplier A operand has the same shared-word select at value 4; no known answer uses it (the `Engine` now models it as that shared word, without a check). MPYB = 4 and 5 (199 words, all FMPY; 27, all MPASSB) differ between the SeedRom and SqRom routines and nowhere else, so they are the seed and square-root ROM outputs. Both inferred; checks added.

**Grade notes.** (1) The flag rules for `0x63`, `0x6b`, `0x68`, `0x69` are positive-only fits (see the note after the flag table). (2) Reading R2 misses the cond 4 and cond 8 branches on `0x62` and no known answer supports the sense of cond 4 at all; the sites that fit are cond 3 and 7 on `0x62` and cond 8 on lines other than `0x62`. The sense of conditions 4 and 8 stays inferred, weaker than conditions 3 and 7. (3) "The stall ends a routine" rests on the start statistic and the host's finish flag; the inline GeSeqTest stalls are consistent with it, not proof. (4) The role of `0x22` as the end x holds for GeFifoTest only: PNT2I writes y << 11 there, so the address is not shown to be an end x. (5) Field names and widths from the GR4 schematic remain vendor-derived: the checks above support the positions of RAM0AD, FALUOP, ALUA, ALUB, REGWR, REGFDEST, SHFTSRC, FIFOEN, READDR, FMPYOP, BRCOND and the MPYA/MPYB values listed here; they say nothing about the bit boundaries of RAM2AD, MISCSRC, DSEL, the sample strobes or REGE. (6) Open: the state words `0x1d`, `0x3c`, `0x3d` against the constants block (see the shared-store paragraph).
