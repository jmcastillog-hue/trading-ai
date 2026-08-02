from __future__ import annotations

import json
import sys
from pathlib import Path

from src.integration.openclaw_controlled_read_only_research_workflow_v1 import (
    OpenClawResearchWorkflowFailure,
    execute_workflow_token,
)


def main() -> int:
    if len(sys.argv) != 2:
        return 20
    try:
        response = execute_workflow_token(
            sys.argv[1],
            root=Path("."),
        )
    except OpenClawResearchWorkflowFailure as exc:
        print(
            json.dumps(
                {
                    "error_id": exc.error_id,
                    "exit_code": exc.exit_code,
                    "failure_mode": "FAIL_CLOSED",
                    "message": str(exc),
                    "partial_response_emitted": False,
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ),
            file=sys.stderr,
        )
        return exc.exit_code
    except Exception as exc:  # pragma: no cover
        print(
            json.dumps(
                {
                    "error_id": (
                        "OPENCLAW_RESEARCH_WORKFLOW_E007_INTERNAL_FAIL_CLOSED"
                    ),
                    "exit_code": 70,
                    "failure_mode": "FAIL_CLOSED",
                    "message": (
                        f"Internal fail-closed error: {type(exc).__name__}"
                    ),
                    "partial_response_emitted": False,
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ),
            file=sys.stderr,
        )
        return 70

    print(
        json.dumps(
            response,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
