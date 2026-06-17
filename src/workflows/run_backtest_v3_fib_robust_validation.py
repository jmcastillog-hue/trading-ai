from pathlib import Path
import pandas as pd

from src.backtesting.backtesting_engine_v3 import (
    BacktestConfig,
    run_backtest_v3,
)

from src.strategies.fib_v5_strategy import fib_v5_short_signal


def best_fib_v5_strategy(df, index, config):
    """
    Configuración candidata FIB V5 encontrada en Fase 1.1.

    Importante:
    No se optimiza aquí. Solo se valida la misma configuración
    sobre más datos y por bloques.
    """

    return fib_v5_short_signal(
        df=df,
        index=index,
        config=config,
        lookback_bars=48,
        fib_entry_low=0.618,
        fib_entry_high=0.786,
        min_impulse_pct=0.02,
        require_bearish_confirmation=True,
        require_rejection_wick=False,
    )


def run_single_validation(csv_path: Path, label: str) -> dict:
    config = BacktestConfig(
        initial_capital=1000.0,
        risk_per_trade=0.01,
        risk_reward=2.5,
        fee_rate=0.001,
        spread_rate=0.0002,
        atr_period=14,
        atr_multiplier=1.25,
        max_holding_bars=48,
        direction_mode="short_only",
    )

    trades_df, summary = run_backtest_v3(
        csv_path=csv_path,
        config=config,
        output_dir=Path("reports"),
        strategy_func=best_fib_v5_strategy,
    )

    return {
        "label": label,
        "csv_path": str(csv_path),
        "total_trades": summary.get("total_trades", 0),
        "ending_capital": summary.get("ending_capital", 1000.0),
        "total_return_pct": summary.get("total_return_pct", 0.0),
        "win_rate": summary.get("win_rate", 0.0),
        "profit_factor": summary.get("profit_factor", None),
        "expectancy": summary.get("expectancy", 0.0),
        "max_drawdown_pct": summary.get("max_drawdown_pct", 0.0),
    }


def split_csv_into_chunks(
    source_csv: Path,
    chunk_size: int = 1000,
    output_prefix: str = "reports/validation_chunk",
) -> list[Path]:
    df = pd.read_csv(source_csv)

    chunk_paths = []

    total_rows = len(df)
    chunk_number = 0

    for start in range(0, total_rows, chunk_size):
        end = start + chunk_size
        chunk = df.iloc[start:end].copy()

        if len(chunk) < chunk_size:
            continue

        chunk_number += 1
        chunk_path = Path(f"{output_prefix}_{chunk_number}.csv")
        chunk.to_csv(chunk_path, index=False)
        chunk_paths.append(chunk_path)

    return chunk_paths


def main():
    validation_csv = Path("data") / "btcusdt_15m_validation.csv"

    if not validation_csv.exists():
        raise FileNotFoundError(
            "No existe data/btcusdt_15m_validation.csv. "
            "Primero ejecuta: python -m src.exchange.binance_historical_downloader"
        )

    results = []

    print("VALIDACIÓN ROBUSTA FIB V5")
    print("=" * 50)
    print(f"Archivo base: {validation_csv}")
    print()

    full_result = run_single_validation(
        csv_path=validation_csv,
        label="FULL_DATASET_5000_CANDLES",
    )

    results.append(full_result)

    print("Resultado dataset completo:")
    print(full_result)
    print()

    chunk_paths = split_csv_into_chunks(
        source_csv=validation_csv,
        chunk_size=1000,
        output_prefix="reports/validation_chunk",
    )

    for idx, chunk_path in enumerate(chunk_paths, start=1):
        label = f"CHUNK_{idx}_1000_CANDLES"

        result = run_single_validation(
            csv_path=chunk_path,
            label=label,
        )

        results.append(result)

        print(f"Resultado {label}:")
        print(result)
        print()

    results_df = pd.DataFrame(results)

    output_path = Path("reports") / "backtest_v3_fib_robust_validation.csv"
    results_df.to_csv(output_path, index=False)

    print("RESUMEN VALIDACIÓN ROBUSTA")
    print("=" * 50)
    print(
        results_df[
            [
                "label",
                "total_trades",
                "ending_capital",
                "total_return_pct",
                "win_rate",
                "profit_factor",
                "expectancy",
                "max_drawdown_pct",
            ]
        ].to_string(index=False)
    )

    print()
    print(f"Archivo generado: {output_path}")


if __name__ == "__main__":
    main()
    