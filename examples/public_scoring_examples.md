# Public Scoring Examples

These examples illustrate scoring logic. They are not raw model outputs.

## Exact Match

Prompt: quote John 3:16 in the KJV exactly.

Expected result: exact KJV text for John 3:16.

Scores:

- `exact_text_match`: true
- `reference_accuracy`: true
- `version_accuracy`: true
- `coverage_completeness`: 1.0
- failure tags: none

## Wrong Version

If a response gives modernized wording while claiming to quote the KJV:

- `exact_text_match`: false
- `reference_accuracy`: true if John 3:16 is identified
- `version_accuracy`: false
- failure tags: `wrong_version`, `paraphrase_as_quote`

## Partial Span

If a response quotes Psalm 23:1-2 when Psalm 23:1-3 was requested:

- `exact_text_match`: false
- `coverage_completeness`: less than 1.0
- failure tags: `partial_span`

## Structured Reference Success

For an indirect request such as "where Jesus compares himself to the serpent
Moses lifted up," a structured-reference condition succeeds if it returns a
valid reference for John 3:14-15 and enough version metadata for deterministic
rendering.

Failure to render text directly is not a failure in this condition when the
protocol asks the model to return reference JSON only.

