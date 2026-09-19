# Task 035 — Provenance-preserving completion worksheet core

Tasks 033–034 found that published material can establish message, direction,
topic, and some timing/rate observations while still lacking authored Service
Contract fields such as LoM, function category, required group, applicability,
and complete required exchange coverage. Treating those observations as a valid
or partial contract would either invent semantics or weaken the complete
authoring grammar.

Task 035 implements **Direction A**: an authoring workspace. Its completion
input records temporary, unconfirmed candidates with source provenance and an
explicit target context. It is not Direction B, a domain model of incomplete
Service Contracts: it does not introduce unknown values into the contract
grammar, replace that grammar, or carry runtime/interoperability semantics.

The worksheet keeps the boundary explicit:

```text
Published/source evidence -> completion worksheet -> explicit human review -> authored Service Contract
```

Only a later explicit human confirmation step can create contract semantics.
No consumer may treat a worksheet as a Service Contract, pass it to ordinary
contract validation, infer OMS compliance from it, or generate an implementation
from it. The tool has no source extraction, LLM inference, candidate ranking,
selection, mapping, apply, or contract-generation path.

The worksheet displays compatible OMS profile requirements separately from
observed candidates. It does not assert candidate-to-profile satisfaction. The
IR Search and Track exercise preserves Task 034 evidence for identity, message
selector/direction, topics, and configured status rate at pinned revision
`7d06735e56aa0baa8cc61e578928ee4d28936bc3`; it deliberately invents no LoM,
function metadata, applicability, event-to-asynchronous classification, or
Capability inventory.
