# Public Examples

Illustrative scenarios showing the shape of the protocol. **These are not the
study data.**

| | Here | Paper 01 study data |
|---|---|---|
| Purpose | Illustrate the schema | The executed experiment |
| Location | `examples/public_scenarios.jsonl` | `papers/p01-scripture-quotation/data/fid056_p01_targets.jsonl` |
| Edition | KJV, public domain | BSB, WEBU, LSV |
| Passage text | Included | Never included; digests only |
| Protocol version | `0.1` | The version fixed by the Paper 01 prospective lock |

These examples carry passage text because the KJV is public domain in the
United States, which makes them suitable for a compact, self-contained example.
The evaluated editions are also open for use: BSB and WEBU are public domain,
and LSV is openly licensed. Their wording is omitted from the study package as
a deliberate, consistent release boundary; passage identity is disclosed
through digests instead.

The condition vocabulary here (`native_parametric_quote`) predates the study's
executed vocabulary (`native_parametric` in the `condition` column,
`unassisted` in `executed_method`). Read these files as a schema illustration,
not as a key to the released dataset. For the dataset's own vocabulary, see
`papers/p01-scripture-quotation/data/README.md`.

## Files

- `public_scenarios.jsonl` — seven example scenarios across explicit,
  multi-span, and version-sensitive request families
- `public_scoring_examples.md` — worked scoring illustrations

## Rights

KJV wording is public domain in the United States. Verify local rights status
before redistributing outside the United States. See `NOTICE`.
