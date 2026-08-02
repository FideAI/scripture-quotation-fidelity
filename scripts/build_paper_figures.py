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
from math import sqrt
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "papers/p01-scripture-quotation/paper/figures"
AGGREGATES = (
    ROOT / "papers/p01-scripture-quotation/results/fid056_p01_aggregate_results.csv"
)
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


def aggregate_count(analysis: str, level: str, condition: str) -> tuple[int, int]:
    with AGGREGATES.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if (
                row["analysis"] == analysis
                and row["level"] == level
                and row["condition"] == condition
            ):
                return int(row["exact"]), int(row["n"])
    raise ValueError(f"Missing aggregate row: {analysis}/{level}/{condition}")


def wilson_interval(
    exact: int, total: int, z: float = 1.959963984540054
) -> tuple[float, float]:
    proportion = exact / total
    denominator = 1 + z**2 / total
    center = (proportion + z**2 / (2 * total)) / denominator
    margin = (
        z
        * sqrt(proportion * (1 - proportion) / total + z**2 / (4 * total**2))
        / denominator
    )
    return 100 * (center - margin), 100 * (center + margin)


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
                    edgecolor=color,
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


def source_delivery_chain_figure() -> None:
    """Show the four necessary stages before introducing the formal notation."""
    fig, ax = plt.subplots(figsize=(10.8, 2.55))
    ax.set_xlim(0, 12.8)
    ax.set_ylim(0, 2.55)
    ax.axis("off")

    stages = (
        ("1  Select", "Which work, edition,\nand span?", "Wrong passage or boundary"),
        (
            "2  Access",
            "Was the declared source\nactually reached?",
            "Bypass or unavailable source",
        ),
        (
            "3  Render",
            "Were the source words\npreserved exactly?",
            "Alteration or blending",
        ),
        (
            "4  Deliver",
            "Did the user receive the\ncomplete text intact?",
            "Truncation or wrapper leakage",
        ),
    )
    x_positions = (0.2, 3.4, 6.6, 9.8)
    box_width = 2.65
    for index, ((title, question, failure), x) in enumerate(zip(stages, x_positions)):
        ax.add_patch(
            Rectangle(
                (x, 0.72),
                box_width,
                1.42,
                facecolor="#F5F6F7",
                edgecolor=COLORS["ink"],
                linewidth=1.0,
            )
        )
        ax.text(x + 0.16, 1.93, title, fontsize=10, fontweight="bold", va="top")
        ax.text(x + 0.16, 1.56, question, fontsize=8.6, va="top", linespacing=1.2)
        ax.text(
            x + 0.16,
            0.91,
            failure,
            fontsize=7.6,
            color=COLORS["deterministic"],
            va="bottom",
        )
        if index < len(stages) - 1:
            ax.add_patch(
                FancyArrowPatch(
                    (x + box_width + 0.06, 1.43),
                    (x_positions[index + 1] - 0.08, 1.43),
                    arrowstyle="-|>",
                    mutation_scale=10,
                    linewidth=1.0,
                    color=COLORS["muted"],
                )
            )

    ax.text(
        0.2,
        0.28,
        "Exact quotation succeeds only when all four stages succeed.",
        color=COLORS["muted"],
        fontsize=8.8,
    )
    fig.savefig(OUTPUT / "figv1_source_delivery_chain.pdf", metadata=PDF_METADATA)
    plt.close(fig)


def architecture_ownership_figure() -> None:
    """Compare the responsibility left to the model in each condition."""
    fig, ax = plt.subplots(figsize=(10.8, 4.45))
    ax.set_xlim(0, 12.2)
    ax.set_ylim(0, 5.15)
    ax.axis("off")

    columns = ("Condition", "Select passage", "Reach source", "Supply exact words")
    x = (0.15, 3.35, 6.25, 9.15)
    widths = (2.75, 2.45, 2.45, 2.85)
    for xpos, width, title in zip(x, widths, columns):
        ax.text(
            xpos + width / 2, 4.77, title, ha="center", fontweight="bold", fontsize=9.2
        )

    rows = (
        ("Native", "Model", "None", "Model", COLORS["native"]),
        ("Source supplied", "Given", "Given", "Model", COLORS["source"]),
        ("Tool mediated", "Model", "Model calls tool", "Model", COLORS["tool"]),
        (
            "Deterministic",
            "Model",
            "Renderer lookup",
            "Renderer",
            COLORS["deterministic"],
        ),
    )
    y_positions = (3.85, 2.85, 1.85, 0.85)
    for (condition, selection, access, words, color), ypos in zip(rows, y_positions):
        values = (condition, selection, access, words)
        for index, (xpos, width, value) in enumerate(zip(x, widths, values)):
            face = color if index == 0 else "#F5F6F7"
            text_color = "white" if index == 0 else COLORS["ink"]
            ax.add_patch(
                Rectangle(
                    (xpos, ypos - 0.37),
                    width,
                    0.74,
                    facecolor=face,
                    edgecolor=color,
                    linewidth=1.05,
                )
            )
            ax.text(
                xpos + width / 2,
                ypos,
                value,
                ha="center",
                va="center",
                fontsize=8.6,
                color=text_color,
                fontweight="bold"
                if index == 0 or value in {"Model", "Renderer"}
                else "normal",
            )

    ax.text(
        0.15,
        0.19,
        "The matched user request is unchanged; the experiment reallocates responsibility for selection, access, and the words shown.",
        color=COLORS["muted"],
        fontsize=8.5,
    )
    fig.savefig(OUTPUT / "figv2_architecture_ownership.pdf", metadata=PDF_METADATA)
    plt.close(fig)


def system_overview_figure() -> None:
    """Combine the source-delivery chain and condition ownership in one figure."""
    fig = plt.figure(figsize=(10.8, 5.85))
    grid = fig.add_gridspec(2, 1, height_ratios=(1.0, 1.55), hspace=0.34)
    chain = fig.add_subplot(grid[0])
    ownership = fig.add_subplot(grid[1])

    chain.set_xlim(0, 12.8)
    chain.set_ylim(0, 2.4)
    chain.axis("off")
    chain.text(
        0.05,
        2.29,
        "(a)  Exact quotation is a four-stage chain",
        fontsize=10,
        fontweight="bold",
    )
    stages = (
        ("1  Select", "Work, edition, span", "Wrong passage"),
        ("2  Access", "Declared source reached", "Bypass or no source"),
        ("3  Render", "Source words preserved", "Alteration or blending"),
        ("4  Deliver", "Complete text received", "Truncation or leakage"),
    )
    x_positions = (0.1, 3.32, 6.54, 9.76)
    box_width = 2.7
    for index, ((title, question, failure), x) in enumerate(zip(stages, x_positions)):
        chain.add_patch(
            Rectangle(
                (x, 0.42),
                box_width,
                1.35,
                facecolor="#F5F6F7",
                edgecolor=COLORS["ink"],
                linewidth=1.0,
            )
        )
        chain.text(x + 0.15, 1.57, title, fontsize=9.3, fontweight="bold", va="top")
        chain.text(x + 0.15, 1.19, question, fontsize=8.1, va="top")
        chain.text(
            x + 0.15,
            0.61,
            failure,
            fontsize=7.3,
            color=COLORS["deterministic"],
            va="bottom",
        )
        if index < len(stages) - 1:
            chain.add_patch(
                FancyArrowPatch(
                    (x + box_width + 0.06, 1.10),
                    (x_positions[index + 1] - 0.08, 1.10),
                    arrowstyle="-|>",
                    mutation_scale=10,
                    linewidth=1.0,
                    color=COLORS["muted"],
                )
            )

    ownership.set_xlim(0, 12.2)
    ownership.set_ylim(0, 4.75)
    ownership.axis("off")
    ownership.text(
        0.05,
        4.59,
        "(b)  The experiment reallocates responsibility",
        fontsize=10,
        fontweight="bold",
    )
    columns = ("Condition", "Select passage", "Reach source", "Supply exact words")
    x = (0.1, 3.3, 6.2, 9.1)
    widths = (2.75, 2.45, 2.45, 2.85)
    for xpos, width, title in zip(x, widths, columns):
        ownership.text(
            xpos + width / 2, 4.16, title, ha="center", fontweight="bold", fontsize=8.8
        )

    rows = (
        ("Native", "Model", "None", "Model", COLORS["native"]),
        ("Source supplied", "Given", "Given", "Model", COLORS["source"]),
        ("Tool mediated", "Model", "Model calls tool", "Model", COLORS["tool"]),
        (
            "Deterministic",
            "Model",
            "Renderer lookup",
            "Renderer",
            COLORS["deterministic"],
        ),
    )
    y_positions = (3.48, 2.62, 1.76, 0.90)
    for (condition, selection, access, words, color), ypos in zip(rows, y_positions):
        values = (condition, selection, access, words)
        for index, (xpos, width, value) in enumerate(zip(x, widths, values)):
            face = color if index == 0 else "#F5F6F7"
            text_color = "white" if index == 0 else COLORS["ink"]
            ownership.add_patch(
                Rectangle(
                    (xpos, ypos - 0.31),
                    width,
                    0.62,
                    facecolor=face,
                    edgecolor=color,
                    linewidth=1.0,
                )
            )
            ownership.text(
                xpos + width / 2,
                ypos,
                value,
                ha="center",
                va="center",
                fontsize=8.1,
                color=text_color,
                fontweight="bold"
                if index == 0 or value in {"Model", "Renderer"}
                else "normal",
            )

    fig.savefig(OUTPUT / "figv1_system_overview.pdf", metadata=PDF_METADATA)
    plt.close(fig)


def outcome_figure() -> None:
    labels = ("Native", "Source supplied", "Tool mediated", "Deterministic")
    conditions = (
        "native_parametric",
        "source_supplied",
        "tool_mediated",
        "deterministic_rendering",
    )
    rates = np.array(
        [aggregate_rate("parser_adjusted", "overall", value) for value in conditions]
    )
    intervals = np.array(
        [
            wilson_interval(*aggregate_count("parser_adjusted", "overall", value))
            for value in conditions
        ]
    )
    colors = (
        COLORS["native"],
        COLORS["source"],
        COLORS["tool"],
        COLORS["deterministic"],
    )

    fig, ax = plt.subplots(figsize=(8.6, 4.5))
    y = np.arange(len(labels))
    height = 0.58
    for index, color in enumerate(colors):
        ax.barh(
            y[index],
            rates[index],
            height,
            color=color,
            edgecolor=color,
            linewidth=0.8,
        )
        ax.text(
            intervals[index, 1] + 0.8,
            y[index],
            f"{rates[index]:.2f}",
            va="center",
            fontsize=8.5,
            color=COLORS["ink"],
        )
    ax.errorbar(
        rates,
        y,
        xerr=np.vstack((rates - intervals[:, 0], intervals[:, 1] - rates)),
        fmt="none",
        ecolor=COLORS["ink"],
        elinewidth=1.0,
        capsize=3,
        capthick=1.0,
        zorder=4,
    )

    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 102)
    ax.set_xlabel("Exact quotation rate (%)")
    ax.xaxis.grid(True, color=COLORS["grid"], linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    fig.subplots_adjust(bottom=0.16)
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
            [
                aggregate_rate("parser_adjusted", stratum, condition)
                for stratum in strata
            ]
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
    cbar.set_label("Exact delivery (%)", rotation=270, labelpad=13)
    cbar.outline.set_visible(False)
    fig.savefig(OUTPUT / "fig3_passage_difficulty.pdf", metadata=PDF_METADATA)
    plt.close(fig)


def failure_migration_figure() -> None:
    """Show where observations fall away in each source-connected path."""
    rows = (
        (
            "Source supplied",
            100.00,
            93.61,
            "exact text already present",
            COLORS["source"],
        ),
        ("Tool mediated", 84.17, 80.09, "requested span retrieved", COLORS["tool"]),
        (
            "Deterministic",
            91.34,
            91.25,
            "correct reference handed off",
            COLORS["deterministic"],
        ),
    )
    fig, ax = plt.subplots(figsize=(9.4, 3.75))
    ax.set_xlim(0, 105)
    ax.set_ylim(-0.7, 2.9)
    ax.set_xlabel("Share of all scheduled observations (%)")
    ax.set_yticks(range(3), [row[0] for row in rows])
    ax.invert_yaxis()
    ax.xaxis.grid(True, color=COLORS["grid"], linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)

    for index, (_, stage_rate, final_rate, stage_label, color) in enumerate(rows):
        ax.plot(
            [0, stage_rate],
            [index, index],
            color=color,
            linewidth=8,
            solid_capstyle="butt",
        )
        ax.plot(
            [stage_rate, 100],
            [index, index],
            color="#E3E5E7",
            linewidth=8,
            solid_capstyle="butt",
        )
        ax.scatter([stage_rate], [index], s=58, color=color, zorder=3)
        ax.scatter(
            [final_rate],
            [index],
            s=58,
            facecolor="white",
            edgecolor=color,
            linewidth=1.6,
            zorder=4,
        )
        ax.text(
            stage_rate,
            index - 0.21,
            f"{stage_rate:.2f}% stage reached",
            ha="right",
            va="bottom",
            fontsize=7.6,
            color=color,
        )
        ax.text(
            final_rate,
            index + 0.23,
            f"{final_rate:.2f}% exact final",
            ha="left",
            va="top",
            fontsize=7.6,
            color=COLORS["ink"],
        )
        ax.text(
            1.0,
            index + 0.23,
            stage_label,
            ha="left",
            va="top",
            fontsize=7.2,
            color=COLORS["muted"],
        )

    fig.subplots_adjust(left=0.18, bottom=0.2, top=0.94)
    fig.savefig(OUTPUT / "figv4_failure_migration.pdf", metadata=PDF_METADATA)
    plt.close(fig)


def prompt_family_figure() -> None:
    """Make the explicit-to-contextual selection burden visually apparent."""
    labels = ("Native", "Source supplied", "Tool mediated", "Deterministic")
    explicit = np.array((27.41, 93.52, 90.19, 99.91))
    contextual = np.array((22.59, 93.70, 70.00, 82.59))
    colors = (
        COLORS["native"],
        COLORS["source"],
        COLORS["tool"],
        COLORS["deterministic"],
    )
    left_offsets = (0.0, 0.5, -2.8, 2.6)

    fig, ax = plt.subplots(figsize=(7.7, 4.3))
    for label, first, second, color, offset in zip(
        labels, explicit, contextual, colors, left_offsets
    ):
        ax.plot(
            [0, 1],
            [first, second],
            color=color,
            linewidth=2.0,
            marker="o",
            markersize=5.5,
        )
        if offset:
            ax.plot([-0.08, 0], [first + offset, first], color=color, linewidth=0.7)
        ax.text(
            -0.10,
            first + offset,
            f"{label}  {first:.2f}",
            ha="right",
            va="center",
            fontsize=8.2,
            color=color,
        )
        ax.text(
            1.04,
            second,
            f"{second:.2f}  {label}",
            ha="left",
            va="center",
            fontsize=8.2,
            color=color,
        )

    ax.set_xlim(-0.72, 1.42)
    ax.set_ylim(0, 106)
    ax.set_xticks((0, 1), ("Explicit reference", "Contextual description"))
    ax.set_ylabel("Exact delivery (%)")
    ax.yaxis.grid(True, color=COLORS["grid"], linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    fig.subplots_adjust(left=0.20, right=0.77, bottom=0.17, top=0.96)
    fig.savefig(OUTPUT / "figv5_prompt_family.pdf", metadata=PDF_METADATA)
    plt.close(fig)


def main() -> None:
    configure()
    system_overview_figure()
    outcome_figure()
    difficulty_figure()
    failure_migration_figure()
    prompt_family_figure()
    print(f"Wrote paper figures to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
