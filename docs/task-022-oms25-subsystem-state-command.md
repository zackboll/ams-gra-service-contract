# Task 022 — OMS 2.5 Subsystem State Command Processing source evidence

## Authoritative artifact inspected

- Repository: `open-arsenal/oms`
- Revision: `726272bd0390982a759c91a9cf4e13b81c2b510b`
- Artifact:
  `docs_official/14_2_OMSC-INS-003_RevM_ServiceContractInstructions_DandD_v2_5.docx`
- Section/table: 3.2.3, Table 3.2-3 *Subsystem State Command Processing Inputs
  and Outputs*

This assessment inspected `word/document.xml` and `word/styles.xml` in the
official DOCX package. Unofficial Markdown was not used for classification.

## Source facts: Table 3.2-3 OOXML evidence

The table immediately following the body caption `Table 3.2-3 Subsystem State
Command Processing Inputs and Outputs` was inspected. Neither substantive row
has an explicit run color.

| Row | Fixed/automatic cells and style inheritance | Green cells and color evidence | Classification |
| --- | --- | --- | --- |
| `SubsystemStateCommand` | `C`: `TableCenterBold` -> `TableCenter` -> `TableLeftAlign` -> `TableHeaderCenterBold` -> `Normal`; `I`, `M`, LoM `M`, and `A`: `TableCenter` -> `TableLeftAlign` -> `TableHeaderCenterBold` -> `Normal`; name: `TableLeftAlignBold` -> `TableLeftAlign` -> `TableHeaderCenterBold` -> `Normal`; information: `TableLeftAlign` -> `TableHeaderCenterBold` -> `Normal`. These resolve to automatic/no `w:color`, with no explicit run color. | Appendix C mapping: `TableLeftAlignGreen`, explicitly `w:color/@w:val="00B050"`. | mixed/ambiguous |
| `SubsystemStateCommandStatus` | `CS`: `TableCenterBold` -> `TableCenter` -> `TableLeftAlign` -> `TableHeaderCenterBold` -> `Normal`; `I`, `M`, LoM `M`, and `OD`: `TableCenter` -> `TableLeftAlign` -> `TableHeaderCenterBold` -> `Normal`; name: `TableLeftAlignBold` -> `TableLeftAlign` -> `TableHeaderCenterBold` -> `Normal`; information: `TableLeftAlign` -> `TableHeaderCenterBold` -> `Normal`. These resolve to automatic/no `w:color`, with no explicit run color. | nominal `0.5 sec`: `TableCenterGreen`, explicitly `00B050`; maximum `3 sec`: `TableCenterGreen`, explicitly `00B050`; Appendix C mapping: `TableLeftAlignGreen`, explicitly `00B050`. | mixed/ambiguous |

Thus the table's command shape is fixed black/automatic content except for its
green Appendix C mapping; the status shape is fixed black/automatic content
except for its green timing and Appendix C cells. The rows cannot be classified
as wholly fixed black content or wholly removable green guidance.

## Source facts: workflow OOXML evidence

The relevant Section 3.2.3 workflow paragraph states: "upon receipt of a
`SubsystemStateCommand`" and "The Subsystem responds with
`SubsystemStateCommandStatus`". Its paragraph style is `BodyText` -> `Normal`,
which resolves to automatic/no `w:color`; its runs have no explicit color. The
command-receipt and status-response statements are therefore black/fixed text,
not green guidance/example text, and are not mixed.

## Analysis and repository design decision

The fixed black table shape presents both `SubsystemStateCommand` and
`SubsystemStateCommandStatus` with I/O `I`. The fixed black workflow prose
requires receipt of the command and says the Subsystem responds with the
status. The latter conflicts with enforcing the table's status `input` as an
exchange direction. The DOCX does not establish a single unambiguous fixed
status direction, and the green timing/Appendix C cells do not resolve that
conflict.

Both rows remain mixed at the complete-row level, but that classification does
not make every field unusable for the deliberately narrow profile matcher. For
`SubsystemStateCommand`, every matched field is fixed black/automatic: OMS
Message, `SubsystemStateCommand`, input, mandatory, and asynchronous. The only
green command-row field is Appendix C mapping, which the profile does not
match. Fixed workflow prose independently corroborates command input by saying
the Subsystem receives the command. The profile therefore enforces that command
minimum with traceability to `3.2.3.4 / Table 3.2-3 /
SubsystemStateCommand`.

`SubsystemStateCommandStatus` remains unprofiled. Its fixed table direction is
input while the fixed workflow prose says the Subsystem responds with it. That
is a genuine fixed-source conflict, so the profile does not select input or
output from message naming or intuition. Its green 0.5/3-second timing and
Appendix C values remain unmatched.

`allowed_applicability: [applicable, not_applicable]` is unchanged. The profile
enforces this command rule when the function is applicable. When a requirement
uses `allowed_applicability` and an actual `not_applicable` function is allowed,
the validator skips only that requirement's `required_exchanges`; portable
validation still requires the rationale and zero exchanges. Fixed-applicable
requirements do not use this gate.

No public State Command Processing example was added: the complete profile test
fixture demonstrates the fixed command minimum without selecting a status
direction despite the unresolved conflict.
