# Microcode: open questions

Each entry: the question, the routes tried, the next route. Answered questions move into [platforms/express/microcode.md](../platforms/express/microcode.md)
and are deleted here. Grades and provenance tags as in [AGENTS.md](../AGENTS.md). This continues item 1 and item 3 of [ge7.md](ge7.md); the
coordinator merges the index.

## 1. What do the remaining GE7 fields select?

Located (see microcode.md, the field map): ALU function (FALUOP, C3[18:13]), multiplier operation, RAM0 address (the input slot),
register selects, raster-engine write enable and address. Not decoded: what ALUA, ALUB, MPYA, MPYB, BUSEL, DSEL, REGFDEST, SHFTSRC,
MISCSRC and the RAMn DEST fields choose, and how REGA to REGE and REGWR address the register file. Routes tried: the FloatOps arms
(operand selects are the same in the add and subtract arms, differ in the multiply arms), field statistics. Next: the Ram12, Shram,
SeedRom, SqRom and GeBus tests (their GE7 routines are known by HQ2 slots 2 to 7) as known answers for the RAM and register fields; read
the GR4 sheet 11 and the RE3 sheet 12.

## 2. How is control flow resolved in the GE7 routines?

Answered in microcode.md: C0[15:0] is also the ALU immediate (ALUA = 5), so the "jump chains" were immediates; `0x31` with target 0 falls
through; condition 10 is the stall; C0[21] is probably unstored. Still open:

- The polarity of conditions 2, 4, 6 and 8 (GeSeqTest fixes only 1, 5 and 3 with BRCOND `0x60`/`0x62`, and the four consistent outcome sets
  differ on the rest), and what flag each BRCOND value selects. Routes tried: `ge7-step.py paths` over GeSeqTest, FpuCondTest's flag names
  (zero, neg, pass). Next: the FpuCondTest routine (GE7 1562 on) pairs each ALU function with a flag and a failure record; step it with the ALU
  results of the immediates it loads to pin BRCOND to a flag.
- What a `0x31` word with a non-zero field does (PNT2I word 63 must not jump at once). Routes tried: PNT2I, GeFifoTest, field statistics
  (1624 of 2144 targets are below 256, 272 equal 141). Next: the HQ2 side of a console draw, or a trace of RE3 writes.
- What conditions 9, 11, 12, 13, 14 and 15 do and what writes the shared pass word (1) at the end of GeSeqTest. Routes tried: their
  position in FloatOps' tail, FpuCondTest's failure pad, GeSeqTest's end. Next: the same routines with the HQ2 operands of slots 12 and 57.

## 2a. RE3 command data

Written addresses per routine are in microcode.md (the PROM image's seven console routines and GeFifoTest). Open: the meaning of each address and
the exact data source of a write (same-cycle ALU result is inferred, previous-word result not excluded). Routes tried: GeFifoTest known answer,
console routines, INIT constants. Next: schematic sheet 12 (vendor-derived, so inferred at best), and the Ram12, Shram, SeedRom, SqRom and GeBus
tests for the RAM1/RAM2 and register-file destination fields (not yet read: their routines start at GE7 395, 388, 916, 932, and 948).

## 3. HQ2 ops outside the console set

Partly answered (microcode.md, "HQ2 words beyond the console set"): `0x80` words are status masks that the following type-6 or
type-7 branch tests, the diagnostic image uses an older operand form. Open: which `0x80` bit is which, the `0x20` operands other than
`0x2000`, the other `0x40`/`0x60` flag forms, the ops `0x01` to `0x06`, `0x10`, `0x22`, `0x81`, `0x90` to `0xd0`. Next: follow the GL
tokens that use them (vertex-attribute path in pipeline.md); the diagnostic HQ2 image's 20 op values as known answers.

## 4. Header words and the second record half-word

The record trailer is a checksum (settled, see microcode.md). Still open from ge7.md item 3: the header words at `0x08` and `0x18`, and
the half-word at record offset 2 (always 1).
