# Open questions: display back end

## 3. Pixel clock chip and protocol

Below revision 4 the part and the meaning of the 17 bytes and the `port0` selector (1, 2, 4) are unknown. At revision 4 and up the 56-bit word is only
inferred to be the ICS1562 of the Indy XZ video board. Routes tried: Library searches for ICS1562 (no hits), the VB3 schematic (names the part),
all `StartClock` and `SetMonitor` code. Next: the ICS1562 data sheet, schematic of the Indigo GR2 back end, board photographs.

## 4. Genlock

`Gr2AdjGenlock` and the `adjntsc.bin` and `adjpal.bin` files are not decoded: it reprograms the clock, loads SRAM and sets `sysctl` bit 6.
Next: read the function in full with the files.

## 5. What revision 4 and up means

The driver treats board revisions 4 and above with a different probe and a serial clock. Whether that is the later Express back end
that the Indy XZ and Indigo2 boards share is unknown (topology is not transferable). The IP22 kernel objects use the same clock
code and add two flat-panel byte sets ([ip22-startup.md](../platforms/express/ip22-startup.md#clock-and-timing-tables-per-monitor-code)).
Next: PROM 4.0.5G display path (the 4.0.5D PROM has no revision 4 clock table), the IP22 and IP24 PROMs' own start-up, a capture
that shows which board revision an Indy or Indigo2 reads.
