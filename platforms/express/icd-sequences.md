# Express: the command sequences a GL driver must emit, per operation

What the shipped IRIX OpenGL core writes to the Express board for a fresh context, a lit triangle (flat or smooth), a clear, a buffer swap and one image transfer, in the order it writes it, and what the kernel does about the board across a context switch. Written for someone building a driver that has to produce the same stream, or a model that has to accept it. The token catalogue itself is in [pipeline.md](pipeline.md), the flow control and kernel contract in [host-contract.md](host-contract.md), the number formats the board converts to in [arithmetic.md](arithmetic.md) and the microcode behind each slot in [microcode.md](microcode.md).

## Sources and grades

- **GL core.** `usr/gfx/arch/IP12GR232/libGLcore.so` of the IRIX 6.5 base set (n32, SHA-256 `8dd07de07edd28b6fa0680e72026ba34847bb488f0ccbab1b0cc045c5e6fc741`, DWARF kept). Addresses below are its virtual addresses. The committed listing under `libglcore/asm/EXPRESS` and the m2c output under `libglcore/decomp/EXPRESS` are from this file: the function addresses and the instruction words checked here (`MakeCurrent`, `SwapBuffers`, `Finish`, `GetBoardInfo` and the slot sequences of the state, lighting, clear and pixel routines) agree with it. Both listings misname calls made through an offset from a global-table entry (`addiu t9` after a table load shows as the nearest symbol, and m2c drops some of them), so every call target below was read from the machine code, and the store counts were taken with [tools/gl-fifo-stores.py](../../tools/gl-fifo-stores.py) over the same file.
- **Kernel.** `gr2.o` and `gr2_retrace.o` of the committed IP12 disassembly (`gr2_kernel/disasm`), offsets are `.text` offsets in those objects; the IP20 archive readings in [host-contract.md](host-contract.md) agree on every slot number used here. `rrm.o` and `gfx.o` are not read; their roles come from the shipped headers `sys/gfx.h` and `sys/rrm.h` (the board function table and the `RRM_*` request numbers).
- **Microcode pair.** The 6.5 `hq2.bin` and `ge7.bin`. The 5.3 and 6.2 images take different operand counts for some slots ([pipeline.md](pipeline.md#slot-261-the-raster-position-token)); do not mix a core with another release's images.

Grades as in [AGENTS.md](../../AGENTS.md): **established** is a store, call or constant read at the address given; **inferred** is a role or an order reasoned from the code; **unknown** says what would settle it. Everything is what software sends. Nothing here is a hardware measurement.

Notation. Offsets are relative to the board window; the FIFO is `+0x40000` to `+0x5ffff`. `[+0x42018] <- 0` is one 32-bit store. `[+0x48608] <- r, g, b` is three consecutive stores to the same address (what the immediate-mode entry points do for a colour, normal or vertex). `D` is the data port `+0x4277c` (slot 479). The core addresses the window with absolute low addresses (`lui 4; ori 0x2018`, base register zero), so the process has the board mapped at virtual address 0 (established); that the kernel's `Gr2MapGfx` does it is inferred.

## 1. A fresh context

### 1.1 Create

`__glExpCreateContext` (0x0da59ebc) allocates the 0x7c98-byte context with the import table's allocator, shares lists and calls `__glEarlyInitContext`. It stores nothing to the window (established: `li a2,31896` at the allocator call; no tracked store in the routine). A driver that has no board work to do at creation matches it.

### 1.2 First make-current

`MakeCurrent` (0x0da59a38, 1156 bytes) is the whole set-up. The context's `gcState` word (offset 0x94) has bit 0 clear until the hardware context exists and bit 1 clear until its buffers do; the routine sets both at the end. Order for a context whose `gcState` is 0:

| # | What it does | Address | Grade |
|---|---|---|---|
| 1 | Calls import +0x38 (the window query). Non-zero means a pixmap context: it calls `__glPixmapMakeCurrent` and returns; nothing below runs | 0x0da59a60, 0x0da59d00 | established |
| 2 | Copies two 257-entry dispatch tables into the context; begin-mode word := 2; dirty mask \|= 0x80 | 0x0da59a74 to 0x0da59afc | established |
| 3 | Stores 0x2000 at context +0x7c90; calls import +0x28 with it, then import +0x2c, whose result is the graphics descriptor, kept at +0x7b10 and +0x7b14. A negative result frees the context through import +0x0c and returns 0 | 0x0da59c78 to 0x0da59ca8, 0x0da59e8c | established; what the imports are: unknown |
| 4 | `GetBoardInfo`: first calls import +0x20 (its result is the first word of the request), then `ioctl(fd, 0x66, {that word, pointer to reply, 0x3c})`; 0x66 is `GFX_GETBOARDINFO` (`GFX_BASE` 100 + 2 in `sys/gfx.h`). From the reply the core builds the renderer string and decides the Z and stencil bits the board can hold | 0x0da58604, called at 0x0da59cb4 | established (request, record); the reply layout: inferred |
| 5 | Import +0x28 again with 0x2000, then import +0x34; its result refreshes +0x7b10. This pair runs on every make-current, not only the first | 0x0da59b04 to 0x0da59b20 | established |
| 6 | `[+0x42398] <- 0`; `[+0x42010] <- pixel-mode value` from `GetPixModeValue`; `[+0x42080] <- 0`; `[+0x42038] <- stencil bits` (0 when the context has no board stencil) | 0x0da59de0 to 0x0da59e2c; `GetPixModeValue` 0x0da588a4 | established. Pixel-mode value: RGB visual whose component bits sum to 24 gives 4, 12 gives 2, 8 gives 1, any other sum 0; colour-index width 12 gives 0xa, 8 gives 9, 4 gives 8, 2 gives 0xb. Roles of slots 230, 4, 32, 14: inferred ([pipeline.md](pipeline.md) lists them as the "MakeCurrent" slots; slot 4 selects the GE7 colour scale, [arithmetic.md](arithmetic.md#quantisation-and-colour-scale)) |
| 7 | `InitBuffers`: builds the colour, depth and stencil buffer method tables; no store to the window | 0x0da59844 | established |
| 8 | `__glMakeCurrentBuffers` (it leaves the displayed-buffer index at context +0x7b48), then `[+0x42018] <- 0` and `[+0x4279c] <- that index` | 0x0da59b3c to 0x0da59b60 | established; the pair's meaning: unknown (slot 6 is also what `Flush` writes, slot 487 is what a swap writes) |
| 9 | `InitFnPtrs`: installs the immediate-mode, display-list and picking procedure tables; no store to the window | 0x0da5958c | established |
| 10 | `__glFindWindowSize`, then `__glExpUpdateViewport`: `[+0x420ec] <- 1.0f`; `D <- x, x+w-1, y, y+h-1, zScale, zCenter` (floats; viewport rectangle and the depth-range scale and centre) | 0x0da589f0 | established stores; word roles: inferred |
| 11 | `__glExpPassMachineState`: `[+0x4a608] <- r, g, b, a` (RGB; colour index sends `[+0x4e3f8] <- index`); `[+0x42434] <- nx, ny, nz`; `[+0x42414] <- valid flag`, then `D <-` window x, y, z, eye z, clip w, and four colour floats each multiplied by 0.99609375 (255/256); `[+0x423d8] <- edge flag` | 0x0da5912c, 0x0da65070 | established |
| 12 | `__glExpInitPrimDispatchState` (no store); `__glExpInitLighting`: `[+0x42214] <- 7.0f, 1.0f`, then `<- 2.0f, 0.0f` (RGB; colour index adds the material block first), then `__glExpUpdateLightingState`: `[+0x42200] <- 4.0f, -1.0f, 10.0f, 0.0f` and the two full material blocks (section 2.2), then `__glExpValidateColorMaterial`: `[+0x42204] <- 0, 0, 0` | 0x0da60764, 0x0da5f37c, 0x0da5f1c0, 0x0da5ed44 | established stores; meaning of the (code, argument) float pairs: unknown |
| 13 | `__glExpInitPixelState` (no store the tracking finds), then the context's validate procedure (offset 0x2e10, the generic validator), which reaches `__glExpPickAllProcs` (installed at +0x2e64 by `InitFnPtrs`); that calls `__glExpValidateLighting` when the lighting dirty bits (0x21) are set | 0x0da645e8, 0x0da61800, 0x0da59e6c | established that each is called; the generic validator was not read, so the chain between them is inferred |
| 14 | `__glContextSetColorScales`, `__glExpLoadPrimDispatchVectors` (software) | 0x0da59ba8 | established |
| 15 | If the context's hardware-state flag (+0x7b4c) is 0: `__glExpUpdateHardwareState`, the full state send of section 2.1, which sets the flag to 1 | 0x0da58f08 | established |
| 16 | `gcState := (gcState \| 3) & ~4` | 0x0da59c28 | established |

Before step 1 the board has to be running: the PROM or kernel console images replaced by the full pair, `GFX_START` done ([host-contract.md](host-contract.md#13-what-a-driver-loads-in-order-and-who-loads-what), steps 5 to 8). Nothing in the core writes the microstore, the HQ2 registers or the RE3 registers (established, [pipeline.md](pipeline.md)); the only host-visible register the core touches outside the FIFO is the read-back status `+0x6c040` and its acknowledge `+0x6d000` (sections 4 to 6).

A second make-current of a context that already has `gcState` 3 skips steps 2 to 4, 6, 7, 9, 11 to 13 and 15. It repeats step 5, then `[+0x42018] <- 0`, `[+0x4279c] <- displayed-buffer index` and the viewport block of step 10 (established, 0x0da59b24 to 0x0da59b98 and the branch at 0x0da59bbc). So a context switch inside one process resends the buffer selection and the viewport and nothing else.

## 2. State for a lit, flat or smooth triangle

### 2.1 What the full send contains

`__glExpUpdateHardwareState` (0x0da58f08, 548 bytes) calls these in this order. The counts are stores through the token address (the tool's per-command word count); "inferred" for what each controls.

| Routine | Stores | Grade |
|---|---|---|
| `PassDrawBuffer`: `SetPixWritemask`, `SetReadSource` | with aux buffers `[+0x4200c] <- mask; [+0x4242c] <- 0, 0`, otherwise `[+0x4200c] <- 0; [+0x4242c] <- front mask, back mask`; `[+0x42428] <- 4 words` | established; mask packing for 4, 8, 12, 16 and 24-bit colour is in `SetPixWritemask` (0x0da58b58) |
| `EnableDither` | `[+0x42044] <- 0 or 1` | established; role inferred |
| `PassBlendFunc`, `EnableBlendFunc`, `PassLogicOp`, `EnableLogicOp` | `[+0x42098] <- mode; [+0x42094] <- 3 words`; `[+0x42068] <- logic op` (3, copy, when off) | established count; factor codes: unknown ([arithmetic.md](arithmetic.md#mode-word-fields)) |
| `PassColorMask`, `PassIndexMask` | `SetPixWritemask` again | established |
| `PassColor`, `PassIndex`, `PassNormal`, `PassRasterPosData`, `PassEdgeFlag` | the same words as step 11 of section 1.2 | established |
| `PassDepthFunc`, `PassDepthMask`, `EnableDepthTest` | `[+0x42090] <- func & 7`; `[+0x42028] <- depth mask or 0`; `[+0x42050] <- 1 or 0` (1 only with a board Z buffer and the test enabled), then the mask word again | established |
| `EnableFog`, `PassFog` | `[+0x4209c] <- 0 or 1`; `[+0x420a0] <-` 18 words | established count; layout: unknown |
| `PassShadeModel` | `[+0x4204c] <- 1` (smooth) or `0` (flat) | established |
| `UpdateLightingState` | `[+0x42200] <- 4.0f, -1.0f, 10.0f, 0.0f`, then both material blocks (2.2) and the colour-material word | established |
| `PassLineWidth`, `PassLineStipple`, `EnableLineStipple`, `EnableLineSmooth`, `EnablePointSmooth` | slots 23, 22 and 24, 34, 33 | established |
| `PassCullFace`, `EnableCullFace`, `PassFrontFace`, `EnablePolygonStipple`, `PassPolygonMode`, `PassPolygonOffset` | `[+0x4206c] <- front cull, [+0x42070] <- back cull`; `[+0x42420] <- 1 (CCW) or 0`; `[+0x42078] <- 0` or the stipple at `+0x4207c`; `[+0x42388] <- 1 fill, 2 point, 3 line`; `[+0x42390] <- factor, units * depth scale` (both 0.0f when off) | established |
| two indirect calls through the context, at +0x3178 (after `PassPolygonOffset`) and +0x2e8c (before `PassStencilMode`) | not resolved | unknown |
| `PassStencilMode`, `EnableStencilTest`, `PassStencilMask` | slots 15, 15, 16 (8, 7 and 2 words) | established count |
| `UpdateMatrixState` | `[+0x420dc] <-` 16 modelview floats, `[+0x420e0] <-` 16 projection floats, `[+0x420e8] <-` 16 texture floats | established |
| `EnableClipPlanes`, `PassClipPlanes`, `EnableNormalize` | `[+0x420b8] <- 2 words`, `[+0x420bc] <- 5 words` per plane; `[+0x4238c] <- 0 or 1` and `[+0x42208] <- 0 or 1` | established |
| one more indirect call through the context at +0x2e90, then the hardware-state flag := 1 | not resolved | unknown |

`UpdateMatrixState` does not send the normal matrix (`+0x420e4`, nine floats); only `__glExpPassMatrix` does, when the modelview matrix changes (section 2.3). Whether a fresh context needs it before its first lit primitive, or the microcode derives it, is unknown.

### 2.2 Lighting and material

`__glExpValidateMaterial` (0x0da5e990), RGB mode, one block per face and only for the property bits asked for (the first call after creation asks for all six):

| Property | Front | Back |
|---|---|---|
| emission | `[+0x421d8] <- r, g, b` | `[+0x421dc] <- r, g, b` |
| ambient | `[+0x421e0] <- r, g, b` | `[+0x421e4] <- r, g, b` |
| diffuse | `[+0x421e8] <- r, g, b, a` | `[+0x421ec] <- r, g, b, a` |
| specular | `[+0x421f0] <- r, g, b` | `[+0x421f4] <- r, g, b` |

then `[+0x4220c] <- 0.0f`. A specular exponent change builds a lookup table in memory and loads it (`__glExpCreateSpecLUT`, `__glExpLoadSpecLUT`, slot 116); the table layout is not read here. Colour index mode sends three (code, value) pairs to `[+0x42200]` (codes 18, 19, 20 front, 21, 22, 23 back) instead. `__glExpValidateColorMaterial` (0x0da5ed44) sends `[+0x42204] <- parameter code (1 emission, 2 ambient, 3 diffuse, 4 specular, 5 ambient and diffuse), face (0 front, 1 back, 2 both), 1` when colour material is on, and `0, 0, 0` otherwise. All established.

`__glExpValidateLighting` (0x0da5ee94) runs from the pick routine when lighting state is dirty. It sends `[+0x42200] <-` (code, argument) float pairs with codes 5.0 and 6.0 per enabled light (the light number, or -1.0) and closes with (4.0, first enabled light) and (10.0, number of enabled lights); it calls `__glExpLoadLightSource` (0x0da5e5d4, from 0x0da5efc8 and 0x0da5f130) and `__glExpLoadLightPath` (0x0da5e460, from 0x0da5f100 and 0x0da5f310). The pairs were read in m2c output and the calls at call-site level, so the interleaving between the pairs and the two loaders is inferred.

- `LoadLightSource`: `[+0x42200] <- 5.0f, n`; `[+0x42394] <- ambient r, g, b`; `[+0x42404] <- diffuse r, g, b`; `[+0x42408] <- specular r, g, b`; `[+0x421fc] <- position x, y, z, w` (eye space, divided by w for a positional light; a directional light sends the transformed direction and w = 0); for a spot light, once its cut-off and exponent lookup table exists, `[+0x42210] <- direction x, y, z`, and `[+0x42200] <- 31.0f, -1.0f` for a light that is not a spot; always `[+0x42424] <- linear, quadratic, constant attenuation`.
- `LoadLightPath`: when lighting is on, `[+0x42438] <- 0.0f; D <- 1`, `[+0x42350] <- 1.0f; D <- two-sided flag`, then (step code, argument) pairs to `[+0x42214]`: `6.0f, local viewer`, then one of three fixed sequences chosen by whether any enabled light is positional, whether a local viewer or two-sided lighting is on, and the light count (the `3.0f/4.0f/5.0f` pairs), and `[+0x4220c] <- 0.0f`. With lighting off it sends `[+0x42438] <- 0.0f; D <- 0` and `[+0x42350] <- 1.0f; D <- 0` only.
- `LoadAmbientSum`: `[+0x421d4] <- scene ambient r, g, b`, plus the enabled lights' ambient when there is no positional light, no local viewer and no two-sided lighting.

Established: the addresses and the stores. Unknown: what the pair codes (3.0 to 10.0, 18 to 23, 31) select.

A spot light, once per context, also asks the kernel for a 0x400-byte saved-state buffer: `ioctl(fd, 0x3aa7, {4})` at 0x0da5e930 (`Gr2AllocCXData`, section 7). Established.

### 2.3 What a lit triangle changes after that

| GL call | Sent | Where | Grade |
|---|---|---|---|
| `glShadeModel(GL_SMOOTH or GL_FLAT)` | `[+0x4204c] <- 1 or 0`; the arithmetic note puts the flat flag in RE3 mode word `0x63` bit 15 | `__glExpPassShadeModel` 0x0da671c4 | established; effect: inferred |
| `glEnable/glDisable(GL_LIGHTING)`, `glEnable(GL_LIGHTn)`, `glLight*` | no store from the enable routine (`__glExpEnableLighting` only frees lookup tables); the next validate sends 2.2 | 0x0da61800 | established for the enable routine, inferred for the rest |
| `glMaterial*`, `glColorMaterial` | `ValidateMaterial` for the changed property bits and `ValidateColorMaterial` | 0x0da5e990 | established |
| `glLightModel*` | `LoadLightPath` and `LoadAmbientSum` | 0x0da5e460 | inferred (call sites) |
| `glMatrixMode`, `glLoadMatrix`, `glMultMatrix`, `glTranslate`, `glRotate`, `glScale`, `glFrustum`, `glOrtho` | `__glExpPassMatrix` (0x0da6c064): modelview `[+0x420dc] <-` 16, then (after recomputing the inverse transpose if stale) `[+0x420e4] <-` 9 floats; projection `[+0x420e0] <-` 16 floats and, with clip planes on, the clip planes again; texture `[+0x420e8] <-` 16 | | established |
| `glViewport`, `glDepthRange`, `glScissor` | the viewport block of 1.2 step 10; scissor `[+0x420f0] <- x0; D <- y0, x1, y1` (0 to 0x7ff when off) | 0x0da589f0, 0x0da58af0 | established |
| `glEnable(GL_NORMALIZE)` | `[+0x4238c], [+0x42208] <- 1` | 0x0da6be7c | established |
| depth test, cull, polygon mode, blend | the routines of 2.1 | | established |

### 2.4 The primitive

`glBegin(GL_TRIANGLES)` (`__glexpim_Begin` 0x0da64f48 selects the begin procedure from the mode) runs `__glExpBeginTriangles` (0x0da64e58): `[+0x423c0] <- 0; [+0x433c8] <- 0`. Each vertex is the application's own attributes in whatever order it gives them, one entry point each:

| Entry | Stores | Address |
|---|---|---|
| `glNormal3f` | `[+0x42434] <- nx, ny, nz` | `__glexpim_Normal3f` 0x0da6bb78 |
| `glColor3f` | `[+0x48608] <- r, g, b` (`Color4f`: `[+0x4a608] <- r, g, b, a`; `Color3ub` forms use `+0x58608`, `+0x5a608` with integer 0 to 255 words) | 0x0da6b2c4 |
| `glVertex3f` | `[+0x4498c] <- x, y, z` (`Vertex4f` `+0x4298c`, `Vertex2f` `+0x4698c`; integer forms add bit 16: `+0x5498c`) | 0x0da6b954 |

`glEnd` runs `__glExpEndTriangles` (0x0da64e28): `[+0x423c4] <- 0; [+0x43194] <- 0`. Flat and smooth shading send the same primitive words; the difference is the single shade-model word. All established, and the vertex path is the one the arithmetic notes describe ([pipeline.md](pipeline.md#fifo-token-encoding)). The GL core can also take a software path (`mips_*` routines: transform, light and clip on the host and send device coordinates) when the pick routine finds a state the board cannot draw; that stream was not catalogued.

## 3. Clear

`__glexpim_Clear` (0x0da582d8) rejects bits outside 0x4700 (`GL_INVALID_VALUE`) and calls inside `glBegin` (`GL_INVALID_OPERATION`), then, for the current buffer methods, in this order:

1. Colour, or colour and depth together when both bits are set and depth writes are on (`CZClear`, 0x0da67b34): 
   - colour alone, RGB (`Clear` 0x0da67a8c): `[+0x42044] <- 0` first when dither is on and the clear colour is exactly representable, then `[+0x42410] <- r; D <- g, b, a`, then `[+0x42044] <- 1`;
   - colour and depth (`CZClear`): the same dither bracket around `[+0x42280] <- r; D <- g, b, 0, scaled depth, 0xffffffff`.
2. Accumulation, when the context has one (a call through the buffer's own procedure; not resolved).
3. Stencil (`Clear` 0x0da6adbc): `[+0x42284] <- value; D <- second word`.
4. Depth alone (`Clear` 0x0da5a578): `[+0x42044] <- 0` when dither is on, `[+0x5c280] <- 0; D <- clear depth scaled by the depth range, 0`, then `[+0x42044] <- 1`.

Colour index uses the `+0xe410` forms (`[+0x4e410]`, `[+0x5e280]`). All established from the routines' stores; the meaning of the dither bracket (the board must not dither a clear) is inferred. There is no completion wait: the clear is ordered by the FIFO.

## 4. Swap, flush and finish

`SwapBuffers` (0x0da5920c), double-buffered visuals only:

1. Exchange the context's front and back buffer pointers, make the buffer that is now the back one the draw buffer, and flip the displayed-buffer index (`1 - index`, stored at +0x7b48).
2. `[+0x4228c] <- 0` (the finish/read-back token, slot 163).
3. Spin until bit 0 of `+0x6c040` is set (a ten-iteration delay loop between reads, no timeout), then `[+0x6d000] <- 0` (acknowledge).
4. `[+0x42018] <- 0`; `[+0x4279c] <- new displayed-buffer index`.
5. Set or clear bit 2 of the context flag word (+0x7b40) to match the index, then `ioctl(fd, 1005, {board index, index, flags})`. 1005 is `RRM_SWAPBUF` (`RRM_BASE` 1000 + 5 in `sys/rrm.h`). A failure calls the import error procedure.

`Finish` (0x0da59370) is steps 2 and 3 only. `Flush` (0x0da593e8) is `[+0x42018] <- 0`. All established.

The kernel half: `rrm.o` (not read) turns the request into the board function table's `gf_SchedSwapBuf` entry, `Gr2SchedSwapBuf` (`gr2_retrace.o` `.text` 0xf50; entry in the board table at `gr2.o` `.data` 0x5b3c). It checks the window ID (0 to 31), refuses a window with a swap already pending (message, error 16), records the swap interval (at least 1), the buffer and the request in the window's 0x18-byte slot of the VC1 shadow, and counts it pending. Then at each retrace interrupt `Gr2RetraceHandler` walks the 32 slots: it polls a status word for the retrace edge (ten 1 us tries), waits for `+0x6c11c` bit 0 to clear, saves the XMAP5 index registers (`+0x6c110`, `+0x6c114`), and for each slot whose interval has run out writes `[+0x6c1b4] <- 0; [+0x6c1b0] <- window ID * 4; [+0x6c1a4] <- new mode word` (`gr2_retrace.o` `.text` 0xa38 to 0xb34), validates the buffer back to the resource manager and clears the slot; slots with time left count down. So on Express the visible flip is an XMAP5 mode-table write made by the kernel at retrace; the GL core's `+0x4279c` and `+0x42018` stores tell the microcode which half the next drawing goes to. Established for the sequence in the objects read; the XMAP5 mode word layout is unknown ([devices/xmap5](../../devices/xmap5/README.md) holds what is known); how `rrm.o` reaches `Gr2SchedSwapBuf` is inferred from the header's function table.

## 5. One image transfer

### 5.1 `glDrawPixels` by FIFO words

`__glExpDrawPixelsUnpack4` (0x0da62620, 32-bit pixels; `Unpack1` 0x0da628a0 for the packed forms) for an RGBA image:

1. `[+0x422ec] <- 0.0f, x zoom magnitude, 1.0f` (three stores; a negative x step is made positive here and shows as the direction word of step 2; the y zoom is done by sending each row that many times).
2. For each strip of up to 48 pixels across: `[+0x422c4] <- 0` (strip start); then for each row of the strip, and for each repeat the y zoom asks for: the row's pixels through `__glExpCopyToPipe4` (0x0da61878: `[+0x421c4] <- word 0; D <- words 1 to 15`, repeated in 16-word groups) or `__glExpSwapToPipe4` (0x0db24268, slot 113 as well) for the byte-swapped format 0x1908; then `[+0x422c8] <- x; D <- y, width, width, direction flag`; then `[+0x422cc] <- 0` (row end).

Established stores and loop shape (the m2c reading of the loops is partial; the tool counts one command each of slot 187 (3 words), 177 (1), 178 (5) and 179 (1) in the routine). The meaning of the two widths and the direction word: inferred.

### 5.2 `glDrawPixels` by DMA

`__glExpDrawPixelsKDMA` (0x0da62b88): `[+0x422f0] <- 1`; `[+0x422ec] <- 0.0f, x zoom magnitude, y zoom magnitude`; then, in chunks of at most 0x20000 bytes (rows times the row pitch), `ioctl(fd, 0x3aa2, args)` where args is the 0x2c-byte record the kernel's private-request switch (`Gr2Private`, then `Gr2PixelDma` in `gr2_dma.o`) copies in. The kernel queues the board command (slot number 181 or 184, 0xb5 or 0xb8, in the first word of the record) with `fin2` cleared and `dmasync` 2, then runs the MC graphics DMA to the `gedma` port and waits for finish flag 2 ([host-contract.md](host-contract.md#3-pixel-dma-gr2_dmao)). Established for the request, sizes and slot constants; the argument words' meaning is unknown, as in the host contract.

### 5.3 Read-back

`__glExpReadPixelsPack1` (0x0da62e44): `[+0x422f0] <- 0`; `[+0x422ec] <- 0.0f, 1.0f, 1.0f`; per block of rows: `[+0x422b4] <- origin x; D <-` six more words (origin y, source width, row count, words per row, two zeros; order read from m2c output, roles inferred); spin on `+0x6c040` bit 0; read the rows from shared RAM at `+0x12088`; `[+0x6d000] <- 0`; `[+0x422f4] <- 0`. The KDMA read (`__glExpReadPixelsKDMA` 0x0da63040) uses the same ioctl. Established.

## 6. What the board expects across a context switch

### 6.1 In the GL core

`LoseCurrent` (0x0da59508) stores nothing to the window. It returns early without detaching when the context is not in `GL_RENDER` mode or is inside `glBegin`; otherwise it calls `__glLoseCurrentBuffers`, saves the begin-mode word and clears the current-context pointer. The core therefore never saves or restores board state itself; the next `MakeCurrent` resends only 1.2 step 5, the buffer pair and the viewport (established). A driver that makes two contexts current in turn on one board must rely on the board's own saved context, not resend.

### 6.2 In the kernel

The kernel never copies board state. It queues dump and load commands and DMAs the result with the MC. Facts below are from `Gr2PcxSwap` (`gr2.o` `.text` 0x275c to about 0x3200) and `_Gr2CXSaveRestore` (0x253c); host-contract section 2 holds the IP20 reading and the token numbers.

1. A render node (`Gr2CreateDDRN`) gets a 0x74-byte record with the context type and size class (0 or 2, from the node's group; the size class changes through private request 0x3aa3, `Gr2ChangeCXSize`, which invalidates the node's mapping). Extra save buffers are added with private request 0x3aa7 (`Gr2AllocCXData`): bit 1 of the mask gives a 0x12c0-byte buffer, bit 2 a 0x400-byte one, bit 3 another 0x400. The one sender in the GL core is the spot-light path of 2.2 (mask 4).
2. Switch: take the graphics lock (`gfx_waitc_on`); save the outgoing context: its finish-flag bit (status bit 0) into its record, then for each valid buffer (record flags, bits 0 to 3) `_Gr2CXSaveRestore` with token 483 and the buffer number: `dmasync` := 2, `fin2` := 0, token, DMA board to memory, wait for status bit 1 (1,000,000 us limit; failure prints a timeout and calls `gr2_error`).
3. Load the incoming context: `fin2` := 0; `[+0x407c0] <- render-node index`; `D <- context type, size class`; wait for status bit 1 (`.text` 0x27e8 to 0x2800); per valid buffer token 484 and the DMA the other way; then the per-window set-up when the window changed: `[+0x40794] <-` window box, `D <-` the clip rectangle words, `[+0x40780] <-` flag, `[+0x40798] <-` flag; and a store to `+0x40004` (slot 1) at `.text` 0x30b8, at the exit of the clip-rectangle loop, value not tracked (the IP20 objects in [pipeline.md](pipeline.md) show no sender for slot 1; this IP12 object does).
4. Restore the saved finish-flag bit to `finish3`; drop the lock.

What the board must provide for this: the microcode implements tokens 481 to 484 and 496 and raises finish flag 2 after each; it publishes the buffer sizes in shared RAM (word 770 at `+0xc08` and the words at `+0xc0c`, `+0xc10`), because the kernel sizes its allocations from them ([host-contract.md](host-contract.md#2-context-save-and-swap-_gr2cxsaverestore-gr2pcxswap)). A model that executes no microcode can treat the saved data as opaque, as host-contract says.

## 7. Unknowns, and what would settle each

| Unknown | What would settle it |
|---|---|
| What the import slots at context +0x20, +0x28, +0x2c, +0x34 and +0x38 are (the window query, the 0x2000 argument, the descriptor and board-index source, the first word of the board-info request) | read the code in `libGL.so` (`IP12GR232`) that fills the context's import table before `__glExpCreateContext` is called |
| Meaning of the (code, argument) float pairs sent to `+0x42200` and `+0x42214` (codes 2 to 10, 18 to 23, 31) | step the GE7 routines at 15694 (slot 128) and 16145 (slot 133) with `tools/ge7-step.py` and read which register each code selects |
| What slots 230 (`+0x42398`), 4, 32, 6 and 487 do beyond the scale and buffer-selection reading | the same stepper on GE7 206, 1628, 1669, 2797 and 13406; a capture of the RE3 writes each causes |
| What `+0x4228c`, `+0x6c040` bit 0 and `+0x6d000` are in the HQ2 | the HQ2 sequencer control operands, [questions/re3.md](../../questions/re3.md) |
| Whether a fresh context needs the normal matrix (`+0x420e4`) before its first lit primitive | step GE7 355 to 502 with a zero normal-matrix store and see whether lighting output changes |
| The three indirect calls in `UpdateHardwareState` (context offsets +0x3178, +0x2e8c and +0x2e90) | read the context's procedure table as `InitFnPtrs` (0x0da5958c) fills it |
| Order of the `+0x42200` pairs and the two loaders inside `__glExpValidateLighting` | read the 0x0da5ee94 to 0x0da5f340 listing instruction by instruction (calls were located, interleaving was not) |
| The XMAP5 mode-word layout written at retrace, and what `rrm.o` does between the ioctl and `Gr2SchedSwapBuf` | read `rrm.o` (`RRM_SWAPBUF` handler) and `devices/xmap5` against the 6.5 X driver's mode-table writes |
| The slot 1 store in `Gr2PcxSwap` (IP12 object) | read the IP20 6.5 `gr2.a` member at the same place; trace the register's source at `.text` 0x301c |
| Software-transform stream (`mips_*` routines) | not catalogued; read those routines with the same tool |
| Argument words of the DMA board command (origin, size) | decode GE7 26475 to 27323 with the stepper ([microcode.md](microcode.md#the-pixel-dma-routines-as-known-answers)) |

## Other heads

The same questions for the two heads this repository does not cover are answered in the sibling repositories; read them there rather than from this page.

- VPro (Odyssey): the odsy repository, `devices/buzz/fresh-context.md` (what the kernel replays at a first switch-in, the save record and the complete validate order) and `devices/buzz/state-sequences.md` (the command words each GL state feature sends), at commit `ed2b34b`.
- InfiniteReality (KONA): the kona repository, `platforms/ir/x-tokens-and-gl-contexts.md` (what happens when an X token arrives while a GL context is current, and across a switch between two GL contexts) and `software/opengl/gl-token-catalogue.md` (the tokens for the entry points the command map left located, in the order a first textured, lit triangle and `glFinish` need them), at commit `7c873b5`.

## Reproducing the counts

```
uv run --script tools/gl-fifo-stores.py root/usr/gfx/arch/IP12GR232/libGLcore.so PROCS 64
```

with `PROCS` one `address<TAB>name` line per function built from the committed listings' `# Address:` headers. The tool groups stores to one token address into one command, in code order, which is not always execution order: the orders above come from reading the routines.
