# /// script
# requires-python = ">=3.12"
# dependencies = ["pandas", "pyarrow"]
# ///
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fide AI
"""Stage the Paper 01 derived-score dataset for the Hugging Face Hub.

Writes parquet (so the Hub dataset viewer renders it) plus a dataset card, into
build/huggingface/. Nothing is uploaded; publishing is a separate, deliberate
step.

The released file contains derived scores and content digests only. No model
prose and no authoritative passage text ever enters it, which is what makes it
publishable at all. This script re-checks that invariant rather than trusting
it, because the Hub is not a place to discover you were wrong.

Usage:
  uv run --script scripts/build_hf_dataset.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers/p01-scripture-quotation"
TRIALS = PAPER / "data/fid056_p01_deidentified_trials.csv.gz"
TARGETS = PAPER / "data/fid056_p01_targets.jsonl"
OUT = ROOT / "build/huggingface"

# Columns that must never appear: raw text of any kind.
FORBIDDEN = {
    "content", "generated_text", "raw_output", "source_text", "passage_text",
    "response", "response_id", "tool_calls", "tool_trace", "prompt",
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
  - retrieval-augmented-generation
  - tool-use
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

# Scripture Quotation Fidelity — Paper 01 derived scores

Trial-level derived scores from **"When Not to Generate: How AI Systems Quote
Scripture, and What Authoritative Quotation Requires"** (FID-056-P01).

8,640 matched requests for English Scripture passages, each routed through one
of four delivery conditions, scored for whether the user-visible output exactly
matched the requested edition and whether the declared delivery path was
actually followed.

- Paper and code: https://github.com/FideAI/scripture-quotation-fidelity
- Research call: [FID-056, Formal Verification for Sacred Text Fidelity](https://github.com/FideAI/research-ideas/blob/main/ideas/FID-056-formal-verification-sacred-text-fidelity.md)

## What this is not

**No passage text and no model output are included.** Passages and outputs are
represented by SHA-256 digests only. You cannot reconstruct Scripture text,
model responses, or prompts from this dataset, and that is deliberate: source
editions carry rights obligations and raw traces carry custody obligations.

This dataset supports reanalysis of the reported results. It does not support
training, text reconstruction, or claims about model quality beyond the
declared conditions.

## Configs

| Config | Rows | What it holds |
|---|---|---|
| `trials` | 8,640 | One row per target x prompt x condition x edition x model route x epoch |
| `targets` | 20 | The passage panel: reference, stratum, and contextual description |

## Design

Each of 20 passages was requested under every combination of:

- **4 delivery conditions** — two columns name these. `condition` is the analysis
  label; `executed_method` is the engine's label for the same thing:

  | `condition` | `executed_method` | What the system does |
  |---|---|---|
  | `native_parametric` | `unassisted` | Quotes from memory |
  | `source_supplied` | `rag` | Gold passage supplied in context to copy; no retrieval is performed |
  | `tool_mediated` | `tool_call` | Authorized lookup tool |
  | `deterministic_rendering` | `buffer_transform_selection` | Model names the passage; non-generative code inserts the text |

- **2 prompt families** — explicit reference, contextual description
- **3 editions** — BSB, WEBU, LSV (all open-licensed)
- **6 model routes** — one per model family
- **3 epochs**

## Headline results

| Delivery condition | Exact delivery |
|---|---|
| Quote from memory | 25.00% |
| Text supplied in context | 93.61% |
| Authorized lookup tool | 80.09% |
| Deterministic insertion | 91.25% |

Connecting a source did not remove failure; it moved failure onto whatever the
model still decided. A tool was invoked in 95.00% of tool observations but used
for the requested lookup in only 84.17%.

The release separately audits a deterministic-parser implementation correction;
all saved responses were replayed and no model outputs were regenerated.

## Key columns

| Column | Meaning |
|---|---|
| `corrected_end_to_end_exact` | Main endpoint after the disclosed parser correction: exact text **and** declared path followed |
| `locked_end_to_end_exact` | Originally executed literal-parser endpoint retained for audit |
| `corrected_final_output_exact` | User-visible output equality after corrected deterministic replay |
| `locked_final_output_exact` | Originally executed final-output equality retained for audit |
| `end_to_end_exact`, `final_output_exact` | Backward-compatible aliases for the locked fields |
| `parser_correction_applied` | Whether the corrected parser recovered this observation |
| `exact`, `normalized` | Text match, strict and after declared normalization |
| `selection_correct` | Model identified the intended reference |
| `tool_invoked`, `tool_used` | Tool called at all vs. called for the requested span |
| `method_adherence` | Condition-specific evidence the declared path was followed |
| `failure_tags` | Structured failure labels; tags co-occur and must not be summed |
| `*_sha256` | Content digests standing in for withheld text |

## Reproducing the paper's numbers

```python
import pandas as pd
df = pd.read_parquet("trials.parquet")
df.groupby("condition")["corrected_end_to_end_exact"].mean().mul(100).round(2)
```

Terminal provider errors (33 observations) remain in the denominator by
design: the intention-to-observe denominator is what the paper reports.

## Limits

Results apply to the named model routes on 2026-07-26/27, a purposive
twenty-passage panel, two prompt families, three open English editions, and the
declared scoring protocol. The dataset does **not** establish a ranking of
models or vendors, theological correctness, contextual appropriateness,
pastoral safety, deployment readiness, training-data membership, or performance
on restricted translations.

The passage panel is purposive, chosen to expose distinct technical behaviors.
It does not estimate how often quotation fails across the Bible or across real
user traffic.

## Citation

```bibtex
@article{chao2026whennottogenerate,
  title  = {When Not to Generate: How AI Systems Quote Scripture,
            and What Authoritative Quotation Requires},
  author = {Chao, Alex},
  year   = {2026},
  note   = {Fide AI. Study FID-056-P01.}
}
```

## License

CC BY 4.0. No authoritative passage text is redistributed.
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    trials = pd.read_csv(TRIALS)
    leaked = FORBIDDEN.intersection(c.lower() for c in trials.columns)
    if leaked:
        raise SystemExit(f"Refusing to stage: raw-content columns present: {sorted(leaked)}")
    if len(trials) != 8640:
        raise SystemExit(f"Expected 8,640 rows, found {len(trials):,}")
    required_outcomes = {
        "locked_end_to_end_exact",
        "corrected_end_to_end_exact",
        "locked_final_output_exact",
        "corrected_final_output_exact",
        "parser_correction_applied",
    }
    missing_outcomes = required_outcomes - set(trials.columns)
    if missing_outcomes:
        raise SystemExit(
            f"Missing locked/corrected outcome columns: {sorted(missing_outcomes)}"
        )
    corrected = trials.groupby("condition")["corrected_end_to_end_exact"].sum()
    expected = {
        "native_parametric": 540,
        "source_supplied": 2022,
        "tool_mediated": 1730,
        "deterministic_rendering": 1971,
    }
    if corrected.to_dict() != expected:
        raise SystemExit(
            f"Corrected endpoint counts do not match the paper: {corrected.to_dict()}"
        )

    targets = pd.DataFrame(
        json.loads(line) for line in TARGETS.read_text().splitlines() if line.strip()
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
    print("    --repo-type=dataset FideAI/scripture-quotation-fidelity-p01 build/huggingface")


if __name__ == "__main__":
    main()
