# Authoritative Quotation Evaluation Methodology

## Purpose

This methodology studies how AI systems respond when a user requests an exact
quotation from an authoritative, canonical, or rights-constrained source.

It is the shared methodology for the FID-056 research program and initially
governs Paper `FID-056-P01`. Later papers may reuse the vocabulary and schema but
require separate questions, scenarios, and release decisions.

The evaluation is not a leaderboard. It separates source
identification, source authorization, and final text rendering so that system
behavior can be evaluated without treating model fluency as source fidelity.

## Research Question

When a user asks for an exact quotation from an authoritative source, which
responsibilities should belong to the model, and which should belong to
retrieval or deterministic source systems?

The methodology separates three claims:

- **Selection fidelity:** the requested source, version, and span were correctly
  identified.
- **Rendering fidelity:** the authorized source text was delivered without
  alteration, truncation, or substitution.
- **Output integrity:** the final user-visible output faithfully reflects the
  authorized rendering.

An exact quotation requires all three. A deterministic renderer can make
rendering highly reliable without proving that the selected passage is
contextually or theologically appropriate.

## Study Domain

Paper 01 studies English Scripture quotation as a substantive faith-domain
problem. Exact wording matters in Christian study, teaching, worship,
memorization, and pastoral communication. Scripture also supports rigorous
evaluation because:

- references are structured;
- exact wording matters;
- different editions and translations are not interchangeable;
- public-domain and restricted editions coexist;
- long quotations may trigger provider-side guardrails;
- indirect requests require reference detection, not only text generation.

The methodology can support separate studies of other sacred texts, legal
clauses, standards, clinical references, regulatory text, policy manuals,
contract provisions, and other canonical or rights-constrained source
materials. Paper 01's empirical results remain specific to its English
Scripture corpus.

## Evaluation Conditions

For causal comparison of architecture conditions, scenario construction must be
crossed: the same target and user request formulation appears under every
eligible condition. Source context, tools, and structured-output instructions
are supplied by the harness rather than written as different user requests.

The protocol distinguishes five system behaviors:

1. `native_parametric_quote`: the model is asked to quote directly without tools
   or source text.
2. `source_supplied_quote`: the prompt includes source text, simulating a simple
   source-supplied or retrieval-augmented condition.
3. `tool_call_quote`: the model is expected to invoke an authorized source tool;
   tool invocation and tool bypass are recorded separately.
4. `reference_token_then_replace`: the model outputs structured reference data;
   a deterministic layer renders exact text from an authorized corpus. A
   streaming output buffer may intercept the reference token and replace it
   before final delivery.
5. `licensed_or_partner_delivery`: a separately identified external system or licensed service
   receives the same user request and returns final user-visible text with
optional metadata.

Fide-controlled reference implementations form the main comparison. External
partner systems are separate evidence streams and do not define the baselines.

## Scenario Families

Public examples use these families:

- explicit single verse or short source span;
- explicit multi-verse source span;
- longer source span likely to reveal truncation or refusal behavior;
- indirect/event-style request requiring reference detection;
- translation/version-sensitive request;
- source-supplied request where the model must preserve provided wording;
- robustness requests involving instruction overrides, malformed or duplicated
  reference tokens, token collisions, range confusion, and attempts to force
  direct quotation across the rendering boundary.

## Minimum Scenario Fields

Each scenario should include:

- stable scenario id;
- domain;
- source family;
- source work;
- requested version or edition;
- prompt family;
- user-facing prompt;
- expected reference;
- expected source text when rights permit publication;
- expected behavior condition;
- license or provenance note;
- release split.

## Reporting Expectations

Any published run should disclose:

- research program ID and paper ID;
- protocol version;
- scenario coverage;
- source editions or translations requested;
- model or system identifiers;
- run date;
- access path;
- prompts and system conditions when publishable;
- scoring-spec version;
- any filtering, repair, abstention, or failed responses;
- selection-fidelity and rendering-fidelity results separately;
- tool invocation or bypass evidence where applicable; and
- release-safe source verification or output hashes for restricted text.

## Claim Boundary

Results apply only to named systems, run dates, scenario sets, source editions,
and scoring rules. They do not establish theological correctness, pastoral
safety, legal compliance, deployment readiness, or product endorsement.
