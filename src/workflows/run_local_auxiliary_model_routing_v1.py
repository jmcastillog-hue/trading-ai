from __future__ import annotations

import json
import sys

from src.integration.local_auxiliary_model_routing_v1 import (
    ROUTING_SCHEMA_VERSION,
    RoutingFailure,
    execute_request,
    parse_request_bytes,
)


def main() -> int:
    if len(sys.argv) != 1:
        return 20

    try:
        payload = sys.stdin.buffer.read(16385)
        request = parse_request_bytes(payload)
        response = execute_request(request)
    except RoutingFailure as exc:
        failure = {
            "routing_schema_version": ROUTING_SCHEMA_VERSION,
            "decision": "LOCAL_AUXILIARY_MODEL_ROUTER_FAILED_CLOSED",
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
            "routing_schema_version": ROUTING_SCHEMA_VERSION,
            "decision": "LOCAL_AUXILIARY_MODEL_ROUTER_FAILED_CLOSED",
            "error_id": "LOCAL_ROUTER_E008_INTERNAL_FAIL_CLOSED",
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
