# HQ2: the host-visible window

What the Indigo PROM and the IRIX IP20 kernel driver touch in the HQ2's part of the graphics slot, as offsets from the board
base (`0x1f000000`). This is the window only; the HQ2's instruction set, token numbering and DMA engine are not covered. No
board context is in [the survey](../../platforms/express/README.md); the register map is [registers.toml](registers.toml) (generated reference
[registers.md](registers.md)) and the host-side contract (flow control, completion flags, context switch, pixel DMA, probe answers) is
[platforms/express/host-contract.md](../../platforms/express/host-contract.md). The shipped IRIX diagnostic program names every HQ2 register and
status field; its names are used below next to NetBSD's. Provenance: `[binary]` shipped binary, `[public]` NetBSD or published document.

Sources: IP20 kernel objects `gr2_init.o` and `gr2.o` (member offsets, disassembly with relocations; SHA-256 in
[references/binaries.md](../../references/binaries.md)); NetBSD `grtwo.c` and `grtworeg.h` (software expectation); the Elan
Graphics Technical Report for the chip's existence and the FIFO. Names in the "Name" column are NetBSD's where it has one and
are not the vendor's. Labels as in [AGENTS.md](../../AGENTS.md).

All accesses are from the IP20 driver as 32-bit loads and stores unless a width is given. No source states a reset value for any register
here, so none is given except the constant probe word. Per-register qtest discriminators are in `registers.toml`.

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
| `+0x6a040` | status (ide: "HQ2 version register"; NetBSD: `VERSION`) | read in `Gr2FIFOHandler` (`gr2.o` `0x2a0`), `Gr2FIFOPollLowater` (`0x158`), `Gr2FIFOTimeoutCallback` (`0x1f8`), `_Gr2UcodeReady`, the DMA triggers and `Gr2SetMonitor`. Decoded in full by the diagnostic program (`gr2_rdHQ2reg`): bit 0 finish flag 3, bit 1 finish flag 2, bit 2 finish flag 1, bits 4:3 DMA sync source, bit 5 FIFO overflow, bits 12:6 FIFO count, bit 13 FIFO low water, bits 15:14 zero, bits 19:16 `ge_ctr`, bits 22:20 `ge_ptr`, bits 31:23 HQ2 version. | established [binary] for the field names and boundaries; the roles of `ge_ctr`, `ge_ptr` and low water are unknown. Question 1 of the old list is settled: the version is bits 31:23, as the PROMs and NetBSD read it. |
| `+0x6a044` | `NUMGE` | write: GE count (from `_Gr2ProbeGEs`), or count with bit 4 set when it is 8 (`_Gr2HQ2RegInit` `0xb70`). The diagnostic program reads it back and compares ("HQ2: Wrong NUMGE") | established |
| `+0x6a048` | `FIN1` (ide: Finish Flag 1) | write 0 by the diagnostic program and the 4.0.5G PROM before a pixel DMA; clears status bit 2 | established [binary] |
| `+0x6a04c` | `FIN2` (ide: Finish Flag 2) | write 0 before every context switch, microcode start and DMA command; clears status bit 1 | established [binary] |
| `+0x6a050` | `DMASYNC` (ide: DMA sync source) | write 2 before every DMA; write 0 in early init; values 0 vertical interrupt, 1 video sync, 2 clear, 3 set | established for the stores and the value names; effect inferred |
| `+0x6a054` | `FIFO_FULL_TIMEOUT` | write `100` | established value; NetBSD's name |
| `+0x6a058` | `FIFO_EMPTY_TIMEOUT` | write `255` | established value; NetBSD's name |
| `+0x6a05c` | `FIFO_FULL` | write `40` at init; `Gr2FIFOPollLowater` (`0x158`) writes 40 back when it finds the count below 35; the handler (`0x2a0`) writes the count plus one, clamped to 40..63 | established value; the field is a fill threshold, inferred from the compares against the status field |
| `+0x6a060` | `FIFO_EMPTY` | write `1` | established value; NetBSD's name |
| `+0x6a064` | `GE7_LOAD_UCODE` | write: fifth word of each GE7 microcode record; read back masked with `0x03dfffff` | established (`Gr2DownloadGE7`) |
| `+0x6a068` | `GEDMA` | the GIO address of every MC graphics DMA to or from the board; the kernel writes 0 twice after a DMA timeout | established [binary]; see [host-contract](../../platforms/express/host-contract.md) section 3 |
| `+0x6a06c` | `HQ_GEPC` | read by `gr2_error` (low 16 bits logged as "GE PC") and by `_Gr2ProbeChipRev`, which keeps bits 23:16 in the probe-record byte the PROMs fill from status bits 31:23. The diagnostic program reads and prints it with "can't read - hw bug" | established that it is read and how; whether bits 23:16 are a revision is **inferred either way** (see the review below) |
| `+0x6a070` | `GEPC` | write: GE microstore address (counts up to 0xffff when clearing the store; set to each record's address when loading); written 0 by `Gr2TpSetup` | established |
| `+0x6a074` | `INTR` (ide: "Intr bit (cleared by host)") | not touched by the IP20 driver or PROMs; the diagnostic program can write it | inferred role as a host-cleared interrupt bit; which interrupt it raises unknown |
| `+0x6a078` | `UNSTALL` | `Gr2TpSetup` writes 0 after the microcode loads | established that a 0 is written; the name's meaning is NetBSD's |
| `+0x6a07c` | probe word (`MYSTERY`) | read in `Gr2Probe` after `badaddr`; must equal `0xdeadbeef` | established (also the PROM probe, via the chips gio page) |
| `+0x6a080` | `REFRESH` | write `16` | established value; NetBSD's name. Inferred role: the refresh interval of the GE7 microcode DRAM that HQ2 drives (GR4 board schematic sheets 7, 9, 10, [vendor-derived]; [host contract section 11](../../platforms/express/host-contract.md#11-across-a-little-endian-restart)); `registers.toml` still says effect unknown |
| `+0x6a100` | `FIN3` (NetBSD) | not touched by any shipped program | unknown |
| `+0x6b000` | Finish Flag 3 write port (ide) | write 0 to clear status bit 0 before a command; `Gr2PcxSwap` restores the saved bit of the incoming context here; the X server clears it before image reads and writes | established [binary] |

The roles of NetBSD's `FIN1`, `FIN2`, `DMASYNC` and `GEDMA` offsets, listed as untouched in the first pass, are settled by the kernel DMA and context
routines and by the diagnostic program's HQ2 register menu (which prints "Finish Flag 1/2/3", "DMA sync source", "GE DMA", "Intr bit").

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

HQ2 reset values: none stated by the PROM, the kernel or the diagnostic program (which only writes and reads back). The sequencer ISA, the
meaning of `ge_ctr`, `ge_ptr` and the low-water bit, the two timeout units, and what raises `INTR` need the microcode decoded. Open items:
[questions/hq2.md](../../questions/hq2.md).

## Review (2026-11-23)

Re-read against `gr2_init.o`, `gr2.o` and `gr2_tpucode.o` (hashes match [references/binaries.md](../../references/binaries.md)) and
PROM 4.0.5D. Results by area are in the [survey's review](../../platforms/express/README.md#review-2026-11-23); the points for
this page:

- Register init values (`+0x6a044`, `+0x6a054`..`+0x6a060`, `+0x6a080`), the `+0x6a000` jump table, `+0x6a070` and `+0x683e0`..`+0x683ec`
  accesses, and the probe word: CONFIRMED.
- GE7 probe: the count is the highest responding slot plus one, not the first failing slot (WRONG, fixed above).
- `+0x6a064` read-back mask: `0x03dfffff` (WRONG, fixed above).
- `+0x6a040`: IRIX also tests bits 1 and 0; no IRIX read looks at bits 31:24, so NetBSD's version byte is unconfirmed (see question 1).
  The `+0x6a06c` upper-half revision remains inferred.
- A qtest that sets up slots 1 and 3 but not 2 would discriminate the probe-count rule (the count would be 4).

## Review update (host contract, 2026-11-23)

- Question 1 of the survey list (is the top byte of `+0x6a040` an HQ2 version) is settled: yes, bits 31:23, named "HQ2 version" by the diagnostic program,
  stored by both PROMs and NetBSD; the kernel's `+0x6a06c` upper half is a register the diagnostic program calls unreadable.
- The status bits the kernel tests besides the FIFO count and overflow are finish flags 2 and 3 (bit 1 and bit 0), not error bits.
- `+0x6b000` is the write port of the third finish flag; the HQ2 register page therefore extends over two 4 KiB pages (`+0x6a000`, `+0x6b000`) as NetBSD's
  `+0x6b004` upper bound suggests.

## Review (2026-11-23, host contract)

Independent re-read of `registers.toml`, this page and the host contract against `gr2.a` (June 1998 `IP20boot` members), PROM 4.0.5D and 4.0.5G, the
Diagnostics 5.2 `ide.IP20` (SHA-256 `744fdebc...df14`; disassembled in full for `gr2_rdHQ2reg` and the write menu) and NetBSD `grtwo.c`/`grtworeg.h`
(`netbsd-src` in the Library). Results:

- Status field map: CONFIRMED. `ide` masks and shifts exactly bits 0, 1, 2 (finflag3, 2, 1), 4:3 (four named dma_sync strings), 5, 12:6, 13, 15:14,
  19:16, 22:20 and 31:23, in that print order. The three finish clears (`+0x6a048` flag 1, `+0x6a04c` flag 2, `+0x6b000` flag 3) and `dmasync` `+0x6a050` (values 0..3)
  are stores in `ide`'s write menu. That bits 4:3 read back `dmasync` is the field name only (inferred).
- `+0x6a06c`: CONFIRMED as `HQ_GEPC` in `ide`, which reads it. WRONG as "read once": `gr2_error` also reads it and logs the low 16 bits as the GE PC.
  GRADE: the claim that the kernel byte "is not the revision" is inferred, not established: PROMs and kernel fill the same probe-record byte (`+0x30`) from different
  registers, and `gfxinfo` very likely prints that byte. The rev-A evidence cannot say which register supplied it.
- Version field width: the PROMs keep bits 30:23 (byte store of `word >> 23`); NetBSD uses mask `0xff000000` with shift 23, which is not the same field. The
  host contract's "NetBSD agrees" holds only for value 0.
- FIFO overflow: WRONG that the handler does nothing else; it calls `gr2_error` (log, flag, kill clients, reset graphics).
- `Gr2FIFOPollLowater`: WRONG as described earlier; it returns 1 and writes 40 to `+0x6a05c` when the count is below 35, and 0 without a write otherwise.
