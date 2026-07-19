from __future__ import annotations

import argparse
import sys

import pandas as pd

from src.validation.frozen_recovery_candidate_static_conformance_v1 import (
    REPORTS_DIR,
    validate_phase_10_42r_2e,
)


def _print_frame(title: str, frame: pd.DataFrame) -> None:
    print(f"\n{title}")
    print("=" * 100)
    if frame.empty:
        print("No rows.")
    else:
        print(frame.to_string(index=False))


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate Phase 10.42R.2E frozen implementation using only "
            "deterministic synthetic static-conformance fixtures."
        )
    )
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Verify the Phase 2D root and safety boundary without building implementations.",
    )
    args = parser.parse_args()
    try:
        outputs = validate_phase_10_42r_2e(preflight_only=args.preflight_only)
    except Exception as exc:
        print(
            f"FAIL-CLOSED: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 1

    print(
        "\nPHASE 10.42R.2E FROZEN IMPLEMENTATION AND STATIC/SYNTHETIC CONFORMANCE"
    )
    print("=" * 100)
    print("No real OHLCV, result report, holdout, backtest or performance metric is read.")
    print("Synthetic signals are conformance assertions, never operational signals.")

    _print_frame("PHASE SUMMARY", outputs["summary"])
    _print_frame("FAIL-CLOSED CHECKS", outputs["checks"])
    _print_frame("IMPLEMENTATION CATALOG — UNEVALUATED", outputs["implementation_catalog"])
    _print_frame("SYNTHETIC CONFORMANCE", outputs["synthetic_conformance"])
    _print_frame("IMPLEMENTATION MANIFEST", outputs["implementation_manifest"])
    _print_frame("IMPLEMENTATION ROOT", outputs["implementation_root"])
    _print_frame("PERMISSIONS", outputs["permissions_snapshot"])
    _print_frame("ERRORS", outputs["errors"])
    print(f"\nREPORT DIRECTORY\n{'=' * 100}\n{REPORTS_DIR}")

    summary = outputs["summary"].iloc[0]
    passed = bool(summary["validation_passed"])
    blockers = int(summary["blocker_count"])
    errors = int(summary["error_rows"])
    return 0 if passed and blockers == 0 and errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
