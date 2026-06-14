import os
import json
from datetime import datetime

import pandas as pd


HISTORY_FILE = "reports/fib_v5_cycle_history.csv"

ALERT_JSON = "reports/fib_v5_live_alert_report.json"
DECISION_JSON = "reports/fib_v5_decision_report.json"
PAPER_TRADES_CSV = "reports/paper_trades.csv"


def now_string():

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def safe_float(
    value,
    default=0.0
):

    try:
        return float(value)

    except Exception:
        return default


def load_json(
    path
):

    if not os.path.exists(path):
        return {}

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def load_paper_summary():

    if not os.path.exists(
        PAPER_TRADES_CSV
    ):

        return {
            "total_trades": 0,
            "open_trades": 0,
            "closed_trades": 0
        }

    df = pd.read_csv(
        PAPER_TRADES_CSV
    )

    if len(df) == 0 or "status" not in df.columns:

        return {
            "total_trades": len(df),
            "open_trades": 0,
            "closed_trades": len(df)
        }

    open_statuses = [
        "OPEN",
        "TP1_HIT_BE_ACTIVE"
    ]

    open_df = df[
        df["status"].isin(
            open_statuses
        )
    ]

    closed_df = df[
        ~df["status"].isin(
            open_statuses
        )
    ]

    return {
        "total_trades": len(df),
        "open_trades": len(open_df),
        "closed_trades": len(closed_df)
    }


def build_history_row():

    alert = load_json(
        ALERT_JSON
    )

    decision_payload = load_json(
        DECISION_JSON
    )

    decision = decision_payload.get(
        "decision",
        {}
    )

    risk = decision_payload.get(
        "risk_report",
        {}
    )

    impulse = alert.get(
        "impulse",
        {}
    )

    paper_summary = load_paper_summary()

    return {
        "logged_at": now_string(),
        "symbol": alert.get("symbol", "BTCUSDT"),
        "setup_active": alert.get("setup_active"),
        "alert_state": alert.get("state"),
        "bias": alert.get("bias"),
        "entry_signal": alert.get("entry_signal"),
        "current_price": safe_float(
            alert.get("current_price")
        ),
        "entry_price": safe_float(
            alert.get("entry_price")
        ),
        "entry_zone_low": safe_float(
            alert.get("entry_zone_low")
        ),
        "entry_zone_high": safe_float(
            alert.get("entry_zone_high")
        ),
        "stop_price": safe_float(
            alert.get("stop_price")
        ),
        "tp1_price": safe_float(
            alert.get("tp1_price")
        ),
        "tp2_price": safe_float(
            alert.get("target_price")
        ),
        "impulse_high": safe_float(
            impulse.get("high_price")
        ),
        "impulse_low": safe_float(
            impulse.get("low_price")
        ),
        "drop_pct": safe_float(
            impulse.get("drop_pct")
        ),
        "decision": decision.get("decision"),
        "permission": decision.get("permission"),
        "risk_check": risk.get("risk_check"),
        "stop_distance_pct": safe_float(
            risk.get("stop_distance_pct")
        ),
        "position_notional": safe_float(
            risk.get("position_notional")
        ),
        "total_paper_trades": paper_summary["total_trades"],
        "open_paper_trades": paper_summary["open_trades"],
        "closed_paper_trades": paper_summary["closed_trades"]
    }


def append_cycle_history():

    row = build_history_row()

    os.makedirs(
        "reports",
        exist_ok=True
    )

    new_df = pd.DataFrame(
        [row]
    )

    if os.path.exists(
        HISTORY_FILE
    ):

        old_df = pd.read_csv(
            HISTORY_FILE
        )

        df = pd.concat(
            [
                old_df,
                new_df
            ],
            ignore_index=True
        )

    else:

        df = new_df

    try:

        df.to_csv(
            HISTORY_FILE,
            index=False
        )

        saved_file = HISTORY_FILE

    except PermissionError:

        fallback_file = (
            "reports/fib_v5_cycle_history_backup_"
            + datetime.now().strftime("%Y%m%d_%H%M%S")
            + ".csv"
        )

        df.to_csv(
            fallback_file,
            index=False
        )

        saved_file = fallback_file

    return row, len(df), saved_file


def main():

    row, total_rows, saved_file = append_cycle_history()

    print(
        "\n=== FIB V5 CYCLE HISTORY LOGGER ===\n"
    )

    print(
        f"logged_at: {row['logged_at']}"
    )

    print(
        f"alert_state: {row['alert_state']}"
    )

    print(
        f"entry_signal: {row['entry_signal']}"
    )

    print(
        f"decision: {row['decision']}"
    )

    print(
        f"current_price: {row['current_price']:.2f}"
    )

    print(
        f"open_paper_trades: {row['open_paper_trades']}"
    )

    print(
        f"history_file: {saved_file}"
    )

    print(
        f"total_history_rows: {total_rows}"
    )

    if saved_file != HISTORY_FILE:

        print(
            "\nAdvertencia: el archivo principal estaba bloqueado. Se guardó una copia alternativa."
        )

if __name__ == "__main__":
    main()