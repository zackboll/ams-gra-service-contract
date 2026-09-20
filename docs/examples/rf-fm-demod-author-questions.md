# RF FM Demod author questions

This report turns the completion scaffold for RF FM Demod into questions for the
service owner. It does not assert that the service is noncompliant and does not
create a portable contract.

## Service Initialization

OMS 2.5 supplies the required function and fixed exchange semantics. The pinned
RF FM Demod evidence does not supply the local authoring fields. Please answer:

1. What portable ID should represent the Service Initialization function?
2. What portable ID and topic should each FileMetadata and FileLocation exchange
   use?
3. What portable ID should the ServiceConfigFile Data Transfer use?
4. What protocol, data type, data format, and sharing pattern should that Data
   Transfer declare?

## Service Status

Already supplied by the OMS profile: function name, required category/group and
applicability; ServiceStatus output, mandatory mandate, and periodic timing;
ServiceStatusDataRequest input, mandatory mandate, and asynchronous timing; and
ServiceStatusDataRequestStatus output, mandatory mandate, and on-demand timing.

The exercise author selected `mission.service-status` and `1.0` Hz from the
supporting configuration document. That selection does **not** claim that the
primary Service Contract contained those values.

Please answer what portable function ID and portable exchange IDs to use, and what
topics ServiceStatusDataRequest and ServiceStatusDataRequestStatus use. Do not
re-answer mandate, direction, or timing kind that OMS already fixes.

## PositionReport

Published evidence says PositionReport is an input; configuration offers
`mission.position-report` as a candidate topic. Please answer:

1. Which portable function owns PositionReport?
2. Is it a Specific Function, or is there a separately author-confirmed
   standard/Capability relationship?
3. What portable function and exchange IDs should be used?
4. What is its Level of Mandate and intended portable timing classification?
5. Should the configuration-example topic become contract semantics?

## SignalReport

Published evidence says SignalReport is an output, published when FM audio energy
exceeds the configured threshold. Configuration offers `mission.signal-report`
and an implementation `report_rate_limit_hz` of `2.0`. Please answer which
portable function owns it, its function and exchange IDs, its Level of Mandate,
its portable timing classification, and whether the topic should be adopted.

Does the 2.0 Hz limit represent a contract timing bound, an implementation
throttle, or only runtime configuration? **Task 046 does not classify the event
trigger or rate limit on the author's behalf.**

## Capability inventory

Does RF FM Demod explicitly provide zero portable OMS Capabilities, or is its
Capability inventory unknown/not yet supplied? Runtime configuration
`capability_ids: []` does not answer this: it is MEL/runtime configuration, not an
explicit portable Service Contract Capability inventory.
