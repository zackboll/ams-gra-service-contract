# Task 029 — OMS 2.5 Capability Enable/Disable exchange evidence

## Authoritative artifact inspected

- Repository: `open-arsenal/oms`
- Revision: `726272bd0390982a759c91a9cf4e13b81c2b510b`
- Artifact: `docs_official/14_2_OMSC-INS-003_RevM_ServiceContractInstructions_DandD_v2_5.docx`
- Surfaces: 3.3.2.2 through 3.3.2.2.5 and Table 3.3-3

Classification uses `word/document.xml` and `word/styles.xml` from the official
DOCX. Upstream Markdown was navigation only.

## OOXML method and generic prose

`BodyText -> Normal` has no color, so inherited body runs are automatic/black.
`GreenBodyText -> BodyText -> Normal` sets `00B050`. `TableLeftAlignGreen ->
TableLeftAlign -> TableHeaderCenterBold -> Normal` and `TableCenterGreen ->
TableCenter -> TableLeftAlign -> TableHeaderCenterBold -> Normal` set `00B050`.
`TableLeftAlignGreenBold` inherits through `TableLeftAlignGreen`; the MP style
`TableCenterBoldGreen` is likewise green. None of the inspected table runs has a
run-level color override. Classification is at run granularity, not whole
paragraph granularity.

The function heading (paragraph 1347) is mixed: the `[CapabilityName]` run is
explicit `00B050`; ` Capability Enable/Disable` is automatic/black. The black
heading establishes the generic function role, while the green replacement is
editable and does not establish a literal owner/name.

Description paragraph 1351 is `BodyText` and mixed at run level. Each
`[CapabilityName]` replacement is explicitly green. `SettingsCommand`,
`SettingsCommandStatus`, `subscribes`, `publishes`, `response`, and `messages`
are automatic/black. Consequently the fixed suffix/behavior text establishes a
Capability-relative command/status family, while the owner/name portion remains
editable. This is conclusion **C: mixed generic requirement plus editable
Capability identifier**, not literal selectors and not name construction.

The fixed black verbs establish conceptual direction independently of green I/O
cells: subscription to `SettingsCommand` is generic **input** behavior and
publication of `SettingsCommandStatus` is generic **output** behavior. Fixed
black `response messages` establishes the conceptual relationship
`SettingsCommand -> SettingsCommandStatus`. It is behavioral evidence only; it
does not establish Periodicity `OD` or other timing discriminator.

## Reporting Interval

Paragraph 1357 is `BodyText`, automatic/black, and says: “This is not
applicable for this function.” It is fixed content. It supplies no command/status
Periodicity evidence: Reporting Interval N/A is distinct from Table 3.3-3's
Periodicity column.

## Table 3.3-3 field-level evidence

| Exchange/example | Kind | Selector | Direction | LoM | Timing kind | Response relation | Numeric timing | MP / DE / Data Exchange Information / Appendix C | OOXML effective color | Generic or example / final decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `ESM_SettingsCommand` | green guidance: DE `M`; portable kind not fixed | green guidance: name/information | green guidance: I/O `I`; fixed generic prose separately supports conceptual input | green guidance: `M`; mandate not fixed | green guidance: `A`; no fixed asynchronous evidence | fixed generic prose only, not this literal row | green `N/A`, informative only | MP `C`, DE `M`, information, and Appendix C are green guidance | `TableCenterBoldGreen`, `TableCenterGreen`, `TableLeftAlignGreenBold`, and `TableLeftAlignGreen` inherit `00B050`; no run override | removable ESM example; no complete profile shape |
| `ESM_SettingsCommandStatus` | green guidance: DE `M`; portable kind not fixed | green guidance: name/information | green guidance: I/O `O`; fixed generic prose separately supports conceptual output | green guidance: `M`; mandate not fixed | green guidance: `OD`; no fixed on-demand evidence | fixed generic prose only, not this literal row | green `TBD` nominal/max; no numeric value is fixed or encoded | MP `CS`, DE `M`, information, and Appendix C are green guidance | same inherited `00B050`, no run override | removable ESM example; no complete profile shape |

Thus each of the five matcher-owned fields (`kind`, `message`, `direction`,
`mandate`, and `timing_kind`) is green guidance in each table row. MP, Data
Exchange Information, numerical response timing, and Appendix C are separately
green. `TBD` is neither a fixed numeric response bound nor evidence for `OD`.
The black abbreviation key explains what values mean; it does not change the
green cells into fixed values.

Paragraph 1362 is `GreenBodyText`, inherited `00B050`, with no run override:
“For example, the green text rows below are shown for the ESM Capability.” It is
**green guidance**. Paragraph 1352 is also wholly green and expressly calls the
two ESM messages examples. The literal ESM rows are removable template examples,
not concrete universal OMS requirements.

## Workflow and examples

The workflow lead (paragraph 1370), “Modify or add the following green text and
message sequences as needed...”, is `GreenBodyText`, inherited `00B050`, and is
green guidance. It does not color-classify later paragraphs by itself.

Generic workflow paragraph 1371 (“A Subsystem or Service may receive...”) is
wholly `GreenBodyText`, inherited `00B050`, including its
`[CapabilityName]SettingsCommand`, `SettingsCommandStatus`, receive/respond,
and message runs; it is green guidance, not fixed corroboration. The later
generic occurrences before the ESM examples (paragraphs 1372–1373) are likewise
green guidance. They illustrate the same selector family and response sequence,
but cannot elevate it to a mandate or establish `A`/`OD`; the fixed partial
shape comes from the mixed Description instead.

The Figure 3.3.2-2 enable narrative (paragraph 1374) and caption (1376) are
green styles. Its `ESM_SettingsCommand` and `ESM_SettingsCommandStatus` runs
inherit green from `GreenBodyText`; it is entirely an ESM example sequence and
does not create universal requirements. The Figure 3.3.2-3 disable narrative
(paragraph 1377) and caption (1379) are likewise green; both ESM names and the
enable/disable scenario prose are example-only.

## Semantic and profile conclusions

**Partial generic shape:** a Capability-relative `SettingsCommand` family has
conceptual input behavior; a Capability-relative `SettingsCommandStatus` family
has conceptual output behavior and is a response to the command. The fixed
source does **not** establish portable `kind`, OMS Level of Mandate, or OMS
`asynchronous`/`on_demand` timing. “Message” and an OMS section do not establish
`kind: oms_message`; mandate is not inferred from command importance; and
receive/respond/response are not timing categories.

No current profile rule is representable. v0.1 requires exact `function.name`
and `exchange.message` plus all five matcher fields. It has no Capability
presence, identity/name, function ownership, multiple-instance, or
Capability-relative selector model. Exact validation therefore needs explicit
Capability identity/ownership or another deliberately designed role-based model;
no literal `[CapabilityName]`, ESM selectors, regex, prefix, suffix, or template
heuristic is appropriate here.

The fixed response relationship also exposes a separate behavioral/causal gap:
the current independent exchange list cannot represent command/status pairing.
It is not a reason to add behavioral DSL semantics in this task.

`examples/capability-enable-disable.yaml` remains ordinary v0.1-valid and useful
as **an illustrative portable transcription of the OMS template's ESM Capability
Enable/Disable example**. It is not a source-backed normative minimum. Its input
and output values can remain authored illustration, but its exact kind, mandate,
and timing fields are copied from green rows and are not OMS profile-enforced.
Its traceability is tightened to the two Table 3.3-3 rows without implying fixed
normativity.

No change is made to `profiles/oms/2.5/profile.yaml`, either schema, the
validator, or diagnostics. Local UCI 2.5 has only the verified manifest, not
schema bytes, so no UCI resolver corroboration was attempted.
