# UCI 2.5 to 2.6 Resolver Evidence

This records a resolver/schema experiment, not OMS cross-version compliance
certification. OMS 2.5 example message names are used only as continuity inputs;
OMS and UCI versions remain independent contract fields.

## Pinned material and extraction

- UCI 2.5: tag `v2.5`, revision `093610b7753944059360d3236770ab446d039556`.
- UCI 2.6: tag `v2.6`, revision `78eb61b6112c8bffa40820c33124b57787fc5bd9`;
  public release date: 8 July 2026.
- UCI 2.6 official ZIP repository path: `UCI Release Documentation - UCI Schema/03_UCI-STD-002_Rev6_UCI_Schema_v2_6-CDRL.zip`.
- Observed ZIP SHA-256: `073dafd85f0a1cf2f1668f75a73aca6a5af28895e0b4645186ed7b23014c145e`.

Extract that ZIP outside this repository and use its top-level directory as the
source root. Its root schema is `UCI_MessageDefinitions_v2_6_0.xsd`. Its direct
include closure for the current resolver is:

- `UCI_MessageDefinitions_v2_6_0.xsd` — `af54ce724c4fe869c8208c86985c0b768d74d581691e21d66c88bb6cfe59955b`
- `UCI_SecurityMarkings_v2_6_0.xsd` — `ee6e58d5db9fd80d526bc964b8244ec296d106301640d34c3cb2c5c00b710b88`

`UCI_Versioning_v2_6_0.xsd` imports the root schema; it is not imported by the
root and is outside the resolver file closure. No XSD or ZIP bytes are checked
in. The manifest schema was unchanged because it already models extracted local
files with immutable upstream revision and byte hashes.

## Observed full-schema results

Using verified source snapshots, UCI 2.5 produced 722 primitive-tagged global
messages, 722 resolved message type references, 722 resolved complex types, and
0 resolved simple types. UCI 2.6 produced 725, 725, 725, and 0, respectively.

Run the repeatable local check after acquiring the two source trees:

```bash
python tools/uci_version_regression.py \
  --uci-25-source-root /path/to/uci-2.5 \
  --uci-26-source-root /path/to/extracted-uci-2.6-schema \
  --format json
```

The command verifies both manifests before parsing, enforces the counts above,
and reports deterministic records without local paths or timestamps.

## Continuity set

The set is Service Status (`ServiceStatus`, `ServiceStatusDataRequest`,
`ServiceStatusDataRequestStatus`), Service Initialization (`FileMetadata`,
`FileLocation`), Subsystem Status (`SubsystemStatus`,
`SubsystemStatusDataRequest`, `SubsystemStatusDataRequestStatus`), and the OMS
2.5 capability example (`ESM_SettingsCommand`, `ESM_SettingsCommandStatus`).

All ten are **unchanged** from 2.5 to 2.6: each exists; retains its local name,
expanded message QName, UCI primitive, exact message type QName, and `complex`
declaration kind. Thus this evidence set has no primitive, message-QName, or
type-QName differences, and no missing or newly resolvable messages. The three
additional UCI 2.6 primitive-tagged messages are outside this deliberately
limited repository-used continuity set.

The resolver remains fail-closed: a missing message is reported as absent rather
than aliased, renamed, searched by similarity, or resolved from UCI 2.5.
