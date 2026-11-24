# Microcode: open questions

Each entry: the question, the routes tried, the next route. Answered questions move into [platforms/express/microcode.md](../platforms/express/microcode.md)
and are deleted here. Grades and provenance tags as in [AGENTS.md](../AGENTS.md). This continues item 1 and item 3 of [ge7.md](ge7.md); the
coordinator merges the index.

## 1. What do the remaining GE7 fields select?

Mostly answered in [microcode.md](../platforms/express/microcode.md#the-data-path) (operand selects 0, 1, 3, 4, 5, 6, 7, the register file with REGC and REGD on the ALU and REGA and REGB on the multiplier, REGWR with
REGFDEST = 3, the constants block behind ALUA = 5, the result taps, RAM0DEST = 3 and RAM1DEST = 1 and 3). Still open, with the routes tried:

- **Select 7 and select 4.** Select 7 is the result two words back in Ram12Test's OR chain, but RECTI2D's min/max pairs and DRAWCHAR's loop read it where the RAM0 word named by the previous word fits, and SeedRom and SqRom take the ROM output
  with it. Select 4 is the previous result in every known answer, but a held result register (RESEN) is not excluded and RECTI2D's `FADD A = 4, B = 6` words would separate them. Routes tried: the engine on RECTI2D with both readings (the
  coordinates come out as nonsense under the two-words-back reading, as plausible float min/max under the RAM0 reading but with doubled sums under select 4 = previous result). Next: GeBusTest and Ram12Test with select 2, the RAM2 path, and a run of LINE2I and DRAWCHAR once 7 is fixed.
- **RESEN, REGFDEST 1 and 2, REGE, REGSEL, RAM2DEST, RAM0DEST and RAM1DEST values other than 1 and 3, MISCSRC, DSEL.** No known answer needs them. Routes tried: field statistics (REGFDEST 1 and 2 occur 295 and 395 times in `ge7.bin`
  and the diagnostic image's FpuCondTest tail, words 1911 to 1913, uses 2 with RAM0AD values 0x20 and 0x40). Next: the other diagnostic tests (SpfCondTest's table compare) and the `ide` register-file test sequences.
- **Where the SeedRom and SqRom values enter the data path.** The loops run 128 passes (checked) and store `ALUA = 7` shifted and masked; the ROM address is the counter shifted left 16. Next: decode the ROM select.

## 2. How is control flow resolved in the GE7 routines?

Mostly answered in microcode.md: conditions 1 and 5 always branch and 2 and 6 never; conditions 3, 4, 7 and 8 branch on a flag line two words behind, the lines `0x62`, `0x63`, `0x64`, `0x68`, `0x69`, `0x6b` are decoded; `0x31`, `0x32` and `0x33` carry a
shared-RAM address (`0x32` does not jump); the stall ends a routine, with the finish-flag evidence. Still open:

- **The sense of the branches, and two GeSeqTest sites.** Two readings fit the 92 FpuCondTest tests; the one that also fits the SeedRom and SqRom loops and the `0x60` and `0x77` sites (all four conditions branch when the line is high,
  five lines active low) misses the cond 8 and cond 4 branches on `0x62` at 1403 and 1410. Routes tried: both readings on all sites, the passing-path enumeration with and without stalls ending the routine, the sampling stage
  (N-2 for conditions 3, 7, 8, 4 from the compare-operation statistics). Next: a second known answer for cond 4 and cond 8 on `0x62` (the full image has 17 and 5 uses), the HQ2 side of a stalled routine.
- **What `0x60`, `0x61`, `0x77`, `0x6f`, `0x67` and the values above `0x77` select.** `0x60` and `0x61` follow ISUB, IRSUB and FSUB at N-2 and look like compare outcomes (less, greater); `0x6f` follows IPASSA (73 of 144 at N-2); `0x67` follows AND
  (72 of 86). Next: simulate more of the full image with the engine and look for which values make a loop terminate.
- **What conditions 9, 12 and 13 do, and whether cond 11 is the FIFO-drain wait** (13 of 14 sit on the `0x5f` flush write). Cond 9 is not needed by the store counter (CMOV2I has none); in FpuCondTest the cond 9 word is also the IADD
  that bumps the failure count. Next: cond 12 and 13 at GE7 6526 to 6666 with the engine.
- **The control `0x35` words** (63, fields up to `0xf280`) and `0x33` (16, up to `0x7fdf`), and the one-hot `0x34` codes against the three status bits (8 raised the host's finish flag 2; 2 and 4 follow DMA tokens whose host poll
  reads bit 2). Routes tried: statistics of fields and contexts, the host's `diag_finish`, `pix_dma` and DMA tests. Next: HQ2 register decode of the finish flags in [devices/hq2](../devices/hq2/README.md).

## 2a. RE3 command data

Answered for the span and point paths and INIT: the values are in [devices/re3](../devices/re3/README.md#addresses-the-microcode-writes) (start x, y and end x, the colour words, `2` to `0x5f`, the INIT table). Open: the meaning
of each address beyond those roles (`0x00`, `0x08`, `0x23` to `0x25`, `0x5e`, `0x67`, `0x6f`, the bits of the INIT words), and the data of RECTI2D, LINE2I, DRAWCHAR and RECTCOPY, which need item 1's select 7 and select 4. Routes tried: GeFifoTest known
answer, the console routines run on the engine, INIT in two builds. Next: schematic sheet 12 (vendor-derived, so inferred at best), and the float form of RECTI2D's coordinates against the RE3 floating-point inputs if the TR's iteration description gives them.

## 3. HQ2 ops outside the console set

Partly answered (microcode.md, "HQ2 words beyond the console set"): `0x80` words are status masks that the following type-6 or
type-7 branch tests (`0x0060` is the poll mask); the ops `0x01` to `0x07` with a branch-shaped operand are conditional branches whose
bits 15:13 select one of eight conditions; bits 9:5 of `0x40`/`0x60` are the slot and bits 4:0 a small number that is not part of it. Open: which
`0x80` bit is which, which condition each selector and op number tests, the meaning of bits 4:0 and 15:10 of the read words, the `0x20`
operands other than `0x2000` and `0x0000` (`0x6464` and 16 more), and the effects of `0x10`, `0x22`, `0x81`, `0x90` to `0xd0` (they appear only
in the diagnostic HQ2 image's self-test sequences and in `hq2.bin` as about 400 words). Routes tried: the ShramTest, GeFifoTest and FloatOps
walks, operand-field statistics, the sixteen-word selector sweep. Next: the HQ2 register map (devices/hq2) to name status bits 5 and 6, and the
GL tokens that use the rarer ops (vertex-attribute path in pipeline.md).

## 4. Header words and the second record half-word

The record trailer is a checksum (settled, see microcode.md). Still open from ge7.md item 3: the header words at `0x08` and `0x18`, and
the half-word at record offset 2 (always 1).

## 4. Where do the state words and the constants block meet?

The `0x31` field of COLOR, PNT2I, RECTI2D, LINE2I, DRAWCHAR and CMOV2I names shared words `0x1d`, `0x3c` and `0x3d` (colour and position, microcode.md), and the loader puts the constants block at shared word 0, so those words are constants-block entries `0x1d`, `0x3c`, `0x3d` (the attenuation-table values in the block). `ge7.bin` reads constants index `0x3d` as a constant (17 times, GE7 1849 to 1944 and 25395 to 25450) and the console routines at the end of the image name `0x3d` in a `0x31` word (36044, the CMOV2I position store). Either the `0x31` field addresses a memory other than the constants words, or those routines overwrite the table. Routes tried: the loader copy (512 words to shared word 0, both loaders), the `0x3f` reads of indices below `0x40` (only `0x3d` is read as a constant), the store addresses of the console routines. Next: find which routine reads index `0x3d` and whether it can run after CMOV2I; the cond 14 window base (host-visible results sit at shared word 255 on, past the 253 constants in use).

## 5. The multiplier selects

MPYA = 4 (3889 words of `ge7.bin`; all 556 control `0x3f` words whose field ALUA does not read) and MPYB = 4, 5 (199 FMPY words, 27 MPASSB words; SeedRom and SqRom differ in this field only) are read as 0 by the `Engine`. Routes tried: field statistics, the SeedRom/SqRom word-by-word difference. Next: a known answer that multiplies by a constant (the diagnostic image has none), then the float paths of RECTI2D, which use both.
