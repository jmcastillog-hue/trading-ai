"""Run one canonical Phase 11.6 supervised query token."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from src.integration.openclaw_supervised_read_only_research_query_v1 import (
    execute_query_token,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the closed runner interface."""

    parser = argparse.ArgumentParser(
        description="Execute one canonical Phase 11.6 supervised query token."
    )
    parser.add_argument(
        "token",
        help="Canonical unpadded Base64URL query token.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Execute the token and emit one canonical JSON response."""

    args = build_parser().parse_args(argv)
    response = execute_query_token(args.token, root=REPOSITORY_ROOT)
    print(
        json.dumps(
            response,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
