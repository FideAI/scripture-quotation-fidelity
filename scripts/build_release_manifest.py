#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fide AI
"""Build a deterministic manifest for the public replication package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "papers/p01-scripture-quotation/provenance/release_manifest.json"
PAPER = "papers/p01-scripture-quotation/"

# Shared, repository-level artifacts plus everything scoped to the paper.
# Add a new PAPER-style prefix when a second paper is released.
INCLUDED_PREFIXES = (
    "CITATION.cff",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "LICENSE-CODE",
    "Makefile",
    "NOTICE",
    "README.md",
    "SECURITY.md",
    "docs/",
    "examples/",
    "protocol/",
    "scripts/",
    PAPER + "README.md",
    PAPER + "data/",
    PAPER + "docs/",
    PAPER + "provenance/",
    PAPER + "results/",
    PAPER + "review/",
    PAPER + "paper/figures/",
    PAPER + "paper/main.pdf",
    PAPER + "paper/main.tex",
    PAPER + "paper/references.bib",
)


def included(relative: str) -> bool:
    return any(
        relative == prefix or relative.startswith(prefix)
        for prefix in INCLUDED_PREFIXES
    )


def main() -> None:
    records = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path == OUTPUT:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if not included(relative):
            continue
        payload = path.read_bytes()
        records.append(
            {
                "path": relative,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    manifest = {
        "schema_version": 1,
        "study_id": "FID-056-P01",
        "artifact_scope": "public_replication_package",
        "hash_algorithm": "sha256",
        "files": records,
    }
    OUTPUT.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(records)} files.")


if __name__ == "__main__":
    main()
