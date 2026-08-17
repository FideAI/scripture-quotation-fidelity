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
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "papers/p01-scripture-quotation/paper/figures"
AGGREGATES = (
    ROOT / "papers/p01-scripture-quotation/results/fid056_p01_aggregate_results.csv"
)
TARGET_LEVEL = (
    ROOT / "papers/p01-scripture-quotation/results/fid056_p01_target_level_results.csv"
)
PARSER_REPLAY = (
    ROOT
    / "papers/p01-scripture-quotation/results/fid056_p01_permissive_parser_replay.csv"
)
OUTPUT.mkdir(parents=True, exist_ok=True)

# Validated categorical palette (see dataviz skill references/palette.md).
# "native" is a true neutral gray -- it is the absence-of-source baseline, so a
# low-chroma color is semantically correct rather than a validator workaround.
# The three source-connected conditions use the first three all-pairs-safe
# categorical slots (blue / orange / aqua), which clear every CVD and
# normal-vision separation check together, unlike the prior teal/blue/gray set.
COLORS = {
    "native": "#6b6b68",
    "source": "#1baf7a",
    "tool": "#2a78d6",
    "deterministic": "#eb6834",
    "ink": "#0b0b0b",
    "muted": "#52514e",
    "axis": "#898781",
    "grid": "#e1e0d9",
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


def corrected_deterministic_route_rates() -> dict[str, float]:
    """Per-route exact rate for deterministic rendering after the parser
    correction (Appendix~\\ref{app:parser-audit}), computed from the
    response-level replay so it matches Table~\\ref{tab:model} exactly."""
    counts: dict[str, list[int]] = {}
    with PARSER_REPLAY.open(newline="") as handle:
        for row in csv.DictReader(handle):
            route = row["model_route"]
            exact, total = counts.setdefault(route, [0, 0])
            counts[route][1] = total + 1
            counts[route][0] = exact + int(row["permissive_parser_replay_exact"])
    return {route: 100 * exact / total for route, (exact, total) in counts.items()}


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
        ("1  Select", "Which work, source version,\nand span?", "Wrong passage or boundary"),
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
    fig = plt.figure(figsize=(10.8, 6.35))
    grid = fig.add_gridspec(2, 1, height_ratios=(1.05, 1.55), hspace=0.4)
    chain = fig.add_subplot(grid[0])
    ownership = fig.add_subplot(grid[1])

    # --- Panel (a): four-stage chain, drawn as numbered stations on a rail
    # rather than boxes joined by separate arrow patches, so the chain reads
    # as one continuous mechanism instead of four independent tiles. ---
    chain.set_xlim(0, 12.8)
    chain.set_ylim(0, 2.55)
    chain.axis("off")
    chain.text(
        0.02,
        2.48,
        "(a)  Exact quotation is a four-stage chain",
        fontsize=11,
        fontweight="bold",
        color=COLORS["ink"],
    )
    stages = (
        ("Select", "Work, source version, span", "Wrong passage"),
        ("Access", "Declared source reached", "Bypass or no source"),
        ("Render", "Source words preserved", "Alteration or blending"),
        ("Deliver", "Complete text received", "Truncation or leakage"),
    )
    centers = (1.55, 4.75, 7.95, 11.15)
    rail_y = 1.66
    badge_r = 0.26

    # The rail is drawn first (zorder 1) so the numbered badges sit on top of
    # it at zorder 3, reading as stations along one continuous path.
    chain.plot(
        [centers[0], centers[-1]],
        [rail_y, rail_y],
        color=COLORS["grid"],
        linewidth=3,
        solid_capstyle="round",
        zorder=1,
    )
    for index, (cx, (title, question, failure)) in enumerate(zip(centers, stages)):
        if index < len(stages) - 1:
            chain.add_patch(
                FancyArrowPatch(
                    (cx + badge_r + 0.08, rail_y),
                    (centers[index + 1] - badge_r - 0.14, rail_y),
                    arrowstyle="-|>",
                    mutation_scale=13,
                    linewidth=0,
                    color=COLORS["axis"],
                    zorder=2,
                )
            )
        chain.add_patch(
            Circle(
                (cx, rail_y),
                badge_r,
                facecolor=COLORS["ink"],
                edgecolor="none",
                zorder=3,
            )
        )
        chain.text(
            cx,
            rail_y,
            str(index + 1),
            ha="center",
            va="center",
            fontsize=10.5,
            fontweight="bold",
            color="white",
            zorder=4,
        )
        chain.text(
            cx,
            rail_y - 0.46,
            title,
            ha="center",
            va="top",
            fontsize=10.2,
            fontweight="bold",
            color=COLORS["ink"],
        )
        chain.text(
            cx,
            rail_y - 0.80,
            question,
            ha="center",
            va="top",
            fontsize=8.3,
            color=COLORS["muted"],
        )
        # Failure mode sits directly under its own stage's question line,
        # in reading order, rather than floating above the rail where it
        # had no visual tether to a specific stage.
        chain.text(
            cx,
            rail_y - 1.07,
            f"✗ {failure}",
            ha="center",
            va="top",
            fontsize=7.7,
            color=COLORS["deterministic"],
            style="italic",
        )

    # --- Panel (b): condition-ownership grid, redrawn as rounded pill row
    # headers with a light shared plot background instead of every cell
    # individually boxed, so the eye reads rows and the "who owns this"
    # values rather than a grid of identical borders. ---
    ownership.set_xlim(0, 12.2)
    ownership.set_ylim(0, 4.9)
    ownership.axis("off")
    ownership.text(
        0.02,
        4.78,
        "(b)  The experiment reallocates responsibility",
        fontsize=11,
        fontweight="bold",
        color=COLORS["ink"],
    )
    columns = ("Condition", "Select passage", "Reach source", "Supply exact words")
    x = (0.1, 3.35, 6.30, 9.25)
    widths = (2.9, 2.65, 2.65, 2.75)
    header_y = 4.28
    for xpos, width, title in zip(x, widths, columns):
        ownership.text(
            xpos + width / 2,
            header_y,
            title,
            ha="center",
            va="center",
            fontweight="bold",
            fontsize=9.0,
            color=COLORS["muted"],
        )
    ownership.plot(
        [x[0], x[-1] + widths[-1]],
        [header_y - 0.30, header_y - 0.30],
        color=COLORS["axis"],
        linewidth=0.9,
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
    row_height = 0.86
    row_top = header_y - 0.30
    for row_index, (condition, selection, access, words, color) in enumerate(rows):
        y_center = row_top - row_height * (row_index + 0.5)
        # Zebra-light row background spans the whole row, replacing the
        # per-cell borders of the previous version.
        if row_index % 2 == 1:
            ownership.add_patch(
                Rectangle(
                    (x[0], y_center - row_height / 2),
                    x[-1] + widths[-1] - x[0],
                    row_height,
                    facecolor="#F5F6F7",
                    edgecolor="none",
                    zorder=0,
                )
            )
        # Condition name as a rounded, filled pill -- the one strong color
        # accent in the row, carrying the same categorical hue used
        # everywhere else this condition appears in the paper.
        pill_width = widths[0] - 0.3
        ownership.add_patch(
            FancyBboxPatch(
                (x[0] + 0.15, y_center - 0.24),
                pill_width,
                0.48,
                boxstyle="round,pad=0,rounding_size=0.24",
                facecolor=color,
                edgecolor="none",
                zorder=2,
            )
        )
        ownership.text(
            x[0] + 0.15 + pill_width / 2,
            y_center,
            condition,
            ha="center",
            va="center",
            fontsize=9.2,
            fontweight="bold",
            color="white",
            zorder=3,
        )
        for xpos, width, value in zip(x[1:], widths[1:], (selection, access, words)):
            is_owner_label = value in {"Model", "Renderer"}
            ownership.text(
                xpos + width / 2,
                y_center,
                value,
                ha="center",
                va="center",
                fontsize=8.7,
                color=COLORS["ink"] if is_owner_label else COLORS["muted"],
                fontweight="bold" if is_owner_label else "normal",
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
    height = 0.42
    for index, color in enumerate(colors):
        ax.barh(
            y[index],
            rates[index],
            height,
            color=color,
            edgecolor="none",
            zorder=2,
        )
        ax.text(
            intervals[index, 1] + 1.6,
            y[index],
            f"{rates[index]:.2f}",
            va="center",
            fontsize=8.8,
            color=COLORS["ink"],
            fontweight="bold",
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
    ax.set_xlim(0, 104)
    ax.set_xlabel("Exact quotation rate (%)", color=COLORS["muted"])
    ax.xaxis.grid(True, color=COLORS["grid"], linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(COLORS["axis"])
    ax.tick_params(axis="x", colors=COLORS["muted"])
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
    # Single-hue sequential ramp (blue, light->dark), matching palette.md's
    # sequential default so magnitude reads consistently across the paper.
    cmap = LinearSegmentedColormap.from_list(
        "exactness", ("#cde2fb", "#5598e7", "#184f95")
    )
    fig, ax = plt.subplots(figsize=(8.2, 3.8))
    image = ax.imshow(values, cmap=cmap, vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(np.arange(len(columns)), columns)
    ax.set_yticks(np.arange(len(rows)), rows)
    ax.tick_params(length=0, colors=COLORS["muted"])
    for row in range(values.shape[0]):
        for column in range(values.shape[1]):
            value = values[row, column]
            ax.text(
                column,
                row,
                f"{value:.1f}",
                ha="center",
                va="center",
                color="white" if value >= 60 else COLORS["ink"],
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


def route_condition_figure() -> None:
    """Visualize Table~\\ref{tab:model}: exact delivery for each of the six
    model routes crossed with all four conditions. Same sequential blue ramp
    as the passage-difficulty heatmap so magnitude reads consistently."""
    routes = (
        "Claude Sonnet 5",
        "DeepSeek V4 Pro",
        "Gemini 3.5 Flash",
        "GLM-5.2",
        "GPT-5.6 Sol",
        "Kimi K3",
    )
    route_keys = (
        "Claude_Sonnet_5",
        "DeepSeek_V4_Pro",
        "Gemini_3_5_Flash",
        "GLM_5_2",
        "GPT_5_6_Sol",
        "Kimi_K3",
    )
    replay_route_keys = (
        "anthropic/claude-sonnet-5",
        "deepseek/deepseek-v4-pro",
        "google/gemini-3.5-flash",
        "z-ai/glm-5.2",
        "openai/gpt-5.6-sol",
        "moonshotai/kimi-k3",
    )
    columns = ("Native", "Source supplied", "Tool mediated", "Deterministic")

    deterministic_by_route = corrected_deterministic_route_rates()
    values = np.array(
        [
            [
                aggregate_rate("locked_model_family", key, "native_parametric"),
                aggregate_rate("locked_model_family", key, "source_supplied"),
                aggregate_rate("locked_model_family", key, "tool_mediated"),
                deterministic_by_route[replay_key],
            ]
            for key, replay_key in zip(route_keys, replay_route_keys)
        ]
    )

    cmap = LinearSegmentedColormap.from_list(
        "exactness", ("#cde2fb", "#5598e7", "#184f95")
    )
    fig, ax = plt.subplots(figsize=(7.6, 4.1))
    image = ax.imshow(values, cmap=cmap, vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(np.arange(len(columns)), columns)
    ax.set_yticks(np.arange(len(routes)), routes)
    ax.tick_params(length=0, colors=COLORS["muted"])
    for row in range(values.shape[0]):
        for column in range(values.shape[1]):
            value = values[row, column]
            ax.text(
                column,
                row,
                f"{value:.1f}",
                ha="center",
                va="center",
                color="white" if value >= 60 else COLORS["ink"],
                fontweight="bold",
                fontsize=9,
            )
    ax.set_xticks(np.arange(-0.5, len(columns), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(routes), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="minor", bottom=False, left=False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    cbar = fig.colorbar(image, ax=ax, fraction=0.032, pad=0.03)
    cbar.set_label("Exact delivery (%)", rotation=270, labelpad=13)
    cbar.outline.set_visible(False)
    fig.subplots_adjust(left=0.22)
    fig.savefig(OUTPUT / "fig4_route_condition.pdf", metadata=PDF_METADATA)
    plt.close(fig)


def target_heterogeneity_figure() -> None:
    """Strip plot of the per-target rate distribution behind
    Table~\\ref{tab:target-distribution}: one dot per passage target
    (N=108 each), so the spread Section~5.2 describes in prose is visible
    rather than summarized only by median/IQR/min/max."""
    conditions = (
        ("Native", "native_parametric", COLORS["native"]),
        ("Source supplied", "source_supplied", COLORS["source"]),
        ("Tool mediated", "tool_mediated", COLORS["tool"]),
        ("Deterministic", "deterministic_rendering", COLORS["deterministic"]),
    )
    rates_by_condition: dict[str, list[float]] = {key: [] for _, key, _ in conditions}
    with TARGET_LEVEL.open(newline="") as handle:
        for row in csv.DictReader(handle):
            rates_by_condition[row["condition"]].append(
                100 * float(row["parser_adjusted_rate"])
            )

    rng = np.random.default_rng(5601)
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    row_y = np.arange(len(conditions))
    for y, (label, key, color) in zip(row_y, conditions):
        values = np.array(rates_by_condition[key])
        jitter = rng.uniform(-0.24, 0.24, size=len(values))
        ax.scatter(
            values,
            np.full_like(values, y) + jitter,
            s=34,
            facecolor=color,
            edgecolor="white",
            linewidth=0.7,
            alpha=0.85,
            zorder=3,
        )
        median = float(np.median(values))
        ax.plot(
            [median, median],
            [y - 0.34, y + 0.34],
            color=COLORS["ink"],
            linewidth=2.2,
            zorder=4,
            solid_capstyle="round",
        )
        ax.text(
            median,
            y - 0.46,
            f"median {median:.1f}",
            ha="center",
            va="bottom",
            fontsize=7.8,
            color=COLORS["ink"],
            fontweight="bold",
        )

    ax.set_yticks(row_y, [label for label, _, _ in conditions])
    ax.invert_yaxis()
    ax.set_xlim(-3, 103)
    ax.set_ylim(len(conditions) - 0.55, -0.75)
    ax.set_xlabel("Exact delivery rate for one passage target (%)", color=COLORS["muted"])
    ax.xaxis.grid(True, color=COLORS["grid"], linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(COLORS["axis"])
    ax.tick_params(axis="y", length=0, colors=COLORS["ink"], labelsize=9.5)
    ax.tick_params(axis="x", colors=COLORS["muted"])
    fig.subplots_adjust(left=0.18, bottom=0.17, top=0.96, right=0.97)
    fig.savefig(OUTPUT / "fig6_target_heterogeneity.pdf", metadata=PDF_METADATA)
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
    # Rows spaced 2 units apart (instead of 1) so each track gets its own
    # clear band: a title line above, the track itself, and a caption line
    # below, with no crowding against the neighboring row.
    row_y = (0, 2, 4)
    fig, ax = plt.subplots(figsize=(9.6, 5.0))
    ax.set_xlim(0, 106)
    ax.set_ylim(-1.1, 5.4)
    ax.set_xlabel("Share of all scheduled observations (%)", color=COLORS["muted"])
    ax.set_yticks(row_y, [row[0] for row in rows])
    ax.invert_yaxis()
    ax.xaxis.grid(True, color=COLORS["grid"], linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(COLORS["axis"])
    ax.tick_params(axis="y", length=0, colors=COLORS["ink"], labelsize=10)
    ax.tick_params(axis="x", colors=COLORS["muted"])

    for y, (_, stage_rate, final_rate, stage_label, color) in zip(row_y, rows):
        ax.plot(
            [0, stage_rate],
            [y, y],
            color=color,
            linewidth=7,
            solid_capstyle="butt",
            zorder=2,
        )
        ax.plot(
            [stage_rate, 100],
            [y, y],
            color=COLORS["grid"],
            linewidth=7,
            solid_capstyle="butt",
            zorder=1,
        )
        ax.scatter([stage_rate], [y], s=70, color=color, zorder=3)
        ax.scatter(
            [final_rate],
            [y],
            s=70,
            facecolor="white",
            edgecolor=color,
            linewidth=1.8,
            zorder=4,
        )
        # Caption sits on its own line well below the track; stage-reached
        # and exact-final call-outs sit on their own line well above it, so
        # none of the three text elements per row ever touches another.
        ax.text(
            0,
            y - 0.85,
            stage_label,
            ha="left",
            va="bottom",
            fontsize=8.6,
            color=COLORS["muted"],
        )
        ax.text(
            stage_rate,
            y - 0.35,
            f"{stage_rate:.2f}% stage reached",
            ha="right" if stage_rate > 15 else "left",
            va="bottom",
            fontsize=8.4,
            color=COLORS["ink"],
            fontweight="bold",
        )
        ax.text(
            final_rate,
            y + 0.35,
            f"{final_rate:.2f}% exact final",
            ha="center",
            va="top",
            fontsize=8.4,
            color=COLORS["ink"],
        )

    fig.subplots_adjust(left=0.16, bottom=0.13, top=0.97, right=0.97)
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
    left_offsets = (0.0, -1.5, -6.5, 4.5)

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
            markersize=6,
            markeredgecolor="white",
            markeredgewidth=1.2,
            zorder=3,
        )
        if offset:
            ax.plot(
                [-0.08, 0],
                [first + offset, first],
                color=COLORS["axis"],
                linewidth=0.7,
            )
        # Identity via a colored dot beside the label; label text stays ink so
        # it stays legible regardless of hue (text never wears the data color).
        ax.scatter([-0.115], [first + offset], s=22, color=color, zorder=4)
        ax.text(
            -0.145,
            first + offset,
            f"{label}  {first:.2f}",
            ha="right",
            va="center",
            fontsize=8.2,
            color=COLORS["ink"],
        )
        ax.scatter([1.055], [second], s=22, color=color, zorder=4)
        ax.text(
            1.08,
            second,
            f"{second:.2f}  {label}",
            ha="left",
            va="center",
            fontsize=8.2,
            color=COLORS["ink"],
        )

    ax.set_xlim(-0.85, 1.55)
    ax.set_ylim(0, 106)
    ax.set_xticks((0, 1), ("Explicit reference", "Contextual description"))
    ax.set_ylabel("Exact delivery (%)", color=COLORS["muted"])
    ax.yaxis.grid(True, color=COLORS["grid"], linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(COLORS["axis"])
    ax.tick_params(axis="y", length=0, colors=COLORS["muted"])
    ax.tick_params(axis="x", colors=COLORS["muted"])
    fig.subplots_adjust(left=0.24, right=0.76, bottom=0.17, top=0.96)
    fig.savefig(OUTPUT / "figv5_prompt_family.pdf", metadata=PDF_METADATA)
    plt.close(fig)


def component_funnel_figure() -> None:
    """Small multiples of Table~\\ref{tab:components}: each panel traces one
    condition through its component stages, so the reader sees where
    observations are lost rather than only the two endpoint rates."""
    panels = (
        (
            "Native",
            (("Answered", 98.29), ("Exact text", 25.14), ("Final exact", 25.00)),
            COLORS["native"],
        ),
        (
            "Source supplied",
            (
                ("Answered", 100.00),
                ("Exact text", 93.66),
                ("Method adherence", 100.00),
                ("Final exact", 93.61),
            ),
            COLORS["source"],
        ),
        (
            "Tool mediated",
            (
                ("Answered", 99.81),
                ("Exact text", 82.31),
                ("Method adherence", 84.17),
                ("Final exact", 82.31),
                ("Path-adherent", 80.09),
            ),
            COLORS["tool"],
        ),
        (
            "Deterministic",
            (
                ("Answered", 100.00),
                ("Exact text", 91.25),
                ("Method adherence", 91.34),
                ("Final exact", 91.25),
            ),
            COLORS["deterministic"],
        ),
    )

    fig, axes = plt.subplots(
        1, 4, figsize=(11.2, 3.55), sharey=True, width_ratios=(3, 4, 5, 4)
    )
    fig.subplots_adjust(left=0.06, right=0.985, bottom=0.34, top=0.86, wspace=0.12)

    for ax, (title, stages, color) in zip(axes, panels):
        labels = [label for label, _ in stages]
        values = [value for _, value in stages]
        x = np.arange(len(stages))
        ax.set_title(title, fontsize=9.6, fontweight="bold", color=COLORS["ink"])
        ax.plot(
            x,
            values,
            color=color,
            linewidth=2.0,
            marker="o",
            markersize=7,
            markeredgecolor="white",
            markeredgewidth=1.2,
            zorder=3,
        )
        for xi, value in zip(x, values):
            ax.text(
                xi,
                value + 5.5,
                f"{value:.1f}",
                ha="center",
                va="bottom",
                fontsize=7.8,
                color=COLORS["ink"],
                fontweight="bold",
            )
        ax.set_xticks(x, labels, rotation=32, ha="right", fontsize=7.6)
        ax.set_xlim(-0.4, len(stages) - 0.6)
        ax.set_ylim(0, 112)
        ax.yaxis.grid(True, color=COLORS["grid"], linewidth=0.8, zorder=0)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines["left"].set_visible(ax is axes[0])
        ax.spines["bottom"].set_color(COLORS["axis"])
        ax.tick_params(axis="x", colors=COLORS["muted"], length=0)
        ax.tick_params(axis="y", colors=COLORS["muted"], length=0)

    axes[0].set_ylabel("Rate (%)", color=COLORS["muted"])
    fig.savefig(OUTPUT / "fig5_component_funnel.pdf", metadata=PDF_METADATA)
    plt.close(fig)


def main() -> None:
    configure()
    system_overview_figure()
    outcome_figure()
    difficulty_figure()
    route_condition_figure()
    target_heterogeneity_figure()
    failure_migration_figure()
    prompt_family_figure()
    component_funnel_figure()
    print(f"Wrote paper figures to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
