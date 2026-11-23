# XMAP5: window and colour mapper (five per Express board)

What the five XMAP5 chips do between the VC1 and the DACs, where the host reaches them, and what the Indigo PROM and IRIX IP20
driver write. Registers and grades are in [registers.toml](registers.toml). Labels follow [AGENTS.md](../../AGENTS.md):
**established**, **inferred**, **unknown**. Every fact also carries a source class: **[public]** (published datasheets and the
Elan Graphics Technical Report, the public NetBSD `grtwo.c` and `grtworeg.h`), **[binary]** (shipped IRIX 6.5 `gr2.a` members
`gr2_init.o`, `gr2.o`, `gr2_retrace.o`, `gr2_tport.o`, PROM 4.0.5D `070-8116-004` and 4.0.5G `070-8116-005`), or
**[vendor-derived]** (the upstream `XMAP5.h`, generated from vendor source: a hypothesis only, never the sole support of an
established fact, not cited from QEMU pages). Offsets are from the graphics window base (physical `0x1f000000` on the
Indigo). Nothing was read on a board.

## What it is

[public] Elan Graphics Technical Report 1.0, section 4.4.2: five Multimode Graphics Processors (XMAP5) receive the cursor
information from the VC1 and the display ID of each pixel; the display ID decides how image data is routed to the DACs; overlay
and underlay planes take precedence over the image planes, a 16 by 24 auxiliary lookup table colours them, the cursor has the
highest precedence and a three-entry, 24-bit cursor colour table; each chip is 18,000 gates at 25 MHz (section 2.1). Section 4.4.3:
in colour-index mode a pixel indexes a 12-bit-in, 24-bit-out map (4096 colours simultaneously visible). Five chips because the
board has five parallel pixel pipes whose output the Bt457 DACs multiplex 5:1 (see [Bt457](../bt457/README.md)); which pixel
column goes to which chip is **inferred** (x modulo 5; the VC1's width divider is by five, see
[VC1](../vc1-express/README.md#internal-registers)).

Chip count per variant: five is established for the Elan ([public] TR; the board schematic of the Indy XZ set, `VB-3_Schematic.pdf`,
shows XMAP LUT channels A to E, but that is a different host and board, so it only corroborates the part count). The IP20 driver
does not branch on variant for any XMAP5 access (it uses the broadcast window and chip 0), so XS, XS24 and XZ presumably carry
five as well; that is **inferred**, nothing shipped counts XMAPs.

## Addressing: five windows and a broadcast window

Each chip has a 0x20-byte window with eight registers on a 4-byte stride. Chip n is at `+0x6c100 + 0x20 * n`; the broadcast
("all") window is the next one, `+0x6c1a0`. Register layout in a window (from [registers.toml](registers.toml)):

| Window offset | Register | Access seen | Grade |
|---|---|---|---|
| `+0x00` | misc | byte writes | established as a port; contents inferred |
| `+0x04` | mode | word writes | established |
| `+0x08` | clut | byte writes | established |
| `+0x0c` | crc | none | unknown |
| `+0x10` | addrlo | byte read and write | established |
| `+0x14` | addrhi | byte read and write | established |
| `+0x18` | bytecount | none | unknown |
| `+0x1c` | fifostatus | byte read | established |

Establishing the window layout from the shipped driver, not from NetBSD: [binary] `Gr2RetraceHandler` (`gr2_retrace.o` `0x0`)
reads chip 0's address pair from `+0x6c110` and `+0x6c114` and restores it through `+0x6c1b0` and `+0x6c1b4`; the status is read at
`+0x6c11c` (chip 0 window `+0x1c`); mode and colour writes go to `+0x6c1a4` and `+0x6c1a8`; `_Gr2XMAPInit1` to `3` and the PROM
(`0xbfc0eafc`) write the broadcast pair at `+0x6c1b0` and `+0x6c1b4`. All of that is consistent with the broadcast window
being the sixth 0x20 window, so its address registers sit at window offsets `+0x10` and `+0x14`. Established.

**The open question is settled.** NetBSD's `grtworeg.h` [public] puts the broadcast address registers at `+0x6c190` and `+0x6c194`
(and its CLUT writes through `+0x6c1a8`). Those two addresses are window offsets `+0x10` and `+0x14` of chip 4 (`+0x6c180`), not
of the broadcast window. The IRIX driver and PROM use `+0x6c1b0` and `+0x6c1b4` everywhere (every one of the five `_Gr2XMAPInit*`
and `Gr2TpMapcolor` sites), so for a model the broadcast address pair is `+0x6c1b0` and `+0x6c1b4`. NetBSD's console loads colours
0 to 7 by setting chip 4's pointer alone and then broadcasting three CLUT bytes per colour; chips 0 to 3 then store at whatever pointer they
already held. It only works if the PROM left every chip at address 0 (inferred). Do not model `+0x6c190` as a broadcast alias.

A write through the broadcast window updates all five chips (the mode, CLUT, misc and address ports). Established as the intent
(the driver never writes a single chip). Reads from the broadcast window are never used; chip 0's window is the only one read.

## The address pair and the three data ports

The pair (addrhi, addrlo) is a 13-bit pointer into whichever table the next data-port access targets:

- **Mode table** (`mode`, word): 32 entries, one per display ID, **byte-addressed** as `4 * ID` (so addrhi 0, addrlo 0 to 124).
  [binary] `Gr2SetDisplayMode` (`gr2_retrace.o` `0x480`) and the retrace swap loop write `addrlo = ID << 2`, `addrhi = 0`, then
  store the 32-bit word. [public] TR 4.4.1: up to 32 simultaneous window styles. The driver sets the address before every
  write, so whether it advances after a write is **unknown**.
- **Colour table** (`clut`, bytes R, G, B): index = `(addrhi << 8) | addrlo`, addrhi masked to five bits, so 8192 entries of
  24 bits. [binary] `Gr2TpMapcolor` (`gr2_tport.o` `0x8`) writes index = 4096 + colour as `addrhi = (index & 0x1f00) >> 8`,
  `addrlo = index`, then R, G, B. [public] NetBSD uses the same mask. The pointer advances after the B byte (established from the init
  clear: 31 passes of 256 entries with no address write between them, `_Gr2XMAPInit3` `0x6e0`), carrying from low into high.
- **Misc** (`misc`, bytes): after `addrhi = addrlo = 0`, `_Gr2XMAPInit1` writes five bytes `0, 0, 0, 14, 0` to the one port, so it
  auto-increments through at least five internal registers (inferred). What they are is **[vendor-derived]** only
  (blackout colour R, G, B, a 4-bit popup page value, cursor index); no shipped reader or writer after init was found.

All three tables share the one pointer, so a write sequence must set the pair first. A qtest can discriminate: after a CLUT write
the pointer reads back advanced by one entry; the mode and misc increments are unknown.

## fifostatus

[binary] Only chip 0's status (`+0x6c11c`) is ever read, always as a byte.

- Bit 0 set means busy: `Gr2BlankScreen` (`gr2_init.o` `0xfe8`) polls up to 10000 times with a 1 microsecond delay for it to clear
  before touching the DACs; the retrace handler (`gr2_retrace.o` `0x130`, `0x458`) and `Gr2SetGammaRamp` (`0xfe8`) poll without
  a bound; each does so before XMAP or DAC writes. Established.
- Bit 1 set means the FIFO has room for a burst: `_Gr2XMAPInit3` waits for it to be set before every 256-entry block of CLUT
  writes, giving up after 10000 microseconds and writing anyway. Established.
- An idle chip therefore reads bit 0 clear and bit 1 set. A model that returns `0x02` always satisfies every shipped poll.
- Bit 2 as an overflow flag, and a 512-word FIFO, are **[vendor-derived]** only.

NetBSD [public] never polls it; `grtwo_wait_gfifo` waits on the INT2 FIFO line instead.

## Initialisation as shipped

`_Gr2RegisterInit` (`gr2_init.o` `0x7a8`) calls the three XMAP routines last, after VC1 setup and the DACs. Each step is read in
full, so established as a sequence of stores:

1. `_Gr2XMAPInit1` (`0x654`): broadcast `addrhi = 0`, `addrlo = 0`; word `0x82000000` to the broadcast `mode` port (mode table entry 0);
   `addrhi = addrlo = 0` again; five bytes `0, 0, 0, 14, 0` to the broadcast `misc` port.
2. `_Gr2XMAPInit2` (`0x690`): `addrhi = 16`, `addrlo = 0`; then eight three-byte entries to the broadcast `clut` port: black, red
   (255, 0, 0), green, yellow, blue, magenta, cyan, white. These are the text port's eight colours at CLUT index 4096 to 4103.
3. `_Gr2XMAPInit3` (`0x6e0`): `addrhi = 1`, `addrlo = 0`; then 7936 zero entries (indices 256 to 8191), waiting on chip 0's status
   bit 1 before each block of 256. Index 4096 to 4103 are inside that range, so step 2's colours are overwritten with black. The
   kernel's text port reloads them through `Gr2TpMapcolor` (`+4096`). Index 0 to 255 are not written, left as the hardware had them.

PROM 4.0.5D does only the first step (`0xbfc0ea9c` to `0xbfc0eb74`, the same ten stores; on a board whose backend revision byte is 1 it first
waits up to 20000 microseconds for the retrace status bit, see the [platform page](../../platforms/express/display.md)). It
has no routine that clears or loads the CLUT in bulk: the only CLUT writer in the image is its text port's mapcolor at `0xbfc2cce8`,
which adds 4096 to the colour number exactly as `Gr2TpMapcolor` does. So after the PROM only mode entry 0 is written and the colour table is
whatever the power-on state was, plus the text port's colours. Mode entries 1 to 31 and CLUT entries below 4096 are unspecified
after either path.

## Mode word

One 32-bit word per display ID. Only the boot word is established: DID 0 = `0x82000000`. Everything else is graded **inferred**
from three kinds of evidence, none of which alone fixes a field:

- [binary] The text port's colours sit at CLUT index 4096 + n, and `0x82000000` has `0b10000` in bits 31:27: 16 pages of 256 entries
  reach 4096. So bits 31:27 select the CLUT page for colour-index pixels (inferred).
- [binary, from an upstream decompilation of the shipped X server `gr2.so`; not re-checked against the object here] the server builds
  `page << 27 | 0x800 | base`, ORs `0xf00000` when bit 8 of the word is clear, and toggles `0x01000000` for the second buffer of a
  double-buffered window. So bit 24 selects buffer 0 or 1, bits 23:20 are overlay enables, bit 8 is an underlay enable, `0x800` is
  an auxiliary-colour page of 4 (bits 13:9). Inferred.
- [vendor-derived] the upstream `XMAP5.h` names bits 26:24 the pixel mode (4, 8, 12, 16, 24 bits per pixel, banks 0 and 1),
  bits 17:16 colour index versus direct RGB, bits 19:18 alternate video, bits 7:0 popup fields. Where this agrees with a [binary]
  point above it is cited as agreement; the rest stays **unknown** in the TOML.

[public] The TR says RGB mode sends 8 bits per colour to the DACs and colour-index mode indexes a 12-bit-in, 24-bit-out map; that
the mode word is where that choice is made is inferred. A QEMU model should store all 32 words per chip and implement at least:
CLUT page lookup (bits 31:27) for index modes, direct RGB passthrough, the buffer bit, overlay enables and the auxiliary-colour
block at CLUT index `0x1c00 + 16 * aux_page`. That last location is **[vendor-derived]** only (the cursor colours at index `0x1c01`
to `0x1c03` and the auxiliary block are not touched by any shipped IP20 object or PROM routine read here); questions/xmap5.md lists the next route.

## Double-buffer swap

[binary] `Gr2RetraceHandler` walks the 32 pending-swap slots in the retrace interrupt; for each slot flagged pending it writes
`addrlo = ID * 4`, `addrhi = 0`, then the slot's new mode word to the broadcast `mode` port, bracketing the loop by saving chip 0's
pointer and restoring it through the broadcast pair. It first waits for `fifostatus` bit 0 clear. Established. The swap is
therefore one mode-word write per window, applied at retrace.

## What a QEMU model needs

Per chip: 32 mode words, 8192 CLUT entries of 3 bytes, a misc register file, an address pointer with CLUT auto-increment, a status
register that reads `0x02`. Broadcast writes fan out to all five chips. For scan-out the model needs the mode word interpretation
(inferred) and the per-pixel display ID from the [VC1](../vc1-express/README.md). Discriminating qtests: (a) broadcast write of
`0x82000000` at address 0 then a per-chip read of nothing (no read path exists, so only the CLUT is observable through scan-out);
(b) CLUT three-byte write increments the pointer; (c) status reads `0x02` idle.

Open items: [questions/xmap5.md](../../questions/xmap5.md).
