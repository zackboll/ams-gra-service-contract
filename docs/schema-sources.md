# Schema-Source Manifests

A Service Contract identifies logical standards versions, while a schema-source
manifest pins the external schema bytes a toolchain uses for a particular
standard version.

```text
service contract                         UCI XSD
  -> UCI version                            -> actual message schema
toolchain mapping
  -> schema-source manifest
  -> repository revision, paths, digests
```

For example, a contract declaring `standards.uci_schema_version: "2.5"` can be
mapped by a toolchain to
`schema-sources/uci/2.5/manifest.yaml`. The manifest specifies the immutable
upstream Git revision, root XSD, required local XSD subset, and SHA-256 digest
for each raw file. A tool must validate the manifest and verify a supplied local
source tree before loading `root_schema`.

The manifest is a separately versioned toolchain artifact, not part of the
portable Service Contract grammar. It does not duplicate XSD-owned message
definitions, types, primitive metadata, or namespaces. It also does not
redistribute, incorporate, or relicense the UCI XSD files.

## Trust boundary

The `sources:` field in a Service Contract provides traceability. It must not
automatically trigger external fetching. A schema-source manifest is instead an
explicit reproducibility input selected by the toolchain. Local verification is
offline and checks only manifest-declared files; unrelated files in a source
checkout are ignored.

## Checked-in UCI 2.5 baseline

The baseline manifest is
[`schema-sources/uci/2.5/manifest.yaml`](../schema-sources/uci/2.5/manifest.yaml).
It declares schema family `uci`, schema version `2.5`, role `baseline`, and
manifest identity `uci-2.5-baseline` at manifest version `0.1`.

- upstream repository: `https://github.com/open-arsenal/uci.git`;
- release tag: `v2.5`;
- immutable revision: `093610b7753944059360d3236770ab446d039556`;
- root: `OAC-STD-UCI_V2.5/UCI_MessageDefinitions_v2_5_0.xsd`; and
- dependency closure:
  - `OAC-STD-UCI_V2.5/UCI_MessageDefinitions_v2_5_0.xsd`;
  - `OAC-STD-UCI_V2.5/UCI_SecurityMarkings_v2_5_0.xsd`.

At present `v2.5` resolves directly to that immutable revision. Reproducibility
relies on the stored revision and digests rather than trusting a tag name alone.
The manifest is the source of truth for exact raw-byte SHA-256 values.

## Version independence

These version values are independent unless an explicit toolchain compatibility
rule connects them:

```text
contract_version = 0.1
manifest_version = 0.1
profile_version = 0.1
OMS = 2.5
UCI = 2.5
```

In particular, neither OMS nor UCI versions are inferred from
`contract_version` or `manifest_version`.

## Commands

### Manifest validation

Validate the checked-in manifest without network access:

```bash
python tools/schema_sources.py validate schema-sources/uci/2.5/manifest.yaml
```

This validates the manifest JSON Schema, manifest semantic rules, path rules,
and root/file-set invariants. It does not contact GitHub and does not prove that
an arbitrary local UCI checkout has matching bytes. This is the operation run by
`make check` and CI.

### Local source-byte verification

Verify raw bytes in an already obtained local checkout:

```bash
python tools/schema_sources.py verify schema-sources/uci/2.5/manifest.yaml \
  --source-root /path/to/uci
```

This additionally verifies raw bytes of the manifest-declared local files
against their SHA-256 values. It remains offline and requires an already
obtained local checkout/tree.
