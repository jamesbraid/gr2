# Express (GR2) host contract on the Indigo

What a host program can observe and must provide at the graphics slot of an Indigo (IP20, with IP12 noted) so that the shipped PROMs, the IRIX kernel driver, the X server and the GL core run on a model of the board: status bits, flow control, completion flags, context switching, pixel DMA, probe answers per board variant, interrupts and reset. Written for the Indigo QEMU model and for the planned iris GR2 crate. The chip pages are [devices/hq2](../../devices/hq2/README.md) (command engine, register map in `registers.toml`), [devices/ge7](../../devices/ge7/README.md), [devices/re3](../../devices/re3/README.md), [devices/clock](../../devices/clock/README.md) (board configuration ports), [devices/vc1-express](../../devices/vc1-express/README.md), [devices/xmap5](../../devices/xmap5/README.md) and the DACs; the board survey is [README.md](README.md), the token catalogue [pipeline.md](pipeline.md) and the display back end [display.md](display.md). The host side of the buses is in the chips repository: `devices/mc` (graphics DMA engine, reset bit), `devices/int2` and `platforms/ip20/interrupts.md`, `platforms/ip20/gio.md` (slot window, probe).

Provenance tags on every fact: `[public]` published document or public driver (the Elan Graphics Technical Report, NetBSD `grtwo.c`, Usenet postings in the Library), `[binary]` a shipped binary (a software expectation; the routine or message is named), `[vendor-derived]` upstream headers (not used on this page). Grades as in [AGENTS.md](../../AGENTS.md): established (read in full), inferred (reasoned), unknown. Binaries read: the 5.3 `IP20boot/gr2.a` members for section 10 ([binaries.md](../../references/binaries.md#irix-53-install-disc-round-9)), `gr2.a` members (`gr2.o`, `gr2_dma.o`, `gr2_init.o`, `gr2_tpucode.o`), the IRIX kernel's graphics-DMA module (`vdma.o`, for the MC calls), PROMs 4.0.5D and 4.0.5G, the diagnostic program `ide.IP20`, the X server driver `gr2.so`, `libGLcore.so` (n32 and o32). Nothing was read on a board.

## 1. HQ2 status word, flow control and finish flags

### The status word (`status` at +0x6a040)

The diagnostic program prints this register, calls it the HQ2 version register, and decodes every field with a name (`gr2_rdHQ2reg`). Established [binary] for the field boundaries and names, which are the ones in `registers.toml`:

| Bits | Name (as printed) | Meaning and who uses it |
|---|---|---|
| 0 | finflag3 | Finish flag 3. Set by microcode, cleared by a store to `finish3`. Used by the kernel (`Gr2SetMonitor`, `Gr2PcxSwap`, `Gr2DestroyDDRN`) and the X server image paths. |
| 1 | finflag2 | Finish flag 2. Cleared by a store of 0 to `fin2`. The kernel's microcode-ready and DMA-done flag (`_Gr2UcodeReady`, both DMA triggers). |
| 2 | finflag1 | Finish flag 1. Cleared by a store of 0 to `fin1`. The diagnostic program's DMA-done flag and the 4.0.5G PROM's pixel-DMA completion flag. |
| 4:3 | dma_sync source | Read-back of `dmasync`: 0 vertical interrupt, 1 video sync, 2 clear, 3 set. |
| 5 | FIFO overflow | The kernel handler prints "FIFO overflowed, data is destroyed - Reset graphics" when set and then calls `gr2_error` (logs the GE PC from `hq_gepc`, flags the board, kills the graphics clients, resets the board). Nothing clears it in shipped software; inferred cleared by the graphics reset. |
| 12:6 | FIFO count | Words in the FIFO. The kernel compares it with 35 (room), 36, 40, 41 and 63. |
| 13 | FIFO low water | Never read by IRIX. Condition unknown. |
| 15:14 | zero | Printed as zero. |
| 19:16 | ge_ctr | Role unknown. |
| 22:20 | ge_ptr | Role unknown. |
| 31:23 | HQ2 version | Both PROMs store `word >> 23` through a byte store (bits 30:23). NetBSD masks `0xff000000` and shifts 23, a different field; they agree only at 0. |

The status bits 1 and 0 decoded: bit 1 is finish flag 2, bit 0 is finish flag 3. The kernel review note "bits 1 and 0 also tested" refers to these. Established [binary] (messages "finish flag not clear" in `Gr2SetMonitor`, the ide field names, and the three clear registers).

### What raises the FIFO interrupt and how it clears

- The interrupt is GIO line 0 (INT2 local interrupt 0, bit 0, `LIO_FIFO`). The kernel registers `Gr2FIFOInterrupt` on it for the graphics slot (`gr2_init`). Established [binary]; line routing in the chips interrupts page.
- The line is a level that follows the FIFO fill count against `fifo_full`. Every PROM drawing routine waits until bit 0 of the INT2 local-0 status byte is clear before each token, then sends a bounded run of operands (at most 25 words for a character strip) without checking again; `fifo_full` is 40. Established [binary] for the polling; **inferred** for the rule "asserted while count >= `fifo_full`", from the PROM budget (40 + 25 fits a 64-word FIFO) and from the kernel handler, which after an interrupt raises `fifo_full` to `min(count + 1, 63)` but not below 40 and masks the INT2 bit, the way one silences a level interrupt. The handler's own test (`sltu count, saved_threshold`, IRIX 5.3 `gr2.o` `0x1000035c`) treats count below the threshold as drained, a software expectation of `>=`; the hardware compare is **unknown** (`>` or `>=`), and no shipped read settles it: the kernel writes `fifo_full` 40 and, after an interrupt, `count + 1`, which is correct under either rule, and the IRIX source tree states only the threshold's name and the values 40 (kernel and PROM library) and 48 (the diagnostic program's `inithq`), never the compare. The Everest graphics path in the same tree tests a different board's word count against 50, which is not evidence for this one. Model: `>=`, inferred; a qtest can write `fifo_full = N`, push words with nothing consuming them, and check whether the line asserts at count N or N + 1.

Does anything else raise the line? Nothing shipped depends on it. The handler reads the overflow bit (status bit 5) on every entry, so overflow reaches the same handler, but overflow means a count past the threshold anyway, so no second source is needed to explain it. `fifo_empty` (written 1 by the kernel, 16 by the diagnostic) is called unused in a comment in the IRIX source library, and status bit 13 (low water) is never read, so no low-water condition drives a line that software relies on. The two timeouts (`fifo_full_timeout` 100, `fifo_empty_timeout` 255 in the kernel, 10 in the PROM library) are written and never read back; whether the hardware raises the line on a timeout is **unknown**, and the kernel's own "FIFO TIMEOUT" messages come from a software timer (`Gr2FIFOTimeoutCallback`), not from a status bit. Established [binary][source] for each of these absences of use.
- Kernel use: `Gr2FIFOPollLowater` returns 1 (room) and writes 40 to `fifo_full` when the count is below 35, and returns 0 without a write otherwise; a caller (not read) sleeps until it says yes, or a timeout callback fires. The handler masks INT2 local-0 bit 0 on entry (byte at `0xbfb801c7`), checks `fifo_overflow`, then compares count with the saved threshold. At or above it, it spins up to a software limit while count >= 36; below it, it either returns or, when that software limit is zero, spins while count >= 41 (limit 300000 us). When a context flag allows, it raises the threshold to `max(40, min(count + 1, 63))`, sets a "FIFO full seen" flag and forces a reschedule so the producer yields. It sets the mask bit again on exit. Established [binary] for the individual compares and stores; the branch conditions that select each path were read only in outline.
- The handler never writes a clear register: the line drops when the count falls below the threshold or the threshold is raised. Inferred.
- `intr` (+0x6a074, "Intr bit (cleared by host)" in ide) is a separate host-cleared bit; no driver touches it. Which line it drives is unknown.
- The fill count is in words: every store to the FIFO window adds one, and the microcode consumes them. A model that executes no microcode must drain the count itself (consume tokens as it interprets them) or the line would stay asserted.

### FIFO depth, thresholds and low water

- **Depth: 64 words. Inferred.** No shipped program or published document states it. The pieces that agree: the count field (status bits 12:6) is seven bits wide and no IRIX test compares it with more than 63 (the kernel clamps its raised threshold to 63, `Gr2FIFOHandler`); the PROM sends at most 25 words after the INT2 FIFO bit reads clear, and with a threshold of 40 that is exactly 64 if clear means a count of 39 or less (a clear at 40 would overflow, see the next point); and the diagnostic program's FIFO RAM test after a graphics reset (microcode stalled, four dummy words queued) walks the window in blocks of 64 words, writing a block and reading it back ([source]: `stand/arcs/ide/fforward/graphics/EXPRESS/RAMtools.c`, `FIFO_LIMIT`; the shipped `ide.IP20` was not rechecked for it). The 32768 in the same table is the size of the window in words, not the depth. The upstream header's "512-word FIFO" [vendor-derived] contradicts its own note that the field holds 0 to 127; it is not used here.
- **Full: the interrupt line asserts at a count of `fifo_full` or more. Inferred.** The threshold is 40 in the kernel and the IRIX PROM library, 48 in the diagnostic program, and the kernel raises it to `min(count + 1, 63)` (never below 40) after an interrupt and writes 40 back when it finds the count below 35. The PROM budget above is the one discriminator that is independent of the handler's own compare: with a 64-word FIFO, "line clear" must mean at most 39 words queued, or 25 more words would overflow. A model should assert at `count >= fifo_full`; a qtest that sets `fifo_full` to 40, pushes 39 words with nothing consuming them and then one more, checks that the line rises on the fortieth.
- **Overflow (status bit 5): a word arrives with 64 queued. Inferred.** The kernel treats it as fatal ("FIFO overflowed", `gr2_error`) and nothing clears it but a graphics reset.
- **Low water (status bit 13) and `fifo_empty`: unknown.** Bit 13 is never read by IRIX. The register is written 1 by the kernel and the IRIX PROM library (a comment there says it is not used), and 16 by the diagnostic program. The upstream header reads bit 13 as "count at or below `fifo_empty`" [vendor-derived, inferred at best]; with the kernel's value of 1 that would mean "at most one word queued", which no software checks. A model may drive the bit that way; nothing depends on it. The two timeouts are in [the interrupt section above](#what-raises-the-fifo-interrupt-and-how-it-clears).

### Finish flag 2 (status bit 1): when it rises, and what clears it

- **A store to `fin2` of 0 drops it. Established [binary] as software expectation.** Every user clears the flag first and then queues a command that must raise it: `Gr2Start` (the class word, below), the context save and restore (`_Gr2CXSaveRestore`, `Gr2PcxSwap`), both DMA triggers, and the diagnostic program's `diag_finish`, which then writes slot 1 and tests bit 1. A flag that survived the store would let each wait pass at once. The write port sets the flag to the stored bit 0, so a store of 1 would raise it (the diagnostic's menu offers it; no driver does it).
- **Raised only once the full image runs? Not decided by any shipped code.** The kernel waits on bit 1 only after the full HQ2 and GE7 images are loaded and started: its start-up wait is `Gr2Start`'s, after it has cleared `fin2` and sent the board class word. The console images (the PROM's and the kernel's built-in pair) are driven without any bit 1 wait, and the HQ2 instruction that sets a finish flag is not decoded, so whether a console routine can set one is not known. The model that fits all shipped waits: raise bit 1 when the microcode has retired the command that was queued after the last store to `fin2`, and for the start-up wait when the class word has been consumed with the full image loaded. Raising it earlier (for instance at download time) cannot be seen, because `Gr2Start` clears the flag immediately before the class word; whether the hardware can raise it with the console images is unknown.

### Finish flags and the FINISH / sync mechanism

Three flags, each set by microcode when it runs a finish-type command, each with a host store port that sets the flag to the stored bit 0 [binary]:

| Flag | Status bit | Host store | Users |
|---|---|---|---|
| 1 | 2 | `fin1` (+0x6a048) | `ide` DMA tests; 4.0.5G PROM pixel DMA |
| 2 | 1 | `fin2` (+0x6a04c) | kernel context swap, microcode start, DMA |
| 3 | 0 | `finish3` (+0x6b000) | kernel monitor change, context swap restore, X server image read and write, GL finish and read-back sequences (through the user mapping, see question 2 of [questions/hq2.md](../../questions/hq2.md)) |

The host sequence is the same for each: store 0 to the flag port, queue the command, poll the status bit. Examples, established [binary]: the X server `expReadImage` stores 0 to `finish3`, queues token slot 344 and its four operands, then polls status bit 0 and reads pixels from shared RAM at `+0x1b000`; `Gr2SetMonitor` queues slot 2 with operands 0x6c and (screen height - 1), polls bit 0 with 10 us sleeps (limit 300000), then stores 0 to `finish3`. The GL origin query (`__glExpGetOrigin`; slot 163 is shared with Finish and SwapBuffers) stores operand 0 to slot 205 (`+0x42334`) and slot 163 (`+0x4228c`), then polls bit 0 at `+0x6c040`, reads two results from shared RAM and stores 0 at `+0x6d000` in the user mapping; those two offsets are not the kernel's (see the question).

The FINISH token NetBSD names (`+0x4064c`, slot 403) is not used by any shipped program and has no word in `hq2.bin`. Which microcode routine sets which flag is not decoded (HQ2 instruction set unknown), so a model must set a flag when it has retired every earlier command (inferred: that is what the shipped callers wait for).

Reset values software relies on: none. Software stores 0 before every use; `probe_word` reads 0xdeadbeef before any initialisation.

### The HQ2 revision: PROM or kernel?

Answer: both read a register, they read different ones, and a model that returns 0 from both is right for every Indigo board on record.

- **What gfxinfo prints.** `gfxinfo` is `usr/gfx/gfxinit` (5.3 disc; the name is a symlink to it). Its GR2 report formats the 60-byte probe record the kernel copies out through `Gr2Info`. Record byte `0x30` selects the HQ2 text: 0 prints "HQ2 rev A", 1 prints "HQ2.1 rev A", anything else "HQ2 rev unknown" (`gfxinit` `0x40aa04` to `0x40aa60`, strings at offsets `0x2844` to `0x2860` of the data segment, file offsets `0x24844` to `0x24860`). Established [binary]. Public captures agree: every Indigo board (GR2 revision 2) prints "HQ2 rev A", and the later GR2 revision 4 and 6 boards (Indy and Indigo2) print "HQ2.1 rev A" (Library mail archive, `3EBA4AA5.8080302@sgi.com`, `20071209164502.GA13877@deprecation.cyrius.com`).
- **Where the kernel gets byte `0x30`.** From bits 23:16 of the word at `+0x6a06c` (`hq_gepc`): `_Gr2ProbeChipRev`, IRIX 5.3 `gr2_init.o` `0x100001dc` to `0x100001e4` (a word load, a shift right by 16, a byte store), the same in 6.5. Established [binary]. The same register's low 16 bits are the GE program counter that `gr2_error` logs.
- **Where the PROMs get theirs.** From bits 31:23 of the status word at `+0x6a040` (`word >> 23` through a byte store; 4.0.5D `0xbfc0ecec`, 4.0.5G `0xbfc11a98`). The IRIX source's PROM library does the same (`info->HQ2Rev = base->hq.version >> 23`, `stand/arcs/lib/libsk/graphics/EXPRESS/gr2_init.c`) and the diagnostic program prints the same field as "HQ2 version". Established [binary][source]. Nothing in the PROM path reaches gfxinfo; the kernel reprobes.
- **Which one is "the revision".** Not settled by software: the two fields would agree only at 0, and 0 is the value for every captured Indigo. The kernel's field is the one users see (value 1 = HQ2.1). For a board that reads 0 in both, the Indigo, nothing depends on it. Model: `status` bits 31:23 = 0 and `hq_gepc` bits 23:16 = 0 for HQ2 rev A, which is every Indigo configuration. If an HQ2.1 board were ever modelled, put 1 in `hq_gepc` bits 23:16 (what gfxinfo needs) and 1 in status bit 23, the PROM-side placement being a guess. NetBSD masks `0xff000000` and shifts 23, a different field again [public]. Grade: the decode and the captures established; "register A is the revision and register B is not" unknown.

### The other revision read-backs gfxinfo prints

The same record carries three more chip revisions. The decode tables are in `gfxinit` (the three letter tables at data-segment offsets `0x2870` to `0x28dc`, file offsets `0x24870` to `0x248dc`), established [binary]; the values the captures need are inferred from them.

| Record byte | Source in the kernel | gfxinfo decode | Capture (XS24, XZ, Elan) | Value to read |
|---|---|---|---|---|
| `0x31` GE7 | word at `+0x683f4` after a store of 0, byte bits 7:5 (`gr2_init.o` `0x100001e8` to `0x100001f8`) | 1 = A, 2 = B, else unknown | "GE7 rev B" on all | `0x40` in the low byte (field value 2) |
| `0x32` RE3 | low byte of shared-RAM word `+0x1ffe0`, copied in `Gr2Start` and on the reuse path; the microcode writes it (`Gr2Start`'s failure message is "RE version read back failed") | low nibble 1 to 4 = A to D (RE3), 5 = A (RE3.1), else unknown | XS24 and the IP12 Elan 4D/30 posting: D and C; XZ postings: "unknown" | 4 for rev D; the INIT routine must leave it |
| `0x33` VC1 | `testreg` low three bits after `addr = 5` (`Gr2ProbeVC1`) | 1 = A, 2 = B, else unknown | "VC1 rev B" on all | 2 |

An earlier version of this page and of the GE7 and VC1 register maps said the value for rev B was 1; the decode above shows A is 1 and B is 2.

## 2. Context save and swap (`_Gr2CXSaveRestore`, `Gr2PcxSwap`)

The kernel never copies board state itself. It asks the microcode to dump or load it, and moves the data with the MC graphics DMA engine (section 3). Established [binary] for the calls below (`gr2.o` `0xbe0`, `0xe00`); the structure of the per-context records is inferred where noted.

`_Gr2CXSaveRestore(board, buffer, bytes, token_slot, token_operand, direction)`:

1. Store 2 to `dmasync` and 0 to `fin2`.
2. Queue a token at slot `token_slot` (481, 482, 483 or 484, i.e. `+0x40784`, `+0x40788`, `+0x4078c`, `+0x40790`): 481 stores 0 (the caller's operand is ignored), 482 stores the word count (`bytes / 4`) as its first operand, 483 stores `token_operand`, and 484 stores `token_operand` and then sends the word count to the data port (`+0x4077c`). Established [binary] (`gr2.o 0xc3c` to `0xdbc`).
3. Run a DMA of `bytes` between the buffer and the DMA port `gedma` (section 3), direction 2 = board to memory (the save path passes 2), 0 = memory to board (zero means write back, nonzero means invalidate); cache write-back before a load, invalidate before a save.
4. Poll status bit 1 (`_Gr2UcodeReady`, up to 1,000,000 us). On failure print "_Gr2CXSaveRestore: TIMEOUT gfx data could not be saved/restored".

Token meaning (inferred from the callers): 481 and 482 move the context's whole shared-RAM image ("get initial state" and "load state"; the kernel allocates the buffer from a word the microcode leaves in shared RAM, word index 770 at byte offset `+0xc08`, size in words); 483 saves and 484 restores one of four state buffers selected by the operand 0 to 3, whose sizes come from words at `+0xc0c` and `+0xc10` of shared RAM (the microcode publishes them, so the sizes depend on the shipped `hq2.bin`/`ge7.bin`).

`Gr2PcxSwap(board, old, new)` sequence (inferred as a whole; the individual stores are established):

1. Take the graphics context lock (`gfx_waitc_on`). Reject a context whose type is not below 4 or size class not below 3 ("Invalid gfx context type/size").
2. Save the outgoing context's finish flag: read status bit 0 into its record.
3. Save each of the outgoing context's valid state buffers (flags in the record word at +0x48, bits 0 to 3) with token 483 and operands 0 to 3; allocate buffers on first use.
4. Restore the incoming context: store 0 to `fin2`; queue slot 496 (`+0x407c0`) with the render-node index (record address minus the node array base) and send the context type and size to the data port; wait for status bit 1; then for each valid buffer token 484 with its operand; send per-window setup (slot 485 `+0x40794` window box, slot 486 `+0x40798` flag, slot 480 `+0x40780` flag, and clip rectangles as packed 11-bit pairs through the data port) when the window changes.
5. Store the incoming context's saved finish flag bit to `finish3`.
6. Errors: "Gr2PcxSwap: TIMEOUT gfx" with a reason ("context switch did not complete (Start)", "(Restore)", "(Kill)", "(CX current RN)", "Context Size change did not complete").

What the hardware must preserve: the diagnostic program's context-switch test (`gr2_ctxsw`, message "CTX_SWITCH DMA test") shows the state that a save and restore must round-trip, by printing each field of context 0 before and after: `Attr_store[n]`, `Cmds_store[n]`, `Cmdreg`, `Vecreg`, `Datareg`, `Act_attr`, `Cur_attr`, `flag_reg`, `hq2pc_reg`, `cmdptr`, `vtxctr`, `fifostate`, `ucode_reg`, `finishflg`, and the first and second vertex coordinates `X_VTX`, `Y_VTX`, `Z_VTX`, `W_VTX`. Established [binary] that these are the compared fields; the register file they come from is inside the HQ2 microcode and sequencer, not host visible. The host-visible part is the finish flag (status bit 0, carried in the record) and the FIFO state (an incoming context starts with an empty FIFO count of its own, `fifostate`).

For a model that interprets tokens directly (no microcode): implement 481 to 484 and 496 as "DMA the model's per-context state to or from the host buffer"; the buffer contents are opaque to every shipped program, so any self-consistent format round-trips. Raise finish flag 2 after each. The shared-RAM words that give buffer sizes must be written by the model at start-up (otherwise the kernel allocates zero bytes). Inferred.

## 3. Pixel DMA (`gr2_dma.o`)

Answer: the MC runs the transfers; the HQ2 is a bus slave; the HQ2 does not start transfers itself.

- Engine and address. The kernel programs the MC graphics DMA engine (`MCdma`: memory address, mode, size, stride, then the GIO address, which starts it) with the GIO address equal to the physical address of the HQ2 `gedma` register (`+0x6a068` in the graphics window, `0x1f06a068` on the Indigo). Every transfer, pixel or context, uses that single address as the board port. Established [binary] (`Gr2MCPixDma` and `_Gr2CXSaveRestore` call `kvtophys(base + 0x6a068)`; `MCdma` stores the fields in the order in the MC page). Register and field meanings are in the chips repository's `devices/mc`.
- Mode. 0x54 for host to board (long burst, incrementing memory address, wait for the graphics sync) and 0x56 for board to host (the same plus the graphics-to-host bit). Established [binary] (`Gr2MCPixDma` stores 84 or 86). The sync bit ties the transfer to `dmasync`; the kernel stores 2 ("clear") before each transfer.
- Parameters. Line width in bytes is the word count per line times 4 (user argument at +0x24); the MC line count is the number of lines (in 16-bit halves); stride is the signed byte distance (the kernel negates for bottom-up and right-to-left reads, flags bits 2 and 3 of the argument half-word at +0x14); zoom 1. Transfers are limited to 8192 bytes per chunk when the MC has no virtual-address translation (MC revision 0, `vdma_rev` 0): the kernel then builds physical page descriptors (`_Gr2mkkdmada`) and walks them with a software DMA routine in 4096-byte pieces (`fakePICdma`). Established that both paths exist; the MC revision split is the MC page's.
- Formats. Argument flag bit 0 selects 84 or 86 (direction), bit 1 a strided/rectangle transfer, bit 2 and bit 3 the two reversal directions, bit 4 an extra mode used by the 32-bit packed read; the pixel formats (32-bit words, packed 16, 8 and 1-bit with colour expansion in the board) come from the GL tokens before the ioctl: `__glExpDrawPixelsKDMA` stores 1 to `+0x422f0` (slot 188), then `0` and two floats (x and y zoom) to `+0x422ec` (slot 187), then calls the kernel with slot number 184 or 181 and its operands. Established [binary] for the sequence. The Elan TR says the DMA channel is 32 bits wide and carries 32-bit pixels and packed 16, 8 and 1-bit pixels, the latter expanded into one of two user-defined RGBA values [public] (section 5.11). Operand layouts of the board commands are the kernel arguments `[slot, first operand, ...]`: `_Gr2MCDMAtrigger` queues slot = argument 0, operand = argument 1, then data words from arguments 3, 2, a half-word of the MC argument block and argument 9, then a 1 or 0 for the direction flag. Argument semantics (origin, size) are not decoded: unknown.
- Handshake. Before: store 2 to `dmasync`, store 0 to `fin2`, queue the board command, then start the MC transfer. After: poll status bit 1 (`fin2`) at 1 us steps, up to 100,000 in `_Gr2DMAtrigger` and in one branch of `_Gr2MCDMAtrigger`; the other branch counts a software limit and, on each expiry, writes 0 to `gedma` twice and logs, up to ten times, then fails (the abort meaning is inferred). `_Gr2MCDMAtrigger` clears the MC done interrupt (`MCIntClr`) before it starts the transfer, but nothing in `gr2.a` waits on INT2 local 0 bit 4; that wait, if any, is inside the MC DMA routines (`vdma.o`, not read here). Established [binary] (`_Gr2MCDMAtrigger`, `_Gr2DMAtrigger`). The 4.0.5G PROM runs a pixel DMA the same way using `fin1` and status bit 2 with a 1000 us x 20 wait. The diagnostic program does the same with `fin1`.
- Can the HQ2 start transfers itself? **No: the host does, through the MC, and the HQ2 only answers as a GIO slave.** Established for all shipped software [binary][source]. The IRIX source's diagnostic DMA code (`stand/arcs/ide/fforward/graphics/EXPRESS/dmasetup.c`) is the clearest statement: `mk_dmada` writes the MC's memory address, mode (incrementing address, long burst, and a "sync" bit that the source says is always set for this board), size, stride and finally the GIO address (the HQ2's `gedma`), and `do_dma` then writes the MC's start-DMA register and waits for the MC to finish. For a board-to-host or host-to-board pixel transfer the host queues the board command first (token words to the FIFO, with `fin1` zeroed) and starts the MC afterwards, then polls `fin1` for up to 20 x 1 ms; the 4.0.5G PROM and the IRIX 5.3 kernel (`_Gr2MCDMAtrigger`, `_Gr2DMAtrigger`) do the same with `fin1` or `fin2`. No host-visible HQ2 register holds a memory address or length, and nothing in `gr2.a`, either PROM, `ide` or the GL core sets one. The diagnostic's comment "this sets up HQ2 with DMA" refers to the board command that arms the board side, not to bus mastering. What stays **unknown** is whether the silicon could master the bus: the HQ2's internal registers and microcode are unread, and no shipped program asks. The model should never initiate a GIO cycle from the board.
- The sync bit. The MC's graphics-DMA mode carries a "graphics sync" bit that the kernel and the diagnostic always set (mode `0x54` and `0x56` above). It pairs with `dmasync` (+0x6a050): the kernel stores 2 ("clear") before each transfer and the diagnostic menu names 0 vertical interrupt, 1 video sync, 2 clear and 3 set. How the MC gates its cycles on the board's sync is the MC page's; what software relies on is only that, after it stores 2 and queues the board command, the transfer runs to completion and the finish flag rises. A model should not stall the MC on the sync; whether "clear" means gated off or released is **unknown**.
- What a model must do. Treat the MC DMA engine as already implemented in the MC model; give it a GIO slave at the `gedma` address that accepts and returns words for the length, and set finish flag 2 (or 1) once the board command has consumed the last word. The words are the board's pixel stream: framebuffer or Z, 32 bits each, in the order the board command selects.

## 4. Probe answers per Indigo variant

All Indigo boards in public hardware listings report board revision 2, so the kernel's "below revision 4" branches are the Indigo's [public] (gfxinfo output in Usenet sale postings, Library mail archive). Revision 4 and up is a later back end whose topology is not the Indigo's (see [questions/display.md](../../questions/display.md) 5).

Public per-variant facts (gfxinfo and hinv, IRIX 5.2 to 6.5.10 on IP12 and IP20), [public], established as reports. Message-ids in the Library mail archive: XS24 `qHFA7.133$Ju5.108226@news.uswest.net` and `tbFy4.1859$34.28937@news.swbell.net`; XZ `n4ra5tkhvpe77pepdipq78m60hj5mo7d10@4ax.com` and `alnr2m$ta$1@netlx020.civ.utwente.nl`; Elan `516a5aae.0110232317.5caacdcd@posting.google.com`, `user-386EA9.23243014062002@news.east.cox.net` and (IP12, IRIX 5.2) `6rt5uk$eva$1@nnrp1.dejanews.com`; RE3 rev C `900704686.602388@globe.uwaterloo.ca`:

| hinv name | Geometry engines | Render engines | Planes | Other fields (all variants seen) |
|---|---|---|---|---|
| GR2-XS24 | 1 | 1 | 24 colour, 4 aux, 4 cid, Z buffer | GR2 revision 2, VB1.1, HQ2 rev A, GE7 rev B, RE3 rev D, VC1 rev B |
| GR2-XZ | 2 | 1 | 24, 4, 4, Z buffer | same |
| GR2-Elan | 4 | 1 | 24, 4, 4, Z buffer | same (an IP12 4D/30 Elan posting prints RE3 rev C; some XZ postings print RE3 rev unknown) |
| GR2-XS | 1 (established, below) | 1 | 8 colour (the TR's Virtual24 board), 4 aux, 4 cid; Z buffer optional ("GR2-XS with Z-buffer" is on record); no `gfxinfo` capture held | unknown |

An 8-bit XS did ship for the Indigo, and it has one GE. Evidence, in order: the Elan Graphics Technical Report's configuration list names "IRIS Indigo XS" as the 8-bit Virtual24 board with a 24-bit Z buffer and 24-bit upgrade optional [public]; the inventory code in the IRIX source (`irix/cmd/hinv/hinv.c`) prints "-XS" for the one-engine flag and appends "24" and " with Z-buffer" from the plane and Z flags, so a board that prints plain "GR2-XS" is one GE and not 24-plane, and the kernel (`gr2_init`, IRIX 5.3 `gr2.o` `0x10000820` to `0x10000870`) sets the one-engine flag (8) from the engine probe's count of 1 [binary][source]; the Library mail archive holds `hinv` captures of "Graphics board: GR2-XS" from R4000 Indigos (`2cb491$l38@news.umbc.edu`; `357bug$oqf@news.acns.nwu.edu`, IRIX 4.0.5IOP; and, taken at the boot monitor with no working IRIX, `34875432.63DE@lmco.com`, quoted again in `3488268D.41C6@zurich.sgi.com`, and `3482CC09.44020AA5@mail.bicos.de`), of "GR2-XS with Z-buffer" (`3srfbb$bl2@gwdu19.gwdg.de`, IRIX 4.0.5f; `427pcq$2oh4@info4.rus.uni-stuttgart.de`, IRIX 5.3) and from an R3000 Indigo on IRIX 5.1.1.2 (`Cqpn8w.2r0@sap-ag.de`); that is eight messages and seven machines, because the zurich message quotes the lmco one [public]; and an SGI engineer states that the XZ has two GE7 and the XS24 with Z has one, and that an XS can take a Z buffer (`jip5uoq@zuni.esd.sgi.com`) [public]. As far as the probe shows, the 24-plane XS24 and the 8-bit XS differ only in the memory boards fitted: slot A alone gives 8 bit, all three give 24 ([port values](#4-probe-answers-per-indigo-variant) above: `port3` `0x3d` against `0x15`). The IRIX source also names a four-engine 8-bit no-Z board, "XSM", as a special build; it is outside the Indigo catalogue until a capture shows it. Grade: established that XS shipped with one GE7; the plane count is the TR's, with the name as a consistency check.

The model's catalogue should add XS beside XS24, XZ and Elan: one GE, `port3` `0x3d`, Z optional (`port1` bits 3:2 = 3 when absent).

Register answers a probe needs, for board revision 2. Established [binary] for which bits software reads and how it combines them (kernel `Gr2Probe`, PROM probe and `gr2_boardvers`, which all use byte loads at the first byte of each word); the per-variant values are **inferred** from the decode and the postings, because no source lists register values per variant:

| Read | Decode | Value for the model |
|---|---|---|
| `probe_word` | must be 0xdeadbeef | all variants |
| port0 (+0x6c000), byte | bits 3:0 are the board revision inverted; zero fails the probe. The diagnostic program (IRIX source `hwinv.c` and the `ide` binary) reads bit 5 un-inverted as the render-engine count: set prints two RE3s, clear one | 0xdd: revision 2, bit 5 clear, so one render engine. Bits 7:6 and 4 are not read at revision 2 |
| port1 (+0x6c004) | bit 0 monitor code bit 0; bit 1 Z DRAM type (ide: 64Kx16 or 256Kx4); bits 3:2 Z board | Z board present: field value 1 or 2; **absent: 3** (both bits set). The kernel, the PROM library and the diagnostic program all agree: the IRIX source's `hwinv.c` prints "Board is not installed" for field value 3 and the kernel's record marks the Z buffer absent only when `(port1 & 0xc) == 0xc`. The earlier note that `ide` encoded absent as 0 was a misreading. NetBSD's opposite test [public] stays an unexplained difference of that driver. |
| port2 (+0x6c008) | bits 1:0 monitor code bits 2:1; bits 3:2 back end (VB) version, inverted by the kernel, zero after inversion fails; bits 5:4 super video board version, inverted, nonzero after inversion makes gfxinfo print a "Video board revision" line | **bits 3:2 = 01** (VB1.1, the value every Indigo capture shows: gfxinfo prints the inverted field minus one) and **bits 5:4 = 11** (no super video board; no capture has the extra line). Base value `0x34`, with monitor code bits 2:1 in bits 1:0. A base of 0 would print "VB1.2" and a video-board line; `0x15` would print the video-board line |
| port3 (+0x6c00c) | memory board versions: bits 1:0, 3:2, 5:4 for slots A, B, C; kernel: slot present unless the field is 3; ide: present unless the field is 3 (the diagnostic's "Board is not installed" value) | present boards: field value 1; XS 8 bit: slot A only (`0x3d`); a 16-bit pair (A and B, `0x35`) is "not supported" in the IRIX source; XS24, XZ, Elan 24 bit: A, B and C (`0x15`); absent slot: 3 |
| GE slots (+0x68000, stride 0x400) | the kernel writes five words per slot 1 to 7 and reads them back; count = highest answering slot + 1 | XS and XS24: slot 0 only; XZ: slots 0 and 1; Elan: slots 0 to 3. Absent slots must neither fault on the five stores nor on the five loads: see the paragraph below |
| GE revision (+0x683f4 after a store of 0) | bits 7:5; gfxinfo prints GE7 rev B for field value 2 | 2 << 5 (`0x40`); see section 1 for the decode |
| HQ revision | see section 1 (`hq_gepc` bits 23:16 for gfxinfo, status bits 31:23 for the PROMs) | 0 in both |
| VC1 revision | internal register 5 low 3 bits via the VC1 ports; gfxinfo prints rev B for 2 | 2 |
| monitor ID | port1 bit 0 and port2 bits 1:0 give the monitor code 0 to 7; code 6 selects 1024 x 768, others 1280 x 1024; gfxinfo "unknown, assuming 19 inch monitor" appears with these boards, so the mapping from code to cable is not needed | 0: 1280 x 1024 at 60 Hz |

Per product, for the four ports (revision 2, monitor code bits `m0` = port1 bit 0 and `m21` = port2 bits 1:0; the monitor code 0 default is 60 Hz 1280 by 1024, and the diagnostic's text for code 15 is "default 1280x1024@60hz monitor presumed"):

| Product | port0 | port1 | port2 | port3 | GE slots answering |
|---|---|---|---|---|---|
| XS (8 bit, no Z) | `0xdd` | `0x0c \| m0` | `0x34 \| m21` | `0x3d` | 0 |
| XS with Z | `0xdd` | `0x04 \| m0` | `0x34 \| m21` | `0x3d` | 0 |
| XS24 with Z | `0xdd` | `0x04 \| m0` | `0x34 \| m21` | `0x15` | 0 |
| XZ | `0xdd` | `0x04 \| m0` | `0x34 \| m21` | `0x15` | 0 and 1 |
| Elan | `0xdd` | `0x04 \| m0` | `0x34 \| m21` | `0x15` | 0 to 3 |

Grades: the decode that turns each field into a gfxinfo line or an inventory flag is established [binary][source] (`Gr2Probe`, IRIX 5.3 `gr2_init.o` `0x10000234`; `Gr2InitInfo` and `hwinv.c` in the IRIX source). The values are inferred from the decode and from what the captures print; no document lists them. The hinv name follows from the GE count and the plane and Z flags: one GE prints "-XS", plus "24" with 24 planes, plus " with Z-buffer" (hinv source); two prints "-XZ" and appends " missing bitplanes" or " missing Z"; four prints "-Elan" with 24 planes and Z, else "-XSM"; eight prints "-Extreme". Bit 1 of port1 (the Z DRAM type) is read only by the diagnostic and is not constrained. Writes to `port0` and `port1` (clock select, VC1 reset) share the addresses with these reads; whether a read after a write still returns the configuration bits is unknown, and the shipped drivers probe before they write.

Absent GE slots (question 6). The engine probe (`_Gr2ProbeGEs`, IRIX 5.3 `gr2_init.o` `0x10000054`; the PROM library and the diagnostic's `Gr2ProbeGEs` in the IRIX source do the same) stores five distinct words per slot for slots 1 to 7 and loads them back, with plain accesses, no `badaddr` guard and no exception handler, on every board it meets. Only the board probe (`Gr2Probe`) is guarded, and only at the probe word (`+0x6a07c`). The captured one-engine boards (XS, XS24: "1 GE") run IRIX this way for years, so an absent slot cannot raise a bus error on either the stores or the loads (inferred as a necessary consequence; the accesses themselves are established [binary][source]). What an absent slot reads is not fixed by any shipped code: a slot counts only if all five words come back, so any value that is not the pattern passes as absent. Model: absent slots accept the stores and read 0. Do not echo the stored words back: a model that remembers writes would make every slot present. The loop does not stop at the first miss; the count is the highest answering slot plus one, so the present slots must be contiguous from 0. Grade: inferred for the hardware, established for the software.

Byte lane of a narrow probe read. Every narrow access the shipped code makes to the board ports is a byte at the first byte of the word, the most significant lane on this big-endian host: the kernel's `Gr2Probe` (`lbu` at `+0x6c000`, `+0x6c004`, `+0x6c008`, `+0x6c00c`), the PROM probe, the diagnostic program's `gr2_boardvers` (`lbu` at the same four offsets), `Gr2ProbeVC1` (`lbu` at `+0x6c04c`, `sb` at `+0x6c050` and `+0x6c054`) and the VC1 `sysctl` byte. Established [binary]. The GE revision is a word load of `+0x683f4` masked to its low byte, a different register. NetBSD reads the board ports as words and masks the low bits [public]; the two cannot both be right unless the gate array drives every lane alike. The model returns the value in the first byte and replicates it in the other three bytes of a word read, which satisfies both readers; a byte load must never come from any other lane. Which the hardware does is unknown, and no shipped program distinguishes them.

Byte position of the board revision: settled for every shipped program. The kernel (`Gr2Probe`), both PROMs and the diagnostic program (`gr2_boardvers`) all load a byte at the first byte of each word (the most significant byte position on this big-endian host). NetBSD masks the low bits of a word instead [public]. The model should return the value at the first byte of the word and, to satisfy NetBSD as well, replicate it in all four byte positions of a word read; whether the board does so is unknown. Established [binary] for the three programs.

## 5. Board outputs to INT2

Only two that any shipped software uses: GIO line 0 (FIFO, section 1) and GIO line 2 (vertical retrace; the `intr` register's line is unknown, so "only two" is inferred from the registrations; what enables the retrace line is in [vc1-express](../../devices/vc1-express/README.md#retrace-interrupt): the INT2 mask is set by `setgiovector`, and VC1 `sysctl` bit 0 set blocks the pulse). The retrace latch is cleared by pulsing bit 3 of the INT2 port byte `0xbfb801df` low and high (PROM at `0xbfc0ed60`), and the retrace status is also readable at bit 0 of the INT2 status byte at `0xbfb801d3` (the kernel handler polls it, up to ten times). `gr2_init` registers no handler on GIO line 1 (other drivers, such as the GIO Ethernet, use it). The MC graphics DMA done interrupt (INT2 local-0 bit 4) is the MC's, not the board's. Established [binary] for the registrations (`gr2_init` calls `setgiovector` twice) and the PROM stores; interrupt tables are in the chips repository.

The bit the FIFO handler touches, bit 0 of the byte at `0xbfb801c7` (and the status byte at `0xbfb801c3`), is the INT2 local-0 mask (status) bit for that same GIO line 0: it is not a second source. The handler clears the mask bit on entry so the level cannot retrigger while it runs and sets it again on exit. Established [binary] (`Gr2FIFOHandler`); the bit meaning is the chips interrupts page.

## 6. What the graphics reset clears

The reset is MC `cpuctrl0` bit 10 (active low): `Gr2Reset` clears it, waits 10 us, sets it; the PROM does the same with its own delay. Software never reads anything to see what the reset cleared; what it does afterwards shows what it assumes is lost. Everything below is re-initialised after the reset, in this order (`gr2_earlyinit`, `Gr2Init`, `_Gr2RegisterInit`, `_Gr2HQ2RegInit`), so a model that clears all of it satisfies the shipped drivers: the pixel clock (`Gr2StartClock`), the three Bt457 DACs, the XMAP5 chips (three init passes), the VC1 SRAM images and registers, the HQ2 registers (`numge`, the two timeouts, `fifo_full`, `fifo_empty`, `refresh`), the HQ2 and GE7 microstores and the shared-RAM constants (downloaded again; the PROM loads its built-in console images, the kernel the built-in image then the full images through an ioctl), the unstall and GE program counter writes, the INT2 retrace latch, and the FIFO count and flags. After the reset the kernel does not write status flags or `intr`, so it assumes they are cleared. Established [binary] for what is re-written; "reset clears it" is **inferred** for each item, because no program checks. What survives a reset is unknown: none of the shipped code relies on any board register keeping its value.

## 7. Token catalogue gaps

### Modifier bits

The FIFO address carries the command in bits 10:2 (the microcode entry) and modifier bits above: established [binary] for the address forms, **inferred** for their roles.

| Address bits | Observed use |
|---|---|
| 16 | set for short and integer operands: `+0x5298c` against `+0x4298c` (vertex), `+0x5e3f8` against `+0x4e3f8` (index) |
| 15:12 | attribute jump index; 0 for console and X driver tokens (`+0x404xx`, `+0x406xx`), 2 for most GL state tokens (`+0x42xxx`), 4 and 6 for three- and two-component vertex floats, 8 for byte colours; also seen in the GL core: 1 (`+0x410cc`, `+0x41188`) and 0xe (`+0x4e3f8`, the index token); the 16-word table at the HQ2 `attr_jump` registers has exactly that many entries |
| 11 | clear in every shipped address |

The PROM and kernel console tokens never set bits above 10. The X driver forms `base + 0x40000 + slot * 4` with slots 300 to 362 and 490, and sends data to slot 479. The slot numbers of the three programs overlap only where the modifier bits differ (for example slot 360 is `+0x405a0` in the X driver and `+0x425a0` in the GL core), so the full address, not the slot, identifies a command (inferred).

### X driver tokens

Slots and the functions that store them, from the shipped X driver's own function names; "data stores" is the largest count of stores to the data port in the straight-line run after a token store in the disassembly (a lower bound, **inferred**; loops and reordered stores hide some). The tokens' names are unknown. Established [binary] for the offsets and call sites.

| Token | Slot | Used by (most frequent first) | Data stores |
|---|---|---|---|
| `+0x404b0` | 300 | `expInitHW` | 0 |
| `+0x404b4` | 301 | `expLineSS`, `expSegmentSS` | 4 |
| `+0x404bc` | 303 | `expZeroPolyArc`, `expPolyPoint`, `expDrawPoints` | 2 |
| `+0x404c0` | 304 | `expValidateVisual`, `expInitHW`, `expClearOverlays`, `expDrawCID`, `expDrawSolidRects` | 4 |
| `+0x404c4` | 305 | `expFillTriangle`, `expSolidSpans`, `expFillPolygon` | 3 |
| `+0x404cc` | 307 | `expLineSD`, `expLineSS`, `expFastLineSD`, `expSegmentSS` | 6 |
| `+0x404d4` | 309 | `expLineSD`, `expValidateVisual`, `expCopyRect`, `expStippledFillRects`, `expLineSS` (207 sites) | 0 |
| `+0x404dc`, `+0x404e0` | 311, 312 | stippled fills, glyph blits (`expPolyGlyphBltTE8/16/32`), `expZeroPolyArc` | 0 |
| `+0x404e4` | 313 | `expOpStippledFillRects`, `expStippledSpans`, `expDrawOpaqueMonoImage` | 0 |
| `+0x404e8` to `+0x40500` | 314 to 320 | `expTileRects`, `expStippledFillRects` | 4, 0, 0, 15, 7, 6, 6 |
| `+0x4050c` to `+0x40518` | 323 to 326 | `expDrawMonoImage`, `expDrawOpaqueMonoImage` | 11 or 3 or 4, 3, 3, 3 |
| `+0x40520`, `+0x40528` | 328, 330 | `expPolyPoint`, `expLineSS`, `expSegmentSS` | 0, 3 |
| `+0x4052c` | 331 | `expValidateVisual`, `expLineSD`, `expCopyRect`, `expStippledFillRects` (221 sites) | 0 |
| `+0x40530` | 332 | `expValidateVisual`, `expLineSD`, `expInitHW`, `expCopyRect` (60 sites) | 3 |
| `+0x40540` | 336 | `expInitHW`, `expDrawCID` | 0 |
| `+0x40544` | 337 | `expValidateWindowPriv`, `expReadImage`, `expCopyRect`, `expDrawImage` | 1 |
| `+0x40550` | 340 | `expValidateWindowPriv`, `expCopyRect` | 7 |
| `+0x40558` | 342 | `expDrawImage`, `expDrawImage12`, `expDrawImage24` | 6 or 22 |
| `+0x40560` | 344 | `expReadImage`, `expReadImage12`, `expReadImage24` | 4 (origin, size) |
| `+0x40564` to `+0x4056c` | 345 to 347 | `expSegmentSS`, `expStippledSpans` | 0 |
| `+0x40570` | 348 | `expStippledFillRects` | 6 |
| `+0x40574` to `+0x40580` | 349 to 352 | `expDrawMonoImage`, `expDrawOpaqueMonoImage` | 7, 11, 19 or 3, 3 |
| `+0x40584` to `+0x40590` | 353 to 356 | `expPolyPoint`, `expFastLineSD`, `expSegmentSS`, `expLineSS` | 0 to 5 |
| `+0x4059c` to `+0x405a8` | 359 to 362 | `expAttachXvc` | 0 |
| `+0x407a8` | 490 | `expDrawMonoImage`, `expValidateVisual`, `expLineSS` (181 sites) | 0 |

From the names: slots 331 and 309 are the most frequent state tokens (they appear in nearly every drawing function, likely write-mask or colour setup); 332 and 304 carry three or four operands. The X server's image functions follow the sequence in section 1 (store 0 to `finish3`, token, operands, poll, read shared RAM at `+0x1b000`). Operand field meanings are not decoded without the microcode (GE7 and HQ2 instruction sets unknown).

### IP22 library slot numbering

Not checked. The software mirror's extracted IRIX 6.5 base tree (archive.org "IRIX 6.4 for Origin, Onyx2 and OCTANE", directory `6.5-base`) does hold `usr/gfx/arch/IP22GR2NG1` and `IP22GR2NG132` (and `IP19GR2EV`, `IP21GR2EV`, `IP25GR2SH`) with `libGLcore.so`, so the earlier "no `IP22GR2*` held" was wrong for that store. Whether the Library indexes them is unknown; slot numbering there is unread. The Indigo2 board topology is a different configuration anyway (survey).

## 8. Microcode image checksums

Held: the IRIX 6.5 base set and the IRIX 5.3 disc (round 9). SHA-256 [binary], from the Library's acquisition manifest and re-computed on the readers' copies:

| Release | Image | Size (bytes) | SHA-256 |
|---|---|---|---|
| 6.5 | `usr/gfx/ucode/hq2.bin` | 58682 | `0c1fbe18d1b451ee32fb81afa4dd85aa86beeee2c5f7fc8b2e33e79e4375fc94` |
| 6.5 | `usr/gfx/ucode/ge7.bin` | 611432 | `085d9e923476750673146a517df5847636e7165fb8e7cb4723f7eef07b114729` |
| 5.3 | `usr/gfx/ucode/hq2.bin` | 57392 | `94ec5ba56589a66657469ce8f72b2717576196b2210a54160f106c9d5c3fd851` |
| 5.3 | `usr/gfx/ucode/ge7.bin` | 608390 | `a9703e817e5de24054b07b44d97afa5d3bc4ee44af97433244a7e6a98be4fc15` |

The 6.5 hashes are on a second copy (the mirror's `6.5-base` tree), whose `IP20boot/gr2.a` hashes differently (`f05d4700...a8a`) from the one this page read, so the two sets agree on the microcode and not on the driver archive. The two releases' images are different builds: 5.3 equals 6.5 word for word below GE7 1363 and differs in a handful of routines above it ([microcode.md](microcode.md#the-irix-53-images)); a model that runs the full images should take the pair of one release, not mix them. The 6.2 and other 6.5 media images were not found; unknown for those releases.

## 9. Model checklist (Elan first)

1. Window at `0x1f000000`, 4 MiB; probe word; board revision 2 values from section 4; GE slots 0 to 3 for Elan.
2. HQ2 registers per `registers.toml`, status word with live FIFO count and three finish flags; FIFO line on INT2 local 0 bit 0 from count against `fifo_full`; drain the count as tokens are consumed.
3. Console tokens and microcode download windows per [pipeline.md](pipeline.md) and [devices/ge7](../../devices/ge7/README.md); built-in console images load and verify; unstall and GE program counter writes accepted.
4. Finish-flag ports: store sets flag from bit 0; set flags after queued commands retire (kernel monitor change, image read, DMA, context tokens 481 to 484 and 496).
5. DMA: GIO slave at `gedma`, board commands for pixel transfer, completion flag 2 (and flag 1 for the PROM and diagnostic path).
6. Retrace on GIO line 2, INT2 port byte pulse clears; `status` bit 0 of INT2 status byte `0xbfb801d3`.
7. Graphics reset: clear all state above.

## 10. Boot sequence: what the kernel writes, in order

The R4000 Indigo kernel's start-up and microcode-load sequence, read from the IRIX 5.3 `IP20boot/gr2.a` (`gr2.o`, `gr2_init.o`, `gr2_tport.o`, `gr2_tpucode.o`; o32 objects) [binary]; each function named below was read in full. The 6.5 objects were compared at `_Gr2HQ2RegInit` (same six stores, same values), `Gr2Start` (same stores) and `gr2_earlyinit` (same order; 6.5 additionally refuses the reuse path when the ready word is 2, which the 5.3 code reaches the same way, because its test is `== 1`). Everything else below that is common to the two is established for 5.3 and **inferred** for 6.5. Offsets are from the graphics window (`0x1f000000`); "register" names are those of [devices/hq2](../../devices/hq2/README.md). The kernel never writes an RE3 or a GE7 register directly: the only GE7 accesses are the probe, the microstore loader and the two program-counter ports; RE3 is written by the microcode alone (the `INIT` token's routine, [devices/re3](../../devices/re3/README.md)). Established [binary] for the absence in these objects.

### A. Per board, at kernel start-up (`gr2_earlyinit`, `gr2.o`)

1. Clear the 60-byte board record; `Gr2Probe` ([section 4](#4-probe-answers-per-indigo-variant)). A failed probe skips the board, and so does a failed `Gr2Init` or `Gr2TpSetup` below.
2. **Reuse test.** If the shared-RAM word `ucode_ready` (`+0x1fffc`) reads 1 *and* this is the first time `gr2_earlyinit` has run since boot, none of steps 3 and 4 runs: the kernel keeps what the board holds, copies the low byte of the shared word `+0x1ffe0` into record byte `0x32`, and only rewrites the cursor image (`initGr2Cursor`, 256 zero bytes at VC1 SRAM `0xa00`, then VC1 registers `0x20` = `0xa00` and three zero half-words). Otherwise steps 3 and 4 run. Established. **Who leaves 1 in the word before the kernel runs: the 4.0.5G PROM.** Its text-port setup (`0xbfc1229c`, the same sequence as the kernel's `Gr2TpSetup`: HQ2 and GE7 console downloads, `gepc` and `unstall` zeroed, the board-class store, a short delay, a blank-screen call) ends with a store of 1 to the word at `0xbfc1237c` (`lui 2`, store at -4), and stores 0 to it on either download failing (`0xbfc122cc`, `0xbfc122f8`). Established [binary], and the IRIX source's PROM library does the same with a named constant for the console-microcode state (`shram[TP_PROBE_ID] = UCODE_TP`, `lib/libsk/graphics/EXPRESS/gr2_init.c`; the diagnostic program stores a different constant when it loads its own images). The 4.0.5D PROM's setup (`0xbfc0f504` to `0xbfc0f588`, INIT store at `0xbfc0f578`) does not write it, and a search of the whole 4.0.5D image for a store of -4 from a `lui 2` base finds none, so a 4.0.5D machine reaches the kernel with whatever the word held, normally 0. Inferred for 4.0.5D (absence by search). So:
   - Boot through the 4.0.5G PROM with the console microcode running: the word is 1 and the kernel takes the reuse path on its first `gr2_earlyinit`. It then needs the board to still hold its console state, and it copies the low byte of `+0x1ffe0` (the RE3 revision, section 4) into the record. A model that boots the real PROM gets this for free if it executes the console tokens and keeps shared RAM.
   - Boot a kernel directly, or through 4.0.5D: start the word at 0. The kernel then resets and re-initialises the board, which is the safe choice and needs no PROM state.
3. `Gr2Reset` (MC `cpuctrl0` bit 10 low, 10 us, high), then `Gr2StartClock` ([devices/clock](../../devices/clock/README.md)), then `Gr2Init`.
4. `Gr2TpSetup(base, width - 1, height - 1, 0)` (section C), which writes the console images and starts them.
5. `Gr2ProbeVC1`: VC1 `addrhi` = 0, `addrlo` = 5, then read `testreg` and keep bits 2:0 as the VC1 revision (record byte `0x33`).
6. Record byte `0x35` = 1 (board live), the board table entry's flag = 1, `dmasync` (`+0x6a050`) = 0; for the first live board only, `htp_register_board(base, gr2_htp_fncs, width, height)` registers the console port between the record store and the last two stores (`gr2.o` `0x100006f4` to `0x10000704`). Established. `Gr2Init` always returns 1 in this object, so its failure branch in step 3 is never taken.

Later, `gr2_init` (after the interrupt system is up): `Gr2RetraceInit`, `setgiovector` for GIO line 0 (`Gr2FIFOInterrupt`) and line 2 (`gr2_retr_intr`), `GfxRegisterBoard`. [section 5](#5-board-outputs-to-int2) has what the lines mean.

### B. `Gr2Init`: `_Gr2RegisterInit`, then `_Gr2HQ2RegInit`

`_Gr2RegisterInit` in order: pulse INT2 byte `0xbfb801df` bit 3 (clear, set); `_Gr2DacInit` on the three Bt457 windows `+0x6c0a0`, `+0x6c0c0` and `+0x6c0e0`; VC1 `sysctl` = 1, the cursor-mode and interlace and width writes, the timing images for the monitor code, the display-ID tables, VC1 registers `0x14`, `0x40`, `0x42`, `0x44`, `0x60`, `initGr2Cursor`, `sysctl` = `0x0c`; then `_Gr2XMAPInit1`, `2` and `3`. Every step and value is on the chip pages: [vc1-express](../../devices/vc1-express/README.md#initialisation-as-shipped), [xmap5](../../devices/xmap5/README.md#initialisation-as-shipped), [bt457](../../devices/bt457/README.md). Established; the monitor code picks the timing images ([monitor codes](../../devices/vc1-express/README.md#monitor-codes-and-the-kernels-built-in-tables)).

`_Gr2HQ2RegInit` writes six HQ2 words, in this order [binary, established]:

| Register | Offset | Value | Reading |
|---|---|---|---|
| `numge` | `+0x6a044` | probe record byte `0x36` (the GE count), with bit 4 also set when the count is 8 | inferred: the number of populated GE7 slots |
| `refresh` | `+0x6a080` | `0x10` | unknown meaning |
| `fifo_full_timeout` | `+0x6a054` | `0x64` | inferred |
| `fifo_empty_timeout` | `+0x6a058` | `0xff` | inferred |
| `fifo_full` | `+0x6a05c` | `0x28` (40, the FIFO interrupt threshold of [section 1](#what-raises-the-fifo-interrupt-and-how-it-clears)) | established as the kernel's default threshold |
| `fifo_empty` | `+0x6a060` | `1` | unknown meaning |

A model's reset values for these registers need not match (software writes them before use); it must accept the writes.

### C. Console images (`Gr2TpSetup`, `gr2_tport.o` and `gr2_tpucode.o`)

1. `Gr2DownloadHQ2` on the kernel's built-in HQ2 console image (129 records, named "IP12/GR2 PROM HQ Microcode"). A failure writes 0 to `ucode_ready` and returns -1.
2. `Gr2DownloadGE7` on the built-in GE7 console image (264 records, "IP12/GR2 PROM GE Microcode"), the same way. Both loaders are on the chip pages: HQ2 first writes the 16-word attribute jump table from image offset `0xfc`, then each record word at `+0x60000 + 4 * address`, and reads every word back; GE7 copies the 512 constants words to shared RAM word 0 and reads them back, clears the microstore, then per record sets `gepc` and writes `+0x683e0`, `+0x683e4`, `+0x683e8`, `+0x683ec` and last `+0x6a064` ([devices/ge7](../../devices/ge7/README.md)). A mismatch makes the loader return failure (and print a line with the verbose flag, which the kernel does not set).
3. `gepc` (`+0x6a070`) = 0, `unstall` (`+0x6a078`) = 0: the GE runs from address 0.
4. The `INIT` token (`+0x40644`) with the **board class** as its operand: 0 for board revisions 1 to 3, 1 for 4, 9, 10 and 11, 2 for 5 to 8 and 12 to 15 (the revision is the inverted low nibble of the byte at `+0x6c000`, [section 4](#4-probe-answers-per-indigo-variant); revision 0 fails `Gr2Probe` and never gets here; the 12-entry jump table is at `gr2_tpucode.o` `0x100001f8`, the selector at `Gr2TpSetup+0x98` to `+0xf4`, and the same mapping is at `Gr2Start` `0x10001a1c` to `0x10001a70` of `gr2.o`, which reads the revision from record byte `0x2e`); then `flushbus` and a 9 us delay. Established for the mapping; the meaning of the class is **inferred** (it selects the back-end variant the microcode drives).
5. `COLOR` (`+0x40648`) = 0, then the `SBOXFI` token (`+0x40654`) with operands 0, 0 (data port), `width - 1`, `height - 1`: a full-screen box in colour 0. `Gr2TpSetup`'s own stores do not poll the FIFO line; the later console calls (`Gr2TpColor`, `Gr2TpDrawBitmap` and the rest) wait for INT2 status byte `0xbfb801c3` bit 0 to clear before each token.
6. `Gr2BlankScreen(base, 0)`: wait up to 10000 x 1 us for XMAP5 chip 0's status bit 0 (`+0x6c11c`) to clear, then for each Bt457 window write address byte 4 and data `0xff` (unblank; the blank case writes 0).
7. `ucode_ready` = 1.

### D. Full images, from user space (`gfxinit`, `Gr2Download`, `Gr2Start`)

`gfxinit` (5.3 `usr/gfx/gfxinit`) maps `hq2.bin`, then `ge7.bin`, from the microcode directory and hands each to the kernel in one request of the form {length, pointer} ([binary], the order is that of the two call sites; the request code `0x6c` is the immediate `li a1,108` before each call, `gfxinit` `0x40a14c` and `0x40a32c`; which library call takes it is not decoded). `Gr2Download` accepts a length above 0 and below `0x100001` (otherwise 0 to `ucode_ready` and EINVAL), maps the user buffer into kernel space (`userdma` and `maputokv`, unmapped again afterwards; nothing is copied, and a failed `userdma` gives EFAULT, `0x10001c90` to `0x10001cb0`), chooses the loader by the magic half-word (`0x965e` HQ2, `0x966e` GE7; anything else prints the magic and returns an error, `gr2.o` `0x10001d58`) and writes 0 to `ucode_ready` when the loader fails. A model must therefore accept a second HQ2 and GE7 load over the running console images with the same register sequence. `Gr2Download` itself makes no reset call, but `Gr2Initialize` (below) does, and the board function table lists Initialize, Download and Start in that order (`gr2.o` `.data` `0x10004b64`): whether the generic graphics layer calls `Gr2Initialize` between the console setup and the downloads was not read (`gfx.o` and `rrm.o` are not read), so a reset between the console images and the full images is **inferred** from that order.

`Gr2Initialize` (`gr2.o` `0x10001afc`) writes, in order: `htp_register_board` with four zero arguments (what that does to the console port is not decoded), `setgiovector` for line 2 to `gr2_retr_intr`, `Gr2Reset`, `Gr2StartClock`, two zero words of kernel data, three timing fields of the board record from record byte `0x2d` (the same lines as in `gr2_init`), then `Gr2Init`, so the six HQ2 stores of B repeat; when record byte `0x38` is non-zero it also calls `ev1_softprobe` and, on a hit, `ev1_reset`. It does not call `Gr2TpSetup` and does not touch `ucode_ready`, so the word still reads 1 after it. The same objects of 6.5 have the same calls in the same order [binary, established for the call list]. Established for 5.3.

`Gr2Start`, run when the graphics system starts, writes: `setgiovector` for line 2 to `Gr2RetraceInterrupt` (the full retrace handler replaces `gr2_retr_intr`), record byte `0x35` = 0, `gepc` = 0, `unstall` = 0, `fin2` = 0, then the board class to the data port `+0x4077c` with no token before it, and waits for status bit 1 (`finflag2`), up to 1,000,000 us, calling `gr2_error` on a timeout whose message is "RE version read back failed" (`gr2.o` `0x100046c8`). Then record byte `0x32` = the low byte of the shared word `+0x1ffe0`, `ucode_ready` = 2 and `Gr2BlankScreen(base, 0)`. Established for the stores, the poll and the message.

The class value is chosen from the board revision (record byte `0x2e`) by a 12-entry table (`gr2.o` `0x10004ab4`, selector `0x10001a1c`): revisions 0 to 3 give 0, 4 and 9 to 11 give 1, 5 to 8 and 12 to 15 give 2. The IRIX source's PROM library has the same mapping for the `INIT` token operand. The Indigo is revision 2, so **the class is always 0**, and a model that sends or expects 0 is right. What the class selects is **inferred**: the back-end variant the microcode drives (video and clock access differ between the Indigo's revision below 4 and the later boards, [devices/clock](../../devices/clock/README.md)); no shipped code or source names the effect, and the 4.0.5D PROM sends 0 without a selection. The 4.0.5G PROM sends 0 for revisions below 4, 1 for 4 and 2 otherwise (`0xbfc12324` to `0xbfc1236c`), a slightly different table that agrees on the Indigo.

What the full image does with it, and what the model must do: the timeout message says the image's first routine reads the RE3's version, so it consumes the class word, reads the render engine's revision, stores it in the low byte of `+0x1ffe0` (the byte gfxinfo decodes as RE3 revision, section 4) and raises finish flag 2. **Inferred** from the message and the kernel's reads; the image's boot routine at GE7 0 was not decoded. A model that does not execute the image must, on the class write, store the RE3 revision byte (4 for rev D) at `+0x1ffe0` and raise `finflag2`. Who else writes `+0x1ffe0` is unknown.

### What a model must provide for this sequence

- Probe answers ([section 4](#4-probe-answers-per-indigo-variant)), the reset ([section 6](#6-what-the-graphics-reset-clears)) and the six HQ2 stores above accepted, a second time as well (`Gr2Initialize`).
- Loaders for both image kinds with read-back, the microstore clear, and `gepc` and `unstall` writes.
- A console `INIT` token that accepts the class operand and a box fill, so the first FIFO words after the download are consumed (the count drains as in [section 1](#what-raises-the-fifo-interrupt-and-how-it-clears)).
- `ucode_ready` as a plain shared-RAM word (0 at power-up, 1 after the console setup, 2 after `Gr2Start`), and the finish flag 2 raised after the class word at start.

## Review (2026-11-23)

Independent review of the first host-contract revision against `gr2.a` (`gr2.o`, `gr2_dma.o`, `gr2_init.o`), PROMs 4.0.5D and 4.0.5G, `ide.IP20`
(`744fdebc...df14`), NetBSD `grtwo.c` and the Library mail archive. Disassembly was done directly from the binaries.

1. `+0x6a040` map: CONFIRMED (all fields, finish clears, `dmasync` write values). FIFO line `>=` vs `>`: UNVERIFIED in hardware; the handler's `sltu count, threshold`
   is a software expectation of `>=` (added). Overflow handling: WRONG (it calls `gr2_error`); fixed.
2. `+0x6a06c`: CONFIRMED as `hq_gepc`; WRONG that it is read once (`gr2_error` logs its low 16 bits); "not a revision" downgraded to unsettled.
3. Context switch: CONFIRMED slots 481 to 484 and 496 (`+0x407c0` carries the render-node index), finish-flag save and restore through bit 0 and `+0x6b000`, MC DMA through `vdma_kv` or `fakePICdma`.
   WRONG that every slot gets `token_operand`: 481 stores 0, 482 the word count; fixed.
4. Pixel DMA: CONFIRMED `+0x6a068` as the GIO address, modes 0x54/0x56 (flag bit 0 set gives 0x54), status bit 1 wait, 4.0.5G PROM `fin1` and bit 2 (1000 us x 20; 4.0.5D has no pixel DMA).
   GRADE: INT2 local 0 bit 4 is not waited on in `gr2.a`; "HQ2 never starts transfers" is inferred and scoped (see section 3).
5. Variants: CONFIRMED engine counts and the first-byte `lbu` reads (`Gr2Probe`). WRONG that XS24 prints no RE count (it prints "1 RE"); message-ids added. Port values per variant stay inferred.
6. INT2: CONFIRMED the two `setgiovector` calls (lines 0 and 2), the `0xbfb801c7` mask clear and set, the `0xbfb801df` bit 3 pulse and the `0xbfb801d3` bit 0 poll (10 tries). "Only two" is inferred.
7. X driver table: 14 sampled slots (300, 301, 303, 304, 305, 331, 332, 337, 342, 344, 359 to 362, 490) all match the offsets and the user-function sets. Modifier bit 16 CONFIRMED
   at `+0x4e3f8`/`+0x5e3f8`; bit 11 clear CONFIRMED; the 15:12 list was incomplete (1 and 0xe added).
8. Microcode hashes: CONFIRMED on two copies of the 6.5 base set; no other release held. The X driver `gr2.so` (SHA-256 of the mirror copy
   `860b9552...3062`) is not in `references/binaries.md`.
