# Inputs/Outputs Projection

`tools/io_projection.py` is non-normative reference tooling that produces a
deterministic Inputs/Outputs summary from a validated Service Contract and a
verified UCI schema snapshot. It does not reconstruct an official OMS Service
Contract or an official DOCX table.

## Ownership boundary

| Source | Projection fields |
| --- | --- |
| Service Contract | function/use, direction, mandate, name, topic, operational attribute, subscription group, Appendix C mapping, timing, Data Transfer fields, details, and reference |
| Verified UCI snapshot | primitive, message QName, exact global message-type QName, manifest ID, and source path |

UCI primitive values are rendered losslessly in the **UCI Primitive** column
(for example, `DataRequest-2`). The projection deliberately does not infer
ambiguous OMS row MP abbreviations from names or primitive families.

## Usage

```bash
python tools/io_projection.py \
  --contract examples/service-status.yaml \
  --baseline-manifest schema-sources/uci/2.5/manifest.yaml \
  --baseline-source-root /path/to/uci \
  --format markdown
```

Use `--format json` for deterministic reference-tool output. The CLI accepts
`--extension MANIFEST SOURCE_ROOT` with the same manifest composition and
immutable verified-byte loading behavior as `tools/uci_resolver.py`.

## Diagnostics

The projection join reports stable `IP_*` diagnostics for unexpected,
ambiguous, message-mismatched, or missing OMS resolutions. Failures during
contract validation, schema-source selection/verification, or UCI resolution
retain their existing `SC_*`, `SS_*`, or `UR_*` diagnostic codes unchanged.

## Rendering semantics

Functions and exchanges retain declaration order. Applicable functions receive
one Markdown table; `not_applicable` functions retain their heading and reason.
Markdown escapes pipes and replaces embedded newlines with spaces. JSON keeps
canonical portable values and semantic field names in a deliberate stable
layout; it is not a normative resolved-contract format.

Markdown display mappings are presentation only: input/output are `I`/`O`,
mandatory/optional are `M`/`O`, asynchronous/on-demand/periodic are
`A`/`OD`/`P`, and OMS Message/Data Transfer/Special Signal/Security Exchange
are `M`/`DT`/`SS`/`SE`. Non-OMS Messages have no invented OMS code.

OMS information is `topic`, followed when present by `[operational_attribute]`
and `[subscription_group]`. Data Transfer information is
`protocol [data_type, data_format, sharing_pattern]`. Other kinds use existing
`details`; `reference` is retained separately. Appendix C is blank unless the
contract supplies it.

Asynchronous timing has blank numerical cells. On-demand values, when present,
are rendered in seconds; periodic values, when present, are rendered in Hz.
Missing optional numbers stay blank and no defaults are inferred.

## UCI 2.5 example evidence

With manifest `uci-2.5-baseline` at revision
`093610b7753944059360d3236770ab446d039556`, the Service Status example resolves
to `Status-1` for `ServiceStatus` and `DataRequest-2` for both
`ServiceStatusDataRequest` and `ServiceStatusDataRequestStatus`. The Service
Initialization example resolves both `FileMetadata` and `FileLocation` as
`DataRecord-1`; this remains visible even where an OMS example's MP-style
presentation may suggest a different family. No compatibility mapping is
applied.

The Subsystem Status example resolves `SubsystemStatus` as `Status-1` and both
`SubsystemStatusDataRequest` and `SubsystemStatusDataRequestStatus` as
`DataRequest-2`. Its authored three-row order is retained in both Markdown and
JSON projection output, with message and exact type QNames from the same
verified UCI snapshot.
