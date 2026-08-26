# Reproduction and the Private Execution Boundary

The public research package defines the evaluation protocol, scenario schema,
scoring specification, exact executed prompts and tool behavior, release-safe
provenance, deidentified derived scores, and analysis code. The execution
engine and raw-trace custody remain in private infrastructure before and after
the repository is released.

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
make verify
```

Paper 01 analysis reads
`papers/p01-scripture-quotation/data/fid056_p01_deidentified_trials.csv.gz`.
Paper 02 analysis reads
`papers/p02-source-delegation/data/fid056_p02_deidentified_trials.csv.gz`.
Each writes its tables beneath the corresponding paper's `results/` directory.
The released rows contain derived outcomes and experimental factors, not model
prose or authoritative passage text. Paper 02 additionally releases prompt,
system-message, and treatment-assignment digests so the public verifier can
reconstruct all 4,800 experimental assignments without provider access. Its
historically named tool-contract digest commits to the executed partner tool
factory's source code and is verified against the pinned public revision; it is
not presented as a locally reconstructable digest of a provider-neutral schema.

An independent end-to-end replication may implement the public prompts,
conditions, schema, and scoring specification in another runner. Exact endpoint
behavior can drift, so such a replication should record its own run dates,
route identifiers, source permissions, retries, and deviations.

Result packages identify `research_program_id: FID-056` and a paper-specific
identifier such as `FID-056-P01` or `FID-056-P02`. Follow-on papers must use
their own paper IDs, prospective records, evidence, and release decisions.
