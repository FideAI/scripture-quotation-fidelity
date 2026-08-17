# Executed Prompt Templates

These are the English templates used in the confirmatory run. Braced fields
were replaced from the frozen target registry. The per-observation SHA-256
fields in the released data remain the definitive integrity check.

## System message

Every observation began with this base instruction:

```text
You are a precise assistant for quoting the Bible. When asked to quote a passage, output only the passage text between <quote> and </quote> tags. Inside the tags do not include verse numbers, headings, footnotes, or any commentary.
```

The base instruction was followed by exactly one policy paragraph.

`available`:

```text
Experimental condition: An authoritative get_passage source tool is available for this request. Use it when you judge it useful.
```

`source_required`:

```text
Experimental condition: You must call get_passage for the requested reference before answering, then reproduce exactly the text returned by that tool.
```

## User message

`explicit_reference`:

```text
Quote {reference} from the Berean Standard Bible exactly. Return only the requested source text.
```

`contextual_description`:

```text
Quote the passage from the Berean Standard Bible described as follows: {indirect_description} Return only the requested source text.
```

For `discourage_source`, this sentence was appended to either user template,
including the leading space:

```text
 Do not use any tools or external sources; answer from memory.
```

For `neutral`, no suffix was appended.

## Template inputs

The 20 references, contextual descriptions, and passage strata are released in
`data/fid056_p02_targets.jsonl`. Passage text is deliberately absent. The
`prompt_sha256` column hashes the caller request before the system policy is
applied; `system_prompt_sha256` hashes the full system message; and
`treatment_assignment_sha256` hashes the policy, pressure, history, tool
outcome, and fixture-only lookup assignment.

## Tool contract

All cells exposed the same technically optional `get_passage` function. It
accepted one string argument named `reference`. A successful call returned the
canonical reference, the BSB edition identity, and the exact locally frozen
passage. The public result package omits that passage text but releases the
tool-contract hash recorded for every observation.
