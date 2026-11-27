# HQ2: open questions

Each entry: the question, the routes tried, the next route. Answered questions move into [devices/hq2](../devices/hq2/README.md) or
[host-contract](../platforms/express/host-contract.md) and are deleted here. Provenance tags as in [AGENTS.md](../AGENTS.md).

## 1. What do `ge_ctr`, `ge_ptr`, FIFO low water and `intr` do?

The diagnostic program prints status bits 19:16, 22:20 and 13 by name and offers a write to the interrupt bit register; no IRIX or PROM
code reads or writes them. Routes tried: `gr2.a`, both PROMs, `ide.IP20`, the GL core and X driver (all `+0x6a0xx` accesses listed by
pattern search). Next: the HQ2 microcode once its instruction set is decoded (questions/ge7.md 1).

## 2. Why does user space poll `+0x6c040` and store at `+0x6d000`?

The GL core's read-back and origin paths and nothing in the kernel use these; the X driver instead polls HQ2 status bit 0 and stores to
the HQ2 finish-3 port. The user mapping (`Gr2MapGfx`) maps the register page at `+0x6a000` and the VC1 page at `+0x6c040`, so the
offsets may be a different alias. Routes tried: GL core disassembly, kernel `Gr2MapGfx`. Next: decide whether `+0x6c040` reads reflect a
copy of the finish flag (VC1 page) by reading the n32 `__glExpFinish` callers; see also questions/re3.md 2.

## 3. Exact FIFO line condition and the timeouts

Whether the line asserts at count `>=` `fifo_full` or only above it, and whether `fifo_full_timeout`, `fifo_empty_timeout` or the
low-water bit gate a second condition. Routes tried: PROM and kernel flow control, ide field names, the handler's own compare (a
software expectation of `>=`; the threshold it writes, count plus one, suits either rule), and the IRIX source library and diagnostic
program (threshold names and values only). Next: none from software; the model uses `>=`
([host contract section 1](../platforms/express/host-contract.md#what-raises-the-fifo-interrupt-and-how-it-clears)).

## 4. Which microcode routine sets which finish flag, and what 481 to 484, 496 save

Needs the HQ2 instruction set. Next: decode the routines reached from slots 481 to 484 and 496 in `hq2.bin`.

## 5. Per-variant probe register values

No source lists port values per variant; the table in host-contract section 4 is inferred. Next: board photographs and schematics, GR2
variant strings in the 4.0.5G PROM.

## 6. Other microcode releases

Only the IRIX 6.5 base-set `hq2.bin` and `ge7.bin` are held. Next: IRIX 5.x and 6.2 media.

## 7. Which register is the hardware's HQ2 revision?

The kernel's gfxinfo path reads `hq_gepc` bits 23:16 (0 = HQ2, 1 = HQ2.1), the PROMs and the diagnostic program read status bits 31:23, and
both give 0 on every Indigo ([host contract section 1](../platforms/express/host-contract.md#the-hq2-revision-prom-or-kernel)). Nothing
in the Indigo model depends on the answer. Next: a board that reads HQ2.1, which the Indy and Indigo2 boards are.

## 8. What is the HQ2 FIFO drain rate?

Nothing shipped or published states it. Routes tried: the Elan technical report (clock rates only), the shipped `sys/gr2hw.h` (depth and watermark constants), the kernel's and the PROM's timeouts (software budgets), the IRIX diagnostic's delays (`time_delay`, `diag_finish`) and the HQ2 slot code (a few words to a few dozen per command). Next: cycle counts of the GE7 routines behind the common tokens (`tools/ge7-step.py`), which give a floor per command but not the HQ2 front end's own pacing. A model's drain rate is an approximation until then.

## 9. Does a present board bus-error on unmapped offsets inside its 4 MiB window?

No software read for this work touches the padding of the window or anything above `+0x6d000`; the only accesses to unnamed space are the engine probe's, which do not fault. Routes tried: the shipped `sys/gr2hw.h` layout (5.3, 6.2), the kernel archive, the PROM, the GL core, the X driver and the diagnostic's RAM tests (offsets listed), the IRIX source's graphics diagnostics. Next: the schematic's GIO address decode (`GR-4_Schematic.pdf`, HQ2 sheets) for the chip-select terms, and a captured bus error on a probe of such an offset if one is ever published.

## 10. What does the graphics reset keep, and does HQ2 refresh the GE7 microcode DRAM?

[Host contract section 11](../platforms/express/host-contract.md#11-across-a-little-endian-restart): the PROM's byte-order flip and its reset entry assert the MC graphics reset, and no shipped code shows what a reset leaves in the HQ2 and GE7 microstores, the shared RAM or the finish flags. The GR4 board schematic (sheets 7 to 10) shows HQ2 driving a DRAM microstore for the GE7s and a GE7 `REFRESH` pin on the stall net, so the `refresh` register is probably that interval (inferred). Routes tried: PROM 4.0.5D and 4.0.5G flip routines, MC specification sections 2.9 and 5.1, the PROM graphics library, `gr2.a`, GR4 schematic sheets 7 to 10. Next: the schematic of the Indigo's own Express board set (the part list names the same RAMs by count only; the Library's HP-1 schematic is the R3000 CPU base board), the MC's list of what a warm restart resets, a model of HQ2's reset state.

## 11. Does the GR2 board's byte-lane decode follow the CPU's byte order?

[Host contract section 12](../platforms/express/host-contract.md#12-a-little-endian-cpu-on-the-gio32-bus): word accesses carry the same value for both byte orders; byte and half-word ports (board configuration, clock, XMAP5, Bt457, VC1) depend on whether the board decodes the byte address and count or only the word, which no source states. Routes tried: GIO specification chapters 2 and 4, MC specification, shipped `sys/mc.h`, the Express code in the IRIX source (no little-endian variant). Next: the VB-3 and GR-4 schematics' port sheets, the 5.3 and 6.2 `sys/gr2hw.h` for a `_MIPSEL` variant, the MC graphics DMA descriptor's little bit.
