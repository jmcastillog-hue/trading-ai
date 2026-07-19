from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_forward_observation_phase_10_39_evidence_collection_official_dataset_schema_implementation_precheck_v1 import (
    BACKUP_DIR,
    EMPTY_SCHEMA_CANDIDATE_PATH,
    OFFICIAL_DATASET_EXPECTED_PATH,
    OFFICIAL_LOCK_PATH,
    OFFICIAL_MANIFEST_PATH,
    OFFICIAL_TEMP_PATH,
)
from src.long_side.long_forward_observation_phase_10_41_evidence_collection_official_dataset_empty_schema_candidate_validation_v1 import (
    EXPECTED_CANDIDATE_SHA256,
)
from src.market_structure.closed_candle_mtf import (
    source_uses_closed_candle_contract,
)


REPORTS_DIR = Path(
    "reports/phase_10_42r_project_scientific_integrity_"
    "and_reproducibility_audit_v1"
)

REQUIRED_DEPENDENCIES = {
    "numpy",
    "openpyxl",
    "pandas",
    "python-binance",
    "python-dotenv",
    "requests",
    "ta",
}

MTF_REGIME_PATH = Path("src/market_structure/mtf_regime_filter.py")
DIRECTIONAL_CONTEXT_PATH = Path(
    "src/market_structure/directional_context_filter_v3.py"
)
CLOSED_CANDLE_HELPER_PATH = Path(
    "src/market_structure/closed_candle_mtf.py"
)
CLOSED_CANDLE_TEST_PATH = Path("tests/test_closed_candle_mtf.py")
REQUIREMENTS_PATH = Path("requirements.txt")

VALIDATED_DECISION = (
    "PHASE_10_42R_PROJECT_SCIENTIFIC_INTEGRITY_AND_REPRODUCIBILITY_"
    "AUDIT_VALIDATED_REVALIDATION_REQUIRED"
)
FAILED_DECISION = (
    "PHASE_10_42R_PROJECT_SCIENTIFIC_INTEGRITY_AND_REPRODUCIBILITY_"
    "AUDIT_FAILED"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_42R_2_SHORT_LONG_CLOSED_CANDLE_MTF_REVALIDATION_V1"
)


def file_sha256(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_requirement_names(path: Path = REQUIREMENTS_PATH) -> set[str]:
    if not path.exists() or not path.is_file():
        return set()

    names: set[str] = set()
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        name = line
        for separator in ("==", ">=", "<=", "~=", "!=", ">", "<", "["):
            name = name.split(separator, 1)[0]
        names.add(name.strip().lower())
    return names


def build_check(
    name: str,
    passed: bool,
    severity: str,
    details: str,
    blocker: bool,
) -> dict[str, Any]:
    return {
        "check_position": 0,
        "check_name": name,
        "passed": bool(passed),
        "severity": severity,
        "details": details,
        "blocker": bool(blocker),
    }


def build_checks() -> pd.DataFrame:
    requirement_names = read_requirement_names()
    candidate_hash = file_sha256(EMPTY_SCHEMA_CANDIDATE_PATH)

    rows = [
        build_check(
            "closed_candle_helper_exists",
            CLOSED_CANDLE_HELPER_PATH.exists(),
            "ERROR",
            str(CLOSED_CANDLE_HELPER_PATH),
            not CLOSED_CANDLE_HELPER_PATH.exists(),
        ),
        build_check(
            "mtf_regime_uses_closed_candle_contract",
            source_uses_closed_candle_contract(MTF_REGIME_PATH),
            "ERROR",
            str(MTF_REGIME_PATH),
            not source_uses_closed_candle_contract(MTF_REGIME_PATH),
        ),
        build_check(
            "directional_context_uses_closed_candle_contract",
            source_uses_closed_candle_contract(DIRECTIONAL_CONTEXT_PATH),
            "ERROR",
            str(DIRECTIONAL_CONTEXT_PATH),
            not source_uses_closed_candle_contract(DIRECTIONAL_CONTEXT_PATH),
        ),
        build_check(
            "closed_candle_tests_exist",
            CLOSED_CANDLE_TEST_PATH.exists(),
            "ERROR",
            str(CLOSED_CANDLE_TEST_PATH),
            not CLOSED_CANDLE_TEST_PATH.exists(),
        ),
        build_check(
            "requirements_file_non_empty",
            REQUIREMENTS_PATH.exists() and REQUIREMENTS_PATH.stat().st_size > 0,
            "ERROR",
            str(REQUIREMENTS_PATH),
            not REQUIREMENTS_PATH.exists() or REQUIREMENTS_PATH.stat().st_size == 0,
        ),
        build_check(
            "required_dependencies_declared",
            REQUIRED_DEPENDENCIES.issubset(requirement_names),
            "ERROR",
            "missing=" + ",".join(sorted(REQUIRED_DEPENDENCIES - requirement_names)),
            not REQUIRED_DEPENDENCIES.issubset(requirement_names),
        ),
        build_check(
            "empty_schema_candidate_exists",
            EMPTY_SCHEMA_CANDIDATE_PATH.exists(),
            "ERROR",
            str(EMPTY_SCHEMA_CANDIDATE_PATH),
            not EMPTY_SCHEMA_CANDIDATE_PATH.exists(),
        ),
        build_check(
            "empty_schema_candidate_hash_stable",
            candidate_hash == EXPECTED_CANDIDATE_SHA256,
            "ERROR",
            f"sha256={candidate_hash}",
            candidate_hash != EXPECTED_CANDIDATE_SHA256,
        ),
        build_check(
            "official_dataset_absent",
            not OFFICIAL_DATASET_EXPECTED_PATH.exists(),
            "ERROR",
            str(OFFICIAL_DATASET_EXPECTED_PATH),
            OFFICIAL_DATASET_EXPECTED_PATH.exists(),
        ),
        build_check(
            "official_temp_absent",
            not OFFICIAL_TEMP_PATH.exists(),
            "ERROR",
            str(OFFICIAL_TEMP_PATH),
            OFFICIAL_TEMP_PATH.exists(),
        ),
        build_check(
            "official_lock_absent",
            not OFFICIAL_LOCK_PATH.exists(),
            "ERROR",
            str(OFFICIAL_LOCK_PATH),
            OFFICIAL_LOCK_PATH.exists(),
        ),
        build_check(
            "official_manifest_absent",
            not OFFICIAL_MANIFEST_PATH.exists(),
            "ERROR",
            str(OFFICIAL_MANIFEST_PATH),
            OFFICIAL_MANIFEST_PATH.exists(),
        ),
        build_check(
            "official_backup_absent",
            not BACKUP_DIR.exists(),
            "ERROR",
            str(BACKUP_DIR),
            BACKUP_DIR.exists(),
        ),
        build_check(
            "short_candidate_revalidation_required",
            True,
            "WARNING",
            "TARGET_SHORT_FIB_V5_MTF_V3_1 + FIXED_RR_2_5",
            False,
        ),
        build_check(
            "long_candidates_revalidation_required",
            True,
            "WARNING",
            "All LONG candidates using MTF context remain non-operational.",
            False,
        ),
        build_check(
            "phase_10_43_paused",
            True,
            "WARNING",
            "Atomic-write design review remains paused until scientific revalidation.",
            False,
        ),
    ]

    for position, row in enumerate(rows, start=1):
        row["check_position"] = position

    return pd.DataFrame(rows)


def build_findings() -> pd.DataFrame:
    rows = [
        {
            "finding_id": "FINDING_001",
            "severity": "CRITICAL",
            "area": "SCIENTIFIC_INTEGRITY",
            "finding": (
                "Higher-timeframe indicators were previously timestamped at candle "
                "open although they used the complete candle close."
            ),
            "remediation": (
                "Expose 1H and 4H features only at open timestamp plus timeframe "
                "duration."
            ),
            "current_state": "CODE_REMEDIATED_REVALIDATION_PENDING",
        },
        {
            "finding_id": "FINDING_002",
            "severity": "CRITICAL",
            "area": "CANDIDATE_STATUS",
            "finding": (
                "Historical SHORT and LONG metrics that used the affected MTF "
                "context are not certified after remediation."
            ),
            "remediation": "Repeat historical, OOS, walk-forward, cost and risk gates.",
            "current_state": "REVALIDATION_REQUIRED",
        },
        {
            "finding_id": "FINDING_003",
            "severity": "HIGH",
            "area": "REPRODUCIBILITY",
            "finding": "The dependency manifest was empty.",
            "remediation": "Declare the validated local Python dependency versions.",
            "current_state": "MANIFEST_RESTORED",
        },
        {
            "finding_id": "FINDING_004",
            "severity": "HIGH",
            "area": "OPENCLAW_READINESS",
            "finding": (
                "OpenClaw must not treat historical validation results as current "
                "readiness evidence."
            ),
            "remediation": (
                "Keep every execution capability disabled and expose only a future "
                "read-only JSON status command."
            ),
            "current_state": "OPENCLAW_INTEGRATION_BLOCKED",
        },
    ]
    return pd.DataFrame(rows)


def build_candidate_status() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "candidate_id": "TARGET_SHORT_FIB_V5_MTF_V3_1 + FIXED_RR_2_5",
                "previous_status": "PAPER_TRADING_CANDIDATE / FORWARD_OBSERVATION_CANDIDATE",
                "current_status": "REVALIDATION_REQUIRED",
                "historical_metrics_certified": False,
                "forward_observation_allowed": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "execution_allowed": False,
            },
            {
                "candidate_id": "LONG_BASE_FAILED_BREAKDOWN_V1",
                "previous_status": "LONG_FORWARD_OBSERVATION_CANDIDATE",
                "current_status": "REVALIDATION_REQUIRED",
                "historical_metrics_certified": False,
                "forward_observation_allowed": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "execution_allowed": False,
            },
            {
                "candidate_id": "LONG_BASE_LIQUIDITY_SWEEP_V1",
                "previous_status": "LONG_SECONDARY_WATCHLIST",
                "current_status": "REVALIDATION_REQUIRED",
                "historical_metrics_certified": False,
                "forward_observation_allowed": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "execution_allowed": False,
            },
        ]
    )


def build_summary(checks: pd.DataFrame) -> pd.DataFrame:
    blocker_count = int(checks["blocker"].astype(bool).sum())
    error_count = int(
        (checks["severity"].eq("ERROR") & ~checks["passed"].astype(bool)).sum()
    )
    warning_count = int(checks["severity"].eq("WARNING").sum())
    validation_passed = blocker_count == 0 and error_count == 0

    return pd.DataFrame(
        [
            {
                "phase": "10.42R",
                "audit_scope": "PROJECT_SCIENTIFIC_INTEGRITY_AND_REPRODUCIBILITY",
                "closed_candle_mtf_contract_implemented": validation_passed,
                "short_candidate_status": "REVALIDATION_REQUIRED",
                "long_candidate_status": "REVALIDATION_REQUIRED",
                "historical_metrics_certified": False,
                "scientific_revalidation_completed": False,
                "forward_observation_allowed": False,
                "phase_10_43_allowed": False,
                "openclaw_read_only_integration_allowed": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "official_dataset_exists": OFFICIAL_DATASET_EXPECTED_PATH.exists(),
                "official_evidence_rows_written": 0,
                "total_checks": len(checks),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    VALIDATED_DECISION if validation_passed else FAILED_DECISION
                ),
                "recommended_next_phase": RECOMMENDED_NEXT_PHASE,
                "total_project_completed": False,
            }
        ]
    )


def run_project_scientific_integrity_and_reproducibility_audit() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks = build_checks()
    findings = build_findings()
    candidate_status = build_candidate_status()
    summary = build_summary(checks)

    outputs = {
        "summary": summary,
        "checks": checks,
        "findings": findings,
        "candidate_status": candidate_status,
    }

    for name, frame in outputs.items():
        frame.to_csv(REPORTS_DIR / f"{name}_v1.csv", index=False)

    return outputs
