<!-- keep -->
# Open questions

One file per chip or area. Each entry: the question, the routes tried, the next route. When answered, move the answer into the owning page
and delete the entry.

- [hq2.md](hq2.md): command engine, finish flags, context switch, probe values.
- [ge7.md](ge7.md): engine distribution, header words, slots.
- [microcode.md](microcode.md): GE7 microword data path, RE3 output path, control flow, HQ2 ops.
- [re3.md](re3.md): raster engine registers, plane packing.
- [xmap5.md](xmap5.md): mode word, cursor colours, chip counts.
- [vc1-express.md](vc1-express.md): line programs, retrace enable, monitor codes.
- [dac.md](dac.md): Bt479 and Bt475, reset state, gamma.
- [display.md](display.md): board configuration port byte lane, Z detect, clock chip, genlock, revision 4.

Settled and removed: the layout of the HQ2 status word (see devices/hq2; which register carries the HQ2 revision is hq2.md 7), the GE7 revision register (`+0x683f4`, see devices/ge7),
the XMAP5 window address, and the byte lane question, which is display.md 1.

## Indigo2 Extreme and XZ

Which Express-family boards the Indigo2 carries, and with what chip counts, is unknown: the IP20 driver handles eight geometry engines and
the GL core names `-Extreme`, but the IP22 kernel objects ([ip22-startup.md](../platforms/express/ip22-startup.md)) count engines with the
same probe and name no board. Next: a `gfxinfo` or `hinv` capture from an Indy or Indigo2 with Express graphics, and the Elan TR sections
not yet read.
