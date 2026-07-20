from __future__ import annotations

import argparse
import json

from src.validation.frozen_recovery_candidate_correction_independent_synthetic_acceptance_v1 import (
    require_valid_acceptance,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Validate Phase 10.42R.2G independent synthetic acceptance "
            "of the frozen recovery candidate correction."
        )
    )
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Run only source identity, registry, lineage, and permission checks.",
    )
    args = parser.parse_args()

    result = require_valid_acceptance(preflight_only=args.preflight_only)

    print(json.dumps(result["summary"], indent=2, sort_keys=True))

    if not args.preflight_only:
        print(
            json.dumps(
                {
                    "accepted_variant_ids": result["accepted_variant_ids"],
                    "failed_checks": [
                        check
                        for check in result["checks"]
                        if not check["passed"]
                    ],
                    "permissions": result["permissions"],
                },
                indent=2,
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
