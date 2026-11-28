# Console microcode of the Indy and Indigo2 Express: kernel pair and PROM pair

Where a driver that has to put text on an Indy or Indigo2 Express board before the full microcode loads can get its HQ2 and GE7 console images, which of the two sources has the `RECTCOPY` token, and how to cut each out. Written for a Windows NT display driver design that must carry the images itself. The start-up around the images is in [ip22-startup.md](ip22-startup.md); the image format, loaders and token set are in [microcode.md](microcode.md#the-console-tokens) and [host-contract.md](host-contract.md#c-console-images-gr2tpsetup-gr2_tportso-and-gr2_tpucodeo).

Ratings: as in [AGENTS.md](../../AGENTS.md), **established** is a fact read from a held file with a tool (hash, offset, size, record count, byte value), including what shipped code does. **Inferred** is a reasoned reading, with the reasoning, and includes a claim about hardware behaviour that rests only on what software does. **Unknown** is what the sources leave open. Source classes: [binary] shipped IRIX 6.5 base-set objects and the held PROM images. Nothing was run on a board.

## Answer

| Question | Answer | Rating |
|---|---|---|
| Is there a console pair in the Indy and Indigo2 PROMs? | Yes, one pair, byte-identical in every held IP22 and IP24 PROM (two IP22 revisions, two IP24 revisions) and also in the IP26 and IP28 PROMs. HQ2 image 3,762 bytes, 150 records; GE7 image 10,286 bytes, 308 records. Offsets in [the PROM table](#the-prom-pair). | established |
| Is there a pair in the kernel? | Yes: `gr2_tpucode.o` in `IP22boot/gr2.a` (and `IP20boot`, `IP26boot`, `IP28boot`). HQ2 image 3,552 bytes, 129 records; GE7 image 9,142 bytes, 264 records. The image bytes are identical in all four archives and in the 6.5.22 `IP22boot` archive, though the object files differ. | established |
| Does the kernel pair carry `RECTCOPY` (slot 409)? | **No.** Its HQ2 image has no first-level word for slot 409, and its GE7 image lacks the 44-word routine that the PROM pair starts for slot 409. | established |
| Does the PROM pair carry it? | **Yes.** Slot 409 jumps to HQ2 address 629, reads eight operand words and starts GE7 at 208 (the routine occupies GE7 addresses 208 to 251). | established |
| Which should a driver use? | The PROM pair if it needs `RECTCOPY` (hardware scroll). The kernel pair has seven drawing tokens and no copy, so a scroll must be redrawn. Neither pair is the full image, which also lacks 409. | established (the kernel text port, `gr2_tport.o`, has no store to `+0x40664` in the IP20 or IP22 archive; the PROM text port sends 409, [microcode.md](microcode.md#the-console-tokens)) |

## The kernel pair

### Held archives

| Archive | SHA-256 of `gr2.a` | `gr2_tpucode.o` SHA-256 |
|---|---|---|
| 6.5 base, `usr/cpu/sysgen/IP20boot/gr2.a` | `c768b3a4889dd50e8e78c065fdddb7ebca2d9536eb39de315511d2a90906128c` | `f77f0399144444240211430708450a556ef67644d4c3beabc220e575315ea211` |
| 6.5 base, `usr/cpu/sysgen/IP22boot/gr2.a` | `19ef07c204ce1fc3c73d3f12783adb1824d48b8ee9af28538914fedf33b6f228` | `8084f158da53e5771021cbed62443bb13756c5748e4c1571657705ef56c2d599` |
| 6.5.22, `usr/cpu/sysgen/IP22boot/gr2.a` | `6e4dde1ca2371aaaf44d06475201b2937831a23b0e4dc761c3565bd2f8980aa2` | `86848e16c30071e11e2966bd9788945c39e6b96196c70953bd3fbf8a4142509d` |

The 6.5 base `IP26boot` and `IP28boot` archives (`d3e04881336eb5efc014fdc32b130eabe7d84b6f966de18453478951af1531b4`, `659d7fb3e842d542c73fc40e8918898aeb55fd972927fe9f140388ab760cd72a`) carry the same image bytes in their own `gr2_tpucode.o` (`31587d19ee80dba947df41ad72fe6184e4d62d86b4441018769255b8115325d9`, `d2872e969141b1b3d1ce0d2c1f65a656899ac95278183e4f415b1c04fd1496b2`). The two 6.5 base objects (`IP20boot`, `IP22boot`) differ only in their debug sections (`.debug_info`, `.debug_pubnames` and the relocations against `.debug_info`); code, data and relocations match. The 6.5.22 object was rebuilt (its `.text` is 472 bytes against 480) and its `.data`, which holds both images, is identical to the others. Established by comparing every section.

An earlier page ([ip22-slot-comparison.md](ip22-slot-comparison.md#microcode)) recorded `04930f71...` as the hash of a `gr2_tpucode.o` shared by `IP20boot` and `IP22boot`. No held copy reproduces it: the two objects above differ from each other, and neither equals it, nor does the hash of the two images concatenated in either order or of the `.data` section. The page's claim that the two objects are byte-identical is withdrawn; the claim that the images are identical stands.

### Recipe

1. Extract the member: `ar x gr2.a gr2_tpucode.o`. GNU `ar` reads these SGI archives.
2. The member is a 32-bit big-endian MIPS ELF relocatable object. The images sit in its `.data` section (size `0x31c0`, file offset `0x7b8` in both 6.5 base objects, `0x678` in the 6.5.22 object). Two global data symbols name them: `ge_ucode_str` at `.data` + `0` (symbol size 9,168) and `hq_ucode_str` at `.data` + `0x23d0` (size 3,568). The routines that use them are `Gr2TpGEUcodeSetup`, `Gr2TpHQUcodeSetup` and `Gr2TpSetup`, in the same object.
3. An image starts at the symbol and runs to its terminator record (a record whose address half-word is `0xffff`). That is 9,142 bytes for GE7 and 3,552 for HQ2, 26 and 16 bytes short of the symbol sizes; the loader stops at the terminator and the tail is not read. The 26 bytes after the GE7 image are not all zero (`00 00 48 00 00 02 00 00` then zeros); their purpose is unknown and nothing uses them.
4. Or run `tools/ucode-decode.py ide gr2_tpucode.o OUTDIR`, which finds both by magic and writes `ge7-<offset>.bin` and `hq2-<offset>.bin` (offset is within the member: `0x7b8` and `0x2b88`, or `0x678` and `0x2a48` in 6.5.22).

Image header (both images): half-word magic `0x966e` (GE7) or `0x965e` (HQ2), version 1, text offset `0x1c`, then the table offsets the loaders use; GE7 record length 26, HQ2 record length 10. Every record checksum verifies (`tools/ucode-decode.py info`: 0 mismatches in both). The attribute jump table at image offset `0xfc` and the loaders are in [microcode.md](microcode.md).

| Image | Member offset | Offset in 6.5 base `IP20boot/gr2.a` | in `IP22boot/gr2.a` | in 6.5.22 `IP22boot/gr2.a` | Size | Records | SHA-256 |
|---|---|---|---|---|---|---|---|
| GE7 | `0x7b8` (`0x678`) | `0x18b98` | `0x1c468` | `0x1b958` | 9,142 | 264, addresses 0 to 271 | `913f8480dd977c44f075fe34c241de41c8992daeadf89d32f83d1ed643a136fa` |
| HQ2 | `0x2b88` (`0x2a48`) | `0x1af68` | `0x1e838` | `0x1dd28` | 3,552 | 129, addresses 0 to 629 | `71842d493447797ca17fb7a2a87b0476251eada21fd277a08b8131e2ffcf2f22` |

Member offsets in parentheses are for 6.5.22. Established for all of it. The member's own name strings read "IP12/GR2 PROM GE Microcode" and "IP12/GR2 PROM HQ Microcode" in all three objects, so the label says IP12 and the Indy and Indigo2 objects carry it unchanged.

### No `RECTCOPY`

HQ2 slot walks (`tools/ucode-decode.py hq2 IMG 401 ... 419`), kernel pair: first-level words exist for 401, 402, 404 to 408 and 417 to 419; none for 403 and 409. Compared with the PROM pair below, the kernel images are the PROM images with slot 409's HQ2 words (the entry at 409 and 20 records at 630 to 649, 21 in all) and GE7 addresses 208 to 251 removed, and every later GE7 address lowered by 44: GE7 addresses 0 to 207 are word-for-word equal; kernel addresses 208 to 271 equal PROM addresses 252 to 315, except one word whose branch target moved by 44 (kernel address 235, target `0xf3` against `0x11f`); the start addresses of slots 417, 418 and 419 in HQ2 are 44 lower. Established. So the kernel pair is the PROM pair without `RECTCOPY`, not a different design.

## The PROM pair

### Held PROM images

All images are 524,288 bytes. The offsets are file offsets. The cut images are the same in every row, so the pair is one pair.

| Part | Banner | SHA-256 of the file | HQ2 offset | GE7 offset |
|---|---|---|---|---|
| IP22 Indigo2 `070-8127-002` | 5.1 Rev B, Sep 16 1993 | `be6b22c3b90adf6eebc18da11ce49e59292eeab35b694c6e8bd75ef485a40241` | `0x66fe0` | `0x67ea4` |
| IP22 Indigo2 (catalogue name `ip22prom-5.3revE.bin`) | 5.3 Rev E, Jan 29 1996 | `7b3eb33889bcc40c3dadc7093c06d3e221b6e2a5073acc556f62932b08b6cd8a` | `0x6dc40` | `0x6eb04` |
| IP24 Indy `070-9101-007` | 5.0 Rev B6, Sep 28 1994 | `ea6800820dddf98e4bdfc3b9d15d7e44e801cc10aebed2774d42171970a471ba` | `0x72eec` | `0x73db0` |
| IP24 Indy `070-9101-011` | 5.3 Rev B10, Feb 12 1996 | `333a0b2e39bb828a28a758b6f633ae7290030129dc747297a1be68dc317b86ae` | `0x72714` | `0x735d8` |
| IP24 Indy, copy staged as `ip24prom.indy-5.3.d7ffc8e1adf5.bin` | same ROM | `d7ffc8e1adf53650672c65c871295fc45a55e6a0823ffe2e28b2aaa541c3e515` | the `070-9101-011` offsets, in the 16-bit byte-swapped file | same |
| IP26 Indigo2 `070-1361-003`, `-004` | 6.0.1 Rev A | `a7d146a3741e96c9c251605af53976864fae7878c4f4b20cc9f1089e4d4eb461`, `78693b05d31fea43876c19e8d399a4832d329bbb1dc1ce88b4ef169128388e40` | `0x543dc`, `0x544cc` | `0x552a0`, `0x55390` |
| IP28 Indigo2 `070-1477-001`, `-002` | 6.2 Rev A | `272fe7de651977c9cfe6cdf36cf0da4147c2ef3bff17b09303c017c40a624970`, `a2c1cf6a8fcfe8e0bb8a82c77a0f3e4cb9b640fa995ee8a957069c993ede9246` | `0x5b8d0`, `0x5d2b0` | `0x5c798`, `0x5e178` |

Established: the offsets, the sizes and the identity of the cut images. The `ip24prom.indy-5.3.d7ffc8e1adf5.bin` file is `070-9101-011` with each pair of bytes swapped (swapping them back reproduces its SHA-256 exactly); its source is not recorded. To cut an image from a PROM: `tools/ucode-decode.py cut PROM OFFSET OUT`. The file must be in the byte order of the part-number files (`0b f0 00 f0` at the start, a MIPS jump).

| Image | Size | Records | Addresses | SHA-256 |
|---|---|---|---|---|
| HQ2 | 3,762 | 150 | 0 to 649 | `51ee313776cc6fea646c24e7c3e934ba50f1fd8794dbcaa21d3d0b007558482c` |
| GE7 | 10,286 | 308 | 0 to 315 | `0867b4cb28a4aa9984320dc73317208b805b425f0c19a77fe116e5bb6a94f1d9` |

Record checksums verify in both (0 mismatches). The 6.5 base diagnostic programs `sbin/stand/ide.IP20`, `ide.IP22` and `ide.IP28` each carry this same pair as their console pair (IP20 at `0xe4d84` and `0xe5c48`, IP22 at `0x1d047c` and `0x1d1340`; the cut images hash the same), next to two larger diagnostic images. Established.

The pair is a later build than the Indigo PROM's. The Indigo's 4.0.5D PROM (`070-8116-004`) carries a pair of 149 and 301 records, 3,752 and 10,104 bytes (HQ2 at `0x49840`, GE7 at `0x4a6f4`), which [microcode.md](microcode.md) reads in detail; the IP22 pair has seven more GE7 words before slot 404's routine (it starts at 58 in the 4.0.5D image, 65 here); slot 409's routine starts at GE7 201 in the 4.0.5D image and 208 here. The routine bodies were not compared word for word.

### Where the CPU sees the file

The first word of each PROM is a jump into `0x1fc003c0`, so the part's first 512 KiB sits at physical `0x1fc00000` and file offset `X` is at `0x1fc00000 + X` (`0xbfc00000 + X` in KSEG1). That is the layout the Indigo PROM notes use. A search of the four held IP22 and IP24 PROMs for a stored pointer or a `lui`/`ori` pair that names either image found none, so how the PROM's own text port reaches the images (a different address window, a runtime-computed pointer) was not read. Inferred for the mapping of the file at reset; **unknown** whether the PROM code addresses the images through that window.

### `RECTCOPY` in the PROM pair

HQ2 slot 409: jump to 629, call the subroutine at 601, one flag word, read-ahead into slots 14 and 13, six reads into slots 0 to 5 (the last read-last), start GE7 at 208. The GE7 routine at 208 to 251 is 44 words. The operand meaning (width in words, a line count, six more words) is read from the 4.0.5D routine in [microcode.md](microcode.md#the-console-tokens); the IP22 routine's HQ2 side has the same shape (slot reads 14, 13, 0 to 5), its GE7 words were not stepped. Established for the HQ2 walk and the existence and length of the GE7 routine; the IP22 routine's operand semantics are **inferred** from the 4.0.5D reading.

## What would settle the rest

- How the IP22 and IP24 PROM text port finds its images: read the PROM's text-port setup (the routine that stores the board class to `+0x4077c` after both downloads) in a disassembly of the 5.3 images. Not done here.
- Whether `RECTCOPY` runs correctly from the IP22 pair on silicon (the y origin runs from the bottom, `1024 - y - height`, per [microcode.md](microcode.md)): a model that runs GE7 words, or a board.
- What the 26 bytes after the kernel GE7 image are: not needed by any loader; settled by finding a reader, or by the producer's tools.
