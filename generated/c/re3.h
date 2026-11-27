/* generated from devices/re3/registers.toml by defs-gen - do not edit, change
 * the source */
/* defs-gen 4 */
/* input sha256 e559fb7a2c82246cdc738e1fe92d4bcc43e2ea7556f489b4fc11622933bb8317 */
/* RE3 raster engine: host-visible register banks */
#ifndef RE3_GEN_H
#define RE3_GEN_H

#include <stdint.h>


/*
 * First word of the bank [public] a public driver's memory map calls the 27-bit
 * registers. Extent, register names and reset values unknown. No shipped
 * program read (PROM, kernel driver, GL core, X driver, diagnostic program)
 * accesses this bank [binary, negative search, inferred]. qtest: none can be
 * written until a source gives the layout; the first test is that an access
 * does not fault.
 */
/* bank_27bit: rw32, reset unknown; NetBSD sgimips public driver memory map
 * comment */
#define RE3_BANK_27BIT_OFFSET                        0x6c200u /* unknown */

/*
 * First word of the bank [public] a public driver's memory map calls the 24-bit
 * registers. Extent, register names and reset values unknown; no shipped
 * program read accesses it [binary, negative search, inferred]. qtest: as for
 * the 27-bit bank.
 */
/* bank_24bit: rw32, reset unknown; NetBSD sgimips public driver memory map
 * comment */
#define RE3_BANK_24BIT_OFFSET                        0x6c280u /* unknown */

/*
 * First word of the bank [public] a public driver's memory map calls the 32-bit
 * registers. Extent, register names and reset values unknown; no shipped
 * program read accesses it [binary, negative search, inferred]. qtest: as for
 * the 27-bit bank.
 */
/* bank_32bit: rw32, reset unknown; NetBSD sgimips public driver memory map
 * comment */
#define RE3_BANK_32BIT_OFFSET                        0x6c600u /* unknown */

#endif /* RE3_GEN_H */
