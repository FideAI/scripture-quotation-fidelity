#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fide AI
set -euo pipefail

# Tectonic embeds a build timestamp, so PDF output is otherwise non-reproducible
# and every compile invalidates the release manifest. Pin the epoch to the
# study's prospective-lock date so the same source always yields the same bytes.
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-1753574400}"


ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PAPER_DIR="$ROOT_DIR/papers/p01-scripture-quotation/paper"
PAPER_SOURCE="${1:-main.tex}"

if [[ "$PAPER_SOURCE" != "$(basename "$PAPER_SOURCE")" || "$PAPER_SOURCE" != *.tex ]]; then
  echo "Paper source must be a .tex filename in $PAPER_DIR" >&2
  exit 2
fi

if [[ ! -f "$PAPER_DIR/$PAPER_SOURCE" ]]; then
  echo "Paper source not found: $PAPER_DIR/$PAPER_SOURCE" >&2
  exit 2
fi

find_tectonic() {
  if [[ -n "${TECTONIC:-}" && -x "$TECTONIC" ]]; then
    printf '%s\n' "$TECTONIC"
    return 0
  fi

  if command -v tectonic >/dev/null 2>&1; then
    command -v tectonic
    return 0
  fi

  if [[ -x "/opt/homebrew/bin/tectonic" ]]; then
    printf '%s\n' "/opt/homebrew/bin/tectonic"
    return 0
  fi

  return 1
}

TECTONIC_BIN="$(find_tectonic || true)"

if [[ -z "$TECTONIC_BIN" ]]; then
  cat >&2 <<'EOF'
Could not find tectonic.

Install it or set TECTONIC to the compiler path, for example:

  export TECTONIC=/opt/homebrew/bin/tectonic

On this workspace, previous paper builds used:

  /opt/homebrew/bin/tectonic
EOF
  exit 127
fi

echo "Using tectonic: $TECTONIC_BIN"
cd "$PAPER_DIR"
"$TECTONIC_BIN" "$PAPER_SOURCE"
