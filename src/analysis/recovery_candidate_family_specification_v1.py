from __future__ import annotations

import hashlib
import json
from typing import Any

import pandas as pd


SPECIFICATION_SCHEMA_VERSION = "RECOVERY_CANDIDATE_SPECIFICATION_V1"
SOURCE_BASELINE_COMMIT = "abb2a4b31a7280b7bb052bcaafc1cd950ffbd995"
SOURCE_PHASE_2C_ARCHIVE_SHA256 = (
    "27d6ccb4e77c2453837df5db48fdea09ce3f6f4733bf00e9c5dd2d22da03bb63"
)
EXPECTED_SPECIFICATION_ROOT_SHA256 = (
    "0872b2bf7355e8a9b35d5b4e0e05d3edf291006862ce9ee5eae847910ef4c015"
)
SPECIFICATION_STATUS = "FROZEN_SPECIFICATION_ONLY_NOT_EVALUATED"
FAMILY_LIMIT = 3
VARIANT_LIMIT_PER_FAMILY = 4
TOTAL_VARIANT_LIMIT = FAMILY_LIMIT * VARIANT_LIMIT_PER_FAMILY
FROZEN_FAMILY_COUNT = 3
FROZEN_VARIANTS_PER_FAMILY = 2
FROZEN_VARIANT_COUNT = FROZEN_FAMILY_COUNT * FROZEN_VARIANTS_PER_FAMILY
ACCOUNTING_CONTRACT = "FRICTIONLESS_GROSS_R_TO_SINGLE_PROFILE_NET_R_V1"
SHORT_REJECTED_REFERENCE = "TARGET_SHORT_FIB_V5_MTF_V3_1 + FIXED_RR_2_5"
FIXED_SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
SHORT_WALK_FORWARD_SPLITS = (
    "WF_202201_202301_TO_202301_202304",
    "WF_202204_202304_TO_202304_202307",
    "WF_202207_202307_TO_202307_202310",
    "WF_202210_202310_TO_202310_202401",
    "WF_202301_202401_TO_202401_202404",
    "WF_202304_202404_TO_202404_202407",
    "WF_202307_202407_TO_202407_202410",
    "WF_202310_202410_TO_202410_202501",
    "WF_202401_202501_TO_202501_202504",
    "WF_202404_202504_TO_202504_202507",
    "WF_202407_202507_TO_202507_202510",
    "WF_202410_202510_TO_202510_202601",
)
FIXED_TIMEFRAMES = ("15m", "1h", "4h")
PRIMARY_COST_PROFILE = "BINANCE_SCALP_BASE_ESTIMATE"
STRESS_COST_PROFILE = "BINANCE_SCALP_STRESS_ESTIMATE"
MULTIPLICITY_METHOD = "HOLM_BONFERRONI_FWER_OVER_ALL_FROZEN_VARIANTS_V1"
PRIMARY_TEST_METHOD = "CENTERED_SYMBOL_WINDOW_CLUSTER_BOOTSTRAP_EXPECTANCY_V1"
BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED_BASE = 10_420_200
FAMILY_WISE_ALPHA = 0.05
RETIRED_REFERENCE_IMPORT_ALLOWED = False

FROZEN_COST_PROFILES = (
    {
        "name": "BINANCE_SCALP_BASE_ESTIMATE",
        "platform": "BINANCE",
        "mode": "SCALP",
        "fee_pct_round_trip": 0.0008,
        "spread_pct_round_trip": 0.0004,
        "slippage_pct_round_trip": 0.0004,
        "funding_or_time_cost_pct": 0.0,
        "safety_buffer_pct": 0.0004,
        "default_risk_pct": 0.0125,
        "risk_per_trade_pct": 0.01,
    },
    {
        "name": "BINANCE_SCALP_STRESS_ESTIMATE",
        "platform": "BINANCE",
        "mode": "SCALP",
        "fee_pct_round_trip": 0.0012,
        "spread_pct_round_trip": 0.0008,
        "slippage_pct_round_trip": 0.0008,
        "funding_or_time_cost_pct": 0.0,
        "safety_buffer_pct": 0.0007,
        "default_risk_pct": 0.0125,
        "risk_per_trade_pct": 0.01,
    },
    {
        "name": "QUANTFURY_SWING_BASE_ESTIMATE",
        "platform": "QUANTFURY",
        "mode": "SWING",
        "fee_pct_round_trip": 0.0,
        "spread_pct_round_trip": 0.0035,
        "slippage_pct_round_trip": 0.0005,
        "funding_or_time_cost_pct": 0.0,
        "safety_buffer_pct": 0.001,
        "default_risk_pct": 0.035,
        "risk_per_trade_pct": 0.01,
    },
    {
        "name": "QUANTFURY_SWING_STRESS_ESTIMATE",
        "platform": "QUANTFURY",
        "mode": "SWING",
        "fee_pct_round_trip": 0.0,
        "spread_pct_round_trip": 0.006,
        "slippage_pct_round_trip": 0.001,
        "funding_or_time_cost_pct": 0.0,
        "safety_buffer_pct": 0.0015,
        "default_risk_pct": 0.035,
        "risk_per_trade_pct": 0.01,
    },
    {
        "name": "EXTREME_COST_STRESS_TEST",
        "platform": "GENERIC",
        "mode": "STRESS",
        "fee_pct_round_trip": 0.0015,
        "spread_pct_round_trip": 0.008,
        "slippage_pct_round_trip": 0.002,
        "funding_or_time_cost_pct": 0.0,
        "safety_buffer_pct": 0.002,
        "default_risk_pct": 0.035,
        "risk_per_trade_pct": 0.01,
    },
)

BANNED_IDENTIFIER_TOKENS = (
    "TARGET_SHORT",
    "FIB_V5",
    "MTF_V3_1",
    "FIXED_RR_2_5",
)

SPECIFICATION_ARTIFACT_ORDER = (
    "common_execution_contract",
    "candidate_family_registry",
    "candidate_variant_registry",
    "cost_profile_freeze",
    "evaluation_order",
    "multiplicity_contract",
    "promotion_gate_contract",
    "holdout_boundary",
)


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def canonical_frame_payload(frame: pd.DataFrame) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for raw_record in frame.to_dict(orient="records"):
        record: dict[str, Any] = {}
        for key, value in raw_record.items():
            if pd.isna(value):
                record[str(key)] = None
            elif hasattr(value, "item"):
                record[str(key)] = value.item()
            else:
                record[str(key)] = value
        records.append(record)
    return {"columns": list(frame.columns), "records": records}


def canonical_frame_sha256(frame: pd.DataFrame) -> str:
    return canonical_sha256(canonical_frame_payload(frame))


def _locked_rows(items: list[tuple[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "contract_order": order,
                "contract_key": key,
                "locked_value_json": canonical_json(value),
                "mutable_after_freeze": False,
            }
            for order, (key, value) in enumerate(items, start=1)
        ]
    )


def build_common_execution_contract() -> pd.DataFrame:
    return _locked_rows(
        [
            ("direction", "SHORT"),
            ("fixed_symbol_cohort", list(FIXED_SYMBOLS)),
            ("required_timeframes", list(FIXED_TIMEFRAMES)),
            ("known_development_period", "2022-01-01/2025-12-31"),
            ("source_baseline_commit", SOURCE_BASELINE_COMMIT),
            ("source_phase_2c_archive_sha256", SOURCE_PHASE_2C_ARCHIVE_SHA256),
            ("base_timeframe", "15m"),
            ("higher_timeframe_availability", "CLOSED_CANDLE_CORRECTED"),
            ("signal_confirmation", "CLOSED_15M_BAR_T"),
            ("fill_contract", "NEXT_15M_BAR_OPEN_T_PLUS_1"),
            ("entry_bar_resolution_allowed", True),
            ("position_concurrency", "ONE_OPEN_POSITION_PER_SYMBOL_PER_VARIANT"),
            ("simultaneous_stop_target_resolution", "STOP_FIRST_PESSIMISTIC"),
            ("maximum_trade_bars", 240),
            ("time_exit", "CLOSE_OF_240TH_ENTRY_RELATIVE_15M_BAR"),
            ("fixed_reward_to_risk", 2.5),
            ("risk_per_trade_fraction", 0.01),
            (
                "atr14_method",
                "WILDER_TRUE_RANGE_EWM_ALPHA_1_OVER_14_ADJUST_FALSE_MIN_PERIODS_14",
            ),
            (
                "ema_method",
                "PANDAS_EWM_SPAN_ADJUST_FALSE_MIN_PERIODS_EQUAL_SPAN",
            ),
            ("accounting_contract", ACCOUNTING_CONTRACT),
            (
                "cost_profile_names",
                [profile["name"] for profile in FROZEN_COST_PROFILES],
            ),
            ("walk_forward_split_names", list(SHORT_WALK_FORWARD_SPLITS)),
            ("overlapping_signal_policy", "IGNORE_WHILE_POSITION_OPEN"),
            ("invalid_entry_gap_policy", "BLOCK_IF_STOP_NOT_STRICTLY_ABOVE_NEXT_OPEN_ENTRY"),
            ("missing_feature_policy", "FAIL_CLOSED_NO_SIGNAL"),
            ("retired_reference", SHORT_REJECTED_REFERENCE),
            ("retired_reference_import_allowed", False),
            ("evaluation_allowed_in_phase_2d", False),
        ]
    )


def _context_rule() -> dict[str, Any]:
    return {
        "regime_1h_allowed": ["BEARISH", "STRONG_BEARISH"],
        "regime_4h_allowed": ["BEARISH", "STRONG_BEARISH"],
        "availability": "CLOSED_CANDLE_CORRECTED_AT_SIGNAL_CLOSE",
        "unknown_policy": "BLOCK",
    }


def _family_definitions() -> list[dict[str, Any]]:
    return [
        {
            "family_order": 1,
            "family_id": "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_V1",
            "family_name": "New upside sweep reversal SHORT",
            "hypothesis_origin": "GENERIC_PRICE_ACTION_HYPOTHESIS_DECLARED_AFTER_PHASE_2C",
            "hypothesis": (
                "A fresh sweep above a prior completed-bar high followed by a "
                "bearish reclaim may define a new SHORT signal family."
            ),
            "rule": {
                "context": _context_rule(),
                "features": {
                    "prior_high": "MAX_HIGH_OVER_VARIANT_LOOKBACK_EXCLUDING_T",
                    "atr": "ATR14_AT_T",
                    "body": "ABS_CLOSE_T_MINUS_OPEN_T_WITH_ZERO_BODY_REJECTED",
                    "upper_wick": "HIGH_T_MINUS_MAX_OPEN_T_CLOSE_T",
                },
                "all_entry_conditions": [
                    "HIGH_T_GREATER_THAN_PRIOR_HIGH",
                    "CLOSE_T_LESS_THAN_PRIOR_HIGH",
                    "CLOSE_T_LESS_THAN_OPEN_T",
                    "BODY_GREATER_THAN_ZERO",
                    "UPPER_WICK_AT_LEAST_VARIANT_WICK_TO_BODY_TIMES_BODY",
                ],
                "stop_formula": "HIGH_T_PLUS_VARIANT_STOP_ATR_BUFFER_TIMES_ATR14_T",
                "target_formula": (
                    "ENTRY_MINUS_2_5_TIMES_OPEN_PAREN_STOP_MINUS_ENTRY_CLOSE_PAREN"
                ),
            },
        },
        {
            "family_order": 2,
            "family_id": "RCV_SHORT_BREAKDOWN_RETEST_F02_V1",
            "family_name": "New breakdown retest rejection SHORT",
            "hypothesis_origin": "GENERIC_MARKET_STRUCTURE_HYPOTHESIS_DECLARED_AFTER_PHASE_2C",
            "hypothesis": (
                "A confirmed support breakdown followed by a bounded retest "
                "from below may define a new SHORT signal family."
            ),
            "rule": {
                "context": _context_rule(),
                "features": {
                    "support_j": "MIN_LOW_OVER_VARIANT_SUPPORT_LOOKBACK_BEFORE_J",
                    "breakdown_j": (
                        "MOST_RECENT_J_IN_T_MINUS_RETEST_WINDOW_TO_T_MINUS_1_"
                        "WITH_CLOSE_J_BELOW_SUPPORT_J_MINUS_BREAK_ATR_TIMES_ATR14_J"
                    ),
                    "atr": "ATR14_AT_J_AND_T",
                },
                "all_entry_conditions": [
                    "BREAKDOWN_J_EXISTS",
                    "HIGH_T_AT_LEAST_SUPPORT_J_MINUS_RETEST_TOLERANCE_ATR_TIMES_ATR14_T",
                    "CLOSE_T_LESS_THAN_SUPPORT_J",
                    "CLOSE_T_LESS_THAN_OPEN_T",
                ],
                "stop_formula": (
                    "MAX_OPEN_PAREN_HIGH_T_COMMA_SUPPORT_J_CLOSE_PAREN_PLUS_"
                    "VARIANT_STOP_ATR_BUFFER_TIMES_ATR14_T"
                ),
                "target_formula": (
                    "ENTRY_MINUS_2_5_TIMES_OPEN_PAREN_STOP_MINUS_ENTRY_CLOSE_PAREN"
                ),
            },
        },
        {
            "family_order": 3,
            "family_id": "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_V1",
            "family_name": "New EMA pullback continuation SHORT",
            "hypothesis_origin": "GENERIC_TREND_PULLBACK_HYPOTHESIS_DECLARED_AFTER_PHASE_2C",
            "hypothesis": (
                "A bearish 15m EMA stack with a closed-bar rejection of EMA20 "
                "may define a new SHORT signal family."
            ),
            "rule": {
                "context": _context_rule(),
                "features": {
                    "ema20": "EMA_CLOSE_20_AT_T",
                    "ema50": "EMA_CLOSE_50_AT_T",
                    "ema200": "EMA_CLOSE_200_AT_T",
                    "atr": "ATR14_AT_T",
                    "separation_atr": "EMA50_T_MINUS_EMA20_T_DIVIDED_BY_ATR14_T",
                },
                "all_entry_conditions": [
                    "EMA20_T_LESS_THAN_EMA50_T_LESS_THAN_EMA200_T",
                    "SEPARATION_ATR_AT_LEAST_VARIANT_MINIMUM",
                    "CLOSE_T_MINUS_1_LESS_THAN_EMA20_T_MINUS_1",
                    "HIGH_T_AT_LEAST_EMA20_T",
                    "CLOSE_T_LESS_THAN_EMA20_T",
                    "CLOSE_T_LESS_THAN_OPEN_T",
                ],
                "stop_formula": "HIGH_T_PLUS_VARIANT_STOP_ATR_BUFFER_TIMES_ATR14_T",
                "target_formula": (
                    "ENTRY_MINUS_2_5_TIMES_OPEN_PAREN_STOP_MINUS_ENTRY_CLOSE_PAREN"
                ),
            },
        },
    ]


def build_candidate_family_registry(
    common_contract_sha256: str,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for definition in _family_definitions():
        payload = {
            "schema_version": SPECIFICATION_SCHEMA_VERSION,
            "common_contract_sha256": common_contract_sha256,
            **definition,
        }
        rows.append(
            {
                "family_order": definition["family_order"],
                "family_id": definition["family_id"],
                "family_name": definition["family_name"],
                "direction": "SHORT",
                "hypothesis_origin": definition["hypothesis_origin"],
                "hypothesis": definition["hypothesis"],
                "rule_json": canonical_json(definition["rule"]),
                "common_contract_sha256": common_contract_sha256,
                "family_specification_sha256": canonical_sha256(payload),
                "retired_reference_import_allowed": False,
                "status": SPECIFICATION_STATUS,
                "evaluated": False,
                "ranking_allowed": False,
                "selection_allowed": False,
                "mutable_after_freeze": False,
            }
        )
    return pd.DataFrame(rows)


def _variant_definitions() -> list[dict[str, Any]]:
    return [
        {
            "family_order": 1,
            "variant_order_within_family": 1,
            "variant_id": "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N48_V01",
            "parameters": {
                "prior_high_lookback_bars": 48,
                "wick_to_body_minimum": 1.0,
                "stop_atr_buffer": 0.25,
            },
        },
        {
            "family_order": 1,
            "variant_order_within_family": 2,
            "variant_id": "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N96_V02",
            "parameters": {
                "prior_high_lookback_bars": 96,
                "wick_to_body_minimum": 1.0,
                "stop_atr_buffer": 0.25,
            },
        },
        {
            "family_order": 2,
            "variant_order_within_family": 1,
            "variant_id": "RCV_SHORT_BREAKDOWN_RETEST_F02_N48_V01",
            "parameters": {
                "support_lookback_bars": 48,
                "retest_window_bars": 8,
                "break_atr": 0.25,
                "retest_tolerance_atr": 0.25,
                "stop_atr_buffer": 0.25,
            },
        },
        {
            "family_order": 2,
            "variant_order_within_family": 2,
            "variant_id": "RCV_SHORT_BREAKDOWN_RETEST_F02_N96_V02",
            "parameters": {
                "support_lookback_bars": 96,
                "retest_window_bars": 8,
                "break_atr": 0.25,
                "retest_tolerance_atr": 0.25,
                "stop_atr_buffer": 0.25,
            },
        },
        {
            "family_order": 3,
            "variant_order_within_family": 1,
            "variant_id": "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_S000_V01",
            "parameters": {
                "minimum_ema20_ema50_separation_atr": 0.0,
                "stop_atr_buffer": 0.25,
            },
        },
        {
            "family_order": 3,
            "variant_order_within_family": 2,
            "variant_id": "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_S025_V02",
            "parameters": {
                "minimum_ema20_ema50_separation_atr": 0.25,
                "stop_atr_buffer": 0.25,
            },
        },
    ]


def build_candidate_variant_registry(
    family_registry: pd.DataFrame,
    common_contract_sha256: str,
) -> pd.DataFrame:
    family_by_order = {
        int(row.family_order): row
        for row in family_registry.itertuples(index=False)
    }
    rows: list[dict[str, Any]] = []
    for evaluation_order, definition in enumerate(_variant_definitions(), start=1):
        family = family_by_order[int(definition["family_order"])]
        payload = {
            "schema_version": SPECIFICATION_SCHEMA_VERSION,
            "common_contract_sha256": common_contract_sha256,
            "family_specification_sha256": family.family_specification_sha256,
            **definition,
            "evaluation_order": evaluation_order,
        }
        rows.append(
            {
                "evaluation_order": evaluation_order,
                "family_order": definition["family_order"],
                "family_id": family.family_id,
                "variant_order_within_family": definition[
                    "variant_order_within_family"
                ],
                "variant_id": definition["variant_id"],
                "parameter_json": canonical_json(definition["parameters"]),
                "family_specification_sha256": family.family_specification_sha256,
                "variant_specification_sha256": canonical_sha256(payload),
                "retired_reference_import_allowed": False,
                "status": SPECIFICATION_STATUS,
                "evaluated": False,
                "result_rows": 0,
                "ranking_allowed": False,
                "selection_allowed": False,
                "mutable_after_freeze": False,
            }
        )
    return pd.DataFrame(rows)


def build_cost_profile_freeze() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for profile_order, profile in enumerate(FROZEN_COST_PROFILES, start=1):
        payload = {
            "profile_order": profile_order,
            **profile,
            "total_cost_pct": sum(
                profile[key]
                for key in (
                    "fee_pct_round_trip",
                    "spread_pct_round_trip",
                    "slippage_pct_round_trip",
                    "funding_or_time_cost_pct",
                    "safety_buffer_pct",
                )
            ),
        }
        rows.append(
            {
                **payload,
                "profile_specification_sha256": canonical_sha256(payload),
                "mutable_after_freeze": False,
            }
        )
    return pd.DataFrame(rows)


def build_evaluation_order(variant_registry: pd.DataFrame) -> pd.DataFrame:
    return variant_registry[
        [
            "evaluation_order",
            "family_order",
            "family_id",
            "variant_order_within_family",
            "variant_id",
            "variant_specification_sha256",
        ]
    ].assign(
        order_implies_performance_rank=False,
        early_stopping_allowed=False,
        evaluation_allowed_in_phase_2d=False,
        mutable_after_freeze=False,
    )


def build_multiplicity_contract() -> pd.DataFrame:
    return _locked_rows(
        [
            ("frozen_family_count", FROZEN_FAMILY_COUNT),
            ("maximum_family_count", FAMILY_LIMIT),
            ("variants_per_family", FROZEN_VARIANTS_PER_FAMILY),
            ("maximum_variants_per_family", VARIANT_LIMIT_PER_FAMILY),
            ("frozen_total_variant_count", FROZEN_VARIANT_COUNT),
            ("maximum_total_variant_count", TOTAL_VARIANT_LIMIT),
            ("primary_cost_profile", PRIMARY_COST_PROFILE),
            ("primary_metric", "normalized_average_result_r"),
            ("null_hypothesis", "NORMALIZED_AVERAGE_RESULT_R_LESS_THAN_OR_EQUAL_ZERO"),
            ("alternative_hypothesis", "NORMALIZED_AVERAGE_RESULT_R_GREATER_THAN_ZERO"),
            ("primary_test_method", PRIMARY_TEST_METHOD),
            ("cluster_universe", "FIXED_3_SYMBOLS_X_12_SPLITS_36_UNITS"),
            ("observed_statistic", "SUM_PRIMARY_PROFILE_NET_R_DIVIDED_BY_TOTAL_TRADES"),
            ("null_centering", "SUBTRACT_OBSERVED_AVERAGE_R_FROM_EACH_TRADE_WITHIN_ITS_FIXED_CLUSTER"),
            ("cluster_resampling", "DRAW_36_SYMBOL_SPLIT_CLUSTERS_WITH_REPLACEMENT_PER_REPLICATE"),
            ("replicate_statistic", "SUM_CENTERED_NET_R_DIVIDED_BY_RESAMPLED_TRADE_COUNT"),
            ("empty_replicate_statistic", 0.0),
            ("zero_trade_clusters_retained", True),
            ("bootstrap_resamples", BOOTSTRAP_RESAMPLES),
            ("rng", "NUMPY_GENERATOR_PCG64"),
            ("seed_formula", "10420200_PLUS_EVALUATION_ORDER"),
            ("unadjusted_p_value_formula", "(1+COUNT_NULL_STATISTIC_GTE_OBSERVED_STATISTIC)/(10000+1)"),
            ("multiplicity_method", MULTIPLICITY_METHOD),
            ("family_wise_alpha", FAMILY_WISE_ALPHA),
            ("correction_scope", "ALL_6_VARIANTS_SINGLE_FAMILY_WISE_POOL"),
            ("holm_tie_break", "ASCENDING_UNADJUSTED_P_THEN_ASCENDING_EVALUATION_ORDER"),
            ("holm_step_down_rule", "AT_ORDER_K_REQUIRE_P_K_LE_ALPHA_DIVIDED_BY_6_MINUS_K_PLUS_1_AND_STOP_AT_FIRST_FAILURE"),
            ("all_results_must_be_published", True),
            ("interim_analysis_allowed", False),
            ("early_stopping_allowed", False),
            ("performance_ranking_allowed", False),
            ("winner_selection_allowed_in_evaluation_phase", False),
        ]
    )


def build_promotion_gate_contract() -> pd.DataFrame:
    gates = [
        ("PG-001", "identity", "SPECIFICATION_HASH_MATCH", "EQUAL", True),
        ("PG-002", "evidence", "AGGREGATE_OOS_TRADE_COUNT", "GREATER_THAN_OR_EQUAL", 100),
        ("PG-003", "evidence", "MINIMUM_OOS_TRADES_PER_SYMBOL", "GREATER_THAN_OR_EQUAL", 20),
        ("PG-004", "base_cost", "BASE_NORMALIZED_AVERAGE_RESULT_R", "GREATER_THAN", 0.0),
        ("PG-005", "base_cost", "BASE_NORMALIZED_PROFIT_FACTOR", "GREATER_THAN_OR_EQUAL", 1.05),
        ("PG-006", "window_stability", "BASE_POSITIVE_WINDOW_RATE", "GREATER_THAN_OR_EQUAL", 0.50),
        ("PG-007", "symbol_stability", "MINIMUM_SYMBOL_BASE_EXPECTANCY_R", "GREATER_THAN", 0.0),
        ("PG-008", "year_stability", "MINIMUM_CALENDAR_YEAR_BASE_EXPECTANCY_R", "GREATER_THAN_OR_EQUAL", 0.0),
        ("PG-009", "stress_cost", "STRESS_NORMALIZED_AVERAGE_RESULT_R", "GREATER_THAN_OR_EQUAL", 0.0),
        ("PG-010", "stress_cost", "STRESS_NORMALIZED_PROFIT_FACTOR", "GREATER_THAN_OR_EQUAL", 1.0),
        ("PG-011", "stress_cost", "STRESS_POSITIVE_WINDOW_RATE", "GREATER_THAN_OR_EQUAL", 0.45),
        ("PG-012", "multiplicity", "HOLM_ADJUSTED_PRIMARY_P_VALUE", "LESS_THAN_OR_EQUAL", 0.05),
        ("PG-013", "cost_completeness", "FIXED_COST_PROFILE_ROWS_PUBLISHED", "EQUAL", 5),
        ("PG-014", "integrity", "ALL_FAIL_CLOSED_INTEGRITY_CHECKS_PASS", "EQUAL", True),
    ]
    return pd.DataFrame(
        [
            {
                "gate_order": order,
                "gate_id": gate_id,
                "category": category,
                "metric": metric,
                "operator": operator,
                "threshold_json": canonical_json(threshold),
                "mandatory": True,
                "override_allowed": False,
                "mutable_after_freeze": False,
            }
            for order, (gate_id, category, metric, operator, threshold) in enumerate(
                gates,
                start=1,
            )
        ]
    )


def build_holdout_boundary() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "holdout_order": 1,
                "holdout_id": "RETROSPECTIVE_LOCKBOX_2026H1_V1",
                "path": "data/holdout/strategy_recovery_retrospective_lockbox_2026h1_v1.csv",
                "evidence_tier": "SECONDARY_RETROSPECTIVE_LOCKBOX",
                "phase_2d_must_be_absent": True,
                "phase_2d_access_allowed": False,
                "phase_2d_open_allowed": False,
                "future_open_permission_granted": False,
                "mutable_after_freeze": False,
            },
            {
                "holdout_order": 2,
                "holdout_id": "PROSPECTIVE_HOLDOUT_20260720_20270120_V1",
                "path": "data/holdout/strategy_recovery_prospective_20260720_20270120_v1.csv",
                "evidence_tier": "PRIMARY_PROSPECTIVE_CONFIRMATION",
                "phase_2d_must_be_absent": True,
                "phase_2d_access_allowed": False,
                "phase_2d_open_allowed": False,
                "future_open_permission_granted": False,
                "mutable_after_freeze": False,
            },
        ]
    )


def build_specification_artifacts() -> dict[str, pd.DataFrame]:
    common = build_common_execution_contract()
    common_sha = canonical_frame_sha256(common)
    families = build_candidate_family_registry(common_sha)
    variants = build_candidate_variant_registry(families, common_sha)
    return {
        "common_execution_contract": common,
        "candidate_family_registry": families,
        "candidate_variant_registry": variants,
        "cost_profile_freeze": build_cost_profile_freeze(),
        "evaluation_order": build_evaluation_order(variants),
        "multiplicity_contract": build_multiplicity_contract(),
        "promotion_gate_contract": build_promotion_gate_contract(),
        "holdout_boundary": build_holdout_boundary(),
    }


def build_specification_manifest(
    artifacts: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if tuple(artifacts) != SPECIFICATION_ARTIFACT_ORDER:
        raise ValueError("Specification artifact order is not canonical.")
    rows: list[dict[str, Any]] = []
    for artifact_order, name in enumerate(SPECIFICATION_ARTIFACT_ORDER, start=1):
        frame = artifacts[name]
        rows.append(
            {
                "artifact_order": artifact_order,
                "artifact_name": name,
                "output_file": f"{name}_v1.csv",
                "schema_version": SPECIFICATION_SCHEMA_VERSION,
                "row_count": len(frame),
                "column_count": len(frame.columns),
                "canonical_sha256": canonical_frame_sha256(frame),
                "mutable_after_freeze": False,
            }
        )
    manifest = pd.DataFrame(rows)
    root_payload = {
        "schema_version": SPECIFICATION_SCHEMA_VERSION,
        "source_baseline_commit": SOURCE_BASELINE_COMMIT,
        "source_phase_2c_archive_sha256": SOURCE_PHASE_2C_ARCHIVE_SHA256,
        "artifacts": manifest[
            [
                "artifact_order",
                "artifact_name",
                "row_count",
                "column_count",
                "canonical_sha256",
            ]
        ].to_dict(orient="records"),
    }
    root_sha = canonical_sha256(root_payload)
    if root_sha != EXPECTED_SPECIFICATION_ROOT_SHA256:
        raise ValueError(
            "Specification root drifted from the preregistered golden SHA-256."
        )
    root = pd.DataFrame(
        [
            {
                "schema_version": SPECIFICATION_SCHEMA_VERSION,
                "source_baseline_commit": SOURCE_BASELINE_COMMIT,
                "source_phase_2c_archive_sha256": SOURCE_PHASE_2C_ARCHIVE_SHA256,
                "artifact_count": len(manifest),
                "family_count": FROZEN_FAMILY_COUNT,
                "variant_count": FROZEN_VARIANT_COUNT,
                "specification_root_sha256": root_sha,
                "status": SPECIFICATION_STATUS,
                "evaluation_allowed": False,
                "selection_allowed": False,
                "holdout_access_allowed": False,
                "mutable_after_freeze": False,
            }
        ]
    )
    return manifest, root


def verify_specification_manifest(
    artifacts: dict[str, pd.DataFrame],
    manifest: pd.DataFrame,
    root: pd.DataFrame,
) -> tuple[bool, str]:
    try:
        rebuilt_manifest, rebuilt_root = build_specification_manifest(artifacts)
    except Exception as exc:
        return False, f"manifest rebuild failed: {type(exc).__name__}: {exc}"
    manifest_equal = canonical_frame_payload(manifest) == canonical_frame_payload(
        rebuilt_manifest
    )
    root_equal = canonical_frame_payload(root) == canonical_frame_payload(
        rebuilt_root
    )
    return (
        manifest_equal and root_equal,
        f"manifest_equal={manifest_equal}, root_equal={root_equal}",
    )


def validate_registry_limits(
    families: pd.DataFrame,
    variants: pd.DataFrame,
) -> tuple[bool, str]:
    family_counts = variants.groupby("family_id")["variant_id"].nunique()
    valid = bool(
        0 < len(families) <= FAMILY_LIMIT
        and families["family_id"].is_unique
        and 0 < len(variants) <= TOTAL_VARIANT_LIMIT
        and variants["variant_id"].is_unique
        and set(variants["family_id"]) == set(families["family_id"])
        and family_counts.le(VARIANT_LIMIT_PER_FAMILY).all()
        and len(families) == FROZEN_FAMILY_COUNT
        and len(variants) == FROZEN_VARIANT_COUNT
        and family_counts.eq(FROZEN_VARIANTS_PER_FAMILY).all()
    )
    return valid, (
        f"families={len(families)}/{FAMILY_LIMIT}, variants={len(variants)}/"
        f"{TOTAL_VARIANT_LIMIT}, per_family={family_counts.to_dict()}"
    )


def validate_new_identifiers_and_no_evaluation(
    families: pd.DataFrame,
    variants: pd.DataFrame,
) -> tuple[bool, str]:
    identifiers = [
        *families["family_id"].astype(str).tolist(),
        *variants["variant_id"].astype(str).tolist(),
    ]
    identifiers_upper = [identifier.upper() for identifier in identifiers]
    banned_found = sorted(
        {
            token
            for token in BANNED_IDENTIFIER_TOKENS
            if any(token in identifier for identifier in identifiers_upper)
        }
    )
    boolean_columns = [
        "retired_reference_import_allowed",
        "evaluated",
        "ranking_allowed",
        "selection_allowed",
        "mutable_after_freeze",
    ]
    boolean_false = bool(
        not families[boolean_columns].astype(bool).any(axis=None)
        and not variants[boolean_columns].astype(bool).any(axis=None)
    )
    result_rows_zero = bool(
        pd.to_numeric(variants["result_rows"], errors="coerce").eq(0).all()
    )
    valid = bool(
        not banned_found
        and SHORT_REJECTED_REFERENCE not in identifiers
        and boolean_false
        and result_rows_zero
    )
    return valid, (
        f"identifiers={len(identifiers)}, banned_found={banned_found}, "
        f"boolean_false={boolean_false}, result_rows_zero={result_rows_zero}"
    )


def build_acceptance_criteria() -> pd.DataFrame:
    criteria = [
        ("AC-001", "All 14 Phase 2C reports match their frozen SHA-256 and row counts."),
        ("AC-002", "Phase 2C is completed with 26/26 checks, zero blockers and zero errors."),
        ("AC-003", "Exactly three new families and two variants per family are frozen within the 3x4 limit."),
        ("AC-004", "No identifier reuses the retired SHORT identity and no retired strategy module is imported."),
        ("AC-005", "BTCUSDT, ETHUSDT and SOLUSDT remain the complete fixed cohort."),
        ("AC-006", "Closed-candle timing, next-open fill, RR, risk, costs and evaluation order are immutable."),
        ("AC-007", "Holm-Bonferroni multiplicity over all six variants and its bootstrap inputs are frozen."),
        ("AC-008", "Promotion requires 100 aggregate trades, 20 per symbol, base edge, stress stability and all gates."),
        ("AC-009", "Every specification artifact and the root bundle have reproducible canonical SHA-256 values."),
        ("AC-010", "No result, comparison, ranking, winner, holdout access or operational permission is produced."),
        ("AC-011", "Both holdouts and all official forward artifacts remain absent."),
        ("AC-012", "Every ERROR check passes and errors_v1.csv is empty."),
    ]
    return pd.DataFrame(criteria, columns=["criterion_id", "acceptance_criterion"])
