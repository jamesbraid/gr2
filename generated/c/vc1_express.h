/* generated from devices/vc1-express/registers.toml by defs-gen - do not edit,
 * change the source */
/* defs-gen 3 */
/* input sha256 bdb968568ab6b51205c75e2c2446abd3a9e9233a34d6da8e3a16ac8b3520f8f4 */
/* VC1 video timing, cursor and display-ID controller on the Express board */
#ifndef VC1X_GEN_H
#define VC1X_GEN_H

#include <stdint.h>


/*
 * Internal register data port. Set the address pair to an internal register
 * number, then write half-words; the address advances by two after each (cursor
 * x then y are written back to back from address 0x22). Reads of this port
 * never occur in shipped code (revision comes through testreg). [binary] A
 * qtest can discriminate: address 0x22, write two half-words, check the address
 * pair reads back advanced by 4 (inferred).
 */
/* command: rw16, reset unknown */
#define VC1X_COMMAND_OFFSET                          0x6c040u /* established */

/*
 * Window to a display-mode table inside the VC1 (the Entry board's equivalent
 * holds the mode words). Express keeps display modes in the XMAP5 chips
 * instead. Unaccessed. Unknown.
 */
/* xmapmode: rw8, reset unknown */
#define VC1X_XMAPMODE_OFFSET                         0x6c044u /* unknown */

/*
 * External SRAM data port. The SRAM is addressed by byte; each half-word
 * transfer advances the address pair by two. Written from timing images and
 * display-ID tables; read back by the dummy-ID builder and Gr2SetMonitor.
 * [binary]
 */
/* sram: rw16, reset unknown */
#define VC1X_SRAM_OFFSET                             0x6c048u /* established */

/*
 * Revision read: after addrhi = 0 and addrlo = 5, the low three bits are stored
 * as the VC1 revision. The value a real part returns is not recorded. [binary]
 */
/* testreg: r8, reset unknown */
#define VC1X_TESTREG_OFFSET                          0x6c04cu /* established */
#define VC1X_TESTREG_REVISION_SHIFT                  0 /* established */
#define VC1X_TESTREG_REVISION_MASK                   0x7u
#define VC1X_TESTREG_REVISION_INPLACE (VC1X_TESTREG_REVISION_MASK << VC1X_TESTREG_REVISION_SHIFT)

/*
 * Low byte of the 16-bit address pair used by command and sram. Readable: the
 * retrace shadow reads it back to save and restore the pair around
 * interrupt-time use. [binary]
 */
/* addrlo: rw8, reset unknown */
#define VC1X_ADDRLO_OFFSET                           0x6c050u /* established */

/*
 * High byte of the address pair. Readable. [binary]
 */
/* addrhi: rw8, reset unknown */
#define VC1X_ADDRHI_OFFSET                           0x6c054u /* established */

/*
 * System control byte; readable (read-modify-write by the retrace handler and
 * Gr2SetMonitor). Bit roles are NetBSD names [public] except as noted: 0
 * interrupt, 1 timing generator, 2 VC1 core, 3 display IDs, 4 cursor logic, 5
 * cursor display (established: toggled at retrace), 6 genlock (inferred), 7
 * video. Values seen: 1 at start, 3 during table loads, 0x0c final in the
 * kernel, 0x3c final in the PROM. Bit 0 is the vertical-interrupt disable: set
 * blocks the retrace latch, clear lets it set (the final values clear it; a
 * comment on the value 1 in the IRIX source says it disables the interrupt)
 * [binary][source]. qtest: with bit 0 set no retrace latch sets over a frame,
 * with it clear one does.
 */
/* sysctl: rw8, reset unknown */
#define VC1X_SYSCTL_OFFSET                           0x6c058u /* established */
#define VC1X_SYSCTL_VIDEO_SHIFT                      7 /* unknown */
#define VC1X_SYSCTL_VIDEO_MASK                       0x1u
#define VC1X_SYSCTL_VIDEO_INPLACE (VC1X_SYSCTL_VIDEO_MASK << VC1X_SYSCTL_VIDEO_SHIFT)
#define VC1X_SYSCTL_GENLOCK_SHIFT                    6 /* inferred */
#define VC1X_SYSCTL_GENLOCK_MASK                     0x1u
#define VC1X_SYSCTL_GENLOCK_INPLACE (VC1X_SYSCTL_GENLOCK_MASK << VC1X_SYSCTL_GENLOCK_SHIFT)
#define VC1X_SYSCTL_CURSOR_DISPLAY_SHIFT             5 /* established */
#define VC1X_SYSCTL_CURSOR_DISPLAY_MASK              0x1u
#define VC1X_SYSCTL_CURSOR_DISPLAY_INPLACE (VC1X_SYSCTL_CURSOR_DISPLAY_MASK << VC1X_SYSCTL_CURSOR_DISPLAY_SHIFT)
#define VC1X_SYSCTL_CURSOR_SHIFT                     4 /* inferred */
#define VC1X_SYSCTL_CURSOR_MASK                      0x1u
#define VC1X_SYSCTL_CURSOR_INPLACE (VC1X_SYSCTL_CURSOR_MASK << VC1X_SYSCTL_CURSOR_SHIFT)
#define VC1X_SYSCTL_DID_SHIFT                        3 /* inferred */
#define VC1X_SYSCTL_DID_MASK                         0x1u
#define VC1X_SYSCTL_DID_INPLACE (VC1X_SYSCTL_DID_MASK << VC1X_SYSCTL_DID_SHIFT)
#define VC1X_SYSCTL_CORE_SHIFT                       2 /* inferred */
#define VC1X_SYSCTL_CORE_MASK                        0x1u
#define VC1X_SYSCTL_CORE_INPLACE (VC1X_SYSCTL_CORE_MASK << VC1X_SYSCTL_CORE_SHIFT)
#define VC1X_SYSCTL_TIMING_SHIFT                     1 /* unknown */
#define VC1X_SYSCTL_TIMING_MASK                      0x1u
#define VC1X_SYSCTL_TIMING_INPLACE (VC1X_SYSCTL_TIMING_MASK << VC1X_SYSCTL_TIMING_SHIFT)
#define VC1X_SYSCTL_INTERRUPT_SHIFT                  0 /* inferred */
#define VC1X_SYSCTL_INTERRUPT_MASK                   0x1u
#define VC1X_SYSCTL_INTERRUPT_INPLACE (VC1X_SYSCTL_INTERRUPT_MASK << VC1X_SYSCTL_INTERRUPT_SHIFT)

#define VC1X_CURSOR_X_THRESHOLD                      0x20u /* established */
#define VC1X_REG_BLACKOUT                            0x60u /* inferred */
#define VC1X_REG_CURSOR_EP                           0x20u /* established */
#define VC1X_REG_CURSOR_MODE                         0x26u /* inferred */
#define VC1X_REG_CURSOR_X                            0x22u /* established */
#define VC1X_REG_CURSOR_Y                            0x24u /* established */
#define VC1X_REG_DID_DIV                             0x44u /* established */
#define VC1X_REG_DID_END                             0x42u /* established */
#define VC1X_REG_DID_EP                              0x40u /* established */
#define VC1X_REG_REVISION                            0x5u /* established */
#define VC1X_REG_VID_ENABLE                          0x14u /* inferred */
#define VC1X_REG_VID_EP                              0x0u /* established */
#define VC1X_SRAM_CURSOR_FRAME_TABLE                 0x900u /* established */
#define VC1X_SRAM_CURSOR_GLYPH                       0xa00u /* established */
#define VC1X_SRAM_CURSOR_LINE_LIST                   0x400u /* established */
#define VC1X_SRAM_DID_FRAME_TABLE                    0xb00u /* established */
#define VC1X_SRAM_DID_LINE_DEFAULT                   0x1400u /* established */
#define VC1X_SRAM_FRAME_TABLE                        0x800u /* established */
#define VC1X_SRAM_INTERLACED                         0x9f0u /* established */
#define VC1X_SRAM_LINE_LIST                          0x0u /* established */
#define VC1X_SRAM_SCREENWIDTH                        0x9f2u /* established */
#define VC1X_SYSCTL_CURSOR_DISPLAY                   0x20u /* established */
#define VC1X_SYSCTL_GENSYNC                          0x40u /* inferred */
#define VC1X_SYSCTL_LOAD                             0x3u /* established */
#define VC1X_SYSCTL_VC1_DID                          0xcu /* established */

#endif /* VC1X_GEN_H */
