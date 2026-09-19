# Task 021 — OMS 2.5 Subsystem Shutdown source evidence

## Authoritative artifact inspected

- Repository: `open-arsenal/oms`
- Revision: `726272bd0390982a759c91a9cf4e13b81c2b510b`
- Artifact:
  `docs_official/14_2_OMSC-INS-003_RevM_ServiceContractInstructions_DandD_v2_5.docx`
- Section/table: 3.2.6, Table 3.2-6 *Subsystem Shutdown Inputs and Outputs*

The DOCX was inspected as OOXML, including `word/document.xml` and
`word/styles.xml`; this conclusion does not rely on a rendered view or an
unofficial Markdown conversion.

## Table-row classification

| Row | OOXML paragraph styles | Color evidence | Classification |
| --- | --- | --- | --- |
| `SubsystemStateCommand` | `TableCenterBoldGreen`, `TableCenterGreen`, `TableLeftAlignGreenBold`, `TableLeftAlignGreen` | `TableCenterGreen` and `TableLeftAlignGreen` explicitly set `w:color/@w:val="00B050"`; the bold variants inherit those styles | removable green guidance/example |
| `SubsystemStateCommandStatus` | `TableCenterBoldGreen`, `TableCenterGreen`, `TableLeftAlignGreenBold`, `TableLeftAlignGreen` | same explicit/inherited `00B050` color | removable green guidance/example |
| `Log_File` | `TableCenterBoldGreen`, `TableCenterGreen`, `TableLeftAlignGreenBold`, `TableLeftAlignGreen` | same explicit/inherited `00B050` color | removable green guidance/example |

The Section 3 template instructions make green guidance/example content
replaceable/removable. Consequently no Table 3.2-6 row is a fixed black source
requirement for the OMS 2.5 machine-readable profile. `Log_File` is excluded
because it is green, not because its LoM is `optional`; LoM is execution/use
semantics and was not treated as permission to omit a fixed row.

## Profile and validation outcome

`Subsystem Shutdown` remains an applicable required Subsystem function but has
no `required_exchanges`. No portable-contract or profile-schema semantics were
changed. No profile rule enforces UCI primitive, topic, operational attribute,
subscription group, Appendix C mapping, response numbers, or Data Transfer
protocol/type/format/sharing metadata.

The removable guidance presents `SubsystemStateCommand` as input, mandatory,
asynchronous, and `SubsystemStateCommandStatus` as output, mandatory,
on-demand, with informative 0.5- and 3-second response values. Section 3.2.6's
status output is the appropriate source when documenting that guidance rather
than the conflicting Table 3.2-3 input direction. Since these rows are green,
none of those shapes or values is an OMS 2.5 profile conformance key.

No public Shutdown example was added: a source-backed example would contain
only removable guidance, and adding `Log_File` would require unsourced portable
Data Transfer metadata. The complete Subsystem fixture retains an empty
Shutdown exchange list and passes ordinary v0.1 and OMS 2.5 profile validation.
