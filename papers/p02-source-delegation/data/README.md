# Paper 02 Data

The release dataset contains one deidentified derived row for each retained
confirmatory observation. It preserves treatment assignment, prompt family,
target stratum, model-family route, repetition, completion status, observed
delegation outcomes, quotation outcomes, and release-safe provenance digests.

- `fid056_p02_deidentified_trials.csv.gz` contains the 4,800 derived rows.
- `fid056_p02_targets.jsonl` contains the 20 target identifiers, references,
  passage strata, and contextual descriptions used to construct prompts.
  Known adjacent and intertextual pairs are identified through
  `correlated_target_ids` and `correlation_note`.

It excludes raw model text, provider response identifiers, credentials, source
passage text, and private execution paths. A release manifest reconciles the
derived rows to the sealed private evidence inventory.

The field `source_result_used` is retained as the locked instrumentation name.
Operationally it means that fixture text appears in the final completion under
the declared string comparison. It does not by itself establish that the model
causally relied on a tool result and is interpreted as source-text presence.

The field `text_before_source` is also retained as executed. Its implementation
counted serialized reasoning content and, when no call occurred, the final
assistant answer. It is therefore not used as evidence that visible quotation
text preceded retrieval. The retrospective aggregate audit is documented in
the protocol and paper without releasing private response text.
