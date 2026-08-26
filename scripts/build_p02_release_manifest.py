#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Build the deterministic Paper 02 release manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER_ROOT = ROOT / "papers/p02-source-delegation"
MANIFEST = PAPER_ROOT / "provenance/release_manifest.json"
INVENTORY = PAPER_ROOT / "provenance/release_inventory.txt"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    intended = {
        line.strip()
        for line in INVENTORY.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }
    public_symlinks = {
        str(path.relative_to(PAPER_ROOT))
        for path in PAPER_ROOT.rglob("*")
        if path.is_symlink()
    }
    if public_symlinks:
        raise ValueError(
            f"Paper 02 release package may not contain symlinks: {sorted(public_symlinks)}"
        )
    actual_public_files = {
        str(path.relative_to(PAPER_ROOT))
        for path in PAPER_ROOT.rglob("*")
        if path.is_file() and path != MANIFEST
    }
    intended_public_files = {path for path in intended if not path.startswith("../")}
    if actual_public_files != intended_public_files:
        raise ValueError(
            "Release inventory mismatch; "
            f"missing={sorted(intended_public_files - actual_public_files)}, "
            f"unexpected={sorted(actual_public_files - intended_public_files)}"
        )
    artifacts = {}
    for relative in sorted(intended):
        inventory_path = PAPER_ROOT / relative
        if inventory_path.is_symlink():
            raise ValueError(f"Release inventory may not contain symlinks: {relative}")
        path = inventory_path.resolve()
        try:
            path.relative_to(ROOT)
        except ValueError as exc:
            raise ValueError(
                f"Release inventory path escapes the repository: {relative}"
            ) from exc
        if not path.is_file():
            raise ValueError(f"Missing intended release artifact: {relative}")
        artifacts[relative] = digest(path)
    payload = {
        "schema_version": "fid056_p02_release_manifest_v1",
        "study_id": "FID-056-P02",
        "status": "public_release_candidate_pending_final_approval",
        "artifacts": artifacts,
        "excluded": [
            "raw model outputs",
            "provider response identifiers",
            "credentials",
            "source passage text",
            "private execution code",
            "local filesystem paths",
            "calibration traces",
        ],
    }
    MANIFEST.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"Recorded {len(artifacts)} Paper 02 release artifacts")


if __name__ == "__main__":
    main()
