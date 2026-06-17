from dataclasses import dataclass
from pathlib import Path
import json
import pandas as pd
import numpy as np


@dataclass
class BacktestConfig:
    initial_capital: float = 1000.0
    risk_per_trade: float = 0.01
    risk_reward: float = 2.0
    fee_rate: float = 0.001
    spread_rate: float = 0.0002
    atr_period: int = 14
    atr_multiplier: float = 1.5
    max_holding_bars: int = 48
    direction_mode: str = "both"  # both, long_only, short_only


def normalize_ohlcv_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza nombres de columnas comunes para trabajar con datos OHLCV.
    Espera columnas equivalentes a:
    timestamp/open_time/date, open, high, low, close, volume.
    """

    df = df.copy()
    df.columns = [str(col).strip().lower() for col in df.columns]

    rename_map = {
        "open time": "timestamp",
        "open_time": "timestamp",
        "time": "timestamp",
        "date": "timestamp",
        "datetime": "timestamp",
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
        "volume": "volume",
    }

    df = df.rename(columns={col: rename_map.get(col, col) for col in df.columns})

    required = ["open", "high", "low", "close"]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Faltan columnas obligatorias en el CSV: {missing}")

    for col in required:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if "volume" in df.columns:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    df = df.dropna(subset=required).reset_index(drop=True)

    return df


def add_indicators(df: pd.DataFrame, atr_period: int = 14) -> pd.DataFrame:
    """
    Agrega EMA20, EMA50, EMA200 y ATR.
    """

    df = df.copy()

    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    df["ema200"] = df["close"].ewm(span=200, adjust=False).mean()

    high_low = df["high"] - df["low"]
    high_close_prev = (df["high"] - df["close"].shift(1)).abs()
    low_close_prev = (df["low"] - df["close"].shift(1)).abs()

    true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
    df["atr"] = true_range.rolling(window=atr_period).mean()

    return df


def generate_basic_signal(row: pd.Series, direction_mode: str = "both") -> str:
    """
    Señal base temporal para probar el Backtesting Engine V3.

    Esta señal NO es la estrategia final.
    Solo sirve para validar el motor con reglas simples.
    """

    bullish_trend = row["ema20"] > row["ema50"] > row["ema200"]
    bearish_trend = row["ema20"] < row["ema50"] < row["ema200"]

    if direction_mode in ["both", "long_only"]:
        if bullish_trend and row["close"] > row["ema20"]:
            return "LONG"

    if direction_mode in ["both", "short_only"]:
        if bearish_trend and row["close"] < row["ema20"]:
            return "SHORT"

    return "NONE"


def calculate_max_drawdown(equity_curve: list[float]) -> float:
    """
    Calcula el máximo drawdown porcentual.
    """

    if not equity_curve:
        return 0.0

    equity = np.array(equity_curve, dtype=float)
    peaks = np.maximum.accumulate(equity)
    drawdowns = (equity - peaks) / peaks

    return float(drawdowns.min())


def simulate_trade(
    df: pd.DataFrame,
    entry_index: int,
    direction: str,
    capital: float,
    config: BacktestConfig,
) -> dict:
    """
    Simula una operación con entrada, SL, TP, fees, spread y salida.
    """

    entry_row = df.iloc[entry_index]

    raw_entry = float(entry_row["close"])
    atr = float(entry_row["atr"])

    if atr <= 0 or np.isnan(atr):
        return {}

    half_spread = config.spread_rate / 2

    if direction == "LONG":
        entry_price = raw_entry * (1 + half_spread)
        stop_loss = entry_price - (atr * config.atr_multiplier)
        take_profit = entry_price + ((entry_price - stop_loss) * config.risk_reward)
        risk_per_unit = entry_price - stop_loss

    elif direction == "SHORT":
        entry_price = raw_entry * (1 - half_spread)
        stop_loss = entry_price + (atr * config.atr_multiplier)
        take_profit = entry_price - ((stop_loss - entry_price) * config.risk_reward)
        risk_per_unit = stop_loss - entry_price

    else:
        return {}

    if risk_per_unit <= 0:
        return {}

    risk_amount = capital * config.risk_per_trade
    quantity = risk_amount / risk_per_unit

    max_exit_index = min(entry_index + config.max_holding_bars, len(df) - 1)

    exit_price = None
    exit_index = None
    exit_reason = None

    for i in range(entry_index + 1, max_exit_index + 1):
        row = df.iloc[i]
        high = float(row["high"])
        low = float(row["low"])
        close = float(row["close"])

        if direction == "LONG":
            hit_stop = low <= stop_loss
            hit_take = high >= take_profit

            # Caso conservador: si SL y TP ocurren en la misma vela, asumimos SL primero.
            if hit_stop:
                exit_price = stop_loss * (1 - half_spread)
                exit_index = i
                exit_reason = "STOP_LOSS"
                break

            if hit_take:
                exit_price = take_profit * (1 - half_spread)
                exit_index = i
                exit_reason = "TAKE_PROFIT"
                break

        if direction == "SHORT":
            hit_stop = high >= stop_loss
            hit_take = low <= take_profit

            # Caso conservador: si SL y TP ocurren en la misma vela, asumimos SL primero.
            if hit_stop:
                exit_price = stop_loss * (1 + half_spread)
                exit_index = i
                exit_reason = "STOP_LOSS"
                break

            if hit_take:
                exit_price = take_profit * (1 + half_spread)
                exit_index = i
                exit_reason = "TAKE_PROFIT"
                break

        if i == max_exit_index:
            if direction == "LONG":
                exit_price = close * (1 - half_spread)
            else:
                exit_price = close * (1 + half_spread)

            exit_index = i
            exit_reason = "MAX_HOLDING_EXIT"

    if exit_price is None:
        return {}

    if direction == "LONG":
        gross_pnl = (exit_price - entry_price) * quantity
    else:
        gross_pnl = (entry_price - exit_price) * quantity

    entry_fee = entry_price * quantity * config.fee_rate
    exit_fee = exit_price * quantity * config.fee_rate
    total_fees = entry_fee + exit_fee

    net_pnl = gross_pnl - total_fees
    return_pct = net_pnl / capital

    return {
        "entry_index": entry_index,
        "exit_index": exit_index,
        "direction": direction,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "exit_price": exit_price,
        "exit_reason": exit_reason,
        "quantity": quantity,
        "gross_pnl": gross_pnl,
        "fees": total_fees,
        "net_pnl": net_pnl,
        "return_pct": return_pct,
        "risk_amount": risk_amount,
        "risk_reward": config.risk_reward,
        "holding_bars": exit_index - entry_index,
    }


def run_backtest_v3(
    csv_path: str | Path,
    config: BacktestConfig | None = None,
    output_dir: str | Path = "reports",
    strategy_func=None,
) -> tuple[pd.DataFrame, dict]:
    """
    Ejecuta Backtesting Engine V3 sobre un archivo CSV OHLCV.
    """

    if config is None:
        config = BacktestConfig()

    csv_path = Path(csv_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not csv_path.exists():
        raise FileNotFoundError(f"No existe el archivo de datos: {csv_path}")

    df = pd.read_csv(csv_path)
    df = normalize_ohlcv_columns(df)
    df = add_indicators(df, atr_period=config.atr_period)

    capital = config.initial_capital
    equity_curve = [capital]
    trades = []

    i = 200

    while i < len(df) - config.max_holding_bars:
        row = df.iloc[i]

        if pd.isna(row["atr"]):
            i += 1
            continue

        signal = generate_basic_signal(row, direction_mode=config.direction_mode)

        if strategy_func is not None:
            signal = strategy_func(df, i, config)
        else:
            signal = generate_basic_signal(row, direction_mode=config.direction_mode)

        trade = simulate_trade(
            df=df,
            entry_index=i,
            direction=signal,
            capital=capital,
            config=config,
        )

        if not trade:
            i += 1
            continue

        capital += trade["net_pnl"]
        equity_curve.append(capital)

        trade["capital_after_trade"] = capital

        if "timestamp" in df.columns:
            trade["entry_time"] = df.iloc[trade["entry_index"]]["timestamp"]
            trade["exit_time"] = df.iloc[trade["exit_index"]]["timestamp"]

        trades.append(trade)

        # Evita operaciones superpuestas.
        i = trade["exit_index"] + 1

    trades_df = pd.DataFrame(trades)
    summary = build_summary(trades_df, equity_curve, config)

    trades_path = output_dir / "backtest_v3_trades.csv"
    summary_json_path = output_dir / "backtest_v3_summary.json"
    summary_txt_path = output_dir / "backtest_v3_summary.txt"

    trades_df.to_csv(trades_path, index=False)

    with open(summary_json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4, ensure_ascii=False)

    with open(summary_txt_path, "w", encoding="utf-8") as f:
        f.write(format_summary_text(summary))

    return trades_df, summary


def build_summary(
    trades_df: pd.DataFrame,
    equity_curve: list[float],
    config: BacktestConfig,
) -> dict:
    """
    Construye resumen estadístico del backtest.
    """

    total_trades = len(trades_df)

    if total_trades == 0:
        return {
            "total_trades": 0,
            "message": "No se detectaron operaciones.",
            "initial_capital": config.initial_capital,
            "ending_capital": config.initial_capital,
        }

    wins = trades_df[trades_df["net_pnl"] > 0]
    losses = trades_df[trades_df["net_pnl"] <= 0]

    gross_profit = float(wins["net_pnl"].sum()) if not wins.empty else 0.0
    gross_loss = float(losses["net_pnl"].sum()) if not losses.empty else 0.0

    if gross_loss < 0:
        profit_factor = gross_profit / abs(gross_loss)
    else:
        profit_factor = None

    ending_capital = float(equity_curve[-1])
    total_return_pct = (ending_capital - config.initial_capital) / config.initial_capital

    summary = {
        "initial_capital": config.initial_capital,
        "ending_capital": ending_capital,
        "total_return_pct": total_return_pct,
        "total_trades": total_trades,
        "wins": int(len(wins)),
        "losses": int(len(losses)),
        "win_rate": float(len(wins) / total_trades),
        "gross_profit": gross_profit,
        "gross_loss": gross_loss,
        "profit_factor": profit_factor,
        "expectancy": float(trades_df["net_pnl"].mean()),
        "average_win": float(wins["net_pnl"].mean()) if not wins.empty else 0.0,
        "average_loss": float(losses["net_pnl"].mean()) if not losses.empty else 0.0,
        "max_drawdown_pct": calculate_max_drawdown(equity_curve),
        "risk_per_trade": config.risk_per_trade,
        "risk_reward": config.risk_reward,
        "fee_rate": config.fee_rate,
        "spread_rate": config.spread_rate,
        "atr_multiplier": config.atr_multiplier,
        "max_holding_bars": config.max_holding_bars,
        "direction_mode": config.direction_mode,
    }

    return summary


def format_summary_text(summary: dict) -> str:
    """
    Formatea resumen en texto legible.
    """

    if summary.get("total_trades", 0) == 0:
        return "BACKTEST V3\n\nNo se detectaron operaciones.\n"

    lines = [
        "BACKTEST V3 SUMMARY",
        "",
        f"Initial capital: {summary['initial_capital']:.2f}",
        f"Ending capital: {summary['ending_capital']:.2f}",
        f"Total return: {summary['total_return_pct']:.2%}",
        "",
        f"Total trades: {summary['total_trades']}",
        f"Wins: {summary['wins']}",
        f"Losses: {summary['losses']}",
        f"Win rate: {summary['win_rate']:.2%}",
        "",
        f"Gross profit: {summary['gross_profit']:.2f}",
        f"Gross loss: {summary['gross_loss']:.2f}",
        f"Profit factor: {summary['profit_factor']}",
        f"Expectancy: {summary['expectancy']:.4f}",
        f"Average win: {summary['average_win']:.4f}",
        f"Average loss: {summary['average_loss']:.4f}",
        f"Max drawdown: {summary['max_drawdown_pct']:.2%}",
        "",
        "CONFIG",
        f"Risk per trade: {summary['risk_per_trade']:.2%}",
        f"Risk reward: {summary['risk_reward']}",
        f"Fee rate: {summary['fee_rate']:.4%}",
        f"Spread rate: {summary['spread_rate']:.4%}",
        f"ATR multiplier: {summary['atr_multiplier']}",
        f"Max holding bars: {summary['max_holding_bars']}",
        f"Direction mode: {summary['direction_mode']}",
    ]

    return "\n".join(lines)


if __name__ == "__main__":
    default_csv = Path("data") / "btcusdt_15m.csv"
    trades, summary = run_backtest_v3(default_csv)
    print(format_summary_text(summary))