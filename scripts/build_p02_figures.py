#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib==3.10.3", "numpy==2.3.2"]
# ///
"""Build Paper 02 architecture and result figures."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "papers/p02-source-delegation/results"
OUTPUT = ROOT / "papers/p02-source-delegation/paper/figures"
COLORS = {
    "available": "#62676D",
    "required": "#23877B",
    "pressure": "#B4513B",
    "exact": "#356FA3",
    "ink": "#202124",
    "muted": "#62676D",
    "grid": "#D8DBDE",
    "paper": "#F5F6F7",
}
PDF_METADATA = {
    "Creator": "FID-056-P02 source delegation analysis",
    "Producer": "Matplotlib",
    "CreationDate": datetime(2026, 8, 12, tzinfo=timezone.utc),
    "ModDate": datetime(2026, 8, 12, tzinfo=timezone.utc),
}


def configure() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 11,
            "axes.labelsize": 9,
            "axes.edgecolor": COLORS["ink"],
            "axes.linewidth": 0.8,
            "pdf.fonttype": 42,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.08,
        }
    )
    OUTPUT.mkdir(parents=True, exist_ok=True)


def architecture() -> None:
    fig, ax = plt.subplots(figsize=(11.3, 3.9))
    ax.set_xlim(0, 12.8)
    ax.set_ylim(0.5, 4.35)
    ax.axis("off")
    boxes = (
        (
            0.2,
            2.7,
            "System policy",
            "Source available\nor source required",
            COLORS["required"],
        ),
        (
            0.2,
            0.7,
            "User request",
            "Neutral or asks to\navoid the source",
            COLORS["pressure"],
        ),
        (
            3.8,
            1.7,
            "Model decision",
            "Invoke get_passage\nor answer from memory",
            COLORS["ink"],
        ),
        (
            7.2,
            2.7,
            "Source action",
            "Reference requested\nand passage returned",
            COLORS["required"],
        ),
        (
            7.2,
            0.7,
            "Bypass",
            "No source event before\nthe final answer",
            COLORS["available"],
        ),
        (
            10.2,
            1.7,
            "Final answer",
            "Returned text may still\nbe preserved or altered",
            COLORS["exact"],
        ),
    )
    for x, y, title, body, color in boxes:
        ax.add_patch(
            Rectangle(
                (x, y),
                2.35,
                1.08,
                facecolor=COLORS["paper"],
                edgecolor=color,
                linewidth=1.25,
            )
        )
        ax.text(x + 0.15, y + 0.83, title, fontweight="bold", color=color, va="top")
        ax.text(x + 0.15, y + 0.55, body, va="top", fontsize=8.4, linespacing=1.2)
    arrows = (
        ((2.58, 3.24), (3.72, 2.55)),
        ((2.58, 1.24), (3.72, 2.05)),
        ((6.18, 2.38), (7.12, 3.12)),
        ((6.18, 2.08), (7.12, 1.24)),
        ((9.58, 3.12), (10.12, 2.55)),
        ((9.58, 1.24), (10.12, 2.05)),
    )
    for start, end in arrows:
        ax.add_patch(
            FancyArrowPatch(
                start,
                end,
                arrowstyle="-|>",
                mutation_scale=10,
                linewidth=1,
                color=COLORS["muted"],
            )
        )
    ax.text(
        0.2,
        4.14,
        "A source tool can be present without governing the answer",
        fontsize=11,
        fontweight="bold",
    )
    ax.text(
        0.2,
        3.91,
        "The source-required policy changes the instruction, not the model's technical ability to bypass it.",
        color=COLORS["muted"],
    )
    fig.savefig(OUTPUT / "fig1_delegation_design.pdf", metadata=PDF_METADATA)
    plt.close(fig)


def load_aggregates() -> list[dict[str, str]]:
    with (RESULTS / "fid056_p02_aggregate_results.csv").open(newline="") as handle:
        return list(csv.DictReader(handle))


def delegation_cells() -> None:
    with (RESULTS / "fid056_p02_factorial_cells.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    order = [
        ("available", "neutral"),
        ("available", "discourage_source"),
        ("source_required", "neutral"),
        ("source_required", "discourage_source"),
    ]
    selected = [
        next(
            row
            for row in rows
            if (row["delegation_policy"], row["user_pressure"]) == key
        )
        for key in order
    ]
    values = np.array([100 * float(row["rate"]) for row in selected])
    lower = values - np.array([100 * float(row["ci_low"]) for row in selected])
    upper = np.array([100 * float(row["ci_high"]) for row in selected]) - values
    labels = [
        "Available\nNeutral",
        "Available\nAvoid source",
        "Required\nNeutral",
        "Required\nAvoid source",
    ]
    colors = [
        COLORS["available"],
        COLORS["pressure"],
        COLORS["required"],
        COLORS["required"],
    ]
    fig, ax = plt.subplots(figsize=(8.8, 4.4))
    x = np.arange(4)
    bars = ax.bar(x, values, color=colors, width=0.66)
    ax.errorbar(
        x,
        values,
        yerr=np.vstack([lower, upper]),
        fmt="none",
        ecolor=COLORS["ink"],
        capsize=3,
        linewidth=1,
    )
    ax.set_ylim(0, 105)
    ax.set_ylabel("Delegated to source (%)")
    ax.set_xticks(x, labels)
    ax.grid(axis="y", color=COLORS["grid"], linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            min(value + 2.5, 101),
            f"{value:.1f}%",
            ha="center",
            fontweight="bold",
        )
    ax.set_title(
        "Observed source delegation in the four conditions",
        loc="left",
        fontweight="bold",
    )
    fig.savefig(OUTPUT / "fig2_delegation_cells.pdf", metadata=PDF_METADATA)
    plt.close(fig)


def route_forest() -> None:
    with (RESULTS / "fid056_p02_route_effects.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    display_names = {
        "anthropic-claude-sonnet-5": "Claude Sonnet 5",
        "deepseek-v4-pro-together": "DeepSeek V4 Pro",
        "google-gemini-3-5-flash": "Gemini 3.5 Flash",
        "moonshot-kimi-k3": "Kimi K3",
        "openai-gpt-5-6-sol": "GPT-5.6 Sol",
        "zai-glm-5-2-together": "GLM-5.2",
    }
    labels = [display_names.get(row["model_route"], row["model_route"]) for row in rows]
    estimates = np.array(
        [100 * float(row["policy_effect_discourage_source"]) for row in rows]
    )
    lows = np.array([100 * float(row["conflict_ci_low"]) for row in rows])
    highs = np.array([100 * float(row["conflict_ci_high"]) for row in rows])
    y = np.arange(len(rows))
    fig, ax = plt.subplots(figsize=(9.1, 5.2))
    ax.axvline(0, color=COLORS["muted"], linewidth=0.9)
    ax.errorbar(
        estimates,
        y,
        xerr=np.vstack([estimates - lows, highs - estimates]),
        fmt="o",
        color=COLORS["required"],
        ecolor=COLORS["ink"],
        capsize=3,
    )
    ax.set_yticks(y, labels, fontsize=9)
    ax.tick_params(axis="y", length=0)
    ax.invert_yaxis()
    ax.set_xlim(-5, 105)
    ax.set_xlabel(
        "Source-required minus available delegation under user conflict\n"
        "(percentage points)"
    )
    ax.grid(axis="x", color=COLORS["grid"], linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.set_title(
        "Instruction-conflict effects vary across evaluated routes",
        loc="left",
        fontweight="bold",
    )
    fig.savefig(OUTPUT / "fig3_route_effects.pdf", metadata=PDF_METADATA)
    plt.close(fig)


def delegation_pipeline() -> None:
    with (RESULTS / "fid056_p02_delegation_pipeline.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    overall = {
        row["conditional_metric"]: row
        for row in rows
        if row["delegation_policy"] == "overall" and row["user_pressure"] == "all"
    }
    correct = overall["correct_reference_given_delegation"]
    exact = overall["quote_span_exact_given_correct_reference"]
    bypass = overall["quote_span_exact_given_bypass"]
    delegated = int(correct["observations"])
    bypassed = int(bypass["observations"])
    total = delegated + bypassed

    fig, ax = plt.subplots(figsize=(11.3, 4.2))
    ax.set_xlim(0, 13.3)
    ax.set_ylim(0.1, 4.15)
    ax.axis("off")

    boxes = (
        (
            0.2,
            2.05,
            "All requests",
            f"{total:,}\nconfirmatory observations",
            COLORS["ink"],
        ),
        (
            3.45,
            2.05,
            "Source invoked",
            f"{delegated:,} / {total:,}\n({100 * delegated / total:.1f}% of requests)",
            COLORS["required"],
        ),
        (
            6.7,
            2.05,
            "Intended reference",
            f"{int(correct['successes']):,} / {delegated:,}\n({100 * float(correct['rate']):.1f}% of calls)",
            COLORS["required"],
        ),
        (
            9.95,
            2.05,
            "Exact quotation span",
            f"{int(exact['successes']):,} / {int(exact['observations']):,}\n({100 * float(exact['rate']):.1f}% after selection)",
            COLORS["exact"],
        ),
        (
            3.45,
            0.25,
            "Source bypassed",
            f"{bypassed:,} / {total:,}; {int(bypass['successes']):,} exact from memory\n({100 * float(bypass['rate']):.1f}% of bypasses)",
            COLORS["pressure"],
        ),
    )
    for x, y_pos, title, body, color in boxes:
        width = 2.55 if title != "Source bypassed" else 3.35
        ax.add_patch(
            Rectangle(
                (x, y_pos),
                width,
                1.15,
                facecolor=COLORS["paper"],
                edgecolor=color,
                linewidth=1.3,
            )
        )
        ax.text(x + 0.16, y_pos + 0.88, title, fontweight="bold", color=color, va="top")
        ax.text(x + 0.16, y_pos + 0.59, body, va="top", fontsize=8.4, linespacing=1.18)

    for start, end in (
        ((2.78, 2.63), (3.37, 2.63)),
        ((6.03, 2.63), (6.62, 2.63)),
        ((9.28, 2.63), (9.87, 2.63)),
        ((2.0, 2.02), (3.37, 1.12)),
    ):
        ax.add_patch(
            FancyArrowPatch(
                start,
                end,
                arrowstyle="-|>",
                mutation_scale=10,
                linewidth=1,
                color=COLORS["muted"],
            )
        )
    ax.text(
        0.2,
        3.88,
        "A source call begins, rather than completes, exact delivery",
        fontsize=11,
        fontweight="bold",
    )
    ax.text(
        0.2,
        3.64,
        "The main path reports conditional counts; bypassed requests are shown separately.",
        color=COLORS["muted"],
    )
    fig.savefig(OUTPUT / "fig4_delegation_pipeline.pdf", metadata=PDF_METADATA)
    plt.close(fig)


def main() -> None:
    configure()
    architecture()
    if (RESULTS / "fid056_p02_aggregate_results.csv").exists():
        delegation_cells()
        route_forest()
        delegation_pipeline()
    print(f"Wrote Paper 02 figures to {OUTPUT}")


if __name__ == "__main__":
    main()
