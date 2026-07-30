# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fide AI
"""Score a returned contextual-description review against the expected panel.

Scoring rules are fixed here before any reviewer response is received. The
script reports three quantities and does not collapse them into a single
figure:

  exact agreement    reviewer's reference matches the expected reference
  span disagreement  same passage identified, different verse boundaries
  identification     different passage identified
  disagreement

Ambiguity flags are reported separately and are never treated as failures. A
description the reviewer marks ambiguous is a finding about the instrument
whether or not the reviewer also guessed the expected reference.

Usage:
  uv run --script scripts/score_contextual_review.py --responses review/<file>.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers/p01-scripture-quotation"
KEY = PAPER / "review" / "packet_key.json"

BOOK_CHAPTER = re.compile(r"^\s*([1-3]?\s*[A-Za-z]+)\s*(\d+)")


def normalize(reference: str) -> str:
    return " ".join(reference.replace("--", "-").replace("–", "-").split()).lower()


def book_chapter(reference: str) -> str | None:
    match = BOOK_CHAPTER.match(reference.strip())
    if not match:
        return None
    return f"{' '.join(match.group(1).split()).lower()} {match.group(2)}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", required=True, type=Path)
    args = parser.parse_args()

    key = json.loads(KEY.read_text())["items"]

    exact = 0
    span_only = 0
    identification = 0
    ambiguous = []
    disagreements = []
    scored = 0

    with args.responses.open() as handle:
        for row in csv.DictReader(handle):
            item = row["item"].strip().zfill(2)
            given = (row.get("reference") or "").strip()
            if not given:
                continue
            scored += 1
            expected = key[item]["expected_reference"]

            if normalize(given) == normalize(expected):
                exact += 1
            elif book_chapter(given) and book_chapter(given) == book_chapter(expected):
                span_only += 1
                disagreements.append((item, expected, given, "span"))
            else:
                identification += 1
                disagreements.append((item, expected, given, "identification"))

            if (row.get("ambiguous") or "").strip().lower().startswith("y"):
                ambiguous.append(
                    (item, expected, (row.get("alternatives") or "").strip())
                )

    if not scored:
        raise SystemExit("No completed rows found in the response file.")

    print(f"Scored {scored} of {len(key)} items\n")
    print(f"  exact agreement            {exact:2d}  ({exact / scored:.1%})")
    print(f"  span disagreement          {span_only:2d}  ({span_only / scored:.1%})")
    print(f"  identification disagreement {identification:2d}  ({identification / scored:.1%})")
    print(f"  flagged ambiguous          {len(ambiguous):2d}  ({len(ambiguous) / scored:.1%})")

    if disagreements:
        print("\nDisagreements (report all of these verbatim):")
        for item, expected, given, kind in disagreements:
            print(f"  item {item}  expected {expected!r}  reviewer {given!r}  [{kind}]")

    if ambiguous:
        print("\nAmbiguity flags (instrument findings, not failures):")
        for item, expected, alternatives in ambiguous:
            print(f"  item {item}  expected {expected!r}  alternatives: {alternatives!r}")


if __name__ == "__main__":
    main()
