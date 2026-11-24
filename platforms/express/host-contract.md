# Express (GR2) host contract on the Indigo

What a host program can observe and must provide at the graphics slot of an Indigo (IP20, with IP12 noted) so that the shipped PROMs, the IRIX kernel driver, the X server and the GL core run on a model of the board: status bits, flow control, completion flags, context switching, pixel DMA, probe answers per board variant, interrupts and reset. Written for the Indigo QEMU model and for the planned iris GR2 crate. The chip pages are [devices/hq2](../../devices/hq2/README.md) (command engine, register map in `registers.toml`), [devices/ge7](../../devices/ge7/README.md), [devices/re3](../../devices/re3/README.md), [devices/clock](../../devices/clock/README.md) (board configuration ports), [devices/vc1-express](../../devices/vc1-express/README.md), [devices/xmap5](../../devices/xmap5/README.md) and the DACs; the board survey is [README.md](README.md), the token catalogue [pipeline.md](pipeline.md) and the display back end [display.md](display.md). The host side of the buses is in the chips repository: `devices/mc` (graphics DMA engine, reset bit), `devices/int2` and `platforms/ip20/interrupts.md`, `platforms/ip20/gio.md` (slot window, probe).

Provenance tags on every fact: `[public]` published document or public driver (the Elan Graphics Technical Report, NetBSD `grtwo.c`, Usenet postings in the Library), `[binary]` a shipped binary (a software expectation; the routine or message is named), `[vendor-derived]` upstream headers (not used on this page). Grades as in [AGENTS.md](../../AGENTS.md): established (read in full), inferred (reasoned), unknown. Binaries read: `gr2.a` members (`gr2.o`, `gr2_dma.o`, `gr2_init.o`, `gr2_tpucode.o`), the IRIX kernel's graphics-DMA module (`vdma.o`, for the MC calls), PROMs 4.0.5D and 4.0.5G, the diagnostic program `ide.IP20`, the X server driver `gr2.so`, `libGLcore.so` (n32 and o32). Nothing was read on a board.

## 1. HQ2 status word, flow control and finish flags

### The status word (`status` at +0x6a040)

The diagnostic program prints this register, calls it the HQ2 version register, and decodes every field with a name (`gr2_rdHQ2reg`). Established [binary] for the field boundaries and names, which are the ones in `registers.toml`:

| Bits | Name (as printed) | Meaning and who uses it |
|---|---|---|
| 0 | finflag3 | Finish flag 3. Set by microcode, cleared by a store to `finish3`. Used by the kernel (`Gr2SetMonitor`, `Gr2PcxSwap`, `Gr2DestroyDDRN`) and the X server image paths. |
| 1 | finflag2 | Finish flag 2. Cleared by a store of 0 to `fin2`. The kernel's microcode-ready and DMA-done flag (`_Gr2UcodeReady`, both DMA triggers). |
| 2 | finflag1 | Finish flag 1. Cleared by a store of 0 to `fin1`. The diagnostic program's DMA-done flag and the 4.0.5G PROM's pixel-DMA completion flag. |
| 4:3 | dma_sync source | Read-back of `dmasync`: 0 vertical interrupt, 1 video sync, 2 clear, 3 set. |
| 5 | FIFO overflow | The kernel handler prints "FIFO overflowed, data is destroyed - Reset graphics" when set. Nothing clears it in shipped software; inferred cleared by the graphics reset. |
| 12:6 | FIFO count | Words in the FIFO. The kernel compares it with 35 (room), 36, 40, 41 and 63. |
| 13 | FIFO low water | Never read by IRIX. Condition unknown. |
| 15:14 | zero | Printed as zero. |
| 19:16 | ge_ctr | Role unknown. |
| 22:20 | ge_ptr | Role unknown. |
| 31:23 | HQ2 version | Both PROMs store `word >> 23` as the HQ2 revision byte. |

The status bits 1 and 0 decoded: bit 1 is finish flag 2, bit 0 is finish flag 3. The kernel review note "bits 1 and 0 also tested" refers to these. Established [binary] (messages "finish flag not clear" in `Gr2SetMonitor`, the ide field names, and the three clear registers).

### What raises the FIFO interrupt and how it clears

- The interrupt is GIO line 0 (INT2 local interrupt 0, bit 0, `LIO_FIFO`). The kernel registers `Gr2FIFOInterrupt` on it for the graphics slot (`gr2_init`). Established [binary]; line routing in the chips interrupts page.
- The line is a level that follows the FIFO fill count against `fifo_full`. Every PROM drawing routine waits until bit 0 of the INT2 local-0 status byte is clear before each token, then sends a bounded run of operands (at most 25 words for a character strip) without checking again; `fifo_full` is 40. Established [binary] for the polling; **inferred** for the rule "asserted while count >= `fifo_full`", from the PROM budget (40 + 25 fits a 64-word FIFO) and from the kernel handler, which after an interrupt raises `fifo_full` to `min(count + 1, 63)` but not below 40 and masks the INT2 bit, the way one silences a level interrupt. Ties: whether the compare is `>=` or `>` is unknown.
- Kernel use: `Gr2FIFOPollLowater` returns "room" below 35 words; otherwise it writes 40 to `fifo_full` and the process waits for the interrupt or a timeout callback. The handler masks INT2 local-0 bit 0 on entry (byte at `0xbfb801c7`), checks `fifo_overflow`, compares count with the saved threshold, spins up to a software limit while count >= 36 (waiting for 41 or more to drain), sets a "FIFO full seen" flag and forces a reschedule so the producer yields, then unmasks. Established [binary] for the sequence (`Gr2FIFOHandler`).
- The handler never writes a clear register: the line drops when the count falls below the threshold or the threshold is raised. Inferred.
- `intr` (+0x6a074, "Intr bit (cleared by host)" in ide) is a separate host-cleared bit; no driver touches it. Which line it drives is unknown.
- The fill count is in words: every store to the FIFO window adds one, and the microcode consumes them. A model that executes no microcode must drain the count itself (consume tokens as it interprets them) or the line would stay asserted.

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

Answer: the HQ2 version is `status` bits 31:23. Established [binary] that this is the field the diagnostic calls "HQ2 version"; both PROMs store `word >> 23` (4.0.5D `0xbfc0ecec`, 4.0.5G `0xbfc11a98`); NetBSD agrees [public]. The kernel stores `(word at +0x6a06c) >> 16` into the same probe-record byte (`_Gr2ProbeChipRev` `0x124`); the diagnostic program says that register (`hq_gepc`, the HQ to GE program counter) cannot be read because of a hardware bug. So the kernel's value is not a revision; whichever program fills the byte, `gfxinfo` prints "HQ2 rev A" on every Indigo board seen in public postings (XS24, XZ, Elan; Library mail archive). Model: `status` bits 31:23 = 0; `hq_gepc` reads 0 (bits 23:16 are all that is used). Inferred for the value 0 = rev A.

## 2. Context save and swap (`_Gr2CXSaveRestore`, `Gr2PcxSwap`)

The kernel never copies board state itself. It asks the microcode to dump or load it, and moves the data with the MC graphics DMA engine (section 3). Established [binary] for the calls below (`gr2.o` `0xbe0`, `0xe00`); the structure of the per-context records is inferred where noted.

`_Gr2CXSaveRestore(board, buffer, bytes, token_slot, token_operand, direction)`:

1. Store 2 to `dmasync` and 0 to `fin2`.
2. Queue a token at slot `token_slot` (481, 482, 483 or 484, i.e. `+0x40784`, `+0x40788`, `+0x4078c`, `+0x40790`) with `token_operand`; slot 484 also sends the word count (`bytes / 4`) to the data port, slot 482 sends it as the first operand.
3. Run a DMA of `bytes` between the buffer and the DMA port `gedma` (section 3), direction 2 = board to memory, 0 = memory to board; cache write-back before a load, invalidate before a save.
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
- Handshake. Before: store 2 to `dmasync`, store 0 to `fin2`, queue the board command, then start the MC transfer. After: poll status bit 1 (`fin2`), at 1 us steps up to 100,000 (kernel) or on the MC done interrupt (INT2 local 0 bit 4, cleared by the MC; the kernel runs either a polled or a sleeping wait, the second writing 0 to `gedma` twice after a timeout, an abort that is inferred). Established [binary] (`_Gr2MCDMAtrigger`, `_Gr2DMAtrigger`). The 4.0.5G PROM runs a pixel DMA the same way using `fin1` and status bit 2 with a 1000 us x 20 wait. The diagnostic program does the same with `fin1`.
- Can the HQ2 start transfers itself? No evidence of any HQ2 register that holds a memory address or length; every transfer is set up by the CPU through the MC. Inferred (absence).
- What a model must do. Treat the MC DMA engine as already implemented in the MC model; give it a GIO slave at the `gedma` address that accepts and returns words for the length, and set finish flag 2 (or 1) once the board command has consumed the last word. The words are the board's pixel stream: framebuffer or Z, 32 bits each, in the order the board command selects.

## 4. Probe answers per Indigo variant

All Indigo boards in public hardware listings report board revision 2, so the kernel's "below revision 4" branches are the Indigo's [public] (gfxinfo output in Usenet sale postings, Library mail archive). Revision 4 and up is a later back end whose topology is not the Indigo's (see [questions/display.md](../../questions/display.md) 5).

Public per-variant facts (gfxinfo and hinv, IRIX 4.0.5 to 6.5.10 on IP12 and IP20), [public], established as reports:

| hinv name | Geometry engines | Render engines | Planes | Other fields (all variants seen) |
|---|---|---|---|---|
| GR2-XS24 | 1 | not printed | 24 colour, 4 aux, 4 cid, Z buffer present in the posting | GR2 revision 2, VB1.1, HQ2 rev A, GE7 rev B, RE3 rev D, VC1 rev B |
| GR2-XZ | 2 | 1 | 24, 4, 4, Z buffer | same |
| GR2-Elan | 4 | 1 | 24, 4, 4, Z buffer | same |
| GR2-XS | 1 (inferred from the parts list and XS24) | 1 (inferred) | 8 (the TR's Virtual24 8-bit board; no XS posting held) | unknown |

Register answers a probe needs, for board revision 2. Established [binary] for which bits software reads and how it combines them (kernel `Gr2Probe`, PROM probe and `gr2_boardvers`, which all use byte loads at the first byte of each word); the per-variant values are **inferred** from the decode and the postings, because no source lists register values per variant:

| Read | Decode | Value for the model |
|---|---|---|
| `probe_word` | must be 0xdeadbeef | all variants |
| port0 (+0x6c000), byte | bits 3:0 are the board revision inverted; zero fails the probe. ide also prints "Number of RE3s" from the inverted bit 5 (set = one RE3) | 0xdd: revision 2, one render engine. Upper bits otherwise unconstrained |
| port1 (+0x6c004) | bit 0 monitor code bit 0; bits 3:2 Z board; bit 1 Z DRAM type (ide: 64Kx16 or 256Kx4) | Z board present: field value 1 or 2 (both readers agree); absent: 3 (kernel). The shipped programs disagree on the encoding of "absent" (kernel 3, ide 0): [questions/display.md](../../questions/display.md) 2 |
| port2 (+0x6c008) | bits 3:2 back end version, inverted by the kernel (zero after inversion fails); bits 5:4 super video board version (inverted); bits 1:0 monitor code bits 2:1 | back end field nonzero after inversion; VB1.1 vs VB1.0 mapping unknown |
| port3 (+0x6c00c) | memory board versions: bits 1:0, 3:2, 5:4 for slots A, B, C; kernel: slot present unless the field is 3; ide: present unless the field is 0 | present boards: field value 1 (satisfies both); XS 8 bit: slot A only; 16-bit: A and B; XS24, XZ, Elan 24 bit: A, B and C; absent slot: 3 |
| GE slots (+0x68000, stride 0x400) | the kernel writes five words per slot 1 to 7 and reads them back; count = highest answering slot + 1 | XS and XS24: slot 0 only; XZ: slots 0 and 1; Elan: slots 0 to 3. Absent slots must not raise a bus error: the kernel and PROM use plain loads there, so shipped IRIX on a one-engine board would otherwise fault (inferred) |
| GE revision (+0x683f4 after a store of 0) | bits 7:5; gfxinfo prints GE7 rev B | 1 << 5 (value 1 = B; inferred letter scheme) |
| HQ revision | see section 1 | 0 |
| VC1 revision | internal register 5 low 3 bits via the VC1 ports; gfxinfo prints rev B | 1 |
| monitor ID | port1 bit 0 and port2 bits 1:0 give the monitor code 0 to 7; code 6 selects 1024 x 768, others 1280 x 1024; gfxinfo "unknown, assuming 19 inch monitor" appears with these boards, so the mapping from code to cable is not needed | 0: 1280 x 1024 at 60 Hz |

Byte position of the board revision: settled for every shipped program. The kernel (`Gr2Probe`), both PROMs and the diagnostic program (`gr2_boardvers`) all load a byte at the first byte of each word (the most significant byte position on this big-endian host). NetBSD masks the low bits of a word instead [public]. The model should return the value at the first byte of the word and, to satisfy NetBSD as well, replicate it in all four byte positions of a word read; whether the board does so is unknown. Established [binary] for the three programs.

## 5. Board outputs to INT2

Only two: GIO line 0 (FIFO, section 1) and GIO line 2 (vertical retrace; [questions/vc1-express.md](../../questions/vc1-express.md) 2 for what enables it). The retrace latch is cleared by pulsing bit 3 of the INT2 port byte `0xbfb801df` low and high (PROM at `0xbfc0ed60`), and the retrace status is also readable at bit 0 of the INT2 status byte at `0xbfb801d3` (the kernel handler polls it, up to ten times). The kernel registers no handler on GIO line 1. The MC graphics DMA done interrupt (INT2 local-0 bit 4) is the MC's, not the board's. Established [binary] for the registrations (`gr2_init` calls `setgiovector` twice) and the PROM stores; interrupt tables are in the chips repository.

The bit the FIFO handler touches, bit 0 of the byte at `0xbfb801c7` (and the status byte at `0xbfb801c3`), is the INT2 local-0 mask (status) bit for that same GIO line 0: it is not a second source. The handler clears the mask bit on entry so the level cannot retrigger while it runs and sets it again on exit. Established [binary] (`Gr2FIFOHandler`); the bit meaning is the chips interrupts page.

## 6. What the graphics reset clears

The reset is MC `cpuctrl0` bit 10 (active low): `Gr2Reset` clears it, waits 10 us, sets it; the PROM does the same with its own delay. Software never reads anything to see what the reset cleared; what it does afterwards shows what it assumes is lost. Everything below is re-initialised after the reset, in this order (`gr2_earlyinit`, `Gr2Init`, `_Gr2RegisterInit`, `_Gr2HQ2RegInit`), so a model that clears all of it satisfies the shipped drivers: the pixel clock (`Gr2StartClock`), the three Bt457 DACs, the XMAP5 chips (three init passes), the VC1 SRAM images and registers, the HQ2 registers (`numge`, the two timeouts, `fifo_full`, `fifo_empty`, `refresh`), the HQ2 and GE7 microstores and the shared-RAM constants (downloaded again; the PROM loads its built-in console images, the kernel the built-in image then the full images through an ioctl), the unstall and GE program counter writes, the INT2 retrace latch, and the FIFO count and flags. After the reset the kernel does not write status flags or `intr`, so it assumes they are cleared. Established [binary] for what is re-written; "reset clears it" is **inferred** for each item, because no program checks. What survives a reset is unknown: none of the shipped code relies on any board register keeping its value.

## 7. Token catalogue gaps

### Modifier bits

The FIFO address carries the command in bits 10:2 (the microcode entry) and modifier bits above: established [binary] for the address forms, **inferred** for their roles.

| Address bits | Observed use |
|---|---|
| 16 | set for short and integer operands: `+0x5298c` against `+0x4298c` (vertex), `+0x5e3f8` against `+0x4e3f8` (index) |
| 15:12 | attribute jump index; 0 for console and X driver tokens (`+0x404xx`, `+0x406xx`), 2 for most GL state tokens (`+0x42xxx`), 4 and 6 for three- and two-component vertex floats, 8 for byte colours; the 16-word table at the HQ2 `attr_jump` registers has exactly that many entries |
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

Not checkable: the Library holds no Indigo2 or Indy Express GL library (`IP22GR2*`); the only held library is `IP12GR232` and `IP12GR2` from the IRIX 6.5 base set. Unknown. The Indigo2 board topology is a different configuration anyway (survey).

## 8. Microcode image checksums

Held: the IRIX 6.5 base set only. SHA-256 [binary], from the Library's acquisition manifest and re-computed on the reader's copy:

| Image | Size (bytes) | SHA-256 |
|---|---|---|
| `usr/gfx/ucode/hq2.bin` | 58682 | `0c1fbe18d1b451ee32fb81afa4dd85aa86beeee2c5f7fc8b2e33e79e4375fc94` |
| `usr/gfx/ucode/ge7.bin` | 611432 | `085d9e923476750673146a517df5847636e7165fb8e7cb4723f7eef07b114729` |

The 5.x, 6.2 and other 6.5 media images were not found: the software mirror's extracted trees and the Library cache hold no other `hq2.bin` or `ge7.bin`, and the unextracted distribution archives were not unpacked. Unknown for those releases; whether the images differ between releases is the question in [questions/ge7.md](../../questions/ge7.md) 3.

## 9. Model checklist (Elan first)

1. Window at `0x1f000000`, 4 MiB; probe word; board revision 2 values from section 4; GE slots 0 to 3 for Elan.
2. HQ2 registers per `registers.toml`, status word with live FIFO count and three finish flags; FIFO line on INT2 local 0 bit 0 from count against `fifo_full`; drain the count as tokens are consumed.
3. Console tokens and microcode download windows per [pipeline.md](pipeline.md) and [devices/ge7](../../devices/ge7/README.md); built-in console images load and verify; unstall and GE program counter writes accepted.
4. Finish-flag ports: store sets flag from bit 0; set flags after queued commands retire (kernel monitor change, image read, DMA, context tokens 481 to 484 and 496).
5. DMA: GIO slave at `gedma`, board commands for pixel transfer, completion flag 2 (and flag 1 for the PROM and diagnostic path).
6. Retrace on GIO line 2, INT2 port byte pulse clears; `status` bit 0 of INT2 status byte `0xbfb801d3`.
7. Graphics reset: clear all state above.
