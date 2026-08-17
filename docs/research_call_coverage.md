# Coverage of Research Call FID-056

This repository exists to answer a public research call. This document tracks,
honestly, how much of that call has been answered and what remains open.

**Call:** [FID-056: Formal Verification for Sacred Text
Fidelity](https://github.com/FideAI/research-ideas/blob/main/ideas/FID-056-formal-verification-sacred-text-fidelity.md)
· published at <https://fideai.org/research/calls>

> How can faith-facing AI systems be formally checked for whether they quote,
> paraphrase, reference, and contextualize sacred texts faithfully within a
> specified text edition, translation, canon, and interpretive context?

Paper 01 addresses quotation delivery and reference selection for **English
Christian Scripture** under **three open editions**. Paper 02 addresses whether
models use an available Scripture source when system and user instructions
agree or conflict. Neither paper addresses paraphrase, contextualization, or
other traditions. The sections below say which is which.

## Requested outputs

| Call output | Status | Where |
|---|---|---|
| Sacred-text fidelity verification protocol | Partial | `protocol/source_delivery_protocol.md`, `protocol/scoring_spec.md`. Covers exact quotation and reference validity. Paraphrase and context-preservation obligations are not specified. |
| Test set of quote, paraphrase, reference, and context-preservation cases | Partial | `papers/p01-scripture-quotation/data/fid056_p01_targets.jsonl`. Twenty targets covering explicit references, multi-verse spans, long passages, and event-style requests. No paraphrase or context-preservation cases. |
| Error taxonomy for citation and paraphrase failures | Partial | Failure tags in `protocol/scoring_spec.md` and the paper's Appendix F. Covers selection, access, rendering, and output-integrity failures. Paraphrase failures are not taxonomised. |
| Reviewer agreement study comparing automated checks with human review | **Open** | Pre-committed but not yet run. Protocol in `papers/p01-scripture-quotation/docs/contextual_description_review_protocol.md`; blinded packet in `papers/p01-scripture-quotation/review/`. |
| Public claim template for what fidelity scores can and cannot say | Delivered | `papers/p01-scripture-quotation/docs/claims_boundary.md` and the paper's Appendix G. |

## Requested controls

The call names four controls. Paper 01 observes all four.

| Control | How it is honored |
|---|---|
| Do not treat textual fidelity as a full measure of theological truth | The paper defines fidelity narrowly as fidelity to a requested English source text and span, and states repeatedly that theological correctness, exegesis, and pastoral appropriateness are outside the claim. |
| Separate quote accuracy, paraphrase quality, reference validity, interpretive claim support, and pastoral appropriateness | The source-delivery chain separates selection, access, rendering, and output integrity as distinct measured stages. Paraphrase quality, interpretive support, and pastoral appropriateness are excluded rather than conflated. |
| Track text edition, translation, canon boundaries, and source licensing | `papers/p01-scripture-quotation/provenance/source_editions.json` records edition identity, provider, rights basis, and per-target digests. The paper states that the three editions carry the Protestant canon and that canon boundaries are not adjudicated. |
| Include disputed and near-match passages where surface similarity can mislead | Partial. Two intertextual or adjacent relationships were annotated rather than treated as independent evidence: the Shema and great-commandment pair, and adjacent passages in John 3. The panel was not built around textual variant units. |

## Open questions from the call

| Question | Status |
|---|---|
| Which sacred texts and translations can be included in public benchmarks? | Partially answered for English Christian Scripture. Three open editions were usable; four restricted editions were locked into the registry but blocked pending AI-use authorization, and are disclosed as excluded. The rights pathway for restricted translations remains unresolved. |
| How much surrounding context is needed for a citation to count as faithful? | Not addressed. Paper 01 measures delivery of a requested span, not context adequacy. |
| How should systems handle traditions where oral transmission, commentary, or interpretive authority is central? | Not addressed. The paper notes that the unit of authority differs across traditions enough to change the study design, not merely the numbers. |
| When does a paraphrase become an unsupported doctrinal claim? | Not addressed. Out of scope by construction. |

## What this implies for later papers

The call is explicitly multi-tradition and covers paraphrase and context, so
Paper 01 answers roughly one quadrant of it. What remains, in rough order of
readiness:

| Open study | Why it is next | Readiness |
|---|---|---|
| Reviewer agreement study | Closes a requested output of the call; already specified and packaged | Needs a reviewer, nothing else |
| P02 delegation | Confirmatory study complete; manuscript and reproducible release candidate in `papers/p02-source-delegation/` | Complete pending release decision |
| P03 selection, P04 availability | Each explains a diagnostic Paper 01 recorded and declined to interpret | Released data in hand |
| P05 paraphrase, P06 context preservation | Named by the call; the clearest gaps in coverage | Need construct definitions first |
| P07 cross-lingual | Most of the world's Scripture reading is not in English | Needs new execution and rights |

Restricted-translation access is a rights workstream rather than a study. Four
editions sit in the Paper 01 locked registry pending AI-use authorization, and
resolving that widens what every study above can measure.

Each study requires its own charter, evidence, and release decision. See
[`research_program.md`](research_program.md) for the full agenda and how to
claim one.
