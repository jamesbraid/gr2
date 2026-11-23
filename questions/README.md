<!-- keep -->
# Open questions

Each entry: the question, the routes tried, the next route. When answered, move the answer into the owning page and delete the
entry.

## 1. Which register is the HQ2 version, and what is `+0x6a040`?

IP20 `gr2.o` reads `+0x6a040` as a status word: bits 12:6 are compared with thresholds (35, 36, 40, 41, 63) in the FIFO
interrupt, poll and timeout routines, and bit 5 triggers an error message. NetBSD `grtworeg.h` names the same offset `VERSION`
and `grtwo_setup_hw` takes a revision from `(word & 0xff000000) >> 23`. Routes tried: both sources read. Next: `Gr2Private` and
`Gr2Info` in `gr2.o`, then the PROM graphics diagnostic and `ide.IP20`, which may print a version.

## 2. Which byte lane carries the board revision registers?

`Gr2Probe` reads `+0x6c000`, `+0x6c004`, `+0x6c008`, `+0x6c00c` with byte loads at offset 0 of each word, the most significant lane
on a big-endian host. NetBSD reads the word and masks low bits, which on the same host is the least significant lane. Either the
board drives the value on all lanes, or one of the two never worked. Routes tried: both read. Next: the PROM probe
(`0xbfc0e6f0`) for the access width it uses; the Bt457 and VC1 datasheets say nothing about this gate-array register.

## 3. Where is the GE7 revision: `+0x683f4` or `+0x680fc`?

The IP20 kernel writes 0 to `+0x683f4`, reads it back and keeps bits 7:5. NetBSD reads `+0x680fc` and keeps bits 7:4 shifted by 5.
Routes tried: both read. Next: other GE7 slot-0 accesses in `ide.IP20` and the GE7 microcode.

## 4. XMAP5 address window

The kernel's "all XMAP5" low-address and high-address registers are at `+0x6c1b0` and `+0x6c1b4` (`_Gr2XMAPInit*` stores at
`+0x6c1b0`/`+0x6c1b4`), one 0x10 step above the mode/CLUT registers. NetBSD's header puts the "all" address registers at
`+0x6c190` and `+0x6c194`. Routes tried: both read. Next: confirm against the per-chip window layout once its register
list is read.

## 5. Indigo2 Extreme and XZ

Which Express-family boards the Indigo2 carries, and with what chip counts, is unknown: the IP20 driver handles eight geometry
engines and the GL core names `-Extreme`, but no Indigo2 object has been read. Next: the Indigo2 kernel objects and
`IP22GR2NG1` GL library, plus the Elan TR sections not yet read.
