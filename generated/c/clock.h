/* generated from devices/clock/registers.toml by defs-gen - do not edit, change
 * the source */
/* defs-gen 4 */
/* input sha256 467273ff471ddf2134ff68f52c6be88c8ce534408f7b0b63cc8677a1cd2e2738 */
/* Express board configuration ports and pixel clock control */
#ifndef GR2_CLK_GEN_H
#define GR2_CLK_GEN_H

#include <stdint.h>


/*
 * Read: board revision and, on revision 4 and up, the monitor code. Bits 3:0
 * read back inverted (board revision is the complement, zero means no board).
 * On revision 4 and up bits 7:4, not inverted, are the monitor code. Write:
 * pixel clock select, see the SEL constants. The read and write sides are
 * different functions at one address. [binary] A qtest can discriminate: a byte
 * read returns the board revision complemented in bits 3:0; a word read has the
 * byte in the most significant lane (NetBSD masks the low bits instead, see
 * questions/display.md).
 */
/* port0: rw8, reset unknown */
#define GR2_CLK_PORT0_OFFSET                         0x6c000u /* established */
#define GR2_CLK_PORT0_MONITOR_CODE_REV4_SHIFT        4 /* established */
#define GR2_CLK_PORT0_MONITOR_CODE_REV4_MASK         0xfu
#define GR2_CLK_PORT0_MONITOR_CODE_REV4_INPLACE (GR2_CLK_PORT0_MONITOR_CODE_REV4_MASK << GR2_CLK_PORT0_MONITOR_CODE_REV4_SHIFT)
#define GR2_CLK_PORT0_BOARD_REV_N_SHIFT              0 /* established */
#define GR2_CLK_PORT0_BOARD_REV_N_MASK               0xfu
#define GR2_CLK_PORT0_BOARD_REV_N_INPLACE (GR2_CLK_PORT0_BOARD_REV_N_MASK << GR2_CLK_PORT0_BOARD_REV_N_SHIFT)

/*
 * Read below revision 4: bit 0 is monitor code bit 0; bits 3:2 both set mean no
 * Z buffer. Read at revision 4 and up: bits 1:0 backend revision as read (both
 * set fails the probe), bit 4 set means 24-bit colour (clear means 8), bit 5
 * set means Z buffer present. Write: pixel clock load control: 0 then 0x40
 * (0x41 interlaced) below revision 4; 0 then 1 (5 interlaced) at revision 4 and
 * up. The roles of the written bits are inferred. [binary]
 */
/* port1: rw8, reset unknown */
#define GR2_CLK_PORT1_OFFSET                         0x6c004u /* established */
#define GR2_CLK_PORT1_Z_PRESENT_REV4_SHIFT           5 /* established */
#define GR2_CLK_PORT1_Z_PRESENT_REV4_MASK            0x1u
#define GR2_CLK_PORT1_Z_PRESENT_REV4_INPLACE (GR2_CLK_PORT1_Z_PRESENT_REV4_MASK << GR2_CLK_PORT1_Z_PRESENT_REV4_SHIFT)
#define GR2_CLK_PORT1_DEPTH24_REV4_SHIFT             4 /* established */
#define GR2_CLK_PORT1_DEPTH24_REV4_MASK              0x1u
#define GR2_CLK_PORT1_DEPTH24_REV4_INPLACE (GR2_CLK_PORT1_DEPTH24_REV4_MASK << GR2_CLK_PORT1_DEPTH24_REV4_SHIFT)
#define GR2_CLK_PORT1_NO_Z_REV3_SHIFT                2 /* established */
#define GR2_CLK_PORT1_NO_Z_REV3_MASK                 0x3u
#define GR2_CLK_PORT1_NO_Z_REV3_INPLACE (GR2_CLK_PORT1_NO_Z_REV3_MASK << GR2_CLK_PORT1_NO_Z_REV3_SHIFT)
#define GR2_CLK_PORT1_LOW2_SHIFT                     0 /* established */
#define GR2_CLK_PORT1_LOW2_MASK                      0x3u
#define GR2_CLK_PORT1_LOW2_INPLACE (GR2_CLK_PORT1_LOW2_MASK << GR2_CLK_PORT1_LOW2_SHIFT)

/*
 * Board revision below 4 only. Bits 3:2 read back inverted as the backend
 * revision (zero fails the probe); bits 1:0 are monitor code bits 2:1. Not read
 * at revision 4 and up. [binary]
 */
/* port2: r8, reset unknown */
#define GR2_CLK_PORT2_OFFSET                         0x6c008u /* established */
#define GR2_CLK_PORT2_BACKEND_REV_N_SHIFT            2 /* established */
#define GR2_CLK_PORT2_BACKEND_REV_N_MASK             0x3u
#define GR2_CLK_PORT2_BACKEND_REV_N_INPLACE (GR2_CLK_PORT2_BACKEND_REV_N_MASK << GR2_CLK_PORT2_BACKEND_REV_N_SHIFT)
#define GR2_CLK_PORT2_MONITOR_CODE_HI_SHIFT          0 /* established */
#define GR2_CLK_PORT2_MONITOR_CODE_HI_MASK           0x3u
#define GR2_CLK_PORT2_MONITOR_CODE_HI_INPLACE (GR2_CLK_PORT2_MONITOR_CODE_HI_MASK << GR2_CLK_PORT2_MONITOR_CODE_HI_SHIFT)

/*
 * Board revision below 4 only: frame-buffer memory slot presence; a slot is
 * empty when both of its bits are set (slot A bits 1:0, slot B bits 3:2, slot C
 * bits 5:4). Colour depth is 24 with all three populated, 16 with A and B only,
 * otherwise 8. [binary] NetBSD multiplies the populated count by 8 instead
 * [public].
 */
/* port3: r8, reset unknown */
#define GR2_CLK_PORT3_OFFSET                         0x6c00cu /* established */
#define GR2_CLK_PORT3_SLOT_C_EMPTY_SHIFT             4 /* established */
#define GR2_CLK_PORT3_SLOT_C_EMPTY_MASK              0x3u
#define GR2_CLK_PORT3_SLOT_C_EMPTY_INPLACE (GR2_CLK_PORT3_SLOT_C_EMPTY_MASK << GR2_CLK_PORT3_SLOT_C_EMPTY_SHIFT)
#define GR2_CLK_PORT3_SLOT_B_EMPTY_SHIFT             2 /* established */
#define GR2_CLK_PORT3_SLOT_B_EMPTY_MASK              0x3u
#define GR2_CLK_PORT3_SLOT_B_EMPTY_INPLACE (GR2_CLK_PORT3_SLOT_B_EMPTY_MASK << GR2_CLK_PORT3_SLOT_B_EMPTY_SHIFT)
#define GR2_CLK_PORT3_SLOT_A_EMPTY_SHIFT             0 /* established */
#define GR2_CLK_PORT3_SLOT_A_EMPTY_MASK              0x3u
#define GR2_CLK_PORT3_SLOT_A_EMPTY_INPLACE (GR2_CLK_PORT3_SLOT_A_EMPTY_MASK << GR2_CLK_PORT3_SLOT_A_EMPTY_SHIFT)

/*
 * Pixel clock serial or command port. Board revision below 4: 17 command bytes.
 * Revision 4 and up: 56 single-bit writes (bit 0 is the data bit, bit 1 set on
 * the last). The chip is not identified. [binary] A qtest can discriminate:
 * count the writes between a port1 write of 0 and the next port1 write (17 or
 * 56).
 */
/* data: w8, reset unknown */
#define GR2_CLK_DATA_OFFSET                          0x6c020u /* established */
#define GR2_CLK_DATA_LAST_SHIFT                      1 /* established */
#define GR2_CLK_DATA_LAST_MASK                       0x1u
#define GR2_CLK_DATA_LAST_INPLACE (GR2_CLK_DATA_LAST_MASK << GR2_CLK_DATA_LAST_SHIFT)
#define GR2_CLK_DATA_BIT_SHIFT                       0 /* established */
#define GR2_CLK_DATA_BIT_MASK                        0x1u
#define GR2_CLK_DATA_BIT_INPLACE (GR2_CLK_DATA_BIT_MASK << GR2_CLK_DATA_BIT_SHIFT)

#define GR2_CLK_BOARD_REV_SPLIT                      0x4u /* established */
#define GR2_CLK_COMMAND_BYTES_REV3                   0x11u /* established */
#define GR2_CLK_EXTRA_BYTE_REV3                      0xa5u /* established */
#define GR2_CLK_LOAD_REV3                            0x40u /* inferred */
#define GR2_CLK_SEL_60HZ                             0x1u /* inferred */
#define GR2_CLK_SEL_72HZ                             0x2u /* inferred */
#define GR2_CLK_SEL_OTHER                            0x4u /* inferred */
#define GR2_CLK_SEL_REV4                             0x7u /* established */
#define GR2_CLK_SERIAL_BYTES_REV4                    0x7u /* established */

#endif /* GR2_CLK_GEN_H */
