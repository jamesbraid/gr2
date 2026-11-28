# Open questions: XMAP5

Each entry: the question, the routes tried, the next route. Answered questions move into the owning page and the entry is deleted.

## 1. Mode word: what the alternate-video, popup and overlay bits do

The field boundaries and codes are settled ([README](../devices/xmap5/README.md#mode-word)). Still unknown: what the chip does with the alternate-video
field (no word read sets it), what each of the four overlay-enable bits enables, the popup fields (the header's popup field at bits 8:7 overlaps the
underlay-enable bit), and whether the PROM's console colours at CLUT index 3073 and 3074 (page 12) are used by any mode word. Routes tried: the diagnostic
program's XMAP5 test and header, `expValidateMode` in `gr2.so`, `Gr2SetDisplayMode`, both PROMs. Next: the Elan TR sections on overlay and popup planes
not yet read, `expInstallOverlayMap` and `expInstallPupMap` (which write overlay and popup colours) read in full, and the 4.0.5G PROM's colour code.

## 2. Pointer advance after a misc access, and the cursor colours' role

The mode port advance is only the diagnostic's expectation (+4 after a write); misc auto-increments (five writes to one address). The three cursor colour
entries at CLUT `0x1c01` to `0x1c03` are written by the X server; that the XMAP uses exactly those as its cursor table is inferred. Next: `ide.IP20`'s
XMAP test, and which of `0x1c01` and `0x1c02` is the foreground.

## 3. `crc` port; the sixth `misc` byte

Never touched by the driver or PROMs; the diagnostic header names no sixth `misc` byte. Next: `ide.IP20` (the diagnostic names XMAP tests), PROM 4.0.5G
diagnostics (`0xbfc06e30` region writes the CLUT).

## 4. FIFO depth and write stalls

Whether a CLUT write while `fifostatus` bit 0 is set is lost or stalls the bus. No shipped code does it. The diagnostic's header calls the XMAP FIFO 512
entries deep and names its three status bits empty, half full and overflow; the shipped drivers read bits 0 and 1 only. Next: none from software;
mark unknown, model never sets bit 0.

## 5. Chip count on XS, XS24 and XZ

Five is established only for the Elan (TR). The Indy XZ video board schematic draws five channels (A to E) of a part its sheets label XMAP7, a later part
than the XMAP5 of this board set. Next: board photographs in the Library cache for XMAP markings.
