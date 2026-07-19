from __future__ import annotations

import sys

import pandas as pd

from src.validation.cost_accounting_normalization_and_strategy_recovery_preregistration_v1 import (
    REPORTS_DIR,
    validate_phase_10_42r_2b,
)


def print_frame(title: str, frame: pd.DataFrame) -> None:
    print()
    print(title)
    print("=" * 100)
    print("Sin registros." if frame.empty else frame.to_string(index=False))


def main() -> int:
    print("PHASE 10.42R.2B COST ACCOUNTING NORMALIZATION AND RECOVERY PREREGISTRATION")
    print("=" * 100)
    print("Report-only. Diagnostic normalized metrics cannot reclassify a strategy.")
    print("No holdout access, signals, evidence persistence, orders or automation.")

    try:
        result = validate_phase_10_42r_2b()
    except Exception as exc:
        print(f"FAIL-CLOSED ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    for key, title in (
        ("summary", "PHASE SUMMARY"),
        ("checks", "VALIDATION CHECKS"),
        ("r2a_report_lineage", "PHASE 10.42R.2A SOURCE LINEAGE"),
        ("accounting_contract", "CANONICAL GROSS-TO-NET CONTRACT"),
        ("normalized_short_summary", "NORMALIZED SHORT METRICS — DIAGNOSTIC ONLY"),
        ("recovery_preregistration", "LOCKED RECOVERY PREREGISTRATION"),
        ("holdout_contract", "SEALED HOLDOUT CONTRACT"),
        ("errors", "ERRORS"),
    ):
        print_frame(title, result[key])

    print()
    print("REPORT DIRECTORY")
    print("=" * 100)
    print(REPORTS_DIR)

    summary = result["summary"].iloc[0]
    return 0 if bool(summary.get("validation_passed", False)) else 1


if __name__ == "__main__":
    sys.exit(main())
