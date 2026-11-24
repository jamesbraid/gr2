/* generated from devices/hq2/registers.toml by defs-gen - do not edit, change
 * the source */
/* defs-gen 3 */
/* input sha256 db608454c7808b9d193bbbb9f5045bbecd35eddd286ca290684ba804a4f80078 */
/* HQ2 command engine: FIFO window, microstore and host registers */
#ifndef HQ2_GEN_H
#define HQ2_GEN_H

#include <stdint.h>


/*
 * Graphics FIFO window, 128 KiB. A store is a command: bits 10:2 of the address
 * select a microcode entry, bits 15:12 and bit 16 select an attribute shape,
 * the value is the first operand. Further operands go to the data port, slot 0
 * or slot 479. [binary] pipeline page; every shipped program. The kernel's
 * pixel-DMA path uses slot 0 as the data port while the full microcode runs, so
 * slot 0 is accepted by it. qtest: a store at a slot raises the FIFO fill level
 * by one word.
 */
/* fifo_window: w32, reset unknown */
#define HQ2_FIFO_WINDOW_OFFSET                       0x40000u /* established */
#define HQ2_FIFO_WINDOW_COUNT                        32768
#define HQ2_FIFO_WINDOW_STRIDE                       4

/*
 * HQ2 microstore, one 32-bit word per address, address = word index from the
 * window base. [binary] Gr2DownloadHQ2 writes each loaded word and reads it
 * back unmasked. The 8192-word size is NetBSD's span [public]; the largest
 * address the shipped image writes is not checked. qtest: a written word reads
 * back.
 */
/* ucode_store: rw32, reset unknown */
#define HQ2_UCODE_STORE_OFFSET                       0x60000u /* established */
#define HQ2_UCODE_STORE_COUNT                        8192
#define HQ2_UCODE_STORE_STRIDE                       4

/*
 * Attribute jump table, 16 words. [binary] The loader writes 16 words from
 * image offset 0xfc and reads them back (Gr2DownloadHQ2); the ide register menu
 * writes entries by number 0 to 15 and reads the table. The table is indexed by
 * bits 15:12 of the FIFO address: inferred from its size and from the GL core's
 * address forms (pipeline page). qtest: each word reads back.
 */
/* attr_jump: rw32, reset unknown */
#define HQ2_ATTR_JUMP_OFFSET                         0x6a000u /* established */
#define HQ2_ATTR_JUMP_COUNT                          16
#define HQ2_ATTR_JUMP_STRIDE                         4

/*
 * Status word. The diagnostic program names it the HQ2 version register and
 * prints the fields below; the kernel and PROMs read it by word load and use
 * the fields marked. The ide field names are those it prints. Bits 2:0 are
 * three finish flags set by microcode and cleared by host stores (finish_flag3
 * by the finish3 register, finish_flag2 by the fin2 register, finish_flag1 by
 * the fin1 register). The fill count and overflow bit are the kernel's FIFO
 * flow control. [binary] qtest: after a store at the fin2 register of 0 bit 1
 * reads 0; the count field equals the number of words queued and not consumed;
 * version reads 0 on every board seen (gfxinfo prints HQ2 rev A, [public]
 * Usenet postings).
 */
/* status: r32, reset unknown */
#define HQ2_STATUS_OFFSET                            0x6a040u /* established */
#define HQ2_STATUS_VERSION_SHIFT                     23 /* established */
#define HQ2_STATUS_VERSION_MASK                      0x1ffu
#define HQ2_STATUS_VERSION_INPLACE (HQ2_STATUS_VERSION_MASK << HQ2_STATUS_VERSION_SHIFT)
#define HQ2_STATUS_GE_PTR_SHIFT                      20 /* established */
#define HQ2_STATUS_GE_PTR_MASK                       0x7u
#define HQ2_STATUS_GE_PTR_INPLACE (HQ2_STATUS_GE_PTR_MASK << HQ2_STATUS_GE_PTR_SHIFT)
#define HQ2_STATUS_GE_CTR_SHIFT                      16 /* established */
#define HQ2_STATUS_GE_CTR_MASK                       0xfu
#define HQ2_STATUS_GE_CTR_INPLACE (HQ2_STATUS_GE_CTR_MASK << HQ2_STATUS_GE_CTR_SHIFT)
#define HQ2_STATUS_ZERO_SHIFT                        14 /* established */
#define HQ2_STATUS_ZERO_MASK                         0x3u
#define HQ2_STATUS_ZERO_INPLACE (HQ2_STATUS_ZERO_MASK << HQ2_STATUS_ZERO_SHIFT)
#define HQ2_STATUS_FIFO_LOWATER_SHIFT                13 /* established */
#define HQ2_STATUS_FIFO_LOWATER_MASK                 0x1u
#define HQ2_STATUS_FIFO_LOWATER_INPLACE (HQ2_STATUS_FIFO_LOWATER_MASK << HQ2_STATUS_FIFO_LOWATER_SHIFT)
#define HQ2_STATUS_FIFO_COUNT_SHIFT                  6 /* established */
#define HQ2_STATUS_FIFO_COUNT_MASK                   0x7fu
#define HQ2_STATUS_FIFO_COUNT_INPLACE (HQ2_STATUS_FIFO_COUNT_MASK << HQ2_STATUS_FIFO_COUNT_SHIFT)
#define HQ2_STATUS_FIFO_OVERFLOW_SHIFT               5 /* established */
#define HQ2_STATUS_FIFO_OVERFLOW_MASK                0x1u
#define HQ2_STATUS_FIFO_OVERFLOW_INPLACE (HQ2_STATUS_FIFO_OVERFLOW_MASK << HQ2_STATUS_FIFO_OVERFLOW_SHIFT)
#define HQ2_STATUS_DMA_SYNC_SRC_SHIFT                3 /* established */
#define HQ2_STATUS_DMA_SYNC_SRC_MASK                 0x3u
#define HQ2_STATUS_DMA_SYNC_SRC_INPLACE (HQ2_STATUS_DMA_SYNC_SRC_MASK << HQ2_STATUS_DMA_SYNC_SRC_SHIFT)
#define HQ2_STATUS_FINISH_FLAG1_SHIFT                2 /* established */
#define HQ2_STATUS_FINISH_FLAG1_MASK                 0x1u
#define HQ2_STATUS_FINISH_FLAG1_INPLACE (HQ2_STATUS_FINISH_FLAG1_MASK << HQ2_STATUS_FINISH_FLAG1_SHIFT)
#define HQ2_STATUS_FINISH_FLAG2_SHIFT                1 /* established */
#define HQ2_STATUS_FINISH_FLAG2_MASK                 0x1u
#define HQ2_STATUS_FINISH_FLAG2_INPLACE (HQ2_STATUS_FINISH_FLAG2_MASK << HQ2_STATUS_FINISH_FLAG2_SHIFT)
#define HQ2_STATUS_FINISH_FLAG3_SHIFT                0 /* established */
#define HQ2_STATUS_FINISH_FLAG3_MASK                 0x1u
#define HQ2_STATUS_FINISH_FLAG3_INPLACE (HQ2_STATUS_FINISH_FLAG3_MASK << HQ2_STATUS_FINISH_FLAG3_SHIFT)

/*
 * Number of geometry engines. [binary] The kernel and PROM write the probed
 * count (bit 4 also set when the count is 8); ide writes it and checks it
 * ('Wrong NUMGE, expected, actual'), so it reads back. NetBSD NUMGE [public].
 * qtest: reads back the written value.
 */
/* numge: rw32, reset unknown */
#define HQ2_NUMGE_OFFSET                             0x6a044u /* established */

/*
 * Finish flag 1 (ide, NetBSD FIN1). A store sets the flag to the stored value;
 * the diagnostic program writes 0 before each DMA test and 1 or 0 from its
 * menu, the 4.0.5G PROM writes 0 before a pixel DMA. Whether bit 2 of the
 * status follows the stored bit 0 is inferred. [binary]
 */
/* fin1: w32, reset unknown */
#define HQ2_FIN1_OFFSET                              0x6a048u /* established */

/*
 * Finish flag 2 (ide, NetBSD FIN2). The kernel writes 0 before every
 * context-switch, microcode-start and DMA command and then polls status bit 1.
 * [binary] Gr2PcxSwap, Gr2Start, Gr2DestroyDDRN, _Gr2CXSaveRestore; triggers.
 */
/* fin2: w32, reset unknown */
#define HQ2_FIN2_OFFSET                              0x6a04cu /* established */

/*
 * DMA sync source select (ide DMA sync source, NetBSD DMASYNC): 0 vertical
 * interrupt, 1 video sync, 2 clear, 3 set. The ide menu warns not to write it
 * through the version register. The kernel writes 2 before every DMA and 0 in
 * early init. Which value releases the MC's sync-gated transfer is inferred.
 * [binary] The MC transfer mode used for board DMA sets the sync bit
 * (devices/mc dma_mode bit 2).
 */
/* dmasync: rw32, reset unknown */
#define HQ2_DMASYNC_OFFSET                           0x6a050u /* established */

/*
 * FIFO full timeout. Written 100 by kernel and both PROMs. Unit and effect
 * unknown. [binary] _Gr2HQ2RegInit.
 */
/* fifo_full_timeout: rw32, reset unknown */
#define HQ2_FIFO_FULL_TIMEOUT_OFFSET                 0x6a054u /* established */

/*
 * FIFO empty timeout. Written 255 by the kernel and 10 by the 4.0.5D PROM. Unit
 * and effect unknown. [binary]
 */
/* fifo_empty_timeout: rw32, reset unknown */
#define HQ2_FIFO_EMPTY_TIMEOUT_OFFSET                0x6a058u /* established */

/*
 * FIFO full threshold. Written 40 at init. The INT2 FIFO line (GIO line 0) is
 * asserted while the fill count is at or above it, inferred from the PROM's
 * wait-until-clear before every token and from the kernel handler raising it to
 * level plus one to deassert the line. [binary] qtest: with the threshold at N
 * the INT2 local-0 bit 0 equals (fifo_count >= N).
 */
/* fifo_full: rw32, reset unknown */
#define HQ2_FIFO_FULL_OFFSET                         0x6a05cu /* established */

/*
 * FIFO empty (low water) threshold. Written 1. Effect unknown; status bit 13 is
 * the likely consumer (inferred). [binary]
 */
/* fifo_empty: rw32, reset unknown */
#define HQ2_FIFO_EMPTY_OFFSET                        0x6a060u /* established */

/*
 * GE7 microcode load word (the fifth word of each record; see devices/ge7).
 * Read back with mask 0x03dfffff. [binary] Gr2DownloadGE7; ide reads and writes
 * it.
 */
/* ge7_load_ucode: rw32, reset unknown */
#define HQ2_GE7_LOAD_UCODE_OFFSET                    0x6a064u /* established */

/*
 * GE DMA port. The MC's graphics DMA engine addresses this location as the GIO
 * slave address of every board DMA (its physical address, 0x1f06a068 on the
 * Indigo, is the transfer's GIO address); the kernel writes 0 to it twice after
 * a DMA timeout. The ide menu reads and writes it. Whether a CPU word store
 * pushes a word into the transfer (the kernel's non-MC fallback may do so) is
 * inferred. [binary] _Gr2CXSaveRestore, Gr2MCPixDma and _Gr2MCDMAtrigger, ide
 * gr2_rdHQ2reg.
 */
/* gedma: rw32, reset unknown */
#define HQ2_GEDMA_OFFSET                             0x6a068u /* established */

/*
 * HQ to GE7 program counter. The diagnostic program says it cannot be read ('hw
 * bug'). The kernel probe nevertheless keeps bits 23:16 of a read as the 'HQ2
 * revision' byte, which is therefore not the revision (see the page). [binary]
 * ide gr2_rdHQ2reg; _Gr2ProbeChipRev.
 */
/* hq_gepc: r32, reset unknown */
#define HQ2_HQ_GEPC_OFFSET                           0x6a06cu /* established */

/*
 * GE microstore address (ide: pc used for loading GE7 microcode, NetBSD GEPC).
 * Written with each record's address by the loaders and with 0 by Gr2TpSetup
 * and the PROM before the unstall. [binary]
 */
/* gepc: w32, reset unknown */
#define HQ2_GEPC_OFFSET                              0x6a070u /* established */

/*
 * Interrupt bit register. The diagnostic program calls it 'Intr bit (cleared by
 * host)' and offers a write. No IRIX or PROM driver code touches it. Which
 * interrupt it raises is unknown. [binary] ide only.
 */
/* intr: rw32, reset unknown */
#define HQ2_INTR_OFFSET                              0x6a074u /* inferred */

/*
 * Unstall HQ and GE (ide), NetBSD UNSTALL. Written 0 after microcode load by
 * Gr2TpSetup and the PROM; the diagnostic program has an 'unstall HQ2/GE7 and
 * set pc to 0' command that writes it. The sense of the value (0 releases) is
 * inferred from the order. [binary]
 */
/* unstall: w32, reset unknown */
#define HQ2_UNSTALL_OFFSET                           0x6a078u /* established */

/*
 * Probe word, always 0xdeadbeef. ide prints it as MYSTERY ADDRESS. [binary]
 * Gr2Probe, PROM probe. qtest: a word read returns 0xdeadbeef before and after
 * the microcode load.
 */
/* probe_word: r32, reset 0xdeadbeef */
#define HQ2_PROBE_WORD_OFFSET                        0x6a07cu /* established */

/*
 * Refresh register. Written 16 by the kernel and both PROMs; the diagnostic
 * program writes it from its menu. Effect unknown. [binary]
 */
/* refresh: rw32, reset unknown */
#define HQ2_REFRESH_OFFSET                           0x6a080u /* established */

/*
 * NetBSD names the fin3_netbsd offset FIN3. No shipped program touches it; the
 * third finish flag is written at the finish3 register in every shipped program
 * (see finish3). [public] Unknown.
 */
/* fin3_netbsd: rw32, reset unknown */
#define HQ2_FIN3_NETBSD_OFFSET                       0x6a100u /* unknown */

/*
 * Finish flag 3 write port (ide Finish Flag 3). The kernel and X server store 0
 * to clear status bit 0 before a command and poll the bit afterwards;
 * Gr2PcxSwap restores the saved bit of the incoming context by storing it here
 * (so a store of 1 sets the flag). [binary] Gr2PcxSwap, Gr2DestroyDDRN,
 * Gr2SetMonitor; expReadImage, expDrawImage. qtest: store 0 clears status bit
 * 0; store 1 sets it.
 */
/* finish3: w32, reset unknown */
#define HQ2_FINISH3_OFFSET                           0x6b000u /* established */

#define HQ2_FIFO_DEPTH_LIMIT                         0x3fu /* inferred */
#define HQ2_FIFO_FULL_INIT                           0x28u /* established */
#define HQ2_FIFO_SPACE_CHECK                         0x23u /* established */
/* established */
#define HQ2_PROBE_WORD                               0xdeadbeefu

#endif /* HQ2_GEN_H */
