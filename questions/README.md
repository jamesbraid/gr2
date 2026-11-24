<!-- keep -->
# Open questions

One file per chip or area. Each entry: the question, the routes tried, the next route. When answered, move the answer into the owning page
and delete the entry.

- [hq2.md](hq2.md): command engine, finish flags, context switch, probe values.
- [ge7.md](ge7.md): microword fields, engine distribution, slots.
- [re3.md](re3.md): raster engine registers, plane packing.
- [xmap5.md](xmap5.md): mode word, cursor colours, chip counts.
- [vc1-express.md](vc1-express.md): line programs, retrace enable, monitor codes.
- [dac.md](dac.md): Bt479 and Bt475, reset state, gamma.
- [display.md](display.md): board configuration port byte lane, Z detect, clock chip, genlock, revision 4.

Settled and removed: the HQ2 version field (status bits 31:23, see devices/hq2), the GE7 revision register (`+0x683f4`, see devices/ge7),
the XMAP5 window address, and the byte lane question, which is display.md 1.

## Indigo2 Extreme and XZ

Which Express-family boards the Indigo2 carries, and with what chip counts, is unknown: the IP20 driver handles eight geometry engines and
the GL core names `-Extreme`, but no Indigo2 object has been read. Next: the Indigo2 kernel objects and `IP22GR2NG1` GL library, plus
the Elan TR sections not yet read.
