# Reproduction and the Private Execution Boundary

The intended public release defines the evaluation protocol, scenario schema,
scoring specification, exact executed prompts and tool contract, release-safe
provenance, deidentified derived scores, and analysis code. The repository
remains private during review. Model execution and raw-trace custody remain in
private infrastructure before and after release.

The protocol separates selection fidelity from rendering fidelity. A reproduction
should report whether the system selected the correct source/version/span, whether
authorized text was rendered exactly, and whether the final output preserved that
rendering. Deterministic rendering results should include release-safe evidence
for source authorization and output integrity where the source text cannot be
published.

The private engine is responsible for:

- calling model endpoints;
- applying private manifests;
- preserving raw outputs;
- evaluating licensed or restricted sources through authorized paths;
- producing aggregate result tables for review.

The published statistical analysis can be regenerated without private code or
network calls:

```bash
make analyze
make verify-release
```

The analysis reads `papers/p01-scripture-quotation/data/fid056_p01_deidentified_trials.csv.gz` and writes the
target-level, bootstrap, and cluster-robust result files under `papers/p01-scripture-quotation/results/`.
The released rows contain derived outcomes and experimental factors, not model
prose or authoritative passage text.

An independent end-to-end replication may implement the public prompts,
conditions, schema, and scoring specification in another runner. Exact endpoint
behavior can drift, so such a replication should record its own run dates,
route identifiers, source permissions, retries, and deviations.

For this initial study, result packages should identify
`research_program_id: FID-056` and `paper_id: FID-056-P01`. Follow-on papers must
use their own paper IDs and must not reuse Paper 1's release decision.
