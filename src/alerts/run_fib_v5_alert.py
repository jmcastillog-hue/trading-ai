import os
import sys

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            ".."
        )
    )
)

from src.quantitative.data_loader import (
    load_csv,
    validate_data,
    clean_data
)

from src.alerts.fib_v5_alert_engine import (
    generate_fib_v5_alert
)


def load_market_data(path):

    df = load_csv(path)

    validate_data(df)

    df = clean_data(df)

    return df


def print_alert(alert):

    print("\n=== FIB V5 ALERT ENGINE ===\n")

    print(
        f"setup_active: {alert.get('setup_active')}"
    )

    print(
        f"state: {alert.get('state')}"
    )

    print(
        f"bias: {alert.get('bias')}"
    )

    print(
        f"current_price: {alert.get('current_price')}"
    )

    print(
        f"comment: {alert.get('comment')}"
    )

    if not alert.get("setup_active"):

        return

    impulse = alert["impulse"]

    print("\n--- IMPULSO 4H ---")

    print(
        f"high_timestamp: {impulse['high_timestamp']}"
    )

    print(
        f"high_price: {impulse['high_price']:.2f}"
    )

    print(
        f"low_timestamp: {impulse['low_timestamp']}"
    )

    print(
        f"low_price: {impulse['low_price']:.2f}"
    )

    print(
        f"drop_pct: {impulse['drop_pct']:.2f}%"
    )

    print("\n--- ZONA Y NIVELES ---")

    print(
        f"entry_zone_low 0.236: {alert['entry_zone_low']:.2f}"
    )

    print(
        f"entry_zone_high 0.382: {alert['entry_zone_high']:.2f}"
    )

    print(
        f"stop 0.618: {alert['stop_price']:.2f}"
    )

    print(
        f"target impulse low: {alert['target_price']:.2f}"
    )

    print("\n--- ENTRADA ---")

    print(
        f"entry_signal: {alert['entry_signal']}"
    )

    entry = alert.get(
        "entry"
    )

    if entry:

        print(
            f"entry_time_checked: {entry['entry_time']}"
        )

        print(
            f"entry_candle_open: {entry['candle_open']:.2f}"
        )

        print(
            f"entry_candle_high: {entry['candle_high']:.2f}"
        )

        print(
            f"entry_candle_low: {entry['candle_low']:.2f}"
        )

        print(
            f"entry_candle_close: {entry['candle_close']:.2f}"
        )

        print(
            f"entry_comment: {entry['comment']}"
        )

    if alert["entry_signal"]:

        print("\n--- PLAN V5 ---")

        print(
            f"entry_price: {alert['entry_price']:.2f}"
        )

        print(
            f"tp1_price: {alert['tp1_price']:.2f}"
        )

        print(
            f"close_at_tp1: {alert['tp1_close_weight'] * 100:.0f}%"
        )

        print(
            f"move_remaining_to: BREAKEVEN"
        )

        print(
            f"tp2_price: {alert['target_price']:.2f}"
        )


def main():

    htf_df = load_market_data(
        "data/btcusdt_4h_history.csv"
    )

    ltf_df = load_market_data(
        "data/btcusdt_30m_history.csv"
    )

    alert = generate_fib_v5_alert(
        htf_df=htf_df,
        ltf_df=ltf_df,
        min_drop_pct=5.0,
        max_impulse_bars=80,
        lookback_bars=300,
        entry_zone_low_ratio="0.236",
        entry_zone_high_ratio="0.382",
        invalidation_ratio="0.618",
        tp1_ratio=0.40,
        tp1_close_weight=0.50,
        left_bars=2,
        right_bars=2,
        use_last_closed_candle=True
    )

    print_alert(
        alert
    )


if __name__ == "__main__":
    main()