from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class ForwardDatasetQualityGateConfig:
    min_resolved_observations: int = 100
    preferred_resolved_observations: int = 300
    max_error_rows: int = 0
    max_duplicate_signal_ids: int = 0
    min_unique_contexts: int = 1
    min_unique_cost_profiles: int = 1
    min_unique_directions: int = 1
    max_open_ratio: float = 0.50
    paper_trade_execution_allowed: bool = False
    real_capital_allowed: bool = False
    live_alerts_allowed: bool = False
    exchange_execution_allowed: bool = False
    automation_allowed: bool = False


REQUIRED_COLUMNS = [
    "signal_id",
    "observed_at",
    "symbol",
    "timeframe",
    "cost_profile",
    "context_name",
    "direction",
    "resolution_status",
    "result_r",
    "mfe_r",
    "mae_r",
    "bars_to_resolution",
]

NUMERIC_COLUMNS = [
    "result_r",
    "mfe_r",
    "mae_r",
    "bars_to_resolution",
]

OPEN_STATUSES = {
    "OPEN_UNRESOLVED",
    "OPEN_NO_FUTURE_DATA",
}

CLOSED_STATUSES = {
    "TARGET_HIT",
    "STOP_HIT",
    "INVALIDATION_HIT",
    "AMBIGUOUS_BOTH_HIT_CONSERVATIVE_STOP",
    "AMBIGUOUS_BOTH_HIT_ZERO_R",
    "AMBIGUOUS_BOTH_HIT_TARGET_FIRST",
    "AMBIGUOUS_BOTH_HIT_REVIEW_REQUIRED",
}


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


def ensure_quality_columns(dataset_df: pd.DataFrame) -> pd.DataFrame:
    df = dataset_df.copy()

    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            df[column] = ""

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    text_columns = [
        "signal_id",
        "observed_at",
        "symbol",
        "timeframe",
        "cost_profile",
        "context_name",
        "direction",
        "resolution_status",
    ]

    for column in text_columns:
        df[column] = df[column].map(lambda value: safe_str(value))

    df["symbol"] = df["symbol"].str.upper()
    df["timeframe"] = df["timeframe"].str.lower()
    df["cost_profile"] = df["cost_profile"].str.upper()
    df["context_name"] = df["context_name"].str.upper()
    df["direction"] = df["direction"].str.upper()
    df["resolution_status"] = df["resolution_status"].str.upper()

    df["is_open"] = df["resolution_status"].isin(OPEN_STATUSES)
    df["is_error"] = df["resolution_status"].str.startswith("RESOLUTION_ERROR")
    df["is_closed"] = (
        df["resolution_status"].isin(CLOSED_STATUSES)
        | (
            ~df["is_open"]
            & ~df["is_error"]
            & (df["resolution_status"] != "")
        )
    )

    df["is_win"] = df["is_closed"] & (df["result_r"] > 0)
    df["is_loss"] = df["is_closed"] & (df["result_r"] < 0)

    return df


def build_check_row(
    check_name: str,
    passed: bool,
    severity: str,
    metric_value: Any,
    threshold: Any,
    details: str,
) -> dict[str, Any]:
    return {
        "check_name": check_name,
        "passed": bool(passed),
        "severity": severity,
        "metric_value": metric_value,
        "threshold": threshold,
        "details": details,
    }


def validate_required_columns(dataset_df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for column in REQUIRED_COLUMNS:
        passed = column in dataset_df.columns
        rows.append(
            build_check_row(
                check_name=f"required_column:{column}",
                passed=passed,
                severity="ERROR",
                metric_value="PRESENT" if passed else "MISSING",
                threshold="PRESENT",
                details="OK" if passed else "Missing required column",
            )
        )

    return pd.DataFrame(rows)


def validate_dataset_size(
    quality_df: pd.DataFrame,
    config: ForwardDatasetQualityGateConfig,
) -> pd.DataFrame:
    total_rows = len(quality_df)
    resolved_rows = int(quality_df["is_closed"].sum()) if not quality_df.empty else 0
    open_rows = int(quality_df["is_open"].sum()) if not quality_df.empty else 0

    open_ratio = round(open_rows / total_rows, 6) if total_rows > 0 else 0.0

    rows = [
        build_check_row(
            check_name="dataset_has_rows",
            passed=total_rows > 0,
            severity="ERROR",
            metric_value=total_rows,
            threshold="> 0",
            details=f"total_rows={total_rows}",
        ),
        build_check_row(
            check_name="minimum_resolved_observations",
            passed=resolved_rows >= config.min_resolved_observations,
            severity="BLOCKER",
            metric_value=resolved_rows,
            threshold=config.min_resolved_observations,
            details=(
                f"resolved_rows={resolved_rows}; "
                f"minimum_required={config.min_resolved_observations}"
            ),
        ),
        build_check_row(
            check_name="preferred_resolved_observations",
            passed=resolved_rows >= config.preferred_resolved_observations,
            severity="INFO",
            metric_value=resolved_rows,
            threshold=config.preferred_resolved_observations,
            details=(
                f"resolved_rows={resolved_rows}; "
                f"preferred_required={config.preferred_resolved_observations}"
            ),
        ),
        build_check_row(
            check_name="open_ratio_limit",
            passed=open_ratio <= config.max_open_ratio,
            severity="WARNING",
            metric_value=open_ratio,
            threshold=config.max_open_ratio,
            details=f"open_rows={open_rows}; total_rows={total_rows}",
        ),
    ]

    return pd.DataFrame(rows)


def validate_signal_ids(
    quality_df: pd.DataFrame,
    config: ForwardDatasetQualityGateConfig,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if quality_df.empty:
        checks_df = pd.DataFrame(
            [
                build_check_row(
                    check_name="signal_id_presence",
                    passed=False,
                    severity="ERROR",
                    metric_value=0,
                    threshold="all rows",
                    details="Dataset empty",
                )
            ]
        )
        return checks_df, pd.DataFrame()

    missing_signal_id_rows = quality_df[quality_df["signal_id"] == ""].copy()

    non_empty_signal_ids = quality_df[quality_df["signal_id"] != ""].copy()
    duplicate_mask = non_empty_signal_ids["signal_id"].duplicated(keep=False)
    duplicate_signal_ids_df = non_empty_signal_ids[duplicate_mask].copy()

    duplicate_count = (
        duplicate_signal_ids_df["signal_id"].nunique()
        if not duplicate_signal_ids_df.empty
        else 0
    )

    checks_df = pd.DataFrame(
        [
            build_check_row(
                check_name="signal_id_presence",
                passed=len(missing_signal_id_rows) == 0,
                severity="ERROR",
                metric_value=len(missing_signal_id_rows),
                threshold=0,
                details=f"missing_signal_id_rows={len(missing_signal_id_rows)}",
            ),
            build_check_row(
                check_name="duplicate_signal_ids",
                passed=duplicate_count <= config.max_duplicate_signal_ids,
                severity="ERROR",
                metric_value=duplicate_count,
                threshold=config.max_duplicate_signal_ids,
                details=f"duplicate_signal_id_count={duplicate_count}",
            ),
        ]
    )

    return checks_df, duplicate_signal_ids_df


def validate_numeric_integrity(quality_df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for column in NUMERIC_COLUMNS:
        if quality_df.empty:
            invalid_count = 0
        else:
            invalid_count = int(quality_df[column].isna().sum())

        rows.append(
            build_check_row(
                check_name=f"numeric_integrity:{column}",
                passed=invalid_count == 0,
                severity="ERROR",
                metric_value=invalid_count,
                threshold=0,
                details=f"invalid_numeric_rows={invalid_count}",
            )
        )

    return pd.DataFrame(rows)


def validate_resolution_integrity(
    quality_df: pd.DataFrame,
    config: ForwardDatasetQualityGateConfig,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if quality_df.empty:
        error_rows_df = pd.DataFrame()
        error_count = 0
    else:
        error_rows_df = quality_df[quality_df["is_error"]].copy()
        error_count = len(error_rows_df)

    checks_df = pd.DataFrame(
        [
            build_check_row(
                check_name="resolution_error_rows",
                passed=error_count <= config.max_error_rows,
                severity="ERROR",
                metric_value=error_count,
                threshold=config.max_error_rows,
                details=f"resolution_error_rows={error_count}",
            )
        ]
    )

    return checks_df, error_rows_df


def validate_distribution(
    quality_df: pd.DataFrame,
    config: ForwardDatasetQualityGateConfig,
) -> pd.DataFrame:
    if quality_df.empty:
        unique_contexts = 0
        unique_cost_profiles = 0
        unique_directions = 0
    else:
        unique_contexts = quality_df.loc[
            quality_df["context_name"] != "",
            "context_name",
        ].nunique()

        unique_cost_profiles = quality_df.loc[
            quality_df["cost_profile"] != "",
            "cost_profile",
        ].nunique()

        unique_directions = quality_df.loc[
            quality_df["direction"] != "",
            "direction",
        ].nunique()

    rows = [
        build_check_row(
            check_name="minimum_unique_contexts",
            passed=unique_contexts >= config.min_unique_contexts,
            severity="WARNING",
            metric_value=unique_contexts,
            threshold=config.min_unique_contexts,
            details=f"unique_contexts={unique_contexts}",
        ),
        build_check_row(
            check_name="minimum_unique_cost_profiles",
            passed=unique_cost_profiles >= config.min_unique_cost_profiles,
            severity="WARNING",
            metric_value=unique_cost_profiles,
            threshold=config.min_unique_cost_profiles,
            details=f"unique_cost_profiles={unique_cost_profiles}",
        ),
        build_check_row(
            check_name="minimum_unique_directions",
            passed=unique_directions >= config.min_unique_directions,
            severity="WARNING",
            metric_value=unique_directions,
            threshold=config.min_unique_directions,
            details=f"unique_directions={unique_directions}",
        ),
    ]

    return pd.DataFrame(rows)


def build_distribution_df(
    quality_df: pd.DataFrame,
    group_column: str,
) -> pd.DataFrame:
    if quality_df.empty or group_column not in quality_df.columns:
        return pd.DataFrame()

    grouped = (
        quality_df.groupby(group_column, dropna=False)
        .agg(
            total_observations=("signal_id", "count"),
            resolved_observations=("is_closed", "sum"),
            open_observations=("is_open", "sum"),
            error_observations=("is_error", "sum"),
            wins=("is_win", "sum"),
            losses=("is_loss", "sum"),
            avg_result_r=("result_r", "mean"),
            avg_mfe_r=("mfe_r", "mean"),
            avg_mae_r=("mae_r", "mean"),
        )
        .reset_index()
    )

    numeric_columns = [
        "avg_result_r",
        "avg_mfe_r",
        "avg_mae_r",
    ]

    for column in numeric_columns:
        grouped[column] = grouped[column].round(6)

    return grouped.sort_values(
        by=["resolved_observations", "avg_result_r"],
        ascending=[False, False],
    ).reset_index(drop=True)


def build_quality_gate_summary(
    quality_df: pd.DataFrame,
    checks_df: pd.DataFrame,
    config: ForwardDatasetQualityGateConfig,
) -> pd.DataFrame:
    total_rows = len(quality_df)
    resolved_rows = int(quality_df["is_closed"].sum()) if not quality_df.empty else 0
    open_rows = int(quality_df["is_open"].sum()) if not quality_df.empty else 0
    error_rows = int(quality_df["is_error"].sum()) if not quality_df.empty else 0
    wins = int(quality_df["is_win"].sum()) if not quality_df.empty else 0
    losses = int(quality_df["is_loss"].sum()) if not quality_df.empty else 0

    open_ratio = round(open_rows / total_rows, 6) if total_rows > 0 else 0.0

    error_checks_failed = checks_df[
        (checks_df["severity"].isin(["ERROR", "BLOCKER"]))
        & (~checks_df["passed"])
    ]

    warning_checks_failed = checks_df[
        (checks_df["severity"] == "WARNING")
        & (~checks_df["passed"])
    ]

    preferred_sample_reached = resolved_rows >= config.preferred_resolved_observations
    minimum_sample_reached = resolved_rows >= config.min_resolved_observations

    if total_rows == 0:
        dataset_quality_decision = "DATASET_NOT_READY"
    elif not error_checks_failed.empty:
        if not minimum_sample_reached:
            dataset_quality_decision = "DATASET_NOT_READY"
        else:
            dataset_quality_decision = "DATASET_REVIEW_REQUIRED"
    elif not minimum_sample_reached:
        dataset_quality_decision = "DATASET_NOT_READY"
    elif not warning_checks_failed.empty:
        dataset_quality_decision = "DATASET_REVIEW_REQUIRED"
    elif preferred_sample_reached:
        dataset_quality_decision = "DATASET_PREFERRED_READY"
    else:
        dataset_quality_decision = "DATASET_MINIMUM_READY"

    avg_result_r = 0.0
    win_rate = 0.0

    closed_df = quality_df[quality_df["is_closed"]].copy() if not quality_df.empty else pd.DataFrame()

    if not closed_df.empty:
        avg_result_r = round(float(closed_df["result_r"].mean()), 6)
        win_rate = round(float((closed_df["result_r"] > 0).mean()), 6)

    return pd.DataFrame(
        [
            {
                "total_observations": total_rows,
                "resolved_observations": resolved_rows,
                "open_observations": open_rows,
                "error_observations": error_rows,
                "wins": wins,
                "losses": losses,
                "win_rate": win_rate,
                "avg_result_r": avg_result_r,
                "open_ratio": open_ratio,
                "min_resolved_observations": config.min_resolved_observations,
                "preferred_resolved_observations": config.preferred_resolved_observations,
                "minimum_sample_reached": minimum_sample_reached,
                "preferred_sample_reached": preferred_sample_reached,
                "failed_error_or_blocker_checks": len(error_checks_failed),
                "failed_warning_checks": len(warning_checks_failed),
                "ready_for_phase_4_2_metrics": dataset_quality_decision
                in {"DATASET_MINIMUM_READY", "DATASET_PREFERRED_READY"},
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "dataset_quality_decision": dataset_quality_decision,
            }
        ]
    )


def run_forward_dataset_quality_gate(
    dataset_df: pd.DataFrame,
    config: ForwardDatasetQualityGateConfig | None = None,
) -> tuple[
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
        config = ForwardDatasetQualityGateConfig()

    required_columns_df = validate_required_columns(dataset_df)
    quality_df = ensure_quality_columns(dataset_df)

    size_checks_df = validate_dataset_size(quality_df, config)
    signal_id_checks_df, duplicate_signal_ids_df = validate_signal_ids(
        quality_df=quality_df,
        config=config,
    )
    numeric_checks_df = validate_numeric_integrity(quality_df)
    resolution_checks_df, error_rows_df = validate_resolution_integrity(
        quality_df=quality_df,
        config=config,
    )
    distribution_checks_df = validate_distribution(
        quality_df=quality_df,
        config=config,
    )

    checks_df = pd.concat(
        [
            required_columns_df,
            size_checks_df,
            signal_id_checks_df,
            numeric_checks_df,
            resolution_checks_df,
            distribution_checks_df,
        ],
        ignore_index=True,
    )

    summary_df = build_quality_gate_summary(
        quality_df=quality_df,
        checks_df=checks_df,
        config=config,
    )

    by_context_df = build_distribution_df(quality_df, "context_name")
    by_cost_profile_df = build_distribution_df(quality_df, "cost_profile")
    by_direction_df = build_distribution_df(quality_df, "direction")
    by_resolution_status_df = build_distribution_df(quality_df, "resolution_status")

    return (
        summary_df,
        checks_df,
        quality_df,
        by_context_df,
        by_cost_profile_df,
        by_direction_df,
        by_resolution_status_df,
        duplicate_signal_ids_df,
        error_rows_df,
    )