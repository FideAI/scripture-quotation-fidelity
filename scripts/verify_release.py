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
RELEASE_DECISION = ROOT / (
    "papers/p01-scripture-quotation/provenance/release_decision_summary.json"
)
REPLAY_CSV = ROOT / (
    "papers/p01-scripture-quotation/results/"
    "fid056_p01_permissive_parser_replay.csv"
)
REPLAY_JSON = ROOT / (
    "papers/p01-scripture-quotation/results/"
    "fid056_p01_permissive_parser_replay.json"
)
AGGREGATES = ROOT / (
    "papers/p01-scripture-quotation/results/fid056_p01_aggregate_results.csv"
)
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
    "native_parametric": (540, 540, 540, 540),
    "source_supplied": (2022, 2022, 2022, 2022),
    "tool_mediated": (1730, 1730, 1778, 1778),
    "deterministic_rendering": (1813, 1971, 1813, 1971),
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
        required_outcomes = {
            "locked_end_to_end_exact",
            "corrected_end_to_end_exact",
            "locked_final_output_exact",
            "corrected_final_output_exact",
            "parser_correction_applied",
        }
        missing_outcomes = required_outcomes - columns
        if missing_outcomes:
            raise SystemExit(
                f"Missing locked/corrected outcomes: {sorted(missing_outcomes)}"
            )
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
    for condition, expected_successes in EXPECTED_SUCCESSES.items():
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
                "corrected_end_to_end_exact": sum(
                    float(row["corrected_end_to_end_exact"]) == 1.0
                    for row in members
                ),
                "corrected_final_output_exact": sum(
                    float(row["corrected_final_output_exact"]) == 1.0
                    for row in members
                ),
            }
        )
        if any(
            row["end_to_end_exact"] != row["locked_end_to_end_exact"]
            or row["final_output_exact"] != row["locked_final_output_exact"]
            for row in members
        ):
            raise SystemExit(f"{condition} legacy outcome aliases drifted")
        observed = (
            counts[condition]["end_to_end_exact"],
            counts[condition]["corrected_end_to_end_exact"],
            counts[condition]["final_output_exact"],
            counts[condition]["corrected_final_output_exact"],
        )
        if observed != expected_successes:
            raise SystemExit(
                f"{condition} success counts {observed}; "
                f"expected {expected_successes}"
            )

    terminal_errors = sum(
        row["terminal_error"].strip().lower() in {"1", "true", "yes"}
        for row in rows
    )
    if terminal_errors != 33:
        raise SystemExit(f"Expected 33 terminal errors, found {terminal_errors}")

    deterministic_ids = {
        row["release_trial_id"]
        for row in rows
        if row["condition"] == "deterministic_rendering"
    }
    with REPLAY_CSV.open(newline="", encoding="utf-8") as handle:
        replay_reader = csv.DictReader(handle)
        replay_columns = set(replay_reader.fieldnames or ())
        replay_overlap = replay_columns & FORBIDDEN_COLUMNS
        if replay_overlap:
            raise SystemExit(
                f"Forbidden parser-replay columns: {sorted(replay_overlap)}"
            )
        replay_rows = list(replay_reader)

    if len(replay_rows) != 2160:
        raise SystemExit(
            f"Expected 2,160 parser-replay rows, found {len(replay_rows):,}"
        )
    replay_ids = {row["release_trial_id"] for row in replay_rows}
    if len(replay_ids) != len(replay_rows) or replay_ids != deterministic_ids:
        raise SystemExit("Parser-replay IDs do not match deterministic trial IDs")

    def replay_count(field: str, members: list[dict[str, str]]) -> int:
        return sum(int(row[field]) for row in members)

    strict = replay_count("strict_architecture_adherent_exact", replay_rows)
    adjusted = replay_count("permissive_parser_replay_exact", replay_rows)
    adjusted_final = replay_count(
        "permissive_parser_replay_final_output_exact", replay_rows
    )
    recovered = replay_count("recovered_by_permissive_parser", replay_rows)
    if (strict, adjusted, adjusted_final, recovered) != (1813, 1971, 1971, 158):
        raise SystemExit(
            "Parser-replay counts do not reconcile: "
            f"{(strict, adjusted, adjusted_final, recovered)}"
        )
    prompt_expected = {
        "explicit_reference": 1079,
        "contextual_description": 892,
    }
    for prompt_family, expected in prompt_expected.items():
        members = [
            row for row in replay_rows if row["prompt_family"] == prompt_family
        ]
        if len(members) != 1080:
            raise SystemExit(f"Parser replay has {len(members)} {prompt_family} rows")
        observed = replay_count("permissive_parser_replay_exact", members)
        if observed != expected:
            raise SystemExit(
                f"Parser replay has {observed} exact {prompt_family} rows; "
                f"expected {expected}"
            )

    replay_report = json.loads(REPLAY_JSON.read_text())
    overall = replay_report.get("summary", {}).get("overall", {})
    if replay_report.get("model_outputs_rerun") is not False:
        raise SystemExit("Parser replay must disclose that model outputs were not rerun")
    if replay_report.get("analysis_status") != "post_hoc_parser_sensitivity":
        raise SystemExit("Parser replay must remain labeled post hoc")
    if (
        overall.get("strict_exact"),
        overall.get("permissive_parser_replay_exact"),
        overall.get("permissive_parser_replay_final_output_exact"),
        overall.get("recovered_by_permissive_parser"),
    ) != (1813, 1971, 1971, 158):
        raise SystemExit("Parser-replay JSON does not reconcile with expected counts")

    with AGGREGATES.open(newline="", encoding="utf-8") as handle:
        aggregate_rows = list(csv.DictReader(handle))
    aggregate_lookup = {
        (row["analysis"], row["level"], row["condition"]): int(row["exact"])
        for row in aggregate_rows
    }
    for condition, expected in EXPECTED_SUCCESSES.items():
        locked_expected, corrected_expected, _, _ = expected
        if aggregate_lookup.get(("locked_primary", "overall", condition)) != locked_expected:
            raise SystemExit(f"Locked aggregate result drifted for {condition}")
        if aggregate_lookup.get(("parser_adjusted", "overall", condition)) != corrected_expected:
            raise SystemExit(f"Corrected aggregate result drifted for {condition}")

    if not MANIFEST.exists():
        raise SystemExit("Missing provenance/release_manifest.json; run make manifest")
    manifest = json.loads(MANIFEST.read_text())
    if manifest.get("schema_version") != 2:
        raise SystemExit("Release manifest must use schema version 2")
    if manifest.get("research_program_id") != "FID-056":
        raise SystemExit("Release manifest has the wrong research program")
    if manifest.get("paper_id") != "FID-056-P01":
        raise SystemExit("Release manifest has the wrong paper ID")

    release_decision = json.loads(RELEASE_DECISION.read_text())
    required_decision_fields = {
        "schema_version",
        "decision_id",
        "decision_date",
        "decision_authority",
        "human_review",
        "research_program_id",
        "paper_id",
        "status",
        "approved_artifacts",
        "blocked_artifacts",
        "claims_limit",
        "review_basis",
    }
    missing_decision_fields = required_decision_fields - set(release_decision)
    if missing_decision_fields:
        raise SystemExit(
            f"Release decision is missing fields: {sorted(missing_decision_fields)}"
        )
    if release_decision.get("schema_version") != "fid056_public_release_decision_summary_v1":
        raise SystemExit("Release decision has the wrong schema version")
    if release_decision.get("research_program_id") != "FID-056":
        raise SystemExit("Release decision has the wrong research program")
    if release_decision.get("paper_id") != "FID-056-P01":
        raise SystemExit("Release decision has the wrong paper ID")
    decision_reference = release_decision.get("decision_id")
    if release_decision.get("human_review") != "completed":
        raise SystemExit("Human release review is not complete")
    if release_decision.get("status") != "approved_public_reproduction_packet":
        raise SystemExit("Public reproduction packet is not approved")
    required_approved_artifacts = {
        "manuscript",
        "deidentified_derived_score_dataset",
        "reviewed_result_tables",
        "public_reproduction_packet",
    }
    if set(release_decision.get("approved_artifacts", ())) != required_approved_artifacts:
        raise SystemExit("Release decision does not approve the complete public packet")
    required_blocked_artifacts = {
        "raw_model_outputs",
        "held_out_prompts",
        "restricted_source_text",
        "provider_response_identifiers",
        "raw_tool_traces",
        "credentials",
        "private_execution_engine_source",
        "partner_private_traces",
    }
    if set(release_decision.get("blocked_artifacts", ())) != required_blocked_artifacts:
        raise SystemExit("Release decision does not preserve the complete private boundary")
    if len(release_decision.get("claims_limit", "").strip()) < 40:
        raise SystemExit("Release decision claims limit is missing or too short")
    for relative in release_decision.get("review_basis", ()):
        if not (ROOT / relative).is_file():
            raise SystemExit(f"Release decision review basis is missing: {relative}")
    manifest_decision = manifest.get("release_decision", {})
    if manifest_decision.get("decision_id") != decision_reference:
        raise SystemExit("Release manifest decision reference does not reconcile")
    if manifest_decision.get("summary_path") != RELEASE_DECISION.relative_to(ROOT).as_posix():
        raise SystemExit("Release manifest has the wrong decision-summary path")

    manifest_paths = {record["path"] for record in manifest["files"]}
    canonical = {
        "papers/p01-scripture-quotation/paper/main.tex",
        "papers/p01-scripture-quotation/paper/main.pdf",
    }
    if not canonical <= manifest_paths:
        raise SystemExit("Release manifest is missing the canonical paper")
    if any("main_visual" in path for path in manifest_paths):
        raise SystemExit("Release manifest contains a non-canonical visual variant")
    required_record_fields = {
        "path",
        "bytes",
        "sha256",
        "rights_classification",
        "evidence_source",
        "verification_mode",
        "release_decision_reference",
    }
    for record in manifest["files"]:
        if set(record) != required_record_fields:
            raise SystemExit(
                f"Manifest metadata is incomplete for {record.get('path', '<unknown>')}"
            )
        if record["release_decision_reference"] != decision_reference:
            raise SystemExit(
                f"Manifest decision reference drifted for {record['path']}"
            )
        for field in ("rights_classification", "evidence_source", "verification_mode"):
            if not record[field].strip():
                raise SystemExit(f"Manifest {field} is empty for {record['path']}")
        path = ROOT / record["path"]
        if not path.is_file():
            raise SystemExit(f"Manifest file is missing: {record['path']}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != record["sha256"]:
            raise SystemExit(
                f"Manifest digest mismatch for {record['path']}; run make manifest"
            )

    print(
        "Release verification passed: 8,640 rows and the 2,160-row parser "
        "replay reconcile."
    )


if __name__ == "__main__":
    main()
