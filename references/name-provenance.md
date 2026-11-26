# Where the sgi-gr2 crate's constant names come from

The Rust crate `rust/sgi-gr2` in the QEMU `sgi-origami` tree (branch `sgi-origami-indigo-gr2-variants`, commit `a37c7ffe0f86`, "tests/qtest: pin the Express board's register contract") carries 471 named constants and statics in `src/`, tests included. This page says, for each prefix family, where a name can be traced to. It covers names only: no value, layout or comment was compared, and a name that matches a source is a possible origin, not proof of derivation. The crate was read, not changed.

Origin classes, as the QEMU pages need them:

- **Shipped developer header**: a name defined in a header the IRIX install discs ship. Citable by header and release.
- **Shipped binary symbol**: a name in a shipped binary's symbol table.
- **Published**: a name in a public document or driver (NetBSD `grtworeg.h` and `grtwo.c` here).
- **Source-only**: a name found only in the IRIX source tree or in the upstream headers `HQ2.h`, `RE3.h` and the rest of the `gr2` repository, which were generated from vendor source ([AGENTS.md](../AGENTS.md)). Not citable from a QEMU page.
- **Crate-own**: found in none of the above.

## What was searched

| Corpus | Contents | Hashes |
|---|---|---|
| IRIX 5.3 install disc, `eoe` product, `usr/include` | `sys/gr2.h`, `sys/gr2_if.h`, `sys/gr2hw.h`, `sys/gr1hw.h`, `sys/lg1hw.h` and the rest of the runtime headers | [binaries.md](binaries.md#irix-53-install-disc-round-9) and below |
| IRIX 6.2 install disc (part 1), `eoe` product, `usr/include` | the same five headers, byte-identical except `gr2.h` and `gr2hw.h` ([binaries.md](binaries.md#irix-62-install-disc-round-10)) | `gr1hw.h` `cce62411fe88e8d7b17ec0f6e6a78d90094a9204ee168d91d3bb67027d038c7f` and `lg1hw.h` `150090a9091397f445c47d01e6fc6d9c2aaea28efc25ea6930bbe348c6564ac8`, equal in 5.3 and 6.2; `gr2.h` and `gr2hw.h` of 5.3 are `52e421a0...` and `ab18cd57...`, of 6.2 `c4d73ee5...` and `03beebf6...` |
| IRIX 6.5 base set and the 6.5.30 overlay, `usr/include` | no `gr2*.h`, `gr1hw.h` or `lg1hw.h` in either; the few matches there are ordinary words | |
| Shipped binaries | the `IP12GR2*` GL cores and IrisGL `libgl.so` of 5.3, 6.2 and 6.5, `IP20boot/gr2.a`, `gfxinit`, `gr2.so` | [binaries.md](binaries.md) |
| NetBSD `sys/arch/sgimips/gio` | `grtworeg.h`, `grtwo.c`, `grtwovar.h` | |
| IRIX source tree 6.5.7 | the graphics diagnostics and PROM library directories | |
| Upstream vendor-derived headers | `GR2.h`, `HQ2.h`, `GE7.h`, `RE3.h`, `VC1.h`, `XMAP5.h`, `VM2.h` in this repository | |

Limits: the 5.3 headers read are those on the install disc; a separate 5.3 developer disc is not held, so a 5.3 name could exist there and not here. Only `.h` text and symbol strings were searched, so a name that appears only as a number in a shipped binary counts as crate-own. A bare word that is also an ordinary identifier elsewhere (`DAC`, `FIFO`, `VC1`, `XMAP`, `ALL`, `OPEN`, `MASK`) is not counted as a match.

## By prefix

| Prefix | Names | Origin | Evidence and notes |
|---|---|---|---|
| `PUC_` | 10 | Shipped developer header | `sys/gr2_if.h` of IRIX 5.3 and 6.2 (the same file in both, `02cc486f...`): `PUC_CMOV2I`, `COLOR`, `DATA`, `DRAWCHAR`, `FINISH`, `INIT`, `LINE2I`, `PNT2I`, `RECTCOPY`, `RECTI2D`. Not in the 6.5 include tree. Eight also appear in the IRIX source's PROM library and all ten in the upstream header. The safest family in the crate |
| `TP_PROBE_ID`, `GR2_BASE` | 2 | Shipped developer header | `sys/gr2_if.h` and `sys/gr2.h` (5.3 and 6.2) |
| `CUR_EP`, `CUR_XL`, `CUR_YL`, `DID_EP`, `VID_EP` | 5 | Shipped developer header | `sys/lg1hw.h` (5.3, 6.2), and `CUR_XL` also in `sys/gr2.h`. `lg1hw.h` is the Entry graphics (LG1) header, which shares the VC1 chip with Express: the names are VC1 registers, the board topology is not the same |
| `AB1`, `CC1` | 2 | Shipped developer header | `sys/gr2hw.h` (5.3, 6.2), bare chip names |
| `DAC_` | 8 | Mixed | `DAC_BLINKMASK`, `DAC_CMD`, `DAC_READMASK`, `DAC_TEST`: shipped developer header `sys/gr1hw.h` (5.3, 6.2), the GR1 board's DAC register names, not Express's. `DAC_ADDR`, `DAC_CTRL`, `DAC_OVERLAY`, `DAC_PALETTE`: crate-own |
| `HQ_` | 26 | Shipped developer header (member names) | 19 are the member names of `struct hq2` in `sys/gr2hw.h` (5.3, 6.2) with the prefix and upper case added: `ATTRJMP`, `VERSION`, `NUMGE`, `FIN1`, `FIN2`, `FIN3`, `DMASYNC`, `FIFO_FULL_TIMEOUT`, `FIFO_EMPTY_TIMEOUT`, `FIFO_FULL`, `FIFO_EMPTY`, `GE7LOADUCODE`, `GEDMA`, `HQ_GEPC`, `GEPC`, `INTR`, `UNSTALL`, `MYSTERY`, `REFRESH`. The other seven are crate-own: `HQ_FIFO_DEPTH`, `HQ_GL_FIN3`, `HQ_PCX_1E0`, `HQ_PCX_1E6`, `HQ_TOKEN_GEDMA`, `HQ_TOKEN_UNSTALL`, `HQ_UCODE_WORDS` |
| `VC1_` | 8 | Shipped developer header (member names), published | `VC1_ADDRHI`, `ADDRLO`, `CMD0`, `SRAM`, `SYSCTL`, `TESTREG` are the member names of `struct vc1` in `sys/gr2hw.h` (5.3, 6.2); all but `CMD0` are also names in NetBSD `grtworeg.h`. `VC1_CMD1` and `VC1_REV` are crate-own |
| `XMAP_` | 8 | Shipped developer header (member names) | `ADDRHI`, `ADDRLO`, `BYTECNT`, `CLUT`, `CRC`, `FIFOSTATUS`, `MISC`, `MODE`: the members of `struct xmap5` in `sys/gr2hw.h` (5.3, 6.2) |
| `HQ2_` | 46 | Source-only (44), published (1), crate-own (1) | 44 are names in the upstream `HQ2.h`: the 2D and X-driver tokens `HQ2_2D_*`, `HQ2_DMA_WRITE_PIXELS` and `HQ2_GL_DMA_*`. No shipped header or binary has them. `HQ2_MYSTERY` is a NetBSD `grtworeg.h` name. `HQ2_REV` is crate-own |
| `T_` | 116 | Mixed: source-only (64), shipped binary symbol (23), crate-own (29) | The 64 are the upstream header's `HQ2_GL_<name>` with the prefix cut (`T_VERTEX` for `HQ2_GL_VERTEX`, `T_COLOR`, `T_RASTER_POS`, ...), and 86 of the 94 token constants in `src/dev/gr2/gl.rs` have the value of an upstream `HQ2_GL_` or `HQ2_2D_` token; many are plain GL concept names (`VERTEX`, `NORMAL`, `MODELVIEW`), so a derivation is likely, not shown. 23 of the 29 `T_IRIS_*` names are public IrisGL function names (`bgnpolygon`, `pmv`, `pdr`, `sboxfi`, `getcpos`, ...) that exist as symbols in the shipped IrisGL `libgl.so` of 5.3 and 6.2. The crate-own 29: `T_BITMAP_HUGE`, `T_BITMAP_TALL`, `T_BLEND_FACTOR`, `T_BLEND_MODE`, `T_CLEAR_CI_DEPTH_I`, `T_DEPTH_CLEAR`, `T_FOG_ON`, `T_IRIS_CHAR16`, `T_IRIS_CHAR16_TALL`, `T_IRIS_CHAR32`, `T_IRIS_GET_COLOR`, `T_IRIS_LCOLOR`, `T_IRIS_SETCPOS`, `T_MATERIAL_COMMIT`, `T_MAT_FIRST`, `T_MAT_LAST`, `T_MODEL_PARAM`, `T_PIX_DATA`, `T_PIX_END`, `T_PIX_RECT`, `T_PIX_START`, `T_SPAN_COLOR`, `T_SPAN_COLOR_B`, `T_SPAN_SETUP`, `T_SPAN_SKIP`, `T_STENCIL_CLEAR`, `T_STENCIL_WMASK`, `T_STIPPLE_OFF`, `T_STIPPLE_ON` |
| `REG_` | 50 | Source-only (46), crate-own (4) | 46 equal the upstream `RE3.h` register mnemonics (`ALIGNPAT`, `AUXMASK`, `FBOPTION`, `UPACMODE`, `PUPDATA`, `XYFRAC`, `ENABDITH`, ...): the suffix is an `RE3_REG_` name there. None is in a shipped header, a shipped binary or NetBSD. The crate-own four: `REG_FILE_LOADED`, `REG_NAMES`, `REG_TABLE_END`, `REG_TABLE_START` |
| `RWMODE_`, `IR_` | 7, 7 | Source-only | The suffixes are `RE3_RWMODE_*` (7) and `RE3_IR_*` (7) names in the upstream `RE3.h`. Nothing shipped has them |
| `RE3_` | 16 | Source-only (2), crate-own (14) | `RE3_OP_ALPHA` and `RE3_OP_BLEND` are names in the upstream `RE3.h`. The rest (`RE3_OP_COPY_A`, `RE3_OP_ZCTL`, `RE3_REGS`, `RE3_SRC_HQ`, ...) are crate-own |
| `GE_` | 8 | Source-only (5), crate-own (3) | `GE_CX_RESTORE_EXT`, `GE_CX_RESTORE_MAIN`, `GE_CX_SAVE_EXT`, `GE_CX_SAVE_MAIN`, `GE_HQMSAV` are names in the upstream `HQ2.h` (the context save and restore tokens). `GE_MAX`, `GE_UCODE_WORDS`, `GE_WINDOW_WORDS` are crate-own |
| `BUS_`, `PD_` | 5 | Source-only (2), crate-own (3) | `BUS_BUSY` and `PD_RGB` are names in the upstream headers; they are ordinary words, so the match is weak. `BUS_ERR`, `BUS_OK` and `PD_BLACKOUT` are crate-own |
| `GR2_` (other) | 2 | Crate-own | `GR2_SLOT_SIZE`, `GR2_STATE_VERSION` |

Crate-own throughout (no match anywhere searched), 55 prefixes and 100 names: `VR_` (12), `PIXFMT_` (5), `SHRAM_` (5), `END_`, `FIFO_`, `GEDMA_`, `GL_`, `MAX_`, `MODE_`, `SRAM_`, `STREAM_`, `TRACE_` (3 each), `CX_`, `FB_`, `PAD_`, `PIECE_`, `PIXEL_`, `READ_`, `SYSCTL_`, `TILE_` (2 each), and one-name prefixes (`BAYER_`, `BITMAP_`, `CLUT_`, `CURSOR_`, `FOG_`, `GEWIN_`, `HQREGS_`, `HQUCODE_`, `LOADUCODE_`, `ZBUF_` and the like), plus 45 constants with no prefix.

## Reading it

Tally of the 471 names: 23 are shipped developer header names by exact match and 33 more (`HQ_`, `VC1_`, `XMAP_`) are upper-cased member names of structs in `sys/gr2hw.h`; 23 are shipped binary symbols (IrisGL function names); 1 is a published name by exact match (`HQ2_MYSTERY`; five `VC1_` names overlap with NetBSD); 177 are source-only; 214 are crate-own, including 45 constants with no prefix. A QEMU page can cite the first three classes. The source-only families, `HQ2_2D_*`, `REG_*`, `RWMODE_*`, `IR_*`, `GE_CX_*` and 64 of the `T_` names, name registers and tokens that only the vendor-derived headers or the IRIX source tree name; a QEMU manual page must not cite them, and the crate's use of them is the question the owner of the crate has to decide. For the token names there is a way out that rests on shipped evidence: the GL cores' own function names (`__glexpim_RasterPos2f`, `PassLineStipple`, `LoadLightPath` and the others in [pipeline.md](../platforms/express/pipeline.md)) name every token the GL cores send, and the IrisGL symbols name the `T_IRIS_*` ones.

Method, for repeating it: an identifier scan of each corpus (upper-case words for the headers and sources, the printable strings of each binary), then the exact-name, member-name and suffix tests described in each row. No tool is committed for it.
