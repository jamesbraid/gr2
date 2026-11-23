# gr2

Reverse-engineering notes for the SGI GR2 graphics family (Express, Elan, XS, XS24, XZ) of the Indigo, read from the shipped IRIX binaries and the published documents. [AGENTS.md](AGENTS.md) has the scope, the evidence rules and the finish line. The IRIX files themselves are not tracked; [references/binaries.md](references/binaries.md) says which to copy into the ignored `root/` directory.

This is the `origami-re` branch of techomancer's [gr2](https://github.com/techomancer/gr2). The upstream files (the `*.h` headers, `docs/`, the decompiled trees) are kept as they were and are treated as notes from another project.

## Start here

- [platforms/express/README.md](platforms/express/README.md): the board variants, the chips on each, the GIO window and probe, what the shipped software tells us, per-chip grades and the reading plan.
- [devices/hq2/README.md](devices/hq2/README.md): the host-visible HQ2 window the PROM and kernel touch.
- [questions/README.md](questions/README.md): open questions, each with the routes tried and the next one.
- [references/binaries.md](references/binaries.md): the shipped objects read so far, with SHA-256.
