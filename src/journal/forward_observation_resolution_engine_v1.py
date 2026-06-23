from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class ForwardObservationResolutionConfig:
    timestamp_column: str = "timestamp"
    same_bar_policy: str = "CONSERVATIVE_STOP"
    max_bars_after_observation: int = 96
    unresolved_status: str = "OPEN_UNRESOLVED"
    no_future_data_status: str = "OPEN_NO_FUTURE_DATA"
    paper_trade_execution_allowed: bool = False
    real_capital_allowed: bool = False


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


def parse_timestamp(value: Any) -> pd.Timestamp | None:
    timestamp = pd.to_datetime(value, errors="coerce")

    if pd.isna(timestamp):
        return None

    return timestamp


def validate_ohlc_df(
    ohlc_df: pd.DataFrame,
    config: ForwardObservationResolutionConfig,
) -> pd.DataFrame:
    required_columns = [
        config.timestamp_column,
        "open",
        "high",
        "low",
        "close",
    ]

    rows = []

    for column in required_columns:
        rows.append(
            {
                "check_name": f"required_column:{column}",
                "passed": column in ohlc_df.columns,
                "details": "OK" if column in ohlc_df.columns else "MISSING",
            }
        )

    rows.append(
        {
            "check_name": "has_rows",
            "passed": len(ohlc_df) > 0,
            "details": f"rows={len(ohlc_df)}",
        }
    )

    return pd.DataFrame(rows)


def normalize_ohlc_df(
    ohlc_df: pd.DataFrame,
    config: ForwardObservationResolutionConfig,
) -> pd.DataFrame:
    normalized = ohlc_df.copy()

    normalized[config.timestamp_column] = pd.to_datetime(
        normalized[config.timestamp_column],
        errors="coerce",
    )

    normalized = normalized.dropna(subset=[config.timestamp_column])
    normalized = normalized.sort_values(config.timestamp_column).reset_index(drop=True)

    for column in ["open", "high", "low", "close"]:
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")

    normalized = normalized.dropna(subset=["open", "high", "low", "close"])
    normalized = normalized.reset_index(drop=True)

    return normalized


def calculate_risk_unit(direction: str, entry: float, stop: float) -> float:
    if direction == "SHORT":
        return stop - entry

    if direction == "LONG":
        return entry - stop

    return 0.0


def calculate_default_target(
    direction: str,
    entry: float,
    stop: float,
    risk_reward: float,
) -> float:
    risk_unit = calculate_risk_unit(direction, entry, stop)

    if risk_unit <= 0:
        return 0.0

    if direction == "SHORT":
        return entry - (risk_unit * risk_reward)

    if direction == "LONG":
        return entry + (risk_unit * risk_reward)

    return 0.0


def calculate_mfe_mae_r(
    direction: str,
    entry: float,
    risk_unit: float,
    bars_df: pd.DataFrame,
) -> tuple[float, float]:
    if bars_df.empty or risk_unit <= 0:
        return 0.0, 0.0

    if direction == "SHORT":
        mfe_r = ((entry - bars_df["low"]) / risk_unit).max()
        mae_r = ((entry - bars_df["high"]) / risk_unit).min()
        return round(float(mfe_r), 6), round(float(mae_r), 6)

    if direction == "LONG":
        mfe_r = ((bars_df["high"] - entry) / risk_unit).max()
        mae_r = ((bars_df["low"] - entry) / risk_unit).min()
        return round(float(mfe_r), 6), round(float(mae_r), 6)

    return 0.0, 0.0


def resolve_same_bar_conflict(
    direction: str,
    entry: float,
    stop: float,
    target: float,
    risk_unit: float,
    bar: pd.Series,
    config: ForwardObservationResolutionConfig,
) -> tuple[str, float, float]:
    if config.same_bar_policy == "CONSERVATIVE_STOP":
        return "AMBIGUOUS_BOTH_HIT_CONSERVATIVE_STOP", -1.0, stop

    if config.same_bar_policy == "CONSERVATIVE_ZERO":
        return "AMBIGUOUS_BOTH_HIT_ZERO_R", 0.0, entry

    if config.same_bar_policy == "TARGET_FIRST":
        return "AMBIGUOUS_BOTH_HIT_TARGET_FIRST", abs((entry - target) / risk_unit), target

    return "AMBIGUOUS_BOTH_HIT_REVIEW_REQUIRED", 0.0, safe_float(bar.get("close"), entry)


def resolve_single_observation(
    observation: pd.Series,
    ohlc_df: pd.DataFrame,
    config: ForwardObservationResolutionConfig,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    observed_at = parse_timestamp(observation.get("observed_at"))
    direction = safe_upper(observation.get("direction"))
    entry = safe_float(observation.get("entry_theoretical"))
    stop = safe_float(observation.get("stop_theoretical"))
    risk_reward = safe_float(observation.get("risk_reward"), 2.5)
    target = safe_float(observation.get("target_theoretical"))

    if target <= 0:
        target = calculate_default_target(
            direction=direction,
            entry=entry,
            stop=stop,
            risk_reward=risk_reward,
        )

    invalidation_level = safe_float(observation.get("invalidation_level"), 0.0)
    signal_id = safe_str(observation.get("signal_id"))

    base_result = observation.to_dict()

    if observed_at is None:
        error = {
            "severity": "ERROR",
            "signal_id": signal_id,
            "check_name": "observed_at",
            "details": "Invalid observed_at",
        }
        base_result.update(
            {
                "resolution_status": "RESOLUTION_ERROR_INVALID_OBSERVED_AT",
                "resolved_at": "",
                "result_r": 0.0,
                "mfe_r": 0.0,
                "mae_r": 0.0,
                "bars_to_resolution": 0,
                "resolution_price": 0.0,
                "resolution_reason": "Invalid observed_at",
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
            }
        )
        return base_result, error

    risk_unit = calculate_risk_unit(direction, entry, stop)

    if risk_unit <= 0:
        error = {
            "severity": "ERROR",
            "signal_id": signal_id,
            "check_name": "risk_unit",
            "details": f"Invalid risk unit for direction={direction}, entry={entry}, stop={stop}",
        }
        base_result.update(
            {
                "resolution_status": "RESOLUTION_ERROR_INVALID_RISK_UNIT",
                "resolved_at": "",
                "result_r": 0.0,
                "mfe_r": 0.0,
                "mae_r": 0.0,
                "bars_to_resolution": 0,
                "resolution_price": 0.0,
                "resolution_reason": "Invalid risk unit",
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
            }
        )
        return base_result, error

    future_bars = ohlc_df[
        ohlc_df[config.timestamp_column] > observed_at
    ].head(config.max_bars_after_observation)

    if future_bars.empty:
        base_result.update(
            {
                "resolution_status": config.no_future_data_status,
                "resolved_at": "",
                "result_r": 0.0,
                "mfe_r": 0.0,
                "mae_r": 0.0,
                "bars_to_resolution": 0,
                "resolution_price": 0.0,
                "resolution_reason": "No future OHLC data available",
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
            }
        )
        return base_result, None

    resolution_status = config.unresolved_status
    resolved_at = ""
    result_r = 0.0
    resolution_price = 0.0
    resolution_reason = "No target, stop or invalidation touched within max bars"
    bars_to_resolution = 0
    bars_used = future_bars.copy()

    for bar_number, (_, bar) in enumerate(future_bars.iterrows(), start=1):
        high = safe_float(bar.get("high"))
        low = safe_float(bar.get("low"))
        close = safe_float(bar.get("close"))
        bar_timestamp = bar[config.timestamp_column]

        target_hit = False
        stop_hit = False
        invalidation_hit = False

        if direction == "SHORT":
            target_hit = low <= target
            stop_hit = high >= stop
            invalidation_hit = invalidation_level > 0 and high >= invalidation_level

        elif direction == "LONG":
            target_hit = high >= target
            stop_hit = low <= stop
            invalidation_hit = invalidation_level > 0 and low <= invalidation_level

        else:
            resolution_status = "RESOLUTION_ERROR_UNSUPPORTED_DIRECTION"
            resolution_reason = f"Unsupported direction={direction}"
            bars_to_resolution = bar_number
            resolved_at = str(bar_timestamp)
            resolution_price = close
            result_r = 0.0
            bars_used = future_bars.head(bar_number)
            break

        if target_hit and stop_hit:
            (
                resolution_status,
                result_r,
                resolution_price,
            ) = resolve_same_bar_conflict(
                direction=direction,
                entry=entry,
                stop=stop,
                target=target,
                risk_unit=risk_unit,
                bar=bar,
                config=config,
            )
            resolution_reason = "Target and stop touched inside same OHLC bar"
            bars_to_resolution = bar_number
            resolved_at = str(bar_timestamp)
            bars_used = future_bars.head(bar_number)
            break

        if stop_hit:
            resolution_status = "STOP_HIT"
            result_r = -1.0
            resolution_price = stop
            resolution_reason = "Stop touched"
            bars_to_resolution = bar_number
            resolved_at = str(bar_timestamp)
            bars_used = future_bars.head(bar_number)
            break

        if invalidation_hit:
            resolution_status = "INVALIDATION_HIT"
            if direction == "SHORT":
                result_r = round(float((entry - invalidation_level) / risk_unit), 6)
            else:
                result_r = round(float((invalidation_level - entry) / risk_unit), 6)

            resolution_price = invalidation_level
            resolution_reason = "Invalidation level touched"
            bars_to_resolution = bar_number
            resolved_at = str(bar_timestamp)
            bars_used = future_bars.head(bar_number)
            break

        if target_hit:
            resolution_status = "TARGET_HIT"
            if direction == "SHORT":
                result_r = round(float((entry - target) / risk_unit), 6)
            else:
                result_r = round(float((target - entry) / risk_unit), 6)

            resolution_price = target
            resolution_reason = "Target touched"
            bars_to_resolution = bar_number
            resolved_at = str(bar_timestamp)
            bars_used = future_bars.head(bar_number)
            break

    mfe_r, mae_r = calculate_mfe_mae_r(
        direction=direction,
        entry=entry,
        risk_unit=risk_unit,
        bars_df=bars_used,
    )

    base_result.update(
        {
            "resolution_status": resolution_status,
            "resolved_at": resolved_at,
            "result_r": result_r,
            "mfe_r": mfe_r,
            "mae_r": mae_r,
            "bars_to_resolution": bars_to_resolution,
            "resolution_price": resolution_price,
            "resolution_reason": resolution_reason,
            "paper_trade_execution_allowed": False,
            "real_capital_allowed": False,
        }
    )

    return base_result, None


def resolve_forward_observations(
    observations_df: pd.DataFrame,
    ohlc_df: pd.DataFrame,
    config: ForwardObservationResolutionConfig | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if config is None:
        config = ForwardObservationResolutionConfig()

    ohlc_validation_df = validate_ohlc_df(ohlc_df, config)

    if ohlc_validation_df["passed"].eq(False).any():
        summary_df = build_resolution_summary(
            resolved_df=pd.DataFrame(),
            open_df=pd.DataFrame(),
            errors_df=ohlc_validation_df[ohlc_validation_df["passed"].eq(False)].copy(),
            validation_passed=False,
        )
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), ohlc_validation_df, summary_df

    normalized_ohlc_df = normalize_ohlc_df(ohlc_df, config)

    resolved_rows = []
    errors = []

    for _, observation in observations_df.reset_index(drop=True).iterrows():
        resolved_row, error = resolve_single_observation(
            observation=observation,
            ohlc_df=normalized_ohlc_df,
            config=config,
        )

        resolved_rows.append(resolved_row)

        if error is not None:
            errors.append(error)

    resolved_df = pd.DataFrame(resolved_rows)

    if resolved_df.empty:
        open_df = pd.DataFrame()
        closed_df = pd.DataFrame()
    else:
        open_statuses = {
            config.unresolved_status,
            config.no_future_data_status,
        }

        open_df = resolved_df[
            resolved_df["resolution_status"].isin(open_statuses)
        ].copy()

        closed_df = resolved_df[
            ~resolved_df["resolution_status"].isin(open_statuses)
        ].copy()

    errors_df = pd.DataFrame(errors)

    summary_df = build_resolution_summary(
        resolved_df=closed_df,
        open_df=open_df,
        errors_df=errors_df,
        validation_passed=True,
    )

    return resolved_df, closed_df, open_df, errors_df, ohlc_validation_df, summary_df


def build_resolution_summary(
    resolved_df: pd.DataFrame,
    open_df: pd.DataFrame,
    errors_df: pd.DataFrame,
    validation_passed: bool,
) -> pd.DataFrame:
    resolved_count = len(resolved_df)
    open_count = len(open_df)
    error_count = len(errors_df)

    avg_result_r = 0.0
    win_rate = 0.0
    avg_mfe_r = 0.0
    avg_mae_r = 0.0

    if resolved_count > 0:
        avg_result_r = round(float(resolved_df["result_r"].mean()), 6)
        win_rate = round(float((resolved_df["result_r"] > 0).mean()), 6)
        avg_mfe_r = round(float(resolved_df["mfe_r"].mean()), 6)
        avg_mae_r = round(float(resolved_df["mae_r"].mean()), 6)

    if not validation_passed:
        decision = "RESOLUTION_INPUT_VALIDATION_FAILED"
    elif error_count > 0:
        decision = "RESOLUTION_COMPLETED_WITH_ERRORS"
    elif resolved_count > 0 and open_count == 0:
        decision = "RESOLUTION_COMPLETED_ALL_CLOSED"
    elif resolved_count > 0 and open_count > 0:
        decision = "RESOLUTION_COMPLETED_PARTIAL_OPEN"
    elif resolved_count == 0 and open_count > 0:
        decision = "RESOLUTION_COMPLETED_ALL_OPEN"
    else:
        decision = "RESOLUTION_NO_OBSERVATIONS"

    return pd.DataFrame(
        [
            {
                "validation_passed": validation_passed,
                "resolved_observations": resolved_count,
                "open_observations": open_count,
                "error_count": error_count,
                "avg_result_r": avg_result_r,
                "win_rate": win_rate,
                "avg_mfe_r": avg_mfe_r,
                "avg_mae_r": avg_mae_r,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "resolution_decision": decision,
            }
        ]
    )


def build_sample_resolution_ohlc_data() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "timestamp": "2026-06-21 05:15:00",
                "open": 65050.0,
                "high": 65300.0,
                "low": 64500.0,
                "close": 64750.0,
            },
            {
                "timestamp": "2026-06-21 05:30:00",
                "open": 64750.0,
                "high": 65400.0,
                "low": 63750.0,
                "close": 63900.0,
            },
            {
                "timestamp": "2026-06-21 06:15:00",
                "open": 65100.0,
                "high": 65600.0,
                "low": 64600.0,
                "close": 65400.0,
            },
            {
                "timestamp": "2026-06-21 06:30:00",
                "open": 65400.0,
                "high": 66050.0,
                "low": 64800.0,
                "close": 65950.0,
            },
        ]
    )