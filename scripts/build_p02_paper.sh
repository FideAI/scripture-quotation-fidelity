#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
set -euo pipefail

export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-1786492800}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PAPER_DIR="$ROOT_DIR/papers/p02-source-delegation/paper"
PAPER_SOURCE="${1:-main.tex}"

if [[ "$PAPER_SOURCE" != "$(basename "$PAPER_SOURCE")" || "$PAPER_SOURCE" != *.tex ]]; then
  echo "Paper source must be a .tex filename in $PAPER_DIR" >&2
  exit 2
fi

if [[ -n "${TECTONIC:-}" && -x "$TECTONIC" ]]; then
  TECTONIC_BIN="$TECTONIC"
elif command -v tectonic >/dev/null 2>&1; then
  TECTONIC_BIN="$(command -v tectonic)"
elif [[ -x /opt/homebrew/bin/tectonic ]]; then
  TECTONIC_BIN=/opt/homebrew/bin/tectonic
else
  echo "Could not find tectonic. Install it or set TECTONIC to its path." >&2
  exit 127
fi

echo "Using tectonic: $TECTONIC_BIN"
cd "$PAPER_DIR"
"$TECTONIC_BIN" "$PAPER_SOURCE"
