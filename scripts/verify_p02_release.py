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
DECISION_PATH = PAPER_ROOT / "provenance/release_decision_summary.json"
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
EXPECTED_COLUMNS = (
    "observation_id",
    "target_id",
    "reference",
    "passage_stratum",
    "prompt_family",
    "delegation_policy",
    "user_pressure",
    "model_route",
    "repetition",
    "completed",
    "terminal_error",
    "delegated_to_source",
    "correct_reference_delegation",
    "source_bypass",
    "text_before_source",
    "source_result_used",
    "final_output_exact",
    "quote_span_exact",
    "tool_call_count",
    "prompt_sha256",
    "system_prompt_sha256",
    "treatment_assignment_sha256",
    "tool_contract_sha256",
)
EXPECTED_TOOL_IMPLEMENTATION_SHA256 = (
    "78702c91e308a2399b070df0d01f617559dbfba5fae39364c9c72e0bbabbe5ed"
)
EXPECTED_MANIFEST_EXCLUSIONS = {
    "raw model outputs",
    "provider response identifiers",
    "credentials",
    "source passage text",
    "private execution code",
    "local filesystem paths",
    "calibration traces",
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
    correlation_graph = {target_id: set() for target_id in target_by_id}
    for target in targets:
        for peer in target.get("correlated_target_ids", []):
            if peer not in target_by_id:
                raise ValueError(f"Unknown correlated target: {peer}")
            if target["target_id"] not in target_by_id[peer].get(
                "correlated_target_ids", []
            ):
                raise ValueError("Correlated target annotations are not symmetric")
            correlation_graph[target["target_id"]].add(peer)
            correlation_graph[peer].add(target["target_id"])
    unseen = set(correlation_graph)
    correlation_components = []
    while unseen:
        pending = [min(unseen)]
        component = set()
        while pending:
            target_id = pending.pop()
            if target_id in component:
                continue
            component.add(target_id)
            pending.extend(correlation_graph[target_id] - component)
        unseen -= component
        correlation_components.append(component)
    if len(correlation_components) != 17:
        raise ValueError(
            "Expected the declared target relationships to form 17 components"
        )
    with gzip.open(DATA, "rt", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = tuple(reader.fieldnames or ())
        fields = set(fieldnames)
        rows = list(reader)
    if fieldnames != EXPECTED_COLUMNS:
        raise ValueError(
            f"Released data columns differ from the approved schema: {fieldnames}"
        )
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
        try:
            tool_call_count = int(row["tool_call_count"])
        except ValueError as exc:
            raise ValueError("tool_call_count must be an integer") from exc
        if tool_call_count < 0 or delegated != int(tool_call_count > 0):
            raise ValueError("tool_call_count does not reconcile with delegation")
        if int(row["source_bypass"]) != 1 - delegated:
            raise ValueError("source_bypass is not the complement of delegation")
        if int(row["correct_reference_delegation"]) > delegated:
            raise ValueError("Correct-reference delegation without delegation")
        if int(row["final_output_exact"]) > int(row["quote_span_exact"]):
            raise ValueError("Wrapper-aware exactness exceeds span exactness")
        if int(row["completed"]) + int(row["terminal_error"]) != 1:
            raise ValueError(
                "Completion and terminal-error flags do not partition rows"
            )
        target = target_by_id.get(row["target_id"])
        if target is None or target["reference"] != row["reference"]:
            raise ValueError("Released row does not reconcile to target registry")
        prompt = expected_prompt(target, row["prompt_family"], row["user_pressure"])
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
        assignment_json = json.dumps(assignment, sort_keys=True, separators=(",", ":"))
        if sha256_text(assignment_json) != row["treatment_assignment_sha256"]:
            raise ValueError("Treatment hash does not match released assignment")
        if row["tool_contract_sha256"] != EXPECTED_TOOL_IMPLEMENTATION_SHA256:
            raise ValueError("Tool-implementation source digest does not match lock")
    if {row["repetition"] for row in rows} != {"1", "2", "3", "4", "5"}:
        raise ValueError("Repetition labels do not equal 1 through 5")
    expected_routes = {
        "anthropic-claude-sonnet-5",
        "deepseek-v4-pro-together",
        "google-gemini-3-5-flash",
        "moonshot-kimi-k3",
        "openai-gpt-5-6-sol",
        "zai-glm-5-2-together",
    }
    if {row["model_route"] for row in rows} != expected_routes:
        raise ValueError("Released model routes do not match the executed panel")
    if sum(int(row["terminal_error"]) for row in rows) != 0:
        raise ValueError("Execution seal records zero terminal errors")
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
    if {row["ci_method"] for row in aggregate_rows} != {
        "wilson_observation_level_descriptive"
    }:
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
        "policy_effect_conflict_route_as_unit": (
            0.5408333333333334,
            0.18462116529312922,
            0.8970455013735376,
        ),
        "policy_effect_conflict_leave_one_route_out": (
            0.5408333333333334,
            0.46799999999999997,
            0.649,
        ),
        "primary_policy_effect_neutral_correlation_components": (
            -0.000833333333333334,
            -0.013725490196078431,
            0.012280701754385965,
        ),
        "policy_effect_discourage_source_correlation_components": (
            0.5408333333333334,
            0.5142857142857143,
            0.5692982456140351,
        ),
        "quote_span_exactness_policy_effect_neutral_correlation_components": (
            0.030833333333333324,
            0.001960784313725491,
            0.07450980392156864,
        ),
        "policy_by_pressure_interaction_correlation_components": (
            0.5416666666666667,
            0.512280701754386,
            0.5705882352941176,
        ),
        "neutral_span_exactness_leave_one_target_out": (
            0.030833333333333324,
            0.01315789473684209,
            0.03508771929824561,
        ),
    }
    for name, expected in expected_sensitivities.items():
        row = sensitivities.get(name)
        if row is None:
            raise ValueError(f"Missing sensitivity analysis: {name}")
        observed = tuple(float(row[key]) for key in ("estimate", "lower", "upper"))
        if any(abs(left - right) > 1e-9 for left, right in zip(observed, expected)):
            raise ValueError(f"Sensitivity result mismatch for {name}: {observed}")
    correlation_rows = [
        row
        for row in sensitivities.values()
        if row["method"] == "correlation_component_bootstrap_10000_seed5602"
    ]
    if len(correlation_rows) != 8:
        raise ValueError(
            "Expected correlation-component sensitivities for all eight effects"
        )
    manifest = json.loads(MANIFEST_PATH.read_text())
    expected_manifest_fields = {
        "schema_version",
        "study_id",
        "status",
        "artifacts",
        "excluded",
    }
    if set(manifest) != expected_manifest_fields:
        raise ValueError("Paper 02 release manifest fields do not match its schema")
    if manifest["schema_version"] != "fid056_p02_release_manifest_v1":
        raise ValueError("Paper 02 release manifest has the wrong schema version")
    if manifest["study_id"] != "FID-056-P02":
        raise ValueError("Paper 02 release manifest has the wrong study ID")
    if manifest["status"] != "approved_public_reproduction_packet":
        raise ValueError("Paper 02 release manifest has the wrong release status")
    decision = json.loads(DECISION_PATH.read_text())
    expected_decision_fields = {
        "schema_version",
        "status",
        "decision_id",
        "decision_authority",
        "decision_date",
        "human_review",
        "research_program_id",
        "paper_id",
        "approved_artifacts",
        "blocked_artifacts",
        "claims_limit",
        "review_basis",
    }
    if set(decision) != expected_decision_fields:
        raise ValueError("Paper 02 release decision fields do not match its schema")
    expected_decision_values = {
        "schema_version": "fid056_public_release_decision_summary_v1",
        "status": "approved_public_reproduction_packet",
        "decision_id": "FID-056-P02-PUBLIC-RELEASE-2026-08-26",
        "decision_authority": "Fide AI",
        "decision_date": "2026-08-26",
        "human_review": "completed",
        "research_program_id": "FID-056",
        "paper_id": "FID-056-P02",
    }
    for field, expected in expected_decision_values.items():
        if decision[field] != expected:
            raise ValueError(f"Paper 02 release decision has wrong {field}")
    for relative in decision["review_basis"]:
        if not (ROOT / relative).is_file():
            raise ValueError(f"Paper 02 review basis is missing: {relative}")
    if (
        len(manifest["excluded"]) != len(EXPECTED_MANIFEST_EXCLUSIONS)
        or set(manifest["excluded"]) != EXPECTED_MANIFEST_EXCLUSIONS
    ):
        raise ValueError(
            "Paper 02 release exclusions do not preserve the private boundary"
        )
    expected_artifacts = {
        line.strip()
        for line in INVENTORY_PATH.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }
    public_symlinks = {
        str(path.relative_to(PAPER_ROOT))
        for path in PAPER_ROOT.rglob("*")
        if path.is_symlink()
    }
    if public_symlinks:
        raise ValueError(
            f"Paper 02 release package contains symlinks: {sorted(public_symlinks)}"
        )
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
        inventory_path = PAPER_ROOT / relative
        if inventory_path.is_symlink():
            raise ValueError(f"Release manifest may not contain symlinks: {relative}")
        path = inventory_path.resolve()
        try:
            path.relative_to(ROOT)
        except ValueError as exc:
            raise ValueError(
                f"Release manifest path escapes the repository: {relative}"
            ) from exc
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        if observed != expected:
            raise ValueError(f"Release hash mismatch for {relative}")
        if path.suffix in {
            ".md",
            ".tex",
            ".bib",
            ".json",
            ".jsonl",
            ".txt",
            ".py",
            ".sh",
            ".csv",
        }:
            content = path.read_text(errors="ignore")
            if any(value in content for value in FORBIDDEN_LITERALS) or any(
                pattern.search(content) for pattern in FORBIDDEN_PATTERNS
            ):
                raise ValueError(f"Release-sensitive content in {relative}")

    with gzip.open(DATA, "rt", errors="ignore") as handle:
        compressed_content = handle.read()
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
