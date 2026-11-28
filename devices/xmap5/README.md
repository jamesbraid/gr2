# XMAP5: window and colour mapper (five per Express board)

What the five XMAP5 chips do between the VC1 and the DACs, where the host reaches them, and what the Indigo PROM and IRIX IP20
driver write. Registers and grades are in [registers.toml](registers.toml). Labels follow [AGENTS.md](../../AGENTS.md):
**established**, **inferred**, **unknown**. Every fact also carries a source class: **[public]** (published datasheets and the
Elan Graphics Technical Report, the public NetBSD `grtwo.c` and `grtworeg.h`), **[binary]** (shipped IRIX 6.5 `gr2.a` members
`gr2_init.o`, `gr2.o`, `gr2_retrace.o`, `gr2_tport.o`, PROM 4.0.5D `070-8116-004` and 4.0.5G `070-8116-005`), **[source]** (the IRIX 6.5.7 diagnostic program's XMAP5 test, `irix-6.5.7/stand/arcs/ide/fforward/graphics/EXPRESS/xmaptest1.c` and `xmap.h` in the IRIX source tree; first-rank evidence under [AGENTS.md](../../AGENTS.md)), or
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
[VC1](../vc1-express/README.md#timing-image-format)).

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

A write through the broadcast window updates all five chips (the mode, CLUT, misc and address ports). **Inferred** from the window's
name and the driver's use (the driver never writes a single chip; no binary or public text states the fan-out). Reads from the broadcast window are never used; chip 0's window is the only one read.

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
- **[source]** The diagnostic program's XMAP5 test names bit 0 "empty", bit 1 "half full" and bit 2 "overflow" and gives the FIFO a depth of 512. Its own
  use of bit 0 (it waits while the bit is set) matches the kernel's "busy", so the name describes the clear state; the kernel's use of bit 1 (wait for it to be
  set before a burst) is the opposite of the name "half full", so that bit is probably active low. No shipped program reads bit 2. Grade: names and depth
  established as the diagnostic's; the sense of bits 1 and 2 inferred.

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

One 32-bit word per display ID. The boot word for display ID 0 is `0x82000000`. Field boundaries and the value codes are **established** from the IRIX source:
the diagnostic program's XMAP5 test (`stand/arcs/ide/fforward/graphics/EXPRESS`, its test file and the small header beside it)
composes mode words from named fields, and the shipped X server and kernel agree with it where they touch the word. The roles are read from the
field names and from which values the diagnostic pairs, so a role says **inferred** where the table below says so.

| Bits | Field | Values | Grade and basis |
|---|---|---|---|
| 31:27 | pixel page | CLUT page (256 entries) read by colour-index pixels; 0 to 31 | Established [source] field, [binary] the boot word is page 16 and the text port's colours sit at CLUT index 4096 (`Gr2TpMapcolor`); the X server builds `page << 27` from a word of its hardware colormap record, the page number (`expValidateMode`, `gr2.so` `0x5ef52fe8`, the shift at `0x5ef530fc`; that the word is the page number is inferred from the use) |
| 26:24 | pixel mode | 0 and 1 four-bit, 2 and 3 eight-bit, 4 and 5 twelve-bit (bank 0 and 1), 6 sixteen-bit, 7 twenty-four-bit | Established [source] codes. The low bit is the bank: `expValidateMode` sets or clears bit 24 from two flag bits of the request record (`0x5ef53114` to `0x5ef53128`, `0x5ef531c8`: flag bit 1 present, bit 2 chooses the bank), the same bank the retrace handler flips |
| 23:20 | overlay enables | four bits | Established [source] field; the X server ORs `0xf00000` whenever bit 8 is clear (`0x5ef531bc`). Which overlay plane each bit enables is inferred |
| 19:18 | alternate video | 0 off, 1 over, 2 under, 3 replace | Established [source] field and codes; zero in every word the diagnostic composes and in everything shipped read here, so what the XMAP does with it is unknown |
| 17:16 | pixel data format | 0 colour index, 1 direct RGB, 2 colour-index multimode, 3 blackout | Established [source] codes for 0 to 2; 3 (blackout) is inferred, as the only source for it is a header constant's name. The diagnostic pairs RGB with 24, 16, 12 and 8-bit and four-bit pixel modes, colour index with 12, 8 and four-bit, and multimode with the two four-bit modes only |
| 15:14 | popup pixel, popup override | one bit each | Names only [source]; inferred, nothing read sets them |
| 13:9 | auxiliary page | five bits | Established [source] field; the X server ORs `0x800` into every word, which is page 4 (`0x5ef53100`) |
| 8 | underlay enable | one bit | Established [source] field; the X server tests it (`0x5ef53108`) |
| 6:5, 4:0 | popup mode, popup page | codes off, eight-bit, four-bit bank 0, four-bit bank 1; page of five bits | Names and codes only [source]; the diagnostic writes a page and never a mode. The header also defines a popup field at bits 8:7 that overlaps bit 8, so one of the two descriptions belongs to another view of the word: unknown which |

What this answers for a driver or model:

- **Eight-bit colour index:** pixel mode 2 (bank 0) or 3 (bank 1), format 0, page in bits 31:27. The boot word is exactly this with page 16 and every other field zero (its low 24 bits are zero).
- **Twenty-four-bit RGB:** pixel mode 7, format 1; the page is ignored for direct pixels (inferred: the diagnostic writes it zero for RGB). **Twelve-bit double-buffered RGB** is pixel mode 4 or 5 with format 1, the bank being the buffer; **twelve-bit colour index** is the same modes with format 0 and a page.
- **Which CLUT page the default window reads:** whatever page its mode word names. The text port uses page 16 (index 4096 to 4103); the kernel's `Gr2TpMapcolor` writes `4096 + n`; the 4.0.5D PROM loads its two console colours at 3073 and 3074, which lie in page 12 (entries 1 and 2 of 3072 to 3327), not in the page 16 its own boot word selects: nothing read says what selects page 12, so which window those two colours serve is unknown.
- **Cursor colours:** not in the mode word. The X server writes the cursor's colours as three ordinary colour-table entries at **CLUT indices `0x1c01`, `0x1c02` and `0x1c03`** (`expDisplayCursor`, `gr2.so` `0x5ef6115c`: it builds a three-entry write record, indices at `0x5ef612cc`, `0x5ef612d8` and `0x5ef612dc`, and the first two entries take the cursor's two colours; the third takes a further colour or zero). Established [binary] for the indices and the byte order of the record; that these entries are the XMAP's cursor colour table is inferred from the number and the TR's three-entry cursor table. The X server's pixel-read conversion (`expReadConvertPixels`, `0x5ef63574`) looks overlay pixels up at `0x1c00` ORed with the pixel and a page term (`0x5ef637a8`, `0x5ef637e4`, `0x5ef63818`; the term was not traced), so CLUT page 28 (`0x1c00` to `0x1cff`) holds the overlay and cursor colours; that agrees with the vendor-derived note that the auxiliary block sits at `0x1c00 + 16 * aux page`, which stays a hypothesis for the block's exact layout.
- **Display IDs and clip IDs:** the per-pixel 5-bit display ID comes from the VC1's line tables and selects the mode-table entry ([VC1](../vc1-express/README.md#display-ids)); the XMAP5 mode word has no clip-ID field. Clip IDs are a separate four-bit plane set that the X server draws into with rectangle tokens ([x-server-tokens.md](../../platforms/express/x-server-tokens.md#clip-id-draw)), so the XMAP does not see them.
- **Writing a window's word at run time:** the X server's `expValidateMode` assembles the word and asks the kernel to apply it (`ioctl` request 1017, `RRM_LOADDISPLAYMODE` in the shipped `sys/rrm.h`, with a five-word record: a context word, the X window id, the display ID, the mode word and the flags); `Gr2SetDisplayMode` writes `addrlo = ID << 2`, `addrhi = 0`, then the word; that the request reaches it through the resource manager is inferred (`rrm.o` is not read). A double-buffer swap rewrites the word for the window at the next retrace (below).

The `misc` bytes: the same diagnostic names the first three blackout red, green and blue, the fourth a popup page value and the fifth a cursor value, and sizes the file at six bytes [source]. Init writes `0, 0, 0, 14, 0`, so it sets the popup page value to 14 and the cursor value to 0 where the diagnostic uses 0 and 15. Inferred roles; no shipped code reads them back.

## Double-buffer swap

[binary] `Gr2RetraceHandler` walks the 32 pending-swap slots in the retrace interrupt; for each slot flagged pending it writes
`addrlo = ID * 4`, `addrhi = 0`, then the slot's new mode word to the broadcast `mode` port, bracketing the loop by saving chip 0's
pointer and restoring it through the broadcast pair. It first waits for `fifostatus` bit 0 clear. Established. The swap is
therefore one mode-word write per window, applied at retrace.

## What a QEMU model needs

Per chip: 32 mode words, 8192 CLUT entries of 3 bytes, a misc register file, an address pointer with CLUT auto-increment, a status
register that reads `0x02`. Broadcast writes fan out to all five chips. For scan-out the model needs the mode word interpretation
(the table above) and the per-pixel display ID from the [VC1](../vc1-express/README.md). Discriminating qtests: (a) broadcast write of
`0x82000000` at address 0 then a per-chip read of nothing (no read path exists, so only the CLUT is observable through scan-out);
(b) CLUT three-byte write increments the pointer; (c) status reads `0x02` idle.

Open items: [questions/xmap5.md](../../questions/xmap5.md).

## Review (2026-11-23)

Independent re-read of `gr2_init.o`, `gr2_retrace.o`, `gr2_tport.o` and PROM 4.0.5D (disassembly), plus the public NetBSD `grtworeg.h`.

- CONFIRMED: every XMAP access in the six kernel objects uses `+0x6c110`, `+0x6c114`, `+0x6c11c` (chip 0) or `+0x6c1a0` to `+0x6c1b4` (broadcast); no other offset in `+0x6c100` to `+0x6c1bf` is touched. The broadcast address pair is `+0x6c1b0` and `+0x6c1b4` everywhere; NetBSD's `+0x6c190` and `+0x6c194` are window offsets `+0x10` and `+0x14` of chip 4 (arithmetic checked), so the page's resolution holds.
- CONFIRMED: `_Gr2XMAPInit1` store sequence (addrlo/addrhi 0, mode word `0x82000000` at `+0x6c1a4`, five misc bytes `0 0 0 14 0` at `+0x6c1a0`); `_Gr2XMAPInit2` (addrhi 16, eight three-byte entries); `_Gr2XMAPInit3` (addrhi 1, status bit 1 wait, 31 blocks of exactly 256 entries, so 7936 entries and no address write between blocks, 10000 microsecond bound).
- CONFIRMED: mode entry address is `ID << 2` with addrhi 0 (`Gr2SetDisplayMode` `gr2_retrace.o` `0x480`, retrace swap loop); text-port colour `4096 + n` with `addrhi = (index & 0x1f00) >> 8` (`Gr2TpMapcolor`, `gr2_tport.o` `0x8`); status bit 0 polls (`0x130`, `0x458`, `Gr2BlankScreen`, `Gr2SetGammaRamp`) and bit 1 (`_Gr2XMAPInit3`); the PROM's console colours go to indices 3073 and 3074 (`0xbfc0f590`).
- CONFIRMED: "CLUT 8192 entries of 24 bits": inferred from the 13-bit pointer and the init clear to index 8191; the pointer advancing after the third byte is established from the 31 unaddressed blocks.
- GRADE (fixed in this review): "broadcast writes update all five chips" was marked established; no binary or public text states the fan-out, so it is inferred. Reworded.
- GRADE (fixed): the X server decompilation bullet was tagged [binary] while saying it was not re-checked and came from the upstream decompilation. Retagged unverified; the fields it names stay inferred and must not be cited as [binary].
- UNVERIFIED: the mode-word field meanings other than the boot word (as the page says), the auxiliary colour block at `0x1c00` (vendor-derived only), the PROM 20000 microsecond retrace wait, PROM 4.0.5G.
- The registers.toml grades match the page; `misc` is correctly inferred and tagged vendor-derived; `fifostatus` established rests on binary reads, with only bit 2 vendor-derived.
