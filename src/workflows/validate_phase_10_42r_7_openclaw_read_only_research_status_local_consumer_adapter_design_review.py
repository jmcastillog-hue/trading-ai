from __future__ import annotations

import argparse
import json

from src.validation.phase_10_42r_7_openclaw_read_only_research_status_local_consumer_adapter_design_review_v1 import (
    validate_phase_10_42r_7,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    summary = validate_phase_10_42r_7(preflight_only=args.preflight_only)
    print(json.dumps(summary, sort_keys=True, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
