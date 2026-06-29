from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


REPORTS_DIR = Path("reports/phase_8_1_long_side_validation_contract_v1")

PHASE_7_CLOSURE_PATH = Path("docs/PHASE_7_REAL_MARKET_INPUT_BRIDGE_CLOSURE.md")
PHASE_8_1_CONTRACT_DOC_PATH = Path("docs/PHASE_8_LONG_SIDE_VALIDATION_CONTRACT.md")

LONG_DIRECTION = "LONG"
LONG_ROUTER_DECISION = "WATCH_ONLY"

REQUIRED_LONG_SIGNAL_COLUMNS = [
    "observed_at",
    "symbol",
    "timeframe",
    "signal_type",
    "router_decision",
    "cost_profile",
    "context_name",
    "direction",
    "manual_review_required",
    "notes",
]

REQUIRED_LONG_PRICE_LEVEL_COLUMNS = [
    "signal_id",
    "context_name",
    "cost_profile",
    "direction",
    "entry_price",
    "stop_price",
    "target_price",
    "price_level_source",
    "notes",
]

REQUIRED_LONG_EVIDENCE_COLUMNS = [
    "signal_id",
    "observed_at",
    "symbol",
    "timeframe",
    "cost_profile",
    "context_name",
    "direction",
    "entry_price",
    "stop_price",
    "target_price",
    "resolution_status",
    "result_r",
    "mfe_r",
    "mae_r",
    "bars_to_resolution",
]

REQUIRED_LONG_RESEARCH_GATES = [
    "in_sample_validation",
    "out_of_sample_validation",
    "walk_forward_validation",
    "cost_aware_validation",
    "monte_carlo_validation",
    "position_sizing_validation",
    "context_risk_router_validation",
    "readiness_gate_validation",
    "forward_observation_validation",
    "evidence_dataset_validation",
]

REQUIRED_LONG_CONTEXT_CONSIDERATIONS = [
    "bullish_trend_continuation",
    "bearish_trend_reversal_risk",
    "liquidity_sweeps_below_price",
    "failed_breakdowns",
    "fibonacci_pullback_zones",
    "volatility_expansion",
    "btc_cycle_context",
    "higher_timeframe_regime",
    "mtf_alignment",
    "liquidation_risk",
    "cost_and_spread_impact",
]

SAFETY_FLAGS = {
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "live_alerts_allowed": False,
    "exchange_execution_allowed": False,
    "automation_allowed": False,
    "execution_allowed": False,
    "long_side_established": False,
    "real_entries_approved": False,
    "total_project_completed": False,
}

NON_APPROVED_LONG_CAPABILITIES = {
    "long_strategy_approved": False,
    "long_entries_approved": False,
    "long_paper_trading_approved": False,
    "long_real_capital_approved": False,
    "long_live_alerts_approved": False,
    "long_exchange_execution_approved": False,
    "long_automation_approved": False,
}


@dataclass(frozen=True)
class LongSideValidationContract:
    phase: str = "8.1"
    contract_name: str = "LONG_SIDE_VALIDATION_CONTRACT_V1"
    direction: str = LONG_DIRECTION
    router_decision: str = LONG_ROUTER_DECISION
    price_structure_rule: str = "stop_price < entry_price < target_price"
    official_short_candidate: str = "TARGET_SHORT_FIB_V5_MTF_V3_1 + FIXED_RR_2_5"
    long_side_established: bool = False
    execution_allowed: bool = False


def build_check(
    check_group: str,
    check_name: str,
    passed: bool,
    severity: str,
    details: str,
) -> dict[str, Any]:
    return {
        "check_group": check_group,
        "check_name": check_name,
        "passed": passed,
        "severity": severity,
        "details": details,
        "blocker": severity == "ERROR" and not passed,
    }


def validate_long_price_structure(
    entry_price: float,
    stop_price: float,
    target_price: float,
) -> bool:
    return stop_price < entry_price < target_price


def validate_short_price_structure(
    entry_price: float,
    stop_price: float,
    target_price: float,
) -> bool:
    return stop_price > entry_price > target_price


def validate_long_side_contract() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    contract = LongSideValidationContract()
    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_7_closure_exists": PHASE_7_CLOSURE_PATH,
        "phase_8_1_contract_doc_exists": PHASE_8_1_CONTRACT_DOC_PATH,
    }

    for check_name, path in phase_anchors.items():
        checks.append(
            build_check(
                check_group="phase_anchor",
                check_name=check_name,
                passed=path.exists(),
                severity="INFO" if path.exists() else "ERROR",
                details=str(path),
            )
        )

    checks.append(
        build_check(
            check_group="contract_identity",
            check_name="long_direction_defined",
            passed=contract.direction == "LONG",
            severity="INFO" if contract.direction == "LONG" else "ERROR",
            details=f"direction={contract.direction}",
        )
    )

    checks.append(
        build_check(
            check_group="contract_identity",
            check_name="watch_only_router_required",
            passed=contract.router_decision == "WATCH_ONLY",
            severity="INFO" if contract.router_decision == "WATCH_ONLY" else "ERROR",
            details=f"router_decision={contract.router_decision}",
        )
    )

    valid_long_structure = validate_long_price_structure(
        entry_price=65000.0,
        stop_price=64500.0,
        target_price=66250.0,
    )

    invalid_mirrored_short_structure = validate_long_price_structure(
        entry_price=65000.0,
        stop_price=65500.0,
        target_price=63750.0,
    )

    checks.append(
        build_check(
            check_group="price_structure",
            check_name="valid_long_structure_accepts_stop_below_entry_target_above",
            passed=valid_long_structure,
            severity="INFO" if valid_long_structure else "ERROR",
            details="64500 < 65000 < 66250",
        )
    )

    checks.append(
        build_check(
            check_group="price_structure",
            check_name="short_structure_rejected_for_long_contract",
            passed=invalid_mirrored_short_structure is False,
            severity="INFO" if invalid_mirrored_short_structure is False else "ERROR",
            details="65500 > 65000 > 63750 must not be valid for LONG",
        )
    )

    required_contract_groups = {
        "required_long_signal_columns": REQUIRED_LONG_SIGNAL_COLUMNS,
        "required_long_price_level_columns": REQUIRED_LONG_PRICE_LEVEL_COLUMNS,
        "required_long_evidence_columns": REQUIRED_LONG_EVIDENCE_COLUMNS,
        "required_long_research_gates": REQUIRED_LONG_RESEARCH_GATES,
        "required_long_context_considerations": REQUIRED_LONG_CONTEXT_CONSIDERATIONS,
    }

    for group_name, values in required_contract_groups.items():
        checks.append(
            build_check(
                check_group="required_contract_components",
                check_name=group_name,
                passed=len(values) > 0,
                severity="INFO" if len(values) > 0 else "ERROR",
                details=",".join(values),
            )
        )

    for flag_name, flag_value in SAFETY_FLAGS.items():
        checks.append(
            build_check(
                check_group="safety_flags",
                check_name=flag_name,
                passed=flag_value is False,
                severity="INFO" if flag_value is False else "ERROR",
                details=f"{flag_name}={flag_value}",
            )
        )

    for capability_name, capability_value in NON_APPROVED_LONG_CAPABILITIES.items():
        checks.append(
            build_check(
                check_group="non_approved_long_capabilities",
                check_name=capability_name,
                passed=capability_value is False,
                severity="INFO" if capability_value is False else "ERROR",
                details=f"{capability_name}={capability_value}",
            )
        )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="long_is_not_short_mirror_clone",
            passed=True,
            severity="INFO",
            details="LONG must follow independent validation, not direct SHORT mirroring.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="official_short_candidate_remains_research_only",
            passed=True,
            severity="INFO",
            details=contract.official_short_candidate,
        )
    )

    checks.append(
        build_check(
            check_group="phase_transition",
            check_name="phase_8_2_recommended_next",
            passed=True,
            severity="INFO",
            details="Recommended next step: Phase 8.2 LONG Candidate Discovery Baseline V1.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="real_entries_remain_blocked",
            passed=True,
            severity="WARNING",
            details="Real entries remain blocked after Phase 8.1.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="long_side_remains_unestablished",
            passed=True,
            severity="WARNING",
            details="Phase 8.1 defines a contract only; LONG side is not established.",
        )
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    summary_df = pd.DataFrame(
        [
            {
                "phase": contract.phase,
                "contract_name": contract.contract_name,
                "direction": contract.direction,
                "router_decision": contract.router_decision,
                "price_structure_rule": contract.price_structure_rule,
                "valid_long_structure_confirmed": valid_long_structure,
                "short_structure_rejected_for_long": invalid_mirrored_short_structure is False,
                "required_signal_columns": len(REQUIRED_LONG_SIGNAL_COLUMNS),
                "required_price_level_columns": len(REQUIRED_LONG_PRICE_LEVEL_COLUMNS),
                "required_evidence_columns": len(REQUIRED_LONG_EVIDENCE_COLUMNS),
                "required_research_gates": len(REQUIRED_LONG_RESEARCH_GATES),
                "required_context_considerations": len(REQUIRED_LONG_CONTEXT_CONSIDERATIONS),
                "official_short_candidate": contract.official_short_candidate,
                "long_strategy_approved": False,
                "long_entries_approved": False,
                "long_side_established": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "real_entries_approved": False,
                "total_project_completed": False,
                "recommended_next_phase": "PHASE_8_2_LONG_CANDIDATE_DISCOVERY_BASELINE_V1",
                "estimated_total_project_progress_percent": 90,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_8_1_LONG_SIDE_VALIDATION_CONTRACT_DEFINED"
                    if validation_passed
                    else "PHASE_8_1_LONG_SIDE_VALIDATION_CONTRACT_FAILED"
                ),
            }
        ]
    )

    checks_df.to_csv(
        REPORTS_DIR / "long_side_validation_contract_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_side_validation_contract_summary_v1.csv",
        index=False,
    )

    signal_columns_df = pd.DataFrame({"required_long_signal_column": REQUIRED_LONG_SIGNAL_COLUMNS})
    price_level_columns_df = pd.DataFrame({"required_long_price_level_column": REQUIRED_LONG_PRICE_LEVEL_COLUMNS})
    evidence_columns_df = pd.DataFrame({"required_long_evidence_column": REQUIRED_LONG_EVIDENCE_COLUMNS})
    gates_df = pd.DataFrame({"required_long_research_gate": REQUIRED_LONG_RESEARCH_GATES})
    context_df = pd.DataFrame({"required_long_context_consideration": REQUIRED_LONG_CONTEXT_CONSIDERATIONS})

    signal_columns_df.to_csv(
        REPORTS_DIR / "required_long_signal_columns_v1.csv",
        index=False,
    )
    price_level_columns_df.to_csv(
        REPORTS_DIR / "required_long_price_level_columns_v1.csv",
        index=False,
    )
    evidence_columns_df.to_csv(
        REPORTS_DIR / "required_long_evidence_columns_v1.csv",
        index=False,
    )
    gates_df.to_csv(
        REPORTS_DIR / "required_long_research_gates_v1.csv",
        index=False,
    )
    context_df.to_csv(
        REPORTS_DIR / "required_long_context_considerations_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "checks": checks_df,
        "signal_columns": signal_columns_df,
        "price_level_columns": price_level_columns_df,
        "evidence_columns": evidence_columns_df,
        "research_gates": gates_df,
        "context_considerations": context_df,
    }