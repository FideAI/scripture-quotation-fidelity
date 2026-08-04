#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fide AI
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

failed=0

report_matches() {
  local label="$1"
  shift
  local output
  output="$("$@" 2>/dev/null || true)"
  if [[ -n "$output" ]]; then
    printf 'FAIL: %s\n%s\n' "$label" "$output"
    failed=1
  fi
}

report_matches "absolute local paths found" \
  rg -n '/Users/|/home/[^/]+/|\.codex/' . \
  --glob '!papers/p01-scripture-quotation/paper/main.pdf' --glob '!scripts/release_audit.sh'

report_matches "possible credentials or private keys found" \
  rg -n -i '(api[_-]?key|secret|token|password)[[:space:]]*[:=][[:space:]]*[A-Za-z0-9_\-]{12,}|BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY' . \
  --glob '!papers/p01-scripture-quotation/paper/main.pdf' --glob '!scripts/release_audit.sh' \
  --glob '!SECURITY.md' --glob '!CONTRIBUTING.md'

if [[ -f papers/p01-scripture-quotation/data/fid056_p01_deidentified_trials.csv.gz ]]; then
  decompressed_header="$(
    gzip -cd papers/p01-scripture-quotation/data/fid056_p01_deidentified_trials.csv.gz |
      awk 'NR == 1 { header = $0 } END { print header }'
  )"
  if printf '%s\n' "$decompressed_header" | \
      rg -qi '(^|,)(content|generated_text|raw_output|source_text|response_id|tool_calls|tool_trace)(,|$)'; then
    printf 'FAIL: forbidden raw-data column in released trial file\n%s\n' \
      "$decompressed_header"
    failed=1
  fi
  decompressed_matches="$(
    gzip -cd papers/p01-scripture-quotation/data/fid056_p01_deidentified_trials.csv.gz |
      rg -n -i '/Users/|/home/[^/]+/|\.codex/|BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY' ||
      true
  )"
  if [[ -n "$decompressed_matches" ]]; then
    printf 'FAIL: private path or key material in released trial file\n%s\n' \
      "$decompressed_matches"
    failed=1
  fi
fi

report_matches "forbidden private artifact filenames found" \
  find . -type f \( \
    -iname '*raw*output*' -o -iname '*partner*trace*' -o \
    -iname '*held*out*' -o -iname '*.env' -o -iname '.env.*' -o \
    -iname '*credential*' -o -iname '*private*manifest*' \
  \) -not -path './.git/*'

report_matches "private engine source-like paths found" \
  find . -type d \( -name 'fide-eval-engine' -o -name 'raw_outputs' -o \
    -name 'product_traces' -o -name 'source_corpora' \) -not -path './.git/*'

if [[ -d papers/p01-scripture-quotation/results ]]; then
  report_matches "unapproved result artifact types found" \
    find papers/p01-scripture-quotation/results -type f ! -name '*.md' ! -name '*.csv' ! -name '*.json' \
    ! -name '*.png' ! -name '*.pdf'
fi

if ! uv run --script scripts/verify_release.py; then
  failed=1
fi

if ! uv run --script scripts/build_hf_dataset.py >/dev/null; then
  printf 'FAIL: Hugging Face release staging failed\n'
  failed=1
fi

if (( failed )); then
  exit 1
fi

printf 'Release audit passed. Human release review is recorded in the public decision summary.\n'
