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
for each raw file. A tool must validate the manifest, read each supplied local
file once, verify its digest, retain the verified bytes in an immutable snapshot,
and parse that snapshot rather than reopening `root_schema` from the filesystem.

The manifest is a separately versioned toolchain artifact, not part of the
portable Service Contract grammar. It does not duplicate XSD-owned message
definitions, types, primitive metadata, or namespaces. It also does not
redistribute, incorporate, or relicense the UCI XSD files.

## Schema-source set composition

A validated contract composes exactly one baseline manifest and exactly its
declared extension manifests. The baseline manifest MUST have `role: baseline`,
`schema_family: uci`, and a `schema_version` equal to
`standards.uci_schema_version`. For a baseline, `schema_version` is the logical
UCI baseline version.

An extension manifest MUST have `role: extension`. Its `schema_version` is the
extension package's own version, not the UCI baseline version. It MUST declare a
non-empty, unique `compatible_baseline_versions` list; the contract's baseline
version must occur in that list. Baseline manifests MUST NOT have that field.
This clarification retains `manifest_version: "0.1"`: no extension artifact was
previously published here under the extension role.

Extension identifiers map by exact, case-sensitive equality from
`standards.uci_extension_schemas[]` to extension-manifest `id`. Missing declared
manifests, undeclared supplied manifests, duplicate supplied IDs, wrong roles,
and incompatible baselines fail composition.

```text
contract baseline UCI: 2.5
contract extensions: ext-a-1.0, ext-b-2.0
supplied manifests:   ext-b-2.0, ext-a-1.0

composed set:
  1. uci-2.5-baseline
  2. ext-a-1.0
  3. ext-b-2.0
```

The numeric/order presentation is deterministic composition order, **not**
override precedence. It does not resolve duplicate XSD declarations.

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

## Checked-in UCI 2.6 baseline

[`schema-sources/uci/2.6/manifest.yaml`](../schema-sources/uci/2.6/manifest.yaml)
pins tag `v2.6` to revision `78eb61b6112c8bffa40820c33124b57787fc5bd9`.
Unlike UCI 2.5, its official schema is distributed in the repository archive
`UCI Release Documentation - UCI Schema/03_UCI-STD-002_Rev6_UCI_Schema_v2_6-CDRL.zip`.
At that revision the archive SHA-256 is
`073dafd85f0a1cf2f1668f75a73aca6a5af28895e0b4645186ed7b23014c145e`.

Obtain the pinned repository material, verify that archive digest, and extract
the archive outside this repository. Point `--source-root` at its extracted
root, which directly contains `UCI_MessageDefinitions_v2_6_0.xsd`. The resolver
does not download or extract ZIP files. The root includes only
`UCI_SecurityMarkings_v2_6_0.xsd`, so the manifest closure is those two XSDs;
the archive's `UCI_Versioning_v2_6_0.xsd` imports the root and is not needed by
the current resolver.

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
python tools/schema_sources.py validate schema-sources/uci/2.6/manifest.yaml
```

This validates the manifest JSON Schema, manifest semantic rules, path rules,
and root/file-set invariants. It does not contact GitHub and does not prove that
an arbitrary local UCI checkout has matching bytes. This is the operation run by
`make check` and CI.

Failures use stable code-first `SS_*` diagnostics; composition preserves `SC_*`
diagnostics when the supplied Service Contract itself is invalid. See
[diagnostics](diagnostics.md).

### Local source-byte verification

Verify raw bytes in an already obtained local checkout:

```bash
python tools/schema_sources.py verify schema-sources/uci/2.5/manifest.yaml \
  --source-root /path/to/uci

python tools/schema_sources.py verify schema-sources/uci/2.6/manifest.yaml \
  --source-root /path/to/extracted-uci-2.6-schema
```

This additionally reads and verifies raw bytes of the manifest-declared local
files against their SHA-256 values. It remains offline and requires an already
obtained local checkout/tree. Resolver use retains those same verified bytes in
a snapshot for parsing; it does not verify a path and later trust a second read.

### Set composition

Compose validated metadata without fetching or verifying source bytes:

```bash
python tools/schema_sources.py compose \
  --contract contracts/example.yaml \
  --baseline-manifest schema-sources/uci/2.5/manifest.yaml \
  --extension-manifest /path/to/ext-a-manifest.yaml
```

Composition is distinct from local byte verification. A consumer verifies bytes
before loading and parsing a usable XSD set.
