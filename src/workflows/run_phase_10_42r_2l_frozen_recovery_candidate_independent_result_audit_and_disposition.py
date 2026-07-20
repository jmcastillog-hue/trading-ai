from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.validation.frozen_recovery_candidate_independent_result_audit_and_disposition_validation_v1 import (
    validate_phase_10_42r_2l,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    arguments = parser.parse_args()
    result = validate_phase_10_42r_2l(
        preflight_only=arguments.preflight_only,
        root=arguments.root,
        write_outputs=not arguments.no_write,
    )
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    if not arguments.preflight_only and "dispositions" in result:
        frame = result["dispositions"]
        print(
            json.dumps(
                {"variant_dispositions": frame.to_dict(orient="records")},
                indent=2,
                sort_keys=True,
            )
        )
    return 0 if result["summary"]["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
