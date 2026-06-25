from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from src.journal.forward_observation_batch_resolver_v1 import (
    ForwardObservationBatchResolverConfig,
    run_forward_observation_batch_resolver,
)
from src.journal.forward_observation_batch_runner_v1 import (
    ForwardObservationBatchRunnerConfig,
    run_forward_observation_batch_runner,
)


@dataclass(frozen=True)
class ForwardEvidenceAccumulationControllerConfig:
    min_forward_observations: int = 100
    preferred_forward_observations: int = 300
    timestamp_column: str = "timestamp"
    same_bar_policy: str = "CONSERVATIVE_STOP"
    max_bars_after_observation: int = 96
    controller_name: str = "FORWARD_EVIDENCE_ACCUMULATION_CONTROLLER_V1"
    paper_trade_execution_allowed: bool = False
    real_capital_allowed: bool = False
    live_alerts_allowed: bool = False
    exchange_execution_allowed: bool = False
    automation_allowed: bool = False


CLOSED_RESOLUTION_STATUSES = {
    "TARGET_HIT",
    "STOP_HIT",
    "TIME_EXIT",
    "MANUAL_CLOSE",
}


EXECUTION_FLAG_COLUMNS = [
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "live_alerts_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
]


PRICE_COLUMNS = [
    "entry_price",
    "stop_price",
    "target_price",
]


def safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except Exception:
        pass

    return str(value).strip()


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or pd.isna(value):
            return default
        return int(value)
    except Exception:
        return default


def summary_value(summary_df: pd.DataFrame, column: str, default: Any = 0) -> Any:
    if summary_df is None or summary_df.empty:
        return default

    if column not in summary_df.columns:
        return default

    try:
        return summary_df.iloc[0][column]
    except Exception:
        return default


def validation_passed(validation_df: pd.DataFrame) -> bool:
    if validation_df is None or validation_df.empty:
        return False

    if "passed" not in validation_df.columns:
        return False

    return bool(validation_df["passed"].all())


def normalize_text_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    normalized = df.copy()

    for column in columns:
        if column not in normalized.columns:
            normalized[column] = ""

        normalized[column] = normalized[column].map(lambda value: safe_str(value))

    return normalized


def normalize_price_levels_df(price_levels_df: pd.DataFrame | None) -> pd.DataFrame:
    if price_levels_df is None or price_levels_df.empty:
        return pd.DataFrame(
            columns=[
                "signal_id",
                "context_name",
                "cost_profile",
                "direction",
                "entry_price",
                "stop_price",
                "target_price",
                "price_level_source",
            ]
        )

    df = price_levels_df.copy()

    for column in [
        "signal_id",
        "context_name",
        "cost_profile",
        "direction",
        "price_level_source",
    ]:
        if column not in df.columns:
            df[column] = ""

        df[column] = df[column].map(lambda value: safe_str(value).upper())

    for column in PRICE_COLUMNS:
        if column not in df.columns:
            df[column] = 0.0

        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0.0)

    return df


def find_price_override(row: pd.Series, price_levels_df: pd.DataFrame) -> pd.Series | None:
    if price_levels_df.empty:
        return None

    row_signal_id = safe_str(row.get("signal_id")).upper()
    row_context_name = safe_str(row.get("context_name")).upper()
    row_cost_profile = safe_str(row.get("cost_profile")).upper()
    row_direction = safe_str(row.get("direction")).upper()

    if row_signal_id and "signal_id" in price_levels_df.columns:
        signal_match = price_levels_df[
            price_levels_df["signal_id"].map(lambda value: safe_str(value).upper()) == row_signal_id
        ]

        if not signal_match.empty:
            return signal_match.iloc[0]

    match_levels = [
        ["context_name", "cost_profile", "direction"],
        ["context_name", "cost_profile"],
        ["context_name"],
    ]

    row_values = {
        "context_name": row_context_name,
        "cost_profile": row_cost_profile,
        "direction": row_direction,
    }

    for match_columns in match_levels:
        if any(row_values.get(column, "") == "" for column in match_columns):
            continue

        mask = pd.Series([True] * len(price_levels_df), index=price_levels_df.index)

        for column in match_columns:
            if column not in price_levels_df.columns:
                mask = pd.Series([False] * len(price_levels_df), index=price_levels_df.index)
                break

            mask = mask & (
                price_levels_df[column].map(lambda value: safe_str(value).upper())
                == row_values[column]
            )

        matched = price_levels_df[mask]

        if not matched.empty:
            return matched.iloc[0]

    return None


def apply_price_level_overrides(
    observations_df: pd.DataFrame,
    price_levels_df: pd.DataFrame | None,
) -> pd.DataFrame:
    df = observations_df.copy()

    if df.empty:
        return df

    df = normalize_text_columns(
        df,
        [
            "signal_id",
            "context_name",
            "cost_profile",
            "direction",
        ],
    )

    for column in PRICE_COLUMNS:
        if column not in df.columns:
            df[column] = 0.0

        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0.0)

    if "price_level_source" not in df.columns:
        df["price_level_source"] = ""

    overrides_df = normalize_price_levels_df(price_levels_df)

    if overrides_df.empty:
        return df

    for idx, row in df.iterrows():
        override = find_price_override(row, overrides_df)

        if override is None:
            continue

        for column in PRICE_COLUMNS:
            override_value = safe_float(override.get(column), 0.0)

            if override_value > 0:
                df.at[idx, column] = override_value

        source = safe_str(override.get("price_level_source"), "PRICE_LEVEL_OVERRIDE")
        df.at[idx, "price_level_source"] = source if source else "PRICE_LEVEL_OVERRIDE"

    return df


def count_cumulative_closed_observations(dataset_df: pd.DataFrame) -> int:
    if dataset_df is None or dataset_df.empty:
        return 0

    if "resolution_status" not in dataset_df.columns:
        return 0

    statuses = dataset_df["resolution_status"].map(lambda value: safe_str(value).upper())

    return int(statuses.isin(CLOSED_RESOLUTION_STATUSES).sum())


def all_execution_flags_false(dataset_df: pd.DataFrame) -> bool:
    if dataset_df is None or dataset_df.empty:
        return True

    for column in EXECUTION_FLAG_COLUMNS:
        if column not in dataset_df.columns:
            return False

        if dataset_df[column].astype(bool).any():
            return False

    return True


def build_readiness_state(
    cumulative_closed_observations: int,
    config: ForwardEvidenceAccumulationControllerConfig,
) -> str:
    if cumulative_closed_observations >= config.preferred_forward_observations:
        return "PREFERRED_FORWARD_SAMPLE_REACHED_REVIEW_REQUIRED"

    if cumulative_closed_observations >= config.min_forward_observations:
        return "MINIMUM_FORWARD_SAMPLE_REACHED_REVIEW_REQUIRED"

    return "FORWARD_SAMPLE_INSUFFICIENT"


def validate_accumulation_controller_output(
    runner_summary_df: pd.DataFrame,
    runner_validation_df: pd.DataFrame,
    resolver_summary_df: pd.DataFrame,
    resolver_validation_df: pd.DataFrame,
    priced_dataset_df: pd.DataFrame,
    dataset_after_resolution_df: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    rows.append(
        {
            "check_name": "runner_summary_exists",
            "passed": not runner_summary_df.empty,
            "severity": "ERROR",
            "details": f"runner_summary_rows={len(runner_summary_df)}",
        }
    )

    rows.append(
        {
            "check_name": "runner_validation_passed",
            "passed": validation_passed(runner_validation_df),
            "severity": "ERROR",
            "details": "runner validation must pass",
        }
    )

    rows.append(
        {
            "check_name": "resolver_summary_exists",
            "passed": not resolver_summary_df.empty,
            "severity": "ERROR",
            "details": f"resolver_summary_rows={len(resolver_summary_df)}",
        }
    )

    rows.append(
        {
            "check_name": "resolver_validation_passed",
            "passed": validation_passed(resolver_validation_df),
            "severity": "ERROR",
            "details": "resolver validation must pass",
        }
    )

    rows.append(
        {
            "check_name": "priced_dataset_exists",
            "passed": not priced_dataset_df.empty,
            "severity": "ERROR",
            "details": f"priced_dataset_rows={len(priced_dataset_df)}",
        }
    )

    rows.append(
        {
            "check_name": "dataset_after_resolution_exists",
            "passed": not dataset_after_resolution_df.empty,
            "severity": "ERROR",
            "details": f"dataset_after_resolution_rows={len(dataset_after_resolution_df)}",
        }
    )

    rows.append(
        {
            "check_name": "all_execution_flags_false",
            "passed": all_execution_flags_false(dataset_after_resolution_df),
            "severity": "ERROR",
            "details": "controller must never enable execution flags",
        }
    )

    return pd.DataFrame(rows)


def build_accumulation_controller_summary_df(
    source_signals_df: pd.DataFrame,
    runner_summary_df: pd.DataFrame,
    resolver_summary_df: pd.DataFrame,
    controller_validation_df: pd.DataFrame,
    dataset_after_resolution_df: pd.DataFrame,
    config: ForwardEvidenceAccumulationControllerConfig,
) -> pd.DataFrame:
    controller_validation_passed = validation_passed(controller_validation_df)

    source_signal_rows = len(source_signals_df)
    generated_observations = safe_int(summary_value(runner_summary_df, "generated_observations", 0))
    new_observations = safe_int(summary_value(runner_summary_df, "accepted_new_observations", 0))
    duplicate_observations = safe_int(summary_value(runner_summary_df, "skipped_duplicate_observations", 0))
    detector_accepted_candidates = safe_int(
        summary_value(runner_summary_df, "detector_accepted_candidates", 0)
    )
    detector_rejected_candidates = safe_int(
        summary_value(runner_summary_df, "detector_rejected_candidates", 0)
    )

    resolution_input_observations = safe_int(
        summary_value(resolver_summary_df, "resolution_input_observations", 0)
    )
    closed_observations = safe_int(summary_value(resolver_summary_df, "closed_observations", 0))
    open_observations = safe_int(summary_value(resolver_summary_df, "open_observations", 0))
    error_observations = safe_int(summary_value(resolver_summary_df, "error_observations", 0))
    wins = safe_int(summary_value(resolver_summary_df, "wins", 0))
    losses = safe_int(summary_value(resolver_summary_df, "losses", 0))
    avg_result_r = safe_float(summary_value(resolver_summary_df, "avg_result_r", 0.0))
    sum_result_r = safe_float(summary_value(resolver_summary_df, "sum_result_r", 0.0))

    cumulative_closed_observations = count_cumulative_closed_observations(
        dataset_after_resolution_df
    )

    minimum_sample_reached = cumulative_closed_observations >= config.min_forward_observations
    preferred_sample_reached = cumulative_closed_observations >= config.preferred_forward_observations

    readiness_state = build_readiness_state(
        cumulative_closed_observations=cumulative_closed_observations,
        config=config,
    )

    if not controller_validation_passed:
        controller_decision = "ACCUMULATION_CONTROLLER_VALIDATION_FAILED"
    elif error_observations > 0:
        controller_decision = "ACCUMULATION_CONTROLLER_COMPLETED_WITH_ERRORS"
    elif closed_observations > 0:
        controller_decision = "ACCUMULATION_CONTROLLER_COMPLETED_RESOLVED_BATCH"
    elif open_observations > 0:
        controller_decision = "ACCUMULATION_CONTROLLER_COMPLETED_OPEN_BATCH"
    elif new_observations == 0 and duplicate_observations > 0:
        controller_decision = "ACCUMULATION_CONTROLLER_COMPLETED_DUPLICATES_ONLY"
    else:
        controller_decision = "ACCUMULATION_CONTROLLER_COMPLETED_NO_NEW_EVIDENCE"

    return pd.DataFrame(
        [
            {
                "controller_validation_passed": controller_validation_passed,
                "source_signal_rows": source_signal_rows,
                "detector_accepted_candidates": detector_accepted_candidates,
                "detector_rejected_candidates": detector_rejected_candidates,
                "generated_observations": generated_observations,
                "new_observations": new_observations,
                "duplicate_observations": duplicate_observations,
                "resolution_input_observations": resolution_input_observations,
                "closed_observations": closed_observations,
                "open_observations": open_observations,
                "error_observations": error_observations,
                "wins": wins,
                "losses": losses,
                "avg_result_r": round(avg_result_r, 6),
                "sum_result_r": round(sum_result_r, 6),
                "cumulative_closed_observations": cumulative_closed_observations,
                "min_forward_observations": config.min_forward_observations,
                "preferred_forward_observations": config.preferred_forward_observations,
                "minimum_sample_reached": minimum_sample_reached,
                "preferred_sample_reached": preferred_sample_reached,
                "sample_gap_to_minimum": max(
                    config.min_forward_observations - cumulative_closed_observations,
                    0,
                ),
                "sample_gap_to_preferred": max(
                    config.preferred_forward_observations - cumulative_closed_observations,
                    0,
                ),
                "readiness_state": readiness_state,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "controller_decision": controller_decision,
            }
        ]
    )


def run_forward_evidence_accumulation_controller(
    source_signals_df: pd.DataFrame,
    existing_dataset_df: pd.DataFrame,
    ohlc_df: pd.DataFrame,
    price_levels_df: pd.DataFrame | None = None,
    config: ForwardEvidenceAccumulationControllerConfig | None = None,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    if config is None:
        config = ForwardEvidenceAccumulationControllerConfig()

    (
        runner_summary_df,
        runner_validation_df,
        generated_observations_df,
        detector_accepted_df,
        detector_rejected_df,
        accepted_new_df,
        duplicate_df,
        open_dataset_after_runner_df,
    ) = run_forward_observation_batch_runner(
        source_signals_df=source_signals_df,
        existing_dataset_df=existing_dataset_df,
        config=ForwardObservationBatchRunnerConfig(
            min_forward_observations=config.min_forward_observations,
            preferred_forward_observations=config.preferred_forward_observations,
            paper_trade_execution_allowed=False,
            real_capital_allowed=False,
            live_alerts_allowed=False,
            exchange_execution_allowed=False,
            automation_allowed=False,
        ),
    )

    priced_dataset_df = apply_price_level_overrides(
        observations_df=open_dataset_after_runner_df,
        price_levels_df=price_levels_df,
    )

    (
        resolver_summary_df,
        resolver_validation_df,
        source_observations_df,
        resolution_input_df,
        invalid_price_df,
        resolved_all_df,
        resolved_closed_df,
        still_open_df,
        resolution_errors_df,
        dataset_after_resolution_df,
    ) = run_forward_observation_batch_resolver(
        observations_df=priced_dataset_df,
        ohlc_df=ohlc_df,
        config=ForwardObservationBatchResolverConfig(
            min_forward_observations=config.min_forward_observations,
            preferred_forward_observations=config.preferred_forward_observations,
            timestamp_column=config.timestamp_column,
            same_bar_policy=config.same_bar_policy,
            max_bars_after_observation=config.max_bars_after_observation,
            paper_trade_execution_allowed=False,
            real_capital_allowed=False,
            live_alerts_allowed=False,
            exchange_execution_allowed=False,
            automation_allowed=False,
        ),
    )

    controller_validation_df = validate_accumulation_controller_output(
        runner_summary_df=runner_summary_df,
        runner_validation_df=runner_validation_df,
        resolver_summary_df=resolver_summary_df,
        resolver_validation_df=resolver_validation_df,
        priced_dataset_df=priced_dataset_df,
        dataset_after_resolution_df=dataset_after_resolution_df,
    )

    controller_summary_df = build_accumulation_controller_summary_df(
        source_signals_df=source_signals_df,
        runner_summary_df=runner_summary_df,
        resolver_summary_df=resolver_summary_df,
        controller_validation_df=controller_validation_df,
        dataset_after_resolution_df=dataset_after_resolution_df,
        config=config,
    )

    return (
        controller_summary_df,
        controller_validation_df,
        runner_summary_df,
        runner_validation_df,
        resolver_summary_df,
        resolver_validation_df,
        generated_observations_df,
        detector_accepted_df,
        detector_rejected_df,
        accepted_new_df,
        duplicate_df,
        priced_dataset_df,
        resolved_closed_df,
        still_open_df,
        dataset_after_resolution_df,
    )