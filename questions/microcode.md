# Microcode: open questions

Each entry: the question, the routes tried, the next route. Answered questions move into [platforms/express/microcode.md](../platforms/express/microcode.md)
and are deleted here. Grades and provenance tags as in [AGENTS.md](../AGENTS.md). This continues item 1 and item 3 of [ge7.md](ge7.md); the
coordinator merges the index.

## 1. What do the remaining GE7 fields select?

Located (see microcode.md, the field map): ALU function (FALUOP, C3[18:13]), multiplier operation, RAM0 address (the input slot),
register selects, raster-engine write enable and address. Not decoded: what ALUA, ALUB, MPYA, MPYB, BUSEL, DSEL, REGFDEST, SHFTSRC,
MISCSRC and the RAMn DEST fields choose, and how REGA to REGE and REGWR address the register file. Routes tried: the FloatOps arms
(operand selects are the same in the add and subtract arms, differ in the multiply arms), field statistics. The Ram12, Shram, SeedRom, SqRom and GeBus routines are read (microcode.md): they give ALUA = 1 as the RAM1 output and the ROM tables, not the
register-file or select roles. Next: step Ram12 (395 to 913) with a data model, read the GR4 sheet 11 and the RE3 sheet 12.

## 2. How is control flow resolved in the GE7 routines?

Answered in microcode.md: C0[15:0] is also the ALU immediate (ALUA = 5), so the "jump chains" were immediates; `0x31` with target 0 falls
through; condition 10 is the stall; C0[21] is probably unstored; conditions 3, 4, 7 and 8 carry a BRCOND flag select and 1, 2, 5, 6 do not;
condition 8 is taken when its flag is clear and `0x64`/`0x69` are the zero flag; GeSeqTest has exactly one passing path (the shared store at
1421); the shared-RAM stores are the SHFTSRC = 3 words between a cond 14 word and the next cond 15 word; and a `0x31` word with a non-zero field
is not a branch (the field is an address: the colour is `0x1d`, the position `0x3c`/`0x3d`). Still open:

- Which flag each BRCOND value selects beyond `0x64`/`0x69` (zero), and the polarity of 4, 7 and the fixed conditions 1, 2, 5, 6. Routes
  tried: FpuCondTest as a known answer (its second and third tests are `0x63`/`0x68` and `0x6b` and fit no sign predicate on the result
  once the registers are set by the zero tests: INEGA of an all-ones register and IPASSA of it both use `0x63`), GeSeqTest's table. Next:
  decode the register file and the operand selects 0, 1, 2, 6 and 7 (FloatOps and Ram12 give 0 and 1; the pipelined result bus and ALUB = 6 are
  open) and the FpuCondTest failure writers (1900, 1903, 1906), which show what the host's flag numbers 1, 2 and 4 are; then re-run
  `ge7-step.py paths` with flags for the 12 branches of the GeSeqTest table (the cond 3 versus cond 8/4 mismatch on `0x62` says the flag
  sampling stage matters).
- What the `0x31` access is: load or store, which RAM, and how data returns (ALUA/ALUB = 6 a word or two later). Routes tried: the writer/reader pairing of
  COLOR, CMOV2I and the drawing routines (microcode.md), statistics for a nearby SHFTSRC = 3 word (not separating). Next: a write
  trace of the shared RAM during COLOR then PNT2I, or the HQ2 side of a console token.
- What conditions 9, 12 and 13 do, and whether cond 11 is the FIFO-drain wait (13 of 14 sit on the `0x5f` flush write). Routes tried:
  FpuCondTest's failure writers (cond 9 then a store), GeSeqTest's tail, the next-word statistics. Next: cond 9 against a known store address
  (the failure record at 256 on) once the register file is decoded.

## 2a. RE3 command data

Written addresses per routine are in microcode.md (the PROM image's seven console routines and GeFifoTest). Open: the meaning of each address and
the exact data source of a write (same-cycle ALU result is inferred, previous-word result not excluded). Routes tried: GeFifoTest known answer,
console routines, INIT constants. The diagnostic image's own INIT (GE7 1004 to 1062) writes the same addresses with constants that are the PROM's
shifted by `0x2d` (`0x2c` for two), so they are build-relative pointers or identifiers, not hardware reset values; the Ram12, Shram, SeedRom, SqRom
and GeBus routines gave no RE3 information. Next: schematic sheet 12 (vendor-derived, so inferred at best).

## 3. HQ2 ops outside the console set

Partly answered (microcode.md, "HQ2 words beyond the console set"): `0x80` words are status masks that the following type-6 or
type-7 branch tests (`0x0060` is the poll mask); the ops `0x01` to `0x07` with a branch-shaped operand are conditional branches whose
bits 15:13 select one of eight conditions; bits 9:5 of `0x40`/`0x60` are the slot and bits 4:0 a small number that is not part of it. Open: which
`0x80` bit is which, which condition each selector and op number tests, the meaning of bits 4:0 and 15:10 of the read words, the `0x20`
operands other than `0x2000` and `0x0000` (`0x6464` and 18 more), and the effects of `0x10`, `0x22`, `0x81`, `0x90` to `0xd0` (they appear only
in the diagnostic HQ2 image's self-test sequences and in `hq2.bin` as about 400 words). Routes tried: the ShramTest, GeFifoTest and FloatOps
walks, operand-field statistics, the sixteen-word selector sweep. Next: the HQ2 register map (devices/hq2) to name status bits 5 and 6, and the
GL tokens that use the rarer ops (vertex-attribute path in pipeline.md).

## 4. Header words and the second record half-word

The record trailer is a checksum (settled, see microcode.md). Still open from ge7.md item 3: the header words at `0x08` and `0x18`, and
the half-word at record offset 2 (always 1).
