# Task 028 — OMS 2.5 Capability and Capability Status exchange evidence

## Authoritative artifact inspected

- Repository: `open-arsenal/oms`
- Revision: `726272bd0390982a759c91a9cf4e13b81c2b510b`
- Artifact: `docs_official/14_2_OMSC-INS-003_RevM_ServiceContractInstructions_DandD_v2_5.docx`
- Surfaces: 3.3.2.1 through 3.3.2.1.5 and Table 3.3-2

Classification uses `word/document.xml` and `word/styles.xml` from the official
DOCX. Upstream Markdown was navigation only.

## OOXML method and generic prose

`BodyText -> Normal` has no color, so inherited body runs are automatic/black.
`GreenBodyText -> BodyText -> Normal` sets `00B050`. `TableLeftAlignGreen ->
TableLeftAlign -> TableHeaderCenterBold -> Normal` and `TableCenterGreen ->
TableCenter -> TableLeftAlign -> TableHeaderCenterBold -> Normal` set `00B050`.
`TableLeftAlignGreenBold` inherits its color through `TableLeftAlignGreen`.
None of the inspected table runs overrides its paragraph color.

The generic function paragraph (document paragraph 1305) is `BodyText`, with
black `This function publishes`, `Capability`, `CapabilityStatus`, `messages`,
and connecting runs; each `[CapabilityName]` run is explicitly `00B050`.
The Description paragraph (1308) has the same mixed effective formatting:
black `publishes specific`, suffixes, `messages`, and `periodically`, with each
replacement run green. Thus each whole paragraph is **mixed**, not wholly black.
It fixes generic publication of two Capability-relative message families and
fixed generic output behavior; it fixes periodic publication in Description.
It does not fix a literal selector or instantiate an owner/name.

The resulting source classification is **C: mixed generic requirement plus
editable identifier**. The black prose establishes the relationship and the
suffix roles, while green `[CapabilityName]` is replacement material. It must
not become a literal message selector.

## Table 3.3-2 field-level evidence

| Exchange/example | Kind | Selector | Direction | LoM | Timing kind | Numeric timing | Appendix C | MP / DE / Data Exchange Information | OOXML color/style | Generic or example / final decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `ESM_Capability` | green guidance: DE `M` | green guidance: name and information `ESM_Capability` | green guidance: I/O `O` | green guidance: `M` | green guidance: `P` | green example: 1 Hz nominal/max | green guidance: `ESM_Capability` | MP `D`, DE `M`, and information are green guidance | MP/I/O/DE/LoM/P/rates use `TableCenterGreen`; name uses `TableLeftAlignGreenBold`; information/Appendix C use `TableLeftAlignGreen`; all inherit `00B050` with no run override | removable ESM example; no fixed five-field exchange shape |
| `ESM_CapabilityStatus` | green guidance: DE `M` | green guidance: name and information `ESM_CapabilityStatus` | green guidance: I/O `O` | green guidance: `M` | green guidance: `P` | green example: 1 Hz nominal/max | green guidance: `ESM_CapabilityStatus` | MP `S`, DE `M`, and information are green guidance | same effective `00B050` inheritance and no run override | removable ESM example; no fixed five-field exchange shape |

Every matcher-owned field (`kind`, `message`, `direction`, `mandate`, and
`timing_kind`) is green guidance for both rows. MP is separately green and is
UCI corroboration only; DE, Data Exchange Information, numerical timing, and
Appendix C are also green. Numerical rates remain informative and are not
profile-enforced even if later evidence changes their color.

Paragraph 1320 is `GreenBodyText`, inherited `00B050`, with no run override:
“For example, the green text rows below are shown for the ESM Capability.” It
is **green guidance**. Paragraph 1309 independently is entirely green and says
the ESM messages are example messages. Together these explicitly establish
`ESM_Capability` and `ESM_CapabilityStatus` as examples, not generic literal
requirements.

## Workflow and semantic conclusions

The black/green-mixed introductory function prose separately says capability
availability is initially DISABLED (paragraph 1306; only the referenced
Capability Enable/Disable replacement is green). The Workflow section’s own
lead (1327), availability/status statement (1330), and ESM sequence (1333) are
all `GreenBodyText`, effective `00B050`, with no contrary run color. The green
lead does not conceal later black prose: inspection shows these following
substantive paragraphs remain green.

Therefore Workflow’s generic availability initially DISABLED and reporting in
`[CapabilityName]CapabilityStatus` are green authoring guidance. The ESM
workflow publication of `ESM_Capability` and `ESM_CapabilityStatus` is likewise
a green example. It does not alter the partial fixed generic shape found in
function/Description prose:

- **selector family:** Capability-relative `Capability` and `CapabilityStatus`
  roles, with an editable `[CapabilityName]` replacement, not exact names;
- **direction:** fixed prose says the function “publishes” them, sufficient
  evidence for generic output behavior, independently of green I/O cells;
- **timing kind:** Description says they publish “periodically,” sufficient for
  generic periodic behavior, independently of green P cells;
- **kind:** not fully fixed. Calling them messages in this OMS section does not
  establish the v0.1 discriminator `oms_message`; green DE `M` cannot supply it;
- **mandate:** not fixed. Green LoM `M` is example content, and publication is
  not an OMS Level-of-Mandate assertion.

This is useful **partial generic shape** evidence, not a normal profile rule.
No conclusion is drawn from UCI-looking names, and no local verified UCI 2.5
schema bytes were available for optional ESM resolver corroboration.

## Current representability and final decision

Task 026’s boundary remains controlling: v0.1 has no independent Capability
presence/identity/name, function-to-Capability ownership, or multiple-instance
model. The profile DSL requires exact `required_functions[].name` and exact
`required_exchanges[].message`. It cannot safely instantiate “for each
applicable Capability” from this partial family, and must not extract `ESM` or
any other identity from a function/message name.

This is a concrete **Capability-relative selector modeling gap**. A future
model might conceptually express a capability-definition/status message role
and a capability owner reference rather than construct names from strings. That
is illustrative only; no schema, validator, profile DSL, diagnostic, heuristic,
or public fixture is added here.

Accordingly, `profiles/oms/2.5/profile.yaml` is unchanged: no ESM requirement,
no literal `[CapabilityName]` selector, and no template/regex matching. The
partial result would apply to each applicable Capability and Capability Status
function, but v0.1 cannot identify or instantiate such functions without the
missing independent facts. `examples/capability-enable-disable.yaml` is not
changed because it concerns Table 3.3-3 rather than this evidence.
