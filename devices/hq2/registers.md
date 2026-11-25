<!-- generated from devices/hq2/registers.toml by defs-gen - do not edit, change the source -->
<!-- defs-gen 3 -->
<!-- input sha256 cba5637da661ab8b8f3e475b328cfed1722aba88cfb3d1a80e1228cd43c13f30 -->

# HQ2 command engine: FIFO window, microstore and host registers

Host-visible window of the HQ2 command engine in the Express graphics slot (physical 0x1f000000 on the Indigo): the FIFO window, the microstore load window and the register page with the finish-flag clear at the finish3 register. Provenance tags in item text: [public] published document or public driver, [binary] shipped IRIX, PROM or diagnostic-program binary (a software expectation, with the routine named), [vendor-derived] upstream headers (none supports any fact here). Register names marked ide are the names the shipped diagnostic program prints; names marked NetBSD are the public driver's. Grades: established means read in full in a shipped binary or stated by a published document; inferred means a reasoned reading; unknown means nothing shipped settles it. Nothing was read on a board and no reset value is stated by any source, so none is given except where noted. Prose in devices/hq2/README.md.

Unit `hq2`, macro prefix `HQ2`.

Every item has a grade: established, inferred or unknown. A grade says how the item was derived from its source; it does not claim the item was measured on silicon.

## Registers

| Register | Offset | Access | Width | Count | Space | Reset | Grade | Source |
|---|---|---|---|---|---|---|---|---|
| `fifo_window` | 0x40000 | w | 32 | 32768 |  | unknown | established |  |
| `ucode_store` | 0x60000 | rw | 32 | 8192 |  | unknown | established |  |
| `attr_jump` | 0x6a000 | rw | 32 | 16 |  | unknown | established |  |
| `status` | 0x6a040 | r | 32 |  |  | unknown | established |  |
| `numge` | 0x6a044 | rw | 32 |  |  | unknown | established |  |
| `fin1` | 0x6a048 | w | 32 |  |  | unknown | established |  |
| `fin2` | 0x6a04c | w | 32 |  |  | unknown | established |  |
| `dmasync` | 0x6a050 | rw | 32 |  |  | unknown | established |  |
| `fifo_full_timeout` | 0x6a054 | rw | 32 |  |  | unknown | established |  |
| `fifo_empty_timeout` | 0x6a058 | rw | 32 |  |  | unknown | established |  |
| `fifo_full` | 0x6a05c | rw | 32 |  |  | unknown | established |  |
| `fifo_empty` | 0x6a060 | rw | 32 |  |  | unknown | established |  |
| `ge7_load_ucode` | 0x6a064 | rw | 32 |  |  | unknown | established |  |
| `gedma` | 0x6a068 | rw | 32 |  |  | unknown | established |  |
| `hq_gepc` | 0x6a06c | r | 32 |  |  | unknown | inferred |  |
| `gepc` | 0x6a070 | w | 32 |  |  | unknown | established |  |
| `intr` | 0x6a074 | rw | 32 |  |  | unknown | inferred |  |
| `unstall` | 0x6a078 | w | 32 |  |  | unknown | established |  |
| `probe_word` | 0x6a07c | r | 32 |  |  | 0xdeadbeef (inferred) | established |  |
| `refresh` | 0x6a080 | rw | 32 |  |  | unknown | established |  |
| `fin3_netbsd` | 0x6a100 | rw | 32 |  |  | unknown | unknown |  |
| `finish3` | 0x6b000 | w | 32 |  |  | unknown | established |  |

### Register `fifo_window`

Graphics FIFO window, 128 KiB. A store is a command: bits 10:2 of the address select a microcode entry, bits 15:12 and bit 16 select an attribute shape, the value is the first operand. Further operands go to the data port, slot 0 or slot 479. [binary] pipeline page; every shipped program. The kernel's pixel-DMA path uses slot 0 as the data port while the full microcode runs, so slot 0 is accepted by it. qtest: a store at a slot raises the FIFO fill level by one word.

Array of 32768 registers, stride 4.

### Register `ucode_store`

HQ2 microstore, one 32-bit word per address, address = word index from the window base. [binary] Gr2DownloadHQ2 writes each loaded word and reads it back unmasked. The 8192-word size is NetBSD's span [public]; the largest address the shipped image writes is not checked. qtest: a written word reads back.

Array of 8192 registers, stride 4.

### Register `attr_jump`

Attribute jump table, 16 words. [binary] The loader writes 16 words from image offset 0xfc and reads them back (Gr2DownloadHQ2); the ide register menu writes entries by number 0 to 15 and reads the table. The table is indexed by bits 15:12 of the FIFO address: inferred from its size and from the GL core's address forms (pipeline page). qtest: each word reads back.

Array of 16 registers, stride 4.

### Register `status`

Status word. The diagnostic program names it the HQ2 version register and prints the fields below; the kernel and PROMs read it by word load and use the fields marked. The ide field names are those it prints. Bits 2:0 are three finish flags set by microcode and cleared by host stores (finish_flag3 by the finish3 register, finish_flag2 by the fin2 register, finish_flag1 by the fin1 register). The fill count and overflow bit are the kernel's FIFO flow control. [binary] qtest: after a store at the fin2 register of 0 bit 1 reads 0; the count field equals the number of words queued and not consumed; version is 0 on every board seen only if the PROM byte matches what gfxinfo prints (HQ2 rev A, [public] Usenet postings; see the version field).

| Bits | Field | Grade | Values | Source | Description |
|---|---|---|---|---|---|
| 31:23 | `version` | established |  |  | ide HQ2 version. Both PROMs store (word >> 23) through a byte store, so the byte holds bits 30:23. NetBSD masks 0xff000000 and then shifts by 23, a doubled value of bits 31:24 that leaves bit 23 out; the two agree only while the field is 0. The kernel fills the same probe-record byte from bits 23:16 of hq_gepc instead, and gfxinfo prints that byte: 0 is 'HQ2 rev A', 1 is 'HQ2.1 rev A' (gfxinit decode, read in full), so the kernel's register is the one users see; which of the two the hardware calls the revision is unsettled. Every captured Indigo reads 0. [binary][public] |
| 22:20 | `ge_ptr` | established |  |  | ide ge_ptr. Role unknown; three bits, wide enough to count eight engines. [binary] |
| 19:16 | `ge_ctr` | established |  |  | ide ge_ctr. Role unknown; four bits. [binary] |
| 15:14 | `zero` | established |  |  | ide zero. Printed as a field that reads zero. [binary] |
| 13 | `fifo_lowater` | established |  |  | ide FIFO low water. Never read by IRIX. Its condition (against FIFO_EMPTY or FIFO_FULL) is unknown. [binary] |
| 12:6 | `fifo_count` | established |  |  | ide FIFO count. Words in the FIFO. The kernel compares it with 35, 36, 40, 41 and 63. [binary] |
| 5 | `fifo_overflow` | established |  |  | ide FIFO overflow. The kernel interrupt handler prints 'FIFO overflowed, data is destroyed - Reset graphics' when set, then calls gr2_error, which logs the low 16 bits of the hq_gepc register as the GE PC, flags the board, kills the graphics clients and resets the board (Gr2Reset, Gr2StartClock). No shipped code writes a clear for it, so the graphics reset is the inferred clear. [binary] Gr2FIFOHandler 0x2a0, gr2_error 0x0. |
| 4:3 | `dma_sync_src` | established |  |  | ide dma_sync source: 0 vertical interrupt, 1 video sync, 2 clear, 3 set. A read-back of the DMASYNC register; the kernel stores 2 before every DMA and 0 at early init. [binary] |
| 2 | `finish_flag1` | established |  |  | ide finflag1. The diagnostic program's DMA-done flag (it prints hq_version_reg when it times out) and the 4.0.5G PROM's pixel-DMA completion flag; cleared by a store of 0 to the fin1 register. [binary] |
| 1 | `finish_flag2` | established |  |  | ide finflag2. The kernel's microcode-ready and DMA-done flag: _Gr2UcodeReady and both DMA triggers poll it; cleared by a store of 0 to the fin2 register. [binary] |
| 0 | `finish_flag3` | established |  |  | ide finflag3. Set by microcode on a finish command; read by Gr2SetMonitor, Gr2PcxSwap, Gr2DestroyDDRN and the X server image paths; cleared (or restored) by a store to the finish3 register. [binary] |

### Register `numge`

Number of geometry engines. [binary] The kernel and PROM write the probed count (bit 4 also set when the count is 8); ide writes it and checks it ('Wrong NUMGE, expected, actual'), so it reads back. NetBSD NUMGE [public]. qtest: reads back the written value.

### Register `fin1`

Finish flag 1 (ide, NetBSD FIN1). A store sets the flag to the stored value; the diagnostic program writes 0 before each DMA test and 1 or 0 from its menu, the 4.0.5G PROM writes 0 before a pixel DMA. Whether bit 2 of the status follows the stored bit 0 is inferred. [binary]

### Register `fin2`

Finish flag 2 (ide, NetBSD FIN2). The kernel writes 0 before every context-switch, microcode-start and DMA command and then polls status bit 1. [binary] Gr2PcxSwap, Gr2Start, Gr2DestroyDDRN, _Gr2CXSaveRestore; triggers.

### Register `dmasync`

DMA sync source select (ide DMA sync source, NetBSD DMASYNC): 0 vertical interrupt, 1 video sync, 2 clear, 3 set. The ide menu warns not to write it through the version register. The kernel writes 2 before every DMA and 0 in early init. Which value releases the MC's sync-gated transfer is inferred. [binary] The MC transfer mode used for board DMA sets the sync bit (devices/mc dma_mode bit 2).

### Register `fifo_full_timeout`

FIFO full timeout. Written 100 by kernel and both PROMs. Unit and effect unknown. [binary] _Gr2HQ2RegInit.

### Register `fifo_empty_timeout`

FIFO empty timeout. Written 255 by the kernel and 10 by the 4.0.5D PROM. Unit and effect unknown. [binary]

### Register `fifo_full`

FIFO full threshold. Written 40 at init. The INT2 FIFO line (GIO line 0) is asserted while the fill count is at or above it, inferred from the PROM's wait-until-clear before every token, from the kernel handler raising it to level plus one to deassert the line, and from the handler's own test, which treats count less than the saved threshold as drained (software expectation of >=; no read settles the hardware compare). Written 40 by Gr2FIFOPollLowater when it sees the count below 35; the handler writes max(40, min(count + 1, 63)). [binary] qtest: with the threshold at N the INT2 local-0 bit 0 equals (fifo_count >= N).

### Register `fifo_empty`

FIFO empty (low water) threshold. Written 1. Effect unknown; status bit 13 is the likely consumer (inferred). [binary]

### Register `ge7_load_ucode`

GE7 microcode load word (the fifth word of each record; see devices/ge7). Read back with mask 0x03dfffff. [binary] Gr2DownloadGE7; ide reads and writes it.

### Register `gedma`

GE DMA port. The MC's graphics DMA engine addresses this location as the GIO slave address of every board DMA (its physical address, 0x1f06a068 on the Indigo, is the transfer's GIO address); the kernel writes 0 to it twice after a DMA timeout. The ide menu reads and writes it. Whether a CPU word store pushes a word into the transfer (the kernel's non-MC fallback may do so) is inferred. [binary] _Gr2CXSaveRestore, Gr2MCPixDma and _Gr2MCDMAtrigger, ide gr2_rdHQ2reg.

### Register `hq_gepc`

HQ to GE7 program counter. The diagnostic program reads it and prints 'Currently, can't read - hw bug - HQ_GE7 PC'. The kernel reads it twice: gr2_error logs the low 16 bits as 'GE PC', and _Gr2ProbeChipRev stores bits 23:16 in the probe-record byte the PROMs fill from status bits 31:23. gfxinfo prints that byte as 'HQ2 rev A' for 0 and 'HQ2.1 rev A' for 1, so those bits are what users see as the revision (established as the decode; the hardware's own name for the field is unknown). [binary] ide gr2_rdHQ2reg; gr2_error; _Gr2ProbeChipRev. qtest: a read does not fault; model value 0 satisfies every shipped reader.

### Register `gepc`

GE microstore address (ide: pc used for loading GE7 microcode, NetBSD GEPC). Written with each record's address by the loaders and with 0 by Gr2TpSetup and the PROM before the unstall. [binary]

### Register `intr`

Interrupt bit register. The diagnostic program calls it 'Intr bit (cleared by host)' and offers a write. No IRIX or PROM driver code touches it. Which interrupt it raises is unknown. [binary] ide only.

### Register `unstall`

Unstall HQ and GE (ide), NetBSD UNSTALL. Written 0 after microcode load by Gr2TpSetup and the PROM; the diagnostic program has an 'unstall HQ2/GE7 and set pc to 0' command that writes it. The sense of the value (0 releases) is inferred from the order. [binary]

### Register `probe_word`

Probe word, always 0xdeadbeef. ide prints it as MYSTERY ADDRESS. [binary] Gr2Probe, PROM probe. qtest: a word read returns 0xdeadbeef before and after the microcode load.

### Register `refresh`

Refresh register. Written 16 by the kernel and both PROMs; the diagnostic program writes it from its menu. Effect unknown. [binary]

### Register `fin3_netbsd`

NetBSD names the fin3_netbsd offset FIN3. No shipped program touches it; the third finish flag is written at the finish3 register in every shipped program (see finish3). [public] Unknown.

### Register `finish3`

Finish flag 3 write port (ide Finish Flag 3). The kernel and X server store 0 to clear status bit 0 before a command and poll the bit afterwards; Gr2PcxSwap restores the saved bit of the incoming context by storing it here (so a store of 1 sets the flag). [binary] Gr2PcxSwap, Gr2DestroyDDRN, Gr2SetMonitor; expReadImage, expDrawImage. qtest: store 0 clears status bit 0; store 1 sets it.

## Constants

| Constant | Value | Grade | Source | Description |
|---|---|---|---|---|
| `FIFO_DEPTH_LIMIT` | 0x3f | inferred |  | Largest fill level the kernel ever programs into the FIFO_FULL threshold (it clamps level plus one to 63). [binary] Gr2FIFOHandler. The status count field is seven bits wide, so the real depth is not shown by this. |
| `FIFO_FULL_INIT` | 0x28 | established |  | Value both PROMs and the kernel write to FIFO_FULL at initialisation; the kernel writes it again when it waits for the FIFO to drain. [binary] _Gr2HQ2RegInit, Gr2FIFOPollLowater. |
| `FIFO_SPACE_CHECK` | 0x23 | established |  | Fill level below which the kernel treats the FIFO as having room (Gr2FIFOPollLowater answers yes and re-arms FIFO_FULL only below 35, and no at 35 or more). [binary] Gr2FIFOPollLowater. |
| `PROBE_WORD` | 0xdeadbeef | established |  | Value every probe expects at the probe_word register. [binary] Gr2Probe, PROM probe. |
