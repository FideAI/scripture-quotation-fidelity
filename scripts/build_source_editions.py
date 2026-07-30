# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fide AI
"""Emit the release-safe source-edition disclosure for FID-056 Paper 01.

Reads the hash-locked private source registry and writes
provenance/source_editions.json. The registry is hash-only: it carries edition
identity, provider routing, rights basis, and per-target normalized-text
SHA-256 digests, but no passage text. Only digests cross into the public
package, so restricted editions can be disclosed as excluded without releasing
their wording.

The input file is identified by the digest recorded in the prospective lock
(artifact_sha256.source_registry). The script refuses to run against any other
file, so the disclosure cannot silently drift from what was locked before
confirmatory execution.

Usage:
  uv run --script scripts/build_source_editions.py --registry <path-to-registry.yaml>
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "papers/p01-scripture-quotation" / "provenance" / "fid056_p01_prospective_lock.json"
OUTPUT_PATH = ROOT / "papers/p01-scripture-quotation" / "provenance" / "source_editions.json"

# Editions that carried the four-condition comparison in the primary phase.
EXECUTED = ("BSB", "WEBU", "LSV")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--registry",
        required=True,
        type=Path,
        help="Path to the hash-locked private source registry YAML.",
    )
    args = parser.parse_args()

    lock = json.loads(LOCK_PATH.read_text())
    expected = lock["artifact_sha256"]["source_registry"]
    actual = sha256_file(args.registry)
    if actual != expected:
        raise SystemExit(
            f"Registry digest mismatch.\n  expected {expected}\n  actual   {actual}\n"
            "This file is not the registry fixed by the prospective lock."
        )

    registry = yaml.safe_load(args.registry.read_text())

    editions = []
    for source in registry["sources"]:
        executed = source["translation_id"] in EXECUTED
        entry = {
            "translation_id": source["translation_id"],
            "name": source["name"],
            "edition": source["edition"],
            "provider": source["provider"],
            "provider_source_id": source["provider_source_id"],
            "rights_basis": source["rights_basis"],
            "public_text_release": source["public_text_release"],
            "execution_status": source["execution_status"],
            "in_primary_phase": executed,
            "normalization_version": source["normalization_version"],
            "verification_status": source["verification_status"],
            "passage_digests": [
                {
                    "target_id": fixture["target_id"],
                    "reference": fixture["reference"],
                    "normalized_text_sha256": fixture["text_sha256"],
                    "verse_count": fixture["verse_count"],
                    "word_count": fixture["word_count"],
                }
                for fixture in source.get("fixtures") or []
            ],
        }
        editions.append(entry)

    document = {
        "schema_version": "fid056_p01_source_editions_v1",
        "purpose": (
            "Release-safe disclosure of the source-of-record editions used as "
            "ground truth. Digests are over normalized passage text; no passage "
            "text is included."
        ),
        "derived_from": {
            "artifact": "source_registry",
            "sha256": actual,
            "matches_prospective_lock": True,
            "lock_id": lock["lock_id"],
            "locked_at_utc": lock["locked_at_utc"],
        },
        "registry_id": registry["registry_id"],
        "registry_schema_version": registry["schema_version"],
        "verified_at_utc": str(registry["verified_at"]),
        "verification_method": registry["verification_method"],
        "normalization_note": (
            "Digests are computed over whitespace-collapsed UTF-8 text. A "
            "replicator can hash their own normalized copy of a passage and "
            "compare against these values to confirm they hold the same "
            "edition text, without either party transmitting the text."
        ),
        "primary_phase_editions": list(EXECUTED),
        "excluded_editions_note": (
            "Editions marked blocked_pending_ai_use_authorization were present "
            "in the locked registry but excluded from the primary phase. They "
            "require separate source and source-to-model authorization and "
            "prospective specification."
        ),
        "editions": editions,
    }

    OUTPUT_PATH.write_text(json.dumps(document, indent=2, sort_keys=False) + "\n")
    executed_count = sum(1 for e in editions if e["in_primary_phase"])
    print(
        f"Wrote {OUTPUT_PATH.relative_to(ROOT)}: {len(editions)} editions "
        f"({executed_count} in primary phase), registry digest verified against lock."
    )


if __name__ == "__main__":
    main()
