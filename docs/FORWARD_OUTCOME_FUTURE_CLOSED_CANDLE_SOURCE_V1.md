# Forward Outcome Future Closed-Candle Source V1

## Purpose

Provide a separately governed, one-shot source of already-closed public Spot
`BTCUSDT` `15m` candles for `FORWARD_OUTCOME_LABELER_V1`.

This component is deliberately separate from synchronized market observation.
It does not recapture microstructure and does not create a new trading observation.

## Why 17 candles

`FORWARD_OUTCOME_LABELER_V1` evaluates horizons `1, 2, 4, 8, 16`.

The primary outcome anchor can begin at the reference boundary while the synchronized
context anchor can begin at the next complete 15-minute boundary after context
availability.

A contiguous 17-candle source beginning at the primary reference boundary therefore
covers:

- 16 bars from the primary anchor; and
- 16 bars from an immediately following context anchor.

The source does not decide which bars the labeler uses. It only provides the
contiguous closed-candle window. The already-closed Labeler owns anchor selection,
maturity, return/MFE/MAE calculation, and target/stop ordering.

## Capture contract

Authorization:

`CAPTURE_ONE_SHOT_FORWARD_OUTCOME_FUTURE_CLOSED_CANDLES_V1`

The capture:

- uses the public Binance Spot klines endpoint already referenced by the existing
  closed-candle capture component;
- uses `BTCUSDT`;
- uses `15m`;
- requires an exact UTC 15-minute-aligned first open time;
- requests exactly 17 rows beginning at that open time;
- performs exactly one foreground public HTTP GET;
- requires all 17 rows to be fully closed at capture time;
- requires exact 15-minute continuity;
- requires the first returned kline to match the requested start time exactly;
- writes external create-only artifacts;
- performs no automatic retry.

## Output

External output:

- `future_closed_candles.csv`;
- `capture_metadata.json`;
- `manifest.sha256`.

The CSV schema is imported directly from
`FORWARD_OUTCOME_LABELER_V1.FUTURE_SOURCE_COLUMNS`.

## Maturity rule

Capture is fail-closed until the last of the required 17 candles is already closed.

There is no partial-window mode in V1.

For an observation whose first required bar began several days earlier, this maturity
gate should already be satisfied. The component still verifies the condition from the
capture clock rather than assuming it.

## Safety boundaries

This component does not:

- use an API key;
- use a signed or authenticated endpoint;
- access an account or orders;
- use WebSocket;
- retry automatically;
- schedule itself;
- run in the background;
- generate a signal;
- modify the primary LONG rule;
- recapture synchronized microstructure;
- send alerts or messages;
- enable paper trading;
- enable real capital;
- execute on an exchange;
- write the official forward dataset;
- enable the official append gate.

## Relationship to preserved observation

A future real capture may be used as input to the already-published
`FORWARD_OUTCOME_LABELER_V1` for the preserved synchronized observation.

The real source capture and the label-package creation remain separate authorization
events. Publishing this component does not authorize either real action.

## Validation

Sandbox validation uses a mocked HTTP function only and must prove:

- exact authorization is required before any output;
- the existing Spot capture authorization is not accepted;
- exactly one request is made;
- request parameters contain the exact requested start time and `limit=17`;
- all rows are closed and contiguous;
- gaps, wrong starts, invalid OHLC, open candles, HTTP failures and malformed JSON
  fail closed;
- output is external and create-only;
- the manifest detects tampering;
- the official artifacts remain unchanged in mocked capture tests;
- no permissions are enabled.

## Next step

After sandbox validation and publication, one explicit human authorization can permit
a single real historical public Spot request for the preserved observation.

Only after that source is captured and validated should
`PREPARE_FORWARD_OUTCOME_LABEL_PACKAGE_V1` be separately authorized.
