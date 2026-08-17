#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Reproduce Paper 02 aggregate results from deidentified derived rows."""

from __future__ import annotations

import csv
import gzip
import random
from collections import defaultdict
from math import sqrt
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "papers/p02-source-delegation/data/fid056_p02_deidentified_trials.csv.gz"
RESULTS = ROOT / "papers/p02-source-delegation/results"
METRICS = (
    "delegated_to_source",
    "correct_reference_delegation",
    "source_result_used",
    "quote_span_exact",
    "final_output_exact",
    "text_before_source",
)
BOOTSTRAP_ITERATIONS = 10_000
BOOTSTRAP_SEED = 5602


def load_rows() -> list[dict[str, str]]:
    with gzip.open(DATA, "rt", newline="") as handle:
        return list(csv.DictReader(handle))


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def outcome(row: dict[str, str], metric: str) -> float:
    return float(row[metric])


def wilson(successes: int, total: int) -> tuple[float, float]:
    if not total:
        return (0.0, 0.0)
    z = 1.959963984540054
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    half = z * sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return max(0.0, center - half), min(1.0, center + half)


def equal_route_policy_effect(
    rows: list[dict[str, str]], metric: str, pressure: str
) -> float:
    effects = []
    for route in sorted({row["model_route"] for row in rows}):
        members = [
            row
            for row in rows
            if row["model_route"] == route and row["user_pressure"] == pressure
        ]
        required = [
            outcome(row, metric)
            for row in members
            if row["delegation_policy"] == "source_required"
        ]
        available = [
            outcome(row, metric)
            for row in members
            if row["delegation_policy"] == "available"
        ]
        effects.append(mean(required) - mean(available))
    return mean(effects)


def equal_route_pressure_effect(
    rows: list[dict[str, str]], metric: str, policy: str
) -> float:
    effects = []
    for route in sorted({row["model_route"] for row in rows}):
        members = [
            row
            for row in rows
            if row["model_route"] == route and row["delegation_policy"] == policy
        ]
        discouraged = [
            outcome(row, metric)
            for row in members
            if row["user_pressure"] == "discourage_source"
        ]
        neutral = [
            outcome(row, metric)
            for row in members
            if row["user_pressure"] == "neutral"
        ]
        effects.append(mean(discouraged) - mean(neutral))
    return mean(effects)


def bootstrap_ci(rows: list[dict[str, str]], statistic) -> tuple[float, float]:
    by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_target[row["target_id"]].append(row)
    targets = sorted(by_target)
    cluster_sizes = {len(by_target[target]) for target in targets}
    if len(cluster_sizes) != 1:
        raise ValueError(
            "Target-level bootstrap shortcut requires balanced target clusters"
        )
    target_statistics = {
        target: statistic(by_target[target]) for target in targets
    }
    rng = random.Random(BOOTSTRAP_SEED)
    draws = []
    for _ in range(BOOTSTRAP_ITERATIONS):
        sampled = [rng.choice(targets) for _ in targets]
        # Every released target has the same route/treatment/repetition design,
        # so the statistic on a resampled row set is exactly the mean of the
        # corresponding target-level statistics. Avoiding row materialization
        # keeps the public 10,000-resample analysis fast and transparent.
        draws.append(mean([target_statistics[target] for target in sampled]))
    draws.sort()
    return (
        draws[int(0.025 * (BOOTSTRAP_ITERATIONS - 1))],
        draws[int(0.975 * (BOOTSTRAP_ITERATIONS - 1))],
    )


def clustered_rate_ci(
    rows: list[dict[str, str]], metric: str
) -> tuple[float, float]:
    """Target-cluster bootstrap interval for one observed binary rate."""
    by_target: dict[str, tuple[int, int]] = {}
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["target_id"]].append(row)
    for target, members in grouped.items():
        by_target[target] = (
            sum(int(row[metric]) for row in members),
            len(members),
        )
    targets = sorted(by_target)
    rng = random.Random(BOOTSTRAP_SEED)
    draws = []
    for _ in range(BOOTSTRAP_ITERATIONS):
        sampled = [rng.choice(targets) for _ in targets]
        successes = sum(by_target[target][0] for target in sampled)
        observations = sum(by_target[target][1] for target in sampled)
        draws.append(successes / observations)
    draws.sort()
    return (
        draws[int(0.025 * (BOOTSTRAP_ITERATIONS - 1))],
        draws[int(0.975 * (BOOTSTRAP_ITERATIONS - 1))],
    )


def write_factorial_cells(rows: list[dict[str, str]]) -> None:
    """Write the four headline cell rates with design-consistent intervals."""
    output = []
    for policy in ("available", "source_required"):
        for pressure in ("neutral", "discourage_source"):
            members = [
                row
                for row in rows
                if row["delegation_policy"] == policy
                and row["user_pressure"] == pressure
            ]
            successes = sum(int(row["delegated_to_source"]) for row in members)
            low, high = clustered_rate_ci(members, "delegated_to_source")
            output.append(
                {
                    "delegation_policy": policy,
                    "user_pressure": pressure,
                    "successes": successes,
                    "observations": len(members),
                    "rate": successes / len(members),
                    "ci_low": low,
                    "ci_high": high,
                    "ci_method": "target_cluster_bootstrap",
                    "bootstrap_iterations": BOOTSTRAP_ITERATIONS,
                    "bootstrap_seed": BOOTSTRAP_SEED,
                }
            )
    path = RESULTS / "fid056_p02_factorial_cells.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(output[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(output)


def write_aggregates(rows: list[dict[str, str]]) -> None:
    group_specs = [("overall", ())]
    group_specs.extend(("route", (route,)) for route in sorted({r["model_route"] for r in rows}))
    group_specs.extend(("prompt_family", (prompt,)) for prompt in sorted({r["prompt_family"] for r in rows}))
    output = []
    for level, keys in group_specs:
        for policy in ("available", "source_required"):
            for pressure in ("neutral", "discourage_source"):
                members = [
                    row
                    for row in rows
                    if row["delegation_policy"] == policy
                    and row["user_pressure"] == pressure
                    and (
                        level == "overall"
                        or (level == "route" and row["model_route"] == keys[0])
                        or (level == "prompt_family" and row["prompt_family"] == keys[0])
                    )
                ]
                for metric in METRICS:
                    successes = sum(int(row[metric]) for row in members)
                    low, high = wilson(successes, len(members))
                    output.append(
                        {
                            "level": level,
                            "stratum": keys[0] if keys else "all",
                            "delegation_policy": policy,
                            "user_pressure": pressure,
                            "metric": metric,
                            "successes": successes,
                            "observations": len(members),
                            "rate": successes / len(members),
                            "ci_low": low,
                            "ci_high": high,
                            "ci_method": "wilson_observation_level_descriptive",
                            "metric_note": (
                                "sealed_specification_mismatch_do_not_interpret_as_visible_pre_call_text"
                                if metric == "text_before_source"
                                else ""
                            ),
                        }
                    )
    path = RESULTS / "fid056_p02_aggregate_results.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(output[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(output)


def effect_row(name: str, estimate: float, ci: tuple[float, float]) -> dict[str, object]:
    return {
        "estimand": name,
        "estimate": estimate,
        "ci_low": ci[0],
        "ci_high": ci[1],
        "bootstrap_iterations": BOOTSTRAP_ITERATIONS,
        "bootstrap_seed": BOOTSTRAP_SEED,
    }


def write_effects(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    specs = [
        (
            "primary_policy_effect_neutral",
            lambda sample: equal_route_policy_effect(sample, "delegated_to_source", "neutral"),
        ),
        (
            "policy_effect_discourage_source",
            lambda sample: equal_route_policy_effect(
                sample, "delegated_to_source", "discourage_source"
            ),
        ),
        (
            "pressure_effect_available",
            lambda sample: equal_route_pressure_effect(
                sample, "delegated_to_source", "available"
            ),
        ),
        (
            "pressure_effect_source_required",
            lambda sample: equal_route_pressure_effect(
                sample, "delegated_to_source", "source_required"
            ),
        ),
        (
            "correct_reference_policy_effect_neutral",
            lambda sample: equal_route_policy_effect(
                sample, "correct_reference_delegation", "neutral"
            ),
        ),
        (
            "quote_span_exactness_policy_effect_neutral",
            lambda sample: equal_route_policy_effect(
                sample, "quote_span_exact", "neutral"
            ),
        ),
        (
            "final_exactness_policy_effect_neutral",
            lambda sample: equal_route_policy_effect(
                sample, "final_output_exact", "neutral"
            ),
        ),
    ]
    effects = [effect_row(name, statistic(rows), bootstrap_ci(rows, statistic)) for name, statistic in specs]
    primary = effects[0]
    pressured = effects[1]
    interaction_stat = lambda sample: (  # noqa: E731
        equal_route_policy_effect(sample, "delegated_to_source", "discourage_source")
        - equal_route_policy_effect(sample, "delegated_to_source", "neutral")
    )
    effects.append(
        effect_row(
            "policy_by_pressure_interaction",
            float(pressured["estimate"]) - float(primary["estimate"]),
            bootstrap_ci(rows, interaction_stat),
        )
    )
    path = RESULTS / "fid056_p02_effect_estimates.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(effects[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(effects)
    return effects


def write_route_effects(rows: list[dict[str, str]]) -> None:
    output = []
    for route in sorted({row["model_route"] for row in rows}):
        members = [row for row in rows if row["model_route"] == route]
        neutral_statistic = lambda sample: equal_route_policy_effect(  # noqa: E731
            sample, "delegated_to_source", "neutral"
        )
        conflict_statistic = lambda sample: equal_route_policy_effect(  # noqa: E731
            sample, "delegated_to_source", "discourage_source"
        )
        neutral_estimate = neutral_statistic(members)
        neutral_low, neutral_high = bootstrap_ci(members, neutral_statistic)
        conflict_estimate = conflict_statistic(members)
        conflict_low, conflict_high = bootstrap_ci(members, conflict_statistic)
        output.append(
            {
                "model_route": route,
                "observations": len(members),
                "policy_effect_neutral": neutral_estimate,
                "neutral_ci_low": neutral_low,
                "neutral_ci_high": neutral_high,
                "neutral_interval_note": (
                    "constant_across_target_clusters"
                    if neutral_low == neutral_high
                    else "target_cluster_bootstrap"
                ),
                "policy_effect_discourage_source": conflict_estimate,
                "conflict_ci_low": conflict_low,
                "conflict_ci_high": conflict_high,
                "conflict_interval_note": (
                    "constant_across_target_clusters"
                    if conflict_low == conflict_high
                    else "target_cluster_bootstrap"
                ),
            }
        )
    path = RESULTS / "fid056_p02_route_effects.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(output[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(output)


def write_subgroup_effects(rows: list[dict[str, str]]) -> None:
    output = []
    for dimension in ("prompt_family", "passage_stratum"):
        for value in sorted({row[dimension] for row in rows}):
            members = [row for row in rows if row[dimension] == value]
            statistic = lambda sample: equal_route_policy_effect(  # noqa: E731
                sample, "delegated_to_source", "neutral"
            )
            estimate = statistic(members)
            low, high = bootstrap_ci(members, statistic)
            output.append(
                {
                    "dimension": dimension,
                    "stratum": value,
                    "observations": len(members),
                    "policy_effect_neutral": estimate,
                    "ci_low": low,
                    "ci_high": high,
                }
            )
    path = RESULTS / "fid056_p02_subgroup_effects.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(output[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(output)


def conditional_rate(
    rows: list[dict[str, str]], numerator: str, denominator: str
) -> tuple[int, int, float]:
    selected = [row for row in rows if int(row[denominator]) == 1]
    successes = sum(int(row[numerator]) for row in selected)
    return successes, len(selected), successes / len(selected) if selected else 0.0


def write_delegation_pipeline(rows: list[dict[str, str]]) -> None:
    groups = [("overall", "all", rows)]
    for policy in ("available", "source_required"):
        for pressure in ("neutral", "discourage_source"):
            members = [
                row
                for row in rows
                if row["delegation_policy"] == policy
                and row["user_pressure"] == pressure
            ]
            groups.append((policy, pressure, members))
    output = []
    for policy, pressure, members in groups:
        for label, numerator, denominator in (
            (
                "correct_reference_given_delegation",
                "correct_reference_delegation",
                "delegated_to_source",
            ),
            (
                "source_result_used_given_correct_reference",
                "source_result_used",
                "correct_reference_delegation",
            ),
            (
                "quote_span_exact_given_correct_reference",
                "quote_span_exact",
                "correct_reference_delegation",
            ),
            (
                "final_output_exact_given_correct_reference",
                "final_output_exact",
                "correct_reference_delegation",
            ),
            (
                "quote_span_exact_given_bypass",
                "quote_span_exact",
                "source_bypass",
            ),
        ):
            successes, observations, rate = conditional_rate(
                members, numerator, denominator
            )
            output.append(
                {
                    "delegation_policy": policy,
                    "user_pressure": pressure,
                    "conditional_metric": label,
                    "successes": successes,
                    "observations": observations,
                    "rate": rate,
                }
            )
    path = RESULTS / "fid056_p02_delegation_pipeline.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(output[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(output)


def sample_standard_deviation(values: list[float]) -> float:
    center = mean(values)
    return sqrt(sum((value - center) ** 2 for value in values) / (len(values) - 1))


def route_effects(rows: list[dict[str, str]], pressure: str) -> list[float]:
    return [
        equal_route_policy_effect(
            [row for row in rows if row["model_route"] == route],
            "delegated_to_source",
            pressure,
        )
        for route in sorted({row["model_route"] for row in rows})
    ]


def route_as_unit_interval(values: list[float]) -> tuple[float, float]:
    # Two-sided 95% Student-t critical value for six fixed route observations.
    critical = 2.570581835636305
    center = mean(values)
    half = critical * sample_standard_deviation(values) / sqrt(len(values))
    return center - half, center + half


def write_sensitivity_analysis(rows: list[dict[str, str]]) -> None:
    routes = sorted({row["model_route"] for row in rows})
    conflict = route_effects(rows, "discourage_source")
    neutral = route_effects(rows, "neutral")
    interaction = [left - right for left, right in zip(conflict, neutral)]
    output = []
    for name, values in (
        ("policy_effect_neutral_route_as_unit", neutral),
        ("policy_effect_conflict_route_as_unit", conflict),
        ("policy_by_pressure_interaction_route_as_unit", interaction),
    ):
        low, high = route_as_unit_interval(values)
        output.append(
            {
                "analysis": name,
                "estimate": mean(values),
                "lower": low,
                "upper": high,
                "method": "route_as_unit_student_t_df5",
                "detail": "generalization sensitivity; not preregistered inference",
            }
        )

    leave_route_out = []
    for route in routes:
        members = [row for row in rows if row["model_route"] != route]
        leave_route_out.append(
            (
                equal_route_policy_effect(
                    members, "delegated_to_source", "discourage_source"
                ),
                route,
            )
        )
    route_min = min(leave_route_out)
    route_max = max(leave_route_out)
    output.append(
        {
            "analysis": "policy_effect_conflict_leave_one_route_out",
            "estimate": equal_route_policy_effect(
                rows, "delegated_to_source", "discourage_source"
            ),
            "lower": route_min[0],
            "upper": route_max[0],
            "method": "leave_one_route_out_range",
            "detail": f"minimum drops {route_min[1]}; maximum drops {route_max[1]}",
        }
    )

    targets = sorted({row["target_id"] for row in rows})
    leave_target_out = []
    for target in targets:
        members = [row for row in rows if row["target_id"] != target]
        leave_target_out.append(
            (
                equal_route_policy_effect(
                    members, "quote_span_exact", "neutral"
                ),
                target,
            )
        )
    target_min = min(leave_target_out)
    target_max = max(leave_target_out)
    output.append(
        {
            "analysis": "neutral_span_exactness_leave_one_target_out",
            "estimate": equal_route_policy_effect(rows, "quote_span_exact", "neutral"),
            "lower": target_min[0],
            "upper": target_max[0],
            "method": "leave_one_target_out_range",
            "detail": (
                f"minimum drops {target_min[1]}; maximum drops {target_max[1]}"
            ),
        }
    )
    path = RESULTS / "fid056_p02_sensitivity_analysis.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(output[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(output)


def write_repetition_sensitivity(rows: list[dict[str, str]]) -> None:
    output = []
    for repetition in sorted({row["repetition"] for row in rows}, key=int):
        for policy in ("available", "source_required"):
            for pressure in ("neutral", "discourage_source"):
                members = [
                    row
                    for row in rows
                    if row["repetition"] == repetition
                    and row["delegation_policy"] == policy
                    and row["user_pressure"] == pressure
                ]
                output.append(
                    {
                        "repetition": repetition,
                        "delegation_policy": policy,
                        "user_pressure": pressure,
                        "observations": len(members),
                        "delegation_rate": mean(
                            [outcome(row, "delegated_to_source") for row in members]
                        ),
                        "quote_span_exact_rate": mean(
                            [outcome(row, "quote_span_exact") for row in members]
                        ),
                    }
                )
    path = RESULTS / "fid056_p02_repetition_sensitivity.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(output[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(output)


def write_result_card(rows: list[dict[str, str]], effects: list[dict[str, object]]) -> None:
    errors = sum(int(row["terminal_error"]) for row in rows)
    primary = next(row for row in effects if row["estimand"] == "primary_policy_effect_neutral")
    text = f"""# FID-056-P02 Result Card

## Execution

- Scheduled observations: 4,800
- Released derived observations: {len(rows):,}
- Terminal errors: {errors:,}
- Target clusters: {len({row['target_id'] for row in rows})}
- Model-family routes: {len({row['model_route'] for row in rows})}

## Primary Estimate

The source-required policy changed delegation under neutral user wording by
{100 * float(primary['estimate']):.2f} percentage points (95% target-cluster
bootstrap interval {100 * float(primary['ci_low']):.2f} to
{100 * float(primary['ci_high']):.2f}).

## Boundary

This is a treatment effect within the locked Scripture quotation study. The
target-cluster interval conditions on six purposively selected routes; separate
route-generalization sensitivities are reported. The result is not a general
model ranking or a claim about theological interpretation.
"""
    (RESULTS / "fid056_p02_result_card.md").write_text(text)


def main() -> None:
    rows = load_rows()
    if len(rows) != 4_800:
        raise ValueError(f"Expected 4,800 observations, found {len(rows)}")
    if len({row["observation_id"] for row in rows}) != len(rows):
        raise ValueError("Duplicate observation IDs")
    RESULTS.mkdir(parents=True, exist_ok=True)
    write_aggregates(rows)
    write_factorial_cells(rows)
    effects = write_effects(rows)
    write_route_effects(rows)
    write_subgroup_effects(rows)
    write_delegation_pipeline(rows)
    write_sensitivity_analysis(rows)
    write_repetition_sensitivity(rows)
    write_result_card(rows, effects)
    print(f"Analyzed {len(rows)} observations")


if __name__ == "__main__":
    main()
