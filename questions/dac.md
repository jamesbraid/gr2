# Open questions: DACs

## 1. Does any Express board carry a Bt479 or Bt475

NetBSD's memory map shows a Bt479 pair at `+0x6c060` and `+0x6c080`; no shipped Indigo code touches those addresses. The Bt475 datasheet is
in the repository with no matching binary use. Routes tried: all driver objects, both PROM images, the Indy XZ schematic (three
BT457). Next: schematics or photographs of the Indigo back end boards.

## 2. Reset state of the palette and registers

The datasheet leaves the command, mask and test registers uninitialised. No evidence on what the board does if the driver's init is
skipped. Unknown; model undefined.

## 3. Does the PROM or any code use the overlay colours

Init writes 0 to 3 into the four overlay entries. Nothing reads them back or changes them. Role of overlay inputs on this board:
unknown (the XMAP5 emits 24 bits and the DAC overlay inputs may be tied low).

## 4. Gamma and the 12-bit colour index

The TR says the RAMDAC gives any 8-bit to 8-bit mapping on both RGB and colour index pixels; the driver's `Gr2SetGammaRamp` is the only
palette writer. Whether a user-space path writes the DAC through a different interface: unknown. Next: `gr2.so`, `libGLcore.so`.
