from __future__ import annotations

import argparse
import sys

import pandas as pd

from src.validation.closed_candle_mtf_revalidation_v1 import (
    REPORTS_DIR,
    run_closed_candle_mtf_revalidation,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Revalidate the official SHORT candidate with completed 1H/4H "
            "candles and rerun the independent LONG structural chain."
        )
    )
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Validate local dataset presence, coverage and integrity without backtesting.",
    )
    parser.add_argument(
        "--allow-download",
        action="store_true",
        help=(
            "Download only missing Binance public OHLCV datasets. Network access "
            "is never used unless this flag is explicitly supplied."
        ),
    )
    parser.add_argument(
        "--simulations",
        type=int,
        default=10_000,
        help="Deterministic SHORT sequence-risk simulation count (default: 10000).",
    )
    return parser.parse_args()


def print_frame(title: str, frame: pd.DataFrame) -> None:
    print()
    print(title)
    print("=" * 100)
    print("Sin registros." if frame.empty else frame.to_string(index=False))


def main() -> int:
    args = parse_args()
    if args.simulations < 100:
        print("ERROR: --simulations must be at least 100.", file=sys.stderr)
        return 2

    print("PHASE 10.42R.2 SHORT/LONG CLOSED-CANDLE MTF REVALIDATION")
    print("=" * 100)
    print("No orders, signals, official evidence writes or automation are permitted.")
    print(f"Preflight only: {args.preflight_only}")
    print(f"Allow missing public-data downloads: {args.allow_download}")
    print(f"Sequence-risk simulations: {args.simulations}")

    try:
        result = run_closed_candle_mtf_revalidation(
            allow_download=args.allow_download,
            preflight_only=args.preflight_only,
            simulations=args.simulations,
        )
    except Exception as exc:
        print(
            f"FAIL-CLOSED ERROR: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 1

    for key, title in (
        ("summary", "REVALIDATION SUMMARY"),
        ("checks", "REVALIDATION CHECKS"),
        ("dataset_manifest", "DATASET MANIFEST"),
        ("context_shift_diagnostics", "LEGACY VS CLOSED-CANDLE CONTEXT"),
        ("short_aggregate_metrics", "SHORT CORRECTED/LEGACY AGGREGATE"),
        ("short_legacy_vs_corrected", "SHORT METRIC DELTA"),
        ("short_cost_aggregate", "SHORT COST GATES"),
        ("short_monte_carlo_summary", "SHORT SEQUENCE-RISK GATE"),
        ("long_source_dependency_audit", "LONG DEPENDENCY CLASSIFICATION"),
        ("long_readiness_revalidation", "LONG CONSISTENCY REVALIDATION"),
        ("candidate_decisions", "CANDIDATE DECISIONS"),
        ("errors", "ERRORS"),
    ):
        if key in result:
            print_frame(title, result[key])

    print()
    print("REPORT DIRECTORY")
    print("=" * 100)
    print(REPORTS_DIR)

    summary = result["summary"].iloc[0]
    validation_passed = bool(summary.get("validation_passed", False))
    if args.preflight_only:
        return 0 if validation_passed else 2

    completed = bool(summary.get("scientific_revalidation_completed", False))
    return 0 if validation_passed and completed else 1


if __name__ == "__main__":
    sys.exit(main())
