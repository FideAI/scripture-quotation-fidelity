#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML==6.0.2"]
# ///
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fide AI
"""Create the release-safe FID-056-P01 replication dataset.

The input is the private combined trial JSONL and the locked target YAML. The
output deliberately excludes generated prose, source text, credentials,
provider response identifiers, request bodies, and raw tool-call traces.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
from typing import Any

import yaml

CONDITION_NAMES = {
    "unassisted": "native_parametric",
    "rag": "source_supplied",
    "tool_call": "tool_mediated",
    "buffer_transform_selection": "deterministic_rendering",
}

METRIC_FIELDS = (
    "exact",
    "normalized",
    "similarity",
    "cer",
    "verse_coverage",
    "answered",
    "quote_span_exact",
    "final_output_exact",
    "extraneous_text",
    "quote_block_count",
    "placeholder_ok",
    "selection_correct",
    "lookup_ok",
    "replacement_ok",
    "tool_invoked",
    "tool_used",
    "method_adherence",
    "end_to_end_exact",
)

OUTPUT_FIELDS = (
    "release_trial_id",
    "target_review_id",
    "reference",
    "passage_stratum",
    "condition",
    "executed_method",
    "prompt_family",
    "translation",
    "model_route",
    "resolved_model",
    "actual_provider",
    "epoch",
    "repetition",
    "sampling_temperature_requested",
    "terminal_error",
    "error_class",
    *METRIC_FIELDS,
    "locked_end_to_end_exact",
    "corrected_end_to_end_exact",
    "locked_final_output_exact",
    "corrected_final_output_exact",
    "parser_correction_applied",
    "failure_tags",
    "selected_reference_parsed",
    "tolerant_recovered_reference",
    "strict_placeholder_count",
    "recoverable_placeholder_count",
    "format_tolerant_reference_selection_success",
    "prompt_sha256",
    "effective_user_input_sha256",
    "source_document_sha256",
    "raw_output_sha256",
    "final_output_sha256",
    "input_tokens",
    "output_tokens",
    "reasoning_tokens",
    "provider_reported_cost_usd",
)


def _stable_release_id(trial_id: str) -> str:
    return hashlib.sha256(trial_id.encode("utf-8")).hexdigest()[:24]


def _read_targets(path: Path) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    public_targets: list[dict[str, Any]] = []
    by_reference: dict[str, dict[str, Any]] = {}
    for target in payload["passage_targets"]:
        item = {
            "review_id": target["review_id"],
            "passage_stratum": target["passage_stratum"],
            "reference": target["expected_reference"]["label"],
            "indirect_description": target["indirect_description"],
        }
        public_targets.append(item)
        by_reference[item["reference"]] = item
    return public_targets, by_reference


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True, sort_keys=True) + "\n")


def _gzip_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with (
        path.open("wb") as raw,
        gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped,
        io.TextIOWrapper(zipped, encoding="utf-8", newline="") as text,
    ):
        writer = csv.DictWriter(text, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _scalar(value: Any) -> Any:
    return "" if value is None else value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", required=True, type=Path)
    parser.add_argument("--targets", required=True, type=Path)
    parser.add_argument("--parser-replay", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    public_targets, targets_by_reference = _read_targets(args.targets)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with args.parser_replay.open(newline="", encoding="utf-8") as handle:
        replay_rows = list(csv.DictReader(handle))
    replay_by_id = {row["release_trial_id"]: row for row in replay_rows}
    if len(replay_rows) != 2_160 or len(replay_by_id) != len(replay_rows):
        raise ValueError("Parser replay must contain 2,160 unique rows")

    rows: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    with args.trials.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            trial = json.loads(line)
            method = trial["method"]
            if method not in CONDITION_NAMES:
                raise ValueError(f"Unexpected method on line {line_number}: {method}")
            target = targets_by_reference.get(trial["reference"])
            if target is None:
                raise ValueError(
                    f"Unknown target reference on line {line_number}: "
                    f"{trial['reference']}"
                )
            release_id = _stable_release_id(trial["trial_id"])
            if release_id in seen_ids:
                raise ValueError(f"Duplicate release ID: {release_id}")
            seen_ids.add(release_id)

            metrics = trial.get("metrics") or {}
            usage = trial.get("usage") or {}
            error = trial.get("error") or {}
            row = {
                "release_trial_id": release_id,
                "target_review_id": target["review_id"],
                "reference": trial["reference"],
                "passage_stratum": target["passage_stratum"],
                "condition": CONDITION_NAMES[method],
                "executed_method": method,
                "prompt_family": trial["prompt_family"],
                "translation": trial["translation"],
                "model_route": trial["requested_model"].removeprefix("openrouter/"),
                "resolved_model": trial["resolved_model"],
                "actual_provider": ";".join(trial.get("actual_providers") or []),
                "epoch": trial["epoch"],
                "repetition": trial["repetition"],
                "sampling_temperature_requested": _scalar(trial.get("temperature")),
                "terminal_error": int(bool(trial.get("error"))),
                "error_class": error.get("error_class", ""),
                "failure_tags": ";".join(sorted(trial.get("failure_tags") or [])),
                "selected_reference_parsed": _scalar(
                    trial.get("selected_reference_parsed")
                ),
                "tolerant_recovered_reference": _scalar(
                    trial.get("recovered_reference")
                ),
                "strict_placeholder_count": _scalar(
                    trial.get("strict_placeholder_count")
                ),
                "recoverable_placeholder_count": _scalar(
                    trial.get("recoverable_placeholder_count")
                ),
                "format_tolerant_reference_selection_success": int(
                    bool(trial.get("format_tolerant_reference_selection_success"))
                ),
                "prompt_sha256": _scalar(trial.get("prompt_sha256")),
                "effective_user_input_sha256": _scalar(
                    trial.get("effective_user_input_sha256")
                ),
                "source_document_sha256": _scalar(
                    trial.get("source_document_sha256")
                ),
                "raw_output_sha256": _scalar(trial.get("raw_output_sha256")),
                "final_output_sha256": _scalar(trial.get("final_output_sha256")),
                "input_tokens": _scalar(usage.get("input_tokens")),
                "output_tokens": _scalar(usage.get("output_tokens")),
                "reasoning_tokens": _scalar(usage.get("reasoning_tokens")),
                "provider_reported_cost_usd": _scalar(
                    trial.get("provider_reported_cost")
                ),
            }
            for metric in METRIC_FIELDS:
                # The locked intention-to-observe denominator treats terminal
                # errors as failures. Materialize zero rather than a blank so
                # downstream software cannot silently drop those observations.
                row[metric] = 0.0 if metrics.get(metric) is None else metrics[metric]
            row["locked_end_to_end_exact"] = row["end_to_end_exact"]
            row["locked_final_output_exact"] = row["final_output_exact"]
            replay = replay_by_id.get(release_id)
            if method == "buffer_transform_selection":
                if replay is None:
                    raise ValueError(f"Missing parser replay row: {release_id}")
                row["corrected_end_to_end_exact"] = int(
                    replay["permissive_parser_replay_exact"]
                )
                row["corrected_final_output_exact"] = int(
                    replay["permissive_parser_replay_final_output_exact"]
                )
                row["parser_correction_applied"] = int(
                    row["corrected_end_to_end_exact"]
                    != row["locked_end_to_end_exact"]
                )
            else:
                row["corrected_end_to_end_exact"] = row["end_to_end_exact"]
                row["corrected_final_output_exact"] = row["final_output_exact"]
                row["parser_correction_applied"] = 0
            rows.append(row)

    if len(rows) != 8640:
        raise ValueError(f"Expected 8,640 trials, found {len(rows):,}")
    deterministic_ids = {
        row["release_trial_id"]
        for row in rows
        if row["condition"] == "deterministic_rendering"
    }
    if deterministic_ids != set(replay_by_id):
        raise ValueError("Parser replay IDs do not match deterministic trial IDs")

    rows.sort(
        key=lambda row: (
            row["target_review_id"],
            row["prompt_family"],
            row["condition"],
            row["translation"],
            row["model_route"],
            int(row["epoch"]),
        )
    )
    _write_jsonl(args.output_dir / "fid056_p01_targets.jsonl", public_targets)
    _gzip_csv(args.output_dir / "fid056_p01_deidentified_trials.csv.gz", rows)


if __name__ == "__main__":
    main()
