<!-- generated from devices/bt475/registers.toml by defs-gen - do not edit, change the source -->
<!-- defs-gen 3 -->
<!-- input sha256 e092e289cdf7071aaa43ac066a8157c9ebaf1861cc18de50147bf970a5c6e882 -->

# Brooktree Bt475 and Bt477 RAMDAC: datasheet port map only, no Express use found

The Bt475 and Bt477 triple RAMDACs are described in the published datasheet held in the repository but no shipped Indigo or Express binary reads or writes one, and none of the Express schematics held names one. This page records only the datasheet's control-input truth table so that a later finding can be graded against it; it is not a statement that any Express board carries the part. Grades: established means stated by the published datasheet as a fact about the part; whether the part is on an Express board is unknown. Prose in devices/bt475/README.md.

Unit `bt475`, macro prefix `BT475`.
Default source: Brooktree Bt475/Bt477 datasheet (docs/Brooktree_Bt475_477.pdf), Table 1.

Every item has a grade: established, inferred or unknown. A grade says how the item was derived from its source; it does not claim the item was measured on silicon.

## Constants

| Constant | Value | Grade | Source | Description |
|---|---|---|---|---|
| `SEL_ADDR_READ` | 0x3 | established | Brooktree Bt475/Bt477 datasheet (docs/Brooktree_Bt475_477.pdf), Table 1 | 011: address register, RAM read mode. [public] |
| `SEL_ADDR_WRITE` | 0x0 | established | Brooktree Bt475/Bt477 datasheet (docs/Brooktree_Bt475_477.pdf), Table 1 | RS2 RS1 RS0 = 000: address register, RAM write mode. [public] datasheet Table 1. |
| `SEL_COMMAND` | 0x6 | established | Brooktree Bt475/Bt477 datasheet (docs/Brooktree_Bt475_477.pdf), Table 1 | 110: command register. [public] |
| `SEL_OVERLAY_DATA` | 0x5 | established | Brooktree Bt475/Bt477 datasheet (docs/Brooktree_Bt475_477.pdf), Table 1 | 101: overlay colour data. [public] |
| `SEL_OVERLAY_READ` | 0x7 | established | Brooktree Bt475/Bt477 datasheet (docs/Brooktree_Bt475_477.pdf), Table 1 | 111: address register, overlay read mode. [public] |
| `SEL_OVERLAY_WRITE` | 0x4 | established | Brooktree Bt475/Bt477 datasheet (docs/Brooktree_Bt475_477.pdf), Table 1 | 100: address register, overlay write mode. [public] |
| `SEL_PALETTE` | 0x1 | established | Brooktree Bt475/Bt477 datasheet (docs/Brooktree_Bt475_477.pdf), Table 1 | 001: colour palette RAM data. [public] |
| `SEL_READ_MASK` | 0x2 | established | Brooktree Bt475/Bt477 datasheet (docs/Brooktree_Bt475_477.pdf), Table 1 | 010: pixel read mask register. [public] |
