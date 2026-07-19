from __future__ import annotations

import argparse
import sys

import pandas as pd

from src.validation.signal_to_fill_timing_integrity_audit_v1 import (
    REPORTS_DIR,
    run_signal_to_fill_timing_integrity_audit,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit same-candle-close diagnostic fills against next-bar-open "
            "fills for the corrected SHORT and independent LONG chains."
        )
    )
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help=(
            "Validate Phase 10.42R.2 reports, immutable dataset lineage and "
            "the LONG historical input without running timing comparisons."
        ),
    )
    return parser.parse_args()


def print_frame(title: str, frame: pd.DataFrame) -> None:
    print()
    print(title)
    print("=" * 100)
    print("Sin registros." if frame.empty else frame.to_string(index=False))


def main() -> int:
    args = parse_args()
    print("PHASE 10.42R.2A SIGNAL-TO-FILL TIMING INTEGRITY AUDIT")
    print("=" * 100)
    print("Report-only audit. No signals, orders, evidence writes or automation.")
    print("Same-candle close is diagnostic-only; next-bar open is the corrected fill.")
    print(f"Preflight only: {args.preflight_only}")

    try:
        result = run_signal_to_fill_timing_integrity_audit(
            preflight_only=args.preflight_only,
        )
    except Exception as exc:
        print(f"FAIL-CLOSED ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    for key, title in (
        ("summary", "AUDIT SUMMARY"),
        ("checks", "AUDIT CHECKS"),
        ("r2_report_lineage", "PHASE 10.42R.2 REPORT LINEAGE"),
        ("long_stage_report_lineage", "LONG STAGE-SPECIFIC REPORT LINEAGE"),
        ("dataset_lineage", "DATASET LINEAGE"),
        ("source_contract_audit", "SOURCE TIMING CONTRACTS"),
        ("short_timing_aggregate", "SHORT SAME-CLOSE VS NEXT-OPEN"),
        ("short_r2_reproduction", "SHORT PHASE 10.42R.2 REPRODUCTION"),
        ("long_timing_metrics", "LONG SAME-CLOSE VS NEXT-OPEN"),
        (
            "long_historical_reproduction",
            "LONG PHASE 8.4 HISTORICAL REPRODUCTION",
        ),
        (
            "long_r2_reproduction",
            "LONG PHASE 8.10 TO PHASE 10.42R.2 READINESS LINEAGE",
        ),
        ("cost_accounting_audit", "COST ACCOUNTING OVERLAP AUDIT"),
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
    completed = bool(summary.get("audit_completed", False))
    return 0 if validation_passed and completed else 1


if __name__ == "__main__":
    sys.exit(main())
