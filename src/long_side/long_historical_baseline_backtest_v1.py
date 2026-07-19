from __future__ import annotations

from pathlib import Path
from socket import close
from typing import Any

import pandas as pd

from src.long_side.long_candidate_discovery_baseline_v1 import (
    DISCOVERY_APPROVAL_STATUS,
    EXPECTED_CANDIDATES,
    build_long_candidate_registry,
)


REPORTS_DIR = Path("reports/phase_8_4_long_historical_baseline_backtest_v1")

PHASE_7_CLOSURE_PATH = Path("docs/PHASE_7_REAL_MARKET_INPUT_BRIDGE_CLOSURE.md")
PHASE_8_1_CONTRACT_DOC_PATH = Path("docs/PHASE_8_LONG_SIDE_VALIDATION_CONTRACT.md")
PHASE_8_2_DISCOVERY_DOC_PATH = Path("docs/PHASE_8_LONG_CANDIDATE_DISCOVERY_BASELINE.md")
PHASE_8_3_HARNESS_DOC_PATH = Path("docs/PHASE_8_LONG_BASELINE_STRUCTURAL_BACKTEST_HARNESS.md")
PHASE_8_4_DOC_PATH = Path("docs/PHASE_8_LONG_HISTORICAL_BASELINE_BACKTEST.md")

HISTORICAL_DATA_CANDIDATE_PATHS = [
    Path("data/btcusdt_15m.csv"),
    Path("data/BTCUSDT_15m.csv"),
    Path("data/BTCUSDT_15M.csv"),
    Path("data/historical/btcusdt_15m.csv"),
    Path("data/market/btcusdt_15m.csv"),
]

HISTORICAL_STATUS = "HISTORICAL_BASELINE_ONLY"
RR_TARGET = 2.5
LOOKAHEAD_BARS = 32
MIN_SIGNAL_GAP_BARS = 12

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


def find_historical_data_path() -> Path | None:
    for path in HISTORICAL_DATA_CANDIDATE_PATHS:
        if path.exists():
            return path

    return None


def find_column(df: pd.DataFrame, aliases: list[str]) -> str | None:
    normalized_map = {
        str(column).strip().lower(): str(column)
        for column in df.columns
    }

    for alias in aliases:
        normalized_alias = alias.strip().lower()
        if normalized_alias in normalized_map:
            return normalized_map[normalized_alias]

    return None


def normalize_ohlc_df(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    missing_columns: list[str] = []

    column_aliases = {
        "timestamp": ["timestamp", "open_time", "date", "datetime", "time", "fecha"],
        "open": ["open", "apertura", "o"],
        "high": ["high", "alto", "h"],
        "low": ["low", "bajo", "l"],
        "close": ["close", "cierre", "c"],
        "volume": ["volume", "volumen", "v"],
    }

    output_df = pd.DataFrame()

    for target_column, aliases in column_aliases.items():
        source_column = find_column(raw_df, aliases)

        if source_column is None:
            if target_column == "timestamp":
                output_df["timestamp"] = range(len(raw_df))
                continue

            if target_column == "volume":
                output_df["volume"] = 0.0
                continue

            missing_columns.append(target_column)
            continue

        output_df[target_column] = raw_df[source_column]

    if missing_columns:
        return pd.DataFrame(), missing_columns

    for column in ["open", "high", "low", "close", "volume"]:
        output_df[column] = pd.to_numeric(output_df[column], errors="coerce")

    output_df["timestamp"] = output_df["timestamp"].astype(str)

    output_df = output_df.dropna(subset=["open", "high", "low", "close"]).copy()

    positive_price_mask = (
        (output_df["open"] > 0)
        & (output_df["high"] > 0)
        & (output_df["low"] > 0)
        & (output_df["close"] > 0)
    )

    valid_ohlc_mask = (
        (output_df["high"] >= output_df[["open", "close"]].max(axis=1))
        & (output_df["low"] <= output_df[["open", "close"]].min(axis=1))
        & (output_df["high"] >= output_df["low"])
    )

    output_df = output_df.loc[positive_price_mask & valid_ohlc_mask].copy()
    output_df = output_df.reset_index(drop=True)

    output_df["symbol"] = "BTCUSDT"
    output_df["timeframe"] = "15m"

    return output_df, missing_columns


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    result_df = df.copy()

    close = result_df["close"]
    high = result_df["high"]
    low = result_df["low"]

    result_df["ema20"] = close.ewm(span=20, adjust=False).mean()
    result_df["ema50"] = close.ewm(span=50, adjust=False).mean()
    result_df["ema200"] = close.ewm(span=200, adjust=False).mean()

    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)

    avg_gain = gain.rolling(14, min_periods=1).mean()
    avg_loss = loss.rolling(14, min_periods=1).mean()

    rs = avg_gain / avg_loss.mask(avg_loss.eq(0))
    result_df["rsi14"] = (100 - (100 / (1 + rs))).fillna(50.0)

    prev_close = close.shift(1)
    true_range = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    result_df["atr14"] = true_range.rolling(14, min_periods=1).mean()

    fallback_atr = (high - low).rolling(14, min_periods=1).mean()
    result_df["atr14"] = result_df["atr14"].fillna(fallback_atr)

    zero_atr_mask = result_df["atr14"].eq(0)
    result_df.loc[zero_atr_mask, "atr14"] = fallback_atr.loc[zero_atr_mask]

    result_df["atr14"] = result_df["atr14"].fillna(close * 0.002)
    result_df["atr14"] = result_df["atr14"].where(
        result_df["atr14"] > 0,
        close * 0.002,
    )

    result_df["rolling_low_20"] = low.shift(1).rolling(20, min_periods=1).min()
    result_df["rolling_high_20"] = high.shift(1).rolling(20, min_periods=1).max()
    result_df["rolling_low_48"] = low.shift(1).rolling(48, min_periods=1).min()
    result_df["rolling_high_48"] = high.shift(1).rolling(48, min_periods=1).max()

    swing_high = result_df["rolling_high_48"]
    swing_low = result_df["rolling_low_48"]
    swing_range = (swing_high - swing_low).clip(lower=0.0)

    result_df["fib_pullback_50"] = swing_high - (swing_range * 0.50)
    result_df["fib_pullback_786"] = swing_high - (swing_range * 0.786)

    return result_df.reset_index(drop=True)


def apply_min_gap(signal_indexes: list[int], min_gap: int) -> list[int]:
    selected_indexes: list[int] = []
    last_index = -10**9

    for index in signal_indexes:
        if index - last_index >= min_gap:
            selected_indexes.append(index)
            last_index = index

    return selected_indexes


def candidate_signal_indexes(df: pd.DataFrame, candidate_id: str) -> list[int]:
    valid_zone = df.index < (len(df) - LOOKAHEAD_BARS - 1)

    if candidate_id == "LONG_BASE_FIB_PULLBACK_V1":
        bullish_context = (df["ema20"] > df["ema50"]) | (df["close"] > df["ema200"])
        pullback_touch = df["low"] <= df["fib_pullback_50"]
        reclaim = df["close"] > df["fib_pullback_786"]
        confirmation = df["close"] > df["open"]
        mask = valid_zone & bullish_context & pullback_touch & reclaim & confirmation

    elif candidate_id == "LONG_BASE_LIQUIDITY_SWEEP_V1":
        swept_low = df["low"] < df["rolling_low_20"]
        reclaim = df["close"] > df["rolling_low_20"]
        confirmation = df["close"] > df["open"]
        mask = valid_zone & swept_low & reclaim & confirmation

    elif candidate_id == "LONG_BASE_MTF_BULLISH_CONTINUATION_V1":
        bullish_stack = (df["ema20"] > df["ema50"]) & (df["ema50"] > df["ema200"])
        pullback_to_ema = df["low"] <= df["ema20"]
        continuation = df["close"] > df["ema20"]
        mask = valid_zone & bullish_stack & pullback_to_ema & continuation

    elif candidate_id == "LONG_BASE_FAILED_BREAKDOWN_V1":
        failed_break = df["low"] < df["rolling_low_48"]
        reclaim = df["close"] > df["rolling_low_48"]
        confirmation = df["close"] > df["open"]
        mask = valid_zone & failed_break & reclaim & confirmation

    else:
        mask = pd.Series(False, index=df.index)

    raw_indexes = df.index[mask.fillna(False)].astype(int).tolist()
    return apply_min_gap(raw_indexes, MIN_SIGNAL_GAP_BARS)


def structural_stop_for_candidate(
    df: pd.DataFrame,
    signal_index: int,
    candidate_id: str,
) -> float:
    row = df.iloc[signal_index]
    entry_price = float(row["close"])
    atr = max(float(row["atr14"]), entry_price * 0.001)

    if candidate_id in {
        "LONG_BASE_LIQUIDITY_SWEEP_V1",
        "LONG_BASE_FAILED_BREAKDOWN_V1",
    }:
        structural_low = float(row["low"])

    elif candidate_id == "LONG_BASE_MTF_BULLISH_CONTINUATION_V1":
        start = max(0, signal_index - 5)
        structural_low = float(df.iloc[start : signal_index + 1]["low"].min())

    else:
        structural_low = min(float(row["low"]), float(row["rolling_low_20"]))

    stop_price = min(structural_low - (0.05 * atr), entry_price - (0.50 * atr))

    if stop_price <= 0 or stop_price >= entry_price:
        stop_price = entry_price - (1.50 * atr)

    return float(stop_price)


def resolve_long_trade(
    df: pd.DataFrame,
    signal_index: int,
    candidate_id: str,
) -> dict[str, Any]:
    signal_row = df.iloc[signal_index]

    entry_price = float(signal_row["close"])
    stop_price = structural_stop_for_candidate(
        df=df,
        signal_index=signal_index,
        candidate_id=candidate_id,
    )

    risk = entry_price - stop_price

    if risk <= 0:
        risk = max(float(signal_row["atr14"]) * 1.5, entry_price * 0.002)
        stop_price = entry_price - risk

    target_price = entry_price + (risk * RR_TARGET)
    reward = target_price - entry_price
    risk_reward = reward / risk if risk > 0 else 0.0

    future_df = df.iloc[signal_index + 1 : signal_index + 1 + LOOKAHEAD_BARS]

    max_high = entry_price
    min_low = entry_price
    resolution_status = "OPEN_TIMEOUT"
    result_r = 0.0
    bars_to_resolution = int(len(future_df))
    resolution_timestamp = ""

    for offset, (_, bar) in enumerate(future_df.iterrows(), start=1):
        high = float(bar["high"])
        low = float(bar["low"])

        max_high = max(max_high, high)
        min_low = min(min_low, low)

        stop_hit = low <= stop_price
        target_hit = high >= target_price

        if stop_hit:
            resolution_status = "STOP_HIT"
            result_r = -1.0
            bars_to_resolution = offset
            resolution_timestamp = str(bar["timestamp"])
            break

        if target_hit:
            resolution_status = "TARGET_HIT"
            result_r = risk_reward
            bars_to_resolution = offset
            resolution_timestamp = str(bar["timestamp"])
            break

    if resolution_status == "OPEN_TIMEOUT" and not future_df.empty:
        resolution_timestamp = str(future_df.iloc[-1]["timestamp"])

    mfe_r = (max_high - entry_price) / risk if risk > 0 else 0.0
    mae_r = (min_low - entry_price) / risk if risk > 0 else 0.0

    return {
        "candidate_id": candidate_id,
        "signal_index": signal_index,
        "observed_at": str(signal_row["timestamp"]),
        "symbol": str(signal_row["symbol"]),
        "timeframe": str(signal_row["timeframe"]),
        "direction": "LONG",
        "router_decision": "WATCH_ONLY",
        "entry_price": entry_price,
        "stop_price": stop_price,
        "target_price": target_price,
        "risk": risk,
        "reward": reward,
        "risk_reward": risk_reward,
        "valid_long_structure": stop_price < entry_price < target_price,
        "resolution_status": resolution_status,
        "result_r": result_r,
        "mfe_r": mfe_r,
        "mae_r": mae_r,
        "bars_to_resolution": bars_to_resolution,
        "resolution_timestamp": resolution_timestamp,
        "historical_status": HISTORICAL_STATUS,
        "approval_status": DISCOVERY_APPROVAL_STATUS,
        "long_strategy_approved": False,
        "long_entries_approved": False,
        "execution_allowed": False,
    }


def run_historical_backtest(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for candidate_id in EXPECTED_CANDIDATES:
        indexes = candidate_signal_indexes(df=df, candidate_id=candidate_id)

        for signal_index in indexes:
            trade = resolve_long_trade(
                df=df,
                signal_index=signal_index,
                candidate_id=candidate_id,
            )
            rows.append(trade)

    if not rows:
        return pd.DataFrame(
            columns=[
                "candidate_id",
                "signal_index",
                "observed_at",
                "symbol",
                "timeframe",
                "direction",
                "router_decision",
                "entry_price",
                "stop_price",
                "target_price",
                "risk",
                "reward",
                "risk_reward",
                "valid_long_structure",
                "resolution_status",
                "result_r",
                "mfe_r",
                "mae_r",
                "bars_to_resolution",
                "resolution_timestamp",
                "historical_status",
                "approval_status",
                "long_strategy_approved",
                "long_entries_approved",
                "execution_allowed",
            ]
        )

    return pd.DataFrame(rows)


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

    for candidate_id in EXPECTED_CANDIDATES:
        group = trades_df[trades_df["candidate_id"].eq(candidate_id)].copy()

        result_r = pd.to_numeric(group.get("result_r", pd.Series(dtype=float)), errors="coerce").fillna(0.0)

        trades = int(len(group))
        wins = int((result_r > 0).sum())
        losses = int((result_r < 0).sum())
        open_trades = int(group["resolution_status"].astype(str).eq("OPEN_TIMEOUT").sum()) if trades > 0 else 0

        gross_win_r = float(result_r[result_r > 0].sum()) if trades > 0 else 0.0
        gross_loss_r = float(result_r[result_r < 0].sum()) if trades > 0 else 0.0

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
                "total_result_r": float(result_r.sum()) if trades > 0 else 0.0,
                "average_result_r": float(result_r.mean()) if trades > 0 else 0.0,
                "max_drawdown_r": calculate_max_drawdown_r(result_r.tolist()) if trades > 0 else 0.0,
                "candidate_approved": False,
                "historical_status": HISTORICAL_STATUS,
            }
        )

    return pd.DataFrame(rows)


def no_candidate_approved(trades_df: pd.DataFrame, metrics_df: pd.DataFrame) -> bool:
    if not metrics_df.empty and metrics_df["candidate_approved"].astype(bool).any():
        return False

    if trades_df.empty:
        return True

    approval_columns = [
        "long_strategy_approved",
        "long_entries_approved",
        "execution_allowed",
    ]

    for column in approval_columns:
        if column not in trades_df.columns:
            return False

        if trades_df[column].astype(bool).any():
            return False

    return True


def validate_long_historical_baseline_backtest() -> dict[str, pd.DataFrame]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    candidates = build_long_candidate_registry()
    candidate_df = pd.DataFrame([candidate.__dict__ for candidate in candidates])

    phase_anchors = {
        "phase_7_closure_exists": PHASE_7_CLOSURE_PATH,
        "phase_8_1_contract_doc_exists": PHASE_8_1_CONTRACT_DOC_PATH,
        "phase_8_2_discovery_doc_exists": PHASE_8_2_DISCOVERY_DOC_PATH,
        "phase_8_3_harness_doc_exists": PHASE_8_3_HARNESS_DOC_PATH,
        "phase_8_4_historical_doc_exists": PHASE_8_4_DOC_PATH,
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

    historical_data_path = find_historical_data_path()
    historical_data_exists = historical_data_path is not None

    checks.append(
        build_check(
            check_group="historical_data",
            check_name="historical_ohlc_file_exists",
            passed=historical_data_exists,
            severity="INFO" if historical_data_exists else "ERROR",
            details=str(historical_data_path) if historical_data_path else "No supported OHLC file found.",
        )
    )

    raw_df = pd.DataFrame()
    normalized_df = pd.DataFrame()
    indicator_df = pd.DataFrame()
    trades_df = pd.DataFrame()
    metrics_df = pd.DataFrame()
    missing_columns: list[str] = []

    if historical_data_path is not None:
        raw_df = pd.read_csv(historical_data_path)
        normalized_df, missing_columns = normalize_ohlc_df(raw_df)

        if not normalized_df.empty:
            indicator_df = add_indicators(normalized_df)
            trades_df = run_historical_backtest(indicator_df)
            metrics_df = build_candidate_metrics(trades_df)

    checks.append(
        build_check(
            check_group="historical_data",
            check_name="required_ohlc_columns_present",
            passed=len(missing_columns) == 0,
            severity="INFO" if len(missing_columns) == 0 else "ERROR",
            details="missing_columns=" + ",".join(missing_columns),
        )
    )

    checks.append(
        build_check(
            check_group="historical_data",
            check_name="normalized_ohlc_rows_present",
            passed=len(normalized_df) > 100,
            severity="INFO" if len(normalized_df) > 100 else "ERROR",
            details=f"normalized_rows={len(normalized_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="candidate_scope",
            check_name="expected_candidate_count_present",
            passed=len(candidate_df) == len(EXPECTED_CANDIDATES),
            severity="INFO" if len(candidate_df) == len(EXPECTED_CANDIDATES) else "ERROR",
            details=f"candidate_count={len(candidate_df)}",
        )
    )

    checks.append(
        build_check(
            check_group="measurement",
            check_name="historical_backtest_executed",
            passed=not metrics_df.empty and len(metrics_df) == len(EXPECTED_CANDIDATES),
            severity=(
                "INFO"
                if not metrics_df.empty and len(metrics_df) == len(EXPECTED_CANDIDATES)
                else "ERROR"
            ),
            details=f"trades={len(trades_df)}, metrics_rows={len(metrics_df)}",
        )
    )

    total_trades = int(len(trades_df))

    checks.append(
        build_check(
            check_group="measurement",
            check_name="historical_trade_count_recorded",
            passed=True,
            severity="INFO" if total_trades > 0 else "WARNING",
            details=f"trade_count={total_trades}",
        )
    )

    if not trades_df.empty:
        all_trades_long = trades_df["direction"].astype(str).str.upper().eq("LONG").all()
        all_watch_only = trades_df["router_decision"].astype(str).str.upper().eq("WATCH_ONLY").all()
        all_valid_long_structure = trades_df["valid_long_structure"].astype(bool).all()
    else:
        all_trades_long = True
        all_watch_only = True
        all_valid_long_structure = True

    checks.append(
        build_check(
            check_group="directional_contract",
            check_name="all_historical_trades_direction_long",
            passed=all_trades_long,
            severity="INFO" if all_trades_long else "ERROR",
            details=f"all_trades_long={all_trades_long}",
        )
    )

    checks.append(
        build_check(
            check_group="directional_contract",
            check_name="all_historical_trades_watch_only",
            passed=all_watch_only,
            severity="INFO" if all_watch_only else "ERROR",
            details=f"all_watch_only={all_watch_only}",
        )
    )

    checks.append(
        build_check(
            check_group="price_structure",
            check_name="all_historical_long_price_structures_valid",
            passed=all_valid_long_structure,
            severity="INFO" if all_valid_long_structure else "ERROR",
            details=f"all_valid_long_structure={all_valid_long_structure}",
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
            check_name="out_of_sample_not_executed",
            passed=True,
            severity="INFO",
            details="OOS validation is deferred.",
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
            check_name="phase_8_5_recommended_next",
            passed=True,
            severity="INFO",
            details="Recommended next step: Phase 8.5 LONG Candidate Historical Comparison V1.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="long_side_remains_unestablished",
            passed=True,
            severity="WARNING",
            details="Phase 8.4 measures historical baseline only; LONG side is not established.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="real_entries_remain_blocked",
            passed=True,
            severity="WARNING",
            details="Real entries remain blocked after Phase 8.4.",
        )
    )

    checks_df = pd.DataFrame(checks)

    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    result_r = pd.to_numeric(trades_df.get("result_r", pd.Series(dtype=float)), errors="coerce").fillna(0.0)

    summary_df = pd.DataFrame(
        [
            {
                "phase": "8.4",
                "historical_data_path": str(historical_data_path) if historical_data_path else "",
                "raw_rows": int(len(raw_df)),
                "normalized_rows": int(len(normalized_df)),
                "indicator_rows": int(len(indicator_df)),
                "candidate_count": int(len(candidate_df)),
                "trade_count": int(len(trades_df)),
                "metrics_rows": int(len(metrics_df)),
                "candidates_with_trades": int(metrics_df["trades"].gt(0).sum()) if not metrics_df.empty else 0,
                "target_hits": int(trades_df["resolution_status"].eq("TARGET_HIT").sum()) if not trades_df.empty else 0,
                "stop_hits": int(trades_df["resolution_status"].eq("STOP_HIT").sum()) if not trades_df.empty else 0,
                "open_timeouts": int(trades_df["resolution_status"].eq("OPEN_TIMEOUT").sum()) if not trades_df.empty else 0,
                "total_result_r": float(result_r.sum()) if len(result_r) > 0 else 0.0,
                "average_result_r": float(result_r.mean()) if len(result_r) > 0 else 0.0,
                "average_risk_reward": (
                    float(pd.to_numeric(trades_df["risk_reward"], errors="coerce").mean())
                    if not trades_df.empty
                    else 0.0
                ),
                "historical_backtest_executed": not metrics_df.empty,
                "out_of_sample_executed": False,
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
                "recommended_next_phase": "PHASE_8_5_LONG_CANDIDATE_HISTORICAL_COMPARISON_V1",
                "estimated_total_project_progress_percent": 93,
                "total_checks": int(len(checks_df)),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_8_4_LONG_HISTORICAL_BASELINE_BACKTEST_VALIDATED"
                    if validation_passed
                    else "PHASE_8_4_LONG_HISTORICAL_BASELINE_BACKTEST_FAILED"
                ),
            }
        ]
    )

    candidate_df.to_csv(
        REPORTS_DIR / "long_historical_candidate_registry_v1.csv",
        index=False,
    )
    normalized_df.to_csv(
        REPORTS_DIR / "long_historical_normalized_ohlc_preview_v1.csv",
        index=False,
    )
    trades_df.to_csv(
        REPORTS_DIR / "long_historical_backtest_trades_v1.csv",
        index=False,
    )
    metrics_df.to_csv(
        REPORTS_DIR / "long_historical_backtest_metrics_v1.csv",
        index=False,
    )
    checks_df.to_csv(
        REPORTS_DIR / "long_historical_backtest_checks_v1.csv",
        index=False,
    )
    summary_df.to_csv(
        REPORTS_DIR / "long_historical_backtest_summary_v1.csv",
        index=False,
    )

    return {
        "summary": summary_df,
        "candidates": candidate_df,
        "normalized_ohlc": normalized_df,
        "trades": trades_df,
        "metrics": metrics_df,
        "checks": checks_df,
    }
