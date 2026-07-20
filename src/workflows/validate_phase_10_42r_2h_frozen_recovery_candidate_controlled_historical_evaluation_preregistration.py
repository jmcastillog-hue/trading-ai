from __future__ import annotations

import argparse
import json
from typing import Any

from src.validation.frozen_recovery_candidate_controlled_historical_evaluation_preregistration_v1 import (
    require_valid_preregistration,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate Phase 10.42R.2H controlled historical "
            "evaluation preregistration."
        )
    )
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Validate source anchors and safety boundaries only.",
    )
    return parser


def print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def main() -> None:
    args = build_parser().parse_args()
    result = require_valid_preregistration(
        preflight_only=args.preflight_only
    )
    print_json(result["summary"])

    if not args.preflight_only:
        protocol = result["protocol"]
        print_json(
            {
                "symbols": protocol["symbols"],
                "timeframes": protocol["timeframes"],
                "variant_ids": protocol["variants"],
                "evidence_windows": protocol["evidence_windows"],
                "cost_profiles": protocol["cost_profiles"],
                "multiplicity": protocol["multiplicity"],
                "promotion_gates": protocol["promotion_gates"],
                "permissions": result["permissions"],
                "failed_checks": result["failed_checks"],
            }
        )


if __name__ == "__main__":
    main()
