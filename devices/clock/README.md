# Board configuration ports and the pixel clock

The four byte-wide ports at `+0x6c000` to `+0x6c00c` and the clock data port at `+0x6c020` of the Express graphics window. Read side:
board revision, backend revision, monitor code, frame-buffer slots, Z buffer, colour depth. Write side: pixel clock select and
load. Registers: [registers.toml](registers.toml). Labels follow [AGENTS.md](../../AGENTS.md); source classes: **[public]**
(NetBSD `grtworeg.h`, `grtwo.c`; the Indy XZ board schematic `VB-3_Schematic.pdf`), **[binary]** (IRIX 6.5 IP20boot `gr2.a` and PROMs
`070-8116-004` 4.0.5D and `070-8116-005` 4.0.5G), **[vendor-derived]** (none used). Nothing was read on a board.

## Read side: the byte-lane question is settled for the IRIX software

[binary] Every board configuration read is a byte load at the first byte of its word: `Gr2Probe` (`gr2_init.o` `0x16c`: `lbu` at `+0x6c000`,
`+0x6c004`, `+0x6c008`, `+0x6c00c`) and the PROM probe (`0xbfc0e720`, `lbu` at `+0x6c000`). On the big-endian host that is bits 31:24 of the
word. NetBSD [public] reads the word and masks low bits of the same registers (`bus_space_read_4`; for example board revision =
`~word & 0xf`), which on the same host is the opposite lane. Both cannot see the same value unless the gate array drives every byte
lane the same. A faithful model for the shipped drivers returns the value in the most significant lane; replicating the byte across all four lanes also satisfies
NetBSD. Which the hardware does is **unknown**; the model rule and the full list of byte accesses are in the [host contract](../../platforms/express/host-contract.md#4-probe-answers-per-indigo-variant). Do not rely on the NetBSD behaviour as evidence.

## Decoding (established as software expectation)

`Gr2Probe` builds the board record. Board revision = `~port0 & 0xf` (zero means no board). Then:

| Item | Below revision 4 | Revision 4 and up |
|---|---|---|
| Backend revision | `(~port2 & 0xc) >> 2`, zero fails | `port1 & 3`, 3 fails |
| Monitor code | `(port1 & 1) | (port2 & 3) << 1` (0 to 7) | `port0 >> 4` (0 to 15) |
| Colour depth | slots A, B, C at `port3` bits 1:0, 3:2, 5:4, empty when both bits set: 24 with all three, 16 with A and B, else 8 | `port1` bit 4: 24, else 8 |
| Z buffer | present unless `port1` bits 3:2 are both set | `port1` bit 5 |
| Screen | 1280 by 1024, or 1024 by 768 when monitor code is 6 | same |

NetBSD agrees on the slot and depth tables [public] but treats the Z buffer as present only when both of `port1` bits 3:2 are
clear (`!(rd1 & 0xc)`), the opposite polarity of the binary. The kernel, both PROMs and the diagnostic program all use both-set as
absent (the IRIX source's diagnostic decode labels a field value of 3 "not installed" for every board slot), so for software the
polarity is settled; NetBSD's reading is the odd one and is unexplained. The super video field (`port2` bits 5:4, inverted, the
record byte at offset 56) is nonzero after inversion only when a super video board is fitted, and then gfxinfo prints a
"Video board revision" line, so an Indigo with none fitted reads 3 there.

The rest of `Gr2Probe`'s record (HQ2 and GE7 revisions) is in [hq2](../hq2/README.md).

## Write side: clock select and load

[binary] Start of the sequence in `gr2_earlyinit`/`Gr2Initialize` (`gr2.o` `0x59c`, `0x1988`): `Gr2Reset`, `Gr2StartClock`, `Gr2Init`;
`Gr2SetMonitor` repeats the clock load for a new timing file. Two protocols, chosen by board revision:

**Below revision 4** (`Gr2StartClock` `gr2_init.o` `0x454`): `port0` = 2 for monitor code 1, 1 for other codes (code 6 writes neither
`port0` nor the 17 bytes); `port1 = 0`; then the 17 command bytes of the table to `data`; `port1 = 0x40`. `Gr2SetMonitor` writes the
timing file's selector (1, 2 or 4) to `port0` first, then the file's 17 bytes, waits 1 ms, writes `port1 = 0` then `0x40` (`0x41` for an
interlaced file), and at the very end writes `0xa5` to `data`. The 17 bytes of the built-in table (`gr2_init.o` `.data+0x788`, also in the
4.0.5D PROM at `0xbfc4cea4`) are `c4 0f 15 20 30 4c 50 60 70 80 91 a5 b6 d1 e0 f0 c4`. They have a visible shape: the high nibble steps 0 to
f and the low nibble carries a value, one command per nibble of a register file. The Entry board's two clock tables (newport
`devices/vc1/timing-tables.md`) have the same shape and the same tail `b6 d1 e0 f0 c4` but different values in several bytes (1 to 3, 5, 6, 8, 10, 11), so
they are the same family of command stream, not the same table (inferred). The 17-byte table is identical in the 60 Hz and 72 Hz
files; the difference between them is the `port0` selector (1 versus 2), so below revision 4 the pixel frequency appears to be chosen by
hardware selection (inferred: an oscillator switch) and the command bytes configure something else (inferred). The other timing files change
only bytes 1 to 3, 5, 6 and 10.

**Revision 4 and up** (`Gr2StartClock` `0x500` onward): `port0 = 7`; then seven bytes (a different table per monitor, below)
sent as 56 single-bit writes to `data`, least significant bit first, the last bit with bit 1 also set; wait 3 microseconds;
`port1 = 0`, `port1 = 1` (`Gr2SetMonitor`: wait 1 ms, `port1 = 0`, then 1 or 5 for an interlaced file). Monitor code (low three
bits) 1 uses `00 00 00 04 05 04 06`, 6 (and 14) skips the load, every other code uses `00 10 00 15 18 01 0f` (the 60 Hz file's bytes).
The 72 Hz and 60 Hz sets are those two. The per-file bytes are in [vc1-express](../vc1-express/README.md#monitor-codes-and-the-kernels-built-in-tables).

## Which part

Unknown for revision below 4: nothing names it. For revision 4 and up a 56-bit serial load, **inferred only** to match the ICS1562
pixel clock generator that sheet 20 of the Indy XZ video board schematic (`VB-3_Schematic.pdf`, sheet title "Pixel Clock: ICS1562")
carries, together with a Bt438 clock part on sheet 22 for genlock. That board is the Indy XZ (GR4 plus VB3) not the Indigo's, so
topology does not transfer; board revision 4 and up is only the driver's name for a later generation of the Express back end. No
ICS1562 datasheet is held in the Library (searched `ICS1562`, text and artifact modes, no hits), so the 56-bit word is not decoded.
What frequency each byte set produces: unknown. The 1280 by 1024 files at 60 Hz and 72 Hz imply roughly 108 and 130 MHz
pixel clocks if timing totals are conventional; unverified (the line-program format is not decoded).

## Qtests

(a) A byte read at `port0` returns the complemented board revision in its low nibble; (b) a clock load below revision 4 is 17 `data`
writes, at revision 4 and up 56; (c) `Gr2Probe` against the model reads depth, Z and monitor as configured.

Open items: [questions/display.md](../../questions/display.md).
