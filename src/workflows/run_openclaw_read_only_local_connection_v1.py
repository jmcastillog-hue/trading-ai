from __future__ import annotations

import sys

from src.integration.openclaw_read_only_local_connection_v1 import (
    run_cli,
)


def main() -> int:
    if len(sys.argv) != 1:
        return 20
    return run_cli()


if __name__ == "__main__":
    raise SystemExit(main())
