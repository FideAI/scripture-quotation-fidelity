# Paper 02 Results

Reviewed confirmatory tables and figure inputs are generated here from the
deidentified derived dataset. Calibration runs are instrument-development
evidence and are not included in confirmatory estimates.

- `fid056_p02_effect_estimates.csv` contains the preregistered primary contrast
  and predeclared secondary contrasts with target-cluster bootstrap intervals.
- `fid056_p02_factorial_cells.csv` contains the four headline delegation rates
  with target-cluster bootstrap intervals used in Figure 2.
- `fid056_p02_route_effects.csv` and `fid056_p02_subgroup_effects.csv` contain
  descriptive heterogeneity analyses. Route intervals that are constant across
  observed target clusters are labeled separately for both neutral and conflict
  conditions; this does not imply zero population uncertainty.
- `fid056_p02_delegation_pipeline.csv` contains explicitly conditional,
  post-treatment descriptive rates.
- `fid056_p02_sensitivity_analysis.csv` contains route-as-unit,
  leave-one-route-out, leave-one-target-out, and post-hoc
  correlation-component sensitivity analyses. The latter resamples the 17
  connected components in the target registry so declared related passages
  receive the same bootstrap multiplicity.
- `fid056_p02_repetition_sensitivity.csv` reports each treatment cell by
  repetition to make time-order drift inspectable.
- `fid056_p02_aggregate_results.csv` is a broad descriptive table. Its
  observation-level Wilson intervals are convenience summaries and are not
  used for confirmatory inference or the headline figures. The CSV identifies
  them directly with `ci_method=wilson_observation_level_descriptive`.

Bootstrap intervals use the deterministic order-statistic convention in the
released analysis script: after sorting 10,000 estimates, the lower and upper
bounds are the observations at indices
`floor(0.025 * (B - 1))` and `floor(0.975 * (B - 1))`. This records the exact
executed convention rather than implying interpolation between estimates.
The preregistered intervals retain the locked 20-target clustering rule. The
correlation-component rows are explicitly post hoc and do not replace those
primary estimates.

The released `text_before_source` column is a sealed historical field with a
post-execution specification mismatch. It must not be interpreted as visible
quotation-like text before retrieval. A private-trace census found visible
pre-call text in 107 of 3,664 delegated observations; none contained the full
target or at least half its unique words. No locked score was changed. Every
aggregate row for this field also carries
`metric_note=sealed_specification_mismatch_do_not_interpret_as_visible_pre_call_text`.
