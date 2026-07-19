from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd

from src.execution.cost_aware_filter_v1 import build_cost_profiles
from src.exits.active_exit_manager_v1 import add_active_exit_features
from src.long_side.long_candidate_discovery_baseline_v1 import EXPECTED_CANDIDATES
from src.long_side.long_historical_baseline_backtest_v1 import (
    LOOKAHEAD_BARS,
    RR_TARGET,
    add_indicators as add_long_indicators,
    build_candidate_metrics,
    candidate_signal_indexes,
    find_historical_data_path,
    normalize_ohlc_df,
    run_historical_backtest,
)
from src.validation.closed_candle_mtf_revalidation_v1 import (
    MODE_CORRECTED,
    OFFICIAL_BACKUP_PATH,
    OFFICIAL_DATASET_PATH,
    OFFICIAL_LOCK_PATH,
    OFFICIAL_MANIFEST_PATH,
    OFFICIAL_TEMP_PATH,
    SYMBOLS,
    aggregate_short_metrics,
    build_combined_context_dataset,
    build_short_config,
    build_walk_forward_splits,
    dataset_path,
    prepare_dataset_manifest,
    short_mtf_with_directional_context_v3_1,
    slice_by_date,
)
from src.validation.walk_forward_engine_v1 import (
    build_fixed_rr_exit_profile,
    build_walk_forward_candidates,
    run_candidate_backtest,
)


PHASE = "10.42R.2A"
REPORTS_DIR = Path(
    "reports/phase_10_42r_2a_signal_to_fill_timing_integrity_audit_v1"
)
R2_REPORTS_DIR = Path(
    "reports/phase_10_42r_2_short_long_closed_candle_mtf_revalidation_v1"
)

FILL_SAME_CLOSE = "SAME_CANDLE_CLOSE_DIAGNOSTIC_ONLY"
FILL_NEXT_OPEN = "NEXT_BAR_OPEN_CORRECTED"

SHORT_CANDIDATE = "TARGET_SHORT_FIB_V5_MTF_V3_1 + FIXED_RR_2_5"
LONG_PRIMARY = "LONG_BASE_FAILED_BREAKDOWN_V1"
LONG_SECONDARY = "LONG_BASE_LIQUIDITY_SWEEP_V1"

R2_REQUIRED_REPORTS = {
    "summary": R2_REPORTS_DIR / "summary_v1.csv",
    "checks": R2_REPORTS_DIR / "checks_v1.csv",
    "dataset_manifest": R2_REPORTS_DIR / "dataset_manifest_v1.csv",
    "short_window_metrics": R2_REPORTS_DIR / "short_window_metrics_v1.csv",
    "long_readiness": R2_REPORTS_DIR / "long_readiness_revalidation_v1.csv",
}

LONG_STAGE_REQUIRED_REPORTS = {
    "phase_8_4_historical_metrics": Path(
        "reports/phase_8_4_long_historical_baseline_backtest_v1/"
        "long_historical_backtest_metrics_v1.csv"
    ),
    "phase_8_10_monte_carlo_summary": Path(
        "reports/phase_8_10_long_monte_carlo_baseline_validation_v1/"
        "long_monte_carlo_candidate_summary_v1.csv"
    ),
}

LONG_STAGE_REQUIRED_COLUMNS = {
    "phase_8_4_historical_metrics": {
        "candidate_id",
        "trades",
        "total_result_r",
        "average_result_r",
        "profit_factor",
        "max_drawdown_r",
    },
    "phase_8_10_monte_carlo_summary": {
        "candidate_id",
        "source_trade_count",
        "original_total_result_r",
    },
}

SAFETY_FLAGS = {
    "signal_generation_enabled": False,
    "forward_observation_allowed": False,
    "official_dataset_write_allowed": False,
    "evidence_persistence_allowed": False,
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "live_alerts_allowed": False,
    "market_execution_allowed": False,
    "exchange_execution_allowed": False,
    "automation_allowed": False,
    "execution_allowed": False,
    "openclaw_operational_integration_allowed": False,
}


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def config_value(config: Any, key: str, default: Any) -> Any:
    if isinstance(config, dict):
        return config.get(key, default)
    return getattr(config, key, default)


def file_sha256(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_check(
    check_name: str,
    passed: bool,
    severity: str,
    details: str,
) -> dict[str, Any]:
    return {
        "check_name": check_name,
        "passed": bool(passed),
        "severity": severity,
        "details": details,
        "blocker": severity == "ERROR" and not bool(passed),
    }


def official_forward_artifacts_absent() -> bool:
    return not any(
        path.exists()
        for path in (
            OFFICIAL_DATASET_PATH,
            OFFICIAL_TEMP_PATH,
            OFFICIAL_LOCK_PATH,
            OFFICIAL_MANIFEST_PATH,
            OFFICIAL_BACKUP_PATH,
        )
    )


def write_outputs(outputs: dict[str, pd.DataFrame]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    for name, frame in outputs.items():
        frame.to_csv(REPORTS_DIR / f"{name}_v1.csv", index=False)


def load_r2_reports() -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    frames: dict[str, pd.DataFrame] = {}
    rows: list[dict[str, Any]] = []
    for name, path in R2_REQUIRED_REPORTS.items():
        exists = path.exists() and path.is_file()
        frame = pd.DataFrame()
        error = ""
        if exists:
            try:
                frame = pd.read_csv(path)
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
        frames[name] = frame
        rows.append(
            {
                "report_name": name,
                "path": str(path),
                "exists": exists,
                "size_bytes": path.stat().st_size if exists else 0,
                "sha256": file_sha256(path),
                "rows": len(frame),
                "read_error": error,
                "report_valid": exists and not frame.empty and not error,
            }
        )
    return frames, pd.DataFrame(rows)


def load_long_stage_reports() -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    """Load the two distinct LONG source stages without collapsing lineage."""
    frames: dict[str, pd.DataFrame] = {}
    rows: list[dict[str, Any]] = []
    for name, path in LONG_STAGE_REQUIRED_REPORTS.items():
        exists = path.exists() and path.is_file()
        frame = pd.DataFrame()
        error = ""
        if exists:
            try:
                frame = pd.read_csv(path)
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
        required_columns = LONG_STAGE_REQUIRED_COLUMNS[name]
        missing_columns = sorted(required_columns - set(frame.columns))
        candidate_ids = (
            set(frame["candidate_id"].astype(str))
            if "candidate_id" in frame.columns
            else set()
        )
        required_candidates = (
            set(EXPECTED_CANDIDATES)
            if name == "phase_8_4_historical_metrics"
            else {LONG_PRIMARY, LONG_SECONDARY}
        )
        missing_candidates = sorted(required_candidates - candidate_ids)
        report_valid = bool(
            exists
            and not frame.empty
            and not error
            and not missing_columns
            and not missing_candidates
        )
        frames[name] = frame
        rows.append(
            {
                "report_name": name,
                "source_stage": (
                    "PHASE_8_4_FULL_HISTORICAL_BASELINE"
                    if name == "phase_8_4_historical_metrics"
                    else "PHASE_8_10_POST_OOS_STRESS_COST_MONTE_CARLO_SOURCE"
                ),
                "path": str(path),
                "exists": exists,
                "size_bytes": path.stat().st_size if exists else 0,
                "sha256": file_sha256(path),
                "rows": len(frame),
                "read_error": error,
                "missing_columns": "|".join(missing_columns),
                "missing_candidates": "|".join(missing_candidates),
                "report_valid": report_valid,
            }
        )
    return frames, pd.DataFrame(rows)


def build_dataset_lineage(
    current_manifest: pd.DataFrame,
    r2_manifest: pd.DataFrame,
) -> pd.DataFrame:
    if current_manifest.empty or r2_manifest.empty:
        return pd.DataFrame()
    current = current_manifest.copy()
    r2 = r2_manifest.copy()
    lineage = current.merge(
        r2[["symbol", "timeframe", "sha256", "rows"]],
        on=["symbol", "timeframe"],
        suffixes=("_current", "_r2"),
        how="outer",
        validate="one_to_one",
    )
    lineage["hash_matches_r2"] = lineage["sha256_current"].eq(
        lineage["sha256_r2"]
    )
    lineage["row_count_matches_r2"] = lineage["rows_current"].eq(
        lineage["rows_r2"]
    )
    return lineage


def _profit_factor(results: pd.Series) -> float | None:
    numeric = pd.to_numeric(results, errors="coerce").fillna(0.0)
    gross_profit = float(numeric[numeric > 0].sum())
    gross_loss = abs(float(numeric[numeric <= 0].sum()))
    if gross_loss == 0:
        return None if gross_profit > 0 else 0.0
    return gross_profit / gross_loss


def _max_drawdown(returns: pd.Series) -> float:
    equity = 1.0
    peak = 1.0
    worst = 0.0
    for value in pd.to_numeric(returns, errors="coerce").fillna(0.0):
        equity *= 1.0 + float(value)
        peak = max(peak, equity)
        worst = min(worst, equity / peak - 1.0)
    return worst


def summarize_short_trades(
    trades: pd.DataFrame,
    initial_capital: float,
    ending_capital: float,
) -> dict[str, Any]:
    if trades.empty:
        return {
            "total_return_pct": 0.0,
            "total_trades": 0,
            "win_rate": 0.0,
            "profit_factor": None,
            "expectancy_r": 0.0,
            "max_drawdown_pct": 0.0,
        }
    returns = pd.to_numeric(trades["return_pct"], errors="coerce").fillna(0.0)
    results = pd.to_numeric(trades["result_r"], errors="coerce").fillna(0.0)
    return {
        "total_return_pct": ending_capital / initial_capital - 1.0,
        "total_trades": len(trades),
        "win_rate": float((results > 0).mean()),
        "profit_factor": _profit_factor(pd.to_numeric(trades["net_pnl"])),
        "expectancy_r": float(results.mean()),
        "max_drawdown_pct": _max_drawdown(returns),
    }


def simulate_short_trade_next_open(
    df: pd.DataFrame,
    signal_index: int,
    capital: float,
    config: Any,
    exit_profile: dict[str, Any],
) -> dict[str, Any] | None:
    entry_index = signal_index + 1
    if signal_index < 0 or entry_index >= len(df):
        return None

    signal_row = df.iloc[signal_index]
    entry_row = df.iloc[entry_index]
    raw_entry_open = safe_float(entry_row.get("open"), 0.0)
    signal_close = safe_float(signal_row.get("close"), 0.0)
    signal_atr = safe_float(signal_row.get("aev1_atr14"), 0.0)
    if raw_entry_open <= 0 or signal_atr <= 0:
        return None

    risk_per_trade = safe_float(config_value(config, "risk_per_trade", 0.01), 0.01)
    atr_multiplier = safe_float(config_value(config, "atr_multiplier", 1.25), 1.25)
    max_holding_bars = int(config_value(config, "max_holding_bars", 48))
    fee_rate = safe_float(config_value(config, "fee_rate", 0.001), 0.001)
    spread_rate = safe_float(config_value(config, "spread_rate", 0.0002), 0.0002)
    risk_reward = safe_float(
        exit_profile.get("risk_reward"),
        safe_float(config_value(config, "risk_reward", 2.5), 2.5),
    )

    entry_price = raw_entry_open * (1.0 - spread_rate / 2.0)
    stop_price = entry_price + signal_atr * atr_multiplier
    risk_distance = stop_price - entry_price
    if risk_distance <= 0:
        return None
    target_price = entry_price - risk_distance * risk_reward
    risk_amount = capital * risk_per_trade
    if risk_amount <= 0:
        return None
    position_units = risk_amount / risk_distance
    entry_fee = abs(entry_price * position_units) * fee_rate

    end_index = min(
        len(df) - 1,
        entry_index + max(1, max_holding_bars) - 1,
    )
    exit_index: int | None = None
    raw_exit_reference: float | None = None
    final_exit_price: float | None = None
    exit_reason = ""
    max_favorable_r = 0.0
    max_adverse_r = 0.0

    for bar_index in range(entry_index, end_index + 1):
        row = df.iloc[bar_index]
        high = safe_float(row.get("high"), 0.0)
        low = safe_float(row.get("low"), 0.0)
        close = safe_float(row.get("close"), entry_price)
        max_favorable_r = max(
            max_favorable_r,
            (entry_price - low) / risk_distance,
        )
        max_adverse_r = max(
            max_adverse_r,
            (high - entry_price) / risk_distance,
        )

        stop_hit = high >= stop_price
        target_hit = low <= target_price
        if stop_hit:
            exit_index = bar_index
            raw_exit_reference = stop_price
            final_exit_price = stop_price * (1.0 + spread_rate / 2.0)
            exit_reason = "STOP_LOSS"
            break
        if target_hit:
            exit_index = bar_index
            raw_exit_reference = target_price
            final_exit_price = target_price * (1.0 + spread_rate / 2.0)
            exit_reason = "TAKE_PROFIT"
            break
        if bar_index == end_index:
            exit_index = bar_index
            raw_exit_reference = close
            final_exit_price = close * (1.0 + spread_rate / 2.0)
            exit_reason = "MAX_HOLDING"

    if exit_index is None or final_exit_price is None:
        return None

    gross_pnl = (entry_price - final_exit_price) * position_units
    exit_fee = abs(final_exit_price * position_units) * fee_rate
    fees = entry_fee + exit_fee
    net_pnl = gross_pnl - fees
    result_r = net_pnl / risk_amount
    return_pct = net_pnl / capital

    return {
        "signal_index": signal_index,
        "entry_index": entry_index,
        "exit_index": exit_index,
        "signal_time": signal_row.get("timestamp"),
        "entry_time": entry_row.get("timestamp"),
        "exit_time": df.iloc[exit_index].get("timestamp"),
        "fill_mode": FILL_NEXT_OPEN,
        "direction": "SHORT",
        "signal_close": signal_close,
        "raw_entry_reference": raw_entry_open,
        "entry_price": entry_price,
        "gap_from_signal_close": raw_entry_open / signal_close - 1.0,
        "signal_atr": signal_atr,
        "stop_loss_initial": stop_price,
        "take_profit_initial": target_price,
        "raw_exit_reference": raw_exit_reference,
        "exit_price": final_exit_price,
        "exit_reason": exit_reason,
        "risk_amount": risk_amount,
        "risk_distance": risk_distance,
        "position_units": position_units,
        "gross_pnl": gross_pnl,
        "fees": fees,
        "net_pnl": net_pnl,
        "result_r": result_r,
        "return_pct": return_pct,
        "max_favorable_r": max_favorable_r,
        "max_adverse_r": max_adverse_r,
        "bars_held": exit_index - entry_index + 1,
    }


def run_short_next_open_backtest(
    df: pd.DataFrame,
    strategy_func: Callable,
    config: Any,
    exit_profile: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    market = add_active_exit_features(df)
    initial_capital = safe_float(config_value(config, "initial_capital", 1000.0), 1000.0)
    capital = initial_capital
    trades: list[dict[str, Any]] = []
    index = 250
    while index < len(market) - 2:
        signal = strategy_func(market, index, config)
        if signal == "SHORT":
            trade = simulate_short_trade_next_open(
                market,
                signal_index=index,
                capital=capital,
                config=config,
                exit_profile=exit_profile,
            )
            if trade is not None:
                capital += float(trade["net_pnl"])
                trades.append(trade)
                index = int(trade["exit_index"]) + 1
                continue
        index += 1
    frame = pd.DataFrame(trades)
    return frame, summarize_short_trades(frame, initial_capital, capital)


def _official_short_candidate() -> dict[str, Any]:
    candidates = [
        candidate
        for candidate in build_walk_forward_candidates()
        if bool(candidate.get("is_official"))
    ]
    if len(candidates) != 1:
        raise ValueError("Expected exactly one official fixed SHORT candidate.")
    return candidates[0]


def _metric_row(
    symbol: str,
    fill_mode: str,
    split: dict[str, str],
    summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "symbol": symbol,
        "timing_mode": fill_mode,
        "source_mtf_mode": MODE_CORRECTED,
        "split_name": split["split_name"],
        "test_start": split["test_start"],
        "test_end": split["test_end"],
        "test_trades": int(summary.get("total_trades", 0)),
        "test_return": safe_float(summary.get("total_return_pct"), 0.0),
        "test_profit_factor": summary.get("profit_factor"),
        "test_expectancy_r": safe_float(summary.get("expectancy_r"), 0.0),
        "test_drawdown": safe_float(summary.get("max_drawdown_pct"), 0.0),
        "test_win_rate": safe_float(summary.get("win_rate"), 0.0),
    }


def run_short_timing_audit() -> tuple[pd.DataFrame, pd.DataFrame]:
    candidate = _official_short_candidate()
    config = build_short_config()
    exit_profile = build_fixed_rr_exit_profile(
        candidate["risk_reward"],
        candidate["candidate_name"],
    )
    metric_rows: list[dict[str, Any]] = []
    trade_frames: list[pd.DataFrame] = []

    for symbol in SYMBOLS:
        market = build_combined_context_dataset(
            dataset_path(symbol, "15m"),
            dataset_path(symbol, "1h"),
            dataset_path(symbol, "4h"),
            MODE_CORRECTED,
        )
        for split in build_walk_forward_splits():
            test = slice_by_date(market, split["test_start"], split["test_end"])
            same_trades, same_summary = run_candidate_backtest(
                df=test,
                strategy_func=short_mtf_with_directional_context_v3_1,
                base_config=config,
                candidate=candidate,
            )
            same_trades = same_trades.copy()
            if not same_trades.empty:
                same_trades["signal_index"] = same_trades["entry_index"]
                same_trades["signal_time"] = same_trades["entry_time"]
                same_trades["fill_mode"] = FILL_SAME_CLOSE
                same_trades["signal_close"] = same_trades["entry_index"].map(
                    test["close"]
                )
                same_trades["raw_entry_reference"] = same_trades["signal_close"]
                same_trades["gap_from_signal_close"] = 0.0
                same_trades["return_pct"] = (
                    same_trades["net_pnl"]
                    / same_trades["risk_amount"].div(config.risk_per_trade)
                )

            next_trades, next_summary = run_short_next_open_backtest(
                test,
                short_mtf_with_directional_context_v3_1,
                config,
                exit_profile,
            )
            metric_rows.extend(
                [
                    _metric_row(symbol, FILL_SAME_CLOSE, split, same_summary),
                    _metric_row(symbol, FILL_NEXT_OPEN, split, next_summary),
                ]
            )
            for fill_mode, trades in (
                (FILL_SAME_CLOSE, same_trades),
                (FILL_NEXT_OPEN, next_trades),
            ):
                if trades.empty:
                    continue
                frame = trades.copy()
                frame["symbol"] = symbol
                frame["split_name"] = split["split_name"]
                frame["test_start"] = split["test_start"]
                frame["test_end"] = split["test_end"]
                frame["fill_mode"] = fill_mode
                trade_frames.append(frame)

    metrics = pd.DataFrame(metric_rows)
    trades = (
        pd.concat(trade_frames, ignore_index=True, sort=False)
        if trade_frames
        else pd.DataFrame()
    )
    return metrics, trades


def compare_short_to_r2(
    timing_metrics: pd.DataFrame,
    r2_windows: pd.DataFrame,
) -> pd.DataFrame:
    same = timing_metrics[timing_metrics["timing_mode"].eq(FILL_SAME_CLOSE)].copy()
    r2 = r2_windows[r2_windows["timing_mode"].eq(MODE_CORRECTED)].copy()
    keys = ["symbol", "split_name", "test_start", "test_end"]
    comparison = same.merge(
        r2,
        on=keys,
        how="outer",
        suffixes=("_rerun", "_r2"),
        indicator=True,
        validate="one_to_one",
    )
    comparison["trade_count_matches"] = comparison["test_trades_rerun"].eq(
        comparison["test_trades_r2"]
    )
    for field in (
        "test_return",
        "test_profit_factor",
        "test_expectancy_r",
        "test_drawdown",
        "test_win_rate",
    ):
        left = pd.to_numeric(comparison[f"{field}_rerun"], errors="coerce")
        right = pd.to_numeric(comparison[f"{field}_r2"], errors="coerce")
        comparison[f"{field}_matches"] = np.isclose(
            left,
            right,
            rtol=1e-10,
            atol=1e-12,
            equal_nan=True,
        )
    metric_match_columns = [
        column for column in comparison.columns if column.endswith("_matches")
    ]
    comparison["all_metrics_match"] = (
        comparison["_merge"].eq("both")
        & comparison[metric_match_columns].astype(bool).all(axis=1)
    )
    return comparison


def build_short_trade_shift(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    keys = ["symbol", "split_name", "signal_time"]
    columns = keys + [
        "entry_time",
        "exit_time",
        "entry_price",
        "exit_price",
        "result_r",
        "net_pnl",
        "exit_reason",
    ]
    same = trades[trades["fill_mode"].eq(FILL_SAME_CLOSE)][columns].copy()
    corrected = trades[trades["fill_mode"].eq(FILL_NEXT_OPEN)][columns].copy()
    shift = same.merge(
        corrected,
        on=keys,
        how="outer",
        suffixes=("_same_close", "_next_open"),
        indicator=True,
    )
    shift["result_r_delta"] = (
        pd.to_numeric(shift["result_r_next_open"], errors="coerce")
        - pd.to_numeric(shift["result_r_same_close"], errors="coerce")
    )
    shift["entry_price_delta_pct"] = (
        pd.to_numeric(shift["entry_price_next_open"], errors="coerce")
        / pd.to_numeric(shift["entry_price_same_close"], errors="coerce")
        - 1.0
    )
    return shift


def _long_structural_stop_next_open(
    df: pd.DataFrame,
    signal_index: int,
    candidate_id: str,
    entry_price: float,
) -> float:
    row = df.iloc[signal_index]
    atr = max(safe_float(row.get("atr14"), 0.0), entry_price * 0.001)
    if candidate_id in {LONG_PRIMARY, LONG_SECONDARY}:
        structural_low = safe_float(row.get("low"), 0.0)
    elif candidate_id == "LONG_BASE_MTF_BULLISH_CONTINUATION_V1":
        start = max(0, signal_index - 5)
        structural_low = float(df.iloc[start : signal_index + 1]["low"].min())
    else:
        structural_low = min(
            safe_float(row.get("low"), entry_price),
            safe_float(row.get("rolling_low_20"), entry_price),
        )
    stop = min(structural_low - 0.05 * atr, entry_price - 0.50 * atr)
    if stop <= 0 or stop >= entry_price:
        stop = entry_price - 1.50 * atr
    return stop


def resolve_long_trade_next_open(
    df: pd.DataFrame,
    signal_index: int,
    candidate_id: str,
) -> dict[str, Any] | None:
    entry_index = signal_index + 1
    if entry_index >= len(df):
        return None
    signal_row = df.iloc[signal_index]
    entry_row = df.iloc[entry_index]
    signal_close = safe_float(signal_row.get("close"), 0.0)
    entry_price = safe_float(entry_row.get("open"), 0.0)
    if entry_price <= 0:
        return None
    stop_price = _long_structural_stop_next_open(
        df,
        signal_index,
        candidate_id,
        entry_price,
    )
    risk = entry_price - stop_price
    if risk <= 0:
        return None
    target_price = entry_price + risk * RR_TARGET
    future = df.iloc[entry_index : entry_index + LOOKAHEAD_BARS]
    max_high = entry_price
    min_low = entry_price
    status = "OPEN_TIMEOUT"
    result_r = 0.0
    bars_to_resolution = len(future)
    resolution_timestamp = ""
    exit_index = future.index[-1] if not future.empty else entry_index

    for offset, (bar_index, bar) in enumerate(future.iterrows(), start=1):
        high = safe_float(bar.get("high"), entry_price)
        low = safe_float(bar.get("low"), entry_price)
        max_high = max(max_high, high)
        min_low = min(min_low, low)
        if low <= stop_price:
            status = "STOP_HIT"
            result_r = -1.0
            bars_to_resolution = offset
            resolution_timestamp = str(bar.get("timestamp", ""))
            exit_index = int(bar_index)
            break
        if high >= target_price:
            status = "TARGET_HIT"
            result_r = RR_TARGET
            bars_to_resolution = offset
            resolution_timestamp = str(bar.get("timestamp", ""))
            exit_index = int(bar_index)
            break
    if status == "OPEN_TIMEOUT" and not future.empty:
        resolution_timestamp = str(future.iloc[-1].get("timestamp", ""))

    return {
        "candidate_id": candidate_id,
        "signal_index": signal_index,
        "entry_index": entry_index,
        "exit_index": exit_index,
        "observed_at": str(signal_row.get("timestamp", "")),
        "entry_time": str(entry_row.get("timestamp", "")),
        "resolution_timestamp": resolution_timestamp,
        "symbol": str(signal_row.get("symbol", "BTCUSDT")),
        "timeframe": str(signal_row.get("timeframe", "15m")),
        "direction": "LONG",
        "fill_mode": FILL_NEXT_OPEN,
        "router_decision": "WATCH_ONLY",
        "signal_close": signal_close,
        "entry_price": entry_price,
        "gap_from_signal_close": entry_price / signal_close - 1.0,
        "stop_price": stop_price,
        "target_price": target_price,
        "risk": risk,
        "reward": target_price - entry_price,
        "risk_reward": RR_TARGET,
        "valid_long_structure": stop_price < entry_price < target_price,
        "resolution_status": status,
        "result_r": result_r,
        "mfe_r": (max_high - entry_price) / risk,
        "mae_r": (min_low - entry_price) / risk,
        "bars_to_resolution": bars_to_resolution,
        "historical_status": "TIMING_AUDIT_ONLY",
        "approval_status": "NOT_APPROVED",
        "long_strategy_approved": False,
        "long_entries_approved": False,
        "execution_allowed": False,
    }


def run_long_timing_audit() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    path = find_historical_data_path()
    if path is None:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    raw = pd.read_csv(path)
    normalized, missing = normalize_ohlc_df(raw)
    if missing or normalized.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    market = add_long_indicators(normalized)
    same = run_historical_backtest(market).copy()
    if not same.empty:
        same["entry_index"] = same["signal_index"]
        same["entry_time"] = same["observed_at"]
        same["fill_mode"] = FILL_SAME_CLOSE
        same["signal_close"] = same["entry_price"]
        same["gap_from_signal_close"] = 0.0

    corrected_rows: list[dict[str, Any]] = []
    for candidate_id in EXPECTED_CANDIDATES:
        for signal_index in candidate_signal_indexes(market, candidate_id):
            trade = resolve_long_trade_next_open(
                market,
                signal_index,
                candidate_id,
            )
            if trade is not None:
                corrected_rows.append(trade)
    corrected = pd.DataFrame(corrected_rows)
    if corrected.empty:
        corrected = pd.DataFrame(
            columns=[
                "candidate_id",
                "signal_index",
                "entry_index",
                "observed_at",
                "entry_time",
                "resolution_timestamp",
                "fill_mode",
                "resolution_status",
                "result_r",
            ]
        )
    trades = pd.concat([same, corrected], ignore_index=True, sort=False)

    metric_frames: list[pd.DataFrame] = []
    for fill_mode, frame in ((FILL_SAME_CLOSE, same), (FILL_NEXT_OPEN, corrected)):
        metrics = build_candidate_metrics(frame)
        metrics.insert(0, "fill_mode", fill_mode)
        metric_frames.append(metrics)
    metrics = pd.concat(metric_frames, ignore_index=True)

    keys = ["candidate_id", "signal_index"]
    compare_columns = keys + [
        "entry_time",
        "entry_price",
        "stop_price",
        "target_price",
        "resolution_status",
        "result_r",
    ]
    shift = same[compare_columns].merge(
        corrected[compare_columns],
        on=keys,
        how="outer",
        suffixes=("_same_close", "_next_open"),
        indicator=True,
    )
    shift["entry_price_delta_pct"] = (
        pd.to_numeric(shift["entry_price_next_open"], errors="coerce")
        / pd.to_numeric(shift["entry_price_same_close"], errors="coerce")
        - 1.0
    )
    shift["result_r_delta"] = (
        pd.to_numeric(shift["result_r_next_open"], errors="coerce")
        - pd.to_numeric(shift["result_r_same_close"], errors="coerce")
    )
    return metrics, trades, shift


def compare_long_historical_to_phase_8_4(
    long_metrics: pd.DataFrame,
    phase_8_4_metrics: pd.DataFrame,
) -> pd.DataFrame:
    """Compare like-for-like full historical metrics with their Phase 8.4 source."""
    metric_columns = [
        "trades",
        "total_result_r",
        "average_result_r",
        "profit_factor",
        "max_drawdown_r",
    ]
    same = long_metrics[
        long_metrics["fill_mode"].eq(FILL_SAME_CLOSE)
        & long_metrics["candidate_id"].isin(EXPECTED_CANDIDATES)
    ][["candidate_id", *metric_columns]].copy()
    source = phase_8_4_metrics[
        phase_8_4_metrics["candidate_id"].isin(EXPECTED_CANDIDATES)
    ][["candidate_id", *metric_columns]].copy()
    same = same.rename(columns={name: f"current_{name}" for name in metric_columns})
    source = source.rename(columns={name: f"source_{name}" for name in metric_columns})
    comparison = same.merge(
        source,
        on="candidate_id",
        how="outer",
        validate="one_to_one",
        indicator=True,
    )
    comparison.insert(1, "current_stage", "PHASE_10_42R_2A_SAME_CLOSE_DIAGNOSTIC")
    comparison.insert(2, "source_stage", "PHASE_8_4_FULL_HISTORICAL_BASELINE")
    comparison["trade_count_matches"] = comparison["current_trades"].eq(
        comparison["source_trades"]
    )
    numeric_checks: list[str] = []
    for metric in metric_columns[1:]:
        check_name = f"{metric}_matches"
        comparison[check_name] = np.isclose(
            pd.to_numeric(comparison[f"current_{metric}"], errors="coerce"),
            pd.to_numeric(comparison[f"source_{metric}"], errors="coerce"),
            rtol=1e-10,
            atol=1e-12,
            equal_nan=True,
        )
        numeric_checks.append(check_name)
    comparison["all_metrics_match"] = comparison[
        ["trade_count_matches", *numeric_checks]
    ].all(axis=1) & comparison["_merge"].eq("both")
    return comparison


def compare_phase_8_10_to_r2_readiness(
    phase_8_10_summary: pd.DataFrame,
    r2_readiness: pd.DataFrame,
) -> pd.DataFrame:
    """Trace R2 readiness values to their actual post-stress Monte Carlo source."""
    candidates = [LONG_PRIMARY, LONG_SECONDARY]
    source = phase_8_10_summary[
        phase_8_10_summary["candidate_id"].isin(candidates)
    ][["candidate_id", "source_trade_count", "original_total_result_r"]].copy()
    r2 = r2_readiness[
        r2_readiness["candidate_id"].isin(candidates)
    ][["candidate_id", "source_trade_count", "original_total_result_r"]].copy()
    source = source.rename(
        columns={
            "source_trade_count": "phase_8_10_source_trade_count",
            "original_total_result_r": "phase_8_10_original_total_result_r",
        }
    )
    r2 = r2.rename(
        columns={
            "source_trade_count": "phase_10_42r_2_source_trade_count",
            "original_total_result_r": "phase_10_42r_2_original_total_result_r",
        }
    )
    comparison = source.merge(
        r2,
        on="candidate_id",
        how="outer",
        validate="one_to_one",
        indicator=True,
    )
    comparison.insert(
        1,
        "source_stage",
        "PHASE_8_10_POST_OOS_STRESS_COST_MONTE_CARLO_SOURCE",
    )
    comparison.insert(2, "consumer_stage", "PHASE_10_42R_2_LONG_READINESS_REVALIDATION")
    comparison["trade_count_matches"] = comparison[
        "phase_8_10_source_trade_count"
    ].eq(comparison["phase_10_42r_2_source_trade_count"])
    comparison["total_result_r_matches"] = np.isclose(
        pd.to_numeric(
            comparison["phase_8_10_original_total_result_r"], errors="coerce"
        ),
        pd.to_numeric(
            comparison["phase_10_42r_2_original_total_result_r"], errors="coerce"
        ),
        rtol=1e-10,
        atol=1e-12,
        equal_nan=True,
    )
    comparison["all_metrics_match"] = (
        comparison["trade_count_matches"]
        & comparison["total_result_r_matches"]
        & comparison["_merge"].eq("both")
    )
    return comparison


def long_timing_metrics_are_identical(long_metrics: pd.DataFrame) -> bool:
    """Compare aggregate timing metrics, independently of entry-price gaps."""
    metric_columns = [
        "trades",
        "total_result_r",
        "average_result_r",
        "profit_factor",
        "max_drawdown_r",
    ]
    required_columns = {"fill_mode", "candidate_id", *metric_columns}
    if long_metrics.empty or not required_columns.issubset(long_metrics.columns):
        return False
    same = long_metrics[
        long_metrics["fill_mode"].eq(FILL_SAME_CLOSE)
        & long_metrics["candidate_id"].isin(EXPECTED_CANDIDATES)
    ][["candidate_id", *metric_columns]].copy()
    corrected = long_metrics[
        long_metrics["fill_mode"].eq(FILL_NEXT_OPEN)
        & long_metrics["candidate_id"].isin(EXPECTED_CANDIDATES)
    ][["candidate_id", *metric_columns]].copy()
    comparison = same.merge(
        corrected,
        on="candidate_id",
        how="outer",
        suffixes=("_same_close", "_next_open"),
        validate="one_to_one",
        indicator=True,
    )
    if (
        len(comparison) != len(EXPECTED_CANDIDATES)
        or not comparison["_merge"].eq("both").all()
        or not comparison["trades_same_close"].eq(
            comparison["trades_next_open"]
        ).all()
    ):
        return False
    return bool(
        all(
            np.isclose(
                pd.to_numeric(
                    comparison[f"{metric}_same_close"], errors="coerce"
                ),
                pd.to_numeric(
                    comparison[f"{metric}_next_open"], errors="coerce"
                ),
                rtol=1e-10,
                atol=1e-12,
                equal_nan=True,
            ).all()
            for metric in metric_columns[1:]
        )
    )


def build_cost_accounting_audit() -> pd.DataFrame:
    config = build_short_config()
    internal_fee = 2.0 * safe_float(config_value(config, "fee_rate", 0.0))
    internal_spread = safe_float(config_value(config, "spread_rate", 0.0))
    rows: list[dict[str, Any]] = []
    for profile in build_cost_profiles():
        fee_overlap = min(internal_fee, profile.fee_pct_round_trip)
        spread_overlap = min(internal_spread, profile.spread_pct_round_trip)
        overlap = fee_overlap + spread_overlap
        unembedded_incremental = (
            max(0.0, profile.fee_pct_round_trip - internal_fee)
            + max(0.0, profile.spread_pct_round_trip - internal_spread)
            + profile.slippage_pct_round_trip
            + profile.funding_or_time_cost_pct
            + profile.safety_buffer_pct
        )
        rows.append(
            {
                "cost_profile": profile.name,
                "platform": profile.platform,
                "internal_result_basis": "NET_PNL_AFTER_INTERNAL_FEE_AND_SPREAD",
                "internal_fee_pct_round_trip": internal_fee,
                "internal_spread_pct_round_trip": internal_spread,
                "profile_fee_pct_round_trip": profile.fee_pct_round_trip,
                "profile_spread_pct_round_trip": profile.spread_pct_round_trip,
                "profile_slippage_pct_round_trip": profile.slippage_pct_round_trip,
                "profile_safety_buffer_pct": profile.safety_buffer_pct,
                "profile_total_cost_pct": profile.total_cost_pct,
                "overlapping_fee_pct": fee_overlap,
                "overlapping_spread_pct": spread_overlap,
                "overlapping_cost_pct": overlap,
                "unembedded_incremental_cost_pct": unembedded_incremental,
                "current_pipeline_subtracts_full_profile_from_net_result": True,
                "potential_cost_double_count_confirmed": overlap > 0,
                "normalized_cost_decision_allowed": False,
            }
        )
    return pd.DataFrame(rows)


def build_source_contract_audit() -> pd.DataFrame:
    rows = [
        {
            "scope": "SHORT",
            "source_path": "src/strategies/fib_v5_strategy.py",
            "signal_contract": "CURRENT_15M_HIGH_LOW_CLOSE_CONFIRM_SIGNAL",
            "legacy_fill_contract": "SAME_SIGNAL_CANDLE_CLOSE",
            "corrected_fill_contract": "NEXT_15M_CANDLE_OPEN",
        },
        {
            "scope": "SHORT",
            "source_path": "src/exits/active_exit_manager_v1.py",
            "signal_contract": "SIGNAL_EVALUATED_AT_INDEX_I",
            "legacy_fill_contract": "ENTRY_PRICE_FROM_CLOSE_AT_INDEX_I",
            "corrected_fill_contract": "ENTRY_PRICE_FROM_OPEN_AT_INDEX_I_PLUS_1",
        },
        {
            "scope": "LONG",
            "source_path": "src/long_side/long_historical_baseline_backtest_v1.py",
            "signal_contract": "CURRENT_15M_OHLC_CONFIRM_SIGNAL",
            "legacy_fill_contract": "ENTRY_PRICE_FROM_SIGNAL_CLOSE",
            "corrected_fill_contract": "ENTRY_PRICE_FROM_NEXT_BAR_OPEN",
        },
        {
            "scope": "COST",
            "source_path": "src/execution/cost_aware_filter_v1.py",
            "signal_contract": "RESULT_R_INFERRED_FROM_NET_RESULT_R",
            "legacy_fill_contract": "FULL_PROFILE_COST_SUBTRACTED_AGAIN",
            "corrected_fill_contract": "AUDIT_ONLY_NO_NORMALIZED_DECISION_IN_THIS_PHASE",
        },
    ]
    frame = pd.DataFrame(rows)
    frame["source_exists"] = frame["source_path"].map(lambda value: Path(value).exists())
    frame["source_sha256"] = frame["source_path"].map(
        lambda value: file_sha256(Path(value))
    )
    return frame


def _all_permissions_false() -> bool:
    return all(value is False for value in SAFETY_FLAGS.values())


def _preflight_outputs(
    r2_frames: dict[str, pd.DataFrame],
    r2_lineage: pd.DataFrame,
    long_stage_frames: dict[str, pd.DataFrame],
    long_stage_lineage: pd.DataFrame,
    current_manifest: pd.DataFrame,
    dataset_lineage: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    reports_valid = bool(
        len(r2_lineage) == len(R2_REQUIRED_REPORTS)
        and r2_lineage["report_valid"].astype(bool).all()
    )
    long_stage_reports_valid = bool(
        len(long_stage_lineage) == len(LONG_STAGE_REQUIRED_REPORTS)
        and long_stage_lineage["report_valid"].astype(bool).all()
        and all(not frame.empty for frame in long_stage_frames.values())
    )
    datasets_valid = bool(
        len(current_manifest) == 9
        and current_manifest["dataset_valid"].astype(bool).all()
        and len(dataset_lineage) == 9
        and dataset_lineage["hash_matches_r2"].astype(bool).all()
        and dataset_lineage["row_count_matches_r2"].astype(bool).all()
    )
    long_data_exists = find_historical_data_path() is not None
    checks = pd.DataFrame(
        [
            build_check(
                "phase_10_42r_2_reports_valid",
                reports_valid,
                "ERROR",
                f"valid={int(r2_lineage['report_valid'].astype(bool).sum())}/{len(r2_lineage)}",
            ),
            build_check(
                "nine_datasets_match_phase_10_42r_2",
                datasets_valid,
                "ERROR",
                f"lineage_rows={len(dataset_lineage)}",
            ),
            build_check(
                "long_historical_source_exists",
                long_data_exists,
                "ERROR",
                str(find_historical_data_path() or "missing"),
            ),
            build_check(
                "long_stage_source_reports_valid",
                long_stage_reports_valid,
                "ERROR",
                f"valid={int(long_stage_lineage['report_valid'].astype(bool).sum())}/{len(long_stage_lineage)}",
            ),
            build_check(
                "official_forward_artifacts_absent",
                official_forward_artifacts_absent(),
                "ERROR",
                str(OFFICIAL_DATASET_PATH),
            ),
            build_check(
                "all_execution_permissions_false",
                _all_permissions_false(),
                "ERROR",
                str(SAFETY_FLAGS),
            ),
        ]
    )
    validation_passed = not checks["blocker"].astype(bool).any()
    summary = pd.DataFrame(
        [
            {
                "phase": PHASE,
                "run_mode": "PREFLIGHT_ONLY",
                "r2_reports_valid": reports_valid,
                "datasets_valid_and_lineage_matched": datasets_valid,
                "long_historical_source_exists": long_data_exists,
                "long_stage_source_reports_valid": long_stage_reports_valid,
                "audit_completed": False,
                "validation_passed": validation_passed,
                "recommended_action": (
                    "RUN_FULL_SIGNAL_TO_FILL_AUDIT"
                    if validation_passed
                    else "REMEDIATE_PREFLIGHT_BLOCKERS"
                ),
                **SAFETY_FLAGS,
                "total_project_completed": False,
            }
        ]
    )
    return {
        "summary": summary,
        "checks": checks,
        "r2_report_lineage": r2_lineage,
        "long_stage_report_lineage": long_stage_lineage,
        "dataset_manifest": current_manifest,
        "dataset_lineage": dataset_lineage,
    }


def run_signal_to_fill_timing_integrity_audit(
    preflight_only: bool = False,
) -> dict[str, pd.DataFrame]:
    r2_frames, r2_lineage = load_r2_reports()
    long_stage_frames, long_stage_lineage = load_long_stage_reports()
    current_manifest = prepare_dataset_manifest(allow_download=False)
    dataset_lineage = build_dataset_lineage(
        current_manifest,
        r2_frames.get("dataset_manifest", pd.DataFrame()),
    )
    preflight = _preflight_outputs(
        r2_frames,
        r2_lineage,
        long_stage_frames,
        long_stage_lineage,
        current_manifest,
        dataset_lineage,
    )
    if preflight_only or not bool(preflight["summary"].iloc[0]["validation_passed"]):
        write_outputs(preflight)
        return preflight

    errors: list[dict[str, str]] = []
    short_metrics = pd.DataFrame()
    short_trades = pd.DataFrame()
    long_metrics = pd.DataFrame()
    long_trades = pd.DataFrame()
    long_shift = pd.DataFrame()
    try:
        short_metrics, short_trades = run_short_timing_audit()
    except Exception as exc:
        errors.append(
            {"scope": "SHORT_TIMING_AUDIT", "error": f"{type(exc).__name__}: {exc}"}
        )
    try:
        long_metrics, long_trades, long_shift = run_long_timing_audit()
    except Exception as exc:
        errors.append(
            {"scope": "LONG_TIMING_AUDIT", "error": f"{type(exc).__name__}: {exc}"}
        )

    short_aggregate = (
        aggregate_short_metrics(short_metrics)
        if not short_metrics.empty
        else pd.DataFrame()
    )
    short_r2_reproduction = compare_short_to_r2(
        short_metrics,
        r2_frames["short_window_metrics"],
    ) if not short_metrics.empty else pd.DataFrame()
    short_shift = build_short_trade_shift(short_trades)
    long_historical_reproduction = compare_long_historical_to_phase_8_4(
        long_metrics,
        long_stage_frames["phase_8_4_historical_metrics"],
    ) if not long_metrics.empty else pd.DataFrame()
    long_r2_reproduction = compare_phase_8_10_to_r2_readiness(
        long_stage_frames["phase_8_10_monte_carlo_summary"],
        r2_frames["long_readiness"],
    )
    cost_audit = build_cost_accounting_audit()
    source_audit = build_source_contract_audit()

    short_reproduced = bool(
        len(short_r2_reproduction) == 36
        and short_r2_reproduction["all_metrics_match"].astype(bool).all()
    )
    next_short = short_trades[short_trades.get("fill_mode", pd.Series(dtype=str)).eq(FILL_NEXT_OPEN)]
    short_fill_after_signal = bool(
        not next_short.empty
        and (
            pd.to_datetime(next_short["entry_time"], errors="coerce")
            > pd.to_datetime(next_short["signal_time"], errors="coerce")
        ).all()
        and (next_short["entry_index"] == next_short["signal_index"] + 1).all()
    )
    long_historical_reproduced = bool(
        len(long_historical_reproduction) == len(EXPECTED_CANDIDATES)
        and long_historical_reproduction["all_metrics_match"].astype(bool).all()
    )
    long_readiness_lineage_reproduced = bool(
        len(long_r2_reproduction) == 2
        and long_r2_reproduction["all_metrics_match"].astype(bool).all()
    )
    next_long = long_trades[long_trades.get("fill_mode", pd.Series(dtype=str)).eq(FILL_NEXT_OPEN)]
    long_fill_after_signal = bool(
        not next_long.empty
        and (
            pd.to_datetime(next_long["entry_time"], errors="coerce")
            > pd.to_datetime(next_long["observed_at"], errors="coerce")
        ).all()
        and (next_long["entry_index"] == next_long["signal_index"] + 1).all()
    )
    cost_overlap_confirmed = bool(
        not cost_audit.empty
        and cost_audit["potential_cost_double_count_confirmed"].astype(bool).any()
        and not cost_audit["normalized_cost_decision_allowed"].astype(bool).any()
    )
    long_next_open_metrics_unchanged = long_timing_metrics_are_identical(
        long_metrics
    )

    checks = pd.DataFrame(
        [
            *preflight["checks"].to_dict("records"),
            build_check(
                "same_close_short_reproduces_phase_10_42r_2",
                short_reproduced,
                "ERROR",
                f"matching_windows={int(short_r2_reproduction.get('all_metrics_match', pd.Series(dtype=bool)).sum())}/36",
            ),
            build_check(
                "next_open_short_fill_occurs_after_signal",
                short_fill_after_signal,
                "ERROR",
                f"next_open_trades={len(next_short)}",
            ),
            build_check(
                "same_close_long_reproduces_phase_8_4_historical_source",
                long_historical_reproduced,
                "ERROR",
                f"matching_candidates={int(long_historical_reproduction.get('all_metrics_match', pd.Series(dtype=bool)).sum())}/{len(EXPECTED_CANDIDATES)}",
            ),
            build_check(
                "phase_8_10_monte_carlo_source_reproduces_phase_10_42r_2_readiness",
                long_readiness_lineage_reproduced,
                "ERROR",
                f"matching_candidates={int(long_r2_reproduction.get('all_metrics_match', pd.Series(dtype=bool)).sum())}/2",
            ),
            build_check(
                "next_open_long_fill_occurs_after_signal",
                long_fill_after_signal,
                "ERROR",
                f"next_open_trades={len(next_long)}",
            ),
            build_check(
                "current_cost_overlap_detected_without_reclassification",
                cost_overlap_confirmed,
                "ERROR",
                "Existing net result_r receives a full additional cost profile; normalized decision remains disabled.",
            ),
            build_check(
                "source_contracts_present",
                bool(source_audit["source_exists"].astype(bool).all()),
                "ERROR",
                f"sources={len(source_audit)}",
            ),
            build_check(
                "no_runtime_errors",
                not errors,
                "ERROR",
                f"errors={len(errors)}",
            ),
            build_check(
                "official_forward_artifacts_still_absent",
                official_forward_artifacts_absent(),
                "ERROR",
                str(OFFICIAL_DATASET_PATH),
            ),
            build_check(
                "all_execution_permissions_still_false",
                _all_permissions_false(),
                "ERROR",
                str(SAFETY_FLAGS),
            ),
        ]
    )
    validation_passed = not checks["blocker"].astype(bool).any()

    aggregate_lookup = (
        short_aggregate.set_index("timing_mode")
        if not short_aggregate.empty
        else pd.DataFrame()
    )
    same_row = (
        aggregate_lookup.loc[FILL_SAME_CLOSE]
        if not short_aggregate.empty and FILL_SAME_CLOSE in aggregate_lookup.index
        else pd.Series(dtype=object)
    )
    next_row = (
        aggregate_lookup.loc[FILL_NEXT_OPEN]
        if not short_aggregate.empty and FILL_NEXT_OPEN in aggregate_lookup.index
        else pd.Series(dtype=object)
    )
    summary = pd.DataFrame(
        [
            {
                "phase": PHASE,
                "run_mode": "FULL_AUDIT",
                "audit_completed": validation_passed,
                "short_candidate": SHORT_CANDIDATE,
                "short_same_close_trades": int(same_row.get("total_test_trades", 0)),
                "short_same_close_compound_return": safe_float(same_row.get("compound_test_return"), 0.0),
                "short_next_open_trades": int(next_row.get("total_test_trades", 0)),
                "short_next_open_compound_return": safe_float(next_row.get("compound_test_return"), 0.0),
                "short_timing_compound_return_delta": (
                    safe_float(next_row.get("compound_test_return"), 0.0)
                    - safe_float(same_row.get("compound_test_return"), 0.0)
                ),
                "short_next_open_decision": str(next_row.get("walk_forward_decision", "NOT_MEASURED")),
                "short_candidate_status": "REVALIDATED_REJECTED_UNCHANGED",
                "long_next_open_metrics_unchanged": long_next_open_metrics_unchanged,
                "long_timing_status": (
                    "NEXT_OPEN_HISTORICAL_METRICS_UNCHANGED_NOT_APPROVED"
                    if long_next_open_metrics_unchanged
                    else "NEXT_OPEN_MEASURED_NOT_APPROVED"
                ),
                "cost_accounting_status": "NORMALIZATION_REMEDIATION_REQUIRED",
                "official_dataset_exists": OFFICIAL_DATASET_PATH.exists(),
                "official_evidence_rows_written": 0,
                "error_rows": len(errors),
                "total_checks": len(checks),
                "blocker_count": int(checks["blocker"].astype(bool).sum()),
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_10_42R_2A_SIGNAL_TO_FILL_TIMING_AUDIT_COMPLETED"
                    if validation_passed
                    else "PHASE_10_42R_2A_SIGNAL_TO_FILL_TIMING_AUDIT_FAILED"
                ),
                "recommended_next_phase": (
                    "PHASE_10_42R_2B_COST_ACCOUNTING_NORMALIZATION_AND_STRATEGY_RECOVERY_PREREGISTRATION_V1"
                    if validation_passed
                    else "REMEDIATE_SIGNAL_TO_FILL_AUDIT_BLOCKERS"
                ),
                **SAFETY_FLAGS,
                "total_project_completed": False,
            }
        ]
    )

    outputs = {
        "summary": summary,
        "checks": checks,
        "r2_report_lineage": r2_lineage,
        "long_stage_report_lineage": long_stage_lineage,
        "dataset_manifest": current_manifest,
        "dataset_lineage": dataset_lineage,
        "source_contract_audit": source_audit,
        "short_timing_window_metrics": short_metrics,
        "short_timing_aggregate": short_aggregate,
        "short_r2_reproduction": short_r2_reproduction,
        "short_timing_trades": short_trades,
        "short_trade_shift": short_shift,
        "long_timing_metrics": long_metrics,
        "long_timing_trades": long_trades,
        "long_trade_shift": long_shift,
        "long_historical_reproduction": long_historical_reproduction,
        "long_r2_reproduction": long_r2_reproduction,
        "cost_accounting_audit": cost_audit,
        "errors": pd.DataFrame(errors, columns=["scope", "error"]),
    }
    write_outputs(outputs)
    return outputs
