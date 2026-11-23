/* generated from devices/ge7/registers.toml by defs-gen - do not edit, change
 * the source */
/* defs-gen 3 */
/* input sha256 4b24a0dac5a13b9f43b822999a4bd0e8cfedcb3e360d3db1c332e9bdb57d3ece */
/* GE7 geometry engines: host window and microcode load registers */
#ifndef GE7_GEN_H
#define GE7_GEN_H

#include <stdint.h>


/*
 * Shared data RAM below the ready flag. [binary] The microcode loader copies
 * the constants block into its first words and reads them back; its error text
 * calls it shared RAM. [public] NetBSD's memory map names it shared data RAM.
 * qtest: a word written reads back.
 */
/* shared_ram: rw32, reset unknown */
#define GE7_SHARED_RAM_OFFSET                        0x0u /* established */
#define GE7_SHARED_RAM_COUNT                         32767
#define GE7_SHARED_RAM_STRIDE                        4

/*
 * Last word of the shared RAM, used as a flag. [binary] The driver stores 1
 * after the built-in console microcode loads and 0 when a load fails; the
 * consumer is unread, so the meaning "microcode ready" is inferred. qtest:
 * reads back what was written.
 */
/* ucode_ready: rw32, reset unknown */
#define GE7_UCODE_READY_OFFSET                       0x1fffcu /* established */

/*
 * Engine 0 storage below the microcode window. [binary] The engine probe takes
 * slot 0 as present and tests only slots 1 to 7, so ordinary storage here is
 * inferred from the other slots. qtest: the first and the last tested offsets
 * read back a written word.
 */
/* slot0_ram: rw32, reset unknown */
#define GE7_SLOT0_RAM_OFFSET                         0x68000u /* inferred */
#define GE7_SLOT0_RAM_COUNT                          248
#define GE7_SLOT0_RAM_STRIDE                         4

/*
 * Microword column 0, lowest. [binary] The loader writes record bytes 20 to 23
 * here and reads them back unmasked. One window serving every populated engine
 * (broadcast) is inferred. qtest: a full 32-bit value reads back.
 */
/* ucode_d0: rw32, reset unknown */
#define GE7_UCODE_D0_OFFSET                          0x683e0u /* established */

/*
 * Microword column 1. [binary] The loader writes record bytes 16 to 19 here and
 * reads them back unmasked. qtest: a full 32-bit value reads back.
 */
/* ucode_d1: rw32, reset unknown */
#define GE7_UCODE_D1_OFFSET                          0x683e4u /* established */

/*
 * Microword column 2. [binary] The loader writes record bytes 12 to 15 here and
 * reads them back unmasked. qtest: a full 32-bit value reads back.
 */
/* ucode_d2: rw32, reset unknown */
#define GE7_UCODE_D2_OFFSET                          0x683e8u /* established */

/*
 * Microword column 3. [binary] The loader writes record bytes 8 to 11 here; the
 * verify masks both sides to seven bits, so only seven bits are stored. qtest:
 * writing all ones reads back with the low seven bits set.
 */
/* ucode_d3: rw32, reset unknown */
#define GE7_UCODE_D3_OFFSET                          0x683ecu /* established */
#define GE7_UCODE_D3_STORED_SHIFT                    0 /* established */
#define GE7_UCODE_D3_STORED_MASK                     0x7fu
#define GE7_UCODE_D3_STORED_INPLACE (GE7_UCODE_D3_STORED_MASK << GE7_UCODE_D3_STORED_SHIFT)

/*
 * GE7 revision. [binary] The kernel driver and the PROM probe write zero, read
 * the word back and keep bits 7:5 of the low byte. [public] NetBSD reads
 * another offset in slot 0 and keeps bits 7:4; no shipped binary read touches
 * that offset, so this register is taken as the revision. That the three bits
 * are a revision number is inferred. qtest: after a write of zero, bits 7:5
 * read as the configured revision.
 */
/* revision: rw32, reset unknown */
#define GE7_REVISION_OFFSET                          0x683f4u /* established */
#define GE7_REVISION_REV_SHIFT                       5 /* inferred */
#define GE7_REVISION_REV_MASK                        0x7u
#define GE7_REVISION_REV_INPLACE (GE7_REVISION_REV_MASK << GE7_REVISION_REV_SHIFT)

/*
 * Engine slots 1 to 7, 1 KiB each. [binary] The engine probe writes five words
 * per slot at slot offsets 0x0, 0x7c, 0xfc, 0x17c and 0x1fc and reads them
 * back; each slot that returns all five sets the count to its index plus one.
 * An absent slot's reply (bus error or data), storage beyond the last probed
 * offset, and whether the load window and revision register repeat in these
 * slots are unknown. qtest: slot n returns the five written words for n below
 * the engine count and not above.
 */
/* slot_ram: rw32, reset unknown */
#define GE7_SLOT_RAM_OFFSET                          0x68400u /* established */
#define GE7_SLOT_RAM_COUNT                           1792
#define GE7_SLOT_RAM_STRIDE                          4

#endif /* GE7_GEN_H */
