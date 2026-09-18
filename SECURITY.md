# Security Policy

This repository is a specification/validation prototype and does not itself provide a secure runtime.

## Reporting

For security issues in this repository's validator/tooling, open a private security advisory in the hosting repository when available. Do not publish exploit details before maintainers have had an opportunity to assess them.

## Threat model notes for consumers

Contract files may influence generated source code and deployment permissions. Treat them as trusted build inputs only after validation/review.

Consumers should:

- validate against the exact contract-language schema;
- reject unknown fields;
- pin and verify UCI/extension schema inputs;
- avoid automatically fetching/processing arbitrary `sources[].uri` values;
- escape user-controlled strings in generated code/docs;
- use safe YAML loading APIs;
- review generated deployment authorization; and
- record source/generator digests for reproducible builds.

Text fields such as `description`, `note`, `locator`, `details`, and `reference` are data, not executable instructions.
