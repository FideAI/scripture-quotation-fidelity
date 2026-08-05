# Publishing

Papers go to arXiv. Derived-score datasets go to the Hugging Face Hub. The
GitHub repository stays the source of truth for protocol, provenance, and
analysis code, and is what both other venues point back to.

Both build targets stage into `build/` and upload nothing. Publishing is a
separate, deliberate step.

## arXiv

```bash
make arxiv
```

Produces `build/arxiv/<paper>-arxiv.tar.gz` and `build/arxiv/abstract.txt`.

**arXiv publishes the LaTeX source you submit, not just the PDF.** Anyone can
download it. The build therefore fails if `main.tex` contains comments, so
notes-to-self cannot ship by accident. Keep it that way: if you need a working
note, put it in a separate file that is not part of the bundle.

The tarball ships a current `main.bbl` so arXiv does not need to run bibtex. It
also includes `references.bib` so the submission remains self-contained if a
compiler elects to refresh the bibliography, plus `main.tex`, the `.bst`, and
the manuscript-referenced figures.

### Submission fields

| Field | Value |
|---|---|
| Primary category | `cs.CL` |
| Cross-list | `cs.AI`, `cs.CY` |
| License | CC BY 4.0, matching this repository |
| Abstract | paste `build/arxiv/abstract.txt` verbatim |
| Comments | link the GitHub repository and the Hugging Face dataset |

`cs.CY` (Computers and Society) is the category that carries the
religion-and-technology framing; without it the paper reads to browsers as a
narrow source-delivery evaluation.

The abstract field is plain text with a **1,920 character limit**. `make arxiv`
reports the generated character count and refuses to package an abstract that
exceeds the limit.

### After submitting

Check arXiv's own compiled PDF rather than a local build. arXiv recompiles from
source with its own TeX Live, and a paper that builds under tectonic locally can
still surface differences there.

Once the identifier is assigned, add it to `CITATION.cff`, the repository
README, and the Hugging Face dataset card.

## Hugging Face

```bash
make hf-dataset
```

Produces `build/huggingface/` containing `trials.parquet` (8,640 rows),
`targets.parquet` (20 rows), and a dataset card.

Parquet rather than the released `.csv.gz` because the Hub's dataset viewer
renders parquet natively, which is most of the value of publishing there — a
reader can inspect and filter the data without downloading anything.

The build refuses to stage if any raw-text column appears in the derived
scores. The released file contains derived scores and content digests only,
which is what makes it publishable; the check exists so that invariant is
verified rather than assumed.

Upload:

```bash
uv run --with huggingface_hub hf upload-large-folder \
  --repo-type=dataset FideAI/scripture-quotation-fidelity-p01 build/huggingface
```

### Card maintenance

The dataset card lives in `scripts/build_hf_dataset.py` and is regenerated on
every build, so edit it there rather than on the Hub. Anything edited in the web
UI will be overwritten by the next upload.

## Keeping the three in sync

Each venue holds a different artifact, and each should point at the other two.

| Venue | Holds | Must link |
|---|---|---|
| arXiv | The paper | GitHub repo, HF dataset |
| Hugging Face | Derived scores | arXiv paper, GitHub repo |
| GitHub | Protocol, provenance, analysis code | arXiv paper, HF dataset |

When a paper is revised, all three move: a new arXiv version, a card update if
numbers changed, and a repository release tag. If a reported number ever
changes, it changes in all three or in none.

## Release tagging

Paper-release tags use the date-based convention already established by Paper
01:

```
p01/release-2026-08-05       Paper 01 release on that date
p01/release-2026-08-05-v2    second Paper 01 release on the same date, if needed
p02/release-YYYY-MM-DD        first release of Paper 02
```

A tag is immutable and freezes one paper's replication package while the
repository keeps growing around it. Record the arXiv identifier in the tag
annotation so the tag, paper version, and dataset revision can be lined up
later. Use a new date or version suffix for a revision rather than moving a
published tag.
