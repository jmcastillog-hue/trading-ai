# Phase 10.42R.2J — Frozen Recovery Candidate Historical Input Manifest Binding and Integrity Validation V1

## Status

This phase freezes and validates the historical input binding required by the preregistered controlled known-evidence evaluation. It does **not** execute any candidate, backtest, performance metric, comparison, ranking, winner selection, paper trade, live alert, capital allocation, market execution, automation, or OpenClaw operational integration.

Phase 10.42R.2J is finite. Once the source package, local binding, integrity checks, tests, commit, push, fast-forward merge, ref equality, and clean working tree are confirmed, the phase closes and advances directly to Phase 10.42R.2K.

## Frozen source anchors

- Source commit from Phase 10.42R.2I: `ddcd059bd747891c47e2738974b1b42465ba5adf`
- Frozen harness-design SHA-256: `ee62064148bdb119c7b3390d7dab3db338b4d5b50a1eaf7adb44d4c9dffd5dbb`
- Acquisition and binding source SHA-256: `d824c562f331cce54a92fb66aaaac59daec2024e0733dabcacf8d668ff9c7c14`
- Binding root SHA-256: `5c1ccb1c9fecdad2e196558a946944f5b9f89f258c5ef591a65d4c4c480d8c14`

## Evidence window

- Window identifier: `KNOWN_EVIDENCE_2022_2025`
- Half-open interval: `[2022-01-01T00:00:00Z, 2026-01-01T00:00:00Z)`
- Provider: Binance Public Data
- Market: Binance Spot
- Acquisition method: monthly kline archives with official SHA-256 checksum files
- Symbols: BTCUSDT, ETHUSDT, SOLUSDT
- Timeframes: 15m, 1h, 4h
- Logical input slots: 9
- Verified monthly archive records: 432

The retrospective lockbox `[2026-01-01, 2026-07-20)` and prospective holdout `[2026-07-20, 2027-01-20)` remain sealed and outside this binding.

## Canonical local artifacts

The market datasets and binding audit artifacts remain local and Git-ignored under:

`data/market_input/local_csv_read_only/input/`

They are not committed to Git. The versioned validation source freezes their exact hashes and metadata so the local evidence can be validated reproducibly without publishing large market-data files.

### Audit artifacts

| Artifact | SHA-256 |
|---|---|
| `phase_10_42r_2j_historical_input_manifest_v1.csv` | `40982ff9b92de06df6413fd3d2f448ff4e10f9fdd266cffb0c4945dccd02799c` |
| `phase_10_42r_2j_archive_provenance_v1.csv` | `9c77fac16b34d7a98ae72f251a1015358c9d2dd2899e593d1314bbc6679eabde` |
| `phase_10_42r_2j_missing_interval_ledger_v1.csv` | `2b079dbd2347f594091a669f608866b8df743ecd3a075a34670c8f05bbf11331` |

### Dataset binding matrix

| Slot | Rows | Declared gaps | Bytes | SHA-256 |
|---|---:|---:|---:|---|
| BTCUSDT 15m | 140251 | 5 | 19588185 | `2d8ff771274b86202866722644e843aba32228463d9fd191f967577b8878dc3b` |
| BTCUSDT 1h | 35063 | 1 | 4917400 | `56aab93c9e336babdcfec82b2d022d5f079638ceeb95c19018853c59ae78951e` |
| BTCUSDT 4h | 8766 | 0 | 1234933 | `8679bb2a138db53e2a54eb409ef3c82755a3fa042f8c1d65b23314d79b9bb196` |
| ETHUSDT 15m | 140251 | 5 | 19080778 | `4ef8ecbe67df362ffb8227bed6cfd577397284ad98a4a6e1bd8f4607eb6b6e59` |
| ETHUSDT 1h | 35063 | 1 | 4792596 | `f45a1bf3803818931ed14db5b20429b75b7fefc5b0c90a8554bbf5055fcfca70` |
| ETHUSDT 4h | 8766 | 0 | 1203329 | `317d8bae4d74ae7aea10500cef3514b80e684859e0eb97ad8d69763985dd70b7` |
| SOLUSDT 15m | 140251 | 5 | 18388960 | `4c70aa25c9a79ab4c09753152cbffc35be48299d0b27279e14720dc3931a9747` |
| SOLUSDT 1h | 35063 | 1 | 4619122 | `d82d9979af9cd786d70a74cccf727e984281517ddf561c4c92ad3ca6c2044598` |
| SOLUSDT 4h | 8766 | 0 | 1159922 | `f354b3cc4ea6c111955a2160061f8dfcd0a6d93a274964a3844ec03463bd0541` |

## Source-gap policy

The official checksum-verified archives contain 18 absent calendar intervals:

- 5 per 15m symbol dataset
- 1 per 1h symbol dataset
- 0 per 4h symbol dataset

The policy is:

`PRESERVE_AND_DECLARE_CHECKSUM_VERIFIED_SOURCE_GAPS_NO_INTERPOLATION`

For every slot:

`observed row count + declared missing interval count = full calendar row count`

No synthetic candle, interpolation, forward fill, backward fill, zero-volume placeholder, or imputed OHLCV row is permitted. Every absent open timestamp must appear exactly once in the missing-interval ledger and must be linked to checksum-verified source archives through the slot provenance hash.

## Manifest contract

The manifest contains exactly 25 ordered fields frozen in Phase 10.42R.2I. Each row must:

- identify one of the exact nine symbol/timeframe slots;
- reference a repository-relative Git-ignored local path;
- match exact file SHA-256 and byte size;
- match exact row count and declared gap count;
- use the canonical seven-column schema;
- contain zero duplicate open timestamps;
- contain zero duplicate close timestamps;
- contain zero invalid OHLCV rows;
- have binding state `BOUND_VERIFIED`;
- pass its canonical `manifest_row_sha256` check;
- pass its per-slot provenance SHA-256 check.

## Provenance contract

The archive provenance ledger must contain exactly 432 records:

- 48 monthly archives per logical slot;
- official `data.binance.vision` monthly kline URLs;
- matching `.CHECKSUM` URLs;
- valid 64-character SHA-256 checksums;
- positive ZIP sizes.

## Integrity validation

The full validation performs streaming reads and verifies:

1. source commit and source-file anchors;
2. acquisition-source hash;
3. exact limited permissions;
4. sealed lockbox and forward paths;
5. exact hashes of 12 local artifacts;
6. exact manifest, provenance, and gap-ledger schemas;
7. exact dataset registry and metadata;
8. exact Git-ignore status for all nine datasets;
9. canonical dataset headers;
10. timestamp ordering and interval arithmetic;
11. complete OHLCV structural validity;
12. exact declared-gap reconciliation;
13. exact missing-timestamp equality between datasets and ledger;
14. exact 48-archive provenance per slot;
15. exact per-slot provenance hashes;
16. zero synthetic gap fills;
17. zero historical evaluation activity.

Expected full validation counts:

- preflight checks: 9
- binding and integrity checks: 122
- total checks: 131
- failed checks: 0
- blockers: 0
- local artifact hash reads: 12
- schema/data parses: 12
- dataset scans: 9

## Limited permissions in 2J

Only these permissions are enabled for this phase:

- real historical data access;
- historical input binding;
- historical file hashing;
- historical schema parsing.

All evaluation and operational permissions remain false, including:

- historical evaluation;
- performance metrics;
- candidate comparison;
- candidate ranking;
- winner selection;
- lockbox access;
- holdout access;
- signal generation;
- paper trading;
- real capital;
- exchange or market execution;
- automation;
- OpenClaw operational integration.

## Closure decision

A successful full validation returns:

`HISTORICAL_INPUT_MANIFEST_BOUND_AND_INTEGRITY_VALIDATED`

This decision means only that the known-evidence inputs are frozen, complete under the declared-gap policy, hash-anchored, and ready for the separately controlled Phase 10.42R.2K evaluator. It is not evidence that any strategy is profitable or operationally approved.

## Next phase

`PHASE_10_42R_2K_FROZEN_RECOVERY_CANDIDATE_CONTROLLED_KNOWN_EVIDENCE_EVALUATION_V1`

Phase 2K may execute only the six frozen variants against the exact 2J binding under the 2H preregistration and 2I harness contract. It must not open the retrospective lockbox or prospective holdout.
