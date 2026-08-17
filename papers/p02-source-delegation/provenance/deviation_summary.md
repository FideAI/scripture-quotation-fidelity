# Paper 02 Deviation Summary

No confirmatory prompt, target, treatment, source, model route, repetition,
outcome, or analysis rule changed after the prospective lock.

Three instrumentation defects were found and repaired during excluded
calibration runs before lock: missing treatment and tool-contract hashes, an
incorrect repetition label in CLI exports, and the need to rerun calibration
on the final shared commit. None of those calibration observations enters a
Paper 02 result.

After execution began, review found that the frozen target snapshot retained a
clerical status label saying that P02 lock was pending. The pre-execution lock
receipt already fixed the snapshot's digest and designated it as the
confirmatory target artifact. The stale label was not changed because that
would alter a locked input; it had no effect on content, execution, or analysis.

Post-execution review also found specification mismatches in three secondary
fields. The executed `text_before_source` field counted serialized reasoning
content and bypass answers rather than only visible pre-call text;
`source_result_used` detects intended-fixture text rather than causal use of an
observed return; and the rubric description of `final_output_exact` corresponds
to the implemented span-exactness field, while the implemented final-output
field additionally checks wrapper compliance. The locked artifact and derived
rows remain unchanged. A retrospective private-trace census found visible
pre-call text in 107 of 3,664 delegated observations, with no complete target
or at least 50% unique-target-word coverage. These fields are disclosed using
their operational meanings and are not primary evidence.

Confirmatory execution remains pinned to shared implementation revision
`dbb1514cde5c7a8e17944d09cf16d0ed1ee619cc`. The prospective correction to
visible pre-call text scoring and its regression tests were committed after
execution as `45f6114580f2e2a5e1823cd65c6156987f48f90b`. The corrected revision
must not be substituted for the executed tree when archiving this study.
