from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.long_side.long_candidate_discovery_baseline_v1 import (
    DISCOVERY_APPROVAL_STATUS,
    EXPECTED_CANDIDATES,
    build_long_candidate_registry,
)


REPORTS_DIR = Path("reports/phase_8_3_long_baseline_structural_backtest_harness_v1")

PHASE_7_CLOSURE_PATH = Path("docs/PHASE_7_REAL_MARKET_INPUT_BRIDGE_CLOSURE.md")
PHASE_8_1_CONTRACT_DOC_PATH = Path("docs/PHASE_8_LONG_SIDE_VALIDATION_CONTRACT.md")
PHASE_8_2_DISCOVERY_DOC_PATH = Path("docs/PHASE_8_LONG_CANDIDATE_DISCOVERY_BASELINE.md")
PHASE_8_2_DISCOVERY_MODULE_PATH = Path("src/long_side/long_candidate_discovery_baseline_v1.py")
PHASE_8_3_DOC_PATH = Path("docs/PHASE_8_LONG_BASELINE_STRUCTURAL_BACKTEST_HARNESS.md")

MEASURED_STATUS = "MEASURED_BASELINE_ONLY"

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
class ControlledLongScenario:
    candidate_id: str
    entry_price: float
    stop_price: float
    target_price: float
    bars: tuple[dict[str, float], ...]
    expected_resolution_status: str


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


def build_controlled_long_scenarios() -> list[ControlledLongScenario]:
    return [
        ControlledLongScenario(
            candidate_id="LONG_BASE_FIB_PULLBACK_V1",
            entry_price=65100.0,
            stop_price=64600.0,
            target_price=66350.0,
            expected_resolution_status="TARGET_HIT",
            bars=(
                {"high": 65400.0, "low": 64900.0, "close": 65350.0},
                {"high": 65900.0, "low": 65100.0, "close": 65750.0},
                {"high": 66400.0, "low": 65600.0, "close": 66300.0},
            ),
        ),
        ControlledLongScenario(
            candidate_id="LONG_BASE_LIQUIDITY_SWEEP_V1",
            entry_price=65200.0,
            stop_price=64700.0,
            target_price=66450.0,
            expected_resolution_status="STOP_HIT",
            bars=(
                {"high": 65300.0, "low": 65000.0, "close": 65150.0},
                {"high": 65250.0, "low": 64650.0, "close": 64720.0},
            ),
        ),
        ControlledLongScenario(
            candidate_id="LONG_BASE_MTF_BULLISH_CONTINUATION_V1",
            entry_price=65300.0,
            stop_price=64800.0,
            target_price=66550.0,
            expected_resolution_status="TARGET_HIT",
            bars=(
                {"high": 65600.0, "low": 65100.0, "close": 65550.0},
                {"high": 66100.0, "low": 65450.0, "close": 66000.0},
                {"high": 66600.0, "low": 65900.0, "close": 66500.0},
            ),
        ),
        ControlledLongScenario(
            candidate_id="LONG_BASE_FAILED_BREAKDOWN_V1",
            entry_price=65400.0,
            stop_price=64900.0,
            target_price=66650.0,
            expected_resolution_status="OPEN_TIMEOUT",
            bars=(
                {"high": 65700.0, "low": 65200.0, "close": 65600.0},
                {"high": 66000.0, "low": 65300.0, "close": 65800.0},
                {"high": 66200.0, "low": 65450.0, "close": 65950.0},
            ),
        ),
    ]


def resolve_long_scenario(scenario: ControlledLongScenario) -> dict[str, Any]:
    risk = scenario.entry_price - scenario.stop_price
    reward = scenario.target_price - scenario.entry_price
    risk_reward = reward / risk if risk > 0 else 0.0

    max_high = scenario.entry_price
    min_low = scenario.entry_price

    resolution_status = "OPEN_TIMEOUT"
    result_r = 0.0
    bars_to_resolution = len(scenario.bars)

    for index, bar in enumerate(scenario.bars, start=1):
        high = float(bar["high"])
        low = float(bar["low"])

        max_high = max(max_high, high)
        min_low = min(min_low, low)

        stop_hit = low <= scenario.stop_price
        target_hit = high >= scenario.target_price

        if stop_hit:
            resolution_status = "STOP_HIT"
            result_r = -1.0
            bars_to_resolution = index
            break

        if target_hit:
            resolution_status = "TARGET_HIT"
            result_r = risk_reward
            bars_to_resolution = index
            break

    mfe_r = (max_high - scenario.entry_price) / risk if risk > 0 else 0.0
    mae_r = (min_low - scenario.entry_price) / risk if risk > 0 else 0.0

    return {
        "candidate_id": scenario.candidate_id,
        "direction": "LONG",
        "router_decision": "WATCH_ONLY",
        "entry_price": scenario.entry_price,
        "stop_price": scenario.stop_price,
        "target_price": scenario.target_price,
        "risk": risk,
        "reward": reward,
        "risk_reward": risk_reward,
        "valid_long_structure": validate_long_price_structure(
            entry_price=scenario.entry_price,
            stop_price=scenario.stop_price,
            target_price=scenario.target_price,
        ),
        "resolution_status": resolution_status,
        "expected_resolution_status": scenario.expected_resolution_status,
        "result_r": result_r,
        "mfe_r": mfe_r,
        "mae_r": mae_r,
        "bars_to_resolution": bars_to_resolution,
        "measured_status": MEASURED_STATUS,
        "approval_status": DISCOVERY_APPROVAL_STATUS,
        "long_strategy_approved": False,
        "long_entries_approved": False,
        "execution_allowed": False,
    }


def calculate_max_drawdown_r(result_values: list[float]) -> float:
    equity = 0.0
    peak = 0.0
    max_drawdown = 0.0

    for result in result_values:
        equity += result
        peak = max(peak, equity)
        drawdown = equity - peak
        max_drawdown = min(max_drawdown, drawdown)

    return max_drawdown


def build_candidate_metrics(trades_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for candidate_id, group in trades_df.groupby("candidate_id", sort=True):
        result_r = pd.to_numeric(group["result_r"], errors="coerce").fillna(0.0)
        wins = int((result_r > 0).sum())
        losses = int((result_r < 0).sum())
        open_trades = int(group["resolution_status"].astype(str).eq("OPEN_TIMEOUT").sum())
        trades = int(len(group))

        gross_win_r = float(result_r[result_r > 0].sum())
        gross_loss_r = float(result_r[result_r < 0].sum())

        if gross_loss_r < 0:
            profit_factor = gross_win_r / abs(gross_loss_r)
        elif gross_win_r > 0:
            profit_factor = 999.0
        else:
            profit_factor = 0.0

        rows.append(
            {
                "candidate_id": candidate_id,
                "trades": trades,
                "wins": wins,
                "losses": losses,
                "open_trades": open_trades,
                "win_rate": wins / trades if trades > 0 else 0.0,
                "gross_win_r": gross_win_r,
                "gross_loss_r": gross_loss_r,
                "profit_factor": profit_factor,
                "total_result_r": float(result_r.sum()),
                "average_result_r": float(result_r.mean()) if trades > 0 else 0.0,
                "max_drawdown_r": calculate_max_drawdown_r(result_r.tolist()),
                "candidate_approved": False,
                "measured_status": MEASURED_STATUS,
            }
        )

    return pd.DataFrame(rows)


def no_candidate_approved(trades_df: pd.DataFrame, metrics_df: pd.DataFrame) -> bool:
    if trades_df.empty or metrics_df.empty:
        return False

    trade_approvals_false = (
        ~trades_df["long_strategy_approved"].astype(bool)
        & ~trades_df["long_entries_approved"].astype(bool)
        & ~trades_df["execution_allowed"].astype(bool)
    ).all()

    metrics_approvals_false = ~metrics_df["candidate_approved"].astype(bool).any()

    return bool(trade_approvals_false and metrics_approvals_false)


def validate_long_baseline_structural_backtest_harness() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    candidates = build_long_candidate_registry()
    candidate_df = pd.DataFrame([candidate.__dict__ for candidate in candidates])

    scenarios = build_controlled_long_scenarios()
    trades_df = pd.DataFrame([resolve_long_scenario(scenario) for scenario in scenarios])
    metrics_df = build_candidate_metrics(trades_df)

    checks: list[dict[str, Any]] = []

    phase_anchors = {
        "phase_7_closure_exists": PHASE_7_CLOSURE_PATH,
        "phase_8_1_contract_doc_exists": PHASE_8_1_CONTRACT_DOC_PATH,
        "phase_8_2_discovery_doc_exists": PHASE_8_2_DISCOVERY_DOC_PATH,
        "phase_8_2_discovery_module_exists": PHASE_8_2_DISCOVERY_MODULE_PATH,
        "phase_8_3_harness_doc_exists": PHASE_8_3_DOC_PATH,
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

    measured_candidates = sorted(trades_df["candidate_id"].unique().tolist())

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="expected_candidates_measured",
            passed=set(measured_candidates) == set(EXPECTED_CANDIDATES),
            severity="INFO" if set(measured_candidates) == set(EXPECTED_CANDIDATES) else "ERROR",
            details=",".join(measured_candidates),
        )
    )

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="one_trade_per_candidate_present",
            passed=trades_df.groupby("candidate_id").size().eq(1).all(),
            severity="INFO" if trades_df.groupby("candidate_id").size().eq(1).all() else "ERROR",
            details="trade_count=" + str(int(len(trades_df))),
        )
    )

    checks.append(
        build_check(
            check_group="directional_contract",
            check_name="all_trades_direction_long",
            passed=trades_df["direction"].astype(str).str.upper().eq("LONG").all(),
            severity="INFO" if trades_df["direction"].astype(str).str.upper().eq("LONG").all() else "ERROR",
            details="directions=" + ",".join(trades_df["direction"].astype(str).unique()),
        )
    )

    checks.append(
        build_check(
            check_group="directional_contract",
            check_name="all_trades_watch_only",
            passed=trades_df["router_decision"].astype(str).str.upper().eq("WATCH_ONLY").all(),
            severity="INFO" if trades_df["router_decision"].astype(str).str.upper().eq("WATCH_ONLY").all() else "ERROR",
            details="router_decisions=" + ",".join(trades_df["router_decision"].astype(str).unique()),
        )
    )

    checks.append(
        build_check(
            check_group="price_structure",
            check_name="all_long_price_structures_valid",
            passed=trades_df["valid_long_structure"].astype(bool).all(),
            severity="INFO" if trades_df["valid_long_structure"].astype(bool).all() else "ERROR",
            details="valid_rows=" + str(int(trades_df["valid_long_structure"].astype(bool).sum())),
        )
    )

    checks.append(
        build_check(
            check_group="measurement",
            check_name="structural_backtest_executed",
            passed=len(trades_df) > 0 and len(metrics_df) > 0,
            severity="INFO" if len(trades_df) > 0 and len(metrics_df) > 0 else "ERROR",
            details=f"trades={len(trades_df)}, metrics_rows={len(metrics_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="measurement",
            check_name="mixed_resolution_statuses_present",
            passed=set(trades_df["resolution_status"].unique()).issuperset(
                {"TARGET_HIT", "STOP_HIT", "OPEN_TIMEOUT"}
            ),
            severity=(
                "INFO"
                if set(trades_df["resolution_status"].unique()).issuperset(
                    {"TARGET_HIT", "STOP_HIT", "OPEN_TIMEOUT"}
                )
                else "ERROR"
            ),
            details="statuses=" + ",".join(sorted(trades_df["resolution_status"].unique())),
        )
    )

    checks.append(
        build_check(
            check_group="measurement",
            check_name="metrics_computed_for_all_candidates",
            passed=set(metrics_df["candidate_id"].tolist()) == set(EXPECTED_CANDIDATES),
            severity=(
                "INFO"
                if set(metrics_df["candidate_id"].tolist()) == set(EXPECTED_CANDIDATES)
                else "ERROR"
            ),
            details="metrics_rows=" + str(int(len(metrics_df))),
        )
    )

    checks.append(
        build_check(
            check_group="approval_control",
            check_name="no_candidate_approved",
            passed=no_candidate_approved(trades_df=trades_df, metrics_df=metrics_df),
            severity="INFO" if no_candidate_approved(trades_df=trades_df, metrics_df=metrics_df) else "ERROR",
            details="All candidate approval flags remain False.",
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
            check_name="production_historical_backtest_not_executed",
            passed=True,
            severity="INFO",
            details="Phase 8.3 uses controlled structural scenarios only.",
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
            check_name="phase_8_4_recommended_next",
            passed=True,
            severity="INFO",
            details="Recommended next step: Phase 8.4 LONG Historical Baseline Backtest V1.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="long_side_remains_unestablished",
            passed=True,
            severity="WARNING",
            details="Phase 8.3 measures structural baseline only; LONG side is not established.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="real_entries_remain_blocked",
            passed=True,
            severity="WARNING",
            details="Real entries remain blocked after Phase 8.3.",
        )
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    result_r = pd.to_numeric(trades_df["result_r"], errors="coerce").fillna(0.0)

    summary_df = pd.DataFrame(
        [
            {
                "phase": "8.3",
                "structural_backtest_harness_defined": True,
                "candidate_count": int(candidate_df.shape[0]),
                "measured_candidate_count": int(trades_df["candidate_id"].nunique()),
                "trade_count": int(len(trades_df)),
                "metrics_rows": int(len(metrics_df)),
                "target_hits": int(trades_df["resolution_status"].eq("TARGET_HIT").sum()),
                "stop_hits": int(trades_df["resolution_status"].eq("STOP_HIT").sum()),
                "open_timeouts": int(trades_df["resolution_status"].eq("OPEN_TIMEOUT").sum()),
                "total_result_r": float(result_r.sum()),
                "average_result_r": float(result_r.mean()) if len(result_r) > 0 else 0.0,
                "average_risk_reward": float(pd.to_numeric(trades_df["risk_reward"], errors="coerce").mean()),
                "structural_backtest_executed": True,
                "production_historical_backtest_executed": False,
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
                "recommended_next_phase": "PHASE_8_4_LONG_HISTORICAL_BASELINE_BACKTEST_V1",
                "estimated_total_project_progress_percent": 92,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_8_3_LONG_BASELINE_STRUCTURAL_BACKTEST_HARNESS_VALIDATED"
                    if validation_passed
                    else "PHASE_8_3_LONG_BASELINE_STRUCTURAL_BACKTEST_HARNESS_FAILED"
                ),
            }
        ]
    )

    candidate_df.to_csv(
        REPORTS_DIR / "long_structural_backtest_candidate_registry_v1.csv",
        index=False,
    )
    trades_df.to_csv(
        REPORTS_DIR / "long_structural_backtest_trades_v1.csv",
        index=False,
    )
    metrics_df.to_csv(
        REPORTS_DIR / "long_structural_backtest_metrics_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_structural_backtest_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_structural_backtest_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "candidates": candidate_df,
        "trades": trades_df,
        "metrics": metrics_df,
        "checks": checks_df,
    }