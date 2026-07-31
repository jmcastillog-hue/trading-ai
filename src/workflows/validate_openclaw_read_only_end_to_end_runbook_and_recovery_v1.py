from __future__ import annotations

import json
from pathlib import Path

from src.validation.openclaw_read_only_end_to_end_runbook_and_recovery_v1 import (
    validate_phase_11_2,
)


REPORT_PATH = Path("reports/phase_11_2/validation_summary.json")


def main() -> int:
    result = validate_phase_11_2()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True))
    return 0 if result["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
