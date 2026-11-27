/* generated from devices/bt457/registers.toml by defs-gen - do not edit, change
 * the source */
/* defs-gen 4 */
/* input sha256 e70d1735c70ebfb40a10bdbfae82173a37248264f8277909d1c208d56f73f0dc */
/* Brooktree Bt457 RAMDAC as wired on the Express board (three chips, one per
 * colour) */
#ifndef BT457_GEN_H
#define BT457_GEN_H

#include <stdint.h>


/*
 * Address register. Written before every register or palette access; after a
 * palette or overlay access it advances (palette wraps to 0 after 255, overlay
 * goes to 4 after overlay 3, control registers do not advance it). [public]
 * [binary] A qtest can discriminate: write 255 to addr, write two bytes to
 * palette, check the address wrapped to 0 then 1.
 */
/* addr: rw8, reset unknown */
#define BT457_ADDR_OFFSET                            0x0u /* established */

/*
 * Colour palette RAM data. The three chips are addressed separately, so the
 * board uses the datasheet's normal mode: one byte write stores one colour
 * component of the addressed entry and the address advances. [public] [binary]
 */
/* palette: rw8, reset unknown */
#define BT457_PALETTE_OFFSET                         0x4u /* established */

/*
 * Control register data: the register picked by addr (read mask, blink mask,
 * command, test) is read or written here and addr does not advance. [public]
 * [binary] Gr2BlankScreen writes the read mask this way, ctrl 0 to blank and
 * 255 to unblank, after addr 4, in all three chips.
 */
/* ctrl: rw8, reset unknown */
#define BT457_CTRL_OFFSET                            0x8u /* established */

/*
 * Overlay colour data, entries 0 to 3 selected by addr. Init writes four bytes
 * 0 to 3 after setting addr to 0. [public] [binary]
 */
/* overlay: rw8, reset unknown */
#define BT457_OVERLAY_OFFSET                         0xcu /* established */

/*
 * Command register fields, from the datasheet. The board writes 0xc1.
 */
/* word COMMAND: 8 bits */
#define BT457_COMMAND_WIDTH                          8 /* established */
#define BT457_COMMAND_MUX_SELECT_SHIFT               7 /* established */
#define BT457_COMMAND_MUX_SELECT_MASK                0x1u
#define BT457_COMMAND_MUX_SELECT_INPLACE (BT457_COMMAND_MUX_SELECT_MASK << BT457_COMMAND_MUX_SELECT_SHIFT)
#define BT457_COMMAND_RAM_ENABLE_SHIFT               6 /* established */
#define BT457_COMMAND_RAM_ENABLE_MASK                0x1u
#define BT457_COMMAND_RAM_ENABLE_INPLACE (BT457_COMMAND_RAM_ENABLE_MASK << BT457_COMMAND_RAM_ENABLE_SHIFT)
#define BT457_COMMAND_BLINK_RATE_SHIFT               4 /* established */
#define BT457_COMMAND_BLINK_RATE_MASK                0x3u
#define BT457_COMMAND_BLINK_RATE_INPLACE (BT457_COMMAND_BLINK_RATE_MASK << BT457_COMMAND_BLINK_RATE_SHIFT)
#define BT457_COMMAND_OVERLAY1_BLINK_SHIFT           3 /* established */
#define BT457_COMMAND_OVERLAY1_BLINK_MASK            0x1u
#define BT457_COMMAND_OVERLAY1_BLINK_INPLACE (BT457_COMMAND_OVERLAY1_BLINK_MASK << BT457_COMMAND_OVERLAY1_BLINK_SHIFT)
#define BT457_COMMAND_OVERLAY0_BLINK_SHIFT           2 /* established */
#define BT457_COMMAND_OVERLAY0_BLINK_MASK            0x1u
#define BT457_COMMAND_OVERLAY0_BLINK_INPLACE (BT457_COMMAND_OVERLAY0_BLINK_MASK << BT457_COMMAND_OVERLAY0_BLINK_SHIFT)
#define BT457_COMMAND_OVERLAY1_DISPLAY_SHIFT         1 /* established */
#define BT457_COMMAND_OVERLAY1_DISPLAY_MASK          0x1u
#define BT457_COMMAND_OVERLAY1_DISPLAY_INPLACE (BT457_COMMAND_OVERLAY1_DISPLAY_MASK << BT457_COMMAND_OVERLAY1_DISPLAY_SHIFT)
#define BT457_COMMAND_OVERLAY0_DISPLAY_SHIFT         0 /* established */
#define BT457_COMMAND_OVERLAY0_DISPLAY_MASK          0x1u
#define BT457_COMMAND_OVERLAY0_DISPLAY_INPLACE (BT457_COMMAND_OVERLAY0_DISPLAY_MASK << BT457_COMMAND_OVERLAY0_DISPLAY_SHIFT)

#define BT457_ADDR_BLINK_MASK                        0x5u /* established */
#define BT457_ADDR_COMMAND                           0x6u /* established */
#define BT457_ADDR_READ_MASK                         0x4u /* established */
#define BT457_ADDR_TEST                              0x7u /* established */
#define BT457_INIT_COMMAND                           0xc1u /* established */
#define BT457_INIT_READ_MASK                         0x0u /* established */
#define BT457_OVERLAY_ENTRIES                        0x4u /* established */
#define BT457_PALETTE_ENTRIES                        0x100u /* established */
#define BT457_UNBLANK_READ_MASK                      0xffu /* established */

#endif /* BT457_GEN_H */
