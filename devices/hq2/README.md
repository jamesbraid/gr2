# HQ2: the host-visible window

What the Indigo PROM and the IRIX IP20 kernel driver touch in the HQ2's part of the graphics slot, as offsets from the board
base (`0x1f000000`). This is the window only; the HQ2's instruction set, token numbering and DMA engine are not covered. No
`registers.toml` yet: the grades below are not yet settled enough to generate from. The board context is in
[the survey](../../platforms/express/README.md).

Sources: IP20 kernel objects `gr2_init.o` and `gr2.o` (member offsets, disassembly with relocations; SHA-256 in
[references/binaries.md](../../references/binaries.md)); NetBSD `grtwo.c` and `grtworeg.h` (software expectation); the Elan
Graphics Technical Report for the chip's existence and the FIFO. Names in the "Name" column are NetBSD's where it has one and
are not the vendor's. Labels as in [AGENTS.md](../../AGENTS.md).

All accesses are from the IP20 driver as 32-bit loads and stores unless a width is given. A qtest can discriminate for each row
the power-on reading, whether a write reads back, and any side effect; those are unknown for every row below because no
reset-state source has been read, so none is listed per row.

## Regions

| Offset | Size | Region | Grade and source |
|---|---|---|---|
| `+0x00000` | `0x20000` | Shared data RAM (CPU and GE7 communication). The microcode loader writes 512 constant words at its start; its last word `+0x1fffc` is a flag the driver writes 0 or 1 to. | established for the accesses (`Gr2DownloadGE7`, `Gr2TpSetup`, `Gr2Download`); the role as "shared with the GE7" is NetBSD's and the loader's error text. |
| `+0x40000` | `0x20000` | Graphics FIFO. A write to `+0x40644` (init), `+0x40648` (colour), `+0x4064c`, `+0x40650`, `+0x40654`, `+0x40658`, `+0x4065c`, `+0x40660`, `+0x40664` selects a command, and `+0x4077c` takes data words. | NetBSD offsets; kernel touches `+0x40644`, `+0x40648`, `+0x40654`, `+0x4077c` (`gr2_tpucode.o` `Gr2TpSetup`). Role of each token: inferred. |
| `+0x60000` | `0x8000` | HQ2 microcode store, 32-bit words, address = `(offset - 0x60000) / 4`. The loader writes then reads back each word it loaded. | established (`Gr2DownloadHQ2` `0xeac`). Size from NetBSD's map; the largest address the image uses is unread. |
| `+0x68000` | `0x2000` | Eight GE7 slots of `0x400` bytes each. See below. | established for the probe and load accesses (`_Gr2ProbeGEs`, `Gr2DownloadGE7`). |
| `+0x6a000` | | HQ2 registers. See below. | |
| `+0x6c000` | | Board revision (read) and clock (write); DACs, VC1, XMAP5 and RE3 windows. Outside this page. | See the survey. |

## HQ2 registers (`+0x6a000`)

| Offset | Name | Access seen in IRIX | Grade |
|---|---|---|---|
| `+0x6a000` to `+0x6a03c` | attribute jump table (NetBSD: `ATTRJUMP`) | the microcode loader writes 16 words from image offset `0xfc`, reads them back | established as a 16-word table (`Gr2DownloadHQ2`). Meaning inferred from NetBSD's name. |
| `+0x6a040` | status (NetBSD: `VERSION`) | read in `Gr2FIFOHandler` (`gr2.o` `0x2a0`), `Gr2FIFOPollLowater` (`0x158`) and `Gr2FIFOTimeoutCallback` (`0x1f8`): bits 12:6 are compared with thresholds 35, 36, 40, 41, 63 as a FIFO fill count; bit 5 set makes the interrupt handler print an error. | established that the count and bit 5 are read this way. **NetBSD uses the same register as a version word**; unresolved, see [questions](../../questions/README.md). |
| `+0x6a044` | `NUMGE` | write: GE count (from `_Gr2ProbeGEs`), or count with bit 4 set when it is 8 (`_Gr2HQ2RegInit` `0xb70`) | established |
| `+0x6a054` | `FIFO_FULL_TIMEOUT` | write `100` | established value; NetBSD's name |
| `+0x6a058` | `FIFO_EMPTY_TIMEOUT` | write `255` | established value; NetBSD's name |
| `+0x6a05c` | `FIFO_FULL` | write `40` at init; the FIFO interrupt handler writes the same 40 back when re-arming (`Gr2FIFOPollLowater` `0x158`, handler `0x2a0`) | established value; the field is a fill threshold, inferred from the compares against the status field |
| `+0x6a060` | `FIFO_EMPTY` | write `1` | established value; NetBSD's name |
| `+0x6a064` | `GE7_LOAD_UCODE` | write: fifth word of each GE7 microcode record; read back masked with `0x03dfffff` | established (`Gr2DownloadGE7`) |
| `+0x6a06c` | `HQ_GEPC` | read once in `_Gr2ProbeChipRev`; the upper 16 bits are kept as a revision byte | established that it is read and shifted; "revision" inferred |
| `+0x6a070` | `GEPC` | write: GE microstore address (counts up to 0xffff when clearing the store; set to each record's address when loading); written 0 by `Gr2TpSetup` | established |
| `+0x6a074` | `INTR` | not touched by the IP20 driver | unknown |
| `+0x6a078` | `UNSTALL` | `Gr2TpSetup` writes 0 after the microcode loads | established that a 0 is written; the name's meaning is NetBSD's |
| `+0x6a07c` | probe word (`MYSTERY`) | read in `Gr2Probe` after `badaddr`; must equal `0xdeadbeef` | established (also the PROM probe, via the chips gio page) |
| `+0x6a080` | `REFRESH` | write `16` | established value; NetBSD's name |
| `+0x6a100` | `FIN3` | not touched by the IP20 driver | unknown |

NetBSD also names `+0x6a048` (`FIN1`), `+0x6a04c` (`FIN2`), `+0x6a050` (`DMASYNC`) and `+0x6a068` (`GEDMA`): not touched by
the IP20 driver objects read so far, **unknown**.

## GE7 slots (`+0x68000`)

- Slot `n` (0 to 7) is at `+0x68000 + 0x400 * n` (established from the stride and from `_Gr2ProbeGEs`).
- Probe (`gr2_init.o` `0x50`): slot 0 is taken as present. For each of slots 1 to 7 in turn, the five words `0x1f1f1f1f`,
  `0x2e2e2e2e`, `0x3d3d3d3d`, `0x4c4c4c4c`, `0x5b5b5b5b` are written at slot offsets `+0x0`, `+0x7c`, `+0xfc`, `+0x17c`, `+0x1fc` and
  read back. A failing slot does not end the loop: all of slots 1 to 7 are tried, and the count byte is rewritten to the
  slot's index plus one whenever a slot returns all five. The result is the highest responding slot plus one, which is
  1 plus the run of responding slots only when the responding slots are contiguous. Established (whole routine read). A qtest can discriminate: a GE slot returns what was written
  at those five offsets and an absent slot does not; whether an absent slot answers with a bus error or with other data is
  **unknown** (the PROM and kernel use plain loads here, with no fault catcher).
- Microcode load window `+0x683e0`, `+0x683e4`, `+0x683e8`, `+0x683ec` (slot 0, offsets `0x3e0`..`0x3ec`) together with
  `+0x6a064` and the address in `+0x6a070` (established). The load goes to every populated GE at once, inferred from there being
  one window rather than one per slot.
- `+0x683f4`: the kernel writes 0, reads the word back, and keeps bits 7:5 of the low byte (`_Gr2ProbeChipRev` `0x108`). Established
  that this happens; treated as the GE7 revision by inference. NetBSD instead reads a revision at `+0x680fc`; the two differ.

## What would settle the unknowns

HQ2 reset values: no source read yet. Candidates: the PROM's graphics diagnostic routine (`0xbfc0e6f0` onward in 4.0.5D), the
Indigo diagnostic program `ide.IP20`, and the microcode images themselves (the attribute jump table and the first sequencer
words show what the HQ2 expects at start). Reading plan is in the survey.
