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
RELEASE_DECISION = (
    ROOT / PAPER / "provenance/release_decision_summary.json"
)

# Shared repository artifacts plus all Paper 01 artifacts. Later papers use
# paper-scoped release inventories and manifests.
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
    PAPER,
)

TRANSIENT_PAPER_SUFFIXES = (
    ".aux",
    ".bbl",
    ".blg",
    ".fdb_latexmk",
    ".fls",
    ".log",
    ".out",
    ".synctex.gz",
)
TRANSIENT_PATH_PARTS = {
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}
TRANSIENT_FILE_SUFFIXES = (".pyc", ".pyo")


def included(relative: str) -> bool:
    path = Path(relative)
    paper_02_tool = (
        relative.startswith("scripts/") and "p02" in path.name.lower()
    )
    selected = any(
        relative == prefix or relative.startswith(prefix)
        for prefix in INCLUDED_PREFIXES
    )
    transient = (
        any(part in TRANSIENT_PATH_PARTS for part in path.parts)
        or relative.endswith(TRANSIENT_PAPER_SUFFIXES)
        or relative.endswith(TRANSIENT_FILE_SUFFIXES)
    )
    return selected and not transient and not paper_02_tool


def rights_classification(relative: str) -> str:
    if relative.startswith("scripts/"):
        return "Apache-2.0"
    if relative.endswith("/acl_natbib.bst"):
        return "LPPL-1.0-or-later"
    return "CC-BY-4.0"


def evidence_source(relative: str) -> str:
    if relative.endswith("fid056_p01_deidentified_trials.csv.gz"):
        return "deidentified export from the sealed FID-056-P01 confirmatory archive"
    if "permissive_parser_replay" in relative:
        return "deidentified replay of saved deterministic-rendering outputs"
    if relative.startswith(PAPER + "results/"):
        return "analysis of the released FID-056-P01 derived-score dataset"
    if relative.startswith(PAPER + "provenance/"):
        return "reviewed FID-056-P01 prospective-lock and release records"
    if relative.startswith(PAPER + "review/"):
        return "release-safe FID-056-P01 review materials"
    if relative.startswith(PAPER + "paper/"):
        return "FID-056-P01 manuscript source and generated publication artifacts"
    if relative.startswith(PAPER + "data/"):
        return "release-safe FID-056-P01 data export"
    if relative.startswith("scripts/"):
        return "public replication and release tooling"
    if relative.startswith(("protocol/", "examples/")):
        return "public FID-056 protocol and example materials"
    return "public repository governance and documentation"


def verification_mode(relative: str) -> str:
    if relative.endswith("fid056_p01_deidentified_trials.csv.gz"):
        return "schema, row-count, uniqueness, factor-level, and headline reconciliation"
    if "permissive_parser_replay" in relative:
        return "row-level ID and locked-versus-corrected outcome reconciliation"
    if relative.startswith(PAPER + "results/"):
        return "regenerated from released derived scores and compared byte-for-byte"
    if relative.startswith(PAPER + "paper/figures/"):
        return "regenerated from released results and visually inspected"
    if relative.endswith("/paper/main.pdf"):
        return "source compilation, visual inspection, and SHA-256 digest"
    if relative.endswith("/paper/main.tex"):
        return "source compilation and SHA-256 digest"
    if relative.endswith("source_editions.json"):
        return "schema, source-registry provenance, and SHA-256 digest"
    if relative.endswith("fid056_p01_prospective_lock.json"):
        return "prospective-lock identity and SHA-256 digest"
    if relative.endswith("release_decision_summary.json"):
        return "release-decision schema and scope validation"
    return "SHA-256 digest"


def main() -> None:
    release_decision = json.loads(RELEASE_DECISION.read_text())
    decision_reference = release_decision["decision_id"]
    records = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path == OUTPUT:
            continue
        if path.is_symlink():
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
                "rights_classification": rights_classification(relative),
                "evidence_source": evidence_source(relative),
                "verification_mode": verification_mode(relative),
                "release_decision_reference": decision_reference,
            }
        )
    manifest = {
        "schema_version": 2,
        "research_program_id": "FID-056",
        "paper_id": "FID-056-P01",
        "study_id": "FID-056-P01",
        "artifact_scope": "public_replication_package",
        "hash_algorithm": "sha256",
        "release_decision": {
            "decision_id": decision_reference,
            "decision_date": release_decision["decision_date"],
            "decision_authority": release_decision["decision_authority"],
            "human_review": release_decision["human_review"],
            "status": release_decision["status"],
            "summary_path": RELEASE_DECISION.relative_to(ROOT).as_posix(),
        },
        "files": records,
    }
    OUTPUT.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(records)} files.")


if __name__ == "__main__":
    main()
