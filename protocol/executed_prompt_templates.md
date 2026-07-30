# Executed Prompt Templates

These are the English templates executed in `FID-056-P01`. Bracketed fields are
runtime substitutions. The shared implementation was pinned at commit
`b67849d55181fdffb3ee28d405733dd5eb35e4bc`.

## Common System Instruction

```text
You are a precise assistant for quoting the Bible. When asked to quote a
passage, output only the passage text between <quote> and </quote> tags. Inside
the tags do not include verse numbers, headings, footnotes, or any commentary.
```

One of the following condition instructions was appended after a blank line and
the literal prefix `Experimental condition: `.

### Native Parametric

```text
Do not use tools or external sources. Produce the requested quotation from model
knowledge.
```

### Source Supplied

```text
Treat text inside <authoritative_source> as the source of record. Reproduce
exactly the span requested inside <user_request>.
```

### Tool Mediated

```text
You must call get_passage for the requested reference before answering, then
reproduce exactly the text returned by that tool.
```

### Deterministic Rendering

```text
Infer the passage reference from the user request and do not produce passage
text. Your entire response must be exactly
<quote>{{QUOTE:<reference>}}</quote>, replacing <reference> with your selection.
Preserve both opening braces and both closing braces in the placeholder.
```

## Caller Prompt Families

### Explicit Reference

```text
Quote [REFERENCE] from the [TRANSLATION DISPLAY NAME] exactly. Return only the
requested source text.
```

### Contextual Description

```text
Quote the passage from the [TRANSLATION DISPLAY NAME] described as follows:
[INDIRECT DESCRIPTION] Return only the requested source text.
```

Caller wording was identical across conditions for a matched cell.

## Source-Supplied User Input

Only the source-supplied condition wrapped the caller prompt with authoritative
text:

```text
<authoritative_source>
[AUTHORITATIVE PASSAGE TEXT]
</authoritative_source>

<user_request>
[CALLER PROMPT]
</user_request>
```

The passage text is omitted from this public template. The release dataset
contains its SHA-256 digest for every source-supplied trial. BSB and WEBU source
text can be independently fetched under their public-domain status. LSV text
must be handled under its CC BY-SA terms.

## Sampling and Turn Policy

- Language: English.
- Requested temperature: omitted for every route; the provider default applied.
- Maximum generated tokens: provider default.
- Native, source-supplied, and deterministic conditions: one model turn.
- Tool condition: at most two model turns, with at most one executable
  `get_passage` call before a final no-tools generation turn.
- Semantic retries: zero.
- Transport retries: bounded separately and retained as execution provenance.

The exact target substitutions are in
`papers/p01-scripture-quotation/data/fid056_p01_targets.jsonl`. The tool schema is in
`protocol/executed_tool_schema.json`.
