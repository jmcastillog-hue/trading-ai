from __future__ import annotations

import argparse
import json

from src.long_side.long_forward_observation_phase_10_45_official_dataset_controlled_empty_initialization_v1 import preflight_official
from src.validation.phase_10_45_long_official_dataset_controlled_empty_initialization_v1 import validate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--authorize-gate-b", action="store_true", help="Reserved for a separately approved Gate B entry point; rejected here.")
    args = parser.parse_args()
    if args.authorize_gate_b:
        print(json.dumps({"validation_passed": False, "error": "GATE_B_NOT_AUTHORIZED_BY_VALIDATION_WORKFLOW"}, sort_keys=True))
        return 2
    if args.preflight_only:
        result = preflight_official(".")
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["state"] == "CLEAN_EMPTY" else 1
    result = validate(verify_git=True, write_reports=True)
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 0 if result["summary"]["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
