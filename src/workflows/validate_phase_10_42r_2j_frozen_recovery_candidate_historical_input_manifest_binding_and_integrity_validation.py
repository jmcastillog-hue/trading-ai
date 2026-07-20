from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.validation.frozen_recovery_candidate_historical_input_manifest_binding_and_integrity_validation_v1 import (
    require_valid_binding,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate Phase 10.42R.2J historical input manifest binding "
            "and integrity without running any strategy evaluation."
        )
    )
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--full-details", action="store_true")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = require_valid_binding(
        preflight_only=args.preflight_only,
        root=args.root,
    )
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    if args.full_details:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
