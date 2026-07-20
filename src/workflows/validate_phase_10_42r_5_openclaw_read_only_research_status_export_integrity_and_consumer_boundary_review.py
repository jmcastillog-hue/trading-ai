from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.validation.phase_10_42r_5_openclaw_read_only_research_status_export_integrity_and_consumer_boundary_review_v1 import (
    validate_phase_10_42r_5,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--root", default=".")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    try:
        result = validate_phase_10_42r_5(
            root=Path(args.root),
            preflight_only=args.preflight_only,
            write_outputs=not args.no_write,
            require_git=True,
        )
    except Exception as exc:
        print(f"Phase 10.42R.5 validation failed: {type(exc).__name__}: {exc}")
        return 1
    print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
