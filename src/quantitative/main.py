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

from backtesting.fib_scenario_backtester import (
    run_fib_short_scenario_backtest
)

from backtesting.sweep_bos_backtester_v2 import (
    run_sweep_bos_backtest_v2
)

from backtesting.sweep_bos_backtester import (
    run_sweep_bos_backtest
)

from structure.market_structure import (
    generate_market_structure_report
)

from signals.liquidity_filter import (
    evaluate_liquidity_filter
)

from liquidity.liquidity_engine import (
    calculate_liquidity_zones,
    classify_liquidity_context,
    generate_liquidity_report_v2
)

from liquidity.liquidity_engine import (
    calculate_liquidity_zones,
    classify_liquidity_context
)

from backtesting.strategy_tester import (
    run_backtest,
    run_atr_backtest,
    run_atr_backtest_with_liquidity_filter
)

from utils.file_writer import (
    save_report
)

from signals.signal_engine import (
    generate_signal
)

from agents.analyst_agent import (
    generate_analysis
)

from indicators.indicator_engine import (
    generate_indicator_report
)

from data_loader import (
    load_csv,
    validate_data,
    clean_data
)

from statistics import (
    calculate_returns,
    calculate_volatility,
    average_range
)

from probability_engine import (
    generate_probability_report
)

from config import (
    DATA_FILE,
    ASSET,
    TIMEFRAME
)


def main():

    print("\n=== AGENTE CUANTITATIVO V2 ===\n")

    df = load_csv(DATA_FILE)

    validate_data(df)

    df = clean_data(df)

    returns = calculate_returns(df)

    volatility = calculate_volatility(df)

    avg_range = average_range(df)

    probability_report = generate_probability_report(df)

    indicator_report = (
    generate_indicator_report(df)
    )

    signal_report = generate_signal(
    probability_report,
    indicator_report
    )

    liquidity_report = calculate_liquidity_zones(
        df,
        lookback=96
    )

    liquidity_report_v2 = generate_liquidity_report_v2(
        df,
        lookback=96,
        tolerance_pct=0.15,
        min_touches=2
    )

    liquidity_filter_report = evaluate_liquidity_filter(
        signal_report,
        liquidity_report_v2,
        max_distance_pct=1.0
    )

    market_structure_report = (
        generate_market_structure_report(
            df,
            left_bars=2,
            right_bars=2
        )
    )

    liquidity_context = classify_liquidity_context(
        liquidity_report
    )


    analysis_text = generate_analysis(
    ASSET,
    TIMEFRAME,
    probability_report,
    indicator_report,
    signal_report
    )

    holding_periods = [1, 2, 3, 4, 8]

    backtest_reports = {}

    for period in holding_periods:

        backtest_reports[period] = run_backtest(
            df,
            holding_period=period
        )
    
    atr_backtest_report = run_atr_backtest(
        df,
        sl_multiplier=1,
        tp_multiplier=2,
        max_bars=8
    )

    atr_liquidity_backtest_report = (
        run_atr_backtest_with_liquidity_filter(
            df,
            sl_multiplier=1,
            tp_multiplier=2,
            max_bars=8,
            liquidity_lookback=96,
            tolerance_pct=0.15,
            min_touches=2,
            max_distance_pct=1.0
        )
    )

    sweep_bos_backtest_report = run_sweep_bos_backtest(
        df,
        sl_multiplier=1,
        tp_multiplier=2,
        max_bars=8,
        structure_lookback=120,
        left_bars=2,
        right_bars=2
    )

    sweep_bos_backtest_v2_report = (
        run_sweep_bos_backtest_v2(
            df,
            sl_multiplier=1,
            tp_multiplier=2,
            max_bars=8,
            structure_lookback=120,
            sweep_lookback=50,
            lookahead_bos=10,
            left_bars=2,
            right_bars=2
        )
    )

    fib_scenario_backtest_report = (
        run_fib_short_scenario_backtest(
            df,
            min_drop_pct=2,
            max_impulse_bars=120,
            max_wait_bars=80,
            max_trade_bars=80,
            entry_zone_low_ratio="0.236",
            entry_zone_high_ratio="0.382",
            invalidation_ratio="0.618",
            left_bars=2,
            right_bars=2
        )
    )

    print(f"Activo: {ASSET}")
    print(f"Timeframe: {TIMEFRAME}")

    print(
        f"\nRetornos analizados: {len(returns)}"
    )

    print(
        f"Volatilidad: {volatility:.4f}"
    )

    print(
        f"Rango promedio: {avg_range:.4f}"
    )

    print("\n=== PROBABILITY ENGINE V2 ===\n")

    for key, value in probability_report.items():

        if isinstance(value, float):

            print(
                f"{key}: {value:.2f}"
            )

        else:

            print(
                f"{key}: {value}"
            )

    print("\n=== INDICATOR ENGINE V1 ===\n")

    for key, value in indicator_report.items():

        print(
        f"{key}: {value:.2f}"
        )

    print("\n=== SIGNAL ENGINE V1 ===\n")

    for key, value in signal_report.items():

        print(
            f"{key}: {value}"
        )

    print("\n")
    print(analysis_text)

    report_path = save_report(
    analysis_text,
    "reports/quantitative_analysis.txt"
    )

    print(
        f"\nReporte guardado: {report_path}"
    )

    print("\n=== BACKTESTING ENGINE V2 ===\n")

    for period, report in backtest_reports.items():

        print(
            f"\n--- Holding Period: {period} vela(s) ---"
        )

        for key, value in report["performance"].items():

            if isinstance(value, float):

                print(
                    f"{key}: {value:.2f}"
                )

            else:

                print(
                    f"{key}: {value}"
                )
    

    print("\n=== LIQUIDITY ENGINE V1 ===\n")

    for key, value in liquidity_report.items():

        if isinstance(value, float):

            print(
                f"{key}: {value:.2f}"
            )

        else:

            print(
                f"{key}: {value}"
            )

    print(
        f"liquidity_context: {liquidity_context}"
    )

    print("\n=== TRADE SIMULATOR V1 ATR ===\n")

    for key, value in atr_backtest_report["performance"].items():

        if isinstance(value, float):

            print(
                f"{key}: {value:.2f}"
            )

        else:

            print(
                f"{key}: {value}"
            )

    print("\n=== LIQUIDITY ENGINE V2 ===\n")

    print("Buy Side Liquidity:")

    print(
        liquidity_report_v2["buy_side_liquidity"]
    )

    print("\nSell Side Liquidity:")

    print(
        liquidity_report_v2["sell_side_liquidity"]
    )

    print("\nEqual Highs:")

    for level in liquidity_report_v2["equal_highs"]:

        print(
            f"level: {level['level']:.2f} | touches: {level['touches']}"
        )

    print("\nEqual Lows:")

    for level in liquidity_report_v2["equal_lows"]:

        print(
            f"level: {level['level']:.2f} | touches: {level['touches']}"
        )

    print("\n=== LIQUIDITY FILTER V1 ===\n")

    for key, value in liquidity_filter_report.items():

        print(
            f"{key}: {value}"
        )

    print("\n=== BACKTESTING ENGINE V3 ATR + LIQUIDITY ===\n")

    for key, value in atr_liquidity_backtest_report["performance"].items():

        if isinstance(value, float):

            print(
                f"{key}: {value:.2f}"
            )

        else:

            print(
                f"{key}: {value}"
            )

    print("\n=== MARKET STRUCTURE ENGINE V1 ===\n")

    for key, value in market_structure_report.items():

        print(
            f"{key}: {value}"
        )

    print("\n=== SWEEP + BOS BACKTEST V1 ===\n")

    for key, value in sweep_bos_backtest_report["performance"].items():

        if isinstance(value, float):

            print(
                f"{key}: {value:.2f}"
            )

        else:

            print(
                f"{key}: {value}"
            )

    print("\n=== SWEEP + BOS BACKTEST V2 ===\n")

    for key, value in sweep_bos_backtest_v2_report["performance"].items():

        if isinstance(value, float):

            print(
                f"{key}: {value:.2f}"
            )

        else:

            print(
                f"{key}: {value}"
            )

    print("\n=== FIB SHORT SCENARIO BACKTEST V1 ===\n")

    for key, value in fib_scenario_backtest_report["performance"].items():

        if isinstance(value, float):

            print(
                f"{key}: {value:.2f}"
            )

        else:

            print(
                f"{key}: {value}"
            )

if __name__ == "__main__":
    main()