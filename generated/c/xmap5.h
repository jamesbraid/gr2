/* generated from devices/xmap5/registers.toml by defs-gen - do not edit, change
 * the source */
/* SPDX-License-Identifier: BSD-3-Clause */
/* defs-gen 5 */
/* input sha256 6396c45c31f5677aa6472288571ce1b4f20590c64e4f4e0ac42d11174353cf35 */
/* XMAP5 multimode colour mapper (five per Express board) */
#ifndef XMAP5_GEN_H
#define XMAP5_GEN_H

#include <stdint.h>


/*
 * Miscellaneous register file, written through one port after the address pair
 * is set; the diagnostic sizes it at six bytes. Init writes 0, 0, 0, 14, 0
 * after address 0, so the port auto-increments (inferred from five writes to
 * one address). [source] The diagnostic program's XMAP5 test and its header
 * name the first three bytes the blackout red, green and blue, the byte at
 * address 3 a popup page value and the byte at address 4 a cursor value (its
 * colour test sets address 3 and writes those two in turn); the sixth byte is
 * unnamed. The init writes 14 at address 3 and 0 at address 4, while the
 * diagnostic uses 0 and 15. Reads never occur in shipped code.
 */
/* misc: w8, reset unknown */
#define XMAP5_MISC_OFFSET                            0x0u /* inferred */

/*
 * Mode table port. The target entry is chosen by addrlo (byte address 4 *
 * display ID, addrhi 0) before each write; init writes entry 0 and the retrace
 * and display-mode paths write one entry per call. The diagnostic program's
 * mode-table test assumes a write advances the address by 4 (its own comment
 * says to assume it); no shipped driver depends on it, since the driver sets
 * the address before every write, so the advance is a software expectation and
 * not shown by any shipped code. A qtest can discriminate: write 0x82000000 at
 * address 0 through the broadcast window and read nothing back (no read path);
 * write through the broadcast window and check all five chips were updated.
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
 * address 4 * ID. Field boundaries are [source] the IRIX diagnostic program's
 * XMAP5 test, which composes words from named fields (pixel mode, pixel page,
 * data format, alternate video, overlay and underlay enables, auxiliary page,
 * popup page, popup mode); they are cross-checked in [binary] by the boot word
 * 0x82000000 (page 16, eight-bit bank 0, colour index: the text port's colours
 * live at CLUT index 4096) and by the shipped X server, which builds words as
 * page << 27 | 0x800 | base, forces 0xf00000 when bit 8 is clear and sets or
 * clears bit 24 for the second buffer (disassembly of expValidateMode). The
 * role of each field is read from its name and how the diagnostic pairs values,
 * so the roles are inferred where a field says so.
 */
/* word MODE_WORD: 32 bits */
#define XMAP5_MODE_WORD_WIDTH                        32 /* established */
#define XMAP5_MODE_WORD_PIX_PAGE_SHIFT               27 /* established */
#define XMAP5_MODE_WORD_PIX_PAGE_MASK                0x1fu
#define XMAP5_MODE_WORD_PIX_PAGE_INPLACE (XMAP5_MODE_WORD_PIX_PAGE_MASK << XMAP5_MODE_WORD_PIX_PAGE_SHIFT)
#define XMAP5_MODE_WORD_PIX_MODE_SHIFT               24 /* established */
#define XMAP5_MODE_WORD_PIX_MODE_MASK                0x7u
#define XMAP5_MODE_WORD_PIX_MODE_INPLACE (XMAP5_MODE_WORD_PIX_MODE_MASK << XMAP5_MODE_WORD_PIX_MODE_SHIFT)
#define XMAP5_MODE_WORD_OVERLAY_ENABLE_SHIFT         20 /* established */
#define XMAP5_MODE_WORD_OVERLAY_ENABLE_MASK          0xfu
#define XMAP5_MODE_WORD_OVERLAY_ENABLE_INPLACE (XMAP5_MODE_WORD_OVERLAY_ENABLE_MASK << XMAP5_MODE_WORD_OVERLAY_ENABLE_SHIFT)
#define XMAP5_MODE_WORD_ALT_VIDEO_SHIFT              18 /* established */
#define XMAP5_MODE_WORD_ALT_VIDEO_MASK               0x3u
#define XMAP5_MODE_WORD_ALT_VIDEO_INPLACE (XMAP5_MODE_WORD_ALT_VIDEO_MASK << XMAP5_MODE_WORD_ALT_VIDEO_SHIFT)
#define XMAP5_MODE_WORD_PD_MODE_SHIFT                16 /* established */
#define XMAP5_MODE_WORD_PD_MODE_MASK                 0x3u
#define XMAP5_MODE_WORD_PD_MODE_INPLACE (XMAP5_MODE_WORD_PD_MODE_MASK << XMAP5_MODE_WORD_PD_MODE_SHIFT)
#define XMAP5_MODE_WORD_POPUP_FLAGS_SHIFT            14 /* inferred */
#define XMAP5_MODE_WORD_POPUP_FLAGS_MASK             0x3u
#define XMAP5_MODE_WORD_POPUP_FLAGS_INPLACE (XMAP5_MODE_WORD_POPUP_FLAGS_MASK << XMAP5_MODE_WORD_POPUP_FLAGS_SHIFT)
#define XMAP5_MODE_WORD_AUX_PAGE_SHIFT               9 /* established */
#define XMAP5_MODE_WORD_AUX_PAGE_MASK                0x1fu
#define XMAP5_MODE_WORD_AUX_PAGE_INPLACE (XMAP5_MODE_WORD_AUX_PAGE_MASK << XMAP5_MODE_WORD_AUX_PAGE_SHIFT)
#define XMAP5_MODE_WORD_UNDERLAY_ENABLE_SHIFT        8 /* established */
#define XMAP5_MODE_WORD_UNDERLAY_ENABLE_MASK         0x1u
#define XMAP5_MODE_WORD_UNDERLAY_ENABLE_INPLACE (XMAP5_MODE_WORD_UNDERLAY_ENABLE_MASK << XMAP5_MODE_WORD_UNDERLAY_ENABLE_SHIFT)
#define XMAP5_MODE_WORD_POPUP_MODE_SHIFT             0 /* inferred */
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
