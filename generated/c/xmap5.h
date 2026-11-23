/* generated from devices/xmap5/registers.toml by defs-gen - do not edit, change
 * the source */
/* defs-gen 3 */
/* input sha256 16b6070bb233d1af1da4ef209d70365aa464954f82eda820d7ca338b5819fb36 */
/* XMAP5 multimode colour mapper (five per Express board) */
#ifndef XMAP5_GEN_H
#define XMAP5_GEN_H

#include <stdint.h>


/*
 * Miscellaneous register file, written through one port after the address pair
 * is set to 0. Init writes 0, 0, 0, 14, 0 in order, so the port auto-increments
 * over five internal registers (inferred from five writes to one address).
 * Meaning of each is [vendor-derived] only: blackout red, green, blue; a
 * four-bit overlay and popup page value; a cursor index. Reads never occur in
 * shipped code.
 */
/* misc: w8, reset unknown */
#define XMAP5_MISC_OFFSET                            0x0u /* inferred */

/*
 * Mode table port. The target entry is chosen by addrlo (byte address 4 *
 * display ID, addrhi 0) before each write; init writes entry 0 and the retrace
 * and display-mode paths write one entry per call. Whether the address advances
 * by 4 after a write is not shown (the driver sets it before every write). A
 * qtest can discriminate: write 0x82000000 at address 0 through the broadcast
 * window and read nothing back (no read path); write through the broadcast
 * window and check all five chips were updated.
 */
/* mode: w32, reset unknown */
#define XMAP5_MODE_OFFSET                            0x4u /* established */

/*
 * Colour table data port. Entry n is selected by addrhi = (n >> 8) & 0x1f and
 * addrlo = n & 0xff; three byte writes (red, green, blue) store one entry and
 * the address then advances to the next entry (the init clear writes 7936
 * entries from address 256 without resetting the address). [binary] Writes
 * while the status busy bit is set are avoided by the callers. A qtest can
 * discriminate: set address 4096, write three bytes, set address 4096 again,
 * write three more and check entry 4097 was not touched.
 */
/* clut: w8, reset unknown */
#define XMAP5_CLUT_OFFSET                            0x8u /* established */

/*
 * Named CRC by NetBSD. Never accessed by the Indigo driver or PROM. Unknown.
 */
/* crc: rw8, reset unknown */
#define XMAP5_CRC_OFFSET                             0xcu /* unknown */

/*
 * Low address byte for the mode, colour table and misc ports. Readable: the
 * retrace handler reads chip 0's pair and writes it back through the broadcast
 * pair. A write through the broadcast window sets all five chips. [binary]
 */
/* addrlo: rw8, reset unknown */
#define XMAP5_ADDRLO_OFFSET                          0x10u /* established */

/*
 * High address byte (five bits used for the colour table). Same rules as
 * addrlo. [binary]
 */
/* addrhi: rw8, reset unknown */
#define XMAP5_ADDRHI_OFFSET                          0x14u /* established */

/*
 * Named byte count by NetBSD. Never accessed by shipped drivers. Unknown.
 */
/* bytecount: rw8, reset unknown */
#define XMAP5_BYTECOUNT_OFFSET                       0x18u /* unknown */

/*
 * Status of the write FIFO in front of the chip (name from NetBSD [public]).
 * Bit 0 set means busy: callers poll until it clears before mode, colour table
 * and DAC writes (Gr2BlankScreen, Gr2SetGammaRamp, the retrace swap; 10 ms
 * bound in the first). Bit 1 set means room for a burst: _Gr2XMAPInit3 waits up
 * to 10 ms for it to be set before each 256-entry block. An idle FIFO therefore
 * reads bit 1 set and bit 0 clear. [binary] Bit 2 (overflow) is
 * [vendor-derived] only. A qtest can discriminate: read after reset has bit 0
 * clear and bit 1 set; during a burst of colour writes bit 0 may be observed
 * set.
 */
/* fifostatus: r8, reset unknown */
#define XMAP5_FIFOSTATUS_OFFSET                      0x1cu /* established */
#define XMAP5_FIFOSTATUS_OVERFLOW_SHIFT              2 /* unknown */
#define XMAP5_FIFOSTATUS_OVERFLOW_MASK               0x1u
#define XMAP5_FIFOSTATUS_OVERFLOW_INPLACE (XMAP5_FIFOSTATUS_OVERFLOW_MASK << XMAP5_FIFOSTATUS_OVERFLOW_SHIFT)
#define XMAP5_FIFOSTATUS_ROOM_SHIFT                  1 /* established */
#define XMAP5_FIFOSTATUS_ROOM_MASK                   0x1u
#define XMAP5_FIFOSTATUS_ROOM_INPLACE (XMAP5_FIFOSTATUS_ROOM_MASK << XMAP5_FIFOSTATUS_ROOM_SHIFT)
#define XMAP5_FIFOSTATUS_BUSY_SHIFT                  0 /* established */
#define XMAP5_FIFOSTATUS_BUSY_MASK                   0x1u
#define XMAP5_FIFOSTATUS_BUSY_INPLACE (XMAP5_FIFOSTATUS_BUSY_MASK << XMAP5_FIFOSTATUS_BUSY_SHIFT)

/*
 * Mode table word, one per display ID, written through the mode port at byte
 * address 4 * ID. Bit meaning is inferred: [binary] two points tie it to
 * shipped code (the boot word 0x82000000 selects page 16 which is where the
 * text port's colours live; the shipped X server builds words as page << 27 |
 * 0x800 | base, forces 0xf00000 when bit 8 is clear, and toggles bit 24 for the
 * second buffer, read from an upstream decompilation not re-checked here); the
 * remaining fields rest on [vendor-derived] notes.
 */
/* word MODE_WORD: 32 bits */
#define XMAP5_MODE_WORD_WIDTH                        32 /* inferred */
#define XMAP5_MODE_WORD_PIX_PAGE_SHIFT               27 /* inferred */
#define XMAP5_MODE_WORD_PIX_PAGE_MASK                0x1fu
#define XMAP5_MODE_WORD_PIX_PAGE_INPLACE (XMAP5_MODE_WORD_PIX_PAGE_MASK << XMAP5_MODE_WORD_PIX_PAGE_SHIFT)
#define XMAP5_MODE_WORD_PIX_MODE_SHIFT               24 /* inferred */
#define XMAP5_MODE_WORD_PIX_MODE_MASK                0x7u
#define XMAP5_MODE_WORD_PIX_MODE_INPLACE (XMAP5_MODE_WORD_PIX_MODE_MASK << XMAP5_MODE_WORD_PIX_MODE_SHIFT)
#define XMAP5_MODE_WORD_OVERLAY_ENABLE_SHIFT         20 /* inferred */
#define XMAP5_MODE_WORD_OVERLAY_ENABLE_MASK          0xfu
#define XMAP5_MODE_WORD_OVERLAY_ENABLE_INPLACE (XMAP5_MODE_WORD_OVERLAY_ENABLE_MASK << XMAP5_MODE_WORD_OVERLAY_ENABLE_SHIFT)
#define XMAP5_MODE_WORD_ALT_VIDEO_SHIFT              18 /* unknown */
#define XMAP5_MODE_WORD_ALT_VIDEO_MASK               0x3u
#define XMAP5_MODE_WORD_ALT_VIDEO_INPLACE (XMAP5_MODE_WORD_ALT_VIDEO_MASK << XMAP5_MODE_WORD_ALT_VIDEO_SHIFT)
#define XMAP5_MODE_WORD_PD_MODE_SHIFT                16 /* inferred */
#define XMAP5_MODE_WORD_PD_MODE_MASK                 0x3u
#define XMAP5_MODE_WORD_PD_MODE_INPLACE (XMAP5_MODE_WORD_PD_MODE_MASK << XMAP5_MODE_WORD_PD_MODE_SHIFT)
#define XMAP5_MODE_WORD_POPUP_FLAGS_SHIFT            14 /* unknown */
#define XMAP5_MODE_WORD_POPUP_FLAGS_MASK             0x3u
#define XMAP5_MODE_WORD_POPUP_FLAGS_INPLACE (XMAP5_MODE_WORD_POPUP_FLAGS_MASK << XMAP5_MODE_WORD_POPUP_FLAGS_SHIFT)
#define XMAP5_MODE_WORD_AUX_PAGE_SHIFT               9 /* inferred */
#define XMAP5_MODE_WORD_AUX_PAGE_MASK                0x1fu
#define XMAP5_MODE_WORD_AUX_PAGE_INPLACE (XMAP5_MODE_WORD_AUX_PAGE_MASK << XMAP5_MODE_WORD_AUX_PAGE_SHIFT)
#define XMAP5_MODE_WORD_UNDERLAY_ENABLE_SHIFT        8 /* inferred */
#define XMAP5_MODE_WORD_UNDERLAY_ENABLE_MASK         0x1u
#define XMAP5_MODE_WORD_UNDERLAY_ENABLE_INPLACE (XMAP5_MODE_WORD_UNDERLAY_ENABLE_MASK << XMAP5_MODE_WORD_UNDERLAY_ENABLE_SHIFT)
#define XMAP5_MODE_WORD_POPUP_MODE_SHIFT             0 /* unknown */
#define XMAP5_MODE_WORD_POPUP_MODE_MASK              0xffu
#define XMAP5_MODE_WORD_POPUP_MODE_INPLACE (XMAP5_MODE_WORD_POPUP_MODE_MASK << XMAP5_MODE_WORD_POPUP_MODE_SHIFT)

/* established */
#define XMAP5_BOOT_MODE_WORD_DID0                    0x82000000u
#define XMAP5_CHIP_COUNT                             0x5u /* established */
#define XMAP5_CLUT_ENTRIES                           0x2000u /* established */
#define XMAP5_MODE_ENTRIES                           0x20u /* established */
#define XMAP5_TEXTPORT_CLUT_BASE                     0x1000u /* established */
#define XMAP5_WINDOW_SIZE                            0x20u /* inferred */

#endif /* XMAP5_GEN_H */
