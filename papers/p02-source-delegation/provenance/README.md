# Paper 02 Provenance

This directory contains the release-safe prospective lock, execution seal,
deviation summary, and release manifest. The private lock was written before
confirmatory execution; its public derivative discloses artifact hashes without
exposing private paths or source text.

Fide AI approved the public reproduction packet on 2026-08-26. The explicit
decision, approved and blocked artifact classes, review basis, and claims limit
are recorded in `release_decision_summary.json`; publication must not be
inferred from the existence of data files alone.

After adding, removing, or changing an intended release artifact, run
`make p02-manifest` before `make p02-verify` to reseal the package.
