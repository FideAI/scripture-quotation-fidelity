# Scripture Quotation Fidelity

Open research on how AI systems deliver exact text from authoritative sources,
studied through English Scripture quotation.

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

That is why released artifacts carry `fid056_p01_` identifiers. The prefix is
the trace: `FID-056` names the public call, `p01` names the first paper
answering it. The identifiers link every released file to the call, to the
prospective lock, and to the release manifest, which is why they are not
renamed to something friendlier.

Paper 01 answers the **quote** and **reference** parts of the call, for English
Christian Scripture. It does not answer paraphrase, contextualization, or other
traditions. [`docs/research_call_coverage.md`](docs/research_call_coverage.md)
tracks exactly which requested outputs are delivered, partial, or still open.

This is an open evaluation methodology, not a leaderboard.

## Papers

### [Paper 01 — Scripture Quotation](papers/p01-scripture-quotation/)

> **When Not to Generate: How AI Systems Quote Scripture, and What
> Authoritative Quotation Requires**

Across 8,640 matched requests, the same Scripture requests were routed through
four designs — the model quotes from memory; the passage is placed in front of
it to copy; it is given a lookup tool; or it only names the passage and
non-generative code inserts the text.

| Design | Exact, architecture-adherent |
|---|---|
| Quotes from memory | 25.00% |
| Text supplied in context | 93.61% |
| Authorized lookup tool | 80.09% |
| Deterministic insertion | 83.94% |

The central finding is that connecting a source did not remove failure but
moved it onto whatever the model still decided. Models called the tool in
95.00% of cases yet asked it for the right passage in only 84.17%.
Deterministic insertion was near-perfect once the model named the right passage
— 1,813 of 1,815 — and powerless when it did not.

These are architecture-condition results within the declared study, not general
model rankings. See the
[result card](papers/p01-scripture-quotation/results/fid056_p01_result_card.md)
for interpretation and limits, and the
[claims boundary](papers/p01-scripture-quotation/docs/claims_boundary.md) for
what the study does not establish.

## Open research

Paper 01 answers one part of the call. Six studies remain open, and Fide AI
does not intend to run them all — several would be done better by biblical
scholars, translators, scholars of other traditions, or researchers in adjacent
fields.

Three can begin immediately against the released Paper 01 dataset with no new
model spend: **delegation to sources of record** (one route bypassed its tool
29% of the time while five others essentially never did), **reference
selection** (the largest unresolved failure, at 84.03%), and **source
availability** (one edition collapsed to near-zero recall on every model
tested). Two more — **paraphrase labeling** and **context preservation** — are
named by the call and owned by nobody.

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
    provenance/  prospective lock, deviations, source editions, manifest
    review/      blinded reviewer materials
    docs/        paper-scoped plan, claims boundary, and disclosures
```

Artifacts keep their `fid056_p01_` prefixes on purpose: they trace each file
back to public research call FID-056 and to the prospective lock. See
[above](#this-repository-answers-a-public-research-call).

## What Is Not Included

Private execution code, raw model outputs, held-out prompts, restricted source
text, partner traces, and credentials. This is a deliberate boundary, described
in [`docs/repository_boundary.md`](docs/repository_boundary.md). The released
derived scores and analysis code reproduce every quantitative claim without
network access.

## Reproduce

With [`uv`](https://docs.astral.sh/uv/) and
[`tectonic`](https://tectonic-typesetting.github.io/) installed:

```bash
make analyze          # regenerate results from released derived scores
make verify-release   # check the manifest and reconcile headline counts
make paper            # rebuild figures and compile the PDF
make release-audit    # scan for secrets, private paths, forbidden artifacts
```

`make analyze` calls no model endpoint. An exact rerun against hosted models is
not guaranteed, since endpoints, routing, and provider defaults change.

## Publishing

```bash
make arxiv        # stage build/arxiv/ : source tarball + plain-text abstract
make hf-dataset   # stage build/huggingface/ : parquet + dataset card
```

Both stage into `build/` and upload nothing. `make arxiv` refuses to package a
`.tex` containing comments, since arXiv publishes submitted source publicly.
`make hf-dataset` refuses to stage if a raw-text column appears in the derived
scores. See [`docs/publishing.md`](docs/publishing.md).

## License

Content is CC BY 4.0 ([`LICENSE`](LICENSE)). Code in `scripts/` is Apache-2.0
([`LICENSE-CODE`](LICENSE-CODE)). No authoritative passage text is released;
passage identity is disclosed through digests only.

## Citation

See [`CITATION.cff`](CITATION.cff).
