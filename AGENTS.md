# Agent Notes

Notes for AI coding agents working in this repository. Humans should start with
`README.md`.

## Build and verify

```bash
make analyze          # regenerate results for both released papers
make verify           # verify both manifests and headline-count reconciliation
make release-audit    # secrets, private paths, forbidden artifacts
make papers           # rebuild figures and compile both PDFs
```

Run `make manifest` after changing a Paper 01 or shared repository release
artifact, and `make p02-manifest` after changing a Paper 02 release artifact,
or verification will fail on a digest mismatch. A shared artifact may require
both manifests. CI also fails if `make analyze` produces results for either
paper that differ from the committed ones.

## Paper builds

`make paper` and `make p02-paper` use the corresponding build scripts. Both
resolve a TeX engine by checking `$TECTONIC`, then `tectonic` on `PATH`, then
`/opt/homebrew/bin/tectonic`. Do not assume a bare `tectonic` is on `PATH`;
some non-interactive shells omit Homebrew paths. `make papers` builds both.

## Reproducible PDF builds

Both paper build scripts export `SOURCE_DATE_EPOCH`. Tectonic embeds a build
timestamp, so without it every compile produces different bytes, invalidating
the release manifests. Do not remove the pins.

The pin makes builds reproducible for a given tectonic version and platform,
not across them: a Linux rebuild will not match a macOS-built PDF byte for
byte. So if you commit a rebuilt PDF, run `make manifest` in the same commit.
CI verifies the manifest but does not assert cross-platform byte equality.

## Editing the paper by hand

VS Code or Cursor with the LaTeX Workshop extension. `.vscode/settings.json`
configures a Tectonic recipe for editing and preview. Release PDFs must be built
with `make paper` or `make p02-paper`, since each paper has its own pinned
`SOURCE_DATE_EPOCH`.

After an edit that changes a PDF, rebuild the corresponding manifest before
committing, or verification fails on a digest mismatch.

## Boundaries

Do not add private execution code, raw model outputs, held-out prompts,
restricted source text, provider credentials, or partner-private traces. See
`docs/repository_boundary.md`.

Released artifacts keep their `fid056_p01_` or `fid056_p02_` identifiers. They
link every file to public research call FID-056 and to the corresponding
prospective lock; renaming them breaks that trace.

Numbers reported in the paper must reconcile with the released dataset. If an
analysis changes, update the paper and rerun `make analyze`, both manifests,
and `make verify` together.

## Publishing

`make arxiv` refuses to package `main.tex` if it contains LaTeX comments, since
arXiv publishes submitted source. `make hf-dataset` refuses to stage if a
raw-text column appears in the derived scores.
