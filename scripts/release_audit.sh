#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fide AI
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

failed=0
credential_pattern='(api[_-]?key|secret|token|password)[[:space:]]*[:=][[:space:]]*[A-Za-z0-9_\-]{12,}|BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY'

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
  --glob '!papers/*/paper/main.pdf' --glob '!scripts/release_audit.sh'

report_matches "possible credentials or private keys found" \
  rg -n -i "$credential_pattern" . \
  --glob '!papers/*/paper/main.pdf' --glob '!scripts/release_audit.sh' \
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
      rg -n -i "/Users/|/home/[^/]+/|\\.codex/|$credential_pattern" ||
      true
  )"
  if [[ -n "$decompressed_matches" ]]; then
    printf 'FAIL: private path or key material in released trial file\n%s\n' \
      "$decompressed_matches"
    failed=1
  fi
fi

if [[ -f papers/p02-source-delegation/data/fid056_p02_deidentified_trials.csv.gz ]]; then
  decompressed_header="$(
    gzip -cd papers/p02-source-delegation/data/fid056_p02_deidentified_trials.csv.gz |
      awk 'NR == 1 { header = $0 } END { print header }'
  )"
  if printf '%s\n' "$decompressed_header" | \
      rg -qi '(^|,)(raw_output|final_output|answer|source_text|provider_response_ids|actual_providers|error|trial_id|execution_request_id)(,|$)'; then
    printf 'FAIL: forbidden raw-data column in Paper 02 trial file\n%s\n' \
      "$decompressed_header"
    failed=1
  fi
  decompressed_matches="$(
    gzip -cd papers/p02-source-delegation/data/fid056_p02_deidentified_trials.csv.gz |
      rg -n -i "/Users/|/home/[^/]+/|\\.codex/|$credential_pattern" ||
      true
  )"
  if [[ -n "$decompressed_matches" ]]; then
    printf 'FAIL: private path or key material in Paper 02 trial file\n%s\n' \
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

report_matches "symbolic links found in public package" \
  find . -type l -not -path './.git/*'

report_matches "private engine source-like paths found" \
  find . -type d \( -name 'fide-eval-engine' -o -name 'raw_outputs' -o \
    -name 'product_traces' -o -name 'source_corpora' \) -not -path './.git/*'

for results_dir in papers/*/results; do
  [[ -d "$results_dir" ]] || continue
  report_matches "unapproved result artifact types found" \
    find "$results_dir" -type f ! -name '*.md' ! -name '*.csv' ! -name '*.json' \
    ! -name '*.png' ! -name '*.pdf'
done

if ! uv run --script scripts/verify_release.py; then
  failed=1
fi

if ! uv run --script scripts/verify_p02_release.py; then
  failed=1
fi

if ! uv run --script scripts/build_hf_dataset.py >/dev/null; then
  printf 'FAIL: Hugging Face release staging failed\n'
  failed=1
fi

if (( failed )); then
  exit 1
fi

printf 'Release audit passed. Each paper records its release status in its provenance package.\n'
