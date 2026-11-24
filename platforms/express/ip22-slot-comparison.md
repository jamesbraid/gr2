# FIFO token slots: Indigo against Indy and Indigo2 Express

Does the GL core of the Indy and Indigo2 Express (IP22) use the same HQ2 FIFO tokens as the Indigo's (IP12/IP20)? Yes: the two
GL cores store the same offsets, in the same order, from the same functions. The Indigo table is in
[pipeline.md](pipeline.md#what-the-gl-core-pushes); the slot encoding is in [pipeline.md](pipeline.md#fifo-token-encoding).

Provenance: every fact is `[binary]` (shipped IRIX 6.5 base-set files, a software expectation), graded inferred unless stated.

## Binaries

All from the IRIX 6.5 base software set, under `usr/gfx/`.

| File | Build | SHA-256 |
|---|---|---|
| `arch/IP12GR232/libGLcore.so` (Indigo) | n32, DWARF | `b6731da1b4422e1ea1e8fbe841af2e05989d4c3022d9c8b8143a53187f67de9a` |
| `arch/IP22GR2NG132/libGLcore.so` (Indy, Indigo2) | n32, DWARF | `fc008c220940a7ce041274e01ba8ec9655b07f84c24429fb2158de3f98348c67` |
| `arch/IP12GR2/libGLcore.so` (Indigo) | o32, stripped | `8e77dae21260c41c8f7587519fa916d5793a6bff698c829ba8381936f24c7222` |
| `arch/IP22GR2NG1/libGLcore.so` (Indy, Indigo2) | o32, stripped | `a6cddc8c5b17827f40c7f4be5b643d0f783286f44bb3c475b00172bf3f39ba2a` |
| `ucode/hq2.bin` | one copy for all | `0c1fbe18d1b451ee32fb81afa4dd85aa86beeee2c5f7fc8b2e33e79e4375fc94` |
| `ucode/ge7.bin` | one copy for all | `085d9e923476750673146a517df5847636e7165fb8e7cb4723f7eef07b114729` |

Context only: `arch/IP19GR2EV`, `IP21GR2EV` and `IP25GR2SH` `libGLcore.so` (SHA-256 `6b8813da...`, `a28c0fbf...`, `8e4a6cdd...`).

## Method

Per library, a linear pass over `.text` tracks register values through `lui`, `ori`, `addiu`, `addu`, `or` and moves (dropping
them on any other write and across calls) and records every load or store whose effective address falls in `+0x40000` to `+0x5ffff`.
Function names come from the DWARF subprograms of the n32 builds; the stripped o32 builds have only exported names, so a hit
is attributed to the nearest exported function before it (approximate, marked `~`). Run on the Indigo n32 library it reproduces 140
of the 141 stored addresses in the Indigo table. The missing one is `+0x4ec00` (the tracker finds no store, as the table's review
already noted). It adds `+0x42218` (`LoadSpotLUT`, 32 stores), a gap the review also found.

Two kinds of hit are not fixed tokens: `RenderBitmap` stores at `+0x42000` through a register that holds `(index << 2) + 0x40000`,
so that address is a computed slot, not slot 0 (agrees with the review's finding about the table's first row); and `ReadColor` loads
from `+0x40000`.

## Result

The event streams (address, access width, order) are compared in `.text` order:

| Pair | Events | Differences |
|---|---|---|
| Indigo n32 against IP22 n32 | 1229 (1222 stores, 7 loads) | none |
| Indigo o32 against IP22 o32 | 1232 (1228 stores, 4 loads) | none |

So for the GR2 drawing path:

- **Slot numbering: identical.** Every token offset, every attribute-bit variant (bit 16, bits 15:12), every data-port store
  (`+0x4277c` and its attribute forms) and the order of stores inside each function match. The GL entry points did not move
  (function sets per offset are equal across the n32 pair, 0 differences). No token exists on only one side.
- **Modifier bits: used the same way.** Slot 99 vertex forms `+0x4298c`, `+0x4498c`, `+0x4698c`, `+0x5298c`, `+0x5498c`, `+0x5698c`,
  colour slot 386 (`+0x48608`, `+0x4a608`, `+0x58608`, `+0x5a608`) and index slot 254 (`+0x4e3f8`, `+0x5e3f8`) appear in both.
- **Same GE7 routine reached:** the platforms load the same `hq2.bin` and `ge7.bin`, so a slot reaches the same routine on both
  (routine per slot: the Indigo table in `pipeline.md`).

The slots that differ, therefore: none between the platforms. The only difference found is between the n32 and o32 builds, and
it is the same on both platforms:

| Slot | Offset | Indigo | IP22 | Note |
|---|---|---|---|---|
| 17 | `+0x40044` | stored by `PassDepthMask`, `SlowRenderBitmap`, `Rectsv` in the o32 build (approximate names) | same | the n32 build of `PassDepthMask` stores `+0x42028` (slot 10) instead; the other two n32 functions were not traced. A build difference, not a platform one |

## Microcode

Neither platform ships its own microcode in the base set: `usr/gfx/ucode` holds one `hq2.bin` and one `ge7.bin`, and they are the Indigo's
(hashes above). The kernel's built-in console image `gr2_tpucode.o` is byte-identical in the `IP20boot` and `IP22boot` copies of
`gr2.a` (SHA-256 `04930f710d1f1278771857d35e15fed789922506bb831abcea9e79d01aaa0667`). The PROM-embedded images of an Indy or
Indigo2 were not read; no IP22 PROM was in scope.

## What does differ

- The IP22 libraries are a superset: the n32 build adds 30 `npt_*` compilation units (the NG1 Newport path, a different device,
  not HQ2 FIFO traffic; the scan finds no FIFO-window store the Indigo library lacks) and a few `mips_vclip` and `mips_vertex` routines. Every `gr2_*` unit of the Indigo
  library is present. Non-FIFO code in the shared units differs (context layout), which is not examined here.
- The IP22 kernel `gr2.a` adds `gr2_corona_i2c.o` and has different `gr2.o`, `gr2_init.o`, `gr2_retrace.o` and `gr2_tport.o`
  (SHA-256 of the archives: IP20 `f05d4700...`, IP22 `80707bc8...`). Registers and board setup are the host-contract question, not a
  token question.
- Everest and Challenge GL cores (`IP19`, `IP21`, `IP25`) form their FIFO addresses differently (base-register forms plus a large displacement,
  for example colour stored at `+0x4704c`), so their tokens are not comparable with this scan. Not examined further.

## Kernel gr2.a and the +0x6c1c0 window

Only `gr2_corona_i2c.o` in the IP22 kernel `gr2.a` (SHA-256 `637b6487...`) reaches `+0x6c1c0` to `+0x6c1fc`, and only through
an index: `lui 0x70000`, plus an index register, minus a 16-bit displacement. So the address is `0x6c1c0` plus the index, not a
fixed offset. `gr2_i2cProbe` stores `0x00`, `0x55` and `0xaa` at `0x6c1e0` plus the index and reads back `0x55` and `0xaa` to
compare them. Two unnamed routines in the same object load the bytes at `0x6c1c0` and `0x6c1c4` (`.text` `0x98` to `0xb8`) and store
to them (`.text` `0xcc` to `0x120`). The other six members (`gr2.o`, `gr2_init.o`, `gr2_retrace.o`, `gr2_tport.o`, `gr2_dma.o`, `gr2_tpucode.o`) have no
access in the window. This is a scan of the archive's code with constant tracking, not a run; the index's source (the probe's
first argument) and its callers are outside the archive and were not checked.

## Open

- The IP22 PROM images and the Indy and Indigo2 board registers are not covered; a different GE count or board revision on IP22 would
  show in the host contract, not in the GL token set.
- The `+0x420f4` to `+0x42114` stores the Indigo review reports were not reproduced by this scan on either platform; the question is open on both.
