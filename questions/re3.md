# RE3: open questions

Each entry: the question, the routes tried, the next route. Answered questions move into [devices/re3](../devices/re3/README.md) and are
deleted here. Grades and provenance tags as in [AGENTS.md](../AGENTS.md).

## 1. What is in the three register banks at `+0x6c200`, `+0x6c280` and `+0x6c600`?

Nothing but a public driver's comment gives their existence, widths and addresses. Routes tried: pattern search of the PROMs (4.0.5D
disassembled in full), the six IP20 kernel driver objects, the n32 and o32 GL cores, the X server driver and the diagnostic program for
any access in `+0x6c200` to `+0x6c7ff`: none found (base-pointer forms excluded from the search). The Elan Technical Report sections 1 to 4
(architecture only). Next, in order: (a) the diagnostic program's raster tests (`gr2_re3dma`, `gr2_shramre3dma`, `gr2_zb`, `gr2_chkpixels`,
`gr2_chkoffset`, `gr2_bitp` and the pixel check routines), which exercise the engine through FIFO tokens and shared RAM and may name
the registers a token loads, read in full; (b) the GR4 and VB3 board schematics in `docs/` (scans of unstated origin, so vendor-derived): the RE3 sheet lists its
host-side address and data pins, which fixes the bank sizes; (c) the GE7 microcode, once its stores to the raster interface can
be told apart (see [ge7.md](ge7.md) question 1); (d) Elan TR sections after 4.3.

## 2. Why does the GL core poll `+0x6c040`?

`ReadColor` and the other read-back paths in the GL core poll bit 0 of the word at `+0x6c040`, then clear `+0x6d000`, after sending
the read tokens, and take the result from shared RAM (`+0x12088`). NetBSD names `+0x6c040` the VC1 command port, where a poll would be
odd. Routes tried: the GL core disassembly (colour-index and RGB read paths), the NetBSD map. Next: the VC1 register list and the
kernel retrace handler, and the diagnostic program's handling of `+0x6c04c`; the read-back handshake (a ready bit set by the
engines) may be a status bit the VC1 window shows.

## 3. How are the 56 planes packed into the five interleaved banks?

The Technical Report gives plane counts and the five-way interleave only. Routes tried: Elan TR 4.3, the GR4 schematic sheet index.
Next: the diagnostic program's pixel and offset checks (`gr2_chkoffset`, `gr2_chkauxoffset`, `gr2_chkzoffset`), which compute where a
pixel's planes live to check them; and the VB3 and GR4 schematics' RAM bank sheets.

## 4. What does bit 5 of the board's first revision byte mean for the RE3 count on older boards?

The diagnostic program sets its RE3 count from that bit for revisions below 4. Routes tried: `gr2_boardvers`. Next: read the code
that prints the count (`print_hinv`) for the string it chooses, and the board revision byte description on the board page.

## 5. Adjacent: the chips at `+0x6c1c0` to `+0x6c1fc`

The diagnostic program writes and reads this range heavily (NetBSD labels two chips "Kaleidoscope" there); no other shipped program touches
it. Recorded for the XMAP5 and board pages; not an RE3 register.
