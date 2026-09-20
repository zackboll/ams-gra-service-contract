# v0.2.0 release readiness

## Scope

Prospective repository/tooling release `0.2.0`; portable contract language
remains `0.1`. No tag or publication is created by this preparation work.

## Compatibility surface

| Surface | Supported |
| --- | --- |
| Repository/tooling release | prospective 0.2.0 |
| Portable contract | 0.1 |
| Completion artifacts | 0.1 |
| OMS profile format | 0.1 |
| OMS profile content | OMS 2.5 |
| Schema-source manifest | 0.1 |
| UCI schema-source baselines | 2.5, 2.6 |
| Portable conformance cases | 64 |

## Validated evidence

The support manifest binds the portable schema fingerprint, conformance manifest,
OMS 2.5 profile, and UCI 2.5/2.6 baseline manifests. `release_check.py` is
offline and read-only: it validates repository metadata, not external UCI bytes.
Real UCI 2.5/2.6 resolver regression has been exercised separately using the
pinned source revisions; reproduce it with `tools/uci_version_regression.py` and
the matching local source roots. Conformance corpus execution remains authoritative.

## Known limitations

Only an OMS 2.5 profile exists. Actual service-owner RF answers were not
obtained. There is no second independent consumer. Behavior/state semantics,
full UCI type-layout parsing, and code generation are separate work.

## Release gate

Follow [the release checklist](release-checklist.md). The support manifest does
not contain a self-digest or commit SHA; a future tag identifies the snapshot.

## Post-merge release actions

Create a tag, create a GitHub release, record the immutable release commit, and
optionally update downstream consumer pins. Do not perform these before review.
