# SGI GR2 (Express, Elan, XS, XS24, XZ) reverse engineering

This workspace reverse-engineers the SGI GR2 graphics family, sold as Express, Elan, XS, XS24 and XZ graphics on the Indigo (IP20 R4000 first, IP12 R3000 later) and in related Indigo2 configurations. The result is published as register maps, generated headers and chapters, so that emulator authors, FPGA builders and the vintage SGI community can work from findings instead of binaries.

The layout and working style follow [gr4](https://github.com/techomancer/gr4) and the sibling workspaces newport, kona and odsy. Where this file is silent, do what gr4 does.

## Branches and the upstream files

`main` is techomancer's repository and is never pushed from here. Our work is on `origami-re`; the public mirror publishes from it. Everything in the upstream commit stays where it is. The upstream headers (`GR2.h`, `HQ2.h`, `GE7.h`, `RE3.h`, `VC1.h`, `XMAP5.h`, `VM2.h`) and the notes under `docs/sgimips_grtwo_graphics.*` are machine-generated, and the headers were generated from vendor source. Treat them as notes from another project: they may confirm or contradict a finding, they never supply one, and no text is copied from them. A fact that rests only on them stays unknown, with the note named. Upstream's own original instructions are kept unchanged at the end of this file.

## Scope

- **Boards**: the Indigo graphics slot only at first; [the survey](platforms/express/README.md) lists the variants and what is known about each. Indigo2 configurations (XZ, Elan, Extreme) are context: each board revision and host is its own configuration, and a fact from one does not fill a gap in another.
- **Chips**: HQ2 (command engine, FIFO, microcode sequencer), GE7 (geometry), RE3 (raster), VC1 (video timing, cursor, display IDs), XMAP5 (window and colour mapper), the Bt457 and Bt479 colour DACs, and the VM2 video memory and Z buffer boards. Block names are the names software and published documents use; a role stays unknown until a labelled description replaces it.
- **Host-visible first**: what the PROM and the IRIX kernel touch through the GIO window, then what the microcode does behind it.

Every fact is labelled **established** (read in full from a binary, a published document or a public driver, with object, function, address or page), **inferred** (a reasoned reading, with the reasoning) or **unknown**. Anything unlabelled is unknown. Do not fill gaps from memory, from other SGI graphics families or from other reimplementations.

## Binaries

Proprietary SGI binaries are not committed (`root/` is gitignored; the upstream tree's `root/...` symlinks dangle until you fill it). [references/binaries.md](references/binaries.md) lists what this work reads, with checksums. Disassembly, decompiled C, headers and notes derived from the binaries are committed. Flat `*_disasm.txt` and `*_dwarfdump.txt` dumps are gitignored.

## Other public sources

- NetBSD `sys/arch/sgimips/gio/grtwo.c`, `grtworeg.h` and `grtwovar.h`: a public console driver. It shows what a working driver expects, not what the hardware does.
- The Elan Graphics Technical Report (SGI, 1992, in `docs/`), the Brooktree datasheets and the board schematics in `docs/`: published, graded "established (published)" for what they state.
- MAME and other emulators: notes from another project.
- The IRIX source tree carried by upstream is first-rank evidence, as `retools/tools/README-analysis.md#evidence-order` ranks it: read it, cite files by path, grade facts from it [source] and write them in your own words. Never paste source text, comments or macro bodies. Facts resting only on it stay out of QEMU manual pages.

## Evidence order

Take each fact from the highest source that states it and grade it by that source. The order, the reset-value grading, the hardware-read limit and the checks that enforce them are in `retools/tools/README-analysis.md#evidence-order`. In short: the IRIX source tree, then shipped binaries and published manuals, public OS drivers, then other projects' notes. A physical hardware read is a last resort and needs the repository owner's approval. Emulator runs are model behaviour, never hardware evidence. A register read after firmware initialisation is not a reset value.

## Evidence: software only

No hardware is available. Do not plan, request or wait for measurements on a real machine.

- What the software touches and expects back is the driver's expectation, not proof of hardware behaviour.
- Write findings in your own words. Never paste vendor source, HDL or proprietary binaries. Symbol names from a shipped binary's own tables or debug info, and names in published headers and manuals, are fine.
- Before calling a fact unknown, search the shipped binaries, documents and public drivers, and list the routes tried.
- `established` only for what you read in full: the whole function body or table, or the whole passage. A reading built from call lists, register-store summaries or a name is `inferred`.
- An entry written quickly and not yet checked ends with "Unverified.".
- Record an open question in `questions/README.md` with every route tried and the next one. When it is answered, move the answer into the owning chapter and delete the entry.

## Output

- Register and word layouts live in TOML: `devices/<unit>/registers.toml`, each item graded and sourced. `generated/` is built from them and never edited by hand.
- To change a fact, edit the TOML, run `retools/tools/defs/defs-gen`, then `retools/tools/defs/ci-check` (the check CI runs), and commit both.
- Prose that does not fit a map goes in a chapter beside the unit it describes, under `devices/`, `platforms/` or `software/`.

## Tools

Shared tooling is the `retools/` submodule. Change it there and move the pin here. `tools/` holds only this repository's scripts, and `tools/config/` its data and config. Run tools from the repository root. Clone setup: `tools/setup-clone.sh`.

## Where new work goes

There is no `evidence/` directory. File each page by what it is about:

- `devices/<chip>/`, `platforms/<board>/`, `software/<area>/`: a note about one device, platform or software component.
- `<subject>/readings/<binary>.md`: per-routine readings of one binary, filed under the subject it explains.
- `references/`: what we hold and cite, with checksums.
- `generated/`: tool output that is regenerated and never hand-edited.
- `questions/`: open questions.

## Working rules

- Commit small and often to `origami-re`. Subjects are lowercase, component-prefixed imperatives (`hq2: label the microcode load window`); bodies say why. Add files by path, never `git add -A`.

---

# Upstream instructions (techomancer, unchanged)

This is a reverse enginering project for SGI (Silicon Graphics) historic GR2 graphics subsystem

The subsystem was engineered and sold under many names and configurations across Indigo, Indy, and Indigo 2 hardware

https://en.wikipedia.org/wiki/Elan_Graphics

Elan Graphics consists of five graphics subsystems: the HQ2 Command Engine, GE7 Geometry Subsystem, RE3 Raster Engine, VM2 framebuffer and VC1 Display Subsystem

- GR2
- EXPRESS
- Extreme
- XZ
- Elan

Unix haters Ian has already figured out some general stuff sgimips_grtwo_graphics.pdf 

## Project Binaries & Evidence

For licensing and clean-room reasons, proprietary SGI binaries are **not checked into source control** (the local `root/` tree is gitignored). Instead, users copy them from an authentic IRIX 6.5.0 distribution into `root/` following the checklist in [IRIX_FILES.md](IRIX_FILES.md).

The subdirectories below contain relative symbolic links resolving into `root/`:

| Directory | Symlinked Files | Target in `root/` | DWARF Status |
|---|---|---|---|
| `gr2_kernel/` | 9 `.o` files (`gr2.o`, `gr2_init.o`, `gr2_dma.o`, `rrm.o`, `gfx.o`, etc.) | `root/var/sysgen/boot/` | **Full DWARF-2 debug symbols & relocations** |
| `libglcore/` | `libGLcore.so`, `libGL.so`, `libgl.so` | `root/usr/gfx/arch/IP12GR232/` | **Full DWARF debug symbols** |
| `gr2_ddx/` | `gr2.so`, `gr2.so.map`, `glx.so` | `root/usr/lib/X11/dyDDX/` | Dynamic symbols & relocations |
| `ucode/` | `ge7.bin`, `hq2.bin`, `adjntsc.bin`, `adjpal.bin`, `vof` | `root/usr/gfx/ucode/` | ASIC Microcode & VOF binaries |

Other reference sources:
- PROM sources `irixhistory/stand/arcs/lib/libsk/graphics/EXPRESS`
- IDE diagnostics `irixhistory/stand/arcs/ide/fforward/graphics/EXPRESS`
- NetBSD driver `netbsd/src/sys/arch/sgimips/gio/grtworeg.h`, `grtwo.c`
- MAME driver `mame/src/mame/sgi`


OUTPUT: we will place our documentation in the following files
We will use these C headers both for defines and comment sections
for reverse engineered documentation to maintain a single source of truth
we will use these as reference and includes when disassembling object code

GR2.h overall memory map, common registers and defines
HQ2.h command engine registers, defines
GE7.h geometry engine
VM2.h framebuffer
VC1.h display subsystem
XMAP5.h compositor/colormap
RE3.h for raster engine

we also have Bt457.pdf for the brooktree ramdac which is off the shelf asic.
and Brooktree_Bt475_477.pdf for Bt479 and mame mame/src/devices/video/bt47x.cpp

consider that there are similarities between older and newer sgi designs like LG1 in Indigo and REX3/Newport in Indy
so some concepts and methods may translate to GR2

TOOLCHAIN:
We can use the mips-unknown-linux-gnu- toolchain (mips-unknown-linux-gnu-readelf, mips-unknown-linux-gnu-objdump, mips-unknown-linux-gnu-gcc, etc.) for cross-inspection and disassembly.
