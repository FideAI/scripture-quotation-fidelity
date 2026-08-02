# Data and Code Availability

The repository remains private during manuscript review. At public release, it
will provide the complete 8,640-row deidentified derived-score dataset used for
the reported quantitative analysis, a release-safe target registry, exact
executed prompt templates, the functional tool schema, target-level and
aggregate tables, provenance receipts, the source-edition record, and
standalone analysis code.

The source-edition record (`provenance/source_editions.json`) discloses
edition identity for every edition in the locked registry: provider and
provider-side source identifier, edition designation, rights basis, execution
status, and a normalized-text SHA-256 digest for each of the twenty targets.
It contains no passage text, so restricted editions appear as excluded without
releasing their wording. It is derived from the source registry fixed by the
prospective lock and carries that artifact's digest, so a reviewer can confirm
the disclosure matches a commitment made before confirmatory execution. A
replicator can hash their own whitespace-collapsed copy of a passage and
compare it against these digests to confirm they hold the same edition text.

The planned release does not include model-generated prose, authoritative passage
text, provider response identifiers, raw tool traces, credentials, restricted
translation payloads, or either organization's execution-engine source code.
These exclusions protect source rights, credentials, partner boundaries, and
raw-response custody while retaining the factors and derived outcomes needed
to reproduce every quantitative result reported in the paper.

The statistical outputs can be regenerated with:

```bash
make analyze
make verify-release
```

An exact rerun against hosted models is not guaranteed because endpoints,
routing, provider defaults, and model behavior can change. Independent
replications should record their own route metadata and run dates.
