from __future__ import annotations

import argparse
import sys

import pandas as pd

from src.validation.recovery_candidate_family_specification_and_multiplicity_freeze_v1 import (
    REPORTS_DIR,
    validate_phase_10_42r_2d,
)


def print_frame(title: str, frame: pd.DataFrame) -> None:
    print()
    print(title)
    print("=" * 100)
    print("Sin registros." if frame.empty else frame.to_string(index=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Freeze Phase 10.42R.2D candidate-family, variant, timing, cost, "
            "multiplicity and promotion-gate specifications without evaluation."
        )
    )
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Validate Phase 2C lineage and safety boundaries without freezing rows.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    print("PHASE 10.42R.2D RECOVERY CANDIDATE SPECIFICATION AND MULTIPLICITY FREEZE")
    print("=" * 100)
    print("Specification only: no backtest, metric calculation, comparison or winner.")
    print("The retired SHORT is immutable and cannot be imported or repaired in place.")
    print("Both holdouts remain absent and every execution/OpenClaw permission remains false.")

    try:
        result = validate_phase_10_42r_2d(
            preflight_only=bool(args.preflight_only)
        )
    except Exception as exc:
        print(f"FAIL-CLOSED ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    for key, title in (
        ("summary", "PHASE SUMMARY"),
        ("checks", "FAIL-CLOSED VALIDATION CHECKS"),
        ("phase_2c_report_lineage", "FROZEN PHASE 2C REPORT LINEAGE"),
        ("acceptance_criteria", "EXPLICIT ACCEPTANCE CRITERIA"),
        ("candidate_family_registry", "NEW CANDIDATE FAMILY REGISTRY — NOT EVALUATED"),
        ("candidate_variant_registry", "FROZEN VARIANT REGISTRY — NOT EVALUATED"),
        ("evaluation_order", "EVALUATION ORDER — NOT PERFORMANCE RANK"),
        ("multiplicity_contract", "MULTIPLICITY CONTRACT"),
        ("promotion_gate_contract", "PROMOTION GATES"),
        ("holdout_boundary", "SEALED HOLDOUT BOUNDARY"),
        ("specification_artifact_manifest", "CANONICAL ARTIFACT MANIFEST"),
        ("specification_root", "SPECIFICATION ROOT SHA-256"),
        ("errors", "ERRORS"),
    ):
        print_frame(title, result.get(key, pd.DataFrame()))

    print()
    print("REPORT DIRECTORY")
    print("=" * 100)
    print(REPORTS_DIR)

    summary = result["summary"].iloc[0]
    return 0 if bool(summary.get("validation_passed", False)) else 1


if __name__ == "__main__":
    sys.exit(main())
