# Shipped binaries read for the Express survey

Copied by the reader from their own IRIX 6.5 base media (June 1998 set) into the ignored `root/`. Paths are the install paths on the media. Nothing here is committed.

| Install path | SHA-256 | Used for |
|---|---|---|
| `usr/cpu/sysgen/IP20boot/gr2.a` | `c768b3a4889dd50e8e78c065fdddb7ebca2d9536eb39de315511d2a90906128c` | The Indigo (IP20) GR2 kernel driver archive. Members, each also hashed below: `gr2.o`, `gr2_dma.o`, `gr2_init.o`, `gr2_retrace.o`, `gr2_tport.o`, `gr2_tpucode.o`. No Corona I2C member. |
| `usr/cpu/sysgen/IP20boot/gr2stubs.a` | `be1eab53bf45fece3ab0f05a21c165aaa3c9c74fdabb8606f49d9a5a4c706b01` | Stub archive for kernels without the board. Not read. |
| `usr/cpu/sysgen/IP20boot/gfx.o` | `4295be87a76062f37fd32b04348e1b9667c2629da48308ccb0ad80bab72ee3e2` | Common graphics layer the driver registers with. Not read. |
| `usr/cpu/sysgen/IP20boot/rrm.o` | `9cfafdd10870873454d4df20163c350a768c61f3e4a8ae2ad6223573cd2554b4` | Rendering resource manager. Not read. |
| `var/sysgen/master.d/gr2` | `b2286d035b8c1d6cf20e86b57c10ac9695829cad8c6a4d3bdeea78ae54a5726c` | Driver configuration: prefix `gr2_`, depends on `gfx`. |
| `usr/gfx/ucode/hq2.bin` | `0c1fbe18d1b451ee32fb81afa4dd85aa86beeee2c5f7fc8b2e33e79e4375fc94` | HQ2 microcode image, 58682 bytes. |
| `usr/gfx/ucode/ge7.bin` | `085d9e923476750673146a517df5847636e7165fb8e7cb4723f7eef07b114729` | GE7 microcode image, 611432 bytes. |
| `usr/gfx/ucode/GR2/vof/adjntsc.bin` | `a189ed0798dccc5b348618d649ad37bb2a61cf6fd655a4500fdcaf22558cde2e` | Genlock adjustment data for NTSC. Not read. |
| `usr/gfx/ucode/GR2/vof/adjpal.bin` | `790d4ca3dc3f8e493186f3d40fff8374724f90f6d1ff11c520856c6596b4727a` | Same for PAL. Not read. |
| `usr/gfx/ucode/GR2/vof/60hz.u` | `db48eeccd7e72ceeefe6ab43b72b92ba67c3369ef552d96e805571a0242e67a9` | One of the 2176-byte video timing files (also `30hz`, `48hz`, `50hz`, `72hz`, `ccir50`, `ccir60`, `iris3k`, `ntsc`, `pal`, `presenter`, `presenter1280`). Not read. |
| `ide.IP20` (the Diagnostics 5.2 program; MIPS-III ECOFF, not stripped) | `744fdebc31843998a3e7d1452873eb8eaf0560c17b8f051da79564ba28fedf14` | The Indigo diagnostic program. Carries four microcode images (a GE7 and an HQ2 diagnostic image, and a GE7 and an HQ2 console pair) and the host side of the known-answer tests (`gr2_FloatOpsTest`, `gr2_GeSeqTest`, `pix_dma` and the other tests named in the microcode page). Its symbols give the test names. Hashed 2026-11-24 from the reader's ignored `root/ide.IP20`; the install path on the media is not recorded. |
| `usr/gfx/arch/IP12GR2/libGLcore.so` | `db8d0331ff6c657ab3e1dc60279741ff4ab00a6c11235c5d0df494ae26e13487` | GL core, o32 build, for GR2 on the R3000/R4000 Indigo. Not read. |
| `usr/gfx/arch/IP12GR232/libGLcore.so` | `b6731da1b4422e1ea1e8fbe841af2e05989d4c3022d9c8b8143a53187f67de9a` | GL core, n32 build; the FIFO token addresses in the pipeline page are read from it, and (round 8) `__glExpPassCullFace`, `__glExpPassFrontFace` and `__glExpGetRasterPosData`. |
| `usr/gfx/arch/IP12GR2*/libGL.so`, `libgl.so` | see media inventory | GL and IrisGL clients. Not read. |

Extracted `gr2.a` members (SHA-256):

- `gr2.o` `e03854933506abf8204706da353b90ae794f98a3e82e4820952cf50e9242ecae`
- `gr2_dma.o` `0bdc863a55232f72d9dc8e923baa46e5e9da7044df14a22c9b345b348da15e4a`
- `gr2_init.o` `73c4986fdefa9258801962079402ecd74f188358b80c43fd7ba8a759268447fe`
- `gr2_retrace.o` `5d698d07d380afb82f1ac334b6637d15995b7a65b1177f899b89d122f4d3beb8`
- `gr2_tport.o` `fe25685c26aada022361083655d8d29683d781c4344aadf971dc5fea86c143e6`
- `gr2_tpucode.o` `f77f0399144444240211430708450a556ef67644d4c3beabc220e575315ea211`

The upstream `root/...` symlinks name an IP12 build of these objects (it also lists a `gr2_corona_i2c.o`). They are not the IP20boot objects above; whether the shared members are byte-identical is not checked.

Local PROM copies used by the microcode passes (hashes of the files read; the 4.0.5D image decodes as the page says, with the HQ2 image at `0x49840` and the GE7 image at `0x4a6f4`): 4.0.5D `e6e1f1ed90d5979ef5829f823c2a4ff65ea24c3273a2b065a8b71abeba97f82f`; 4.0.5G `ae35c0971b594c9f028f79e2fd97bf45fbf170697b334d2ca8a4f46349d939bd`, verified as `070-8116-005`: it is byte-identical to the library copy `library/cache/firmware/indigo/ip20prom-070-8116-005-BE.bin`, and its banner reads 4.0.5G Rev B (HQ2 image at `0x4d294`). The 4.0.5D banner reads 4.0.5D Rev A; its part number `070-8116-004` is not checked against a library copy (none was found).

PROMs that probe the board: Indigo R4000 `070-8116-004` (4.0.5D) and `070-8116-005` (4.0.5G); the probe is described in the chips repository's `platforms/ip20/gio.md`.

## IRIX 5.3 install disc (round 9)

A second release, read from the reader's copy of the IRIX 5.3 install disc image (SGI disk label, EFS partition; the disc the chips repository's `references/ip12-binaries.md` describes and extracts the same way). Install paths are those of the disc's `dist/eoe1.idb` and `dist/x_eoe.idb`. The disc carries the Express kernel archives for the R3000 Indigo (`IP12boot`) and the R4000 Indigo (`IP20boot`), the GL and IrisGL libraries, the X server's GR2 display modules, the loader `gfxinit`, and the two microcode images as files under `usr/gfx/ucode` (the IP22 NG1 libraries were extracted and not read). Nothing is committed. All are [binary] sources; the disc is held, but the Library's text search does not index installation media, so the lookup was by hash.

| Item | Size | SHA-256 |
|---|---|---|
| Disc image `IRIX 5.3.iso` | 525377536 | `a194caea63d280109c37d50be929c34a0f80a23c3e951c3cfa2af1315a0d8cad` |
| `dist/eoe1.sw` (archive: 13-byte header, then a 16-bit path length, the path and `cmpsize` bytes per file) | 88115456 | `070ab3b3447879f5c7e44fbe27430d9d2bc6db7d2983b096e2010e1ea7b45780` |
| `dist/eoe1.idb` | 666418 | `b2db306f94fb366a70fa6e07e55baa02e3924a312ddfaf05daf749271e5d344c` |
| `dist/x_eoe.sw` | 28762742 | `c9659edda9484abbb0a3a6985b7553dc7a7e41cbd1fcabf59aa211c9c6ab716a` |
| `dist/x_eoe.idb` | 204295 | `0c88537f9c3aed255b7a28202464992ace09be2ad88d3b0f41b1377f2f2b09fc` |
| `usr/gfx/ucode/ge7.bin` (608390 bytes, 23312 records, checksums good) | 608390 | `a9703e817e5de24054b07b44d97afa5d3bc4ee44af97433244a7e6a98be4fc15` |
| `usr/gfx/ucode/hq2.bin` (57392 bytes, 5513 records, checksums good) | 57392 | `94ec5ba56589a66657469ce8f72b2717576196b2210a54160f106c9d5c3fd851` |
| `usr/gfx/ucode/GR2/vof/60hz.u`, `72hz.u`, `adjntsc.bin`, `adjpal.bin` | | `60hz.u`, `adjntsc.bin` and `adjpal.bin` equal the 6.5 hashes above, and `72hz.u` (`69f93081cc88ed103b889a5457d4b96ec9d45cc559a6367b3c8f175b455f7273`) equals the 6.5 copy read in round 1. `30hz`, `48hz`, `50hz`, `ccir50`, `ccir60`, `iris3k`, `ntsc`, `pal`, `presenter`, `rs343a` and `st492` were extracted and not read; `presenter1280` is not on this disc |
| `usr/cpu/sysgen/IP20boot/gr2.a` (the R4000 Indigo's driver archive, o32 ECOFF objects) | 92340 | `04d78b92e8fdd329139c90b117c44bcfd4e75d6720c45f7dd94a14a4b00ccc37` |
| `usr/cpu/sysgen/IP20boot/gr2stubs.a` | 740 | `ced50fc8c0393f33d9ec048850744a40f7a6bd0466130182d8f1ce567283224a` |
| `usr/cpu/sysgen/IP20boot/gfx.o`, `rrm.o` (not read) | 17748, 28916 | `b2ac8c4d...2467`, `00767fd5...0a32` |
| `usr/cpu/sysgen/IP12boot/gr2.a` (the R3000 Indigo's; the chips repository hashes the same file) | 90984 | `bbe461d4e0919bcf4a68c48562036d339131a17761fbbb1d65f8fa85e0478e68` |
| `usr/gfx/arch/IP12GR2/libGLcore.so` (o32, MIPS-I) | 1563764 | `0148b9b01abb053d97a092acca01494549a1c675e4e924dc7b3b0a1fa11e9f88` |
| `usr/gfx/arch/IP12GR2/libGL.so` | 323188 | `8599ce098e5fe1fc746b6e577655b7295f8846c9f1caa17213c9c312603eee50` |
| `usr/gfx/arch/IP12GR2/libgl.so` (IrisGL, 7068 function and object symbols) | 1914236 | `2627309d869d730caf489b2d0a4796905a41b1463e0f70198f0bb93db2a89228` |
| `usr/gfx/arch/IP12GR2/libgl_s` (ECOFF) | 1405968 | `7443de15d2fc83511b866a19d44d79da67ac17b2eb3a1ee0950e02ae376cf8a3` |
| `usr/gfx/gfxinit` (the user-space loader of the two images) | 178376 | `524c75008943e9fb7d6db74ae65414573661561f78acc222ef2f78375de91e54` |
| `usr/lib/X11/dyDDX/gr2.so` (Indigo; stripped) | 1337584 | `c806ccc8c338cba9dd45beea8142284fb1151278d2e65e120a4cacad53650d60` |
| `usr/lib/X11/dyDDX/gr2ev.so`, `gr2mp.so`, `gr2tp.so` (the other Express display modules; token scan only) | 1217280, 1208560, 1230144 | listed below |
| `usr/gfx/arch/GENERIC/Xsgi` (stripped) | 917664 | `5096bf18a00ba9b2c344821bf74bfee14144d46c96a6c10d8d22d1e3c236daaa` |
| `var/sysgen/master.d/gr2` | 114 | `ad6b85d2f8ed6b44f355f1057388a5948b225a54b8f5ad54822aa1f64ed43589` |
| `stand/ide` for the R4000 Indigo (`CPUBOARD=IP20`, 976800 bytes) | 976800 | `c6dd9b20df9e8a3caef385697238ccbc3176d3a889c543a9e4837714a0999ea3` |
| `stand/ide` for the R3000 Indigo (`hw_field.ide`, `GFXBOARD=EXPRESS`; the chips repository hashes it) | 636048 | `5979f1532c4e0de0208115ff47197f9023901c8a663e713ed4a3c2859323ff4c` |

`gr2ev.so` `3234e58d175ee94dd56397c583bc870d0bb22ae8803aa23b5d6782c2a1fb84a3`, `gr2mp.so` `bb80305e6de2c0d8d95c6f3aad698fcab686efedb4ba6ca8a09f186f67b99073`, `gr2tp.so` `35c9d005bb030965c87c719f4b364eb6f258de2c0b7c82069910b5d35cf69586`.

Extracted `IP20boot/gr2.a` members (SHA-256): `gr2.o` `da844b3379668da55ed294808e129ec752425c67e2d09d8732032ae6d13ec96c`, `gr2_dma.o` `80552ab4810c043f21c6d525bb68650331188f1a2804c877dd056e65ae8d6a1d`, `gr2_init.o` `c5e7c94e0b9383c5436332565c2afb78267a77d55ac7c38de2cf37110df36ae4`, `gr2_retrace.o` `1d2e17832e1271e3f33e060c89d3b5a381bd8c8b1766f3b13aa02758c7611b55`, `gr2_tport.o` `7c105ec69a2c857e1ec1f1086bc5e39bc038f1b5376bdecd05b966e43daadd0a`, `gr2_tpucode.o` `b839231a7b74ccb9ca640a114e551cbab595136e5b0ae20048465942364c0b48`. The IP20 `ide` carries the same four diagnostic and console images as the 5.2 `ide.IP20` above (hash-equal as images). The 6.5 and 5.3 microcode differ; [microcode.md](../platforms/express/microcode.md#the-irix-53-images) records how.

How the files were taken from the disc: the disk label's partition 7 (type 5) is EFS (block size 512, superblock magic `0x72959`); a small EFS reader written for the purpose walked it. The `.sw` archives follow the records-in-archive-order scheme the chips page describes: a record's size is the `.idb` entry's `cmpsize`, or `size` when `cmpsize` is `0`, and a `cmpsize` that differs from `size` marks compress-format data (`gzip -dc` reads it). Read that way `eoe1.sw` and `x_eoe.sw` each end exactly at the end of the file. The three hashes of the disc, `eoe1.sw` and `eoe1.idb` equal the ones the chips repository records, so the two extractions agree. Every hash in the sections above (the 6.5 images, the diagnostic program, both PROMs) was re-computed on the working copies before the round: all equal.
