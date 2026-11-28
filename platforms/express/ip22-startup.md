# Indy and Indigo2 Express start-up, from the IP22 kernel objects

What the IRIX 6.5 kernel's own Express driver for the Indy (IP24) and Indigo2 (IP22) does to find a board, read its configuration, start its clock, reset it and route its interrupts, set against the Indigo (IP20) driver that [host-contract.md](host-contract.md) reads. Written for a Windows NT display driver that has to repeat the start-up on these two hosts. The console images are in [console-microcode-ip22.md](console-microcode-ip22.md); the slot-numbering comparison of the GL cores is in [ip22-slot-comparison.md](ip22-slot-comparison.md).

Ratings: **established** is a fact read from a held file with a tool (a table, a symbol, a value in a header). **Software expectation** is what the shipped IRIX code does with the hardware or expects back; it is not proof of what the board does. **Inferred** is a reasoned reading, with the reasoning. **Unknown** has what would settle it. Nothing was run on a board, and no physical read was made.

## Sources

| Source | Identity | Used for |
|---|---|---|
| `usr/cpu/sysgen/IP22boot/gr2.a`, IRIX 6.5 base set | SHA-256 `19ef07c204ce1fc3c73d3f12783adb1824d48b8ee9af28538914fedf33b6f228`; members `gr2.o` `b0528d9ff32580bdb1fa12af2e1b22712638355c631026f8104f9556d2557148`, `gr2_corona_i2c.o` `86bc8541909ca7b763dad68eae26dd9907979ecdf51d1ccc51f9b0b8d8ad823e`, `gr2_dma.o` `0c4ffb78f778aa41d5264e508db802ea69df73d496f49476559b77c894fbf093`, `gr2_init.o` `e59f584408f975a57f0577e3c565f23097aca56210b266b196186f7569fa785f`, `gr2_retrace.o` `10f3e5d9e5dcd94d70bbfbd8bb29d0bc13a58fa8566c8a265bd824ecfb8176a6`, `gr2_tport.o` `e6b9d5687697a4e8d95376f5b04ec7f2106486aebf0cf3b0f7052b3ffd0120b6`, `gr2_tpucode.o` `8084f158da53e5771021cbed62443bb13756c5748e4c1571657705ef56c2d599` | the driver; read as disassembly with relocations and DWARF symbols |
| `usr/cpu/sysgen/IP22boot/kernel.o`, same set | `633902b92f5f7d01fceea7905962344d4053e026dcc8dbce6593b64ce1612c7c` | `setgiovector` only |
| `usr/cpu/sysgen/IP20boot/gr2.a`, same set | `c768b3a4889dd50e8e78c065fdddb7ebca2d9536eb39de315511d2a90906128c` | the Indigo build, compared function by function |
| Shipped headers `usr/include/sys/IP22.h`, `hpc3.h`, `mc.h`, same set | not hashed | register addresses, bit names, vector numbers |
| IRIX source, PROM library `stand/arcs/lib/libsk/graphics/EXPRESS/gr2_init.c` and `libsk/io/corona_i2c.c`, with `NEWPORT/pcd.h` | first-rank source for the PROM's copy of the same logic; read, restated in our words, not copied | cross-checks of the object, the I2C protocol, panel names |

The IP22 kernel's `gr2.a` has a seventh member, `gr2_corona_i2c.o`, that the IP20 archive lacks. Comparing the six common members function by function (normalised instruction streams, relocation symbols kept): `gr2_dma.o` and `gr2_tpucode.o` are identical; in `gr2_init.o` the probe, clock, reset, register-init and monitor paths differ and the loaders, DAC, XMAP and HQ2 register code do not; `gr2.o` differs in start, interrupts, monitor and info code. The rest of this page is those differences.

## Answers

| Question | Answer | Rating |
|---|---|---|
| Slot base | Two boards are probed, at physical `0x1f000000` (the graphics slot) and `0x1f400000` (GIO slot 0). The table is the same on the Indy and the Indigo2. | established (table) |
| INT2 and its relatives | Indigo2: INT2 at `0x1fbd9000`, its PORT_CONFIG byte at `0x1fbd901f`, the extended slot register at `0x1fbd9900`. Indy: INT3 at `0x1fbd9880`, and the HPC3 general-control register at `0x1fbd984c` clears the Express retrace latch. Indigo: INT2 registers from `0x1fb801c0`, PORT_CONFIG byte `0x1fb801df`. | established (headers, object constants) |
| Probe record | Same 60-byte record and decode as the Indigo, with two added bytes (`+0x37`, a timing mode id set at init, and `+0x39`, the flat-panel marker) and the monitor code replaced by `0x82` or `0x83` when a panel answers on the I2C window. | software expectation |
| Clock tables per monitor code | Table below. The Indigo's two tables are unchanged; two flat-panel sets are new. | established (bytes), software expectation (use) |
| `INIT` class | Same selector as the Indigo: 0 for board revisions 0 to 3, 1 for 4 and 9 to 11, 2 for 5 to 8 and 12 and up. | software expectation |
| I2C window | A byte-wide I2C controller (the Philips PCD8584 family) at `+0x6c1c0` (data) and `+0x6c1c4` (control), probed through `+0x6c1e0`, reached behind the XMAP5 FIFO. It talks to a flat-panel adapter, not to the monitor. | software expectation |
| HQ2.1 differences | None in the driver: no code reads the HQ2 revision byte, and the HQ2 register writes are the Indigo's. | software expectation; hardware difference unknown |
| GIO64 effects on DMA | None in the driver: `gr2_dma.o` is the Indigo's instruction stream. | software expectation; hardware effect unknown |

## Which host, and the addresses

The shipped header says the HPC3 system-ID register at `0x1fbd9858` holds the board identity in bit 0: 1 for the Indigo2 board ("fullhouse", IP22), 0 for the Indy board ("guinness", IP24). The driver asks two predicates, `is_fullhouse()` and `is_indyelan()` (the latter reads that register and returns true when bit 0 is clear, caching the answer). The header also gives `is_ioc1()` (chip-ID bit `0x20`, Indy). Established for the register and the driver's use of it; that `is_fullhouse()` returns the same bit is **inferred** (the function returns a flag set during early boot, which was not read).

| | Indigo (IP20) | Indigo2 (IP22, fullhouse) | Indy (IP24, guinness) |
|---|---|---|---|
| Interrupt chip | INT2 from `0x1fb801c0` | INT2 `0x1fbd9000` | INT3 `0x1fbd9880` |
| Local-0 status byte (bit 0 is the FIFO line) | `0x1fb801c3` | `0x1fbd9003` | `0x1fbd9883` |
| Retrace-latch clear | PORT_CONFIG `0x1fb801df`, bit 3 | PORT_CONFIG `0x1fbd901f`, bit 3 (graphics slot) or bit 4 (slot 0) | HPC3 general control `0x1fbd984c` bit 0, after setting bit 0 of the select register `0x1fbd9848` |
| Board reset | MC CPUCTRL0 bit 10 low 10 us, high | PORT_CONFIG bit 1 (graphics slot) or bit 2 (slot 0) low 10 us, high | MC CPUCTRL0 (`0x1fa00004`) bit 10 low 10 us, high |
| Retrace status read | INT2 byte `0x1fb801d3` bit 0 | extended register `0x1fbd9900`, bit 0 (graphics slot) or bit 2 (slot 0) | the same code reads `0x1fbd9900`; see below |

Addresses are physical; the objects add `0xa0000000` (KSEG1). The Indigo column is from [host-contract.md](host-contract.md#5-board-outputs-to-int2). Local-0 status bytes: header offset `0x0 | 3` from the interrupt chip (the `|3` is the byte lane on a big-endian host). Established.

PORT_CONFIG bit names from the shipped header: bit 0 DMA-sync select (slot 1 or slot 0), bit 1 reset slot 0 (this is the graphics slot, "SG"), bit 2 reset slot 1 (named "S0"), bit 3 clear slot 0's retrace, bit 4 clear slot 1's retrace. The header names the slots oddly (slot 0 and slot 1 for the graphics slot and GIO slot 0); the driver's use fixes the meaning: the entry for the graphics slot clears with `0x08` and resets with `0x02`, the entry for GIO slot 0 clears with `0x10` and resets with `0x04`. Established from the board table below.

### The board table

`gr2.o` `.data` holds a table of 28-byte entries ended by an all-zero entry (symbol `Gr2Boards`, 84 bytes). Established.

| Offset in entry | Graphics-slot entry | GIO-slot-0 entry | Use |
|---|---|---|---|
| `+0x00` | `0xbf000000` | `0xbf400000` | base address (KSEG1) |
| `+0x08` | pointer to the first 60-byte probe record (`.bss` + 0) | pointer to the second (`.bss` + `0x3c`) | probe record |
| `+0x10` | 2 | 0 | slot number passed to the reset and to `setgiovector` (graphics slot is 2, slot 0 is 0, per the header's slot names) |
| `+0x14` | 0 | 1 | board index, passed to the interrupt handlers as their argument |
| `+0x18` | `0x08` | `0x10` | retrace-latch clear mask for PORT_CONFIG (Indigo2) |

The kernel does not probe the Indy's GIO slot 1 (the header says that slot exists only on the Indy); no entry for it. Established.

## The probe

`Gr2Probe(base, record)` (`gr2_init.o` `0x3d4`), in order. Reads are byte loads at the first byte of each word, as on the Indigo ([clock page](../../devices/clock/README.md)).

1. Look the board up in the table. A per-board state byte (in `.sbss`) caches the result: 0 not yet tried, 1 failed, 2 live. A live board answers 1 again at once; a failed one answers 0 at once. The state is set to 1 before the checks and to 2 only at the very end. Established; software expectation for the use.
2. `badaddr` at `+0x6a07c`, then the word there must equal `0xdeadbeef`. Both the same as the Indigo.
3. Copy the name `"GR2"` into the first 16 bytes; record word at `+0x24` = 60.
4. Port 0 (`+0x6c000`): inverted low nibble is the board revision, 0 fails the probe. Revision below 4: the Indigo's decode, unchanged ([clock page](../../devices/clock/README.md#decoding-established-as-software-expectation)). Revision 4 and up: back-end revision = `port1 & 3` (3 fails), Z buffer = `port1` bit 5, planes 24 if `port1` bit 4 else 8, monitor code = `port0 >> 4`. Same as the Indigo kernel's.
5. **IP22 addition.** Record `+0x39` = 0. Call `gr2_i2cProbe(base)`. If it succeeds: `+0x38` = 0, `+0x39` = `0xff`, run `gr2_i2cSetup`, then `gr2_fp_probe`, which reads the panel ID (below): ID 3 stores `0x82` in `+0x39`, ID 4 stores `0x83`, any other ID stores 0, and no answer leaves `0xff`. It also updates the machine-inventory entry of class 17 with whether a panel was found (what `hinv` prints for it was not checked). If `+0x39` is neither 0 nor `0xff`, the monitor code (`+0x2d`) is overwritten with it. If the probe fails: on an Indy (`is_indyelan()` true) `+0x38` = 0; otherwise `+0x38` is computed as the Indigo kernel does for every board, from the inverted `port2` bits 5:4 (revision below 4) or inverted `port1` bits 3:2 (revision 4 and up).
6. Record `+0x2a` and `+0x2b` = 4 (auxiliary planes, window IDs: same constants the PROM library sets). `_Gr2ProbeGEs` (GE count at `+0x36`; identical to the Indigo), `_Gr2ProbeChipRev` (identical).
7. Monitor code 6: width 1024, height 768 in the record and return 0. Code `0x82`: width **1025**, height 768, return 1. Anything else: 1280 by 1024, return 1. State set to 2.

Record layout, as the IP22 objects write it (byte offsets). `Gr2Info` copies the whole record (at most 60 bytes) to user space; if `+0x39` is non-zero it first runs `gr2_fp_probe` again, and for monitor code `0x82` with `+0x37` equal to 29 it presents a width of 1024 in the copy (the stored 1025 is restored after the copy). Established that it does; why the user level wants 1024 is **unknown**.

| Offset | Content |
|---|---|
| `0x00` to `0x0f` | name `"GR2"` |
| `0x20`, `0x22` | width, height (16-bit) |
| `0x24` | record length, 60 |
| `0x28` | 0 |
| `0x29` | colour planes, 8 or 24 |
| `0x2a`, `0x2b` | auxiliary planes 4, window IDs 4 |
| `0x2c` | Z buffer present |
| `0x2d` | monitor code (or `0x82`, `0x83`) |
| `0x2e` | board revision |
| `0x2f` | MC revision level ORed with `0x80` (the kernel's `mc_rev_level`) |
| `0x30` | HQ2 revision byte, `hq_gepc` (`+0x6a06c`) bits 23:16 |
| `0x31` | GE7 revision, bits 7:5 of the word at `+0x683f4` after a store of 0 |
| `0x32` | RE3 revision, low byte of shared word `+0x1ffe0` after the full microcode starts |
| `0x33` | VC1 revision, internal register 5 low three bits |
| `0x34` | back-end (video) revision |
| `0x35` | board live |
| `0x36` | geometry engine count |
| `0x37` | timing mode id, set by `gr2_init` (not the probe): 23 for the 72 Hz codes (low three bits 1), 29 for monitor code `0x82`, 1 for everything but low three bits 6 (which set nothing); meaning unknown |
| `0x38` | super-video field (step 5) |
| `0x39` | flat-panel marker (new on IP22) |

Established as stores; the reading of each byte is as on the Indigo for every offset but `0x28`, `0x37` (unknown) and `0x39`.

## Clock and timing tables per monitor code

`Gr2StartClock(base, record)` (`gr2_init.o` `0x7bc`). Revision below 4 is the Indigo's code (the 17-byte table and `port0` selector 1 or 2). Revision 4 and up:

1. `port0` (`+0x6c000`, write) = **7** if this board is the first live graphics board in the table (`gr2_firstgfxslot()`), else **`0x47`**. The PROM library source writes `0x47` for every board. Bit 6 is unexplained: **inferred** to tell a second board's clock or video path from the first's; settled by the board schematics or a second-board capture.
2. Pick seven bytes by the monitor code (table below), send them as 56 single-bit writes to the clock data port `+0x6c020`, least significant bit first, the last bit written with bit 1 also set.
3. 3 us delay; `port1` (`+0x6c004`) = 0, then 1.

| Monitor code (`+0x2d`) | Seven clock bytes | VC1 timing tables loaded (`_Gr2RegisterInit`) | Screen |
|---|---|---|---|
| 1, 9 | `00 00 00 04 05 04 06` | 72 Hz set: line table 400 bytes at VC1 SRAM `0x000`, frame table 56 bytes at `0x800`, cursor line table 384 bytes at `0x400`, cursor frame table 56 bytes at `0x900` | 1280 by 1024 |
| 6 | none | none | the kernel refuses the board at probe ([monitor codes](host-contract.md#monitor-codes-the-kernel-refusal-and-gfxinfos-names)) |
| 14 | none | none | not refused by the probe: 1280 by 1024 with no clock load and no timing tables |
| `0x82` (XGA flat panel from the panel ID) | `00 10 00 04 06 03 07` | panel set: line table 334 bytes at `0x000`, frame table 40 bytes at `0x800`; no cursor tables | 1025 by 768 |
| `0x83` (hi-res flat panel from the panel ID) | `00 10 00 15 18 01 0f` | hi-res panel set: 596, 56, 550, 56 bytes at the four addresses above | 1280 by 1024 |
| low three bits 7 with marker `0xff` (I2C controller answers, no panel ID) | `00 10 00 15 18 01 0f` | the hi-res panel set | 1280 by 1024 |
| every other code (0, 2 to 5, 7 without the marker, 8, 10 to 13, 15) | `00 10 00 15 18 01 0f` | 60 Hz set: 474, 50, 436, 50 bytes at the four addresses | 1280 by 1024 |

The clock choice looks at the monitor code's low three bits (1 gives the 72 Hz bytes, 6 none, anything else the 60 Hz bytes) after the two panel codes; the timing-table choice compares the full code. They agree on every code. The two tables the Indigo already had (`00 00 00 04 05 04 06`, `00 10 00 15 18 01 0f`) and all four 60 Hz and 72 Hz timing tables are byte-identical to the Indigo objects' (compared by hash, all eight). Tables are in `gr2_init.o`: clock bytes `PLLclk132` at `.sdata` `+0x20`, `PLLclk107` at `+0x28`, `PLLclkFP` at `+0x10`, `PLLclkIchiban` at `+0x18`; VC1 tables `ltableH60` at `.data` `+0x0`, `frtableH60` `+0x1e0`, `ltableH60_400` `+0x218`, `frtableH60_400` `+0x3d0`, `ltableH72` `+0x408`, `frtableH72` `+0x598`, `ltableH72_400` `+0x5d0`, `frtableH72_400` `+0x750`, `ltableFP` `+0x788`, `frtableFP` `+0x8d8`, `ltableIchiban` `+0x918`, `frtableIchiban` `+0xb70`, `ltableIchiban_400` `+0xba8`, `frtableIchiban_400` `+0xdd0`; sizes as in the table. Established. A driver that carries these takes them from the user's own object or media, not from this repository.

For a flat panel (`0x82`, `0x83`, or code-7 with the marker) `_Gr2RegisterInit` also writes the five XMAP5 FIFO-status ports (`+0x6c11c`, `+0x6c13c`, `+0x6c15c`, `+0x6c17c`, `+0x6c19c`) with `0xf`, `0xc`, `0xd`, `0xe`, `0xf` and then calls `gr2_i2cPanelOn`. Established for the stores; that these enable the panel's video output is the PROM library's comment ("enable output to the video connector"), a software expectation. `Gr2SetMonitor` repeats the clock load for a new timing file (same first-board rule for `port0`) and, when the panel ID answers, turns the panel off, reads the ID and turns it on again. Established.

What the seven-byte sets produce, and the 17-byte table of the Indigo, are unknown ([questions/display.md](../../questions/display.md)). `gr2.o` also holds `genlockclk` (17 bytes at `.data` `+0x58`) and `clearPLL` (7 bytes at `.sdata` `+0x10`) used by the genlock code; not read.

## The `INIT` class

`Gr2Start` (`gr2.o` `0x1c48`) and `Gr2TpSetup` (`gr2_tpucode.o`, identical to the Indigo's, including its read-only table) store the class word at `+0x4077c` with no token before it. The class comes from the board revision (record `+0x2e`) through a 12-entry jump table in `gr2.o`'s `.rodata` (offset `0x290`): revisions 0 to 3 give 0, 4 gives 1, 5 to 8 give 2, 9 to 11 give 1, 12 and up give 2 (the code falls through to 2 for any revision above 11). The Indigo kernel's table and the PROM library source agree. Established for the table; which revision an Indy or Indigo2 board reads is **unknown** from these objects. The public captures that print "HQ2.1 rev A" for revision 4 and 6 boards ([host-contract.md](host-contract.md#4-probe-answers-per-indigo-variant)) would give classes 1 and 2; a driver can compute the class from the revision it reads and needs not know the product.

`Gr2Start` also stores 0 to `gepc` (`+0x6a070`), `unstall` (`+0x6a078`) and `fin2` (`+0x6a04c`) before the class word, as on the Indigo, replaces the retrace handler (below) and finishes by recording the RE3 revision byte and `+0x1fffc` = 2. Established.

## The I2C window

`gr2_corona_i2c.o` (a member new in the IP22 archive; the source library calls the same thing the Presenter flat-panel control). Established for the addresses and the sequence; the protocol is also stated in the PROM library's `corona_i2c.c`.

- **Registers.** Byte-wide, behind the XMAP5 display-control FIFO: data register at `+0x6c1c0`, control/status register at `+0x6c1c4`. Every access first polls XMAP5 chip 0's status byte at `+0x6c11c` until bit 0 clears, 1 us per poll, up to 1000 polls ("wait for the display-control FIFO to empty"), so the I2C access does not collide with FIFO traffic.
- **Probe** (`gr2_i2cProbe`): write `0x00`, `0x55`, `0xaa` in turn to a byte at `+0x6c1e0` (the access path that does not wait for an acknowledge), reading it back after each of the last two and requiring the value; success means the I2C hardware exists. It does not guard against a bus error.
- **Controller** is a PCD8584-class bus controller (the shipped constants and the algorithm are the Philips part's): setup writes own-address `0x7f`, clock register `0x1c` (12 MHz clock, 90 kHz bus), then enables the bus; a transfer sets the target address, writes the control register with START, polls the status register for the PIN bit to clear (100 tries), checks the last-received-bit and error bits, and ends with a STOP that waits for status `0x81` (10 tries; the 100 and 10 are the PROM library's constants, the object's 100 matches).
- **Devices.** A port expander at I2C address `0x70` (read gives the panel ID in bits 7:5; write sets power, brightness steps and a 15 or 18-bit mode): panel on writes `0xe7`, off writes `0xff`. An audio chip at address `0x82` (left and right volume, bass, treble, switch registers) set to `0xf6`, `0xf6`, `0xf6`, `0xf6`, `0xce` on panel-on. Backlight up is 100 four-write steps. Panel-on ends by selecting 15-bit emulation (the PROM library source selects 18-bit; the kernel object calls the set-mode routine with 0).
- **Panel IDs** (expander bits 7:5): 3 is an XGA flat panel (1025 by 768 in the record), 4 the hi-res panel (1280 by 1024). The PROM library names ID 3 as a Mitsubishi XGA panel. Any other ID selects neither.

Rating: software expectation (the sequence), inferred for what the devices are beyond the part numbers' standard roles (an I2C expander and an audio chip with those register layouts), and **unknown** whether a plain Indy or Indigo2 Express board (no panel adaptor) answers the probe at all: a board without the I2C hardware is the case the probe is for, and the kernel treats a failed probe as "no panel". What would settle it: a `gfxinfo` capture or hardware inventory of a stock board.

## Interrupts and the retrace latch

Established from the objects, `kernel.o`'s `setgiovector` and the shipped header, except where marked.

- The graphics slot's FIFO line is the GIO interrupt 0, local vector 0 (local-0 bit 0, "fifo full"); the graphics interrupt is GIO 1, vector 6; the retrace line is GIO 2, vector 15 (local-1 bit 7). The kernel's `setgiovector(interrupt, slot, handler, arg)` for the graphics slot installs `Gr2FIFOInterrupt` on interrupt 0 and `gr2_retr_intr` (at start-up) or `Gr2RetraceInterrupt` (after `Gr2Start`) on interrupt 2, on both the Indy and the Indigo2. For GIO slot 0 on the Indy it installs on vectors 22 and 23 (GIO expansion lines 0 and 1); on the Indigo2 slot 0 shares the three lines with the graphics slot (`setgiovector` hands the extended register's address to the shared handler, and the header gives that register per-slot interrupt bits), so the shared handler tells the slots apart by those bits (**inferred**; the handlers at the table's addresses were not read).
- The FIFO handler on the Indigo masks and unmasks the FIFO line by writing INT2 local-0 mask byte `0x1fb801c7`. The IP22 kernel does not: it calls kernel services (`gfx_waitf_on`, `gfx_waitf_off`) for the FIFO-not-full wait. What those services write was not read, so how the "not full" line (header vectors 22 and 23, local-2 bits 6 and 7, labelled "fifo not full" on the Indigo2) is enabled is **unknown** from these objects.
- Retrace latch: the handler clears the latch by writing the slot's mask to 0 in PORT_CONFIG, flushing the bus, then back to 1 (Indigo2); on the Indy it clears bit 0 of `0x1fbd984c`, flushes, sets it again. At start-up the Indy path also sets bit 0 of the select register `0x1fbd9848` and of the general-control register, i.e. makes the line an output and releases it; the header labels the line "clear EXPRESS interrupt". `_Gr2RegisterInit` pulses PORT_CONFIG bits 3 and 4 together (`0x18`) at the top without testing the host. On the Indy that address is, by the header, unused; that the write is harmless there is **inferred** (the kernel does it).
- Before each console token the text port waits for the local-0 status byte's bit 0 to clear: `0x1fbd9003` on the Indigo2, `0x1fbd9883` on the Indy (the objects test `is_ioc1()` to choose the chip), as on the Indigo ([host-contract.md](host-contract.md#5-board-outputs-to-int2)). The retrace handler waits up to ten 1 us polls for the vertical-status bit in the extended register `0x1fbd9900` (bit 0 for the first table entry, bit 2 for the second) before its work; the same code runs on the Indy, whose header says the register is an Indigo2-only feature. What a read of `0x1fbd9900` returns on an Indy is **unknown**; the poll gives up after ten tries, so the handler tolerates any answer.

## HQ2.1 and GIO64

- **HQ2.1.** The only visible difference is the value in `hq_gepc` bits 23:16, copied to record byte `0x30` (0 prints "HQ2 rev A", 1 prints "HQ2.1 rev A" in `gfxinfo`; [host-contract.md](host-contract.md#4-probe-answers-per-indigo-variant)). `_Gr2ProbeChipRev` and `_Gr2HQ2RegInit` are instruction-for-instruction the Indigo's, and no byte load from record offset `0x30` exists in any member (the record is copied whole to user space; two word loads at displacement 48, in `gr2.o` and `gr2_retrace.o`, each feed a further pointer load, so they read pointer fields of other structures). So the driver treats HQ2 and HQ2.1 alike. Software expectation. Whether the silicon behaves differently (FIFO depth, finish flags, token set) is **unknown**; the GL tokens are the same ([ip22-slot-comparison.md](ip22-slot-comparison.md)).
- **GIO64.** None of the objects names a GIO64 arbitration, 33 MHz or bus-width control. The DMA code (`gr2_dma.o`, ten functions) is identical to the Indigo's instruction for instruction; it programs the MC graphics DMA engine and the board address `+0x6a068` as on the Indigo. The MC revision level is stored in record byte `0x2f` and in a kernel variable (`vdma_rev`) that the DMA code reads, on both hosts. Software expectation that the Indy and Indigo2 need no different DMA programming for this board; **unknown** whether the Indy's and Indigo2's MC and GIO bridge change what the board's slave interface sees. What would settle it: the chips repository's MC and GIO pages for IP22 read against the GIO32 slave behaviour here, or a DMA capture.

## Not read

`Gr2Private` (the user-level control calls, including the I2C command pass-through), the genlock code, the full text-port functions (`gr2_tport.o` differs from the Indigo's mostly in per-board indexing and flat-panel handling), what `setgiovector`'s slot-0 handlers do beyond vector selection, and how `gfx_waitf_on` enables the FIFO-not-full line. The PROM's own start-up for these hosts was not read; the PROM library source is the only account of it here.
