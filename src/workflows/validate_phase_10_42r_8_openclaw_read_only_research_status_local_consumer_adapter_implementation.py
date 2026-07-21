from __future__ import annotations

import argparse
import json

from src.validation.phase_10_42r_8_openclaw_read_only_research_status_local_consumer_adapter_implementation_v1 import (
    validate_phase_10_42r_8,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()

    result = validate_phase_10_42r_8(
        preflight_only=args.preflight_only,
        write_reports=True,
    )
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 0 if result["summary"]["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
