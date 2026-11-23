# GE7: open questions

Each entry: the question, the routes tried, the next route. Answered questions move into [devices/ge7](../devices/ge7/README.md) and are
deleted here. Grades and provenance tags as in [AGENTS.md](../AGENTS.md).

## 1. What do the microword fields mean?

The loader stores 128 bits per word across five registers and `ge7.bin` holds 23429 words, but no field (op code, operand selects,
immediate, branch target) is decoded. Routes tried: the loader and its verify masks; the image header and record layout; the
HQ2 dispatch from each FIFO token to a start address (which names the entry of 233 routines and the size of each); the constants block
contents; the published Elan TR (architecture only, no instruction set). Next: decode the nine console routines in the PROM image
(301 words), whose effect is known from the PROM caller (set colour, move, draw a point, box, line, character, copy): the
operand-select and immediate fields show up as the values that change with the operand, and the page layout (code starts two words into
each 256-word page) fixes the branch field width. Then extend to the matrix and state routines. The GR4 schematic sheets "GE7 Ucode &
Shared RAM" and "2GE7 ASIC" are the other route; their text layer is poor and the sheets need a manual read.

## 2. How does the HQ2 spread primitives over the engines?

The Technical Report says the command engine delegates one primitive to each engine; no binary read shows the policy. Routes tried:
`NUMGE` writes (count only); every GE slot access in the PROM, kernel driver and diagnostic program (all are probe, load or revision
reads, none selects an engine). Next: the HQ2 microcode routine reached from the vertex-attribute entries of `hq2.bin`, which holds the
engine counter if there is one (this is the HQ2 page's decode).

## 3. Header and record fields the loader does not read

`ge7.bin` header words at `0x08` (`0xe0`) and `0x18` (`0xfd`, `0xeb` in the PROM image), the half-word at record offset 2 (always 1) and
the half-word at the end of each record (varies). Routes tried: comparison of both images; values against counts in the file (the
`0x18` word matches the number of constants in use). Next: compare against a different `ge7.bin` build (other IRIX releases have
different microcode builds in the Library) to see which fields track the content.

## 4. Slots 1 to 7 and the unprobed offsets of slot 0

Does an absent slot raise a bus error, read zero or echo? Do the load window and the revision register exist in each populated slot
or only slot 0? What are the offsets `+0x683f8` to `+0x683ff` and the storage between the probed offsets and the window? Routes
tried: every access to `+0x68000` to `+0x69fff` in the PROM, the kernel objects and the diagnostic program. Next: the diagnostic
program's per-engine tests (`gr2_GeBusTest`, `gr2_GeFifoTest`, `gr2_GeSeqTest`, `gr2_FloatOpsTest`, `gr2_Ram12Test`, `gr2_ShramTest`,
`gr2_SeedRomTest`, `gr2_SqRomTest`) read in full: their names suggest the per-engine RAM, FIFO and ROMs they exercise.

## 5. Revision register: resolved, kept for the index

`+0x683f4` bits 7:5 (kernel driver and PROM) against NetBSD's `+0x680fc` bits 7:4: answered in the GE7 page in favour of `+0x683f4`.
Question 3 in [README.md](README.md) can be deleted by the coordinator.

## 6. Adjacent: HQ2 revision source (for the HQ2 page)

The PROM probe stores `(word at +0x6a040) >> 23` as the HQ2 revision byte (`0xbfc0ecec`); the kernel probe stores
`(half-word at +0x6a06c) >> 16` in the same record byte (`gr2_init.o` `0x108`). NetBSD agrees with the PROM. This bears on question 1 in
[README.md](README.md) and on the HQ2 revision guess; recorded here because it was found while settling the GE7 revision.
