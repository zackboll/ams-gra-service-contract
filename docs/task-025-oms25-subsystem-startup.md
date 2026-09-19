# Task 025 — OMS 2.5 Subsystem Startup source evidence

## Authoritative artifact inspected

- Repository: `open-arsenal/oms`
- Revision: `726272bd0390982a759c91a9cf4e13b81c2b510b`
- Artifact: `docs_official/14_2_OMSC-INS-003_RevM_ServiceContractInstructions_DandD_v2_5.docx`
- Section/table: 3.2.1, Table 3.2-1 *Subsystem Startup Inputs and Outputs*, and
  3.2.1.5 *Subsystem Startup Workflow and Orchestration*

Classification used `word/document.xml` and `word/styles.xml` from the official
DOCX. The Markdown conversion was navigation only.

## OOXML color method

Each substantive table cell has a paragraph style and no explicit run color.
`TableCenterGreen` and `TableLeftAlignGreen` explicitly set `00B050`;
`TableLeftAlignGreenBold` inherits it from `TableLeftAlignGreen`; and
`TableCenterBoldGreen` inherits it through `GreenCenterBold` and `GreenCenter`.
Their other based-on paths end at `Normal`. Thus the effective color is green
`00B050`, not automatic/black, despite some style names also expressing
alignment or boldness. There are no candidate-cell run overrides.

`GreenBodyText -> BodyText -> Normal` explicitly sets `00B050`. Every relevant
example paragraph and its message-name runs have that paragraph style and no
run override. In contrast, general initialization prose is `BodyText` with
automatic color; it says power starts initialization, CAL is initialized, and a
network connection is needed for message receipt/publication, but establishes
no candidate exchange's five-field shape.

## Table A — Table 3.2-1 field classification

| Exchange | Kind | Selector | Direction | LoM | Periodicity | Non-matched fields | Effective color/style | Universal? | Final decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `FileMetadata` | green `M` | green name | green `I` | green `O` | green `A` | green MP `D`, exchange information `FileMetadata [SOAC-3]`, N/A timings, Appendix C | `TableCenterBoldGreen`/`TableCenterGreen`/`TableLeftAlignGreen`, all `00B050` | no | removable green guidance; not profiled |
| `FileLocation` | green `M` | green name | green `I` | green `O` | green `A` | green MP `D`, exchange information `FileLocation [SOAC-3]`, N/A timings, Appendix C | same effective green styles, no overrides | no | removable green guidance; not profiled |
| `Subsystem_OFP` | green `DT` | green name | green `I` | green `O` | green `A` | green MP `-`, `tftp [Subsystem_OFP, Binary, Exclusive Use]`, N/A timings/Appendix C | same effective green styles, no overrides | no | removable green guidance; no Startup prose makes it an MDF strategy or universal input |
| `SubsystemConfigFile` | green `DT` | green name | green `I` | green `O` | green `A` | green MP `-`, `NFS [Configuration File, Custom Text, Exclusive Use]`, N/A timings/Appendix C | same effective green styles, no overrides | no | removable green guidance; Example 1 discusses configuration metadata about MDF, not direct MDF transfer |
| `MDF` | green `DT` | green name | green `I` | green `O` | green `A` | green MP `-`, `NFS [MDF, Binary, Exclusive Use]`, N/A timings/Appendix C | same effective green styles, no overrides | no | removable green guidance; not equivalent to `SubsystemConfigFile` |

All profile-matched fields are green independently. MP, exchange information,
protocol/type/format/sharing examples, N/A timing values, and Appendix C are
also green non-matched source content. A green non-matched field would not by
itself invalidate fixed matcher fields, but no such fixed fields exist here.
`O` is Optional LoM, not logic permitting omission of a fixed row; row absence
instead follows the independently established green classification.

## Table B — Startup MDF workflow strategies

| Strategy | Relevant exchanges | OOXML prose classification | Fixed/green selection instruction | Universal/alternative/example | Profile representation decision |
| --- | --- | --- | --- | --- | --- |
| Example 1: configuration file learns MDF identification/location | `SubsystemConfigFile` conceptually; no direct `MDF` transfer asserted | green `GreenBodyText`, no overrides; synchronous/asynchronous protocol explanation also green | green: “Keep the one example ... remove the other examples” | removable example guidance | no rule |
| Example 2: external Service pushes MDF information | `FileMetadata` and `FileLocation` | green `GreenBodyText`; each message-name run has no override and inherits green | same green instruction | removable paired example guidance, not a universal pair | no rule |
| Example 3: query learns MDF information | `QueryDataRequest`, `QueryDataRequestStatus` (not Table 3.2-1 rows) | green `GreenBodyText`; both message-name runs inherit green | same green instruction | removable example guidance | no rule; do not add non-table messages |

The NFS/FTP statement (“may connect ... Provide details”), general workflow
instructions, all three examples, and “Modify green text and message sequences
above as needed” are green guidance. The keep-one/remove-others instruction is
also green, so the source does **not** prove a fixed requirement to select
exactly one machine-checkable strategy. It is classification A: removable green
example guidance, not a normative alternative-set requirement.

## Repository decision

There are no universal Startup exchange rules: no row has five fixed,
unambiguous matcher-owned fields, and no workflow prose changes that result.
Consequently `Subsystem Startup` remains fixed-applicable with no
`required_exchanges`; the complete applicable Subsystem fixture correctly keeps
`exchanges: []`. The tests explicitly prevent every Table 3.2-1 row, including
the Example 2 pair, from becoming an accidental universal minimum, and show
that an additional guidance exchange remains allowed.

No fixed conditional/alternative exchange set and no fixed-source conflict
emerge. Therefore the profile has no demonstrated alternative-set modeling gap,
and neither profile schema nor validator is changed. `Subsystem_OFP` remains
independently removable guidance rather than an inferred MDF alternative. No
real UCI resolver run was needed because no OMS-message Startup row became a
profile minimum.
