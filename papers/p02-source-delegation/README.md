# Paper 02 - Source Delegation

**Knowing When to Defer: How Language Models Use and Bypass Sources of Record**

Study identifier `FID-056-P02`. This paper follows Paper 01's finding that a
tool can be present without being used correctly. It isolates the prior
behavioral question: when an authoritative source tool is optional, what makes
a model use it before quoting Scripture rather than answer from memory?

## Confirmatory design

The same 20 frozen passage targets are crossed with two prompt
families, two system-policy levels, two user-pressure levels, six model-family
routes, and five repetitions. The Berean Standard Bible is the sole source
edition in the confirmatory phase. The designated source tool remains
technically optional in every cell.

The contextual descriptions received an AI-assisted review and same-reviewer
blinded reapproval of six revisions. Credentialed external biblical-scholar
validation remains an open release gate and is not claimed as complete.

The primary endpoint is an observed action: whether the model invokes the
source tool before its user-visible answer. The primary contrast is the effect
of a source-required system policy, relative to neutral source availability,
under neutral user wording. Anti-tool user pressure and the policy-by-pressure
interaction are secondary contrasts.

This is a controlled factorial study of source delegation within the declared
setting. It is not a model leaderboard, a test of theological interpretation,
or a claim that tool use alone guarantees correct quotation.

Exact executed templates are documented in
`docs/prompt_templates.md`, and the release-safe target inputs are in
`data/fid056_p02_targets.jsonl`.

## Repository boundary

This public-intended package will contain the manuscript, deidentified derived
scores, aggregate results, figures, prospective lock receipt, and analysis
needed to reproduce reported quantities without calling a model endpoint. Raw
model traces, credentials, private execution code, and source passage text
remain outside this repository.

## Reproduce

From the repository root:

```bash
make p02-analyze  # regenerate aggregates and bootstrap intervals
make p02-paper    # rebuild figures and compile with Tectonic
make p02-manifest # reseal the reviewed public package after final changes
make p02-verify   # check the balanced data and every release hash
```

These commands make no model or source API calls.

## Release gate

This remains a private manuscript draft. The pinned shared implementation
revision is publicly reachable at partner commit
[`dbb1514`](https://github.com/apologist-project/llm-scripture-fidelity/commit/dbb1514cde5c7a8e17944d09cf16d0ed1ee619cc).
The release manifest must be regenerated after final review.
