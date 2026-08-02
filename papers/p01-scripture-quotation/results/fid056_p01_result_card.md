# FID-056-P01 Result Card

## Question

When a user asks for an exact quotation from an authoritative source, which
responsibilities should belong to the model, and which should belong to
retrieval or deterministic source systems?

## Study Scope

The confirmatory study crossed:

- 20 Scripture passage targets;
- 2 prompt families: explicit reference and contextual description;
- 4 delivery conditions;
- 3 open English editions: BSB, WEBU, and LSV;
- 6 model-family routes; and
- 3 repeated observations per cell.

All 8,640 scheduled observations completed. The study is a matched evaluation
of delivery conditions, not a model leaderboard or a probability sample of
Scripture requests.

## Main Result

Exact delivery required exact final text and all condition-specific evidence
that the declared delivery path was followed.
Terminal provider errors remained failures in the denominator.

| Condition | Exact | N | Rate | Wilson 95% CI |
| --- | ---: | ---: | ---: | ---: |
| Native parametric quotation | 540 | 2,160 | 25.00% | 23.22%-26.87% |
| Source-supplied quotation | 2,022 | 2,160 | 93.61% | 92.50%-94.57% |
| Tool-mediated retrieval | 1,730 | 2,160 | 80.09% | 78.36%-81.72% |
| Reference selection plus deterministic rendering | 1,971 | 2,160 | 91.25% | 89.98%-92.37% |

The conditions intentionally assign different responsibilities. Source
supplied is a gold-passage preservation ceiling that performs neither selection
nor retrieval, so the pooled rates and paired differences are descriptive and
must not be read as equal-burden treatment effects.

Paired risk differences relative to native quotation were +68.61 percentage
points for source-supplied quotation, +55.09 for tool-mediated retrieval, and
+66.25 for deterministic rendering. Target-cluster bootstrap 95% intervals
were +61.71 to +75.60, +46.48 to +63.47, and +58.47 to +73.98, respectively.

This is a path-adherent process outcome, called architecture-adherent in the
locked materials, not a common text-only construct. The common final-output
exactness rates were 25.00% for native,
93.61% for source supplied, 82.31% for tool mediated, and 91.25% for
deterministic rendering. Tool-mediated final output was therefore exact in some
cases that failed the stricter method-adherence gates.

The Wilson intervals above are retained as descriptive observation-level
summaries. Repeated rows share a purposive panel of twenty targets, so these
are not population intervals for Scripture passages, models, editions, or user
requests. The paired bootstrap intervals describe variation across the twenty
target clusters within the fixed model and edition panel.

Target-level medians were 18.98% for native, 98.61% for source supplied,
88.43% for tool mediated, and 99.07% for deterministic rendering. A post-hoc
target-cluster-robust fixed-panel sensitivity analysis yielded adjusted
contrasts of +68.61, +55.09, and +66.25 percentage points, respectively. These
support the fixed-panel result but do not create population-level inference.

### Implementation correction

The executed deterministic runner rejected correct references carrying a
redundant edition annotation. All 2,160 saved deterministic responses were
replayed through the corrected parser using the original source fixtures and no
new model calls. The main result reports that complete replay. The original
literal-interface result was 1,813 of 2,160 (83.94%); the public replay files
provide the complete reconciliation.

## Interpretation

The main result concerns the staged delivery system. Exact quotation should not be assumed to
emerge reliably from parametric generation. Making authoritative text
available, retrieving it through a tool, or separating reference selection
from rendering all produced large improvements in this study.

The pooled rates do not imply that one intervention is universally best:

- Source-supplied quotation was highest overall, but 138 observations still
  failed strict path-adherent quotation exactness.
- The source tool was invoked in 2,052 of 2,160 observations, while only 1,818
  satisfied full method adherence. Tool availability was not equivalent to
  correct tool use.
- The model selected the expected reference and completed deterministic lookup
  and replacement in 1,973 observations. Of those, 1,971 produced an exact final
  output. Deterministic rendering remained unable to repair a genuinely wrong
  reference or span.

Long passages were the hardest stratum under every condition. Contextual
descriptions particularly reduced tool-mediated delivery, from 90.19% for
explicit references to 70.00%.

## Integrity and Missingness

Thirty-three terminal provider errors remained non-deliveries: 23 on the
DeepSeek route and 10 on the Kimi route. Thirty-two occurred in native
generation and one in tool-mediated retrieval. Response-level provider and
response-ID metadata were absent for 46 observations; requested
routes nevertheless had one upstream pinned and fallbacks disabled.

The run consumed 1,954,958 input tokens, 3,285,730 output tokens, and 2,772,266
reasoning tokens.

## Release Boundary

This public result package contains aggregate and target-level results plus the
complete 8,640-row deidentified derived-score dataset. It excludes generated
prose, authoritative passage text, raw tool traces, provider response
identifiers, partner-private traces, credentials, and restricted-edition text.

Results apply only to the named routes, run dates, target panel, prompt
families, editions, delivery conditions, and scoring protocol. They do not
establish theological correctness, contextual appropriateness, pastoral
safety, universal legal compliance, training-data membership, product
certification, or a general ranking of models or vendors.

## Files

- `fid056_p01_aggregate_results.csv`: machine-readable aggregate results.
- `fid056_p01_target_level_results.csv`: per-target condition results.
- `fid056_p01_cluster_bootstrap.csv`: locked target-cluster analysis.
- `fid056_p01_cluster_robust_sensitivity.csv`: post-hoc sensitivity analysis.
- `fid056_p01_permissive_parser_replay.csv`: release-safe per-response replay
  classifications and output hashes.
- `fid056_p01_permissive_parser_replay.json`: replay provenance and summaries.
- `../data/fid056_p01_deidentified_trials.csv.gz`: released derived scores.
- `../paper/main.pdf`: working manuscript.
- `../protocol/source_delivery_protocol.md`: public evaluation methodology.
- `../protocol/scoring_spec.md`: metric and failure definitions.
