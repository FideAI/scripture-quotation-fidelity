.PHONY: paper papers figures clean-paper clean-papers analyze p01-analyze manifest verify verify-release release-audit arxiv hf-dataset p02-paper p02-figures p02-analyze p02-manifest p02-verify p02-arxiv p02-hf-dataset

paper: figures
	./scripts/build_paper.sh

papers: paper p02-paper

figures:
	uv run --script scripts/build_paper_figures.py

clean-paper:
	rm -f \
		papers/p01-scripture-quotation/paper/*.aux \
		papers/p01-scripture-quotation/paper/*.bbl \
		papers/p01-scripture-quotation/paper/*.blg \
		papers/p01-scripture-quotation/paper/*.fdb_latexmk \
		papers/p01-scripture-quotation/paper/*.fls \
		papers/p01-scripture-quotation/paper/*.log \
		papers/p01-scripture-quotation/paper/*.out \
		papers/p01-scripture-quotation/paper/*.synctex.gz

clean-papers: clean-paper
	rm -f \
		papers/p02-source-delegation/paper/*.aux \
		papers/p02-source-delegation/paper/*.bbl \
		papers/p02-source-delegation/paper/*.blg \
		papers/p02-source-delegation/paper/*.fdb_latexmk \
		papers/p02-source-delegation/paper/*.fls \
		papers/p02-source-delegation/paper/*.log \
		papers/p02-source-delegation/paper/*.out \
		papers/p02-source-delegation/paper/*.synctex.gz

analyze: p01-analyze p02-analyze

p01-analyze:
	uv run --script scripts/analyze_results.py

manifest:
	uv run --script scripts/build_release_manifest.py

verify-release:
	uv run --script scripts/verify_release.py

verify: verify-release p02-verify

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

p02-arxiv:
	./scripts/build_arxiv_bundle.sh papers/p02-source-delegation

p02-hf-dataset:
	uv run --script scripts/build_p02_hf_dataset.py
