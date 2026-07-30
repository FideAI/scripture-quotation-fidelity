#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "matplotlib==3.10.3",
#   "numpy==2.3.2",
# ]
# ///
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fide AI
"""Build the explanatory figures used in the authoritative-quotation paper."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch, Rectangle
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "papers/p01-scripture-quotation/paper/figures"
AGGREGATES = ROOT / "papers/p01-scripture-quotation/results/fid056_p01_aggregate_results.csv"
OUTPUT.mkdir(parents=True, exist_ok=True)

COLORS = {
    "native": "#555555",
    "source": "#23877B",
    "tool": "#356FA3",
    "deterministic": "#B4513B",
    "ink": "#202124",
    "muted": "#62676D",
    "grid": "#D8DBDE",
}
PDF_METADATA = {
    "Creator": "Authoritative Quotation Evaluation",
    "Producer": "Matplotlib",
    "CreationDate": datetime(2026, 7, 27, tzinfo=timezone.utc),
    "ModDate": datetime(2026, 7, 27, tzinfo=timezone.utc),
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
            "ps.fonttype": 42,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.08,
        }
    )


def aggregate_rate(analysis: str, level: str, condition: str) -> float:
    with AGGREGATES.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if (
                row["analysis"] == analysis
                and row["level"] == level
                and row["condition"] == condition
            ):
                return float(row["rate_percent"])
    raise ValueError(f"Missing aggregate row: {analysis}/{level}/{condition}")


def architecture_figure() -> None:
    fig, ax = plt.subplots(figsize=(11.4, 5.4))
    ax.set_xlim(0, 13.4)
    ax.set_ylim(0, 6.2)
    ax.axis("off")

    columns = (0.35, 3.25, 6.35, 9.55)
    widths = (2.2, 2.45, 2.55, 3.1)
    headers = ("User request", "Model responsibility", "Source path", "Final delivery")
    for x, header in zip(columns, headers):
        ax.text(
            x,
            5.72,
            header,
            color=COLORS["ink"],
            fontsize=10,
            fontweight="bold",
            va="bottom",
        )

    rows = (
        (
            "Native",
            "Generate the\npassage words",
            "No external\nsource",
            "Model-generated\ntext",
            COLORS["native"],
        ),
        (
            "Source supplied",
            "Preserve words\nalready in context",
            "Authoritative span\ninside the prompt",
            "Generated\nreproduction",
            COLORS["source"],
        ),
        (
            "Tool mediated",
            "Choose and call\nthe passage tool",
            "Authorized\nget_passage lookup",
            "Retrieved text\nre-rendered by model",
            COLORS["tool"],
        ),
        (
            "Deterministic",
            "Select the\nreference only",
            "Authorized local\nsource lookup",
            "Deterministically\nrendered source text",
            COLORS["deterministic"],
        ),
    )
    y_positions = (4.75, 3.45, 2.15, 0.85)

    for (label, model, source, final, color), y in zip(rows, y_positions):
        cells = (
            (f"Same matched\nquotation request\n\n{label}", color, "white"),
            (model, "#F4F5F6", COLORS["ink"]),
            (source, "#F4F5F6", COLORS["ink"]),
            (final, "#F4F5F6", COLORS["ink"]),
        )
        for idx, ((text, face, text_color), x, width) in enumerate(
            zip(cells, columns, widths)
        ):
            ax.add_patch(
                Rectangle(
                    (x, y - 0.43),
                    width,
                    0.9,
                    facecolor=face,
                    edgecolor=color if idx else color,
                    linewidth=1.2,
                )
            )
            ax.text(
                x + width / 2,
                y + 0.02,
                text,
                ha="center",
                va="center",
                color=text_color,
                fontsize=8.6,
                fontweight="bold" if idx == 0 else "normal",
                linespacing=1.18,
            )
            if idx < 3:
                next_x = columns[idx + 1]
                ax.add_patch(
                    FancyArrowPatch(
                        (x + width + 0.06, y + 0.02),
                        (next_x - 0.08, y + 0.02),
                        arrowstyle="-|>",
                        mutation_scale=10,
                        linewidth=1,
                        color=COLORS["muted"],
                    )
                )

    ax.text(
        0.35,
        0.04,
        "The user request is held fixed. What changes is which component owns "
        "selection, source access, and the final words.",
        color=COLORS["muted"],
        fontsize=8.7,
    )
    fig.savefig(OUTPUT / "fig1_delivery_paths.pdf", metadata=PDF_METADATA)
    plt.close(fig)


def outcome_figure() -> None:
    labels = ("Native", "Source supplied", "Tool mediated", "Deterministic")
    conditions = (
        "native_parametric",
        "source_supplied",
        "tool_mediated",
        "deterministic_rendering",
    )
    final_exact = np.array(
        [aggregate_rate("common_final_output", "overall", value) for value in conditions]
    )
    adherent = np.array(
        [aggregate_rate("primary", "overall", value) for value in conditions]
    )
    colors = (
        COLORS["native"],
        COLORS["source"],
        COLORS["tool"],
        COLORS["deterministic"],
    )

    fig, ax = plt.subplots(figsize=(8.6, 4.5))
    y = np.arange(len(labels))
    height = 0.31
    for index, color in enumerate(colors):
        ax.barh(
            y[index] - height / 2,
            final_exact[index],
            height,
            color=color,
            alpha=0.42,
            edgecolor=color,
            linewidth=0.8,
        )
        ax.barh(
            y[index] + height / 2,
            adherent[index],
            height,
            color=color,
            edgecolor=color,
            linewidth=0.8,
        )
        ax.text(
            final_exact[index] + 1.0,
            y[index] - height / 2,
            f"{final_exact[index]:.2f}",
            va="center",
            fontsize=8.5,
            color=COLORS["ink"],
        )
        ax.text(
            adherent[index] + 1.0,
            y[index] + height / 2,
            f"{adherent[index]:.2f}",
            va="center",
            fontsize=8.5,
            color=COLORS["ink"],
        )

    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 102)
    ax.set_xlabel("Exact quotation rate (%)")
    ax.xaxis.grid(True, color=COLORS["grid"], linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    handles = (
        Rectangle((0, 0), 1, 1, facecolor="#8F969C", alpha=0.42, edgecolor="#555555"),
        Rectangle((0, 0), 1, 1, facecolor="#555555", edgecolor="#555555"),
    )
    ax.legend(
        handles,
        ("Common final-text exactness", "Architecture-adherent exactness"),
        loc="upper center",
        bbox_to_anchor=(0.5, -0.17),
        ncol=2,
        frameon=False,
        fontsize=8.5,
    )
    fig.subplots_adjust(bottom=0.23)
    fig.savefig(OUTPUT / "fig2_condition_outcomes.pdf", metadata=PDF_METADATA)
    plt.close(fig)


def difficulty_figure() -> None:
    rows = ("Native", "Source supplied", "Tool mediated", "Deterministic")
    columns = ("Single verse", "Short passage", "Indirect event", "Long passage")
    conditions = (
        "native_parametric",
        "source_supplied",
        "tool_mediated",
        "deterministic_rendering",
    )
    strata = ("single_verse", "short_passage", "indirect_event", "long_passage")
    values = np.array(
        [
            [aggregate_rate("passage_stratum", stratum, condition) for stratum in strata]
            for condition in conditions
        ]
    )
    cmap = LinearSegmentedColormap.from_list(
        "exactness", ("#F3F4F5", "#BBD5CF", "#23877B")
    )
    fig, ax = plt.subplots(figsize=(8.2, 3.8))
    image = ax.imshow(values, cmap=cmap, vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(np.arange(len(columns)), columns)
    ax.set_yticks(np.arange(len(rows)), rows)
    ax.tick_params(length=0)
    for row in range(values.shape[0]):
        for column in range(values.shape[1]):
            value = values[row, column]
            ax.text(
                column,
                row,
                f"{value:.1f}",
                ha="center",
                va="center",
                color="white" if value >= 66 else COLORS["ink"],
                fontweight="bold",
                fontsize=9,
            )
    ax.set_xticks(np.arange(-0.5, len(columns), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(rows), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="minor", bottom=False, left=False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    cbar = fig.colorbar(image, ax=ax, fraction=0.028, pad=0.025)
    cbar.set_label("Architecture-adherent exactness (%)", rotation=270, labelpad=13)
    cbar.outline.set_visible(False)
    fig.savefig(OUTPUT / "fig3_passage_difficulty.pdf", metadata=PDF_METADATA)
    plt.close(fig)


def main() -> None:
    configure()
    architecture_figure()
    outcome_figure()
    difficulty_figure()
    print(f"Wrote paper figures to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
