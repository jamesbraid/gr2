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
| `usr/gfx/arch/IP12GR2/libGLcore.so` | `db8d0331ff6c657ab3e1dc60279741ff4ab00a6c11235c5d0df494ae26e13487` | GL core, o32 build, for GR2 on the R3000/R4000 Indigo. Not read. |
| `usr/gfx/arch/IP12GR232/libGLcore.so` | `b6731da1b4422e1ea1e8fbe841af2e05989d4c3022d9c8b8143a53187f67de9a` | GL core, n32 build; the FIFO token addresses in the pipeline page are read from it. |
| `usr/gfx/arch/IP12GR2*/libGL.so`, `libgl.so` | see media inventory | GL and IrisGL clients. Not read. |

Extracted `gr2.a` members (SHA-256):

- `gr2.o` `e03854933506abf8204706da353b90ae794f98a3e82e4820952cf50e9242ecae`
- `gr2_dma.o` `0bdc863a55232f72d9dc8e923baa46e5e9da7044df14a22c9b345b348da15e4a`
- `gr2_init.o` `73c4986fdefa9258801962079402ecd74f188358b80c43fd7ba8a759268447fe`
- `gr2_retrace.o` `5d698d07d380afb82f1ac334b6637d15995b7a65b1177f899b89d122f4d3beb8`
- `gr2_tport.o` `fe25685c26aada022361083655d8d29683d781c4344aadf971dc5fea86c143e6`
- `gr2_tpucode.o` `f77f0399144444240211430708450a556ef67644d4c3beabc220e575315ea211`

The upstream `root/...` symlinks name an IP12 build of these objects (it also lists a `gr2_corona_i2c.o`). They are not the IP20boot objects above; whether the shared members are byte-identical is not checked.

PROMs that probe the board: Indigo R4000 `070-8116-004` (4.0.5D) and `070-8116-005` (4.0.5G); the probe is described in the chips repository's `platforms/ip20/gio.md`.
