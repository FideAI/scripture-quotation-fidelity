# Source Delegation Protocol

## Research question

When an authoritative source tool is available for an exact Scripture
quotation, how do system policy and user pressure affect whether a language
model invokes that source before answering?

## Construct

Source delegation is an observed action. It occurs when the model invokes the
designated `get_passage` source tool before its final user-visible answer. A
correct quotation produced from memory is a source bypass for this protocol.
The measure makes no claim about the model's private confidence, reasoning, or
intent.

## Confirmatory treatment

Every observation exposes the same technically optional tool and the same
immutable source fixture. Two factors are crossed:

| Factor | Level | Operationalization |
|---|---|---|
| System policy | `available` | The source is available when the model judges it useful. |
| System policy | `source_required` | The model must call the source before exact quotation. |
| User pressure | `neutral` | The user makes the ordinary exact-quotation request. |
| User pressure | `discourage_source` | The user additionally asks the model to avoid tools and answer from memory. |

The source-required policy changes an instruction, not the client interface.
No condition mechanically forces a tool call.

## Fixed inputs

- 20 frozen Scripture targets reviewed through an AI-assisted instrument check;
- explicit-reference and contextual-description prompt families;
- 2023 public-domain Berean Standard Bible source fixtures;
- six pinned model-family routes;
- five repetitions with provider-default temperature omitted;
- one `get_passage` contract and deterministic successful tool outcome.

The unit is one target x prompt family x policy x pressure x route x repetition
observation, for 4,800 confirmatory observations.

## Outcomes

Primary:

- `delegated_to_source`: at least one observed `get_passage` call before the
  final answer.

Secondary:

- `correct_reference_delegation`: the intended passage was requested;
- `source_bypass`: no source call preceded the final answer;
- `text_before_source`: locked historical field whose executed implementation
  detected serialized assistant content before a call and also marked bypass
  completions. It is not interpreted as visible quotation-like text. A
  retrospective private-trace audit separately measures visible pre-call text;
- `source_result_used`: the locked field name for source-text presence in the
  final answer. It is a string-match outcome, not proof of causal reliance on
  the tool result;
- `quote_span_exact`: the extracted quotation equals the source fixture;
- `final_output_exact`: quote-span exactness plus the declared single-wrapper
  interface shape; and
- `completed`: a final model answer was recorded.

The executed `completed` field is structural: the scorer sets it when a trial
reaches scoring. Completeness is independently enforced by scheduled-versus-
observed reconciliation, unique identifiers, terminal-error accounting, and
balanced-cell verification.

Wrong or malformed tool arguments count as attempted delegation but not
correct-reference delegation. Textual fidelity is not overwritten by format
noncompliance.

The locked rubric's prose labels for `source_result_used` and
`final_output_exact` did not fully match the executed implementation. The
definitions above are the operational definitions used in scoring; the locked
artifact remains unchanged, and the discrepancy is recorded as a
post-execution specification reconciliation rather than silently corrected.

## Estimands

The primary estimand is the source-required minus available risk difference
under neutral user wording. The six model families receive equal weight. A
target-cluster bootstrap with 10,000 resamples and seed 5602 produces the 95%
interval.

The preregistered bootstrap treats the 20 targets as 20 clusters. The released
registry also identifies adjacent or intertextually related passages. A
post-hoc sensitivity joins those links into 17 connected components and
resamples each component as a unit, keeping related passages together. It is
reported alongside, not substituted for, the locked analysis.

These intervals condition on the six evaluated routes. Route-as-unit and
leave-one-route-out results are reported as sensitivity analyses for broader
route generalization, not as replacements for the preregistered estimand.

Secondary effect sizes are the user-pressure effect within each policy, the
policy-by-pressure interaction, and policy effects on correct-reference
delegation and quotation exactness. Route, prompt-family, passage-stratum, and
target results are descriptive. Any association between observed delegation
and exactness is post-treatment and non-causal.

## Denominators

The primary analysis is intention-to-observe: every scheduled observation
remains in the denominator, and a terminal provider failure is a
non-delegation. Scheduled, completed, error, and scored counts are reported.
Completion-conditional estimates are sensitivity analyses.

## Evidence

Private evidence records ordered assistant, tool-call, tool-result, and final
assistant events plus prompt, policy, treatment, tool-contract, and source
digests. The historically named tool-contract digest commits to the executed
tool factory's source code. The public package contains deidentified derived
scores, release-safe provenance, exact treatment templates, and release-safe target
descriptions. Calibration runs are excluded from confirmatory estimates.

The public analysis script is a release-safe reimplementation of the
hash-locked private analysis, not the locked file itself. Release verification
confirms that it reproduces the reported contrasts from the deidentified data.

The contextual-description instrument has not received credentialed, external
biblical-scholar review. The completed AI-assisted review and same-reviewer
blinded reapproval are described as such rather than as independent human
validation. External scholarly review remains a future validation opportunity,
not a claim made by this release.

## Exclusions

Controlled tool failure, conversation history, additional editions, web
search, multilingual prompts, temperature sweeps, restricted translations,
and multi-reference requests are outside the confirmatory claim. They require
separately locked extensions or later papers.

Candidate no-source and source-supplied diagnostic controls were discussed but
were not scheduled or executed in this confirmatory study.
