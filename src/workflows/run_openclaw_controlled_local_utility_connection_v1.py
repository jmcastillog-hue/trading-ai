from __future__ import annotations

import json
import sys

from src.integration.openclaw_controlled_local_utility_connection_v1 import (
    CONNECTION_SCHEMA_VERSION,
    OpenClawLocalUtilityFailure,
    execute_request_token,
)


def main() -> int:
    if len(sys.argv) != 2:
        return 20

    try:
        response = execute_request_token(sys.argv[1])
    except OpenClawLocalUtilityFailure as exc:
        failure = {
            "connection_schema_version": CONNECTION_SCHEMA_VERSION,
            "decision": "OPENCLAW_CONTROLLED_LOCAL_UTILITY_FAILED_CLOSED",
            "error_id": exc.error_id,
            "error": str(exc),
            "all_operational_permissions_allowed": False,
        }
        print(
            json.dumps(
                failure,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            ),
            file=sys.stderr,
        )
        return exc.exit_code
    except Exception as exc:
        failure = {
            "connection_schema_version": CONNECTION_SCHEMA_VERSION,
            "decision": "OPENCLAW_CONTROLLED_LOCAL_UTILITY_FAILED_CLOSED",
            "error_id": (
                "OPENCLAW_LOCAL_UTILITY_E005_INTERNAL_FAIL_CLOSED"
            ),
            "error": str(exc),
            "all_operational_permissions_allowed": False,
        }
        print(
            json.dumps(
                failure,
                indent=2,
                sort_keys=True,
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
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
