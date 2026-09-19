# Task 030 — OMS 2.5 Capability Operations exchange evidence

## Authoritative artifact inspected

- Repository: `open-arsenal/oms`
- Revision: `726272bd0390982a759c91a9cf4e13b81c2b510b`
- Artifact: `docs_official/14_2_OMSC-INS-003_RevM_ServiceContractInstructions_DandD_v2_5.docx`
- Surfaces: 3.3.2.3 through 3.3.2.3.5 and Table 3.3-4

Classification uses `word/document.xml` and `word/styles.xml` from the official
DOCX. Upstream Markdown was navigation only.

## OOXML method and generic content

`BodyText -> Normal` and the relevant heading paths have no color, so an
unoverridden run is automatic/black. `GreenBodyText -> BodyText -> Normal` sets
`00B050`. `TableCenterGreen`, `TableCenterBoldGreen`, `TableLeftAlignGreen`, and
`TableLeftAlignGreenBold` resolve to `00B050` through their paragraph-style
inheritance. Every inspected Table 3.3-4 candidate run inherits that green; none
has a contrary run-level color override.

The 3.3.2.3 heading and Description are **mixed** at run level: each
`[CapabilityName]` run explicitly sets `00B050`, while ` Capability Operations`
and the Description's “function that performs a Capability” prose are
automatic/black. That fixed generic wording establishes only the generic role of
an Operations function. It neither selects an exchange family nor supplies a
Capability identity, ownership, or universal I/O shape. The placeholder is
editable replacement material, not a literal selector.

The Preconditions prose is fixed black/automatic: a Subsystem must be in
`OPERATE` or a Service in `NORMAL`, and the Capability is enabled as defined in
3.3.2.2. These are behavioral/precondition facts, not exchange requirements.
The Reporting Interval paragraph is green guidance telling authors to provide a
reporting interval where applicable; it establishes no generic exchange timing
and cannot turn Table P=`A` into fixed asynchronous evidence.

## Table 3.3-4 groups and field-level classification

The instruction before the first group is `GreenBodyText`, effective `00B050`,
without a run override: “the first 2 green text rows below may apply to an ESM
Capability.” It is **green guidance**, and expressly makes `Entity` and
`SignalReport` ESM-domain examples rather than universal Operations rows. The
corresponding instruction for “the last 3 green text rows” is likewise
`GreenBodyText`, effective `00B050`, without an override: it says they may apply
to a PO/POST Capability. It is **green guidance**, expressly separating
`ProductMetadata`, `ProductLocation`, and `ImageFile` as PO/POST-domain examples.

| Exchange | Domain/example group | Kind | Selector | Direction | LoM | Timing kind | Non-matched metadata | Workflow evidence | OOXML classification / universal? | Final decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Entity` | ESM first-two example | green DE=`M`; portable kind not fixed | green name | green I/O=`O` | green `M` | green P=`A` | green MP=`D`, Information/Appendix C `Entity`; numeric `N/A` | green ESM AUTO/MANUAL example only | all matched fields/metadata green; domain-specific, not universal | no profile rule |
| `SignalReport` | ESM first-two example | green DE=`M`; portable kind not fixed | green name | green I/O=`O` | green `M` | green P=`A` | green MP=`D`, Information/Appendix C `SignalReport`; numeric `N/A` | green ESM AUTO/MANUAL example only | all matched fields/metadata green; domain-specific, not universal | no profile rule |
| `ProductMetadata` | PO/POST last-three example | green DE=`M`; portable kind not fixed | green name | green I/O=`O` | green `M` | green P=`A` | green MP=`D`, Information/Appendix C `ProductMetadata`; numeric `N/A` | green Passive Optical image example | all matched fields/metadata green; domain-specific, not universal | no profile rule |
| `ProductLocation` | PO/POST last-three example | green DE=`M`; portable kind not fixed | green name | green I/O=`O` | green `M` | green P=`A` | green MP=`D`, Information/Appendix C `ProductLocation`; numeric `N/A` | green Passive Optical image example | all matched fields/metadata green; domain-specific, not universal | no profile rule |
| `ImageFile` | PO/POST last-three example | green DE=`DT`; `data_transfer` not fixed | green name | green I/O=`O` | green `M` | green P=`A` | green protocol `NFS`; type `Image`; format `JPEG`; sharing `Shared Use`; Appendix C `TBD`; MP `-`; numeric `N/A` | green Passive Optical retrieval example | all matched fields/metadata green; domain-specific, not universal | no profile rule or Data Transfer-detail match |

Thus `kind`, selector, direction, mandate, and timing kind are green guidance
for every row. MP, DE, Data Exchange Information, protocol, type, format,
sharing pattern, numerical timing, and Appendix C are separately green example
values. The table's black abbreviation key defines column vocabulary, not these
row values. Neither “message,” operational importance, nor event narrative is
used to infer `oms_message`, mandatory, or asynchronous.

## Workflow classification

The Workflow lead, “Modify or add the following green text and message sequences
as needed,” is `GreenBodyText`, effective `00B050`: green guidance. Subsequent
paragraphs were independently inspected rather than inheriting that conclusion.

- **ESM AUTO (Figure 3.3.2-4):** its narrative, `ESM_Capability`,
  `ESM_CapabilityStatus`, `ESM_Activity`, `SignalReport`, and `Entity` runs are
  green. It is an ESM operational example; no workflow-only message is added.
- **ESM MANUAL (Figure 3.3.2-5):** its narrative and `ESM_Capability`,
  `ESM_CapabilityStatus`, `ESM_Activity`, `ESM_Command`, `ESM_CommandStatus`,
  `SignalReport`, `Entity`, and `PulseData` references are green. It corroborates
  examples only, not generic Operations semantics.
- **Passive Optical (Figure 3.3.2-6):** its narrative and `PO_Capability`,
  `PO_CapabilityStatus`, `PO_Command`, `PO_CommandStatus`, `PO_Activity`,
  `ProductMetadata`, `ProductLocation`, and data-transfer/image-retrieval text
  are green. It is a PO image example, not a PO/POST rule for every Capability.

The Passive Optical narrative relates metadata, location, and image retrieval
only within that green example. It establishes no fixed generic dependency or
required grouped relationship among `ProductMetadata`, `ProductLocation`, and
`ImageFile`/Data Transfer.

## Conclusions and representability

There is **no fixed universal Capability Operations exchange shape** in the
inspected evidence. This does not make Operations unimportant: the template
shows that its I/O is Capability/domain-specific. ESM-specific semantics are
the removable `Entity`/`SignalReport` examples; PO/POST-specific semantics are
the removable `ProductMetadata`/`ProductLocation`/`ImageFile` examples.

The existing profile uses exact universal `required_functions[].name` and
`required_exchanges[]`. It cannot express Capability presence/identity, function
ownership, multiple Capability instances, Capability-relative exchange roles, or
domain-conditional exchange sets. Names must not reconstruct those facts. No
ESM/PO/POST literal rule, placeholder, prefix/suffix/regex heuristic, profile
rule, schema, validator, diagnostic, or public Capability Operations example is
added. The local UCI 2.5 directory has only its verified manifest and no schema
bytes, so optional resolver corroboration was skipped.

The focused regression parametrizes both ordinary complete Service and
Subsystem profile fixtures across all five Table 3.3-4 selectors, searching
`message` for the OMS-message examples and `name` for `ImageFile`. It locks in
that these domain examples are not universal OMS 2.5 profile requirements.
