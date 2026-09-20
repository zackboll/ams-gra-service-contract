# Portable v0.1 conformance handoff

Portable v0.1 compatibility is defined by the schema at
`schema/v0.1/service-contract.schema.json` and the machine-readable corpus at
`conformance/v0.1/manifest.json`. The manifest points to every fixture, records
its acceptance expectation, optional reference-validator `SC_*` codes, and
YAML/JSON semantic equivalence groups.

The `materialized-complete-service` equivalence group is also the deterministic
portable serialization golden for completion materialization: its YAML and JSON
members must parse to the same contract model.

`schema_canonical_sha256` is SHA-256 over parsed schema JSON serialized with
sorted keys, compact separators, UTF-8, and `ensure_ascii=False`. It detects
accidental changes to the v0.1 compatibility surface; it is not semantic proof.
The reference command recomputes it:

```bash
python tools/conformance.py check conformance/v0.1/manifest.json
```

## Independent consumers

An independent reader accepts every valid case, rejects every invalid case, and
makes members of an equivalence group equal in its parsed contract model. It
need not reproduce Python diagnostic prose or codes. The pack has no runtime
dependency on another repository.

### OMS-codegen handoff

`ams-gra-codegen-oms` is the first intended independent consumer. It should pin
or otherwise record the manifest/schema revision, run its own reader against the
corpus, and report compatibility results independently. Portable acceptance does
not imply OMS 2.5 profile conformance, UCI message existence, extension mapping,
or code-generation readiness. Extension identifiers remain logical portable
strings until a schema-source/codegen integration resolves them.

For a concrete handoff, see [Task 044](task-044-yaml-safe-contract-output.md).
