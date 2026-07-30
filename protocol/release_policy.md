# Release Policy

This repository is an open evaluation protocol and methodology artifact. It is
not a public execution engine and not a product comparison site.

Every result package produced under a multi-paper call should identify its
`research_program_id` and `paper_id`. Approval applies only to that paper's
artifacts and claims.

## Public by Default

- Paper draft and references.
- Protocol documentation.
- Scoring specification.
- Scenario schema.
- Public-domain example scenarios.
- Aggregate result tables after review.
- Deidentified trial-level derived scores after an explicit release decision,
  provided that generated prose, source text, response identifiers, raw tool
  traces, credentials, and restricted-source payloads are absent.
- Standalone analysis code and release-safe provenance receipts.
- Claim-boundary and responsible-use documentation.

## Private by Default

- `fide-eval-engine` source code.
- Raw model outputs.
- Held-out prompts.
- Partner traces.
- Private product outputs.
- API credentials.
- Restricted source text.
- Licensed-source payloads.
- Partner and Fide execution-harness source code.
- Trial-level handoff packages before an explicit release decision.
- Trial-level generated text, source text, provider response identifiers, and
  raw tool traces even when derived scores are released.

The detailed repository and artifact promotion boundary is defined in
`docs/repository_boundary.md`.

## Restricted Sources

Restricted translations, editions, or source works may be evaluated only through
authorized APIs, private licensed access, hashes, verification receipts, or
aggregate metrics that do not expose restricted text.

## Companion Publications

Partners may publish their own companion posts describing their systems or
solutions. Fide AI's public research artifact should remain independent,
methodology-focused, and clear about what was and was not evaluated.

## Multi-Paper Boundary

Diagnostic findings may motivate another paper, but cannot be promoted into a
new primary claim after results are observed. Follow-on papers require separate
charters, preregistrations, source permissions, and release decisions.
