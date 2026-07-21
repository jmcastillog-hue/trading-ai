# Phase 10.42R.8 — OpenClaw Read-Only Research Status Local Consumer Adapter Implementation V1

## Decision boundary

Phase 10.42R.8 implements one local, one-shot, read-only consumer adapter.

The adapter accepts exactly one JSON request from standard input, validates the
fixed Phase 10.42R.4 two-file export bundle, emits exactly one allowlisted JSON
response to standard output, and exits.

It does not invoke OpenClaw or LM Studio, register a tool, start a service, open
a socket, use a network, execute shell commands supplied by a caller, write a
file, create a cache or log, mutate the export bundle, read market data,
generate a signal, place a paper trade or use real capital.

Python remains the source of truth. Human review remains mandatory.

## Source authority

The implementation is bound to:

- Phase 10.42R.7 review commit
  `6df6aa8aef73cd9c5118caf5acf1e723e5438d32`;
- Phase 10.42R.6 design commit
  `45d22e5dc242fd0f475135182c32b37b2c4d4a4c`;
- design root
  `b7336e60c705841f3ff313016816d9115fb46485d67d3a016d0206ab43d89e21`;
- Phase 10.42R.3 contract root
  `ba84140879bac8a897505bd55e12d3c117354caf1a5a5ad4f6c3eb003bd6fa46`;
- snapshot SHA-256
  `72a77f3a726d38f0008378218958a5ea8ee8fb0162477692a7370dcf9af43e88`;
- export-manifest SHA-256
  `f829010549a79fb3eb35b38ce51736f730020747d6fc77b7fa56eac5ade6a5f7`;
- snapshot size of 5,965 bytes.

The Phase 10.42R.7 commit must exist and remain an ancestor of HEAD.

## Request contract

The adapter accepts one JSON object with exactly:

```json
{
  "operation": "GET_VALIDATED_RESEARCH_STATUS",
  "response_profile": "HUMAN_EXPLANATION_ONLY",
  "require_human_review": true,
  "allow_actionable_fields": false
}
```

The adapter rejects malformed JSON, duplicate keys, additional fields,
unsupported operations, disabled human review and requests for actionable
fields.

The maximum request size is 4,096 bytes.

## Read boundary

The adapter resolves the repository from its current working directory and may
read only:

- `reports/phase_10_42r_4/openclaw_read_only_export_v1/openclaw_read_only_research_status_v1.json`;
- `reports/phase_10_42r_4/openclaw_read_only_export_v1/openclaw_read_only_research_status_v1.manifest.json`.

The directory must contain exactly those two regular non-symbolic-link files.
Subdirectories, temporary files, path overrides, globs and traversal are
rejected.

The implementation validates exact byte hashes, snapshot size, canonical JSON,
manifest bindings, the contract root, the six read-only capabilities, the 23
prohibited capabilities and the mandatory human-review policy.

## Response boundary

A successful response has exactly eight top-level fields:

- `adapter_schema_version`;
- `adapter_mode`;
- `decision`;
- `source`;
- `research_status`;
- `restrictions`;
- `human_review`;
- `next_routes`.

The payload is for human explanation only. It contains no entry, stop, target,
position size, leverage, side, signal, order, quantity, exchange command or
trading instruction.

The response retains the frozen Phase 10.42R.6 contract identifiers. That is a
compatibility property, not a claim that the implementation remains design-only.

## Failure boundary

Any failure:

- emits no response on standard output;
- emits one compact diagnostic object on standard error;
- returns a nonzero fail-closed exit code.

Exit codes remain within the frozen registry:

- 20 invalid request shape or malformed request;
- 21 unsupported operation;
- 22 source authority failure;
- 23 export bundle integrity failure;
- 24 permission boundary violation;
- 25 response allowlist violation;
- 26 missing human-review requirement;
- 27 stale source binding;
- 28 prohibited runtime integration request;
- 70 internal fail-closed error.

## Explicitly prohibited

Phase 10.42R.8 keeps zero or false:

- OpenClaw invocation or runtime integration;
- LM Studio invocation;
- tool registration or invocation;
- persistent services, APIs, HTTP, sockets and network access;
- adapter filesystem writes, logs and caches;
- historical evaluation, backtesting and performance recalculation;
- candidate comparison, ranking, selection or mutation;
- lockbox or holdout access;
- official evidence writes;
- signal generation and live alerts;
- paper trading and real capital;
- market or exchange execution;
- automation.

## Passing decision

`PHASE_10_42R_8_OPENCLAW_READ_ONLY_RESEARCH_STATUS_LOCAL_CONSUMER_ADAPTER_IMPLEMENTATION_VALIDATED`

A passing decision validates only a local one-shot adapter. It does not connect
the adapter to OpenClaw and does not approve any strategy or operation.

## Recommended next phase

`PHASE_10_42R_9_OPENCLAW_READ_ONLY_RESEARCH_STATUS_LOCAL_CONSUMER_ADAPTER_INDEPENDENT_IMPLEMENTATION_REVIEW_V1`

Phase 10.42R.9 may independently review the implementation, its one-shot
process behavior and its failure boundary. It still may not invoke OpenClaw,
register a tool, start a service, use a network or grant operational
permissions.

Phase 10.43 remains separately allowed and not started.
