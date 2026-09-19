# Completion materialization

`tools/completion_materialize.py` is the first completion operation that emits a
portable v0.1 Service Contract. A worksheet and scaffold remain tooling-only;
successful materializer stdout is a real portable Service Contract.

```bash
python tools/completion_materialize.py \
  --input examples/completion/complete-service.yaml \
  --decisions examples/completion/complete-service-decisions.yaml \
  --mapping examples/completion/complete-service-mapping.yaml \
  --profile profiles/oms/2.5/profile.yaml
```

It produces deterministic JSON only on stdout. It has no output, write, apply,
or in-place option and never mutates files. Failures print `FAIL <diagnostic>` to
stderr and produce no stdout.

After existing completion, decision, mapping, and profile validation, it checks
unresolved required scaffold paths, then unmapped explicit decisions. It then
validates its candidate contract with `SC_*` validation and the selected OMS
profile with `OP_*` validation before emission. Lower-layer diagnostics retain
their original identity.

Only resolved author-owned values are emitted; no IDs, topics, functions, or
defaults are generated. Declared specific functions follow profile-required
functions in structure order. Capability declarations, sources,
and traceability are omitted. Completion candidate provenance is audit evidence,
not automatically authored portable traceability.
