# VC1 on the Express board: timing, cursor and display IDs

The Express-side port set, init and monitor-load sequences for the VC1, the chip that generates the video timing, the hardware
cursor and the per-pixel display ID. The Entry (LG1) board's use of the same part is on the newport repository's `devices/vc1`
page (the newport repository); this page does not repeat it and notes only where Express differs. Registers are in
[registers.toml](registers.toml).

Labels: **established**, **inferred**, **unknown** ([AGENTS.md](../../AGENTS.md)). Source classes: **[public]** (published docs and
public NetBSD `grtwo.c`/`grtworeg.h`), **[binary]** (shipped IRIX 6.5 `gr2.a` members `gr2_init.o`, `gr2.o`, `gr2_retrace.o`,
the `usr/gfx/ucode/GR2/vof` timing files, PROMs `070-8116-004` 4.0.5D and `070-8116-005` 4.0.5G), **[vendor-derived]** (upstream
`VC1.h`; hypothesis only). Offsets are from the graphics window base. Nothing was read on a board.

## Chip identity

[public] Elan Graphics Technical Report section 2.1: VC1 is a 50,000 gate, 50 MHz design providing "video timing control for the
output monitor, run-length encoded windowing tables, and the cursor"; section 4.4.1: a 32 by 32, three-colour cursor glyph, a
window display ID per pixel in a run-length table, up to 32 window styles, and these monitor types: 72, 60 and 30 Hz at 1280 by
1024; 72, 60 and 30 Hz at 1024 by 768; NTSC and PAL unencoded; 120 Hz stereo at both sizes. Same chip as the Entry board's
`L1A6654 VC1` (newport page). VC1 revision: [binary] addrhi 0, addrlo 5, read `testreg`, keep bits 2:0 (`Gr2ProbeVC1`,
`gr2_init.o` `0x148`; PROM `0xbfc0ed2c`). Unlike LG1 the driver stores the raw value (no subtract one). What a part returns: unknown.

## Ports (established)

Seven ports on a 4-byte stride from `+0x6c040`: `command` (half-word), `xmapmode` (never touched, unknown), `sram` (half-word),
`testreg` (byte, read-only), `addrlo`, `addrhi`, `sysctl` (bytes). `command` and `sram` auto-advance the 16-bit address pair by 2 per
half-word (inferred from sequences: `Gr2LoadVC1SRAM` sets the pair once and streams up to 1024 half-words; the cursor x then y
writes land at 0x22 then 0x24 with one address set). `addrlo`, `addrhi` and `sysctl` read back what was written (the retrace
shadow reads all three, `Gr2FillVc1Shadow`). The pair addresses either an internal register (small numbers, through `command`) or the
external SRAM (through `sram`); they are different windows selected by which port is used, not by the address.

Differences from LG1 (newport page): LG1 uses a selector and byte data with a "GO" alias; Express has a direct port per window and
half-word data; SRAM addresses are byte addresses here as there; the cursor glyph is at SRAM `0xa00` (kernel; PROM `0x200`) rather
than `0x3000`; the display-ID tables are half-word lists, not byte records (below).

## Init (kernel `_Gr2RegisterInit`, `gr2_init.o` `0x7a8`; PROM `0xbfc0ed5c`)

All established, in order:

1. Pulse INT2 port register `0x1fb801df` bit 3 (clear, then set): the retrace interrupt latch clear (chips interrupts page).
2. Initialise the three Bt457 DACs ([bt457](../bt457/README.md)).
3. `sysctl = 1`, `addrhi = 0`, `addrlo = 0x26`, `command = 0` (internal register 0x26, cursor mode); `addrhi = 9`, `addrlo = 0xf0`,
   `sram = 0` (interlace half-word at `0x9f0`), then `sram = width` (at `0x9f2`; width from the probe: 1280, or 1024 for monitor code 6).
4. Load timing images by monitor code (next section) with `Gr2LoadVC1SRAM(addr, image, count)`: set `addrhi:addrlo` to the SRAM
   address, then write `count` half-words to `sram`.
5. Set register 0 (`VID_EP`) to the frame table pointer: `0x800` if the width is below 1026, else `0x900`.
6. Build the display-ID tables (below), set register `0x14` to 0, `0x40` to `0xb00`, `0x42` to `0xb00 + 2 * height`, `0x44` to `0xff04`,
   `0x60` to 0.
7. `initGr2Cursor`: write 256 zero bytes at SRAM `0xa00` (128 half-words), then register `0x20 = 0xa00` and three zero half-words
   (registers `0x22` x, `0x24` y, `0x26` mode).
8. `sysctl = 0x0c`, then the XMAP5 init ([xmap5](../xmap5/README.md#initialisation-as-shipped)).

The PROM matches except its own tables (its monitor code 1 image sizes are 122, 25, 128, 25 half-words; others 165, 24, 163, 24;
the data are in the PROM, not in `.u` files), a cursor glyph at SRAM `0x200` (256 half-words), a final `sysctl` of `0x3c` (adds the
cursor logic and cursor display bits), and `0xff04` for register `0x44` at 1280 wide.

## Monitor codes and the kernel's built-in tables

The monitor code is read from the board configuration ports ([clock](../clock/README.md)). `_Gr2RegisterInit` picks images by
`code`, [binary]:

| Monitor code | Images loaded | Same bytes as |
|---|---|---|
| 1 and 9 | set B: line list 400 bytes at `0x0`, frame table 56 bytes at `0x800`, cursor line list 384 bytes at `0x400`, cursor frame table 56 bytes at `0x900` | `vof/72hz.u` (byte for byte, checked) |
| 6 and 14 | none | the timing is loaded later by the monitor-set ioctl |
| everything else | set A: 474, 50, 436 and 50 bytes at the same four addresses | `vof/60hz.u` (byte for byte, checked) |

So on an unconfigured board the codes mean (inferred from the match): 1 and 9 are 72 Hz 1280 by 1024, 6 and 14 await a user timing
file, all others are 60 Hz 1280 by 1024. The probe sets the screen to 1024 by 768 only for code 6 (revision below 4) and 1280 by 1024
otherwise. Which physical monitor each code means: unknown (no document ties code to monitor).

## Timing image format

One timing file (`.u`) is a block loaded by `Gr2SetMonitor` (`gr2.o` `0x2860`) from user space; layout from the code, [binary]:

| File offset | Content |
|---|---|
| `0x000` | big-endian 32-bit byte count, then the line-program list loaded to SRAM `0x0000` |
| `0x3bc` | count, then the frame table loaded to `0x0800` |
| `0x424` | count, then the cursor line list loaded to `0x0400` |
| `0x7e0` | count, then the cursor frame table loaded to `0x0900` |
| `0x848` | 32-bit clock selector (board revision below 4: port0) |
| `0x84c` | 17 clock command bytes (below 4) |
| `0x860` | width, height, interlaced flag, cursor x adjustment, cursor y adjustment (five 32-bit words) |
| `0x874` | 32-bit format id (stored at byte 55 of the board record: 1 60 Hz, 2 NTSC, 9 PAL, 23 72 Hz, ...) |
| `0x878` | 7 clock bytes (revision 4 and up), 8 bytes with a pad |

Files are 2176 bytes. The built-in sets are exactly `60hz.u` and `72hz.u`. The files held (extracted from the IRIX 6.5 media, sizes
in [references/binaries.md](../../references/binaries.md)):

| File | Size | Interlaced | Cursor x/y adj | Format id | Selector | Rev 4+ clock bytes |
|---|---|---|---|---|---|---|
| `30hz.u` | 1280x1024 | yes | 130 / 53 | 0 | 4 | `00 20 00 15 18 01 0f` |
| `48hz.u` | 1280x1024 | no | 250 / 168 | 30 | 1 | `00 10 00 15 18 01 0f` |
| `50hz.u` | 1280x1024 | no | 250 / 35 | 24 | 4 | `00 10 00 15 1b 05 15` |
| `60hz.u` | 1280x1024 | no | 250 / 35 | 1 | 1 | `00 10 00 15 18 01 0f` |
| `72hz.u` | 1280x1024 | no | 240 / 34 | 23 | 2 | `00 00 00 04 05 04 06` |
| `ccir50.u` | 1280x1024 | no | 250 / 35 | 24 | 4 | `00 10 00 05 2c 05 1f` |
| `ccir60.u` | 1280x1024 | no | 250 / 35 | 1 | 1 | `00 00 00 05 27 05 2e` |
| `iris3k.u` | 1025x768 | no | 150 / 39 | 5 | 4 | `00 10 00 04 06 03 07` |
| `presenter.u` | 1025x768 | no | 145 / 30 | 29 | 4 | `00 10 00 04 06 03 07` |
| `presenter1280.u` | 1280x1024 | no | 250 / 35 | 1 | 4 | `00 10 00 15 18 01 0f` |
| `st492.u` | 1280x1024 | no | 250 / 34 | 15 | 1 | `00 10 00 15 18 01 0f` |
| `ntsc.u` | 640x485 | yes | 60 / 14 | 2 | 4 | `00 20 00 04 05 05 12` |
| `pal.u` | 780x575 | yes | 90 / 20 | 9 | 4 | `00 20 00 04 18 03 39` |
| `rs343a.u` | 1280x960 | yes | 150 / 26 | 14 | 4 | `00 20 00 15 2c 01 1e` |

(All established as bytes, read in full. A 1024-wide mode is stored with width 1025. The `00 10`/`00 20` leading bytes of the
revision 4 clock stream track progressive versus interlaced; meaning inferred.) 120 Hz stereo and the 1024 by 768 60 and 72 Hz
files named in the TR are not among the files held; the held `iris3k.u` and `presenter.u` are 1024-class.

`Gr2SetMonitor` sequence, [binary]: blank the screen (`Gr2BlankScreen`, arg 1); save `sysctl` and the address pair; `sysctl = 3`;
send two FIFO commands to the HQ2 (token 108 then height - 1 at `+0x40008`, outside this page's scope); wait for HQ2 status bit 0;
start the pixel clock ([clock](../clock/README.md)); set register 0 to `0x800` or `0x900` (see the cursor rule below); load the four
images; register `0x14 = 8192` for a loaded file; update the board record width, height, format id and cursor adjustments;
register `0x44 = ((w-1)/5) << 8 | ((w-1)%5)` for width 1280 (`w/5, w%5` below 1280, untouched above); SRAM `0x9f0` = 0 or 16 (progressive
or interlaced file) then width at `0x9f2`; rebuild the display-ID tables; restore `sysctl & ~0x43` and the address pair; unblank.

### Frame table and line programs

Frame table entries, established as bytes and as a shape: a header byte (4 for the 1280 files), then 3-byte records
(line count, 16-bit line-program address in the first list), ending with `ff ff`. The 60 Hz table decodes as 41 lines at `0x5c`, 3 at `0x0`,
2 at `0x2f`, 1 at `0x5c`, 34 at `0xbe`, 1 at `0xf1`, eight records of 126 lines at `0xf1`, 15 at `0x185`; the program addresses fall on
line-program boundaries. **Unestablished**: the line-count total (1105 for 60 Hz, 1101 for 72 Hz) does not match a conventional
1066 or 1072 line total, so whether the field is a count, a count minus one or a repeat is unknown, and the line-program word
encoding (the images are 237 and 200 half-words) is **unknown**. [vendor-derived] `VC1.h` proposes a word layout (duration, sync bits,
end-of-line flag); no binary evidence confirms it. A QEMU model can skip timing programs: pick width and height from the loaded
file or monitor code and generate frames at the nominal rate (approximation; needs the stated limitation).

## Display IDs

[binary] `_Gr2RegisterInit`, `_Gr2CreateDummyDID` (`gr2.o` `0x2630`):

- DID frame table at SRAM `0xb00`: one half-word per screen line holding the SRAM address of that line's line table. At init every
  line holds `0x1400` except the last, `0x1404`. Registers `0x40 = 0xb00` and `0x42 = 0xb00 + 2 * height` bound the table (`Gr2SetMonitor`, not
  the init, moves the table to start at `0x1300 - 2 * height` when the height is below 1024).
- Default line table at `0x1400`: half-words `1, 0` (count 1, entry display ID 0 from x 0), then at `0x1404` `5, 0, 0, 0, 0, 0` (count 5, four
  of them dummy). Established as the init bytes. The dummy-ID builder reads a line table (count first, then entries), appends four
  zero half-words and adds 4 to the count: the "four dummy IDs" requirement is a hardware quirk worked around in software
  (inferred from the code; the reason is [vendor-derived] only).
- Entry encoding `(x << 5) | id`: [binary] the builder shifts entries right by 5 and compares with the width; so a line table is
  `count`, then `count` half-words, each a start x (11 bits) and a 5-bit display ID, which feeds mode table entry `id` of every XMAP5.
  Established. [public] TR: 32 window styles.
- Register `0x44` (`0xff04` for 1280 wide) splits the 1280 columns into five-pixel groups; NPIX columns 1276 to 1279 reuse the previous
  group's ID ([vendor-derived] reading of the constant; the arithmetic `(w-1)/5, (w-1)%5` is [binary]).

## Cursor

[binary] `Gr2PositionCursor`, `Gr2SetCursorHotspot` and the retrace handler: cursor x and y are written as two back-to-back half-words to
registers `0x22` and `0x24` with the address pair saved and restored. x = (cursor x - hotspot x) + the board's x adjustment, only
when the left edge is under 32 (`CURSOR_X_THRESHOLD`) and register 0 is switched to `0x800`; otherwise register 0 is `0x900` and no x
adjustment is added. y = (cursor y - hotspot y) + y adjustment (plus the screen height beyond 1024 on taller screens). The adjustments come from the
timing file (table above); the 60 Hz file carries 250 and 35. The glyph is 128 half-words (32 rows of two half-words in each of two
planes, inferred from [public] NetBSD's commented glyph table in two "Bit" blocks). The cursor appears when `sysctl` bit 5 is set;
the retrace handler sets or clears it at vertical retrace from pending flags. Cursor colours are three entries in the XMAP5s, where
is **unknown** ([xmap5](../xmap5/README.md)).

## Retrace interrupt

[binary] The retrace handler (`gr2_retr_intr`, `gr2.o` `0xa0`) re-arms the INT2 port register bit 3 by clearing then setting it, then
runs `Gr2RetraceHandler`, which applies the pending cursor, display-mode and buffer-swap changes. The source of the pulse is the VC1;
which `sysctl` bit enables it is unknown (the kernel's final `0x0c` has bit 0 clear). For a QEMU model: raise INT2 local 1 bit 7 once
per frame while video is enabled; the guest only clears via the port register pulse. See questions/vc1-express.md.

## Status

Established: ports and offsets, address-pair behaviour, SRAM map for the loaded images, init and `Gr2SetMonitor` sequences, the
two built-in images, the timing-file layout and contents of the 14 held files, DID table shapes, cursor register sequence.
Inferred: monitor code meaning, sysctl bit roles other than bit 5, glyph plane layout. Unknown: line-program format, line-count
semantics, retrace enable bit, cursor colour location, `xmapmode` port, reset values.
