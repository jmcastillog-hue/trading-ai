from __future__ import annotations

import argparse
import json
from typing import Any

from src.validation.frozen_recovery_candidate_controlled_historical_evaluation_harness_design_v1 import (
    require_valid_harness_design,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate Phase 10.42R.2I controlled historical "
            "evaluation harness design."
        )
    )
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Validate frozen anchors and safety boundary only.",
    )
    return parser


def _print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def main() -> None:
    args = build_parser().parse_args()
    result = require_valid_harness_design(preflight_only=args.preflight_only)
    _print_json(result["summary"])
    if not args.preflight_only:
        design = result["design"]
        _print_json({
            "finite_completion_route": design["finite_completion_route"],
            "repair_policy": design["repair_policy"],
            "dataset_slots": design["dataset_slots"],
            "components": design["components"],
            "state_transitions": design["state_transitions"],
            "failure_modes": design["failure_modes"],
            "audit_artifacts": design["audit_artifacts"],
            "permissions": result["permissions"],
            "failed_checks": result["failed_checks"],
        })


if __name__ == "__main__":
    main()
