# Contributing

Two very different kinds of contribution are welcome here, and they follow
different paths.

## Taking on an open study

Most of the research this repository exists to support is unclaimed. Fide AI
does not intend to run every study in
[`docs/research_program.md`](docs/research_program.md), and several would be
done better by biblical scholars, translators, scholars of other traditions, or
researchers in adjacent fields.

Three studies can begin immediately against the released Paper 01 dataset with
no new model spend. Two more are named by the research call and owned by
nobody.

To claim one, open a `Claim or help with an idea` issue on
[`FideAI/research-ideas`](https://github.com/FideAI/research-ideas) referencing
FID-056 and the study ID. Claiming is not exclusive ownership; it signals active
work so effort is not duplicated. Your study needs its own charter, prospective
specification, evidence, reviewers, and release decision — it does not inherit
Paper 01's.

There is also an open **reviewer agreement study**: an independent scholarly
review of the twenty contextual descriptions, fully packaged in
[`papers/p01-scripture-quotation/review/`](papers/p01-scripture-quotation/review/)
and blocked only on finding a reviewer. It is roughly an hour of work for
someone qualified, and it closes a requested output of the research call.

## Changing this repository

Welcome:

- Documentation improvements and corrections.
- Scenario-schema and scoring-spec clarifications.
- Additional public-domain examples with clear source provenance.
- Release-policy improvements.
- Paper corrections that improve accuracy or methodological clarity.
- Analysis code improvements that preserve reported results.

Never submit:

- Private execution-engine source code.
- API keys, provider credentials, or endpoint secrets.
- Raw model outputs, or held-out prompts.
- Restricted source text, or authoritative passage text of any edition.
- Partner traces or private product outputs.
- Claims that treat this work as a leaderboard, model ranking, product
  endorsement, theological certification, or legal opinion.

### Before opening a pull request

```bash
make analyze          # must reproduce committed results with no diff
make verify-release   # manifest digests and headline counts
make release-audit    # secrets, private paths, forbidden artifacts
```

If you changed a released artifact, run `make manifest` as well, or
verification will fail on a digest mismatch. CI runs all of these.

Two constraints that are easy to trip over:

- **Reported numbers must reconcile with the released dataset.** If an analysis
  changes, update the paper and rerun the checks together.
- **Released artifacts keep their `fid056_p01_` identifiers.** They link every
  file to the research call and the prospective lock. Renaming breaks the
  trace.

## Reporting problems

A factual error in the paper, a number that does not reconcile, or a broken
reproduction step is a valuable issue — please open one.

Security concerns, credential exposure, or private data appearing anywhere in
this repository go through [`SECURITY.md`](SECURITY.md), **not** a public issue.

## Conduct

This repository touches religious texts and the practices of communities that
regard them as authoritative. [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)
applies to all participation.
