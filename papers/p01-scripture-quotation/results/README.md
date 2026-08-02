# Results

This directory contains reviewed, release-safe result artifacts for
`FID-056-P01`. The public derived-score input used to regenerate these tables
is in `data/`.

- `fid056_p01_result_card.md` gives the study scope, primary findings,
  interpretation, integrity disclosures, and claims boundary.
- `fid056_p01_aggregate_results.csv` provides machine-readable locked and
  corrected aggregate counts plus descriptive prompt, edition, passage, and
  model-family interactions.
- `fid056_p01_target_level_results.csv` reports outcomes by target and
  condition.
- `fid056_p01_target_distribution_summary.csv` summarizes the distribution of
  target-level rates.
- `fid056_p01_cluster_bootstrap.csv` reproduces the prospectively specified
  target-cluster bootstrap.
- `fid056_p01_cluster_robust_sensitivity.csv` reports a post-hoc
  target-cluster-robust fixed-panel sensitivity analysis.
- `fid056_p01_permissive_parser_replay.csv` and `.json` reconcile the complete
  deterministic replay with the originally executed literal-parser outcome.

Do not commit raw model outputs, private partner traces, held-out prompts,
restricted source text, provider credentials, or licensed-source payloads.

Each result package must include:

- research program ID and paper ID;
- protocol version;
- scoring-spec version;
- scenario coverage;
- system identifiers;
- run dates;
- access paths;
- condition names;
- aggregate metrics;
- known exclusions or failed calls.

The current files are derived paper artifacts, not raw execution output. They
follow `docs/repository_boundary.md` at the repository root. This directory must never be used as the
output directory for either organization's execution harness.
