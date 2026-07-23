from __future__ import annotations

import json

from src.validation.phase_10_44_long_official_dataset_atomic_write_harness_implementation_v1 import validate


def main() -> int:
    result = validate(verify_git=True, write_reports=True)
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 0 if result["summary"]["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
