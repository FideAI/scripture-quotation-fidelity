# Agent Notes

Notes for AI coding agents working in this repository. Humans should start with
`README.md`.

## Build and verify

```bash
make analyze          # regenerate results from the released derived scores
make verify-release   # manifest digests and headline-count reconciliation
make release-audit    # secrets, private paths, forbidden artifacts
make paper            # figures, then compile the PDF
```

Run `make manifest` after changing any released artifact, or `verify-release`
will fail on a digest mismatch. CI also fails if `make analyze` produces
results that differ from the committed ones.

## Paper builds

`make paper` uses `scripts/build_paper.sh`, which resolves a TeX engine by
checking `$TECTONIC`, then `tectonic` on `PATH`, then
`/opt/homebrew/bin/tectonic`. Do not assume a bare `tectonic` is on `PATH`;
some non-interactive shells omit Homebrew paths.

## Reproducible PDF builds

`scripts/build_paper.sh` exports `SOURCE_DATE_EPOCH`. Tectonic embeds a build
timestamp, so without it every compile produces different bytes, invalidating
the release manifest. Do not remove the pin.

The pin makes builds reproducible for a given tectonic version and platform,
not across them: a Linux rebuild will not match a macOS-built PDF byte for
byte. So if you commit a rebuilt PDF, run `make manifest` in the same commit.
CI verifies the manifest but does not assert cross-platform byte equality.

## Boundaries

Do not add private execution code, raw model outputs, held-out prompts,
restricted source text, provider credentials, or partner-private traces. See
`docs/repository_boundary.md`.

Released artifacts keep their `fid056_p01_` identifiers. They link every file
to public research call FID-056 and to the prospective lock; renaming them
breaks that trace.

Numbers reported in the paper must reconcile with the released dataset. If an
analysis changes, update the paper and rerun `make analyze` and
`make verify-release` together.

## Publishing

`make arxiv` refuses to package `main.tex` if it contains LaTeX comments, since
arXiv publishes submitted source. `make hf-dataset` refuses to stage if a
raw-text column appears in the derived scores.
