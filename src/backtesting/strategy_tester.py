import os
import sys

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from liquidity.liquidity_engine import (
    generate_liquidity_report_v2
)

from signals.liquidity_filter import (
    evaluate_liquidity_filter
)

from backtesting.trade_simulator import (
    simulate_trade_with_atr
)

from indicators.indicator_engine import (
    generate_indicator_report
)

from backtesting.performance_metrics import (
    generate_performance_report
)


def calculate_trade_result(
    entry_price,
    exit_price,
    direction
):

    if direction == "LONG":

        return (
            (exit_price - entry_price)
            / entry_price
        ) * 100

    if direction == "SHORT":

        return (
            (entry_price - exit_price)
            / entry_price
        ) * 100

    return 0


def evaluate_strategy_signal(row):

    if (
        row["ema20"] > row["ema50"]
        and row["rsi"] > 55
    ):
        return "LONG"

    if (
        row["ema20"] < row["ema50"]
        and row["rsi"] < 45
    ):
        return "SHORT"

    return "WAIT"


def prepare_indicator_columns(df):

    df = df.copy()

    df["ema20"] = (
        df["close"]
        .ewm(span=20, adjust=False)
        .mean()
    )

    df["ema50"] = (
        df["close"]
        .ewm(span=50, adjust=False)
        .mean()
    )

    delta = df["close"].diff()

    gain = delta.where(
        delta > 0,
        0
    )

    loss = -delta.where(
        delta < 0,
        0
    )

    avg_gain = gain.rolling(14).mean()

    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss

    df["rsi"] = 100 - (
        100 / (1 + rs)
    )

    df = df.dropna()

    high_low = df["high"] - df["low"]

    high_close = (
        df["high"] - df["close"].shift()
    ).abs()

    low_close = (
        df["low"] - df["close"].shift()
    ).abs()

    true_range = high_low.combine(
        high_close,
        max
    ).combine(
        low_close,
        max
    )

    df["atr"] = true_range.rolling(14).mean()

    return df


def run_backtest(
    df,
    holding_period=1
):

    df = prepare_indicator_columns(df)

    trades = []

    for i in range(
        0,
        len(df) - holding_period
    ):

        row = df.iloc[i]

        signal = evaluate_strategy_signal(row)

        if signal == "WAIT":
            continue

        entry_price = df.iloc[i]["close"]

        exit_price = df.iloc[
            i + holding_period
        ]["close"]

        result_pct = calculate_trade_result(
            entry_price,
            exit_price,
            signal
        )

        trades.append({
            "timestamp": row["timestamp"],
            "direction": signal,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "result_pct": result_pct
        })

    performance = generate_performance_report(
        trades
    )

    return {
        "trades": trades,
        "performance": performance
    }

def run_atr_backtest(
    df,
    sl_multiplier=1,
    tp_multiplier=2,
    max_bars=8
):

    df = prepare_indicator_columns(df)

    trades = []

    for i in range(
        0,
        len(df) - max_bars
    ):

        row = df.iloc[i]

        signal = evaluate_strategy_signal(row)

        if signal == "WAIT":
            continue

        result = simulate_trade_with_atr(
            df=df,
            entry_index=i,
            direction=signal,
            atr_value=row["atr"],
            sl_multiplier=sl_multiplier,
            tp_multiplier=tp_multiplier,
            max_bars=max_bars
        )

        if result is None:
            continue

        trades.append({
            "timestamp": row["timestamp"],
            "direction": signal,
            "result": result["result"],
            "exit_reason": result["exit_reason"],
            "result_pct": result["result_pct"]
        })

    performance = generate_performance_report(
        trades
    )

    return {
        "trades": trades,
        "performance": performance
    }

def run_atr_backtest_with_liquidity_filter(
    df,
    sl_multiplier=1,
    tp_multiplier=2,
    max_bars=8,
    liquidity_lookback=96,
    tolerance_pct=0.15,
    min_touches=2,
    max_distance_pct=1.0
):

    df = prepare_indicator_columns(df)

    trades = []

    for i in range(
        liquidity_lookback,
        len(df) - max_bars
    ):

        row = df.iloc[i]

        signal = evaluate_strategy_signal(row)

        if signal == "WAIT":
            continue

        partial_df = df.iloc[
            :i + 1
        ].copy()

        liquidity_report = generate_liquidity_report_v2(
            partial_df,
            lookback=liquidity_lookback,
            tolerance_pct=tolerance_pct,
            min_touches=min_touches
        )

        signal_report = {
            "signal": signal
        }

        liquidity_filter = evaluate_liquidity_filter(
            signal_report,
            liquidity_report,
            max_distance_pct=max_distance_pct
        )

        if liquidity_filter["adjusted_signal"] == "WAIT":
            continue

        result = simulate_trade_with_atr(
            df=df,
            entry_index=i,
            direction=signal,
            atr_value=row["atr"],
            sl_multiplier=sl_multiplier,
            tp_multiplier=tp_multiplier,
            max_bars=max_bars
        )

        if result is None:
            continue

        trades.append({
            "timestamp": row["timestamp"],
            "direction": signal,
            "liquidity_filter": liquidity_filter["liquidity_filter"],
            "liquidity_comment": liquidity_filter["comment"],
            "result": result["result"],
            "exit_reason": result["exit_reason"],
            "result_pct": result["result_pct"]
        })

    performance = generate_performance_report(
        trades
    )

    return {
        "trades": trades,
        "performance": performance
    }
