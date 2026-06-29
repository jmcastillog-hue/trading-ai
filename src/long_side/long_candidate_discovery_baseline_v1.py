from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd


REPORTS_DIR = Path("reports/phase_8_2_long_candidate_discovery_baseline_v1")

PHASE_7_CLOSURE_PATH = Path("docs/PHASE_7_REAL_MARKET_INPUT_BRIDGE_CLOSURE.md")
PHASE_8_1_CONTRACT_DOC_PATH = Path("docs/PHASE_8_LONG_SIDE_VALIDATION_CONTRACT.md")
PHASE_8_1_CONTRACT_MODULE_PATH = Path("src/long_side/long_side_validation_contract_v1.py")
PHASE_8_2_DOC_PATH = Path("docs/PHASE_8_LONG_CANDIDATE_DISCOVERY_BASELINE.md")

LONG_DIRECTION = "LONG"
WATCH_ONLY_ROUTER_DECISION = "WATCH_ONLY"
DISCOVERY_APPROVAL_STATUS = "DISCOVERY_BASELINE_ONLY"

EXPECTED_CANDIDATES = [
    "LONG_BASE_FIB_PULLBACK_V1",
    "LONG_BASE_LIQUIDITY_SWEEP_V1",
    "LONG_BASE_MTF_BULLISH_CONTINUATION_V1",
    "LONG_BASE_FAILED_BREAKDOWN_V1",
]

SAFETY_FLAGS = {
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
}


@dataclass(frozen=True)
class LongCandidateDefinition:
    candidate_id: str
    direction: str
    router_decision: str
    hypothesis: str
    trigger_family: str
    primary_context: str
    entry_condition: str
    invalidation_rule: str
    confirmation_requirement: str
    price_structure_rule: str
    expected_signal_type: str
    evidence_goal: str
    known_failure_modes: str
    research_priority: int
    approval_status: str
    approved_for_execution: bool = False
    approved_for_paper_trading: bool = False
    approved_for_real_capital: bool = False
    approved_for_live_alerts: bool = False
    approved_for_automation: bool = False


def build_long_candidate_registry() -> list[LongCandidateDefinition]:
    return [
        LongCandidateDefinition(
            candidate_id="LONG_BASE_FIB_PULLBACK_V1",
            direction=LONG_DIRECTION,
            router_decision=WATCH_ONLY_ROUTER_DECISION,
            hypothesis=(
                "Bullish or recovering contexts may produce LONG opportunities "
                "after controlled pullbacks into Fibonacci zones."
            ),
            trigger_family="FIBONACCI_PULLBACK",
            primary_context="BULLISH_OR_BULLISH_TRANSITION_CONTEXT",
            entry_condition=(
                "Price pulls back into a predefined Fibonacci area and then "
                "shows confirmation before entry."
            ),
            invalidation_rule=(
                "Reject if price loses the pullback structure or if stop_price "
                "is not below entry_price."
            ),
            confirmation_requirement=(
                "Requires structural confirmation after pullback; no blind limit entry."
            ),
            price_structure_rule="stop_price < entry_price < target_price",
            expected_signal_type="LONG_ENTRY_SIGNAL",
            evidence_goal="Measure whether Fibonacci pullbacks produce positive R outcomes.",
            known_failure_modes=(
                "Trend reversal, catching falling knife, shallow bounce, "
                "late entry after move already expanded."
            ),
            research_priority=1,
            approval_status=DISCOVERY_APPROVAL_STATUS,
        ),
        LongCandidateDefinition(
            candidate_id="LONG_BASE_LIQUIDITY_SWEEP_V1",
            direction=LONG_DIRECTION,
            router_decision=WATCH_ONLY_ROUTER_DECISION,
            hypothesis=(
                "Sweeps below local lows followed by recovery may produce LONG "
                "opportunities when the breakdown fails."
            ),
            trigger_family="SELL_SIDE_LIQUIDITY_SWEEP",
            primary_context="FAILED_SELL_SIDE_SWEEP_RECOVERY",
            entry_condition=(
                "Price sweeps sell-side liquidity and reclaims the swept zone "
                "before entry confirmation."
            ),
            invalidation_rule=(
                "Reject if price remains below the swept low or if stop_price "
                "is not below entry_price."
            ),
            confirmation_requirement=(
                "Requires reclaim confirmation after the sweep; no entry during breakdown."
            ),
            price_structure_rule="stop_price < entry_price < target_price",
            expected_signal_type="LONG_ENTRY_SIGNAL",
            evidence_goal="Measure whether failed sell-side sweeps generate positive R.",
            known_failure_modes=(
                "Real bearish breakdown, liquidity sweep continuation, "
                "weak reclaim, high spread during volatility."
            ),
            research_priority=2,
            approval_status=DISCOVERY_APPROVAL_STATUS,
        ),
        LongCandidateDefinition(
            candidate_id="LONG_BASE_MTF_BULLISH_CONTINUATION_V1",
            direction=LONG_DIRECTION,
            router_decision=WATCH_ONLY_ROUTER_DECISION,
            hypothesis=(
                "Higher-timeframe bullish contexts may produce continuation LONG "
                "opportunities after lower-timeframe pullbacks."
            ),
            trigger_family="MTF_BULLISH_CONTINUATION",
            primary_context="HIGHER_TIMEFRAME_BULLISH_ALIGNMENT",
            entry_condition=(
                "Higher timeframe remains bullish while lower timeframe completes "
                "a controlled pullback and resumes upward structure."
            ),
            invalidation_rule=(
                "Reject if higher-timeframe context turns bearish or if stop_price "
                "is not below entry_price."
            ),
            confirmation_requirement=(
                "Requires MTF alignment and lower-timeframe continuation confirmation."
            ),
            price_structure_rule="stop_price < entry_price < target_price",
            expected_signal_type="LONG_ENTRY_SIGNAL",
            evidence_goal="Measure whether MTF bullish continuation produces stable R.",
            known_failure_modes=(
                "Late trend entry, higher-timeframe exhaustion, false continuation, "
                "volatility compression before reversal."
            ),
            research_priority=3,
            approval_status=DISCOVERY_APPROVAL_STATUS,
        ),
        LongCandidateDefinition(
            candidate_id="LONG_BASE_FAILED_BREAKDOWN_V1",
            direction=LONG_DIRECTION,
            router_decision=WATCH_ONLY_ROUTER_DECISION,
            hypothesis=(
                "Failed breakdowns below support may produce LONG opportunities "
                "after price rejects lower levels."
            ),
            trigger_family="FAILED_BREAKDOWN",
            primary_context="SUPPORT_BREAK_RECOVERY",
            entry_condition=(
                "Price breaks below support temporarily, fails to continue lower, "
                "and reclaims the breakdown zone."
            ),
            invalidation_rule=(
                "Reject if price accepts below support or if stop_price is not below entry_price."
            ),
            confirmation_requirement=(
                "Requires reclaim confirmation after failed breakdown."
            ),
            price_structure_rule="stop_price < entry_price < target_price",
            expected_signal_type="LONG_ENTRY_SIGNAL",
            evidence_goal="Measure whether failed breakdown recovery produces positive R.",
            known_failure_modes=(
                "Breakdown continuation, support-to-resistance flip, weak reclaim, "
                "range chop."
            ),
            research_priority=4,
            approval_status=DISCOVERY_APPROVAL_STATUS,
        ),
    ]


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


def candidate_registry_to_df(
    candidates: list[LongCandidateDefinition],
) -> pd.DataFrame:
    return pd.DataFrame([asdict(candidate) for candidate in candidates])


def build_controlled_price_level_fixture(
    candidates: list[LongCandidateDefinition],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    base_entry = 65000.0
    base_risk = 500.0
    base_reward = 1250.0

    for index, candidate in enumerate(candidates, start=1):
        entry_price = base_entry + float(index * 100)
        stop_price = entry_price - base_risk
        target_price = entry_price + base_reward

        rows.append(
            {
                "candidate_id": candidate.candidate_id,
                "direction": candidate.direction,
                "entry_price": entry_price,
                "stop_price": stop_price,
                "target_price": target_price,
                "risk": entry_price - stop_price,
                "reward": target_price - entry_price,
                "risk_reward": (target_price - entry_price) / (entry_price - stop_price),
                "valid_long_structure": validate_long_price_structure(
                    entry_price=entry_price,
                    stop_price=stop_price,
                    target_price=target_price,
                ),
                "approval_status": candidate.approval_status,
            }
        )

    return pd.DataFrame(rows)


def all_candidates_have_required_text(candidate_df: pd.DataFrame) -> bool:
    required_text_columns = [
        "candidate_id",
        "direction",
        "router_decision",
        "hypothesis",
        "trigger_family",
        "primary_context",
        "entry_condition",
        "invalidation_rule",
        "confirmation_requirement",
        "price_structure_rule",
        "expected_signal_type",
        "evidence_goal",
        "known_failure_modes",
        "approval_status",
    ]

    if candidate_df.empty:
        return False

    for column in required_text_columns:
        if column not in candidate_df.columns:
            return False

        if candidate_df[column].astype(str).str.strip().eq("").any():
            return False

    return True


def no_candidate_has_execution_approval(candidate_df: pd.DataFrame) -> bool:
    approval_columns = [
        "approved_for_execution",
        "approved_for_paper_trading",
        "approved_for_real_capital",
        "approved_for_live_alerts",
        "approved_for_automation",
    ]

    if candidate_df.empty:
        return False

    for column in approval_columns:
        if column not in candidate_df.columns:
            return False

        if candidate_df[column].astype(bool).any():
            return False

    return True


def validate_long_candidate_discovery_baseline() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    candidates = build_long_candidate_registry()
    candidate_df = candidate_registry_to_df(candidates)
    price_level_fixture_df = build_controlled_price_level_fixture(candidates)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_7_closure_exists": PHASE_7_CLOSURE_PATH,
        "phase_8_1_contract_doc_exists": PHASE_8_1_CONTRACT_DOC_PATH,
        "phase_8_1_contract_module_exists": PHASE_8_1_CONTRACT_MODULE_PATH,
        "phase_8_2_discovery_doc_exists": PHASE_8_2_DOC_PATH,
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

    discovered_ids = candidate_df["candidate_id"].tolist()

    checks.append(
        build_check(
            check_group="candidate_registry",
            check_name="expected_candidate_count_present",
            passed=len(discovered_ids) == len(EXPECTED_CANDIDATES),
            severity="INFO" if len(discovered_ids) == len(EXPECTED_CANDIDATES) else "ERROR",
            details=f"candidate_count={len(discovered_ids)}",
        )
    )

    checks.append(
        build_check(
            check_group="candidate_registry",
            check_name="expected_candidate_ids_present",
            passed=set(discovered_ids) == set(EXPECTED_CANDIDATES),
            severity="INFO" if set(discovered_ids) == set(EXPECTED_CANDIDATES) else "ERROR",
            details=",".join(discovered_ids),
        )
    )

    checks.append(
        build_check(
            check_group="candidate_registry",
            check_name="all_candidates_direction_long",
            passed=candidate_df["direction"].astype(str).str.upper().eq("LONG").all(),
            severity=(
                "INFO"
                if candidate_df["direction"].astype(str).str.upper().eq("LONG").all()
                else "ERROR"
            ),
            details="directions=" + ",".join(candidate_df["direction"].astype(str).unique()),
        )
    )

    checks.append(
        build_check(
            check_group="candidate_registry",
            check_name="all_candidates_watch_only",
            passed=candidate_df["router_decision"].astype(str).str.upper().eq("WATCH_ONLY").all(),
            severity=(
                "INFO"
                if candidate_df["router_decision"].astype(str).str.upper().eq("WATCH_ONLY").all()
                else "ERROR"
            ),
            details="router_decisions=" + ",".join(candidate_df["router_decision"].astype(str).unique()),
        )
    )

    checks.append(
        build_check(
            check_group="candidate_registry",
            check_name="all_candidates_discovery_only",
            passed=candidate_df["approval_status"].astype(str).eq(DISCOVERY_APPROVAL_STATUS).all(),
            severity=(
                "INFO"
                if candidate_df["approval_status"].astype(str).eq(DISCOVERY_APPROVAL_STATUS).all()
                else "ERROR"
            ),
            details="approval_statuses=" + ",".join(candidate_df["approval_status"].astype(str).unique()),
        )
    )

    checks.append(
        build_check(
            check_group="candidate_registry",
            check_name="all_candidates_have_required_text",
            passed=all_candidates_have_required_text(candidate_df),
            severity="INFO" if all_candidates_have_required_text(candidate_df) else "ERROR",
            details="Required candidate text fields are populated.",
        )
    )

    checks.append(
        build_check(
            check_group="candidate_registry",
            check_name="research_priorities_unique",
            passed=candidate_df["research_priority"].is_unique,
            severity="INFO" if candidate_df["research_priority"].is_unique else "ERROR",
            details="priorities=" + ",".join(candidate_df["research_priority"].astype(str).tolist()),
        )
    )

    checks.append(
        build_check(
            check_group="price_structure",
            check_name="controlled_long_price_levels_valid",
            passed=price_level_fixture_df["valid_long_structure"].astype(bool).all(),
            severity=(
                "INFO"
                if price_level_fixture_df["valid_long_structure"].astype(bool).all()
                else "ERROR"
            ),
            details=(
                "valid_rows="
                + str(int(price_level_fixture_df["valid_long_structure"].astype(bool).sum()))
            ),
        )
    )

    checks.append(
        build_check(
            check_group="price_structure",
            check_name="controlled_risk_reward_positive",
            passed=(pd.to_numeric(price_level_fixture_df["risk_reward"], errors="coerce") > 0).all(),
            severity=(
                "INFO"
                if (pd.to_numeric(price_level_fixture_df["risk_reward"], errors="coerce") > 0).all()
                else "ERROR"
            ),
            details=(
                "risk_reward_values="
                + ",".join(price_level_fixture_df["risk_reward"].round(2).astype(str).tolist())
            ),
        )
    )

    checks.append(
        build_check(
            check_group="approval_control",
            check_name="no_candidate_has_execution_approval",
            passed=no_candidate_has_execution_approval(candidate_df),
            severity="INFO" if no_candidate_has_execution_approval(candidate_df) else "ERROR",
            details="All approval flags remain False.",
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

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="historical_backtest_not_executed",
            passed=True,
            severity="INFO",
            details="Phase 8.2 defines candidates only; no historical backtest is executed.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="walk_forward_not_executed",
            passed=True,
            severity="INFO",
            details="Walk-forward validation is deferred.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="monte_carlo_not_executed",
            passed=True,
            severity="INFO",
            details="Monte Carlo validation is deferred.",
        )
    )

    checks.append(
        build_check(
            check_group="phase_transition",
            check_name="phase_8_3_recommended_next",
            passed=True,
            severity="INFO",
            details="Recommended next step: Phase 8.3 LONG Baseline Structural Backtest Harness V1.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="long_side_remains_unestablished",
            passed=True,
            severity="WARNING",
            details="Phase 8.2 discovers candidates only; LONG side is not established.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="real_entries_remain_blocked",
            passed=True,
            severity="WARNING",
            details="Real entries remain blocked after Phase 8.2.",
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
                "phase": "8.2",
                "candidate_registry_defined": True,
                "candidate_count": int(len(candidate_df)),
                "expected_candidate_count": int(len(EXPECTED_CANDIDATES)),
                "all_candidates_long": bool(
                    candidate_df["direction"].astype(str).str.upper().eq("LONG").all()
                ),
                "all_candidates_watch_only": bool(
                    candidate_df["router_decision"].astype(str).str.upper().eq("WATCH_ONLY").all()
                ),
                "all_candidates_discovery_only": bool(
                    candidate_df["approval_status"].astype(str).eq(DISCOVERY_APPROVAL_STATUS).all()
                ),
                "controlled_long_price_levels_valid": bool(
                    price_level_fixture_df["valid_long_structure"].astype(bool).all()
                ),
                "average_controlled_risk_reward": float(
                    pd.to_numeric(price_level_fixture_df["risk_reward"], errors="coerce").mean()
                ),
                "historical_backtest_executed": False,
                "walk_forward_executed": False,
                "monte_carlo_executed": False,
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
                "recommended_next_phase": "PHASE_8_3_LONG_BASELINE_STRUCTURAL_BACKTEST_HARNESS_V1",
                "estimated_total_project_progress_percent": 91,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_8_2_LONG_CANDIDATE_DISCOVERY_BASELINE_DEFINED"
                    if validation_passed
                    else "PHASE_8_2_LONG_CANDIDATE_DISCOVERY_BASELINE_FAILED"
                ),
            }
        ]
    )

    candidate_df.to_csv(
        REPORTS_DIR / "long_candidate_discovery_registry_v1.csv",
        index=False,
    )
    price_level_fixture_df.to_csv(
        REPORTS_DIR / "long_candidate_controlled_price_levels_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_candidate_discovery_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_candidate_discovery_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "candidates": candidate_df,
        "controlled_price_levels": price_level_fixture_df,
        "checks": checks_df,
    }