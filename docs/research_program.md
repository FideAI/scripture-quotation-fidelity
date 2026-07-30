# FID-056 Research Program

This repository answers [FID-056: Formal Verification for Sacred Text
Fidelity](https://github.com/FideAI/research-ideas/blob/main/ideas/FID-056-formal-verification-sacred-text-fidelity.md),
a public call for research. The call is deliberately larger than one paper, so
the program is a set of narrow, individually auditable studies rather than one
study attempting to cover every form of sacred-text fidelity.

Paper 01 is complete. This document is the agenda for what comes next.

[`research_call_coverage.md`](research_call_coverage.md) tracks which of the
call's requested outputs are delivered, partial, or open.

## Getting involved

Every study below is unclaimed. Fide AI does not intend to run all of them, and
several would be done better by people with expertise we do not have — biblical
scholars, translators, scholars of other traditions, and researchers in
adjacent fields.

To take one up, open a `Claim or help with an idea` issue on
[`FideAI/research-ideas`](https://github.com/FideAI/research-ideas) referencing
FID-056 and the study ID. Claiming is not exclusive ownership; it signals active
work so effort is not duplicated.

Three studies can begin immediately against the released Paper 01 dataset with
no new model spend and no restricted sources. Those are marked **data in hand**.

## Agenda

| ID | Study | Readiness |
|---|---|---|
| P01 | Scripture quotation across four architectures | Complete |
| P02 | Model delegation to sources of record | Data in hand |
| P03 | Reference selection | Data in hand |
| P04 | Source availability and parametric recall | Data in hand |
| P05 | Paraphrase and quotation labeling | Needs construct design |
| P06 | Context preservation | Needs construct design |
| P07 | Cross-lingual and translation fidelity | Needs new execution and rights |

There is also an open **reviewer agreement study** attached to Paper 01: an
independent scholarly review of all twenty contextual descriptions. It is a
requested output of the call, fully specified and packaged, and blocked only on
finding a reviewer. See
[`papers/p01-scripture-quotation/docs/contextual_description_review_protocol.md`](../papers/p01-scripture-quotation/docs/contextual_description_review_protocol.md).

---

## Studies that explain Paper 01's open results

Paper 01 recorded several diagnostics and deliberately declined to explain
them. Each is now a study, and each can start with data already released.

### P02 · Model delegation to sources of record

Paper 01 reports a tool invoked in 95.00% of tool observations. That pooled
figure conceals a binary split:

| Route | Tool invoked | Used for the requested span |
|---|---|---|
| GPT-5.6 Sol | 100.0% | 93.3% |
| Claude Sonnet 5 | 100.0% | 87.2% |
| Gemini 3.5 Flash | 99.7% | 89.4% |
| DeepSeek V4 Pro | 99.7% | 84.2% |
| GLM-5.2 | 99.4% | 85.8% |
| Kimi K3 | **71.1%** | **65.0%** |

Five routes essentially always delegate; one bypasses roughly three times in
ten. This is not a performance spectrum but a difference in whether the model
treats an authorized source as necessary at all.

**Question.** What makes a model decide a source of record is unnecessary, and
can delegation be made reliable through prompt, harness, or interface design
rather than through model choice?

**Needs.** Released Paper 01 data for the descriptive result; new execution to
test interventions. No restricted sources.

### P03 · Reference selection

The largest unresolved failure in Paper 01. Deterministic rendering was 99.89%
reliable *given* a correct reference, and the model supplied one in only 84.03%
of observations — 345 wrong or unparseable selections. Contextual descriptions
cost tool-mediated retrieval 20.19 percentage points. Separately, an
analysis-only tolerant parser recovered the intended reference in 90.46% of
observations, including 158 of 161 syntax-tagged cases.

**Question.** How much of selection failure is genuine misidentification versus
interface non-conformance, and what makes a passage hard to identify from
description? Paper 01's failure review saw selections that expanded an event to
include narrative setup and others that narrowed a range to its most salient
verse — opposite errors that a single accuracy number hides.

**Needs.** Released Paper 01 data. Benefits from the reviewer agreement study,
which will establish whether the descriptions themselves are unambiguous.

### P04 · Source availability and parametric recall

The sharpest signal in the dataset, and the one Paper 01 most firmly refuses to
interpret. Native exactness by edition and route:

| Route | BSB | WEBU | LSV |
|---|---|---|---|
| Kimi K3 | 64.2% | 34.2% | 2.5% |
| DeepSeek V4 Pro | 59.2% | 31.7% | 5.8% |
| GPT-5.6 Sol | 53.3% | 36.7% | 15.8% |
| GLM-5.2 | 34.2% | 25.0% | 0.8% |
| Gemini 3.5 Flash | 21.7% | 24.2% | 2.5% |
| Claude Sonnet 5 | 16.7% | 19.2% | 2.5% |

LSV collapses to near zero on **every** route while BSB varies from 16.7% to
64.2%. The consistency of the LSV result across otherwise dissimilar models
points at a property of the edition rather than of any model.

**Question.** What explains the edition effect — corpus availability,
translation distinctiveness, licensing-driven absence, or tokenization? Paper
01 documents the interaction and declines to attribute a cause.

**Needs.** Released Paper 01 data, plus corpus-availability evidence.

**Hazard.** This sits adjacent to existing memorization and extraction work. It
needs a question sharper than "models reproduce popular translations better," or
it will restate known results in a new domain.

---

## Studies the call asks for that nothing yet covers

The call names paraphrase and context obligations directly. Paper 01 measures
only exact delivery, so a fluent paraphrase and a verbatim quotation are both
simply "not exact" to it.

### P05 · Paraphrase and quotation labeling

**Question.** Can the boundary between faithful paraphrase, unfaithful
paraphrase, and unsupported doctrinal claim be specified precisely enough to
check automatically, and do systems label their own paraphrases honestly?

**Needs.** A paraphrase taxonomy and human adjudication. Requires theological
and linguistic expertise. **Strong candidate for external collaboration.**

### P06 · Context preservation

**Question.** Can context adequacy be defined as a measurable obligation, and do
systems truncate context in ways that change what a passage appears to say?

**Needs.** A construct definition first. This is a conceptual problem before it
is an empirical one, and it may be the hardest study in the program.

---

## Extending the domain

### P07 · Cross-lingual and translation fidelity

Paper 01 covers three English editions. Reference conventions, translation
ecosystems, source availability, and language-technology maturity all differ
elsewhere, and most of the world's Scripture reading is not in English.

**Question.** Do the architecture effects hold outside English, and where does
the source-delivery chain need different machinery?

**Needs.** New execution, new source rights, and native-language expertise. A
substantial lift, and plausibly the highest real-world impact in the program
after Paper 01.

---

## Scope

This program studies sacred-text fidelity. The source-delivery chain applies
wherever a source of record exists — statutes, contracts, clinical
instructions, standards — and that work is worth doing, but it needs different
sources, reviewers, rights analysis, and domain expertise. Paper 01 states the
framework's intended transfer and the boundary on its effect sizes; work of
that kind should cite it and proceed under its own program.

## Supporting technical workstreams

Endpoint integration, verification receipts, streaming-buffer hardening, and
source-corpus governance make rigorous studies possible but are not papers by
default. A technical artifact becomes a paper only when it has a generalizable
research question, a comparison design, and a contribution beyond
implementation quality.

Source rights are the live workstream here. Four editions (ESV, NASB 1995, NIV
2011, NLT) sit in the Paper 01 locked registry, blocked pending AI-use
authorization. Resolving that access widens what every study above can measure.

## Shared foundation and independence

Studies may reuse the public scenario schema, scoring vocabulary, source-rights
metadata, verification-receipt concepts, and release policy.

They must not reuse another study's results or release approval as evidence for
a new claim. Each requires its own charter, scenario set, prospective
specification, evidence, reviewers, and release decision.

Published result packages identify both the program and the study:

```yaml
research_program_id: FID-056
paper_id: FID-056-P01
```

This lets the program accumulate evidence over time while every individual
study stays narrow and auditable.
