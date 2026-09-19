# Task 038 — Fail-closed portable contract materialization

Task 038 materializes the applicable OMS 2.5 profile-required function scaffold
into a portable v0.1 Service Contract only after all required values are resolved
and every explicit author decision is mapped. The synthetic `complete-service`
files are a conformance example, not a published contract.

Materialization is JSON-only and stdout-only. It constructs no specific
functions or capabilities, and it does not copy completion provenance or profile
traceability into the portable document. The expected JSON fixture demonstrates
Data Transfer and asynchronous, periodic, and on-demand timing materialization.

The IR Search and Track exercise intentionally fails closed because it retains
unresolved scaffold values and unmapped decisions for unsupported specific
exchanges.
