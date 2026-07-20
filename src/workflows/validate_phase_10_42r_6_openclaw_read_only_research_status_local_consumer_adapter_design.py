from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.validation.phase_10_42r_6_openclaw_read_only_research_status_local_consumer_adapter_design_v1 import (
    validate_phase_10_42r_6,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    arguments = parser.parse_args()

    result = validate_phase_10_42r_6(
        root=arguments.root,
        preflight_only=arguments.preflight_only,
        write_outputs=not arguments.no_write,
        require_source_authority=True,
    )
    print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
