# Upstream References and Source Map

This project is independent and non-authoritative. The links below are provided so schema/semantic decisions can be reviewed against public upstream AMS GRA, OMS, and UCI material.

**Reference snapshot:** 2026-09-18.

## 1. AMS GRA primary sources

### Public AMS GRA repository

- <https://github.com/open-arsenal/ams-gra>

The public repository contains architecture volumes, compliance artifacts, interface-description documents, an executive summary, and a glossary. For this project's scope, the most relevant architecture volumes are below.

### AMS GRA Service MPU

- <https://github.com/open-arsenal/ams-gra/blob/main/Architecture_Volumes/AMS_GRA_Service_MPU.pdf>

Use this as primary AMS GRA architectural context for the Service MPU role/boundary. This repository does not copy or redefine that architecture.

### OMS Service MPU

- <https://github.com/open-arsenal/ams-gra/blob/main/Architecture_Volumes/OMS_Service_MPU.pdf>

Use this for AMS GRA-specific architectural context around OMS Service MPUs. The portable contract defined here remains a companion representation of Service Contract interface information, not an alternative MPU definition.

### Software Architecture

- <https://github.com/open-arsenal/ams-gra/blob/main/Architecture_Volumes/Software_Architecture.pdf>

Relevant when evaluating where generated service interfaces, local functions, and other software components fit in the wider architecture.

### Mission Agnostic Service Infrastructure (MASI)

- <https://github.com/open-arsenal/ams-gra/blob/main/Architecture_Volumes/Mission_Agnostic_Service_Infrastructure.pdf>

Relevant to the infrastructure boundary and CAL-oriented integration context.

### Executive Summary

- <https://github.com/open-arsenal/ams-gra/blob/main/Executive_Summary.pdf>

Useful high-level orientation. Detailed contract semantics should be traced to the OMS artifacts below.

## 2. OMS primary sources

### Public OMS repository

- <https://github.com/open-arsenal/oms>

At this reference snapshot, the repository identifies OMS Version 2.5 as the current released D&D set, released 22 January 2026.

### OMS Standard v2.5

- **Document:** OMSC-STD-001 Rev M
- **Official artifact:** <https://github.com/open-arsenal/oms/blob/main/docs_official/02_OMSC-STD-001_RevM_OMS_Standard_DandD_v2_5.docx>

Use for normative OMS concepts and requirements.

### CAL Specification v2.5

- **Document:** OMSC-SPC-001 Rev L
- **Official artifact:** <https://github.com/open-arsenal/oms/blob/main/docs_official/04_OMSC-SPC-001_RevL_CAL_Specification_DandD_v2_5.docx>

Relevant to CAL APIs/semantics and the runtime boundary. This repository intentionally avoids embedding a particular CAL programming-language API.

### Service Contract Template v2.5

- **Document:** OMSC-TMP-003 Rev M
- **Official artifact:** <https://github.com/open-arsenal/oms/blob/main/docs_official/14_1_OMSC-TMP-003_RevM_ServiceContractTemplate_DandD_v2_5.docx>

The human document structure that motivates the machine-readable companion.

### Service Contract Instructions v2.5

- **Document:** OMSC-INS-003 Rev M
- **Date:** 22 January 2026
- **Official artifact:** <https://github.com/open-arsenal/oms/blob/main/docs_official/14_2_OMSC-INS-003_RevM_ServiceContractInstructions_DandD_v2_5.docx>

This is the principal source for v0.1 Service Contract field semantics. In particular, it describes:

- the function list and Required/Specific categorization;
- Inputs and Outputs tables for functions;
- I/O direction;
- Data Exchange categories (`M`, `DT`, `SS`, `SE`);
- Data Exchange Name/Information;
- Level of Mandate (`M`, `O`);
- periodicity (`A`, `OD`, `P`);
- informative nominal/max timing columns;
- the relationship between Message Primitive and UCI-owned message metadata (serialized as `UCI_PRIMITIVE:` documentation in public UCI 2.5); and
- the rule that a message used as both input and output appears as two unique rows.

The upstream repository also contains an **unofficial Markdown conversion** for search/navigation:

- <https://github.com/open-arsenal/oms/blob/main/docs_markdown_unofficial/14_2_OMSC-INS-003_RevM_ServiceContractInstructions_DandD_v2_5.md>

That Markdown file is convenient for tooling but should not be mistaken for the official source artifact.

### Language-Agnostic CAL Specification v2.5

- **Document:** OMSC-SPC-013 Rev B
- **Official artifact:** <https://github.com/open-arsenal/oms/blob/main/docs_official/20_OMSC-SPC-013_RevB_LanguageAgnostic_CAL_Specification_DandD_v2_5.docx>

Relevant when projecting a resolved contract into language-agnostic CAL integration/deployment artifacts.

### Service Checklist v2.5

- **Checklist:** <https://github.com/open-arsenal/oms/blob/main/docs_official/18_1_OMSC-CHK-005_RevM_ServiceChecklist_DandD_v2_5.xlsx>
- **Instructions:** <https://github.com/open-arsenal/oms/blob/main/docs_official/18_2_OMSC-INS-011_RevM_ServiceChecklistInstructions_DandD_v2_5.docx>

Useful for future compliance/profile validation. v0.1 does not attempt to encode the complete checklist.

## 3. UCI primary sources

### Public UCI repository

- <https://github.com/open-arsenal/uci>

At this reference snapshot, the repository identifies UCI Version 2.6 as released 8 July 2026.

UCI supplies the standardized message-schema definitions that a contract-aware resolver should use for:

- message existence;
- nested type structure;
- enumeration/range metadata;
- message primitive annotations; and
- other schema-owned details.

The contract format therefore stores message references but does not duplicate those definitions.

### Version caveat

An OMS Service Contract may target a different UCI release than the latest available UCI repository release. A contract declares its logical `uci_schema_version`; tools must not substitute “latest UCI” automatically.

### Checked-in reproducibility artifact

The baseline UCI 2.5 schema-source manifest is
[`schema-sources/uci/2.5/manifest.yaml`](../schema-sources/uci/2.5/manifest.yaml).
It pins UCI tag `v2.5` to immutable revision
`093610b7753944059360d3236770ab446d039556`. The manifest, not this references
page, is authoritative for exact file hashes.

## 4. Public implementation/reference examples

The following repositories are useful for understanding how the architecture can be implemented, but they are not substitutes for the official architecture/standard artifacts.

### AMS GRA Hello World Starter Kit

- <https://github.com/open-arsenal/ams-gra-hello-world-sk-getting-started>

The starter kit demonstrates an AMS GRA mission system with Sleet/LA-CAL, simulated MFA/MEL data, and example skills/services that publish UCI messages. It is especially useful as a practical integration example.

### Build an OMS Service tutorial

- <https://open-arsenal.gitlab.io/ams-gra/hello-world-sk/getting-started/tutorials/1-build-oms-service.html>

The tutorial describes the Service Contract as defining the UCI messages a Service subscribes to/publishes and other integration parameters. Treat it as implementation guidance; use the OMS official D&D set for definitive Service Contract semantics.

### Sleet

- <https://github.com/open-arsenal/ams-gra-hello-world-sk-infra-sleet>

Sleet is useful evidence that topic/message authorization/configuration can be a derived deployment concern. This project does **not** define Sleet configuration as the Service Contract format.

## 5. IETF references used by this specification

- RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels: <https://www.rfc-editor.org/rfc/rfc2119>
- RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words: <https://www.rfc-editor.org/rfc/rfc8174>

## 6. Source-selection policy for future changes

When adding/changing a field because of a claimed AMS GRA/OMS/UCI requirement, contributors should cite sources in this preference order:

1. official public AMS GRA/OMS/UCI artifact;
2. immutable upstream release/tag/commit containing the official artifact;
3. official public repository documentation;
4. public reference implementation/tutorial, clearly identified as non-normative implementation evidence.

A downstream implementation detail should not be promoted into the portable contract merely because one runtime happens to use it.
