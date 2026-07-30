# Scoring Specification v0.1

The scoring specification is designed for authoritative quotation. It evaluates whether the system
selected and delivered the requested source text faithfully, not whether the
response was eloquent, useful, contextually appropriate, or theologically
persuasive.

Selection fidelity and rendering fidelity must be reported separately. Two
outcomes anchor cross-condition interpretation:

- a common final-output equality outcome, evaluated identically in every
  condition; and
- an architecture-adherent end-to-end outcome, which additionally requires the
  process evidence applicable to the declared condition.

## Primary Endpoint and Components

- `final_output_exact` is the common binary text outcome. The complete stripped
  user-visible output must equal the requested source span under the declared
  wrapper policy.
- `end_to_end_exact` is the locked binary architecture-adherent endpoint. It
  requires `final_output_exact` plus all condition-applicable evidence: requested
  tool invocation and verified lookup in the tool condition; correct structured
  selection, source lookup, replacement, and integrity in the deterministic
  condition; and the corresponding declared gates in other conditions.
- Because the process gates differ by architecture, `end_to_end_exact` is not a
  text-only construct. Reports must show `final_output_exact` alongside it.
- Normalized matches are diagnostic and cannot substitute for either strict
  endpoint.
- `exact_text_match`: whether the complete final output matches the expected
  source text without omitted or extraneous text.
- `reference_accuracy`: whether the system identifies the correct work, chapter,
  verse, section, or span.
- `version_accuracy`: whether the output uses the requested translation, edition,
  or source version.
- `coverage_completeness`: whether the requested span is complete and no required
  portion is omitted.
- `extraneous_text_rate`: whether the quote includes source text outside the
  requested span.
- `truncation_rate`: whether the response is cut short relative to the requested
  span.
- `refusal_or_guardrail_rate`: whether the response refuses, partially refuses,
  or cites policy constraints instead of delivering text.
- `hallucinated_or_blended_quote_rate`: whether wording is invented, blended
  across versions, or paraphrased while presented as exact text.
- `structured_reference_success`: whether structured reference output is valid
  and sufficient for deterministic rendering.
- `deterministic_render_success`: whether the deterministic layer renders the
  correct authorized text from the structured reference.
- `tool_invocation_rate`: whether the configured source tool was actually used.
- `tool_bypass_rate`: whether the model answered from parametric memory despite
  tool availability.
- `placeholder_integrity`: whether a structured token was valid, recognized, and
  did not leak or collide with user content.
- `authorized_render_verification`: whether source, version, range, and final
  output are confirmed by a local oracle or independent trusted verifier.
- `partner_attestation`: a partner-reported receipt, hash, or status field that
  has not been independently verified.

Do not combine these components into a weighted primary score. Component
applicability varies by architecture and must be stated in result tables.
Risk differences for `end_to_end_exact` estimate architecture-adherent delivery,
not a pure effect on user-visible text equality.

## Normalization

Published reports must disclose normalization choices. The default public
examples support:

- exact raw comparison;
- case-insensitive comparison;
- punctuation-normalized comparison;
- whitespace-normalized comparison.

Normalization must not erase source-version differences that matter to the
scenario.

## Failure Tags

Use failure tags for diagnosis:

- `wrong_reference`
- `wrong_version`
- `partial_span`
- `extra_span`
- `paraphrase_as_quote`
- `blended_versions`
- `hallucinated_text`
- `truncated`
- `refused`
- `policy_substitution`
- `invalid_structured_reference`
- `deterministic_render_failed`
- `tool_call_bypassed`
- `malformed_placeholder`
- `placeholder_leaked`
- `source_verification_failed`
- `output_hash_mismatch`
- `source_unavailable`

## Reporting

Report metrics by system, condition, source family, prompt family, and requested
version. For deterministic systems, report both conditional rendering fidelity
among correctly selected references and end-to-end exactness across all cases.
For a purposive scenario set, inference is limited to the evaluated scenario
universe unless a separate sampling frame justifies broader claims.
Avoid model-rank claims unless the scenario set, run date, and conditions are
fully disclosed and the comparison is framed as descriptive rather than
certification.
