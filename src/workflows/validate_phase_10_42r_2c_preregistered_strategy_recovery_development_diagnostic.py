from __future__ import annotations

import argparse
import sys

import pandas as pd

from src.validation.preregistered_strategy_recovery_development_diagnostic_v1 import (
    REPORTS_DIR,
    validate_phase_10_42r_2c,
)


def print_frame(title: str, frame: pd.DataFrame) -> None:
    print()
    print(title)
    print("=" * 100)
    print("Sin registros." if frame.empty else frame.to_string(index=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate Phase 10.42R.2C report-only diagnostics on known "
            "2022-2025 evidence."
        )
    )
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Validate lineage, local datasets and safety gates without diagnostics.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    print("PHASE 10.42R.2C PREREGISTERED STRATEGY-RECOVERY DEVELOPMENT DIAGNOSTIC")
    print("=" * 100)
    print("Known 2022-2025 data only. Descriptive output; no ranking or selection.")
    print("The rejected SHORT remains retired and immutable.")
    print("No holdout access, forward write, signals, orders, automation or OpenClaw operation.")

    try:
        result = validate_phase_10_42r_2c(
            preflight_only=bool(args.preflight_only)
        )
    except Exception as exc:
        print(f"FAIL-CLOSED ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    for key, title in (
        ("summary", "PHASE SUMMARY"),
        ("checks", "VALIDATION CHECKS"),
        ("phase_2b_report_lineage", "PHASE 10.42R.2B SOURCE LINEAGE"),
        ("dataset_lineage", "IMMUTABLE KNOWN-DATA LINEAGE"),
        ("diagnostic_contract", "LOCKED DIAGNOSTIC CONTRACT"),
        ("acceptance_criteria", "EXPLICIT ACCEPTANCE CRITERIA"),
        ("volatility_thresholds", "OUTCOME-INDEPENDENT VOLATILITY THRESHOLDS"),
        ("slice_coverage", "PREREGISTERED SLICE COVERAGE"),
        ("errors", "ERRORS"),
    ):
        print_frame(title, result[key])

    metrics = result["slice_metrics"]
    if not metrics.empty:
        base = metrics[
            metrics["cost_profile"].eq("BINANCE_SCALP_BASE_ESTIMATE")
        ][
            [
                "slice_dimension",
                "slice_value",
                "trade_rows",
                "normalized_average_result_r",
                "normalized_profit_factor",
                "normalized_max_drawdown_r",
                "positive_window_rate",
                "frictionless_average_result_r",
                "gross_edge_to_profile_cost_ratio",
            ]
        ]
        print_frame("BINANCE BASE DIAGNOSTIC SLICES — NOT RANKED", base)

    print()
    print("REPORT DIRECTORY")
    print("=" * 100)
    print(REPORTS_DIR)

    summary = result["summary"].iloc[0]
    return 0 if bool(summary.get("validation_passed", False)) else 1


if __name__ == "__main__":
    sys.exit(main())
