# Scripture Quotation Fidelity

Open research on how AI systems deliver exact text from authoritative sources,
studied through English Scripture quotation. This repository contains the
public research packages for Papers 01 and 02: manuscripts, protocols,
deidentified derived scores, reviewed results, provenance records, and
standalone analysis code.

When someone asks an AI assistant for a passage of Scripture, the reply usually
sounds right. A fluent answer can blend two translations, drop a verse, or
paraphrase inside quotation marks — and the person who asked is the one least
able to check. This repository holds the papers, protocol, data, and analysis
code for measuring when that happens and which part of the system caused it.

## This repository answers a public research call

Fide AI publishes its research agenda openly as numbered calls at
[fideai.org/research/calls](https://fideai.org/research/calls), with
[`FideAI/research-ideas`](https://github.com/FideAI/research-ideas) as the
source of truth. This repository is the work answering one of them:

> **[FID-056: Formal Verification for Sacred Text
> Fidelity](https://github.com/FideAI/research-ideas/blob/main/ideas/FID-056-formal-verification-sacred-text-fidelity.md)**
> — How can faith-facing AI systems be formally checked for whether they quote,
> paraphrase, reference, and contextualize sacred texts faithfully within a
> specified text edition, translation, canon, and interpretive context?

That is why released artifacts carry paper-scoped identifiers such as
`fid056_p01_` and `fid056_p02_`. `FID-056` names the public call, while `p01`
or `p02` names the paper answering it. These identifiers link each released
file to the call, prospective lock, and release manifest.

Paper 01 addresses quotation delivery and reference selection for English
Christian Scripture. Paper 02 asks when models defer to an available source of
record. Neither paper answers paraphrase, contextualization, or questions about
other traditions. [`docs/research_call_coverage.md`](docs/research_call_coverage.md)
tracks exactly which requested outputs are delivered, partial, or still open.

This is an open evaluation methodology, not a leaderboard.

## Papers

### [Paper 01 — Scripture Quotation](papers/p01-scripture-quotation/)

> **When Not to Generate: How AI Systems Quote Scripture, and What
> Authoritative Quotation Requires**

📄 [Read the paper (PDF)](papers/p01-scripture-quotation/paper/main.pdf) ·
[LaTeX source](papers/p01-scripture-quotation/paper/main.tex) ·
[dataset](papers/p01-scripture-quotation/data/)

Across 8,640 matched requests, the same Scripture requests were routed through
four designs — the model quotes from memory; the passage is placed in front of
it to copy; it is given a lookup tool; or it only names the passage and
non-generative code inserts the text.

| Design | Exact delivery |
|---|---:|
| Quotes from memory | 25.00% |
| Text supplied in context | 93.61% |
| Authorized lookup tool | 80.09% |
| Deterministic insertion | 91.25% |

These conditions intentionally assign different responsibilities. In
particular, text supplied in context is a best-case copy test:
the correct reference and text are already given, so the model performs neither
selection nor retrieval. The four rates describe the staged delivery system;
they are not equal-burden treatment effects.

The central finding is that connecting a source did not remove failure but
moved it onto whatever the model still decided. Models called the tool in
95.00% of cases yet asked it for the right passage in only 84.17%.
Deterministic insertion was exact in 99.91% of explicit-reference requests and
82.59% of contextual requests, showing that reference identification rather
than final rendering remained its principal limitation.

The result package separately audits an implementation correction to the
deterministic parser; no model outputs were regenerated.

These are delivery-condition results within the declared study, not general
model rankings. See the
[result card](papers/p01-scripture-quotation/results/fid056_p01_result_card.md)
for interpretation and limits, and the
[claims boundary](papers/p01-scripture-quotation/docs/claims_boundary.md) for
what the study does not establish.

### [Paper 02 — Source Delegation](papers/p02-source-delegation/)

> **Knowing When to Defer: How Language Models Use and Bypass Sources of Record**

📄 [Read the paper (PDF)](papers/p02-source-delegation/paper/main.pdf) ·
[LaTeX source](papers/p02-source-delegation/paper/main.tex) ·
[dataset](papers/p02-source-delegation/data/)

Paper 02 tests whether a model actually uses an available Scripture source
before answering. It crosses a system policy that either makes source use
available or requires it with user wording that either remains neutral or asks
the model to avoid tools and answer from memory.

Across 4,800 requests, ordinary prompts produced approximately 95% source use
under both system policies. Under conflicting user pressure, source use fell
to 30.6% when the source was merely available but remained at 84.7% when the
system required it. Source use was still not sufficient for correct delivery:
89.1% of delegated requests named the intended passage, and 93.5% of those
reproduced the source span exactly.

These are fixed-route results from six tested model configurations, not a
provider ranking or evidence about theological interpretation. See the
[result card](papers/p02-source-delegation/results/fid056_p02_result_card.md)
and [claims boundary](papers/p02-source-delegation/docs/claims_boundary.md).

## Open research

Papers 01 and 02 answer quotation-delivery and source-delegation questions from
the call. Five studies remain open, and Fide AI
does not intend to run them all — several would be done better by biblical
scholars, translators, scholars of other traditions, or researchers in adjacent
fields.

Two can begin immediately against released data with no new model spend:
**reference selection** (now separated from literal interface compliance) and
**source availability** (the LSV collapsed to near-zero recall on every model
tested, while the BSB ranged from 16.7% to 64.2%). Two more — **paraphrase
labeling** and **context preservation** — are
named by the call and owned by nobody.

A fifth study, **cross-lingual and translation fidelity**, requires new
execution, source-rights work, and native-language expertise.

See [`docs/research_program.md`](docs/research_program.md) for the full agenda,
evidence, and how to claim a study, and
[`docs/research_call_coverage.md`](docs/research_call_coverage.md) for what the
call still asks for.

## Why Scripture

Scripture is the study domain, not a stand-in for one. Exact wording matters to
Christian study, teaching, worship, memorization, and pastoral communication,
and AI assistants are already used in those settings. The domain is also
unusually measurable: verse references give a conventional addressing scheme,
multiple English translations make edition identity observable, and passage
length can be varied systematically.

The systems framework — separating source selection, authorized access, exact
rendering, and final-output integrity — applies wherever a source of record
exists, including statutes, clinical instructions, contracts, and standards.
The measured effect sizes do not transfer to those domains without separate
replication.

## Layout

```
protocol/    the shared method: source-delivery protocol, scoring spec, schemas
docs/        program-level governance, boundary, and responsible-use documents
examples/    public-domain example scenarios and scoring examples
scripts/     analysis, build, provenance, and release-audit tooling
papers/
  p01-scripture-quotation/
    paper/       LaTeX source and figures
    data/        deidentified derived scores and release-safe target registry
    results/     reviewed aggregate and target-level results
    provenance/  release decision, prospective lock, deviations, source editions, manifest
    review/      blinded reviewer materials
    docs/        paper-scoped plan, claims boundary, and disclosures
  p02-source-delegation/
    paper/       LaTeX source and figures
    data/        deidentified behavioral rows and release-safe targets
    results/     factorial effects, route sensitivity, and delegation pipeline
    provenance/  prospective lock, execution seal, deviations, and manifest
    docs/        protocol, prompts, claims boundary, and disclosures
```

Artifacts keep their `fid056_p01_` or `fid056_p02_` prefixes on purpose: they
trace each file back to public research call FID-056, the corresponding paper,
and the prospective lock. See [above](#this-repository-answers-a-public-research-call).

## What is not included

Private execution code, raw model outputs, held-out prompts, restricted source
text, partner traces, and credentials. This is a deliberate boundary, described
in [`docs/repository_boundary.md`](docs/repository_boundary.md). The released
derived scores and analysis code reproduce every quantitative claim without
network access.

## Reproduce

With [`uv`](https://docs.astral.sh/uv/) and
[`tectonic`](https://tectonic-typesetting.github.io/) installed:

```bash
make analyze          # regenerate results for both papers
make verify           # check both manifests and reconcile headline counts
make papers           # rebuild figures and compile both PDFs
make release-audit    # scan for secrets, private paths, forbidden artifacts
```

Paper-specific targets remain available as `make p01-analyze`, `make paper`,
`make verify-release`, `make p02-analyze`, `make p02-paper`, and
`make p02-verify`. Publication bundles are staged without upload through
`make arxiv` and `make hf-dataset` for Paper 01 or `make p02-arxiv` and
`make p02-hf-dataset` for Paper 02.

`make analyze` calls no model endpoint. An exact rerun against hosted models is
not guaranteed, since endpoints, routing, and provider defaults change.

## Contributing

Open studies are genuinely unclaimed, and several need expertise Fide AI does
not have. See [`docs/research_program.md`](docs/research_program.md) for what is
open and how to claim it, [`CONTRIBUTING.md`](CONTRIBUTING.md) for what belongs
here, and [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) for the standard we hold
in a repository that touches religious texts and practice.

Security or private-data concerns go through [`SECURITY.md`](SECURITY.md),
never a public issue.

Maintainers: build and release procedures are in
[`AGENTS.md`](AGENTS.md) and [`docs/publishing.md`](docs/publishing.md).

## Citation

Paper 01:

```bibtex
@misc{chao2026whennottogenerate,
  title  = {When Not to Generate: How AI Systems Quote Scripture,
            and What Authoritative Quotation Requires},
  author = {Chao, Alex},
  year   = {2026},
  note   = {Fide AI. Study FID-056-P01.},
  url    = {https://github.com/FideAI/scripture-quotation-fidelity}
}
```

Paper 02:

```bibtex
@misc{chao2026knowingwhentodefer,
  title  = {Knowing When to Defer: How Language Models Use and Bypass
            Sources of Record},
  author = {Chao, Alex},
  year   = {2026},
  note   = {Fide AI. Study FID-056-P02.},
  url    = {https://github.com/FideAI/scripture-quotation-fidelity}
}
```

Repository-level machine-readable metadata is in
[`CITATION.cff`](CITATION.cff); paper-scoped citation guidance is included with
each paper package.

## License

Content is CC BY 4.0 ([`LICENSE`](LICENSE)). Code in `scripts/` is Apache-2.0
([`LICENSE-CODE`](LICENSE-CODE)). The third-party
[`acl_natbib.bst`](papers/p01-scripture-quotation/paper/acl_natbib.bst) retains
LPPL-1.0-or-later. The released study data contains no authoritative passage
text from the evaluated BSB, WEBU, or LSV editions; passage identity is
disclosed through digests only. Public examples include KJV wording identified
as public domain in the United States; verify local rights before
redistributing it elsewhere.
