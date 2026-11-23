# Open questions: XMAP5

Each entry: the question, the routes tried, the next route. Answered questions move into the owning page and the entry is deleted.

## 1. Mode word fields

Only bits 31:27 (CLUT page), bit 24 (buffer), 23:20 (overlay enables), bit 8 and `0x800` (auxiliary page) have support from shipped
code, through an upstream decompilation of the shipped X server (`gr2.so`) that was not re-checked against the object. Pixel format
(bits 26:24), colour index versus RGB (17:16), alternate video, popup fields rest on the upstream `XMAP5.h` only. Routes tried: IP20
`gr2.a`, both PROMs (they only ever write `0x82000000`), upstream `gr2_ddx/decomp`. Next: disassemble `usr/lib/X11/dyDDX/gr2.so`
(`expValidateMode`, `exp_window`) and `libGLcore.so` swap-buffer code for the words they write; `ide.IP20` xmap tests.

## 2. Pointer advance after a mode or misc access

The driver sets the address before every mode write, so auto-increment on `mode` and `misc` is not shown (misc advances: five writes
to one port after one address set; mode unknown). Next: `ide.IP20` xmap diagnostic, X server mode-table loader.

## 3. Cursor colours and the auxiliary colour block

Where the three cursor colours and the 16-entry auxiliary table live. Only the vendor-derived header places them in the CLUT near index
`0x1c00`. Nothing in the IP20 objects or PROM 4.0.5D writes there (greps of every XMAP5 address write). Next: `gr2.so`
(`exp_cmap`, `exp_cursor`), PROM 4.0.5G console code, `ide.IP20`.

## 4. `crc` and `bytecount` ports; misc register meanings

Never touched by the driver or PROMs. Next: `ide.IP20` (the diagnostic names XMAP tests), PROM 4.0.5G diagnostics (`0xbfc06e30` region
writes the CLUT).

## 5. FIFO depth and write stalls

Whether a CLUT write while `fifostatus` bit 0 is set is lost or stalls the bus. No shipped code does it. Next: none from software;
mark unknown, model never sets bit 0.

## 6. Chip count on XS, XS24 and XZ

Five is established only for the Elan (TR). Next: board photographs in the Library cache for XMAP markings.
