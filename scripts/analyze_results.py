#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy==2.3.2",
#   "pandas==2.3.1",
#   "scipy==1.16.1",
#   "statsmodels==0.14.5",
# ]
# ///
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fide AI
"""Reproduce target-level and cluster-aware FID-056-P01 analyses."""

from __future__ import annotations

import argparse
import random
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import t

CONDITIONS = (
    "native_parametric",
    "source_supplied",
    "tool_mediated",
    "deterministic_rendering",
)
MODEL_LABELS = {
    "anthropic/claude-sonnet-5": "Claude_Sonnet_5",
    "deepseek/deepseek-v4-pro": "DeepSeek_V4_Pro",
    "google/gemini-3.5-flash": "Gemini_3_5_Flash",
    "openai/gpt-5.6-sol": "GPT_5_6_Sol",
    "z-ai/glm-5.2": "GLM_5_2",
    "moonshotai/kimi-k3": "Kimi_K3",
}
STRATUM_LABELS = {
    "explicit_single_verse": "single_verse",
    "explicit_short_passage": "short_passage",
    "indirect_event_reference": "indirect_event",
    "long_passage_guardrail_probe": "long_passage",
}
OUTCOMES = (
    "end_to_end_exact",
    "final_output_exact",
    "parser_adjusted_end_to_end_exact",
)


def _validate(df: pd.DataFrame) -> None:
    if len(df) != 8640:
        raise ValueError(f"Expected 8,640 rows, found {len(df):,}")
    if set(df["condition"]) != set(CONDITIONS):
        raise ValueError(f"Unexpected condition panel: {sorted(df['condition'].unique())}")
    if df["release_trial_id"].duplicated().any():
        raise ValueError("release_trial_id is not unique")
    required_outcomes = {
        "end_to_end_exact",
        "final_output_exact",
        "locked_end_to_end_exact",
        "corrected_end_to_end_exact",
        "locked_final_output_exact",
        "corrected_final_output_exact",
        "parser_correction_applied",
    }
    missing = required_outcomes - set(df.columns)
    if missing:
        raise ValueError(f"Missing locked/corrected outcome columns: {sorted(missing)}")
    expected = {
        "target_review_id": 20,
        "prompt_family": 2,
        "condition": 4,
        "translation": 3,
        "model_route": 6,
        "epoch": 3,
    }
    observed = {column: df[column].nunique() for column in expected}
    if observed != expected:
        raise ValueError(f"Factor mismatch: expected {expected}, observed {observed}")


def _target_level(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby(
            ["target_review_id", "reference", "passage_stratum", "condition"],
            observed=True,
        )
        .agg(
            observations=("release_trial_id", "size"),
            end_to_end_successes=("end_to_end_exact", "sum"),
            architecture_adherent_rate=("end_to_end_exact", "mean"),
            final_output_successes=("final_output_exact", "sum"),
            final_output_exact_rate=("final_output_exact", "mean"),
            parser_adjusted_successes=("parser_adjusted_end_to_end_exact", "sum"),
            parser_adjusted_rate=("parser_adjusted_end_to_end_exact", "mean"),
        )
        .reset_index()
    )
    return grouped


def _distribution_summary(target: pd.DataFrame) -> pd.DataFrame:
    records = []
    for condition in CONDITIONS:
        subset = target[target["condition"] == condition]
        for outcome, column in (
            ("architecture_adherent", "architecture_adherent_rate"),
            ("final_output_exact", "final_output_exact_rate"),
            ("parser_adjusted", "parser_adjusted_rate"),
        ):
            values = subset[column].to_numpy()
            records.append(
                {
                    "condition": condition,
                    "outcome": outcome,
                    "targets": len(values),
                    "mean": np.mean(values),
                    "median": np.median(values),
                    "q1": np.quantile(values, 0.25),
                    "q3": np.quantile(values, 0.75),
                    "minimum": np.min(values),
                    "maximum": np.max(values),
                }
            )
    return pd.DataFrame(records).round(6)


def _cluster_bootstrap(
    target: pd.DataFrame, *, outcome_column: str, seed: int = 5601
) -> pd.DataFrame:
    wide = target.pivot(
        index="reference", columns="condition", values=outcome_column
    ).loc[:, CONDITIONS]
    records = []
    for condition in CONDITIONS[1:]:
        differences = (
            wide[condition] - wide["native_parametric"]
        ).tolist()
        rng = random.Random(seed)
        samples = []
        for _ in range(10_000):
            draw = [rng.choice(differences) for _ in differences]
            samples.append(sum(draw) / len(draw))
        samples.sort()
        low_index = int(0.025 * (len(samples) - 1))
        high_index = int(0.975 * (len(samples) - 1))
        records.append(
            {
                "outcome": outcome_column,
                "contrast": f"{condition}_vs_native_parametric",
                "estimate": np.mean(differences),
                "target_cluster_bootstrap_low": samples[low_index],
                "target_cluster_bootstrap_high": samples[high_index],
                "targets": len(wide),
                "resamples": len(samples),
                "seed": seed,
            }
        )
    return pd.DataFrame(records).round(6)


def _cluster_robust_lpm(df: pd.DataFrame, outcome: str) -> pd.DataFrame:
    formula = (
        f"{outcome} ~ "
        "C(condition, Treatment(reference='native_parametric')) + "
        "C(model_route) + C(translation) + C(prompt_family) + "
        "C(passage_stratum) + C(epoch)"
    )
    fitted = smf.ols(formula, data=df).fit(
        cov_type="cluster",
        cov_kwds={
            "groups": df["target_review_id"],
            "use_correction": True,
            "df_correction": True,
        },
        use_t=True,
    )
    critical = t.ppf(0.975, df=df["target_review_id"].nunique() - 1)
    records = []
    for condition in CONDITIONS[1:]:
        term = (
            "C(condition, Treatment(reference='native_parametric'))"
            f"[T.{condition}]"
        )
        estimate = fitted.params[term]
        standard_error = fitted.bse[term]
        records.append(
            {
                "outcome": outcome,
                "contrast": f"{condition}_vs_native_parametric",
                "adjusted_risk_difference": estimate,
                "cluster_robust_standard_error": standard_error,
                "t19_low": estimate - critical * standard_error,
                "t19_high": estimate + critical * standard_error,
                "target_clusters": df["target_review_id"].nunique(),
                "observations": len(df),
                "model": "linear_probability_fixed_panel_target_cluster_robust",
            }
        )
    return pd.DataFrame(records).round(6)


def _update_aggregate_results(df: pd.DataFrame, output_dir: Path) -> None:
    path = output_dir / "fid056_p01_aggregate_results.csv"
    existing = pd.read_csv(path)
    existing = existing[existing["analysis"] != "parser_adjusted"]
    legacy_labels = {
        "primary": "locked_primary",
        "common_final_output": "locked_common_final_output",
        "prompt_family": "locked_prompt_family",
        "edition": "locked_edition",
        "passage_stratum": "locked_passage_stratum",
        "model_family": "locked_model_family",
        "epoch": "locked_epoch",
    }
    existing["analysis"] = existing["analysis"].replace(legacy_labels)
    records = []
    groupings = (
        ("overall", None, None),
        ("prompt_family", "prompt_family", None),
        ("edition", "translation", None),
        ("passage_stratum", "passage_stratum", STRATUM_LABELS),
        ("model_family", "model_route", MODEL_LABELS),
        ("epoch", "epoch", {1: "epoch_1", 2: "epoch_2", 3: "epoch_3"}),
    )
    for analysis_level, column, labels in groupings:
        grouped = [("overall", df)] if column is None else df.groupby(column)
        for level, members in grouped:
            output_level = labels.get(level, level) if labels else level
            for condition in CONDITIONS:
                subset = members[members["condition"] == condition]
                exact = int(subset["parser_adjusted_end_to_end_exact"].sum())
                total = len(subset)
                records.append(
                    {
                        "analysis": "parser_adjusted",
                        "level": "overall" if analysis_level == "overall" else output_level,
                        "condition": condition,
                        "exact": exact,
                        "n": total,
                        "rate_percent": round(100 * exact / total, 2),
                        "interval_or_note": (
                            "corrected complete parser replay"
                            if condition == "deterministic_rendering"
                            else "unchanged from locked architecture-adherent outcome"
                        ),
                    }
                )
    pd.concat([existing, pd.DataFrame(records)], ignore_index=True).to_csv(
        path, index=False
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--trials",
        type=Path,
        default=Path("papers/p01-scripture-quotation/data/fid056_p01_deidentified_trials.csv.gz"),
    )
    parser.add_argument(
        "--parser-replay",
        type=Path,
        default=Path(
            "papers/p01-scripture-quotation/results/"
            "fid056_p01_permissive_parser_replay.csv"
        ),
    )
    parser.add_argument("--output-dir", type=Path, default=Path("papers/p01-scripture-quotation/results"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.trials)
    _validate(df)
    replay = pd.read_csv(args.parser_replay)
    if len(replay) != 2_160 or replay["release_trial_id"].duplicated().any():
        raise ValueError("Parser replay must contain 2,160 unique deterministic rows")
    deterministic_ids = set(
        df.loc[df["condition"] == "deterministic_rendering", "release_trial_id"]
    )
    if set(replay["release_trial_id"]) != deterministic_ids:
        raise ValueError("Parser replay IDs do not match the deterministic panel")
    df = df.merge(
        replay[
            [
                "release_trial_id",
                "permissive_parser_replay_exact",
                "permissive_parser_replay_final_output_exact",
            ]
        ],
        on="release_trial_id",
        how="left",
        validate="one_to_one",
    )
    deterministic = df["condition"] == "deterministic_rendering"
    if not (df["end_to_end_exact"] == df["locked_end_to_end_exact"]).all():
        raise ValueError("Legacy end_to_end_exact no longer matches the locked endpoint")
    if not (df["final_output_exact"] == df["locked_final_output_exact"]).all():
        raise ValueError("Legacy final_output_exact no longer matches the locked endpoint")
    if not (
        df.loc[deterministic, "corrected_end_to_end_exact"]
        == df.loc[deterministic, "permissive_parser_replay_exact"]
    ).all():
        raise ValueError("Corrected endpoint does not match the parser replay")
    if not (
        df.loc[deterministic, "corrected_final_output_exact"]
        == df.loc[deterministic, "permissive_parser_replay_final_output_exact"]
    ).all():
        raise ValueError("Corrected final-output endpoint does not match the parser replay")
    nondeterministic = ~deterministic
    if not (
        df.loc[nondeterministic, "corrected_end_to_end_exact"]
        == df.loc[nondeterministic, "locked_end_to_end_exact"]
    ).all():
        raise ValueError("Non-deterministic corrected endpoints must equal locked endpoints")
    if int(df["parser_correction_applied"].sum()) != 158:
        raise ValueError("Expected exactly 158 parser-corrected observations")
    df["parser_adjusted_end_to_end_exact"] = df["corrected_end_to_end_exact"]
    df["final_output_exact"] = df["corrected_final_output_exact"]
    for outcome in OUTCOMES:
        df[outcome] = df[outcome].astype(float)

    target = _target_level(df)
    target.round(6).to_csv(
        args.output_dir / "fid056_p01_target_level_results.csv", index=False
    )
    _distribution_summary(target).to_csv(
        args.output_dir / "fid056_p01_target_distribution_summary.csv",
        index=False,
    )
    pd.concat(
        [
            _cluster_bootstrap(
                target,
                outcome_column=(
                    "architecture_adherent_rate"
                    if outcome == "end_to_end_exact"
                    else (
                        "final_output_exact_rate"
                        if outcome == "final_output_exact"
                        else "parser_adjusted_rate"
                    )
                ),
            )
            for outcome in OUTCOMES
        ],
        ignore_index=True,
    ).to_csv(args.output_dir / "fid056_p01_cluster_bootstrap.csv", index=False)
    pd.concat(
        [_cluster_robust_lpm(df, outcome) for outcome in OUTCOMES],
        ignore_index=True,
    ).to_csv(
        args.output_dir / "fid056_p01_cluster_robust_sensitivity.csv",
        index=False,
    )
    _update_aggregate_results(df, args.output_dir)


if __name__ == "__main__":
    main()
