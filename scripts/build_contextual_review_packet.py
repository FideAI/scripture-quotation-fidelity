# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fide AI
"""Build the blinded reviewer packet for the contextual-description validation.

The packet presents all twenty contextual descriptions in a deterministically
shuffled order with references, passage strata, and revision history withheld.
The reviewer never sees which descriptions were revised during instrument
development, so the six revised items cannot be treated differently from the
fourteen originals.

Ordering is seeded so the packet is reproducible from the public target file,
but it does not follow canonical biblical order, which would otherwise let a
reviewer infer answers positionally.

Usage:
  uv run --script scripts/build_contextual_review_packet.py
"""

from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers/p01-scripture-quotation"
TARGETS = PAPER / "data" / "fid056_p01_targets.jsonl"
PACKET = PAPER / "review" / "blinded_contextual_descriptions.md"
RESPONSE = PAPER / "review" / "reviewer_response_template.csv"

SHUFFLE_SEED = 5601  # same seed family as the analysis bootstrap

HEADER = """# Contextual Description Review — Blinded Packet

You are being asked to validate a research instrument, not to evaluate an AI
system. No model output appears in this packet.

## What each item is

Each item below is a description of a biblical passage written **without**
naming the book, chapter, or verse, and written to avoid distinctive wording
from any particular English translation. In the study, these descriptions were
given to AI systems to test whether a system can identify which passage is
meant before it attempts to quote it.

## What we are asking

For each item, working only from the description:

1. **Reference** — name the passage you believe is intended (book, chapter,
   verses). If you believe the description points to a range, give the range
   you would consider correct.
2. **Ambiguity** — is there more than one passage a competent reader could
   defensibly land on? If yes, name the alternatives. This is the single most
   valuable judgment you can give us: a description that admits two defensible
   answers is a defect in our instrument, and we would rather find it than
   score around it.
3. **Confidence** — high / medium / low.
4. **Comment** — optional. Note anything misleading, anachronistic,
   theologically loaded, or dependent on a particular translation tradition.

Please do not consult the study's published materials, and please answer from
your own knowledge and ordinary reference tools rather than by querying an AI
assistant. Items are presented in a scrambled order; the numbering carries no
information.

## How your answers will be used

We will report exact agreement with our expected reference, and we will report
every disagreement and every ambiguity flag as you wrote it. We will not revise
descriptions and re-run the comparison in order to improve the agreement
figure. If your review shows that descriptions were ambiguous, that is a
finding about our instrument and will be published as one.

---

"""


def main() -> None:
    targets = [json.loads(line) for line in TARGETS.read_text().splitlines() if line.strip()]

    order = list(range(len(targets)))
    random.Random(SHUFFLE_SEED).shuffle(order)

    PACKET.parent.mkdir(exist_ok=True)

    lines = [HEADER]
    for position, index in enumerate(order, start=1):
        lines.append(f"### Item {position:02d}\n")
        lines.append(f"> {targets[index]['indirect_description']}\n")
        lines.append("- Reference: \n- Ambiguous (yes/no, alternatives): \n"
                     "- Confidence (high/medium/low): \n- Comment: \n")
    PACKET.write_text("\n".join(lines))

    rows = ["item,reference,ambiguous,alternatives,confidence,comment"]
    rows += [f"{position:02d},,,,," for position in range(1, len(order) + 1)]
    RESPONSE.write_text("\n".join(rows) + "\n")

    # Mapping from packet position back to the expected reference. Kept out of
    # the packet itself; used only by the scoring script after responses are in.
    key = {
        f"{position:02d}": {
            "review_id": targets[index]["review_id"],
            "expected_reference": targets[index]["reference"],
            "passage_stratum": targets[index]["passage_stratum"],
        }
        for position, index in enumerate(order, start=1)
    }
    (PAPER / "review" / "packet_key.json").write_text(
        json.dumps({"shuffle_seed": SHUFFLE_SEED, "items": key}, indent=2) + "\n"
    )

    print(f"Wrote {PACKET.relative_to(ROOT)} ({len(order)} items), "
          f"{RESPONSE.relative_to(ROOT)}, and review/packet_key.json")


if __name__ == "__main__":
    main()
