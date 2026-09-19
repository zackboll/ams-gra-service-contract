# Task 026 — OMS 2.5 capability function inventory evidence

## Authoritative artifact inspected

- Repository: `open-arsenal/oms`
- Revision: `726272bd0390982a759c91a9cf4e13b81c2b510b`
- Artifact: `docs_official/14_2_OMSC-INS-003_RevM_ServiceContractInstructions_DandD_v2_5.docx`
- Surfaces: Table 3.0-1 and Sections 3.3, 3.3.1, and 3.3.2 through 3.3.2.3

Classification used `word/document.xml` and `word/styles.xml` from the official
DOCX. The upstream Markdown was navigation only.

## OOXML color method

`BodyText -> Normal` and the relevant `Heading2`/`Heading3`/`Heading4` paths
have no color value, so absent a run override their effective color is
automatic/black. `GreenBodyText -> BodyText -> Normal` explicitly sets
`00B050`. `TableLeftAlignGreen -> TableLeftAlign -> TableHeaderCenterBold ->
Normal` and `TableCenterGreen -> TableCenter -> TableLeftAlign ->
TableHeaderCenterBold -> Normal` explicitly set `00B050`.

The paragraphs and Table 3.0-1 cells below have no contrary run-color override
unless noted. The Section 3.3.2 headings have a black heading paragraph style,
but their text runs explicitly set `00B050`; their effective visible text is
green.

## A. Section 3.3 applicability

### Authoritative source facts

`word/document.xml` paragraph 2393 is `BodyText`, no explicit run color, and
therefore automatic/black: a Subsystem or Service that provides a Capability is
required to provide these functions. This establishes the source's parent
condition, but it does not identify which capabilities a particular component
provides.

Paragraphs 2392, 2394, and 2395 are `GreenBodyText`, inherited `00B050`, with
no run overrides. They respectively say Section 3.3 may not be tailored except
where indicated; say it applies only to Capability-providing Subsystems/Services
and exclude Isolators; and instruct a component without a Capability to mark
the parent section N/A with a rationale, retain the section/subsection
structure, remove green text, and place N/A in table cells. These are template
authoring instructions, not fixed black contract inventory.

The green whole-section N/A instruction describes document sections and table
cells. It does not say that Function List rows remain, nor does it require a
machine-readable N/A function entry. Conversely, Table 3.0-1's independently
green row-selection instruction says to retain applicable rows and remove
inapplicable rows. The source therefore does not equate parent-section presence,
Function List row presence, and a portable `functions[]` member.

### Repository conclusion

The existing profile must not infer Capability provision from the presence or
absence of `required_group: capability` functions: doing so would make the
requirement circular. It currently does not do so.

## B. Table 3.0-1 capability rows

The surrounding row-selection instruction at paragraph 1370 is
`GreenBodyText`, effective `00B050`: keep applicable rows, change green text to
black, and remove rows that are not applicable. Every relevant Table 3.0-1 row
has no explicit run color and is entirely green:

| Function row | Function-name cell | Category cell | Detail locator cell | Classification |
| --- | --- | --- | --- | --- |
| Position Information Processing | `TableLeftAlignGreen`, inherited `00B050` | `TableLeftAlignGreen`, inherited `00B050` | `TableCenterGreen`, inherited `00B050` (`3.3.1`) | green removable template inventory |
| Capability and Capability Status | same | same | `TableCenterGreen`, `00B050` (`3.3.2.1`) | green removable template inventory |
| Capability Enable/Disable | same | same | `TableCenterGreen`, `00B050` (`3.3.2.2`) | green removable template inventory |
| Capability Operations | same | same | `TableCenterGreen`, `00B050` (`3.3.2.3`) | green removable template inventory |

Thus the labels “Required Function for Capabilities” do not by themselves make
these four Table 3.0-1 rows fixed black inventory. The row-removal instruction
is also green.

## C. Position Information Processing applicability

### Authoritative source facts

The 3.3.1 heading at paragraph 2396 is `Heading3`, automatic/black. Paragraph
2397 is black `BodyText` and calls it the function that supports Capabilities.
However, paragraphs 2398 and 2399 are green `GreenBodyText`, effective
`00B050`: the function applies only where a provided Capability depends on
position information, and is marked N/A where position information is not
required for that Capability.

The source therefore establishes the function type and the conditional
applicability concept, not a universal Position Information Processing function
for every Capability provider. It does not establish that a Function List N/A
row must remain when position is unnecessary; Table 3.0-1 instead directs
removal of inapplicable green rows.

### Repository conclusion

v0.1 has no independent Capability-presence or position-dependency fact, so a
profile cannot decide whether the function is required without guessing. No
Position Information Processing profile rule is added.

## D. `[CapabilityName]` replacement semantics

Paragraph 2476 is green `GreenBodyText`, effective `00B050`, and explicitly
instructs the author to replace `[CapabilityName]` with the Capability name in
the heading and subsection headings (example: `ESM`). It may apply to black and
green paragraph/table occurrences. `[CapabilityName]` is consequently a field
delimiter/replacement location, not a literal canonical final function name.

The 3.3.2 parent heading (paragraph 2473) and the three function headings
(2478, 2558, and 2638) are heading styles with explicit green `00B050` text
runs. Their generic text is editable template material. The source supports
final names following the shown replacement pattern, such as `ESM Capability
Enable/Disable`, but does not provide a portable canonical-name contract that
makes string parsing or prefix/suffix matching safe.

## E. Per-capability repetition semantics

Paragraph 2477 is green `GreenBodyText`, effective `00B050`: “IMPORTANT: Copy
this entire Section 3.3.2 for each additional Capability.” It is not fixed black
source content. The source documents an authoring pattern for separate 3.3.2
sections, but this task does not promote that green instruction into a fixed
machine-checkable exactly-three rule.

## F. Required function types per capability

Section 3.3.2 contains these three generic types: Capability and Capability
Status, Capability Enable/Disable, and Capability Operations. Their Table 3.0-1
rows and generic 3.3.2 heading text are green template inventory. The black
parent statement says a Capability provider is required to provide “these
functions,” but neither the fixed source content nor v0.1 provides a reliable
component-specific capability set or owner relationship. This task classifies
the types but does not claim an exact fixed three-functions-per-capability
profile rule, nor does it infer that any of the three is independently N/A.

## G. Isolator treatment

The Section 3.3 Isolator exclusion is green authoring guidance (paragraph
2394), while the black parent requirement names only Subsystems and Services.
No Section 3.3 profile requirement applies to `service.kind: isolator`; the
existing profile correctly leaves Isolators subject only to their Section 3.1
rules.

## H. Current v0.1 representability

v0.1 supplies `service.kind`, `functions[].name`, `category`,
`required_group`, and `applicability`. It does **not** supply whether the
component provides Capabilities, a list/identity/name for each Capability,
whether each Capability depends on position information, or a function's
Capability owner/reference. Function names cannot safely reconstruct those
facts.

## I. Profile-model representability

The v0.1 profile DSL has component-level `applies_to` and singleton exact
`required_functions[].name` matching. It can express neither Section 3.3's
conditional parent presence nor conditional position applicability without an
independent contract fact. It cannot express exactly three functions per
arbitrary Capability, verify that the three share an owner, or represent
multiple independent Capabilities. Exact-name matching is appropriate for fixed
names such as `Subsystem Status`, but not an arbitrary repeated family.

## J. Concrete modeling gaps

Exact validation would minimally need independent capability data, for example:

```yaml
capabilities:
  - id: esm
    name: ESM
    requires_position_information: true
```

and an ownership reference on each relevant function, for example:

```yaml
function:
  capability: esm
```

Other deliberately designed representations may be possible. Without at least
equivalent independent presence, identity, ownership, and position-dependency
information, a validator cannot distinguish no Capability, one Capability,
multiple Capabilities, or an incomplete family without circular or
name-heuristic inference. These are candidate future v0.2 concepts, not Task
026 schema changes.

## K. Final decision on profile changes

No OMS 2.5 `required_functions` rule is added. No portable schema, profile
schema, profile manifest, validator, diagnostic, or exchange-table requirement
is changed. Regressions verify that complete ordinary Service, Subsystem, and
Isolator contracts without capability functions—and therefore without Position
Information Processing—remain profile-valid. This is a conservative limitation
of the absent model facts, not a claim that OMS never requires capability
functions.

`examples/capability-enable-disable.yaml` remains ordinary v0.1-valid: it is a
source-backed portable fragment using an ESM replacement example, not evidence
of a universal literal name or complete Section 3.3 inventory.
