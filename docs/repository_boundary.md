# Public and Private Repository Boundary

## Principle

The research should be reproducible at the level of questions, protocols,
scenarios, scoring definitions, disclosed configurations, approved derived
outcomes, analyses, and claims. Reproducibility does not require publishing either organization's
general-purpose execution infrastructure or proprietary product implementation.

Three repositories or artifact zones should remain distinct:

| Zone | Owner | Default visibility | Purpose |
| --- | --- | --- | --- |
| Authoritative Quotation public research package | Fide AI | Public/open | Paper, methodology, public scenarios, schemas, release policy, and approved result artifacts |
| `fide-eval-engine` and FID-056 execution study | Fide AI | Private/proprietary | Manifests, providers, orchestration, raw outputs, held-out prompts, restricted corpora, analysis staging, and release review |
| The Apologist Project implementation | The Apologist Project | Private/proprietary by default | Product code, partner execution harness, credentials, provider integrations, private traces, and internal analysis |

An organization may separately choose to open-source a deliberately scoped
research harness, but that is not required by the Fide study and must not expose
product code, credentials, restricted source material, or private traces.

## Public Repository Contents

The public repository may contain:

- paper source, bibliography, and compiled paper;
- public research question and study plan;
- protocol and scoring specification;
- domain-neutral and domain-extension schemas;
- public-domain scenario examples;
- public release and claims boundaries;
- disclosed run metadata needed to interpret released claims;
- aggregate tables, confidence intervals, figures, and failure counts;
- deidentified trial-level derived scores after paper-specific review;
- standalone analysis code and release-safe provenance receipts;
- approved, rights-safe illustrative examples; and
- checksums or verification summaries that do not expose restricted text.

Public result artifacts should be machine-readable where practical and include:

- `research_program_id` and `paper_id`;
- protocol, scenario-set, and scoring versions;
- named system and source configurations;
- run dates and denominators;
- error, refusal, and missing-output counts;
- confirmatory versus exploratory labels;
- verification mode; and
- known exclusions and deviations.

## Fide-Private Contents

The following remain in `fide-eval-engine` or another approved private store:

- engine source and reusable provider adapters;
- live and private manifests;
- credentials, endpoint contracts, and secret-bearing configuration;
- held-out scenarios and private prompt variants;
- raw model messages, tool payloads, and provider responses;
- restricted or licensed source text and caches;
- partner handoff packages and private product traces;
- intermediate analysis, adjudication, and reviewer notes;
- unreleased result tables and exploratory analyses; and
- release decisions before publication.

## Partner-Private Contents

The Apologist Project retains:

- proprietary product and output-buffer implementation;
- internal evaluation and provider integration code;
- credentials and licensed-source access details;
- raw private runs and restricted source payloads;
- product-specific prompts, policies, and traces not approved for disclosure;
- commercial interpretation and companion-publication drafts.

Fide receives only the evidence package necessary for the agreed evidence level,
through a private transfer path. Receiving that package does not make it public.

## Artifact Promotion Flow

```text
Fide private execution                 Partner private execution
        |                                      |
        | raw traces and private evidence      | private handoff package
        +------------------+-------------------+
                           |
                   Private Fide analysis
                           |
              claims, rights, privacy, and
                  partner-permission review
                           |
                    release decision
                           |
                           v
              Public protocol repository
       paper + protocol + approved derived artifacts
```

Files are copied into the public repository only after a paper-specific release
decision. The public repository must never be used as an execution output
directory or as temporary storage for raw evidence.

## Public Result Package

A typical approved release should use a structure such as:

```text
data/
  fid056_p01_deidentified_trials.csv.gz
  fid056_p01_targets.jsonl
results/
  aggregate_metrics.csv
  target_level_results.csv
  paired_comparisons.csv
provenance/
  release_manifest.json
  source_editions.json
```

The release manifest should identify every included artifact, its checksum,
rights classification, evidence source, verification mode, and release-decision
reference. Exact executed prompt templates may be released after review; raw
completions, source payloads, tool traces, and restricted text are not part of
the package.

## Partner Naming

The public paper may state that The Apologist Project is an implementation
collaborator and may report an approved, separately labeled partner case study.
It should not disclose partner implementation details beyond approved method
descriptions. Partner results must remain distinguishable from Fide-controlled
conditions.

## Enforcement

Before any public commit or release:

1. Run `make release-audit`.
2. Confirm the paper-specific release decision.
3. Review new result files against the release manifest.
4. Confirm restricted-source and partner permissions.
5. Inspect repository history, not only the current working tree, for secrets or
   private artifacts.

The automated audit is a minimum check. It does not replace human rights,
privacy, claims, or partner-permission review.
