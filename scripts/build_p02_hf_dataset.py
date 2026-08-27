# /// script
# requires-python = ">=3.12"
# dependencies = ["pandas", "pyarrow"]
# ///
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fide AI
"""Stage the Paper 02 derived outcomes for the Hugging Face Hub."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers/p02-source-delegation"
TRIALS = PAPER / "data/fid056_p02_deidentified_trials.csv.gz"
TARGETS = PAPER / "data/fid056_p02_targets.jsonl"
OUT = ROOT / "build/huggingface/p02-source-delegation"

FORBIDDEN = {
    "content",
    "generated_text",
    "raw_output",
    "source_text",
    "passage_text",
    "response",
    "response_id",
    "provider_response_id",
    "tool_calls",
    "tool_trace",
    "prompt",
    "system_prompt",
}

CARD = """---
license: cc-by-4.0
language:
  - en
size_categories:
  - 1K<n<10K
task_categories:
  - text-generation
tags:
  - evaluation
  - tool-use
  - source-delegation
  - quotation-fidelity
  - scripture
  - reproducibility
configs:
  - config_name: trials
    data_files: trials.parquet
    default: true
  - config_name: targets
    data_files: targets.parquet
---

# Scripture Quotation Fidelity — Paper 02 derived outcomes

Trial-level derived outcomes from **“Knowing When to Defer: How Language Models
Use and Bypass Sources of Record”** (FID-056-P02).

The controlled study contains 4,800 exact Scripture quotation requests. It
crosses two source-policy conditions, two user-pressure conditions, two prompt
families, six model-family routes, five repetitions, and twenty passage targets.

- Paper, protocol, and analysis: https://github.com/FideAI/scripture-quotation-fidelity
- Research call: [FID-056, Formal Verification for Sacred Text Fidelity](https://github.com/FideAI/research-ideas/blob/main/ideas/FID-056-formal-verification-sacred-text-fidelity.md)

## What this is not

**No source passage text and no model output are included.** The dataset contains
derived behavioral outcomes, safe target metadata, and SHA-256 digests. It does
not support reconstructing provider transcripts or the authoritative source.

The release supports reanalysis of the paper's reported quantities. It is not a
model leaderboard, a product endorsement, or evidence of theological quality.

## Configs

| Config | Rows | What it holds |
|---|---|---|
| `trials` | 4,800 | One row per target × prompt family × policy × pressure × route × repetition |
| `targets` | 20 | Release-safe reference, stratum, contextual-description, and correlation metadata |

## Design

The source tool remained technically optional in every cell. The system policy
either said the authoritative source was available when useful or instructed
the model that it must call the source before answering. User wording was either
neutral or explicitly discouraged tool use and requested an answer from memory.

The primary endpoint, `delegated_to_source`, records whether a source call was
observed before the user-visible answer. Secondary outcomes distinguish correct
reference selection, use of the returned source, exact quote span, and exact
final output.

## Headline results

| Source policy | User request | Delegated |
|---|---|---|
| Available | Neutral | 95.1% |
| Required | Neutral | 95.0% |
| Available | Avoid tools | 30.6% |
| Required | Avoid tools | 84.7% |

Among 3,664 delegated observations, 89.1% requested the intended reference.
Conditional on correct-reference delegation, 93.5% reproduced the requested
quote span exactly.

## Reproducing the primary cells

```python
import pandas as pd

df = pd.read_parquet("trials.parquet")
(
    df.groupby(["delegation_policy", "user_pressure"])["delegated_to_source"]
      .mean()
      .mul(100)
      .round(1)
)
```

## Limits

Results apply to the named endpoints and run window, a purposive twenty-target
English Scripture panel, one public-domain source edition, and the declared
treatments. They do not establish enduring vendor behavior, theological
correctness, exegetical quality, pastoral safety, deployment readiness, or
performance on other translations, languages, sacred texts, or domains.

## Citation

```bibtex
@misc{chao2026knowingwhentodefer,
  title  = {Knowing When to Defer: How Language Models Use and Bypass
            Sources of Record},
  author = {Chao, Alex},
  year   = {2026},
  note   = {Fide AI. Study FID-056-P02.},
  url    = {https://github.com/FideAI/scripture-quotation-fidelity}
}
```

## License

CC BY 4.0. No source passage text or model output is redistributed.
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    trials = pd.read_csv(TRIALS)
    leaked = FORBIDDEN.intersection(column.lower() for column in trials.columns)
    if leaked:
        raise SystemExit(
            f"Refusing to stage raw-content columns: {sorted(leaked)}"
        )
    if len(trials) != 4_800:
        raise SystemExit(f"Expected 4,800 rows, found {len(trials):,}")

    required = {
        "delegation_policy",
        "user_pressure",
        "delegated_to_source",
        "correct_reference_delegation",
        "quote_span_exact",
        "final_output_exact",
    }
    missing = required - set(trials.columns)
    if missing:
        raise SystemExit(f"Missing required outcome columns: {sorted(missing)}")

    observed = (
        trials.groupby(["delegation_policy", "user_pressure"])[
            "delegated_to_source"
        ]
        .sum()
        .to_dict()
    )
    expected = {
        ("available", "neutral"): 1_141,
        ("available", "discourage_source"): 367,
        ("source_required", "neutral"): 1_140,
        ("source_required", "discourage_source"): 1_016,
    }
    if observed != expected:
        raise SystemExit(f"Delegation counts do not match the paper: {observed}")

    targets = pd.DataFrame(
        json.loads(line) for line in TARGETS.read_text().splitlines() if line.strip()
    )
    if len(targets) != 20:
        raise SystemExit(f"Expected 20 targets, found {len(targets):,}")
    target_leaks = FORBIDDEN.intersection(column.lower() for column in targets.columns)
    if target_leaks:
        raise SystemExit(
            f"Refusing to stage target raw-content columns: {sorted(target_leaks)}"
        )

    trials.to_parquet(OUT / "trials.parquet", index=False)
    targets.to_parquet(OUT / "targets.parquet", index=False)
    (OUT / "README.md").write_text(CARD)

    print(f"Staged {OUT.relative_to(ROOT)}/")
    print(f"  trials.parquet   {len(trials):,} rows x {len(trials.columns)} cols")
    print(f"  targets.parquet  {len(targets):,} rows x {len(targets.columns)} cols")
    print("  README.md        dataset card")
    print()
    print("Publish with:")
    print("  uv run --with huggingface_hub hf upload-large-folder \\")
    print("    --repo-type=dataset FideAI/scripture-quotation-fidelity-p02 \\")
    print("    build/huggingface/p02-source-delegation")


if __name__ == "__main__":
    main()
