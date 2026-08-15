# Synchronized Observation V1.1 — Microstructure Authorization Propagation V1

## Purpose

This is an additive compatibility repair after the separately closed
`PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1` authorization-contract repair.

The closed `SYNCHRONIZED_15M_OBSERVATION_V1_1` implementation remains immutable.
It still delegates the historical internal microstructure token
`CAPTURE_ONE_SHOT_BINANCE_USDM_PUBLIC_MICROSTRUCTURE_V1`.

The repaired Microstructure V1.1 entry point now correctly requires
`CAPTURE_ONE_SHOT_BINANCE_USDM_PUBLIC_MICROSTRUCTURE_V1_1`.

Without an adapter, a new synchronized V1.1 session therefore fails closed before
the microstructure capture. This component repairs only that propagation boundary.

## Additive design

This module does **not** edit or fork the scientific logic of the closed synchronized
observer.

Instead it:

1. requires a new user-facing outer authorization:
   `RUN_BOUNDED_SYNCHRONIZED_15M_OBSERVATION_SESSION_V1_1_MICROSTRUCTURE_AUTH_PROPAGATION_V1`;
2. invokes the closed `SYNCHRONIZED_15M_OBSERVATION_V1_1` runner as an internal
   dependency;
3. injects a narrow microstructure capture bridge;
4. verifies that the closed runner delegates exactly its known legacy internal token;
5. intercepts that internal token and calls the repaired Microstructure V1.1 capture
   with `CAPTURE_ONE_SHOT_BINANCE_USDM_PUBLIC_MICROSTRUCTURE_V1_1`;
6. records a separate create-only authorization-propagation attestation around the
   preserved inner synchronized session.

The legacy user-facing synchronized authorization is **not** accepted by this new
capability. The legacy microstructure token is also not accepted as a user-facing
authorization. Its presence is tolerated only at the known internal seam of the
already-published closed V1.1 orchestrator.

## Why the internal compatibility seam is acceptable

The old constant is not sent to Binance, is not an API credential, and is not
accepted from the user by this capability.

It is checked only to prove that the closed orchestrator has not changed. The bridge
then substitutes the repaired version-specific local authorization before calling
Microstructure V1.1.

If either side of that known seam changes, the adapter fails closed.

## Output

The outer create-only output contains:

- `authorization_propagation.json`;
- `manifest.sha256`;
- child directory `synchronized_v1_1_session/`, containing the untouched output
  contract of the closed synchronized V1.1 runner.

The outer attestation records:

- the new outer authorization contract;
- that legacy user authorizations are rejected;
- that the closed internal delegated token was intercepted;
- the repaired Microstructure V1.1 token actually delegated;
- the number of completed synchronized cycles;
- the preserved 8-request-per-completed-cycle contract;
- the hash of the inner session manifest;
- false permission fields;
- `automatic_retry_allowed=false`.

## Network behavior

The adapter contains no HTTP client and performs no direct network request.

A future real invocation is still a network-capable synchronized observation because
the closed inner runner delegates one public Spot request and seven public USD-M
Futures requests per completed cycle.

The sandbox validation for this component uses mocks only and performs zero real
market-data requests.

No real session is authorized merely by installing or publishing this repair.

## Failure behavior

There is no automatic retry.

If a future real inner session fails after some requests have occurred, a second
market-data attempt requires a new explicit authorization decision.

## Scientific boundaries

This repair does not:

- modify `LONG_BASE_FAILED_BREAKDOWN_V1`;
- create or cancel a candidate;
- change temporal eligibility;
- change depth-band semantics;
- change the 1/2/4/8/16 Forward Outcome Labeler horizons;
- infer direction from microstructure;
- generate a signal;
- send an alert or message;
- enable paper trading;
- enable real capital;
- execute on an exchange;
- write the official forward dataset;
- enable the official append gate.

## Closed dependencies

The following remain preserved:

- `SYNCHRONIZED_15M_OBSERVATION_V1_1`;
- repaired `PUBLIC_READ_ONLY_MICROSTRUCTURE_SNAPSHOT_V1_1`;
- `FORWARD_OUTCOME_LABELER_V1`;
- the frozen primary LONG rule and its source adapter.

## Validation objective

Sandbox validation must prove, without real network access, that:

- only the new outer authorization starts the wrapper;
- the closed internal synchronized authorization is implementation-only;
- the bridge accepts only the exact known delegated legacy microstructure token;
- the bridge calls repaired Microstructure V1.1 with the new V1.1 token;
- the 7-request microstructure contract is preserved;
- the synchronized 8-request-per-cycle accounting remains unchanged;
- the outer attestation and manifest validate;
- no permission surface is enabled;
- no closed dependency is edited.

## Continuation

After this additive propagation repair is sandbox validated and published, no
additional repair is required unless a concrete reproducible defect appears.

The next useful project step is to govern an already-closed future-candle source for
`FORWARD_OUTCOME_LABELER_V1` and produce one controlled real forward-label package
for the preserved synchronized observation.

That future-data acquisition must remain separately authorized from synchronized
microstructure observation. A new synchronized market capture is not required merely
to validate the Forward Outcome Labeler.
