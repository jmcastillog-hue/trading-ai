# Onchain Context Interface V1

## Purpose

`ONCHAIN_CONTEXT_INTERFACE_V1` is the Level A `FUTURE_INTERFACE` contract for
bringing externally frozen Bitcoin on-chain measurements into the Context
Feature Pack without granting them trading semantics.

V1 does not choose an on-chain data vendor, call a provider API, query a node,
or define a profitable interpretation of any metric.

## External snapshot

The producer consumes an immutable JSON snapshot with schema:

`ONCHAIN_CONTEXT_SNAPSHOT_V1`

The snapshot identifies:

- observation ID and reference boundary;
- asset `BTC`;
- network `BITCOIN`;
- provider and dataset identity;
- source reference;
- immutable metric-schema SHA-256;
- snapshot creation time;
- one or more metric records.

Each metric record contains:

- `metric_id`;
- `unit`;
- finite numeric `value`;
- observation start/end;
- information cutoff;
- provider availability time;
- provider/source revision ID.

Metric IDs must be unique and sorted for deterministic serialization.

## Point-in-time contract

For each metric:

`observation_end <= observation_reference`

`observation_end <= information_cutoff <= provider_available <= snapshot_created`

The producer does not interpolate a metric forward to the observation time.

The component information cutoff is the latest metric information cutoff.
Feature availability is the maximum of snapshot creation, the policy floor,
all provider availability times, and the information cutoff.

The Context Feature Pack then independently decides whether the component was
available by the synchronized context cutoff.

## Governance floor

`2026-08-19T02:27:00+00:00`

A historical on-chain snapshot created before this policy may be retained for
audit, but it cannot be retrospectively promoted as point-in-time evidence for
an older observation.

## Metric semantics

Raw metric values are preserved exactly as descriptive inputs. V1 does not
assign any of the following:

- bullish/bearish meaning;
- long/short meaning;
- overbought/oversold meaning;
- threshold signal;
- probability;
- expected return;
- composite score;
- candidate modification.

Metric age in seconds is descriptive provenance only.

## Deliberately absent provider

The feature is intentionally provider-agnostic. A future provider adapter may
be implemented separately only after its source contract, timestamps,
revisions, licensing, and availability behavior are audited.

This interface therefore gives the project a stable on-chain schema without
silently selecting Glassnode, CryptoQuant, a node RPC, or another provider.

## Package authorization

Authorization:

`PREPARE_ONCHAIN_CONTEXT_INTERFACE_V1`

Inputs:

- external observation descriptor JSON;
- external frozen on-chain snapshot JSON;
- explicit `produced_at_utc`.

Output:

- `onchain_context_interface_component.json`
- `producer_checks.json`
- `manifest.sha256`

The package is external, create-only and transactional.

## Safety

No web request, provider API request, node RPC, exchange request, market-data
fetch, live alert, paper trade, real-capital action, execution, or official
dataset append is permitted.

## Evaluation boundary

On-chain measurements are context hypotheses, not evidence of edge. Their
usefulness must be tested later by the Context Evaluation Engine against
separately preserved point-in-time observations and forward outcomes.
