# Reference Audit

Audit date: 2026-07-27

This audit verifies the identity and bibliographic metadata of every source in
`paper/references.bib` against a publisher, proceedings, DOI, government, or
official rights-holder record. It also records whether the manuscript uses the
source for a claim that the source can support.

## Result

- No cited work was found to be fabricated.
- Every technical-paper citation now resolves to an official proceedings,
  journal, publisher, or conference record.
- One material metadata error was corrected: `ji2023survey` previously combined
  the ten-author ACM journal record with three additional authors from a later
  arXiv revision.
- `huang2023survey` was updated from its 2023 arXiv record to the peer-reviewed
  2025 ACM journal article.
- Published versions are now cited for Lewis et al., Carlini et al. (2023),
  HELM, the U.S. Copyright Office report, and the WEB/WEBU licensing statement,
  rather than attaching an arXiv DOI or an access year to a different
  publication type.
- Six verified sources were added because they are directly adjacent to the
  paper's novelty claim: Toolformer, When2Call, grammar-constrained decoding,
  CopyBench, Quote-Tuning, and Metzger and Ehrman's textual-history volume.

## Citation-Level Verification

| Key | Status | Authoritative record | Claim-use assessment |
| --- | --- | --- | --- |
| `lewis2020retrieval` | Verified | https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html | Supports the description of RAG as combining parametric generation with retrieved evidence. |
| `mallen2023when` | Verified | https://aclanthology.org/2023.acl-long.546/ | Supports the parametric versus non-parametric memory framing. |
| `min2023factscore` | Verified | https://aclanthology.org/2023.emnlp-main.741/ | Supports fine-grained factuality evaluation. |
| `gao2023alce` | Verified | https://aclanthology.org/2023.emnlp-main.398/ | Supports citation-oriented generation and attribution evaluation. |
| `ji2023survey` | Corrected and verified | https://doi.org/10.1145/3571730 | Supports broad hallucination taxonomy. Journal author list now matches the DOI record. |
| `huang2023survey` | Corrected and verified | https://doi.org/10.1145/3703155 | Supports the LLM hallucination survey claim. Updated to the 2025 journal version. |
| `es2024ragas` | Verified | https://aclanthology.org/2024.eacl-demo.16/ | Supports the statement that RAGAS evaluates retrieval and generation dimensions. |
| `carlini2021extracting` | Verified | https://www.usenix.org/conference/usenixsecurity21/presentation/carlini-extracting | Supports the claim that model outputs can reproduce memorized training material under some conditions. |
| `carlini2023quantifying` | Corrected and verified | https://openreview.net/forum?id=TatRHT_1cK | Supports cross-model memorization measurement. Citation now names the ICLR publication rather than attaching the arXiv DOI to it. |
| `usco2025ai` | Corrected and verified | https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-3-Generative-AI-Training-Report-Pre-Publication-Version.pdf | Supports policy and legal context only. The citation now identifies the document as the pre-publication version. |
| `liang2022helm` | Corrected and verified | https://openreview.net/forum?id=iO4LZibEqW | Supports multi-metric, scenario-based evaluation methodology. Citation now points to the TMLR record. |
| `ribeiro2020checklist` | Verified | https://aclanthology.org/2020.acl-main.442/ | Supports behavioral and capability-specific testing. |
| `schick2023toolformer` | Verified | https://proceedings.neurips.cc/paper/2023/hash/d842425e4bf79ba039352da0f658a906-Abstract-Conference.html | Supports model decisions about when and how to invoke tools. |
| `ross2025when2call` | Verified | https://aclanthology.org/2025.naacl-long.174/ | Supports explicit evaluation of when a model should and should not call a tool. |
| `geng2023grammar` | Verified | https://aclanthology.org/2023.emnlp-main.674/ | Supports the distinction between prompted structured output and grammar-constrained decoding. |
| `chen2024copybench` | Verified | https://aclanthology.org/2024.emnlp-main.844/ | Establishes directly adjacent work on literal and non-literal reproduction. |
| `zhang2025verifiable` | Verified | https://aclanthology.org/2025.naacl-long.191/ | Establishes directly adjacent work on aligning models to quote verifiable strings from trusted corpora. |
| `metzger2005text` | Verified | https://academic.oup.com/jts/article-abstract/57/2/551/1643535 | Supports only the broad textual-history framing. It is not used as evidence for the empirical AI results or for translation superiority. |
| `tov2012textual` | Verified | https://ms.fortresspress.com/downloads/9780800696641BibleTodayJuly2012.pdf | Publisher-hosted review confirms author, title, third revised and expanded edition, publisher, year, and pagination. Used only for Hebrew Bible textual-history context. |
| `nida1969theory` | Verified | https://brill.com/display/title/8384 | Publisher record and title pages confirm authors, title, original 1969 publication, series, and publisher. Used for the distinction between translation decisions and verbatim reproduction of a selected edition. |
| `berean2023license` | Verified | https://berean.bible/licensing.htm | Official source for the BSB public-domain statement. |
| `weblicense` | Corrected and verified | https://ebible.org/eng-web/webfaq.htm | Official FAQ identifies WEB/WEBU and public-domain/CC0 status; publication year is the page's update year, not the access year. |
| `lsvlicense` | Verified | https://www.bible.com/en-GB/versions/2660-lsv-literal-standard-version | Official edition page states the 2020 edition and CC BY-SA release. |

## Important Boundaries

- Bibliographic verification does not validate the manuscript's statistical
  analysis or establish that every broad theological statement has received
  scholarly review.
- The three edition-license sources support corpus selection and release
  boundaries, not translation quality, doctrinal soundness, or source-language
  fidelity.
- The U.S. Copyright Office report is a government policy source, not a
  peer-reviewed technical study and not legal advice.
- The Metzger and Ehrman citation is New Testament-focused. Before journal
  submission, a biblical scholar should advise whether additional Hebrew Bible,
  translation-theory, and canon scholarship is necessary for the final wording.

## Audit Method

1. Match title and full author list to the authoritative record.
2. Match year, venue or journal, volume/issue, pages, DOI, and URL where
   applicable.
3. Prefer the published version when manuscript prose names a published venue.
4. Check that manuscript prose does not attribute a stronger conclusion than
   the source supports.
5. Record official licensing statements separately from peer-reviewed research.
