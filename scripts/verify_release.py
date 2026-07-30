#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fide AI
"""Verify the released FID-056-P01 derived dataset and headline results."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRIALS = ROOT / "papers/p01-scripture-quotation/data/fid056_p01_deidentified_trials.csv.gz"
TARGETS = ROOT / "papers/p01-scripture-quotation/data/fid056_p01_targets.jsonl"
MANIFEST = ROOT / "papers/p01-scripture-quotation/provenance/release_manifest.json"
FORBIDDEN_COLUMNS = {
    "content",
    "generated_text",
    "raw_output",
    "source_text",
    "response_id",
    "tool_calls",
    "tool_trace",
}
EXPECTED_SUCCESSES = {
    "native_parametric": (540, 540),
    "source_supplied": (2022, 2022),
    "tool_mediated": (1730, 1778),
    "deterministic_rendering": (1813, 1813),
}


def main() -> None:
    targets = [json.loads(line) for line in TARGETS.read_text().splitlines()]
    if len(targets) != 20 or len({row["review_id"] for row in targets}) != 20:
        raise SystemExit("Target release must contain 20 unique review IDs")

    with gzip.open(TRIALS, "rt", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or ())
        overlap = columns & FORBIDDEN_COLUMNS
        if overlap:
            raise SystemExit(f"Forbidden release columns: {sorted(overlap)}")
        rows = list(reader)

    if len(rows) != 8640:
        raise SystemExit(f"Expected 8,640 trial rows, found {len(rows):,}")
    if len({row["release_trial_id"] for row in rows}) != len(rows):
        raise SystemExit("release_trial_id values are not unique")

    expected_levels = {
        "target_review_id": 20,
        "prompt_family": 2,
        "condition": 4,
        "translation": 3,
        "model_route": 6,
        "epoch": 3,
    }
    for field, expected in expected_levels.items():
        observed = len({row[field] for row in rows})
        if observed != expected:
            raise SystemExit(
                f"{field} has {observed} levels; expected {expected}"
            )

    counts: dict[str, Counter[str]] = {}
    for condition in EXPECTED_SUCCESSES:
        members = [row for row in rows if row["condition"] == condition]
        if len(members) != 2160:
            raise SystemExit(f"{condition} has {len(members)} rows")
        counts[condition] = Counter(
            {
                "end_to_end_exact": sum(
                    float(row["end_to_end_exact"]) == 1.0 for row in members
                ),
                "final_output_exact": sum(
                    float(row["final_output_exact"]) == 1.0 for row in members
                ),
            }
        )
        observed = (
            counts[condition]["end_to_end_exact"],
            counts[condition]["final_output_exact"],
        )
        if observed != EXPECTED_SUCCESSES[condition]:
            raise SystemExit(
                f"{condition} success counts {observed}; "
                f"expected {EXPECTED_SUCCESSES[condition]}"
            )

    terminal_errors = sum(
        row["terminal_error"].strip().lower() in {"1", "true", "yes"}
        for row in rows
    )
    if terminal_errors != 33:
        raise SystemExit(f"Expected 33 terminal errors, found {terminal_errors}")

    if not MANIFEST.exists():
        raise SystemExit("Missing provenance/release_manifest.json; run make manifest")
    manifest = json.loads(MANIFEST.read_text())
    for record in manifest["files"]:
        path = ROOT / record["path"]
        if not path.is_file():
            raise SystemExit(f"Manifest file is missing: {record['path']}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != record["sha256"]:
            raise SystemExit(
                f"Manifest digest mismatch for {record['path']}; run make manifest"
            )

    print("Release verification passed: 8,640 rows and headline counts reconcile.")


if __name__ == "__main__":
    main()
