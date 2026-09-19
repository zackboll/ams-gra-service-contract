# Task 024 — OMS 2.5 Subsystem Calibration source evidence

## Authoritative artifact inspected

- Repository: `open-arsenal/oms`
- Revision: `726272bd0390982a759c91a9cf4e13b81c2b510b`
- Artifact: `docs_official/14_2_OMSC-INS-003_RevM_ServiceContractInstructions_DandD_v2_5.docx`
- Section/table: 3.2.5, Table 3.2-5 *Subsystem Calibration Inputs and Outputs*

Classification used `word/document.xml` and `word/styles.xml` from the official
DOCX. The Markdown conversion was not classification evidence.

## OOXML color method

No candidate cell or message-specific workflow run has an explicit run-level
color override. `TableCenterGreen` explicitly resolves to `00B050` through
`TableCenter -> TableLeftAlign -> TableHeaderCenterBold -> Normal`;
`TableLeftAlignGreen` explicitly resolves to `00B050`; and
`TableLeftAlignGreenBold` inherits it through `TableLeftAlignGreen`.
`GreenBodyText -> BodyText -> Normal` explicitly resolves to `00B050`.
Consequently the field classifications below are based on effective color, not
style names.

## Source facts: field-level Table 3.2-5 evidence

Every substantive candidate cell below is green guidance (`00B050`): MP uses
`TableCenterGreen`; I/O, DE, LoM, P, and numeric timing use
`TableCenterGreen`; names use `TableLeftAlignGreenBold`; exchange information
and Appendix C use `TableLeftAlignGreen`. Thus every matcher-owned field is
green. `O` in LoM is a green source value for Optional level of mandate, not a
conclusion that a completed-contract row may be absent.

| Exchange | Kind | Selector | Direction | LoM | Timing kind | Non-matched fields | Fixed workflow evidence | Conflict | Repository decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `SubsystemCalibrationStatus` | green `M` | green name | green `O` | green `O` | green `P` | green MP `S`, exchange info, `1 Hz`/`1 Hz`, Appendix C | green periodic/status-result statements | none fixed | unprofiled |
| `SubsystemCalibrationConfiguration` | green `M` | green name | green `O` | green `O` | green `P` | green MP `D`, exchange info, `1 Hz`/`1 Hz`, Appendix C | green advertisement statements | none fixed | unprofiled |
| `SubsystemStateCommand` | green `M` | green name | green `I` | green `O` | green `A` | green MP `C`, exchange info, Appendix C | green CALIBRATION receipt statements | none fixed | unprofiled; independently classified from Table 3.2-3 |
| `SubsystemStateCommandStatus` | green `M` | green name | green `O` | green `O` | green `OD` | green MP `CS`, exchange info, `0.5 sec`/`3 sec`, Appendix C | green response statements | none fixed | unprofiled |
| `SubsystemCalibrationCommand` | green `M` | green name | green `I` | green `O` | green `A` | green MP `C`, exchange info, Appendix C | green receipt statements | none fixed | unprofiled |
| `SubsystemCalibrationCommandStatus` | green `M` | green name | green `O` | green `O` | green `OD` | green MP `CS`, exchange info, `0.5 sec`/`3 sec`, Appendix C | green response statements | none fixed | unprofiled |
| `Log_File` | green `DT` | green name | green `O` | green `O` | green `A` | green MP `-`, data-transfer exchange information, Appendix C | not discussed | none fixed | unprofiled |

## Workflow prose classification

The lead instruction and all message-specific statements are `GreenBodyText`
with effective `00B050`, including the statements that a Subsystem may advertise
`SubsystemCalibrationConfiguration`, periodically publishes/reports
`SubsystemCalibrationStatus`, receives `SubsystemStateCommand` with
`CommandedState=CALIBRATION`, responds with `SubsystemStateCommandStatus`,
receives `SubsystemCalibrationCommand`, responds with
`SubsystemCalibrationCommandStatus`, and reports test results in
`SubsystemCalibrationStatus`. They are green guidance, not fixed corroboration.
`Log_File` has no Calibration-specific workflow statement. No fixed-source
conflict exists because no candidate shape has fixed table or workflow fields.

## Repository design decision

No `required_exchanges` are added under **Subsystem Calibration**. The profile
model requires all five matcher-owned fields to be fixed and unambiguous; each
candidate has all five fields as green guidance. This is not an inference from
the Markdown table and does not inherit the State Command Processing rule.

Calibration remains conditional with
`allowed_applicability: [applicable, not_applicable]`. Applicable contracts have
zero source-backed Calibration minimum exchanges; additional local exchanges are
permitted. A permitted `not_applicable` Calibration function skips that
function's profile rules, while portable validation still requires a rationale
and zero exchanges. Numeric `1 Hz`, `0.5 sec`, and `3 sec` values remain
informative source facts and are not profile keys. No public Calibration example
was added because it would risk presenting removable guidance as mandatory. No
real UCI resolver run was needed because no Calibration message became a profile
minimum.
