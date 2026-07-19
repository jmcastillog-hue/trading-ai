from __future__ import annotations

import sys

import pandas as pd

from src.validation.project_scientific_integrity_and_reproducibility_audit_v1 import (
    REPORTS_DIR,
    run_project_scientific_integrity_and_reproducibility_audit,
)


def print_section(title: str, frame: pd.DataFrame) -> None:
    print()
    print(title)
    print("=" * 100)
    print("Sin registros." if frame.empty else frame.to_string(index=False))


def main() -> int:
    print("PHASE 10.42R PROJECT SCIENTIFIC INTEGRITY AND REPRODUCIBILITY AUDIT")
    print("=" * 100)
    print(
        "Purpose: enforce completed higher-timeframe candles, preserve every "
        "execution prohibition and mark affected strategy evidence for revalidation."
    )

    result = run_project_scientific_integrity_and_reproducibility_audit()

    print_section("AUDIT SUMMARY", result["summary"])
    print_section("AUDIT CHECKS", result["checks"])
    print_section("AUDIT FINDINGS", result["findings"])
    print_section("CANDIDATE STATUS", result["candidate_status"])

    print()
    print("REPORT FILES")
    print("=" * 100)
    for filename in (
        "summary_v1.csv",
        "checks_v1.csv",
        "findings_v1.csv",
        "candidate_status_v1.csv",
    ):
        print(f"- {REPORTS_DIR / filename}")

    summary = result["summary"].iloc[0]
    return 0 if bool(summary["validation_passed"]) else 1


if __name__ == "__main__":
    sys.exit(main())
