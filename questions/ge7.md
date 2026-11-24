# GE7: open questions

Each entry: the question, the routes tried, the next route. Answered questions move into [devices/ge7](../devices/ge7/README.md) and are
deleted here. Grades and provenance tags as in [AGENTS.md](../AGENTS.md).

## 1. What do the microword fields mean?

Partly answered: sequencer target, control and condition, and the input slot field are in [microcode.md](../platforms/express/microcode.md).
The rest (data path, RE3 output) is [microcode.md](microcode.md) items 1 and 2. The GR4 schematic sheets "GE7 Ucode & Shared RAM"
and "2GE7 ASIC" remain a route (poor text layer, manual read).

## 2. How does the HQ2 spread primitives over the engines?

The Technical Report says the command engine delegates one primitive to each engine; no binary read shows the policy. Routes tried:
`NUMGE` writes (count only); every GE slot access in the PROM, kernel driver and diagnostic program (all are probe, load or revision
reads, none selects an engine). Next: the HQ2 microcode routine reached from the vertex-attribute entries of `hq2.bin`, which holds the
engine counter if there is one (this is the HQ2 page's decode).

## 3. Header words the loader does not read

`ge7.bin` header words at `0x08` (`0xe0`) and `0x18` (`0xfd`, `0xeb` in the PROM image) and the half-word at record offset 2 (always 1).
The trailing record half-word is settled: a checksum (see [devices/ge7](../devices/ge7/README.md)). Routes tried: comparison of both images;
values against counts in the file (the `0x18` word matches the number of constants in use). Next: compare against a different `ge7.bin` build
(other IRIX releases have different microcode builds in the Library).

## 4. Slots 1 to 7 and the unprobed offsets of slot 0

Does an absent slot raise a bus error, read zero or echo? Do the load window and the revision register exist in each populated slot
or only slot 0? What are the offsets `+0x683f8` to `+0x683ff` and the storage between the probed offsets and the window? Routes
tried: every access to `+0x68000` to `+0x69fff` in the PROM, the kernel objects and the diagnostic program. Next: the diagnostic
program's per-engine tests (`gr2_GeBusTest`, `gr2_GeFifoTest`, `gr2_GeSeqTest`, `gr2_FloatOpsTest`, `gr2_Ram12Test`, `gr2_ShramTest`,
`gr2_SeedRomTest`, `gr2_SqRomTest`) read in full: their names suggest the per-engine RAM, FIFO and ROMs they exercise.
