# Bt457: the three colour DACs on the Express board

Three Brooktree Bt457 RAMDACs, one per colour, take the five XMAP5 pixel streams multiplexed 5:1 and produce the analogue video.
Registers: [registers.toml](registers.toml). Labels: **established**, **inferred**, **unknown**. Source classes: **[public]**
(the Brooktree Bt457/Bt458 datasheet, `docs/Bt457.pdf`; NetBSD `grtworeg.h`), **[binary]** (shipped IRIX 6.5 `gr2.a` and the PROMs),
**[vendor-derived]** (upstream headers, not used here). Nothing was read on a board.

## Identity and count

[public] NetBSD's memory map comment lists "BT457 DAC (red) 0x1f06c0a0, (green) 0x1f06c0c0, (blue) 0x1f06c0e0" and a "BT479 triple
DAC" read and write pair at `+0x6c060` and `+0x6c080`. [binary] The IP20 driver and both PROMs write exactly the three Bt457
windows (`_Gr2DacInit`, `gr2_init.o` `0x5a0`; `Gr2BlankScreen` `0xfe8`; `Gr2SetGammaRamp`, `gr2_retrace.o` `0xfe8`; PROM `0xbfc0e9d4`,
`0xbfc2cc00`) and never the `+0x6c060` and `+0x6c080` addresses (greps of all five driver objects and both PROM images: the only hit is
data). So the Indigo Express boards carry **three Bt457**, one per channel; a Bt479 on any Express board is unknown and not
modelled. The Bt475/Bt477 datasheet in `docs/` has no match in any shipped Express binary or in the Indy XZ schematic
(`VB-3_Schematic.pdf` names three BT457 on sheets 14 to 16, red, green and blue): see [bt475](../bt475/README.md).

Board facts, [public]: the Elan TR (4.4.3) describes DACs fed with up to 24 bits per pixel, eight per colour, multiplexed to handle
the five parallel pixel pipes, with RAMDAC gamma correction under application control (any 8-bit to 8-bit mapping, applied to both
RGB and colour index pixels).

## Windows and ports

| Chip | Window (graphics base `+`) |
|---|---|
| red | `0x6c0a0` |
| green | `0x6c0c0` |
| blue | `0x6c0e0` |

Each chip has four byte ports on a 4-byte stride, which are the datasheet's C1 and C0 input values (offset bit 2 is C0, bit 3 is
C1): `+0` address register, `+4` colour palette RAM, `+8` control registers, `+0xc` overlay colours. [public] datasheet Table 3. The
driver accesses are all byte stores at stride offset 0, so the data is in the most significant byte lane of the word on a
big-endian CPU (established, every shipped DAC access is `sb`).

Because the three chips have their own windows, the board works in the datasheet's *normal mode* (one byte per colour per chip)
not RGB mode (three consecutive bytes to a shared chip): [binary] each palette store is one `sb` to one chip, and the three chips
are written alternately in `Gr2SetGammaRamp`. The CE inputs are wired per chip. Established.

## Initialisation (`_Gr2DacInit`, established)

Per chip, byte stores, in order:

1. `addr = 4`, `ctrl = 0` (read mask 0: no plane addresses the palette; every pixel reads entry 0, which is black).
2. `addr = 5`, `ctrl = 0` (blink mask 0).
3. `addr = 6`, `ctrl = 0xc1` (command register: 5:1 multiplexing, palette RAM enabled, blink off, overlay 0 enabled, overlay 1 disabled).
4. `addr = 7`, `ctrl = 0` (test register).
5. `addr = 0`, then 256 byte writes of 0 to 255 to `palette`: an identity ramp for each colour. The address wraps to 0 after 255.
6. `addr = 0`, then four byte writes 0, 1, 2, 3 to `overlay`.

The screen therefore stays black after init because the read mask is 0. The driver (and PROM) unblank later with
`Gr2BlankScreen(board, 0)`: poll XMAP5 chip 0 `fifostatus` bit 0 clear (up to 10 ms), then on all three chips `addr = 4` and
`ctrl = 0xff`. Blank (`Gr2BlankScreen(board, 1)`) writes `ctrl = 0` the same way. Established as stores. The sequence is the same in PROM
4.0.5D at `0xbfc0e9d4` and `0xbfc2cc00`.

## Colour map path

Colour index and RGB pixels do not go through the Bt457 palette in the default state: the XMAP5 chips already produce 24 bits per
pixel (the XMAP5's own 8192-entry colour table does the indexing, see [xmap5](../xmap5/README.md)), and the DAC's palette holds the
identity ramp, so it is transparent. The driver changes the ramp only in `Gr2SetGammaRamp` (`gr2_retrace.o` `0xfe8`): `addr = 0` on
each chip, then for i in 0 to 255 one byte to each chip's `palette` from three 256-byte arrays (red, green, blue), checking
`fifostatus` bit 0 and re-raising the interrupt level every 100 entries. Established. That is the TR's "RAMDAC gamma correction under
application control" ([public]).

## Reset state

The datasheet states the command, read mask, blink mask and test registers are not initialised at power-up and the palette
contents are not specified: a model should not give them reset values. A guest that does not run the driver init sees undefined
colours (inferred: nothing shipped depends on them).

## Qtests

Discriminators: (a) write `addr = 255`, two bytes to `palette`, read `addr`: wraps to 0 then 1 (datasheet); (b) `ctrl` access does not
advance `addr`; (c) a `ctrl` write with `addr = 4` of 0 then 0xff changes scan-out from black to the framebuffer; (d) the identity
ramp loaded by init leaves colours unchanged.

Open items: [questions/dac.md](../../questions/dac.md).
