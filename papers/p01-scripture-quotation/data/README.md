# Released Data

`fid056_p01_deidentified_trials.csv.gz` contains one row for each of the 8,640
scheduled observations. It includes experimental factors, terminal-error
status, derived scoring fields, failure tags, release-safe digests, token
usage, and provider-reported cost. It excludes generated prose, authoritative passage text, provider
response identifiers, credentials, and raw tool traces.

`fid056_p01_targets.jsonl` contains the twenty public target references,
passage strata, and contextual descriptions used in the executed study.

The release identifier is a one-way digest derived from the private trial
identifier and a study-specific namespace. It is intended for row-level
integrity checks, not linkage back to provider records.

Terminal provider errors remain rows in the dataset and carry zero for strict
delivery outcomes, matching the intention-to-observe denominator. Empty
component fields mean that the component was not observed or did not apply;
they must not be silently converted into successful outcomes.

The dataset is a derived-score release, not raw execution data. See
`protocol/release_policy.md` at the repository root and `docs/data_availability.md` in this paper directory.
