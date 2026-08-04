# Paper 01 — Scripture Quotation

**When Not to Generate: How AI Systems Quote Scripture, and What Authoritative
Quotation Requires**

Alex Chao, Fide AI.

Study identifier `FID-056-P01`: the first paper answering public research call
[FID-056, Formal Verification for Sacred Text
Fidelity](https://github.com/FideAI/research-ideas/blob/main/ideas/FID-056-formal-verification-sacred-text-fidelity.md).
Coverage of that call is tracked in
[`docs/research_call_coverage.md`](../../docs/research_call_coverage.md). Developed by Fide AI in collaboration with The
Apologist Project, which maintains the shared condition implementation used for
local execution. Fide AI controlled the methodology, prospective lock,
credentials, confirmatory execution, analysis, evidence custody, release
decision, and claims boundary.

## The question

When a user asks for an exact quotation from an authoritative source, which
responsibilities should belong to the model, and which should belong to
retrieval or deterministic source systems?

## Design

8,640 matched observations: 20 targets × 2 prompt families × 4 conditions ×
3 editions × 6 model routes × 3 epochs. The request panel is held fixed and the
delivery path varies. The four conditions intentionally assign different
responsibilities, so pooled rates describe the staged system rather than
equal-burden treatment arms.

The exact-delivery endpoint requires strict final-output equality **and**
condition-specific evidence that the declared delivery path was followed. The
paper reports the complete corrected deterministic replay and preserves the
executed literal-parser result in an appendix audit.

## Contents

| Path | What it holds |
|---|---|
| `paper/` | LaTeX source, bibliography, generated figures, compiled PDF |
| `data/` | Deidentified 8,640-row derived scores; release-safe target registry |
| `results/` | Aggregate, target-level, bootstrap, and sensitivity results; result card |
| `provenance/` | Public release-decision summary, prospective lock, deviation summary, source editions, release manifest |
| `review/` | Blinded contextual-description reviewer packet and response template |
| `docs/` | Public research plan, claims boundary, data availability, disclosures |

## Provenance

The study was prospectively specified and internally hash-locked at
`2026-07-26T22:28:40Z`, before confirmatory execution began at
`2026-07-26T23:11:30Z`. This was an internal SHA-256 lock, not a public registry
deposit.

`provenance/source_editions.json` discloses edition identity and per-target
normalized-text digests for every edition in the locked registry. It is derived
from the source registry fixed by that lock and carries the artifact digest, so
the disclosure can be checked against a commitment made before execution. No
passage text is released.

## Open check

Materials for an independent scholarly review of all twenty contextual
descriptions are released here: protocol in
`docs/contextual_description_review_protocol.md`, blinded packet and scoring
rules in `review/`. The paper discloses the current validation as an internal
construct check rather than credentialed scholarly validation. Primary scores
are frozen, so such a review can qualify how the contextual-prompt findings are
interpreted but cannot alter any reported quantity. The check is open to anyone
qualified to perform it.

## Limits

The study does not establish a ranking of models or vendors, theological truth
or contextual appropriateness, pastoral safety, deployment readiness,
training-data membership, licensing compliance, or performance on restricted
translations. See `docs/claims_boundary.md`.
