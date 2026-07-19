from __future__ import annotations

import argparse
import json

from src.validation.frozen_recovery_candidate_independent_code_review_v1 import (
    ReviewFailure,
    require_valid_review,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Phase 10.42R.2F source-only independent code review."
    )
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Verify frozen hashes, source isolation and permissions only.",
    )
    args = parser.parse_args()
    try:
        result = require_valid_review(preflight_only=args.preflight_only)
    except ReviewFailure as exc:
        print(str(exc))
        return 1
    print(json.dumps(result["summary"], sort_keys=True, indent=2))
    if not args.preflight_only:
        print(
            json.dumps(
                {
                    "confirmed_findings": result["confirmed_findings"],
                    "risks_not_demonstrated": result["risks_not_demonstrated"],
                    "optional_out_of_scope": result["optional_out_of_scope"],
                },
                sort_keys=True,
                indent=2,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
