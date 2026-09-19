# Task 027 — OMS 2.5 Position Information exchange evidence

## Authoritative artifact inspected

- Repository: `open-arsenal/oms`
- Revision: `726272bd0390982a759c91a9cf4e13b81c2b510b`
- Artifact: `docs_official/14_2_OMSC-INS-003_RevM_ServiceContractInstructions_DandD_v2_5.docx`
- Surfaces: Sections 3.3.1.1, 3.3.1.4, Table 3.3-1, and Section 3.3.1.5

The upstream Markdown was navigation only. Classification below comes from
`word/document.xml` and `word/styles.xml` in the official DOCX.

## OOXML color method

`Normal` has no color. `BodyText -> Normal`, `TableHeaderCenterBold -> Normal`,
`TableLeftAlign -> TableHeaderCenterBold`, and `TableCenter -> TableLeftAlign`
also have no color, so absent a run override their effective color is
automatic/black. `GreenBodyText -> BodyText` explicitly sets `00B050`.
`TableLeftAlignGreen -> TableLeftAlign` and
`TableCenterGreen -> TableCenter -> TableLeftAlign` explicitly set `00B050`.
`TableLeftAlignGreenBold -> TableLeftAlignGreen` inherits that green color.

The inspected paragraphs and candidate table runs have no explicit run color.
Thus style inheritance, rather than style names alone, determines the effective
colors reported here. No candidate run overrides its paragraph style.

## A. Table 3.3-1 field-level evidence

Both candidate rows have green paragraph styles for MP, I/O, DE, name, Data
Exchange Information, LoM, periodicity, and numerical timing. Appendix C is
black `TableLeftAlign` in each row. The five matcher-owned fields are `kind`,
`message`, `direction`, `mandate`, and `timing_kind`; `DE` is the source for
kind, data-exchange name/information identify the message, I/O supplies
direction, LoM supplies mandate, and P supplies timing kind.

| Exchange | Kind | Selector | Direction | LoM | Timing kind | Numeric timing | Appendix C | Effective style/color | Final field-shape decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `PositionReport` | green guidance: DE `M`, `TableCenterGreen`, inherited `00B050` | green guidance: name `TableLeftAlignGreenBold` and information `TableLeftAlignGreen`, inherited `00B050` | green guidance: I/O `I`, `TableCenterGreen`, inherited `00B050` | green guidance: `M`, `TableCenterGreen`, inherited `00B050` | green guidance: P, `TableCenterGreen`, inherited `00B050` | green guidance: 1 Hz nominal/max, `TableCenterGreen`, inherited `00B050` | fixed black/automatic: `TableLeftAlign` | no run overrides; matched cells all effective `00B050` | removable green example row; no fixed five-field exchange shape |
| `PositionReportDetailed` | green guidance: DE `M`, `TableCenterGreen`, inherited `00B050` | green guidance: name `TableLeftAlignGreenBold` and information `TableLeftAlignGreen`, inherited `00B050` | green guidance: I/O `I`, `TableCenterGreen`, inherited `00B050` | green guidance: `M`, `TableCenterGreen`, inherited `00B050` | green guidance: P, `TableCenterGreen`, inherited `00B050` | green guidance: 50 Hz nominal/max, `TableCenterGreen`, inherited `00B050` | fixed black/automatic: `TableLeftAlign` | no run overrides; matched cells all effective `00B050` | removable green example row; no fixed five-field exchange shape |

The black Appendix C cells do not repair the green matcher-owned fields and are
not matched by the current profile. MP is separately green guidance for both
rows; it is UCI corroboration only, not a profile field. Numerical rates remain
informative under repository policy and are not profile-enforced.

## B. Row-selection instruction

Paragraph 2411 is `GreenBodyText`, inherits `00B050`, and has no run override:
“For example, the green text rows below show both position report messages.
Change green text to black text for the applicable row(s) being used and remove
any green text row not being used.” It is **green guidance**, not fixed black
contract content.

It explains that a contract author may retain applicable rows, blacken them, and
remove unused rows. Because the instruction itself is removable guidance and
says only “applicable row(s),” it does not establish an authoritative fixed
zero/one/both cardinality rule.

## C. Fixed Description prose

Paragraph 2401 is `BodyText -> Normal`, automatic/black, with no run override.
Its ordinary text, `PositionReport` run, `or` run, and `PositionReportDetailed`
run are all black: “This section describes the Position Information Processing
function to subscribe to periodic PositionReport or PositionReportDetailed
messages.” Therefore `subscribe`, `periodic`, and `or` are fixed source wording.

This independently establishes a fixed conceptual subscription to periodic
position-report messages and names the two conceptual alternatives. It does not
unambiguously map `subscribe` to the profile's exchange `direction: input`:
subscription is an interaction role, whereas the profile direction field is
defined from the table's I/O column. Nor does prose alone establish all of the
kind, mandate, and timing fields required for a profile shape. `periodic` can
corroborate timing-kind intent, but cannot convert its green table cell into a
fixed matcher field.

## D. Fixed Workflow prose

Paragraph 2453 is `BodyText -> Normal`, automatic/black, without run overrides.
“Upon receipt of a PositionReport or PositionReportDetailed message, the
Subsystem or Service retains the position information for use by the Capability”
is fixed; both message-name runs, `receipt`, and `or` are black.

Receipt is fixed corroboration that either named message is incoming to the
Subsystem or Service, and is consistent with `direction: input` if a particular
applicable exchange is authored. It also corroborates the conceptual message
alternatives. It does not fix exchange mandate, kind, timing kind, or whether
one versus both messages must be present.

## E. Green example workflow

Paragraph 2456 (“Use or modify the following green text and message sequences
as needed...”) and paragraph 2457 (the lead and both examples) are
`GreenBodyText`, inherited `00B050`, with no run overrides. Example 1 describes
a Service subscribing to `PositionReport`; Example 2 describes a Subsystem
subscribing to `PositionReportDetailed`. They are independently removable green
examples, not fixed rules. They must not be merged with the fixed workflow
prose.

## F. Alternative/cardinality analysis

**Authoritative source fact:** fixed black Description and Workflow prose use
`or` between the two message names; green table instructions say “applicable
row(s)” and permit removal of unused green rows. The all-green candidate rows
are removable examples.

**Repository conclusion:** the best supported classification is **E: the source
establishes a conceptual alternative but not a machine-checkable cardinality**.
The source does not say exactly one, and the green instruction cannot establish
one-or-both as fixed. Consequently neither both-required, exactly-one,
one-or-both, nor neither-only-examples is an authoritative fixed exchange rule.

## G. Mandate and function conditionality

The `M` LoM cells are green for both rows. No fixed prose independently states
that either individual exchange is mandatory. The black conceptual need for
position information does not make each exchange individually mandatory.

Task 026 established that Section 3.3 applies when a Service or Subsystem
provides a Capability, and Position Information Processing is conditional on a
Capability's position dependency; v0.1 lacks independent facts for those
conditions, Capability identity, and function ownership. Thus nothing here is
universal for every Service or Subsystem.

## H. Current profile representability and final decision

The current DSL can express a fixed exact required function, its fixed
applicability/allowed applicability, and a list of required exchanges (which
means all listed shapes). It cannot express an optional-if-present function
rule, condition a function rule on independent Capability facts, or express
one-of/at-least-one-of exchange groups.

Even if later source work establishes fixed exchange/cardinality semantics,
v0.1 has a **conditional-function exchange validation gap**: it cannot safely
attach them because Position Information Processing itself is conditional. If a
fixed alternative set is later demonstrated, there is also an
**alternative-exchange modeling gap**: listing both exchanges would incorrectly
turn OR into AND.

No `required_functions` or `required_exchanges` entry is added to
`profiles/oms/2.5/profile.yaml`. No portable schema, profile schema, validator,
or diagnostic changes are made. This is not an assertion that position reporting
is never required; it preserves the source boundary and avoids an accidental
component-wide requirement.

## I. Optional UCI resolver corroboration

The repository has `schema-sources/uci/2.5/manifest.yaml`, but no verified local
UCI 2.5 schema bytes from which to resolve `PositionReport` or
`PositionReportDetailed`. Resolver identity was therefore not attempted and did
not influence this classification.
