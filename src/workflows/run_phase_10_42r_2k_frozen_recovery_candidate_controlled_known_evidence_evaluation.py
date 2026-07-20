from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.evaluation import (
    frozen_recovery_candidate_controlled_known_evidence_evaluation_v1 as evaluator,
)
from src.validation import (
    frozen_recovery_candidate_controlled_known_evidence_evaluation_validation_v1
    as validation,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run Phase 10.42R.2K controlled known-evidence evaluation. "
            "This never opens lockboxes, ranks variants, selects a winner, "
            "or grants operational permissions."
        )
    )
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Validate sources, binding and permissions without reading market content.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Run the evaluation in memory without publishing the audit bundle.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root. Defaults to the current working directory.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = args.root.resolve()

    preflight = validation.validate_preflight(root)
    print(json.dumps(preflight["summary"], indent=2, sort_keys=True))
    if not preflight["summary"]["validation_passed"]:
        print(json.dumps(preflight["failed_checks"], indent=2, sort_keys=True))
        return 1
    if args.preflight_only:
        return 0

    evaluation_result = evaluator.run_controlled_known_evidence_evaluation(
        root=root,
        write_outputs=not args.no_write,
        progress=True,
    )
    if args.no_write:
        print(json.dumps(evaluation_result["summary"], indent=2, sort_keys=True))
        return 0 if int(evaluation_result["summary"].get("blocker_count", 1)) == 0 else 1

    completed = validation.validate_completed_evaluation(
        evaluation_result,
        root=root,
    )
    print(json.dumps(completed["summary"], indent=2, sort_keys=True))
    if not completed["summary"]["validation_passed"]:
        print(json.dumps(completed["failed_checks"], indent=2, sort_keys=True))
        return 1

    classifications = (
        evaluation_result["gate_classification"]
        [["evaluation_order", "variant_id", "variant_gate_classification"]]
        .drop_duplicates()
        .sort_values("evaluation_order")
        .to_dict(orient="records")
    )
    print(json.dumps({"variant_classifications": classifications}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
