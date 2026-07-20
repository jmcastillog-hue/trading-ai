from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.validation.phase_10_42r_3_master_disposition_and_openclaw_read_only_integration_planning_v1 import (
    validate_phase_10_42r_3,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    arguments = parser.parse_args()

    result = validate_phase_10_42r_3(
        preflight_only=arguments.preflight_only,
        root=arguments.root,
        write_outputs=not arguments.no_write,
    )
    print(json.dumps(result["summary"], sort_keys=True, indent=2))
    return 0 if result["summary"]["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
