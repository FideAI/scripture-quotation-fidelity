# FID-056-P01 Public Research Question and Plan

## Status

This is the canonical public overview for the first paper under Fide AI's
`FID-056` research program. It explains the research question, confirmatory
study design, public outputs, and how The Apologist Project's work contributes.

Working paper title:

> **When Not to Generate: How AI Systems Quote Scripture, and What Authoritative Quotation Requires**

The primary open-edition study is complete: 8,640 scheduled observations were
collected and analyzed. Reviewed aggregate findings are available in
`../results/fid056_p01_result_card.md`. This document preserves the study
question, design, responsibility boundary, and release sequence. It is not a
model ranking, product certification, or endorsement.

## Public Research Question

> When a user asks for an exact quotation from an authoritative source, which
> responsibilities should belong to the model, and which should belong to
> retrieval or deterministic source systems?

The paper distinguishes four system acts:

- **Selection:** identify the requested work, version, and span.
- **Source access:** rely on model parameters, supplied context, an authorized
  retrieval tool, or a structured source reference.
- **Rendering:** produce the exact authorized source text.
- **Output integrity:** preserve that rendering in the final user-visible
  response without omission, alteration, or extra text.

The central hypothesis is not that every task should use deterministic
rendering. It is that an AI model should not automatically be treated as the
source of record when exact wording matters, and that selection and rendering
should be evaluated separately.

## Why Scripture Is the Study Domain

Scripture is the substantive domain of Paper 1. Exact quotation matters in
Christian study, teaching, worship, memorization, and pastoral communication.
It also supports rigorous evaluation because references and ranges are
structured, wording differs across translations, public and restricted
editions coexist, and indirect requests require source selection before
quotation.

Paper 1 results remain scoped to evaluated Scripture scenarios. Legal,
clinical, regulatory, standards, policy, contractual, and other sacred texts
motivate related systems questions but require later replication with
domain-appropriate expertise.

## Confirmatory Comparison

Fide AI executed a matched, crossed experiment in which the same eligible
target and user request appeared under four delivery conditions:

1. **Native generation:** quotation from parametric knowledge without a supplied
   source or tool.
2. **Source-supplied reproduction:** authoritative text is included in context.
3. **Authorized tool retrieval:** a source-of-record tool is available, with
   invocation, lookup, and final rendering observed.
4. **Structured reference and deterministic rendering:** the model selects a
   structured reference and an authorized source layer renders the final text.

The evaluation harness assigns a delivery condition without changing the
underlying user request. This supports matched descriptive comparisons within
the same target, request, model, and source version. Because the conditions
assign different selection, retrieval, and rendering responsibilities, they
are not interpreted as equal-burden treatment arms.

Fide-controlled implementations form the confirmatory comparison. External
partner systems are separately identified evidence streams and do not define
the baselines.

## Executed Scope

The completed confirmatory study was:

- English-first;
- based on three public/open English source editions;
- stratified across single verses, ranges, longer passages, and indirect
  reference requests;
- evaluated on six named and pinned model-family routes; and
- repeated three times per matched cell.

The final matrix contained twenty targets, two prompt families, four delivery
conditions, three editions, six routes, and three epochs.

Restricted translations require documented authorization and a verification
design distinguishing independent verification from partner attestation.

Web search, broad temperature sweeps, multi-reference stress tests, and
multilingual evaluation are not pooled into the confirmatory four-condition
result. They may appear as labeled exploratory or robustness work or become
follow-on FID-056 papers.

## Outcomes

The locked materials call the endpoint **architecture-adherent quotation
exactness**; the paper uses **path-adherent exact delivery**. The complete final output
equals the requested authoritative span without omitted or extraneous text.
Tool and deterministic conditions additionally require verified lookup and
intact rendering.

Component outcomes include:

- reference and source-version selection;
- method adherence and source lookup;
- quote-span and final-output exactness;
- passage coverage and partial delivery;
- rendering and output-integrity verification;
- tool invocation and bypass;
- refusal and truncation; and
- hallucinated, blended, or extraneous text.

Components are preserved rather than collapsed into a weighted score. This
distinguishes correct text produced after tool bypass from altered text produced
after successful retrieval.

## How The Apologist Project Contributes

The Apologist Project is the initial implementation collaborator. Its public
`llm-scripture-fidelity` repository supplied the shared condition
implementation used for local execution. Its commercial product code may
remain private; public paper use depends on auditable evidence and declared
provenance, not disclosure of product source code.

That work can contribute at four evidence levels:

1. **Implementation context:** map the architecture classes to a real Scripture
   application and identify practical failure modes.
2. **Pilot evidence:** provide corrected exploratory runs that improve scenario,
   source, provider, and integration choices before protocol lock.
3. **Partner case study:** provide matched, auditable trial-level results that
   Fide can analyze in a separately labeled section or table.
4. **Evidence supporting a main claim:** contribute preregistration-aligned
   results that pass source verification, reconciliation, and independent Fide
   review.

The Apologist Project need not disclose proprietary product source code. For
empirical use, Fide requires immutable run configuration, trial-level outputs or
release-safe hashes, execution traces, source provenance, component metrics,
resolved model identities, and written publication permissions.

The Apologist Project may publish a separate product-specific companion article
and link it to the independent Fide paper.

## Responsibility Boundary

Fide AI is responsible for:

- the generalized question, protocol, preregistration, and paper;
- confirmatory scenarios, estimands, and statistical analysis;
- Fide-controlled reference conditions;
- evidence reconciliation and verification classification;
- claims boundaries and release review; and
- public methodology and approved aggregate findings.

The Apologist Project is responsible for:

- validity of its public harness and method implementations;
- accurate model, provider, source, and post-processing documentation;
- corrected, reproducible, auditable partner runs; and
- permissions governing its name, traces, examples, and aggregate results.

Both organizations jointly decide the matched partner scenario subset, source
scope, pinned endpoints, evidence transfer, verification requirements,
attribution, authorship, and publication permissions.

## Execution and Release Sequence

### Phase 1: design and source review

- **Complete.** Strata, sources, conditions, metrics, endpoints, analyses, and
  deviation rules were locked before confirmatory output inspection.

### Phase 2: integration pilot

- **Complete.** Integration and four-stratum calibration runs exercised the
  conditions, traces, fixtures, route resolution, and scoring boundary.

### Phase 3: confirmatory public/open run

- **Complete.** All 8,640 scheduled observations and 48 durable execution
  blocks completed. Errors remained in the denominator, paired comparisons
  were calculated, and a route-blinded stratified failure review was completed.

### Phase 4: partner case study and extensions

- **Deferred from the primary result.** Restricted editions, multilingual
  evaluation, web search, temperature sweeps, tier robustness, and any separate
  product case study require their own authorization and analysis boundary.

### Phase 5: paper and public release

- **In progress.** The manuscript, deidentified derived-score package,
  analysis code, aggregate and target-level tables, result card, protocol,
  examples, and claim-evidence mapping are drafted. Final credentialed
  biblical-scholar,
  theological, rights, privacy, attribution, and release review remains
  required before the working manuscript is promoted as a final publication.

## Claims Boundary

Paper 1 may report authoritative-quotation behavior for named systems, sources, scenarios,
configurations, and run dates. It does not establish theological correctness,
pastoral safety, universal legal compliance, general deployment readiness,
training-set membership, commercial superiority, or Fide AI endorsement.

## Public Release

The public working package includes the paper, this plan, protocol, scoring
specification, executed prompt templates, schemas, claims boundary, result
card, deidentified derived scores, provenance receipts, and reproducible
analyses. Private engine code, generated prose, restricted text, raw tool
traces, provider identifiers, partner-private traces, and credentials remain
non-public.
