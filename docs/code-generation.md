# Code-Generation Integration Guide

This document describes a recommended architecture for consuming the machine-readable Service Contract. It is informative; backends may use different internal designs if they preserve the contract semantics.

## 1. Inputs

A contract-aware generator normally needs at least:

1. the machine-readable service contract;
2. the baseline UCI XSD/schema set selected and verified through a schema-source manifest;
3. declared UCI extension schemas, if any; and
4. a target backend configuration.

Example CLI shape:

```bash
oms-codegen generate \
  --contract contracts/example-service.yaml \
  --schema-source-manifest schema-sources/uci/2.5/manifest.yaml \
  --schema-source-root ./uci \
  --target ada \
  --out generated/
```

The exact CLI belongs to the generator project, not this specification.

## 2. Recommended pipeline

```text
contract YAML
       |
       v
Contract Model -- uci_schema_version --> toolchain schema-source selection
                                             |
                                             v
                                   schema-source manifest
                                             |
                                  verify local schema bytes
                                             |
                                             v
                                  UCI XSD set --> UCI parser
                                                       |
                                                       v
                                                  UCI Schema IR
                                             |
       Contract Model + UCI Schema Model
                     |
                     v
              Resolved Service IR
                 |
      +----------+----------+-----------+
      |          |          |           |
      v          v          v           v
     Ada        Rust       C++      deployment/docs
```

The **Resolved Service IR** should be an implementation detail of the generator. It may contain data not present in the portable contract, such as:

```text
ResolvedExchange
  function_id
  exchange_id
  direction
  mandate
  topic
  message_name
  message_qname
  primitive          <- derived from UCI PRIMITIVE_TYPE
  generated_type     <- backend mapping
  timing
  source_locations
```

## 3. Resolution algorithm

For each contract:

1. Parse YAML/JSON.
2. Validate against the matching contract-language JSON Schema.
3. Run semantic contract checks.
4. Map `standards.uci_schema_version` to a toolchain schema-source manifest.
5. Verify the supplied local schema files against the manifest SHA-256 values.
6. Load `manifest.root_schema` from those verified bytes.
7. Load only the declared extension schemas according to explicit toolchain mapping.
8. For every `kind: oms_message` exchange:
   1. resolve `message` uniquely;
   2. find its UCI definition;
   3. derive `PRIMITIVE_TYPE` and any other generator-required schema metadata;
   4. preserve the contract's direction/mandate/topic/timing metadata;
   5. produce one resolved exchange entry.
9. Apply OMS-version-specific profile checks, if the tool supports them.
10. Lower the resolved model into the target backend.

### Fail-closed behavior

Generation should fail rather than guess when:

- a message does not exist;
- multiple extension schemas make a name ambiguous;
- the configured UCI schema files do not match the requested version;
- a required annotation needed by the backend is missing; or
- a contract-language version is unsupported.

## 4. What should be derived from UCI

At minimum, do not duplicate these in the contract when UCI is authoritative:

- message field layout;
- nested UCI types;
- enumeration definitions;
- numeric/string restrictions;
- message primitive / `PRIMITIVE_TYPE`;
- namespaces/QNames; and
- schema inheritance/composition.

The contract identifies use of a message; the UCI parser owns the message's type model.

## 5. Ada/SPARK backend

A narrow generated API can make the declared contract visible at compile time.

Conceptually:

```ada
package Example_Service.Generated_Contract is

   procedure Handle_Service_Status_Data_Request
     (Request : UCI.Service_Status_Data_Request);

   procedure Publish_Service_Status
     (Status : UCI.Service_Status);

   procedure Publish_Service_Status_Data_Request_Status
     (Status : UCI.Service_Status_Data_Request_Status);

end Example_Service.Generated_Contract;
```

A backend could generate interfaces/abstract operations rather than implementations so user code must provide handlers for selected exchanges.

### SPARK caution

Do not automatically translate v0.1 informative timing values into `Pre`, `Post`, loop invariants, Global/Depends aspects, or real-time proof claims.

Future formal semantics could generate SPARK contracts, but only after the portable contract language defines normative behavior precisely.

## 6. Rust backend

A Rust backend could map input exchanges to handlers and output exchanges to publisher capabilities:

```rust
pub trait ExampleServiceInputs {
    fn handle_service_status_data_request(
        &mut self,
        request: uci::ServiceStatusDataRequest,
    );
}

pub trait ExampleServiceOutputs {
    fn publish_service_status(
        &mut self,
        status: uci::ServiceStatus,
    ) -> Result<(), PublishError>;
}
```

Exact ownership, async behavior, error types, and transport abstractions are backend policy, not portable contract semantics.

## 7. C++ backend

A C++ backend may generate pure abstract interfaces, strongly typed adapters, or wrappers around an existing CAL API.

Do not force C++ ABI details into the portable YAML. The contract should remain independent of:

- exceptions vs status codes;
- `std::unique_ptr`/references;
- templates;
- shared-library ABI policy; and
- compiler/runtime selection.

## 8. Python backend

A Python backend can generate:

- typed Protocol/ABC definitions;
- dataclass/Pydantic wrappers around generated UCI types;
- dispatch tables; and
- contract-based validation tests.

Again, those implementation details should not leak into the portable format.

## 9. Deployment/Sleet projection

The public AMS GRA Hello World Sleet implementation uses per-service configuration to constrain/describe topics/messages available to a service. A resolver can project OMS Message exchanges into deployment data:

```text
input OMS Message  -> subscribe/receive authorization candidate
output OMS Message -> publish/send authorization candidate
```

This projection should be reviewed as a security-sensitive derived artifact. The contract does not, by itself, define every deployment policy dimension.

A useful generator test is:

```text
set(generated_publish_permissions)
    == set(contract output OMS messages/topics)

set(generated_subscribe_permissions)
    == set(contract input OMS messages/topics)
```

subject to explicit platform/runtime exceptions.

## 10. Contract tests

A code generator can generate target-language tests from the resolved contract:

- every input exchange has a dispatch route;
- every output exchange has a typed publishing surface;
- every mandatory exchange is represented by the chosen backend policy;
- message types resolve to the expected UCI definitions;
- no generated public publisher exists for undeclared messages in a restricted façade; and
- deployment/topic projections agree with generated code.

These tests are particularly valuable across multiple language bindings.

## 11. Documentation generation

The same resolved model can generate an Inputs/Outputs summary containing:

- function name;
- message primitive (derived from UCI);
- I/O direction;
- data-exchange kind;
- message/transfer name;
- topic/configuration;
- Level of Mandate;
- periodicity; and
- informative timing values.

This allows human documentation and source interfaces to share one machine source while retaining UCI as the source for schema-owned facts.

## 12. Reproducibility

A serious toolchain should record:

- contract file digest;
- contract-language version;
- contract source commit/tag;
- schema-source manifest version, identity, and digest;
- UCI schema release, immutable revision, and file digest(s);
- extension schema digest(s);
- generator version/commit;
- backend version; and
- generated artifact manifest.

This is more reliable than recording only `UCI 2.5` or a moving `main` branch.
See [schema-source manifests](schema-sources.md).

## 13. Recommended diagnostic style

Diagnostics should identify both the contract path and external source context:

```text
error[C102]: unknown UCI message 'ESM_SetingsCommand'
  contract: functions[2].exchanges[0].message
  function: esm-enable-disable
  exchange: settings-command-input
  UCI baseline: 2.5
  extension schemas: none
```

For an ambiguity:

```text
error[C118]: OMS message name resolves to multiple schema definitions
  message: ExampleMessage
  candidates:
    - baseline:...
    - extension:...
```

Never silently choose based on file order unless that ordering rule is an explicit part of the resolver's contract.
