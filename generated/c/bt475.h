/* generated from devices/bt475/registers.toml by defs-gen - do not edit, change
 * the source */
/* defs-gen 3 */
/* input sha256 e092e289cdf7071aaa43ac066a8157c9ebaf1861cc18de50147bf970a5c6e882 */
/* Brooktree Bt475 and Bt477 RAMDAC: datasheet port map only, no Express use
 * found */
#ifndef BT475_GEN_H
#define BT475_GEN_H

#include <stdint.h>


#define BT475_SEL_ADDR_READ                          0x3u /* established */
#define BT475_SEL_ADDR_WRITE                         0x0u /* established */
#define BT475_SEL_COMMAND                            0x6u /* established */
#define BT475_SEL_OVERLAY_DATA                       0x5u /* established */
#define BT475_SEL_OVERLAY_READ                       0x7u /* established */
#define BT475_SEL_OVERLAY_WRITE                      0x4u /* established */
#define BT475_SEL_PALETTE                            0x1u /* established */
#define BT475_SEL_READ_MASK                          0x2u /* established */

#endif /* BT475_GEN_H */
