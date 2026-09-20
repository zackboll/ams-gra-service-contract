# Task 047 — Deterministic source extraction

Implemented tooling-only, offline extraction recipes with raw-byte SHA-256 verification, exact regex capture/assertion, and JSON/YAML scalar pointers. All failures are fail-closed `CA_EXTRACTION_*` diagnostics. The portable and completion-input schemas remain unchanged.

The RF FM Demod recipe pins revision `af13bd2926b15253e795920c91320733a29927ea`: `oms-service-contract.md` `3b3b2d22cd1c7169eb81547d1e1ad6583407ea7d3ee6184d598f1dbc7c9e40aa`, `configuration.md` `35d3f5f45e871a9d432ebeaf0f669297d5c499b50c938807a4320bfc39095a84`, and `contracts.md` `9cd199802968a32beb92832b4c556efab53369bcf0059d4b2a096d100b37cc58`. Its 23 rules reproduce all 23 Task 046 candidates semantically. SignalReport trigger/rate remain observations; no Capability inventory, decisions, mapping, or structure is generated.
