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

Partly answered: condition 10 is the stall at idle; BRCOND (C3[26:19]) selects GE7 results for conditions 3, 4, 7, 8. Open: the
polarity of conditions 1 to 8, what control `0x3f` and `0x31` do when the target is not wanted (the PROM chain 65, 125, 126, 127 has
no exit; the FloatOps routine's second word is a `0x31` word that must fall through), and C0[21]. Routes tried: the GeSeqTest
and FloatOps structure; BRCOND statistics. Next: step GeSeqTest's straight-line program with candidate polarities against its
required outcome (nine RAM0 words not -1, shared flag 1).

## 2a. RE3 command data

READDR values per console routine are listed in microcode.md; which register each is and what supplies the data is not known. Routes
tried: GeFifoTest known answer (a ten-pixel span at x = 100 from five words), PNT2I/RECTI2D/LINE2I word comparison. Next: schematic
sheet 12, the data source fields (DSEL, REGFDEST), and the RE3 window offsets in devices/re3.

## 3. HQ2 ops outside the console set

Partly answered (microcode.md, "HQ2 words beyond the console set"): `0x80` words are status masks that the following type-6 or
type-7 branch tests, the diagnostic image uses an older operand form. Open: which `0x80` bit is which, the `0x20` operands other than
`0x2000`, the other `0x40`/`0x60` flag forms, the ops `0x01` to `0x06`, `0x10`, `0x22`, `0x81`, `0x90` to `0xd0`. Next: follow the GL
tokens that use them (vertex-attribute path in pipeline.md); the diagnostic HQ2 image's 20 op values as known answers.

## 4. Header words and the second record half-word

The record trailer is a checksum (settled, see microcode.md). Still open from ge7.md item 3: the header words at `0x08` and `0x18`, and
the half-word at record offset 2 (always 1).
