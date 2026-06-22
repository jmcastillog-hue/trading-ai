from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from src.journal.system_forward_observation_record_builder_v1 import (
    SystemForwardObservationCandidate,
    build_system_forward_observation_records,
)


@dataclass(frozen=True)
class ForwardObservationCandidateDetectorConfig:
    allowed_directions: tuple[str, ...] = ("SHORT",)
    allowed_signal_types: tuple[str, ...] = (
        "SHORT_ENTRY_SIGNAL",
        "FORWARD_OBSERVATION_CANDIDATE",
        "SHORT_REARMED",
    )
    blocked_router_decisions: tuple[str, ...] = (
        "BLOCKED",
        "REJECTED",
        "NO_TRADE",
        "LIVE_EXECUTION_NOT_ALLOWED",
    )
    default_symbol: str = "BTCUSDT"
    default_timeframe: str = "15m"
    default_cost_profile: str = "BINANCE_SCALP_BASE_ESTIMATE"
    default_context_name: str = "NORMAL_VALIDATION_CONTEXT"
    default_risk_reward: float = 2.5
    default_manual_reviewer: str = "SYSTEM_GENERATED_REVIEW_REQUIRED"
    data_source: str = "FORWARD_OBSERVATION_CANDIDATE_DETECTOR_V1"


def safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except Exception:
        pass

    return str(value).strip()


def safe_upper(value: Any, default: str = "") -> str:
    return safe_str(value, default).upper()


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value

    text = safe_str(value).lower()

    if text in {"true", "1", "yes", "y", "si", "sí"}:
        return True

    if text in {"false", "0", "no", "n"}:
        return False

    return default


def first_existing_value(
    row: pd.Series,
    candidate_columns: list[str],
    default: Any = None,
) -> Any:
    for column in candidate_columns:
        if column in row.index:
            value = row[column]

            try:
                if pd.isna(value):
                    continue
            except Exception:
                pass

            if safe_str(value) != "":
                return value

    return default


def normalize_observed_at(value: Any) -> str:
    timestamp = pd.to_datetime(value, errors="coerce")

    if pd.isna(timestamp):
        raise ValueError(f"Invalid observed_at/timestamp value: {value}")

    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def validate_detector_input_columns(signals_df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    required_any_groups = [
        ("observed_at_or_timestamp", ["observed_at", "timestamp", "signal_time"]),
        ("entry", ["entry_theoretical", "entry_price", "entry"]),
        ("stop", ["stop_theoretical", "stop_price", "stop"]),
    ]

    for check_name, columns in required_any_groups:
        found = [column for column in columns if column in signals_df.columns]

        rows.append(
            {
                "check_name": check_name,
                "passed": len(found) > 0,
                "details": ", ".join(found) if found else f"missing_any_of={columns}",
            }
        )

    rows.append(
        {
            "check_name": "has_rows",
            "passed": len(signals_df) > 0,
            "details": f"rows={len(signals_df)}",
        }
    )

    return pd.DataFrame(rows)


def classify_signal_row(
    row: pd.Series,
    config: ForwardObservationCandidateDetectorConfig,
) -> tuple[bool, str]:
    signal_active = safe_bool(
        first_existing_value(
            row,
            ["signal_active", "setup_detected", "observable", "should_observe"],
            True,
        ),
        default=True,
    )

    if not signal_active:
        return False, "SIGNAL_NOT_ACTIVE"

    signal_type = safe_upper(
        first_existing_value(
            row,
            ["signal_type", "setup_state", "candidate_type", "state"],
            "FORWARD_OBSERVATION_CANDIDATE",
        )
    )

    if signal_type not in set(config.allowed_signal_types):
        return False, f"SIGNAL_TYPE_NOT_ALLOWED:{signal_type}"

    router_decision = safe_upper(
        first_existing_value(
            row,
            ["router_decision", "decision", "risk_decision"],
            "WATCH_ONLY",
        )
    )

    if router_decision in set(config.blocked_router_decisions):
        return False, f"ROUTER_DECISION_BLOCKED:{router_decision}"

    direction = safe_upper(
        first_existing_value(
            row,
            ["direction", "side", "trade_direction"],
            "",
        )
    )

    if direction not in set(config.allowed_directions):
        return False, f"DIRECTION_NOT_ALLOWED:{direction}"

    entry = safe_float(
        first_existing_value(
            row,
            ["entry_theoretical", "entry_price", "entry"],
            0.0,
        )
    )

    stop = safe_float(
        first_existing_value(
            row,
            ["stop_theoretical", "stop_price", "stop"],
            0.0,
        )
    )

    if entry <= 0:
        return False, "INVALID_ENTRY_PRICE"

    if stop <= 0:
        return False, "INVALID_STOP_PRICE"

    if direction == "SHORT" and stop <= entry:
        return False, "INVALID_SHORT_STOP_NOT_ABOVE_ENTRY"

    if direction == "LONG" and stop >= entry:
        return False, "INVALID_LONG_STOP_NOT_BELOW_ENTRY"

    return True, "OBSERVABLE_CANDIDATE"


def build_candidate_from_signal_row(
    row: pd.Series,
    config: ForwardObservationCandidateDetectorConfig,
) -> SystemForwardObservationCandidate:
    observed_at = normalize_observed_at(
        first_existing_value(
            row,
            ["observed_at", "timestamp", "signal_time"],
            None,
        )
    )

    symbol = safe_upper(
        first_existing_value(
            row,
            ["symbol", "asset"],
            config.default_symbol,
        )
    )

    timeframe = safe_str(
        first_existing_value(
            row,
            ["timeframe", "tf"],
            config.default_timeframe,
        ),
        config.default_timeframe,
    )

    cost_profile = safe_upper(
        first_existing_value(
            row,
            ["cost_profile", "execution_profile"],
            config.default_cost_profile,
        )
    )

    context_name = safe_upper(
        first_existing_value(
            row,
            ["context_name", "context", "router_context"],
            config.default_context_name,
        )
    )

    direction = safe_upper(
        first_existing_value(
            row,
            ["direction", "side", "trade_direction"],
            "SHORT",
        )
    )

    entry = safe_float(
        first_existing_value(
            row,
            ["entry_theoretical", "entry_price", "entry"],
            0.0,
        )
    )

    stop = safe_float(
        first_existing_value(
            row,
            ["stop_theoretical", "stop_price", "stop"],
            0.0,
        )
    )

    risk_reward = safe_float(
        first_existing_value(
            row,
            ["risk_reward", "rr", "target_r"],
            config.default_risk_reward,
        ),
        config.default_risk_reward,
    )

    invalidation_level_value = first_existing_value(
        row,
        ["invalidation_level", "invalid_level"],
        None,
    )

    invalidation_level = (
        None
        if invalidation_level_value is None or safe_str(invalidation_level_value) == ""
        else safe_float(invalidation_level_value)
    )

    signal_type = safe_upper(
        first_existing_value(
            row,
            ["signal_type", "setup_state", "candidate_type", "state"],
            "FORWARD_OBSERVATION_CANDIDATE",
        )
    )

    router_decision = safe_upper(
        first_existing_value(
            row,
            ["router_decision", "decision", "risk_decision"],
            "WATCH_ONLY",
        )
    )

    invalidation_reason = safe_str(
        first_existing_value(
            row,
            ["invalidation_reason"],
            "System candidate detector invalidation: stop-based structural level.",
        )
    )

    manual_notes = safe_str(
        first_existing_value(
            row,
            ["manual_notes", "notes", "comment"],
            (
                f"System-detected forward observation candidate. "
                f"signal_type={signal_type}; router_decision={router_decision}. "
                f"No execution. Human review required."
            ),
        )
    )

    return SystemForwardObservationCandidate(
        observed_at=observed_at,
        symbol=symbol,
        timeframe=timeframe,
        cost_profile=cost_profile,
        context_name=context_name,
        direction=direction,
        entry_theoretical=entry,
        stop_theoretical=stop,
        risk_reward=risk_reward,
        invalidation_level=invalidation_level,
        invalidation_reason=invalidation_reason,
        manual_reviewer=config.default_manual_reviewer,
        manual_notes=manual_notes,
        data_source=config.data_source,
        screenshot_path=safe_str(
            first_existing_value(row, ["screenshot_path"], "")
        ),
    )


def detect_forward_observation_candidates(
    signals_df: pd.DataFrame,
    config: ForwardObservationCandidateDetectorConfig | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if config is None:
        config = ForwardObservationCandidateDetectorConfig()

    validation_df = validate_detector_input_columns(signals_df)

    if validation_df["passed"].eq(False).any():
        return (
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame(),
            validation_df,
        )

    accepted_rows = []
    rejected_rows = []
    candidates = []

    for index, row in signals_df.reset_index(drop=True).iterrows():
        is_observable, reason = classify_signal_row(row, config)

        base_detail = {
            "source_row_index": index,
            "detector_decision": reason,
            "observed_at": safe_str(
                first_existing_value(row, ["observed_at", "timestamp", "signal_time"], "")
            ),
            "symbol": safe_upper(first_existing_value(row, ["symbol", "asset"], config.default_symbol)),
            "timeframe": safe_str(first_existing_value(row, ["timeframe", "tf"], config.default_timeframe)),
            "signal_type": safe_upper(
                first_existing_value(row, ["signal_type", "setup_state", "candidate_type", "state"], "")
            ),
            "router_decision": safe_upper(
                first_existing_value(row, ["router_decision", "decision", "risk_decision"], "")
            ),
            "cost_profile": safe_upper(
                first_existing_value(row, ["cost_profile", "execution_profile"], config.default_cost_profile)
            ),
            "context_name": safe_upper(
                first_existing_value(row, ["context_name", "context", "router_context"], config.default_context_name)
            ),
            "direction": safe_upper(first_existing_value(row, ["direction", "side", "trade_direction"], "")),
            "entry_theoretical": safe_float(
                first_existing_value(row, ["entry_theoretical", "entry_price", "entry"], 0.0)
            ),
            "stop_theoretical": safe_float(
                first_existing_value(row, ["stop_theoretical", "stop_price", "stop"], 0.0)
            ),
            "risk_reward": safe_float(
                first_existing_value(row, ["risk_reward", "rr", "target_r"], config.default_risk_reward),
                config.default_risk_reward,
            ),
        }

        if is_observable:
            try:
                candidate = build_candidate_from_signal_row(row, config)
                candidates.append(candidate)
                accepted_rows.append(base_detail)
            except Exception as exc:
                rejected = dict(base_detail)
                rejected["detector_decision"] = f"CANDIDATE_BUILD_ERROR:{repr(exc)}"
                rejected_rows.append(rejected)
        else:
            rejected_rows.append(base_detail)

    records_df = build_system_forward_observation_records(candidates) if candidates else pd.DataFrame()
    accepted_df = pd.DataFrame(accepted_rows)
    rejected_df = pd.DataFrame(rejected_rows)

    return records_df, accepted_df, rejected_df, validation_df


def build_candidate_detector_summary(
    records_df: pd.DataFrame,
    accepted_df: pd.DataFrame,
    rejected_df: pd.DataFrame,
    validation_df: pd.DataFrame,
) -> pd.DataFrame:
    validation_passed = (
        bool(validation_df["passed"].all())
        if not validation_df.empty and "passed" in validation_df.columns
        else False
    )

    observable_candidates = len(accepted_df)
    rejected_candidates = len(rejected_df)
    generated_records = len(records_df)

    if not validation_passed:
        decision = "DETECTOR_INPUT_VALIDATION_FAILED"
    elif generated_records > 0 and generated_records == observable_candidates:
        decision = "DETECTOR_COMPLETED_GENERATED_RECORDS"
    elif generated_records == 0 and rejected_candidates > 0:
        decision = "DETECTOR_COMPLETED_NO_OBSERVABLE_CANDIDATES"
    else:
        decision = "DETECTOR_REVIEW_REQUIRED"

    return pd.DataFrame(
        [
            {
                "validation_passed": validation_passed,
                "observable_candidates": observable_candidates,
                "rejected_candidates": rejected_candidates,
                "generated_records": generated_records,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "detector_decision": decision,
            }
        ]
    )


def build_sample_strategy_signal_candidates() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "observed_at": "2026-06-21 05:00:00",
                "symbol": "BTCUSDT",
                "timeframe": "15m",
                "signal_type": "SHORT_ENTRY_SIGNAL",
                "signal_active": True,
                "router_decision": "WATCH_ONLY",
                "cost_profile": "BINANCE_SCALP_BASE_ESTIMATE",
                "context_name": "NORMAL_VALIDATION_CONTEXT",
                "direction": "SHORT",
                "entry_price": 65050.0,
                "stop_price": 65550.0,
                "risk_reward": 2.5,
                "invalidation_reason": "Detector sample: stop above short pullback structure.",
            },
            {
                "observed_at": "2026-06-21 06:00:00",
                "symbol": "BTCUSDT",
                "timeframe": "15m",
                "signal_type": "SHORT_REARMED",
                "signal_active": True,
                "router_decision": "WATCH_ONLY",
                "cost_profile": "QUANTFURY_SWING_BASE_ESTIMATE",
                "context_name": "WAVE_5_CAUTION_CONTEXT",
                "direction": "SHORT",
                "entry_price": 65100.0,
                "stop_price": 65900.0,
                "risk_reward": 2.5,
                "invalidation_reason": "Detector sample: wave caution invalidation above structure.",
            },
            {
                "observed_at": "2026-06-21 07:00:00",
                "symbol": "BTCUSDT",
                "timeframe": "15m",
                "signal_type": "FIB_ZONE_ACTIVE",
                "signal_active": True,
                "router_decision": "WATCH_ONLY",
                "cost_profile": "BINANCE_SCALP_BASE_ESTIMATE",
                "context_name": "NORMAL_VALIDATION_CONTEXT",
                "direction": "SHORT",
                "entry_price": 64900.0,
                "stop_price": 65400.0,
                "risk_reward": 2.5,
            },
            {
                "observed_at": "2026-06-21 08:00:00",
                "symbol": "BTCUSDT",
                "timeframe": "15m",
                "signal_type": "SHORT_ENTRY_SIGNAL",
                "signal_active": True,
                "router_decision": "BLOCKED",
                "cost_profile": "BINANCE_SCALP_STRESS_ESTIMATE",
                "context_name": "STRESS_OR_DEGRADED_CONTEXT",
                "direction": "SHORT",
                "entry_price": 64800.0,
                "stop_price": 65300.0,
                "risk_reward": 2.5,
            },
        ]
    )