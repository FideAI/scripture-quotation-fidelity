# Scoring Specification v0.1

The scoring specification is designed for authoritative quotation. It evaluates whether the system
selected and delivered the requested source text faithfully, not whether the
response was eloquent, useful, contextually appropriate, or theologically
persuasive.

Selection fidelity and rendering fidelity must be reported separately. Two
outcomes anchor cross-condition interpretation:

- a common final-output equality outcome, evaluated identically in every
  condition; and
- a path-adherent end-to-end outcome, which additionally requires the
  process evidence applicable to the declared condition.

## Primary Endpoint and Components

- `locked_final_output_exact` is the originally executed common binary text
  outcome. `corrected_final_output_exact` applies the disclosed parser replay
  to deterministic observations and is the paper's common text outcome.
  `final_output_exact` remains a backward-compatible alias for the locked field.
  In either form, the complete stripped user-visible output must equal the
  requested source span under the declared wrapper policy.
- `locked_end_to_end_exact` is the originally executed literal-parser endpoint.
  `corrected_end_to_end_exact` is the paper's main endpoint after complete
  parser replay. `end_to_end_exact` remains a backward-compatible alias for the
  locked field. Both require the corresponding final-output outcome plus all
  condition-applicable evidence: requested
  tool invocation and verified lookup in the tool condition; correct structured
  selection, source lookup, replacement, and integrity in the deterministic
  condition; and the corresponding declared gates in other conditions.
- Because the process gates differ by delivery condition, the end-to-end
  outcomes are not text-only constructs. Reports must show the corresponding
  final-output outcome alongside them.
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
applicability varies by delivery condition and must be stated in result tables.
Risk differences for the end-to-end outcomes estimate path-adherent delivery,
not a pure effect on user-visible text equality.

## Interface Compliance and Semantic Selection

For structured-reference conditions, reports must distinguish literal grammar
compliance from whether one unambiguous requested reference can be recovered.
A response must not be labeled a wrong-reference failure solely because it adds
a redundant textual edition annotation to an otherwise valid reference.

Any parser-adjusted analysis must:

- preserve and report the originally locked interface score;
- state whether the parser rule was prospective or post hoc;
- replay all eligible saved responses, not only inspected failures;
- reject ambiguous payloads containing a second reference or alternate range;
- use the original fixed source fixtures and make no new model calls; and
- release enough per-response classifications and parser provenance to
  reconcile the adjusted result without exposing withheld text.

The Paper 01 implementation correction follows these rules. The paper reports
the complete corrected replay as its substantive exact-delivery result and
preserves the executed literal-interface result as an appendix audit.

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
