# Microcode: open questions

Each entry: the question, the routes tried, the next route. Answered questions move into [platforms/express/microcode.md](../platforms/express/microcode.md)
and are deleted here. Grades and provenance tags as in [AGENTS.md](../AGENTS.md). This continues item 1 and item 3 of [ge7.md](ge7.md); the
coordinator merges the index.

## 1. Which GE7 fields carry the data path and the raster-engine output?

Decoded so far: the 16-bit target in C0[15:0], the sequencer control and condition in C0[25:16], the input slot number in C4[31:24]
(it matches the slot sets of all console routines), a register select in C1 qualified by C2[31:30]. Not decoded: C2 low half, all of C3,
C4[23:0] and the second instruction form flagged by C2[25] (about 12% of words). The raster-engine write is not located. Routes tried:
field statistics over `ge7.bin`; the nine console routines against the HQ2 slot sets; comparison of the drawing routines with
CMOV2I, which draws nothing. Next: (a) the diagnostic program's `gr2_GeSeqTest` and `gr2_FloatOpsTest`, which exercise the sequencer
and the floating-point unit with known operands and may name the operations; (b) the RE3 command words the GL core sends for a clear
and for a point, found in the matching `ge7.bin` routines by following the HQ2 tokens (clear, point and line tokens in the pipeline table);
(c) the GR4 schematic sheets "GE7 Ucode & Shared RAM" and "2GE7 ASIC".

## 2. How is control flow resolved in the GE7 routines?

Chains such as the shared tail of the PROM image loop forever if every jump word is unconditional; the exit condition is not in
C0 or C1. Routes tried: jump-word statistics (5279 with C1 = 0, 630 with it nonzero). Next: decode the second instruction form
(item 1) and check whether C3 or C4 carry a condition select; read the diagnostic program's sequencer test for the condition names.

## 3. HQ2 ops outside the console set

The `0x80` control operand (`0x0611`, `0x0601`, `0x0641`, `0x1000`, ...), the `0x40`/`0x60` flag forms (`0x3661`, `0x1101`, `0x2600`),
type-6 and type-7 branches and the roughly 400 words with op values `0x01` to `0x06`, `0x10`, `0x22`, `0x81`, `0x90` to `0xd0`
are not decoded. Routes tried: value statistics over `hq2.bin`; the console routines. Next: follow the GL tokens that use them (the
vertex-attribute path in [pipeline.md](../platforms/express/pipeline.md)), where the operand count and the engine
distribution (ge7.md item 2) are visible in the sequence; the registers they write are the ones in [devices/hq2](../devices/hq2/README.md).

## 4. Header words and the second record half-word

The record trailer is a checksum (settled, see microcode.md). Still open from ge7.md item 3: the header words at `0x08` and `0x18`, and
the half-word at record offset 2 (always 1).
