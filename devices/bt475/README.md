# Bt475 and Bt477: datasheet only, no Express use found

The repository holds the Brooktree Bt475/Bt477 datasheet (`docs/Brooktree_Bt475_477.pdf`). No shipped Indigo or Express binary reads
or writes such a part: the IP20 driver and both PROMs address only the three Bt457 windows ([bt457](../bt457/README.md)), and the
Indy XZ board schematic (`VB-3_Schematic.pdf`) shows three BT457 and no BT475. The Entry (LG1) board uses a separate colour map
documented in the newport repository's `devices/bt479`. So the status is **unknown**: nothing places a Bt475 or Bt477 on an Express or Elan
board, and none of this is needed to model the Express display path.

Datasheet-level facts, [public], graded established as facts about the part and kept in [registers.toml](registers.toml) so a later
finding can be checked against them: the part is a triple 6-bit (8-bit on the Bt477) RAMDAC with a 256-entry palette (18 or 24 bits)
and overlay colours; the MPU interface has three select inputs RS2 to RS0 and the truth table is Table 1 of the datasheet (000 address
register write mode, 001 palette data, 010 pixel read mask, 011 address register read mode, 100 overlay write mode, 101 overlay data,
110 command register, 111 overlay read mode). The Bt457's four-port scheme is different (two selects C1, C0 plus an in-chip control register address):
do not substitute one for the other.

Next route if a Bt475 is suspected on a board: the board schematics for the Indigo back end (VB1 and VB1.1), which are not held; a photograph of the
back end board (`photos/bukosek-indigo/express/` in the Library cache) read for chip markings.
