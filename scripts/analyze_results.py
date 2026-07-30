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
from scipy.stats import t
import statsmodels.formula.api as smf


CONDITIONS = (
    "native_parametric",
    "source_supplied",
    "tool_mediated",
    "deterministic_rendering",
)
OUTCOMES = ("end_to_end_exact", "final_output_exact")


def _validate(df: pd.DataFrame) -> None:
    if len(df) != 8640:
        raise ValueError(f"Expected 8,640 rows, found {len(df):,}")
    if set(df["condition"]) != set(CONDITIONS):
        raise ValueError(f"Unexpected condition panel: {sorted(df['condition'].unique())}")
    if df["release_trial_id"].duplicated().any():
        raise ValueError("release_trial_id is not unique")
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--trials",
        type=Path,
        default=Path("papers/p01-scripture-quotation/data/fid056_p01_deidentified_trials.csv.gz"),
    )
    parser.add_argument("--output-dir", type=Path, default=Path("papers/p01-scripture-quotation/results"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.trials)
    _validate(df)
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
                    else "final_output_exact_rate"
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


if __name__ == "__main__":
    main()
