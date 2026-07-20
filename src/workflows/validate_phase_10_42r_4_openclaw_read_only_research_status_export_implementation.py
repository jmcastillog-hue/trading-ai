from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.validation.phase_10_42r_4_openclaw_read_only_research_status_export_implementation_v1 import (
    validate_phase_10_42r_4,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Phase 10.42R.4.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--allow-no-git", action="store_true")
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    summary = validate_phase_10_42r_4(
        root=Path(arguments.root),
        preflight_only=arguments.preflight_only,
        write_outputs=not arguments.no_write,
        require_git=not arguments.allow_no_git,
    )
    print(json.dumps(summary, sort_keys=True, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
