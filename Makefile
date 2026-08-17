.PHONY: paper figures clean-paper analyze manifest verify-release release-audit arxiv hf-dataset p02-paper p02-figures p02-analyze p02-manifest p02-verify

paper: figures
	./scripts/build_paper.sh

figures:
	uv run --script scripts/build_paper_figures.py

clean-paper:
	rm -f paper/*.aux paper/*.bbl paper/*.blg paper/*.fdb_latexmk paper/*.fls paper/*.log paper/*.out paper/*.synctex.gz

analyze:
	uv run --script scripts/analyze_results.py

manifest:
	uv run --script scripts/build_release_manifest.py

verify-release:
	uv run --script scripts/verify_release.py

release-audit:
	./scripts/release_audit.sh

arxiv:
	./scripts/build_arxiv_bundle.sh

hf-dataset:
	uv run --script scripts/build_hf_dataset.py

p02-analyze:
	uv run --script scripts/analyze_p02_results.py

p02-manifest:
	uv run --script scripts/build_p02_release_manifest.py

p02-verify:
	uv run --script scripts/verify_p02_release.py

p02-figures:
	uv run --script scripts/build_p02_figures.py

p02-paper: p02-figures
	./scripts/build_p02_paper.sh
