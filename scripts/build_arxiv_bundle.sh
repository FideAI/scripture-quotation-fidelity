#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Fide AI
#
# Stage an arXiv submission tarball for a paper in this repository.
#
# arXiv compiles submitted source itself and publishes that source publicly.
# This script therefore (a) ships a current .bbl so arXiv never needs to run
# bibtex, (b) includes only files the build actually needs, and (c) refuses to
# package a .tex containing comments, since anyone can download the source.
#
# Usage: scripts/build_arxiv_bundle.sh [paper-dir]
#        defaults to papers/p01-scripture-quotation

set -euo pipefail

# Match the reproducible-build epoch used by scripts/build_paper.sh so staging
# an arXiv bundle does not change the committed PDF's digest.
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-1753574400}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PAPER_REL="${1:-papers/p01-scripture-quotation}"
PAPER_DIR="$ROOT_DIR/$PAPER_REL/paper"
BUILD_DIR="$ROOT_DIR/build/arxiv"
STAGE="$BUILD_DIR/$(basename "$PAPER_REL")"

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

if [[ ! -f "$PAPER_DIR/main.tex" ]]; then
  echo "No main.tex under $PAPER_DIR" >&2
  exit 1
fi

TECTONIC_BIN="$(find_tectonic || true)"
if [[ -z "$TECTONIC_BIN" ]]; then
  echo "Could not find tectonic; install it or set TECTONIC to its executable path." >&2
  exit 127
fi

# A current .bbl is required: arXiv will not reliably run bibtex.
echo "==> Compiling to refresh main.bbl"
( cd "$PAPER_DIR" && "$TECTONIC_BIN" -X compile main.tex --keep-intermediates >/dev/null )

if [[ ! -f "$PAPER_DIR/main.bbl" ]] || ! grep -q '\\bibitem' "$PAPER_DIR/main.bbl"; then
  echo "main.bbl was not produced with bibliography entries; cannot submit without it" >&2
  exit 1
fi

rm -rf "$STAGE"
mkdir -p "$STAGE/figures"

cp "$PAPER_DIR/main.tex" "$PAPER_DIR/main.bbl" "$PAPER_DIR/references.bib" "$STAGE/"
cp "$PAPER_DIR"/*.bst "$STAGE/" 2>/dev/null || true
while IFS= read -r figure; do
  [[ -n "$figure" ]] || continue
  if [[ ! -f "$PAPER_DIR/figures/$figure" ]]; then
    echo "Missing referenced figure: $figure" >&2
    exit 1
  fi
  cp "$PAPER_DIR/figures/$figure" "$STAGE/figures/"
done < <(
  grep -oE '\\includegraphics(\[[^]]*\])?\{[^}]+\}' "$PAPER_DIR/main.tex" |
    sed -E 's/.*\{([^}]+)\}/\1/' |
    sort -u
)

# arXiv source is public. Refuse to ship notes-to-self.
if grep -qE '^\s*%|[^\\]%.*[A-Za-z]' "$STAGE/main.tex"; then
  echo "FAIL: main.tex contains LaTeX comments." >&2
  echo "arXiv publishes submitted source; remove them before packaging." >&2
  grep -nE '^\s*%|[^\\]%.*[A-Za-z]' "$STAGE/main.tex" >&2 | head
  exit 1
fi

# Generate the metadata abstract before packaging and enforce arXiv's field
# limit so an otherwise valid source bundle cannot reach submission unusable.
python3 - "$PAPER_DIR/main.tex" "$BUILD_DIR/abstract.txt" <<'PY'
import re
import sys
from pathlib import Path

limit = 1920
src = Path(sys.argv[1]).read_text()
body = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", src, re.S).group(1)
body = body.replace("---", " - ").replace("\\%", "%").replace("``", '"').replace("''", '"')
body = re.sub(r"\\emph\{([^}]*)\}", r"\1", body)
paras = [" ".join(paragraph.split()) for paragraph in body.strip().split("\n\n") if paragraph.strip()]
abstract = "\n\n".join(paras) + "\n"
length = len(abstract.rstrip("\n"))
if length > limit:
    raise SystemExit(f"Abstract is {length} characters; arXiv limit is {limit}")
Path(sys.argv[2]).write_text(abstract)
print(f"==> Wrote {sys.argv[2]} ({length}/{limit} characters)")
PY

TARBALL="$BUILD_DIR/$(basename "$PAPER_REL")-arxiv.tar.gz"
python3 - "$STAGE" "$TARBALL" "$SOURCE_DATE_EPOCH" <<'PY'
import gzip
import sys
import tarfile
from pathlib import Path

stage = Path(sys.argv[1])
tarball = Path(sys.argv[2])
mtime = int(sys.argv[3])
paths = [stage, *sorted(stage.rglob("*"), key=lambda path: path.relative_to(stage).as_posix())]

with tarball.open("wb") as raw:
    with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=mtime) as compressed:
        with tarfile.open(fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT) as archive:
            for path in paths:
                arcname = "." if path == stage else f"./{path.relative_to(stage).as_posix()}"
                info = archive.gettarinfo(str(path), arcname)
                info.uid = 0
                info.gid = 0
                info.uname = "root"
                info.gname = "root"
                info.mtime = mtime
                if info.isfile():
                    with path.open("rb") as source:
                        archive.addfile(info, source)
                else:
                    archive.addfile(info)
PY

echo
echo "==> Wrote $TARBALL"
echo
tar tzf "$TARBALL" | sed 's/^/    /'
echo
cat <<'EOF'
Submission checklist
--------------------
  Categories   primary cs.CL; cross-list cs.AI, cs.CY
               (cs.CY carries the religion-and-technology framing)
  License      choose CC BY 4.0 to match this repository
  Abstract     paste from build/arxiv/abstract.txt (plain text, no LaTeX)
  Comments     note the code/data repository URL in the Comments field
  Check        arXiv's own PDF, not a local one; it recompiles from source
EOF
