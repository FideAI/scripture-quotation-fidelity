# Paper Build

Compile the paper from the repository root:

```bash
make paper
```

`make paper` builds the canonical visual manuscript. It first regenerates the
paper's PDF figures from
`scripts/build_paper_figures.py`, then compiles `main.tex` with the repository
Tectonic wrapper. Run `make figures` to rebuild only the figures.

The build wrapper uses `tectonic`. It checks `$TECTONIC`, then `tectonic` on
`PATH`, then `/opt/homebrew/bin/tectonic`.

Direct compile command used in this workspace:

```bash
/opt/homebrew/bin/tectonic main.tex
```

The build wrapper accepts a paper filename in this directory when a temporary
review variant must be compiled, but publication tooling always uses the
canonical `main.tex`.
