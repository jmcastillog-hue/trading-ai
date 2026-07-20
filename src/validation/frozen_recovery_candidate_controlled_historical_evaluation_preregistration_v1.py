from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any


PHASE = "10.42R.2H"
SCHEMA_VERSION = "CONTROLLED_HISTORICAL_EVALUATION_PREREGISTRATION_V1"
SOURCE_PHASE_2G_COMMIT = "a1ced46cf71f4a5880d74b76ad2bc8d1eaae16e3"
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_42R_2I_FROZEN_RECOVERY_CANDIDATE_"
    "CONTROLLED_HISTORICAL_EVALUATION_HARNESS_DESIGN_V1"
)

EXPECTED_SOURCE_HASHES = {
    "docs/PHASE_10_42R_2B_COST_ACCOUNTING_NORMALIZATION_AND_STRATEGY_RECOVERY_PREREGISTRATION.md":
        "39c7ea80c7e5b8269464c171fc73a05b505588b8e5a8bdffad4fbb9e4ab30204",
    "docs/PHASE_10_42R_2D_RECOVERY_CANDIDATE_FAMILY_SPECIFICATION_AND_MULTIPLICITY_FREEZE.md":
        "b1493544e192e119105a6b1ae6c4c28e739954be7f8473cc2f4bd183da1a663d",
    "docs/PHASE_10_42R_2G_FROZEN_RECOVERY_CANDIDATE_CORRECTION_INDEPENDENT_SYNTHETIC_ACCEPTANCE.md":
        "d92d8e1240ff39e4d8942ca628f8c0ccfbd8a38f15a617f12b3b51a1f39a98da",
    "src/analysis/frozen_recovery_candidate_implementation_v2.py":
        "ccf3cc05823515fa56e9e1183eb51ab903503e310aa037248847ad7445b2cc1e",
    "PHASE_10_42R_2G_MANIFEST.sha256":
        "7975637afe547fdee30e95078fd39ae7dee95a12daed87ebf2d37c2cc92ce285",
}

FORBIDDEN_ARTIFACT_PATHS = (
    "data/holdout/strategy_recovery_retrospective_lockbox_2026h1_v1.csv",
    "data/holdout/strategy_recovery_prospective_20260720_20270120_v1.csv",
    "data/forward/long_forward_observation_dataset_v1.csv",
)

SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
TIMEFRAMES = ("15m", "1h", "4h")
VARIANTS = (
    "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N48_V01",
    "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N96_V02",
    "RCV_SHORT_BREAKDOWN_RETEST_F02_N48_V01",
    "RCV_SHORT_BREAKDOWN_RETEST_F02_N96_V02",
    "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_S000_V01",
    "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_S025_V02",
)
FAMILIES = (
    "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_V1",
    "RCV_SHORT_BREAKDOWN_RETEST_F02_V1",
    "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_V1",
)

TIMING_CONTRACT = "CLOSED_CANDLE_CORRECTED_PLUS_NEXT_BAR_OPEN_CORRECTED"
ACCOUNTING_CONTRACT = "FRICTIONLESS_GROSS_R_TO_SINGLE_PROFILE_NET_R_V1"
DRAWDOWN_ORDER_CONTRACT = (
    "EXIT_TIME_UTC_THEN_ENTRY_TIME_UTC_THEN_SYMBOL_"
    "THEN_SOURCE_TRADE_ROW_ASCENDING"
)
MULTIPLICITY_METHOD = "STEP_DOWN_HOLM_BONFERRONI"
MULTIPLICITY_ALPHA = 0.05
P_VALUE_METHOD = "INHERITED_EXACTLY_FROM_PHASE_10_42R_2D_FROZEN_SPECIFICATION"
FIXED_REWARD_TO_RISK = 2.5
MAXIMUM_TRADE_BARS = 240

PERMISSIONS = {
    name: False
    for name in (
        "real_data_access_allowed",
        "historical_evaluation_allowed",
        "retrospective_lockbox_access_allowed",
        "prospective_holdout_access_allowed",
        "performance_metrics_allowed",
        "candidate_comparison_allowed",
        "candidate_ranking_allowed",
        "winner_selection_allowed",
        "candidate_mutation_allowed",
        "forward_observation_allowed",
        "official_dataset_write_allowed",
        "evidence_persistence_allowed",
        "signal_generation_enabled",
        "live_alerts_allowed",
        "paper_trade_execution_allowed",
        "real_capital_allowed",
        "market_execution_allowed",
        "exchange_execution_allowed",
        "automation_allowed",
        "execution_allowed",
        "openclaw_operational_integration_allowed",
    )
}

FORBIDDEN_IMPORT_PREFIXES = (
    "pandas", "numpy", "scipy", "src.backtesting", "src.exchange",
    "src.analysis", "src.execution", "src.long_side", "src.journal",
)


@dataclass(frozen=True)
class Check:
    check_id: str
    check_name: str
    passed: bool
    details: str
    blocker: bool


@dataclass(frozen=True)
class Protocol:
    schema_version: str
    source_phase_2g_commit: str
    symbols: tuple[str, ...]
    timeframes: tuple[str, ...]
    variants: tuple[str, ...]
    families: tuple[str, ...]
    timing_contract: str
    accounting_contract: str
    drawdown_order_contract: str
    fixed_reward_to_risk: float
    maximum_trade_bars: int
    dataset_slots: tuple[tuple[str, str, str], ...]
    evidence_windows: tuple[tuple[str, str, str, str], ...]
    cost_profiles: tuple[tuple[str, float, float, float, str], ...]
    primary_metrics: tuple[str, ...]
    diagnostic_metrics: tuple[str, ...]
    slices: tuple[str, ...]
    multiplicity: tuple[Any, ...]
    promotion_gates: tuple[tuple[str, str, str, str], ...]
    rules: tuple[tuple[str, str, str, bool, bool], ...]
    permissions: tuple[tuple[str, bool], ...]


class PreregistrationFailure(RuntimeError):
    pass


def normalized_source_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_dataset_slots() -> tuple[tuple[str, str, str], ...]:
    return tuple(
        (
            symbol,
            timeframe,
            "PRIMARY_SIGNAL_AND_EXECUTION" if timeframe == "15m"
            else "CLOSED_CONTEXT_ONLY",
        )
        for symbol in SYMBOLS
        for timeframe in TIMEFRAMES
    )


def build_evidence_windows() -> tuple[tuple[str, str, str, str], ...]:
    return (
        (
            "KNOWN_EVIDENCE_2022_2025",
            "2022-01-01T00:00:00+00:00",
            "2026-01-01T00:00:00+00:00",
            "KNOWN_EVIDENCE_DESCRIPTIVE_ONLY",
        ),
        (
            "RETROSPECTIVE_LOCKBOX_2026H1",
            "2026-01-01T00:00:00+00:00",
            "2026-07-20T00:00:00+00:00",
            "SECONDARY_ONE_TIME_LOCKBOX_SEALED",
        ),
        (
            "PROSPECTIVE_HOLDOUT_2026_2027",
            "2026-07-20T00:00:00+00:00",
            "2027-01-20T00:00:00+00:00",
            "PRIMARY_CONFIRMATORY_HOLDOUT_SEALED",
        ),
    )


def build_cost_profiles() -> tuple[tuple[str, float, float, float, str], ...]:
    return (
        ("BINANCE_SCALP_BASE_ESTIMATE", 0.0008, 0.0004, 0.0004, "PRIMARY_BASE_GATE"),
        ("BINANCE_SCALP_STRESS_ESTIMATE", 0.0012, 0.0008, 0.0008, "PRIMARY_STRESS_GATE"),
        ("QUANTFURY_SWING_BASE_ESTIMATE", 0.0000, 0.0035, 0.0005, "SECONDARY_DIAGNOSTIC"),
        ("QUANTFURY_SWING_STRESS_ESTIMATE", 0.0000, 0.0060, 0.0010, "SECONDARY_DIAGNOSTIC"),
        ("EXTREME_COST_STRESS_TEST", 0.0015, 0.0080, 0.0020, "EXTREME_DIAGNOSTIC"),
    )


def build_promotion_gates() -> tuple[tuple[str, str, str, str], ...]:
    return (
        ("GATE_001", "aggregate_trade_count", ">=", "100"),
        ("GATE_002", "trade_count_each_symbol", ">=", "20"),
        ("GATE_003", "binance_base_profit_factor", ">=", "1.05"),
        ("GATE_004", "binance_base_expectancy_aggregate", ">", "0.0"),
        ("GATE_005", "binance_base_expectancy_each_symbol", ">", "0.0"),
        ("GATE_006", "binance_base_expectancy_each_year", ">=", "0.0"),
        ("GATE_007", "binance_stress_expectancy", ">=", "0.0"),
        ("GATE_008", "binance_stress_profit_factor", ">=", "1.00"),
        ("GATE_009", "holm_adjusted_p_value", "<=", "0.05"),
        ("GATE_010", "all_predeclared_stability_slices", "==", "NON_FAILING"),
    )


def build_rules() -> tuple[tuple[str, str, str, bool, bool], ...]:
    rows = (
        ("PR-001", "objective", "Evaluate fixed candidates; do not optimize."),
        ("PR-002", "timing", "Closed-candle context plus next-bar-open fill only."),
        ("PR-003", "short_reference", "Retired SHORT reference cannot be repaired in place."),
        ("PR-004", "long_reference", "LONG references remain research-only."),
        ("PR-005", "symbols", "Fixed BTCUSDT, ETHUSDT, SOLUSDT cohort; no deletion."),
        ("PR-006", "known_data", "2022-2025 is known evidence and never holdout."),
        ("PR-007", "slices", "Symbol, year, volatility tercile, regime and family fixed."),
        ("PR-008", "multiplicity", "Three families and six variants frozen before evaluation."),
        ("PR-009", "costs", "Single-profile normalized accounting and five profiles."),
        ("PR-010", "metrics", "Expectancy, PF, drawdown, positive windows, trades."),
        ("PR-011", "minimum_evidence", "At least 100 aggregate and 20 per symbol."),
        ("PR-012", "promotion", "Base positive, stress non-failing, stable, multiplicity pass."),
        ("PR-013", "retrospective", "2026-01-01 to 2026-07-20 one-time secondary lockbox."),
        ("PR-014", "prospective", "2026-07-20 to 2027-01-20 confirmatory holdout."),
        ("PR-015", "mutation", "Any change requires new version and invalidates test claims."),
        ("HPR-016", "input_manifest", "Bind nine paths and hashes before first read."),
        ("HPR-017", "dataset_completeness", "All three symbols and timeframes mandatory."),
        ("HPR-018", "timestamps", "UTC, ordered, unique open and close times."),
        ("HPR-019", "bar_integrity", "Finite closed structurally valid OHLCV only."),
        ("HPR-020", "mtf", "1H/4H features available only after source close."),
        ("HPR-021", "fill", "Signal at closed 15m t; fill at next open t+1."),
        ("HPR-022", "overlap", "One open position; overlap blocked."),
        ("HPR-023", "gap", "SHORT stop must be strictly above next-open entry."),
        ("HPR-024", "exit", "2.5R target, stop-first simultaneous, bar-240 time exit."),
        ("HPR-025", "cost_application", "Reconstruct gross R; apply one profile exactly once."),
        ("HPR-026", "drawdown", "Chronological drawdown order is immutable."),
        ("HPR-027", "multiplicity_pool", "Six p-values, one pool, fixed order, Holm."),
        ("HPR-028", "classification", "Classify variants only; no winner."),
        ("HPR-029", "lockboxes", "Both lockboxes sealed in 2H and next design phase."),
        ("HPR-030", "operational_lock", "No result enables operations or execution."),
    )
    return tuple((rid, cat, rule, True, False) for rid, cat, rule in rows)


def build_protocol() -> Protocol:
    return Protocol(
        schema_version=SCHEMA_VERSION,
        source_phase_2g_commit=SOURCE_PHASE_2G_COMMIT,
        symbols=SYMBOLS,
        timeframes=TIMEFRAMES,
        variants=VARIANTS,
        families=FAMILIES,
        timing_contract=TIMING_CONTRACT,
        accounting_contract=ACCOUNTING_CONTRACT,
        drawdown_order_contract=DRAWDOWN_ORDER_CONTRACT,
        fixed_reward_to_risk=FIXED_REWARD_TO_RISK,
        maximum_trade_bars=MAXIMUM_TRADE_BARS,
        dataset_slots=build_dataset_slots(),
        evidence_windows=build_evidence_windows(),
        cost_profiles=build_cost_profiles(),
        primary_metrics=(
            "TRADE_COUNT", "NET_EXPECTANCY_R", "PROFIT_FACTOR",
            "CHRONOLOGICAL_MAX_DRAWDOWN_R", "POSITIVE_WINDOW_RATE",
            "HOLM_ADJUSTED_P_VALUE",
        ),
        diagnostic_metrics=(
            "FRICTIONLESS_GROSS_EXPECTANCY_R",
            "FRICTIONLESS_PROFIT_FACTOR",
        ),
        slices=(
            "AGGREGATE", "SYMBOL", "CALENDAR_YEAR", "VOLATILITY_TERCILE",
            "CLOSED_MTF_TREND_REGIME", "SIGNAL_FAMILY", "COST_PROFILE",
        ),
        multiplicity=(
            6, 3, 6, 1, MULTIPLICITY_METHOD, MULTIPLICITY_ALPHA,
            P_VALUE_METHOD, VARIANTS, False,
        ),
        promotion_gates=build_promotion_gates(),
        rules=build_rules(),
        permissions=tuple(sorted(PERMISSIONS.items())),
    )


def protocol_sha256(protocol: Protocol | None = None) -> str:
    payload = json.dumps(
        asdict(protocol or build_protocol()),
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate_protocol_object(protocol: Protocol) -> tuple[str, ...]:
    expected = build_protocol()
    failures = []
    for field_name in expected.__dataclass_fields__:
        if getattr(protocol, field_name) != getattr(expected, field_name):
            failures.append(field_name)
    return tuple(failures)


def _append(checks: list[Check], name: str, passed: bool, details: str) -> None:
    checks.append(Check(
        check_id=f"2H-CHECK-{len(checks)+1:03d}",
        check_name=name,
        passed=bool(passed),
        details=details,
        blocker=not bool(passed),
    ))


def _source_is_isolated(path: Path) -> tuple[bool, str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    forbidden = sorted(
        item for item in imports
        if any(item == p or item.startswith(p + ".") for p in FORBIDDEN_IMPORT_PREFIXES)
    )
    return not forbidden, "forbidden_imports=" + ",".join(forbidden)


def _source_commit_is_ancestor(root: Path) -> tuple[bool, str]:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", SOURCE_PHASE_2G_COMMIT, "HEAD"],
        cwd=root, capture_output=True, text=True, check=False,
    )
    return result.returncode == 0, f"returncode={result.returncode}"


def validate_phase_10_42r_2h(
    *, preflight_only: bool = False, root: Path | None = None
) -> dict[str, Any]:
    project_root = (root or Path.cwd()).resolve()
    checks: list[Check] = []

    passed, details = _source_commit_is_ancestor(project_root)
    _append(checks, "source_phase_2g_commit_is_ancestor", passed, details)

    for relative_path, expected_hash in EXPECTED_SOURCE_HASHES.items():
        path = project_root / relative_path
        actual = normalized_source_sha256(path) if path.is_file() else ""
        _append(
            checks,
            "source_anchor_" + relative_path.replace("/", "_"),
            path.is_file() and actual == expected_hash,
            f"expected={expected_hash},actual={actual}",
        )

    module_path = project_root / (
        "src/validation/frozen_recovery_candidate_controlled_"
        "historical_evaluation_preregistration_v1.py"
    )
    _append(checks, "phase_2h_source_exists", module_path.is_file(), str(module_path))
    isolated, details = _source_is_isolated(module_path) if module_path.is_file() else (False, "missing")
    _append(checks, "phase_2h_source_is_static_and_isolated", isolated, details)

    existing = tuple(
        path for path in FORBIDDEN_ARTIFACT_PATHS
        if (project_root / path).exists()
    )
    _append(checks, "lockboxes_and_official_dataset_absent", not existing, ",".join(existing))
    _append(checks, "protocol_build_deterministic", build_protocol() == build_protocol(), protocol_sha256())
    _append(checks, "all_permissions_false", all(not v for v in PERMISSIONS.values()), str(len(PERMISSIONS)))
    _append(checks, "no_market_or_result_content_read", True, "source hashes and path existence only")

    preflight_count = len(checks)
    protocol = build_protocol()

    if not preflight_only:
        contract_checks = (
            ("dataset_slot_count_nine", len(protocol.dataset_slots) == 9, str(len(protocol.dataset_slots))),
            ("dataset_cross_product_exact", set(protocol.dataset_slots) == set(build_dataset_slots()), "3x3"),
            ("evidence_windows_exact", protocol.evidence_windows == build_evidence_windows(), str(len(protocol.evidence_windows))),
            ("both_lockboxes_sealed", all("SEALED" in w[3] for w in protocol.evidence_windows[1:]), "sealed"),
            ("cost_profile_count_five", len(protocol.cost_profiles) == 5, str(len(protocol.cost_profiles))),
            ("cost_profiles_exact", protocol.cost_profiles == build_cost_profiles(), "exact"),
            ("single_profile_accounting_locked", protocol.accounting_contract == ACCOUNTING_CONTRACT, protocol.accounting_contract),
            ("primary_metrics_exact", protocol.primary_metrics[:5] == (
                "TRADE_COUNT", "NET_EXPECTANCY_R", "PROFIT_FACTOR",
                "CHRONOLOGICAL_MAX_DRAWDOWN_R", "POSITIVE_WINDOW_RATE",
            ), ",".join(protocol.primary_metrics)),
            ("slice_contract_exact", len(protocol.slices) == 7, ",".join(protocol.slices)),
            ("multiplicity_one_pool_six", protocol.multiplicity[:4] == (6, 3, 6, 1), str(protocol.multiplicity[:4])),
            ("holm_alpha_locked", protocol.multiplicity[4:6] == (MULTIPLICITY_METHOD, 0.05), str(protocol.multiplicity[4:6])),
            ("variant_order_locked", protocol.multiplicity[7] == VARIANTS, ",".join(VARIANTS)),
            ("promotion_gate_count_ten", len(protocol.promotion_gates) == 10, str(len(protocol.promotion_gates))),
            ("minimum_evidence_gates_locked", protocol.promotion_gates[0][3] == "100" and protocol.promotion_gates[1][3] == "20", "100/20"),
            ("base_and_stress_gates_locked", tuple(g[3] for g in protocol.promotion_gates[2:8]) == ("1.05","0.0","0.0","0.0","0.0","1.00"), "exact"),
            ("rule_count_thirty", len(protocol.rules) == 30, str(len(protocol.rules))),
            ("rules_locked_immutable", all(r[3] and not r[4] for r in protocol.rules), "locked"),
            ("protocol_object_exact", not validate_protocol_object(protocol), ",".join(validate_protocol_object(protocol))),
            ("protocol_hash_deterministic", protocol_sha256(protocol) == protocol_sha256(build_protocol()), protocol_sha256(protocol)),
        )
        for name, ok, detail in contract_checks:
            _append(checks, name, ok, detail)

    failed = tuple(c for c in checks if not c.passed)
    passed = not failed
    decision = (
        "PREFLIGHT_PASSED" if preflight_only and passed
        else "CONTROLLED_HISTORICAL_EVALUATION_PREREGISTRATION_LOCKED"
        if passed else "CONTROLLED_HISTORICAL_EVALUATION_PREREGISTRATION_BLOCKED"
    )

    summary = {
        "phase": PHASE,
        "preflight_only": preflight_only,
        "source_phase_2g_commit": SOURCE_PHASE_2G_COMMIT,
        "protocol_sha256": protocol_sha256(protocol),
        "source_anchor_count": len(EXPECTED_SOURCE_HASHES),
        "dataset_slot_count": len(protocol.dataset_slots),
        "evidence_window_count": len(protocol.evidence_windows),
        "cost_profile_count": len(protocol.cost_profiles),
        "primary_metric_count": len(protocol.primary_metrics),
        "slice_count": len(protocol.slices),
        "variant_count": len(protocol.variants),
        "family_count": len(protocol.families),
        "promotion_gate_count": len(protocol.promotion_gates),
        "preregistration_rule_count": len(protocol.rules),
        "preflight_check_count": preflight_count,
        "contract_check_count": 0 if preflight_only else len(checks)-preflight_count,
        "total_check_count": len(checks),
        "failed_check_count": len(failed),
        "blocker_count": len(failed),
        "real_data_content_read_count": 0,
        "historical_evaluation_count": 0,
        "backtest_execution_count": 0,
        "retrospective_lockbox_access_count": 0,
        "prospective_holdout_access_count": 0,
        "performance_metric_count": 0,
        "candidate_comparison_count": 0,
        "candidate_ranking_count": 0,
        "winner_selection_count": 0,
        "report_artifact_write_count": 0,
        "permissions_enabled_count": sum(PERMISSIONS.values()),
        "preregistration_locked": bool(passed and not preflight_only),
        "historical_evaluation_allowed": False,
        "validation_decision": decision,
        "validation_passed": passed,
        "recommended_next_phase": RECOMMENDED_NEXT_PHASE if passed and not preflight_only else "NONE",
    }
    return {
        "summary": summary,
        "checks": tuple(asdict(c) for c in checks),
        "failed_checks": tuple(asdict(c) for c in failed),
        "protocol": asdict(protocol),
        "permissions": dict(protocol.permissions),
    }


def require_valid_preregistration(
    *, preflight_only: bool = False, root: Path | None = None
) -> dict[str, Any]:
    result = validate_phase_10_42r_2h(preflight_only=preflight_only, root=root)
    if not result["summary"]["validation_passed"]:
        names = ", ".join(item["check_name"] for item in result["failed_checks"])
        raise PreregistrationFailure("Phase 10.42R.2H failed: " + names)
    return result


__all__ = [
    "ACCOUNTING_CONTRACT", "DRAWDOWN_ORDER_CONTRACT", "EXPECTED_SOURCE_HASHES",
    "FAMILIES", "FIXED_REWARD_TO_RISK", "FORBIDDEN_ARTIFACT_PATHS",
    "MAXIMUM_TRADE_BARS", "MULTIPLICITY_ALPHA", "MULTIPLICITY_METHOD",
    "PERMISSIONS", "PHASE", "P_VALUE_METHOD", "Protocol",
    "RECOMMENDED_NEXT_PHASE", "SCHEMA_VERSION", "SOURCE_PHASE_2G_COMMIT",
    "SYMBOLS", "TIMEFRAMES", "TIMING_CONTRACT", "VARIANTS",
    "build_cost_profiles", "build_dataset_slots", "build_evidence_windows",
    "build_promotion_gates", "build_protocol", "build_rules",
    "normalized_source_sha256", "protocol_sha256", "replace",
    "require_valid_preregistration", "validate_phase_10_42r_2h",
    "validate_protocol_object",
]
