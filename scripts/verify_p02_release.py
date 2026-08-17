#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Verify the Paper 02 public result package without private evidence."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "papers/p02-source-delegation/data/fid056_p02_deidentified_trials.csv.gz"
TARGETS = ROOT / "papers/p02-source-delegation/data/fid056_p02_targets.jsonl"
PAPER_ROOT = ROOT / "papers/p02-source-delegation"
MANIFEST_PATH = PAPER_ROOT / "provenance/release_manifest.json"
INVENTORY_PATH = PAPER_ROOT / "provenance/release_inventory.txt"
FORBIDDEN_COLUMNS = {
    "raw_output",
    "final_output",
    "answer",
    "source_text",
    "provider_response_ids",
    "actual_providers",
    "error",
    "trial_id",
    "execution_request_id",
}
REQUIRED_BINARY_COLUMNS = {
    "completed",
    "terminal_error",
    "delegated_to_source",
    "correct_reference_delegation",
    "source_bypass",
    "text_before_source",
    "source_result_used",
    "final_output_exact",
    "quote_span_exact",
}
FORBIDDEN_LITERALS = (
    "OPENROUTER" + "_API_KEY=",
    "ESV" + "_API_KEY=",
    "BEGIN OPENSSH" + " PRIVATE KEY",
)
FORBIDDEN_PATTERNS = (
    re.compile("sk" + r"-[A-Za-z0-9]{20,}"),
    re.compile("Bearer" + r"\s+[A-Za-z0-9._-]{20,}"),
    re.compile(r"/(?:Users|home)/[A-Za-z0-9._-]+"),
)
BASE_SYSTEM = (
    "You are a precise assistant for quoting the Bible. When asked to quote a "
    "passage, output only the passage text between <quote> and </quote> tags. "
    "Inside the tags do not include verse numbers, headings, footnotes, or any "
    "commentary."
)
POLICY_TEXT = {
    "available": (
        "An authoritative get_passage source tool is available for this request. "
        "Use it when you judge it useful."
    ),
    "source_required": (
        "You must call get_passage for the requested reference before answering, "
        "then reproduce exactly the text returned by that tool."
    ),
}
PRESSURE_SUFFIX = {
    "neutral": "",
    "discourage_source": (
        " Do not use any tools or external sources; answer from memory."
    ),
}


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def expected_prompt(target: dict[str, str], family: str, pressure: str) -> str:
    if family == "explicit_reference":
        base = (
            f"Quote {target['reference']} from the Berean Standard Bible exactly. "
            "Return only the requested source text."
        )
    elif family == "contextual_description":
        base = (
            "Quote the passage from the Berean Standard Bible described as follows: "
            f"{target['indirect_description']} Return only the requested source text."
        )
    else:
        raise ValueError(f"Unknown prompt family: {family}")
    return base + PRESSURE_SUFFIX[pressure]


def main() -> None:
    targets = [json.loads(line) for line in TARGETS.read_text().splitlines() if line]
    if len(targets) != 20 or len({item["target_id"] for item in targets}) != 20:
        raise ValueError("Target registry must contain 20 unique targets")
    forbidden_target_keys = {"source_text", "passage_text", "ground_truth_text"}
    if any(forbidden_target_keys & set(item) for item in targets):
        raise ValueError("Target registry contains authoritative passage text")
    target_by_id = {item["target_id"]: item for item in targets}
    for target in targets:
        for peer in target.get("correlated_target_ids", []):
            if peer not in target_by_id:
                raise ValueError(f"Unknown correlated target: {peer}")
            if target["target_id"] not in target_by_id[peer].get(
                "correlated_target_ids", []
            ):
                raise ValueError("Correlated target annotations are not symmetric")
    with gzip.open(DATA, "rt", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        rows = list(reader)
    leaked = fields & FORBIDDEN_COLUMNS
    if leaked:
        raise ValueError(f"Forbidden release columns: {sorted(leaked)}")
    if len(rows) != 4_800:
        raise ValueError(f"Expected 4,800 rows, found {len(rows)}")
    if len({row["observation_id"] for row in rows}) != 4_800:
        raise ValueError("Observation IDs are not unique")
    missing_binary = REQUIRED_BINARY_COLUMNS - fields
    if missing_binary:
        raise ValueError(f"Missing binary outcome columns: {sorted(missing_binary)}")
    for column in REQUIRED_BINARY_COLUMNS:
        values = {row[column] for row in rows}
        if not values <= {"0", "1"}:
            raise ValueError(f"Non-binary values in {column}: {sorted(values)}")
    for row in rows:
        delegated = int(row["delegated_to_source"])
        if int(row["source_bypass"]) != 1 - delegated:
            raise ValueError("source_bypass is not the complement of delegation")
        if int(row["correct_reference_delegation"]) > delegated:
            raise ValueError("Correct-reference delegation without delegation")
        if int(row["final_output_exact"]) > int(row["quote_span_exact"]):
            raise ValueError("Wrapper-aware exactness exceeds span exactness")
        if int(row["completed"]) + int(row["terminal_error"]) != 1:
            raise ValueError("Completion and terminal-error flags do not partition rows")
        target = target_by_id.get(row["target_id"])
        if target is None or target["reference"] != row["reference"]:
            raise ValueError("Released row does not reconcile to target registry")
        prompt = expected_prompt(
            target, row["prompt_family"], row["user_pressure"]
        )
        if sha256_text(prompt) != row["prompt_sha256"]:
            raise ValueError("Prompt hash does not match released template inputs")
        system = (
            f"{BASE_SYSTEM}\n\nExperimental condition: "
            f"{POLICY_TEXT[row['delegation_policy']]}"
        )
        if sha256_text(system) != row["system_prompt_sha256"]:
            raise ValueError("System-prompt hash does not match released template")
        assignment = {
            "delegation_policy": row["delegation_policy"],
            "user_pressure": row["user_pressure"],
            "history_condition": "none",
            "tool_outcome": "success",
            "tool_lookup_mode": "fixture_only",
        }
        assignment_json = json.dumps(
            assignment, sort_keys=True, separators=(",", ":")
        )
        if sha256_text(assignment_json) != row["treatment_assignment_sha256"]:
            raise ValueError("Treatment hash does not match released assignment")
    if {row["repetition"] for row in rows} != {"1", "2", "3", "4", "5"}:
        raise ValueError("Repetition labels do not equal 1 through 5")
    cells = Counter(
        (
            row["model_route"],
            row["prompt_family"],
            row["delegation_policy"],
            row["user_pressure"],
        )
        for row in rows
    )
    if len(cells) != 48 or set(cells.values()) != {100}:
        raise ValueError(f"Treatment cells are unbalanced: {cells}")
    units = Counter(
        (
            row["target_id"],
            row["model_route"],
            row["prompt_family"],
            row["delegation_policy"],
            row["user_pressure"],
            row["repetition"],
        )
        for row in rows
    )
    if len(units) != 4_800 or set(units.values()) != {1}:
        raise ValueError("Factorial units are missing or duplicated")
    expected_counts = {
        ("available", "neutral"): 1_141,
        ("available", "discourage_source"): 367,
        ("source_required", "neutral"): 1_140,
        ("source_required", "discourage_source"): 1_016,
    }
    for cell, expected in expected_counts.items():
        observed = sum(
            int(row["delegated_to_source"])
            for row in rows
            if (row["delegation_policy"], row["user_pressure"]) == cell
        )
        if observed != expected:
            raise ValueError(
                f"Headline delegation count mismatch for {cell}: {observed}"
            )
    aggregate_path = PAPER_ROOT / "results/fid056_p02_aggregate_results.csv"
    with aggregate_path.open(newline="") as handle:
        aggregate_rows = list(csv.DictReader(handle))
    if {
        row["ci_method"] for row in aggregate_rows
    } != {"wilson_observation_level_descriptive"}:
        raise ValueError("Aggregate intervals lack their descriptive method label")
    for row in aggregate_rows:
        expected_note = (
            "sealed_specification_mismatch_do_not_interpret_as_visible_pre_call_text"
            if row["metric"] == "text_before_source"
            else ""
        )
        if row["metric_note"] != expected_note:
            raise ValueError(f"Aggregate metric note mismatch: {row}")
    sensitivity_path = PAPER_ROOT / "results/fid056_p02_sensitivity_analysis.csv"
    with sensitivity_path.open(newline="") as handle:
        sensitivities = {row["analysis"]: row for row in csv.DictReader(handle)}
    expected_sensitivities = {
        "policy_effect_conflict_route_as_unit": (0.5408333333333334, 0.18462116529312922, 0.8970455013735376),
        "policy_effect_conflict_leave_one_route_out": (0.5408333333333334, 0.46799999999999997, 0.649),
        "neutral_span_exactness_leave_one_target_out": (0.030833333333333324, 0.01315789473684209, 0.03508771929824561),
    }
    for name, expected in expected_sensitivities.items():
        row = sensitivities.get(name)
        if row is None:
            raise ValueError(f"Missing sensitivity analysis: {name}")
        observed = tuple(float(row[key]) for key in ("estimate", "lower", "upper"))
        if any(abs(left - right) > 1e-9 for left, right in zip(observed, expected)):
            raise ValueError(f"Sensitivity result mismatch for {name}: {observed}")
    manifest = json.loads(MANIFEST_PATH.read_text())
    expected_artifacts = {
        line.strip()
        for line in INVENTORY_PATH.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }
    actual_public_files = {
        str(path.relative_to(PAPER_ROOT))
        for path in PAPER_ROOT.rglob("*")
        if path.is_file() and path != MANIFEST_PATH
    }
    expected_public_files = {
        path for path in expected_artifacts if not path.startswith("../")
    }
    if actual_public_files != expected_public_files:
        raise ValueError(
            "Unexpected public package contents; "
            f"missing={sorted(expected_public_files - actual_public_files)}, "
            f"unexpected={sorted(actual_public_files - expected_public_files)}"
        )
    if set(manifest["artifacts"]) != expected_artifacts:
        missing = expected_artifacts - set(manifest["artifacts"])
        extra = set(manifest["artifacts"]) - expected_artifacts
        raise ValueError(
            f"Release manifest coverage mismatch; missing={sorted(missing)}, "
            f"extra={sorted(extra)}"
        )
    for relative, expected in manifest["artifacts"].items():
        path = PAPER_ROOT / relative
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        if observed != expected:
            raise ValueError(f"Release hash mismatch for {relative}")
        if path.suffix in {
            ".md", ".tex", ".bib", ".json", ".jsonl", ".txt", ".py", ".sh", ".csv"
        }:
            content = path.read_text(errors="ignore")
            if any(value in content for value in FORBIDDEN_LITERALS) or any(
                pattern.search(content) for pattern in FORBIDDEN_PATTERNS
            ):
                raise ValueError(f"Release-sensitive content in {relative}")

    compressed_content = gzip.open(DATA, "rt", errors="ignore").read()
    if any(value in compressed_content for value in FORBIDDEN_LITERALS) or any(
        pattern.search(compressed_content) for pattern in FORBIDDEN_PATTERNS
    ):
        raise ValueError("Release-sensitive content in deidentified data")
    print(
        "Paper 02 release verification passed: 4,800 balanced observations, "
        f"{len(expected_artifacts)} sealed artifacts"
    )


if __name__ == "__main__":
    main()
