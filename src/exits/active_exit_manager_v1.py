from __future__ import annotations

import math
from typing import Callable

import pandas as pd


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift(1)).abs()
    low_close = (df["low"] - df["close"].shift(1)).abs()

    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    return true_range.ewm(alpha=1 / period, adjust=False).mean()


def calculate_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()

    rs = avg_gain / avg_loss.mask(avg_loss.eq(0))
    rsi = 100 - (100 / (1 + rs))

    return rsi.fillna(50)


def add_active_exit_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    for col in ["open", "high", "low", "close", "volume"]:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors="coerce")

    result["aev1_atr14"] = calculate_atr(result, period=14)
    result["aev1_rsi14"] = calculate_rsi(result["close"], period=14)
    result["aev1_ema20"] = result["close"].ewm(span=20, adjust=False).mean()
    result["aev1_ema50"] = result["close"].ewm(span=50, adjust=False).mean()

    result["aev1_bullish_candle"] = result["close"] > result["open"]
    result["aev1_bearish_candle"] = result["close"] < result["open"]

    result["aev1_close_above_ema20"] = result["close"] > result["aev1_ema20"]
    result["aev1_close_below_ema20"] = result["close"] < result["aev1_ema20"]

    result["aev1_ema20_slope_5"] = (
        result["aev1_ema20"] / result["aev1_ema20"].shift(5) - 1
    )

    result["aev1_bearish_momentum_lost"] = (
        result["aev1_bullish_candle"]
        & result["aev1_close_above_ema20"]
        & (result["aev1_rsi14"] > 52)
    )

    return result


def build_exit_profile(profile_name: str) -> dict:
    profiles = {
        "FIXED_RR_2_5": {
            "name": "FIXED_RR_2_5",
            "risk_reward": 2.5,
            "move_to_be_after_r": None,
            "trail_after_r": None,
            "trail_atr_multiplier": None,
            "partial_at_r": None,
            "momentum_exit_after_r": None,
        },
        "BREAKEVEN_AFTER_1R": {
            "name": "BREAKEVEN_AFTER_1R",
            "risk_reward": 2.5,
            "move_to_be_after_r": 1.0,
            "trail_after_r": None,
            "trail_atr_multiplier": None,
            "partial_at_r": None,
            "momentum_exit_after_r": None,
        },
        "TRAIL_ATR_AFTER_1R": {
            "name": "TRAIL_ATR_AFTER_1R",
            "risk_reward": 2.5,
            "move_to_be_after_r": 1.0,
            "trail_after_r": 1.0,
            "trail_atr_multiplier": 1.5,
            "partial_at_r": None,
            "momentum_exit_after_r": None,
        },
        "PARTIAL_1R_THEN_2_5R": {
            "name": "PARTIAL_1R_THEN_2_5R",
            "risk_reward": 2.5,
            "move_to_be_after_r": 1.0,
            "trail_after_r": None,
            "trail_atr_multiplier": None,
            "partial_at_r": 1.0,
            "partial_fraction": 0.5,
            "momentum_exit_after_r": None,
        },
        "MOMENTUM_EXIT_AFTER_1R": {
            "name": "MOMENTUM_EXIT_AFTER_1R",
            "risk_reward": 2.5,
            "move_to_be_after_r": 1.0,
            "trail_after_r": None,
            "trail_atr_multiplier": None,
            "partial_at_r": None,
            "momentum_exit_after_r": 1.0,
        },
    }

    if profile_name not in profiles:
        raise ValueError(f"Unknown exit profile: {profile_name}")

    return profiles[profile_name]


def _safe_float(value, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return default

        if isinstance(value, float) and math.isnan(value):
            return default

        return float(value)
    except Exception:
        return default

def _config_get(config, key: str, default=None):
    if isinstance(config, dict):
        return config.get(key, default)

    return getattr(config, key, default)

def _profit_factor(net_pnl: pd.Series):
    gross_profit = float(net_pnl[net_pnl > 0].sum())
    gross_loss = float(net_pnl[net_pnl < 0].sum())

    if gross_loss == 0:
        if gross_profit > 0:
            return None
        return 0.0

    return gross_profit / abs(gross_loss)


def simulate_short_trade_active_exit(
    df: pd.DataFrame,
    entry_index: int,
    capital: float,
    config: dict,
    exit_profile: dict,
) -> dict | None:
    entry_row = df.iloc[entry_index]

    close = _safe_float(entry_row.get("close"), 0.0)
    atr = _safe_float(entry_row.get("aev1_atr14"), 0.0)

    if close <= 0 or atr <= 0:
        return None

    initial_capital = _safe_float(_config_get(config, "initial_capital"), 1000.0)
    risk_per_trade = _safe_float(_config_get(config, "risk_per_trade"), 0.01)
    atr_multiplier = _safe_float(_config_get(config, "atr_multiplier"), 1.25)
    max_holding_bars = int(_config_get(config, "max_holding_bars", 48))
    fee_rate = _safe_float(_config_get(config, "fee_rate"), 0.001)
    spread_rate = _safe_float(_config_get(config, "spread_rate"), 0.0002)

    risk_reward = _safe_float(
        exit_profile.get("risk_reward"),
        _safe_float(_config_get(config, "risk_reward"), 2.5),
    )

    entry_price = close * (1 - spread_rate / 2)
    stop_initial = entry_price + atr * atr_multiplier
    risk_distance = stop_initial - entry_price

    if risk_distance <= 0:
        return None

    take_profit_initial = entry_price - risk_distance * risk_reward

    risk_amount = capital * risk_per_trade

    if risk_amount <= 0:
        risk_amount = initial_capital * risk_per_trade

    position_units = risk_amount / risk_distance

    entry_fee = abs(entry_price * position_units) * fee_rate

    current_stop = stop_initial
    remaining_fraction = 1.0
    partial_taken = False
    partial_exit_price = None
    partial_realized_gross = 0.0
    partial_exit_fees = 0.0

    max_favorable_r = 0.0
    max_adverse_r = 0.0

    exit_index = None
    final_exit_price = None
    exit_reason = None

    mfe_reached = False

    end_index = min(len(df) - 1, entry_index + max_holding_bars)

    for i in range(entry_index + 1, end_index + 1):
        row = df.iloc[i]

        high = _safe_float(row.get("high"), 0.0)
        low = _safe_float(row.get("low"), 0.0)
        close_i = _safe_float(row.get("close"), 0.0)
        atr_i = _safe_float(row.get("aev1_atr14"), atr)

        favorable_r = (entry_price - low) / risk_distance
        adverse_r = (high - entry_price) / risk_distance

        max_favorable_r = max(max_favorable_r, favorable_r)
        max_adverse_r = max(max_adverse_r, adverse_r)

        if exit_profile.get("move_to_be_after_r") is not None:
            if max_favorable_r >= float(exit_profile["move_to_be_after_r"]):
                mfe_reached = True
                current_stop = min(current_stop, entry_price)

        if exit_profile.get("trail_after_r") is not None:
            if max_favorable_r >= float(exit_profile["trail_after_r"]):
                trail_multiplier = float(exit_profile.get("trail_atr_multiplier", 1.5))
                trail_stop = close_i + atr_i * trail_multiplier
                current_stop = min(current_stop, trail_stop)

        if high >= current_stop:
            exit_index = i
            final_exit_price = current_stop * (1 + spread_rate / 2)
            if current_stop <= entry_price:
                exit_reason = "BREAKEVEN_OR_TRAILING_STOP"
            else:
                exit_reason = "STOP_LOSS"
            break

        if exit_profile.get("partial_at_r") is not None and not partial_taken:
            partial_r = float(exit_profile["partial_at_r"])
            partial_target = entry_price - risk_distance * partial_r

            if low <= partial_target:
                partial_fraction = float(exit_profile.get("partial_fraction", 0.5))
                partial_exit_price = partial_target * (1 + spread_rate / 2)

                partial_units = position_units * partial_fraction

                partial_realized_gross = (
                    entry_price - partial_exit_price
                ) * partial_units

                partial_exit_fees = abs(partial_exit_price * partial_units) * fee_rate

                remaining_fraction -= partial_fraction
                partial_taken = True

                current_stop = min(current_stop, entry_price)

        if low <= take_profit_initial:
            exit_index = i
            final_exit_price = take_profit_initial * (1 + spread_rate / 2)
            exit_reason = "TAKE_PROFIT"
            break

        if exit_profile.get("momentum_exit_after_r") is not None:
            momentum_trigger = float(exit_profile["momentum_exit_after_r"])

            if max_favorable_r >= momentum_trigger:
                momentum_lost = bool(row.get("aev1_bearish_momentum_lost", False))

                if momentum_lost:
                    exit_index = i
                    final_exit_price = close_i * (1 + spread_rate / 2)
                    exit_reason = "MOMENTUM_EXIT"
                    break

    if exit_index is None:
        exit_index = end_index
        final_exit_price = _safe_float(df.iloc[end_index].get("close"), entry_price)
        final_exit_price = final_exit_price * (1 + spread_rate / 2)
        exit_reason = "MAX_HOLDING"

    remaining_units = position_units * remaining_fraction

    final_gross = (entry_price - final_exit_price) * remaining_units
    final_exit_fees = abs(final_exit_price * remaining_units) * fee_rate

    total_gross = partial_realized_gross + final_gross
    total_fees = entry_fee + partial_exit_fees + final_exit_fees
    net_pnl = total_gross - total_fees

    result_r = net_pnl / risk_amount if risk_amount else 0.0

    return {
        "entry_index": entry_index,
        "exit_index": exit_index,
        "entry_time": entry_row.get("timestamp", None),
        "exit_time": df.iloc[exit_index].get("timestamp", None),
        "direction": "SHORT",
        "exit_profile": exit_profile["name"],
        "entry_price": entry_price,
        "stop_loss_initial": stop_initial,
        "take_profit_initial": take_profit_initial,
        "exit_price": final_exit_price,
        "partial_taken": partial_taken,
        "partial_exit_price": partial_exit_price,
        "risk_amount": risk_amount,
        "position_units": position_units,
        "gross_pnl": total_gross,
        "fees": total_fees,
        "net_pnl": net_pnl,
        "result_r": result_r,
        "max_favorable_r": max_favorable_r,
        "max_adverse_r": max_adverse_r,
        "bars_held": exit_index - entry_index,
        "exit_reason": exit_reason,
    }


def run_active_exit_backtest(
    df: pd.DataFrame,
    strategy_func: Callable,
    config: dict,
    exit_profile: dict,
) -> tuple[pd.DataFrame, dict]:
    market_df = add_active_exit_features(df)

    initial_capital = _safe_float(_config_get(config, "initial_capital"), 1000.0)

    capital = initial_capital
    equity_curve = [capital]
    trades = []

    i = 250

    while i < len(market_df) - 2:
        signal = strategy_func(market_df, i, config)

        if signal == "SHORT":
            trade = simulate_short_trade_active_exit(
                df=market_df,
                entry_index=i,
                capital=capital,
                config=config,
                exit_profile=exit_profile,
            )

            if trade is not None:
                capital += trade["net_pnl"]
                equity_curve.append(capital)
                trades.append(trade)
                i = int(trade["exit_index"]) + 1
                continue

        i += 1

    trades_df = pd.DataFrame(trades)

    if trades_df.empty:
        summary = {
            "initial_capital": initial_capital,
            "ending_capital": initial_capital,
            "total_return_pct": 0.0,
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0,
            "profit_factor": None,
            "expectancy": 0.0,
            "expectancy_r": 0.0,
            "max_drawdown_pct": 0.0,
        }

        return trades_df, summary

    wins = int((trades_df["net_pnl"] > 0).sum())
    losses = int((trades_df["net_pnl"] <= 0).sum())
    total_trades = int(len(trades_df))

    equity = pd.Series(equity_curve)
    running_max = equity.cummax()
    drawdown = equity / running_max - 1
    max_drawdown_pct = float(drawdown.min())

    summary = {
        "initial_capital": initial_capital,
        "ending_capital": capital,
        "total_return_pct": (capital / initial_capital) - 1,
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "win_rate": wins / total_trades if total_trades else 0.0,
        "profit_factor": _profit_factor(trades_df["net_pnl"]),
        "expectancy": float(trades_df["net_pnl"].mean()),
        "expectancy_r": float(trades_df["result_r"].mean()),
        "average_win_r": float(
            trades_df.loc[trades_df["result_r"] > 0, "result_r"].mean()
        ),
        "average_loss_r": float(
            trades_df.loc[trades_df["result_r"] <= 0, "result_r"].mean()
        ),
        "max_drawdown_pct": max_drawdown_pct,
        "avg_bars_held": float(trades_df["bars_held"].mean()),
    }

    return trades_df, summary
