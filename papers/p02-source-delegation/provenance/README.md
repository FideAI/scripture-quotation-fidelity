# Paper 02 Provenance

This directory contains the release-safe prospective lock, execution seal,
deviation summary, and release manifest. The private lock was written before
confirmatory execution; its public derivative discloses artifact hashes without
exposing private paths or source text.

The manifest identifies this package as a public release candidate pending
final approval. A later release decision should be recorded explicitly rather
than inferred from the existence of these files.

After adding, removing, or changing an intended release artifact, run
`make p02-manifest` before `make p02-verify` to reseal the package.
