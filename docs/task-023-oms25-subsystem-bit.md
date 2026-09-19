# Task 023 — OMS 2.5 Subsystem BIT source evidence

## Authoritative artifact inspected

- Repository: `open-arsenal/oms`
- Revision: `726272bd0390982a759c91a9cf4e13b81c2b510b`
- Artifact: `docs_official/14_2_OMSC-INS-003_RevM_ServiceContractInstructions_DandD_v2_5.docx`
- Section/table: 3.2.4, Table 3.2-4 *Subsystem BIT Inputs and Outputs*

This assessment inspected `word/document.xml` and `word/styles.xml` from the official DOCX package. The unofficial Markdown conversion was used only to find the section; it was not classification evidence.

## OOXML color method

There are no explicit run-color overrides in the seven substantive table rows. Their effective color is inherited as follows:

- `TableCenterBoldGreen` -> `GreenCenterBold` -> `GreenCenter` (whose `w:rPr/w:color/@w:val` is `00B050`) -> `Center` -> `Normal`;
- `TableCenterGreen` has its own `00B050`, then inherits through `TableCenter` -> `TableLeftAlign` -> `TableHeaderCenterBold` -> `Normal`;
- `TableLeftAlignGreen` has its own `00B050`, and `TableLeftAlignGreenBold` inherits it from that style.

Thus style names were not used as the conclusion: every candidate cell resolves to green `00B050`. The black/automatic header and abbreviation cells are not candidate exchange content.

## Field-level source facts and profile decision

`M`/`DT`, the data-exchange name, I/O, LoM, and P would respectively map to the profile matcher's kind, selector, direction, mandate, and timing kind. In every row those source cells are green guidance. A green non-matched cell is not independently disqualifying, but here every matched field is green.

| Exchange | Kind | Selector | Direction | LoM | Periodicity | Non-matched fields | Fixed prose / conflict | Repository profile decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `SubsystemBIT_Status` | green `M` | green name | green `O` | green `O` | green `P` | green MP `S`, exchange info, `1 Hz` nominal/max, Appendix C | message-specific workflow is green; no fixed shape or conflict | unprofiled |
| `SubsystemBIT_Configuration` | green `M` | green name | green `O` | green `O` | green `P` | green MP `D`, exchange info, `1 Hz` nominal/max, Appendix C | green workflow only | unprofiled |
| `SubsystemStateCommand` | green `M` | green name | green `I` | green `O` | green `A` | green MP `C`, exchange info, N/A timing, Appendix C | green receipt/status workflow only; separate from Table 3.2-3 | unprofiled |
| `SubsystemStateCommandStatus` | green `M` | green name | green `O` | green `O` | green `OD` | green MP `CS`, exchange info, `0.5 sec`/`3 sec`, Appendix C | green response workflow only | unprofiled |
| `SubsystemBIT_Command` | green `M` | green name | green `I` | green `O` | green `A` | green MP `C`, exchange info, N/A timing, Appendix C | green receipt/status workflow only | unprofiled |
| `SubsystemBIT_CommandStatus` | green `M` | green name | green `O` | green `O` | green `OD` | green MP `CS`, exchange info, `0.5 sec`/`3 sec`, Appendix C | green response workflow only | unprofiled |
| `Log_File` | green `DT` | green name | green `O` | green `O` | green `A` | green MP `-`, exchange info `DT`, N/A timing/Appendix C | not discussed in BIT workflow prose | unprofiled |

No candidate has five fixed, unambiguous profile-match fields. There is no fixed-source conflict to resolve; none of the green guidance becomes a profile rule. `SubsystemStateCommand` here is deliberately not inherited from the separate State Command Processing table.

## Workflow prose classification

The generic section purpose and preconditions are `BodyText` -> `Normal` with automatic color, but they do not state a candidate's five-field exchange shape. The message-specific statements for `SubsystemBIT_Configuration`, `SubsystemBIT_Status`, `SubsystemStateCommand`, `SubsystemStateCommandStatus`, `SubsystemBIT_Command`, and `SubsystemBIT_CommandStatus` are all `GreenBodyText` -> `BodyText` -> `Normal`. `GreenBodyText` explicitly sets `00B050`; its runs have no override. The lead instruction itself is green: “Use or modify the following green text and message sequences as needed.” `Log_File` has no BIT-specific workflow prose. Consequently this prose is guidance/corroboration only, not a fixed rule.

## Scope outcome

`Subsystem Built-In Test (BIT)` remains required inventory and retains `allowed_applicability: [applicable, not_applicable]`, but has no `required_exchanges`. An applicable complete fixture therefore contains zero BIT exchanges; additional program-specific exchanges remain allowed.

LoM `O` is the source's Optional level-of-mandate value, not permission to omit a fixed row. These rows are unprofiled because their matched cells are green. Numeric `1 Hz`, `0.5 sec`, and `3 sec` values are source information only and are not profile keys. No public BIT example was added because it would present removable guidance as normative. No real UCI resolver check was run: no BIT exchange became a source-backed profile minimum.
