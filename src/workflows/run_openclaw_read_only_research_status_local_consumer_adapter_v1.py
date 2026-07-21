from __future__ import annotations

import sys

from src.integration.openclaw_read_only_research_status_local_consumer_adapter_v1 import (
    run_stdio_adapter,
)


def main() -> int:
    if len(sys.argv) != 1:
        return 20
    return run_stdio_adapter()


if __name__ == "__main__":
    raise SystemExit(main())
