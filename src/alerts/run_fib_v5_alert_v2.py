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

from src.alerts.fib_v5_alert_engine_v2 import (
    generate_fib_v5_alert_v2
)


def load_market_data(path):

    df = load_csv(path)

    validate_data(df)

    df = clean_data(df)

    return df


def print_candidate_summary(candidate, index):

    impulse = candidate["impulse"]

    print(
        f"\n--- CANDIDATO #{index} ---"
    )

    print(
        f"state: {candidate['state']}"
    )

    print(
        f"active: {candidate['setup_active']}"
    )

    print(
        f"entry_signal: {candidate['entry_signal']}"
    )

    print(
        f"impulse_high: {impulse['high_price']:.2f}"
    )

    print(
        f"impulse_low: {impulse['low_price']:.2f}"
    )

    print(
        f"drop_pct: {impulse['drop_pct']:.2f}%"
    )

    print(
        f"zone: {candidate['entry_zone_low']:.2f} - {candidate['entry_zone_high']:.2f}"
    )

    print(
        f"stop: {candidate['stop_price']:.2f}"
    )

    print(
        f"target: {candidate['target_price']:.2f}"
    )

    print(
        f"distance_to_zone_pct: {candidate['distance_to_zone_pct']:.2f}"
    )


def print_alert(alert):

    print("\n=== FIB V5 ALERT ENGINE V2 ===\n")

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

    candidates = alert.get(
        "candidates",
        []
    )

    print(
        f"\ncandidates_scanned: {len(candidates)}"
    )

    for index, candidate in enumerate(
        candidates,
        start=1
    ):

        print_candidate_summary(
            candidate,
            index
        )

    if not alert.get("setup_active"):

        return

    print("\n=== MEJOR SETUP ACTIVO ===")

    print(
        f"state: {alert['state']}"
    )

    print(
        f"entry_zone_low: {alert['entry_zone_low']:.2f}"
    )

    print(
        f"entry_zone_high: {alert['entry_zone_high']:.2f}"
    )

    print(
        f"stop_price: {alert['stop_price']:.2f}"
    )

    print(
        f"target_price: {alert['target_price']:.2f}"
    )

    print(
        f"entry_signal: {alert['entry_signal']}"
    )

    if alert["entry_signal"]:

        print("\n--- PLAN OPERATIVO V5 ---")

        print(
            f"entry_price: {alert['entry_price']:.2f}"
        )

        print(
            f"tp1_price: {alert['tp1_price']:.2f}"
        )

        print(
            f"cerrar_en_tp1: {alert['tp1_close_weight'] * 100:.0f}%"
        )

        print(
            "mover_restante_a: BREAKEVEN"
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

    alert = generate_fib_v5_alert_v2(
        htf_df=htf_df,
        ltf_df=ltf_df,
        min_drop_pct=5.0,
        max_impulse_bars=80,
        lookback_bars=300,
        max_candidates=5,
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