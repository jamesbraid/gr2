<!-- generated from devices/re3/registers.toml by defs-gen - do not edit, change the source -->
<!-- SPDX-License-Identifier: BSD-3-Clause -->
<!-- defs-gen 5 -->
<!-- input sha256 e559fb7a2c82246cdc738e1fe92d4bcc43e2ea7556f489b4fc11622933bb8317 -->

# RE3 raster engine: host-visible register banks

Host window of the RE3 raster engine in the Express graphics slot. Only the three banks that a public driver comment names are listed; their contents are unknown. Provenance tags in item text: [public] published document or public driver, [binary] shipped binary, [vendor-derived] upstream headers (none used). See the unit README.

Unit `re3`, macro prefix `RE3`.
Default source: NetBSD sgimips public driver memory map comment.

Every item has a grade: established, inferred or unknown. A grade says how the item was derived from its source; it does not claim the item was measured on silicon.

## Registers

| Register | Offset | Access | Width | Count | Space | Reset | Grade | Source |
|---|---|---|---|---|---|---|---|---|
| `bank_27bit` | 0x6c200 | rw | 32 |  |  | unknown | unknown | NetBSD sgimips public driver memory map comment |
| `bank_24bit` | 0x6c280 | rw | 32 |  |  | unknown | unknown | NetBSD sgimips public driver memory map comment |
| `bank_32bit` | 0x6c600 | rw | 32 |  |  | unknown | unknown | NetBSD sgimips public driver memory map comment |

### Register `bank_27bit`

First word of the bank [public] a public driver's memory map calls the 27-bit registers. Extent, register names and reset values unknown. No shipped program read (PROM, kernel driver, GL core, X driver, diagnostic program) accesses this bank [binary, negative search, inferred]. qtest: none can be written until a source gives the layout; the first test is that an access does not fault.

### Register `bank_24bit`

First word of the bank [public] a public driver's memory map calls the 24-bit registers. Extent, register names and reset values unknown; no shipped program read accesses it [binary, negative search, inferred]. qtest: as for the 27-bit bank.

### Register `bank_32bit`

First word of the bank [public] a public driver's memory map calls the 32-bit registers. Extent, register names and reset values unknown; no shipped program read accesses it [binary, negative search, inferred]. qtest: as for the 27-bit bank.
