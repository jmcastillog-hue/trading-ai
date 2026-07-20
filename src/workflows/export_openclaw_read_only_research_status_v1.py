from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.integration.openclaw_read_only_research_status_export_v1 import (
    publish_status_export,
    validate_export_bundle,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Publish or validate the local OpenClaw read-only research status export."
    )
    parser.add_argument("--root", default=".")
    parser.add_argument("--output-dir")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--allow-no-git", action="store_true")
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    root = Path(arguments.root)
    if arguments.validate_only:
        result = validate_export_bundle(
            root,
            output_dir=arguments.output_dir,
            require_git=not arguments.allow_no_git,
        )
    else:
        result = publish_status_export(
            root,
            output_dir=arguments.output_dir,
            require_git=not arguments.allow_no_git,
        )
    print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
