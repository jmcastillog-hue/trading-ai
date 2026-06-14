import os
import json
import hashlib
from datetime import datetime

import pandas as pd


PAPER_TRADES_FILE = "reports/paper_trades.csv"


ALLOWED_DECISIONS = [
    "PAPER_TRADE_ONLY",
    "TRADE_CANDIDATE",
    "SMALL_SIZE_ONLY"
]


OPEN_STATUSES = [
    "OPEN",
    "TP1_HIT_BE_ACTIVE"
]


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


def short_result_pct(
    entry_price,
    exit_price
):

    return (
        (entry_price - exit_price)
        / entry_price
    ) * 100


def generate_trade_id(
    symbol,
    strategy,
    entry_time,
    entry_price,
    stop_price,
    target_price
):

    raw = (
        f"{symbol}|{strategy}|{entry_time}|"
        f"{entry_price}|{stop_price}|{target_price}"
    )

    return hashlib.md5(
        raw.encode("utf-8")
    ).hexdigest()


def load_paper_trades(
    path=PAPER_TRADES_FILE
):

    if not os.path.exists(path):

        return pd.DataFrame()

    return pd.read_csv(path)


def save_paper_trades(
    df,
    path=PAPER_TRADES_FILE
):

    os.makedirs(
        os.path.dirname(path),
        exist_ok=True
    )

    df.to_csv(
        path,
        index=False
    )


def load_decision_payload(
    path
):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)

def setup_key_from_values(
    symbol,
    strategy,
    direction,
    impulse_high,
    impulse_low,
    stop_price,
    tp2_price
):

    return (
        f"{symbol}|{strategy}|{direction}|"
        f"{round(safe_float(impulse_high), 2)}|"
        f"{round(safe_float(impulse_low), 2)}|"
        f"{round(safe_float(stop_price), 2)}|"
        f"{round(safe_float(tp2_price), 2)}"
    )


def setup_key_from_record(
    record
):

    return setup_key_from_values(
        symbol=record.get("symbol", ""),
        strategy=record.get("strategy", ""),
        direction=record.get("direction", ""),
        impulse_high=record.get("impulse_high", 0),
        impulse_low=record.get("impulse_low", 0),
        stop_price=record.get("stop_price", 0),
        tp2_price=record.get("tp2_price", 0)
    )


def open_trade_exists_for_same_setup(
    df,
    trade_record
):

    if len(df) == 0:
        return False

    new_setup_key = setup_key_from_record(
        trade_record
    )

    for _, row in df.iterrows():

        row_dict = row.to_dict()

        status = row_dict.get(
            "status",
            ""
        )

        if status not in OPEN_STATUSES:
            continue

        existing_setup_key = setup_key_from_record(
            row_dict
        )

        if existing_setup_key == new_setup_key:
            return True

    return False

def build_trade_record(
    payload,
    symbol="BTCUSDT"
):

    alert = payload.get(
        "alert",
        {}
    )

    risk = payload.get(
        "risk_report",
        {}
    )

    decision = payload.get(
        "decision",
        {}
    )

    entry = alert.get(
        "entry",
        {}
    )

    impulse = alert.get(
        "impulse",
        {}
    )

    outcomes = risk.get(
        "outcomes",
        {}
    )

    strategy = "FIB_V5_TP1_BE"

    entry_time = entry.get(
        "entry_time",
        now_string()
    )

    entry_price = safe_float(
        alert.get("entry_price")
    )

    stop_price = safe_float(
        alert.get("stop_price")
    )

    tp1_price = safe_float(
        alert.get("tp1_price")
    )

    tp2_price = safe_float(
        alert.get("target_price")
    )

    trade_id = generate_trade_id(
        symbol=symbol,
        strategy=strategy,
        entry_time=entry_time,
        entry_price=entry_price,
        stop_price=stop_price,
        target_price=tp2_price
    )

    return {
        "trade_id": trade_id,
        "setup_key": setup_key_from_values(
            symbol=symbol,
            strategy=strategy,
            direction="SHORT",
            impulse_high=impulse.get("high_price"),
            impulse_low=impulse.get("low_price"),
            stop_price=stop_price,
            tp2_price=tp2_price
        ),
        "created_at": now_string(),
        "updated_at": now_string(),
        "symbol": symbol,
        "strategy": strategy,
        "direction": "SHORT",
        "status": "OPEN",
        "decision": decision.get("decision"),
        "permission": decision.get("permission"),
        "state": decision.get("state"),
        "bias": alert.get("bias"),
        "entry_time": entry_time,
        "entry_price": entry_price,
        "current_price_at_signal": safe_float(
            alert.get("current_price")
        ),
        "stop_price": stop_price,
        "tp1_price": tp1_price,
        "tp2_price": tp2_price,
        "tp1_close_weight": safe_float(
            alert.get("tp1_close_weight"),
            0.50
        ),
        "position_notional": safe_float(
            risk.get("position_notional")
        ),
        "btc_size": safe_float(
            risk.get("btc_size")
        ),
        "risk_amount": safe_float(
            risk.get("risk_amount")
        ),
        "risk_per_trade_pct": safe_float(
            risk.get("risk_per_trade_pct")
        ),
        "stop_distance_pct": safe_float(
            risk.get("stop_distance_pct")
        ),
        "potential_stop_pct": safe_float(
            outcomes.get("stop_result_pct")
        ),
        "potential_tp1_pct": safe_float(
            outcomes.get("tp1_result_pct")
        ),
        "potential_tp2_pct": safe_float(
            outcomes.get("tp2_result_pct")
        ),
        "potential_tp1_be_pct": safe_float(
            outcomes.get("tp1_then_be_result_pct")
        ),
        "potential_tp1_tp2_pct": safe_float(
            outcomes.get("tp1_then_tp2_result_pct")
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
        "entry_zone_low": safe_float(
            alert.get("entry_zone_low")
        ),
        "entry_zone_high": safe_float(
            alert.get("entry_zone_high")
        ),
        "tp1_hit": False,
        "be_active": False,
        "exit_time": "",
        "exit_price": "",
        "exit_reason": "",
        "final_result_pct": "",
        "last_checked_price": safe_float(
            alert.get("current_price")
        ),
        "notes": decision.get(
            "suggested_action",
            ""
        )
    }


def trade_exists(
    df,
    trade_id
):

    if len(df) == 0:
        return False

    if "trade_id" not in df.columns:
        return False

    return trade_id in df["trade_id"].astype(str).values


def update_open_short_trade(
    row,
    current_price
):

    status = row.get(
        "status",
        "OPEN"
    )

    if status not in OPEN_STATUSES:
        return row

    entry_price = safe_float(
        row.get("entry_price")
    )

    stop_price = safe_float(
        row.get("stop_price")
    )

    tp1_price = safe_float(
        row.get("tp1_price")
    )

    tp2_price = safe_float(
        row.get("tp2_price")
    )

    potential_stop_pct = safe_float(
        row.get("potential_stop_pct")
    )

    potential_tp1_be_pct = safe_float(
        row.get("potential_tp1_be_pct")
    )

    potential_tp1_tp2_pct = safe_float(
        row.get("potential_tp1_tp2_pct")
    )

    row["last_checked_price"] = current_price
    row["updated_at"] = now_string()

    if status == "OPEN":

        if current_price >= stop_price:

            row["status"] = "CLOSED_STOP"
            row["exit_time"] = now_string()
            row["exit_price"] = stop_price
            row["exit_reason"] = "STOP_LOSS"
            row["final_result_pct"] = potential_stop_pct

            return row

        if current_price <= tp2_price:

            row["status"] = "CLOSED_TP2"
            row["tp1_hit"] = True
            row["be_active"] = False
            row["exit_time"] = now_string()
            row["exit_price"] = tp2_price
            row["exit_reason"] = "TP1_AND_TP2"
            row["final_result_pct"] = potential_tp1_tp2_pct

            return row

        if current_price <= tp1_price:

            row["status"] = "TP1_HIT_BE_ACTIVE"
            row["tp1_hit"] = True
            row["be_active"] = True
            row["updated_at"] = now_string()
            row["notes"] = (
                "TP1 alcanzado. Cerrar 50% y mover restante a breakeven."
            )

            return row

    if status == "TP1_HIT_BE_ACTIVE":

        if current_price <= tp2_price:

            row["status"] = "CLOSED_TP2"
            row["be_active"] = False
            row["exit_time"] = now_string()
            row["exit_price"] = tp2_price
            row["exit_reason"] = "TP1_THEN_TP2"
            row["final_result_pct"] = potential_tp1_tp2_pct

            return row

        if current_price >= entry_price:

            row["status"] = "CLOSED_BREAKEVEN"
            row["be_active"] = False
            row["exit_time"] = now_string()
            row["exit_price"] = entry_price
            row["exit_reason"] = "TP1_THEN_BREAKEVEN"
            row["final_result_pct"] = potential_tp1_be_pct

            return row

    return row


def update_open_trades(
    df,
    current_price
):

    if len(df) == 0:
        return df

    updated_rows = []

    for _, row in df.iterrows():

        row_dict = row.to_dict()

        updated_row = update_open_short_trade(
            row_dict,
            current_price=current_price
        )

        updated_rows.append(
            updated_row
        )

    return pd.DataFrame(
        updated_rows
    )


def log_paper_trade_from_decision(
    decision_payload,
    output_path=PAPER_TRADES_FILE
):

    alert = decision_payload.get(
        "alert",
        {}
    )

    decision = decision_payload.get(
        "decision",
        {}
    )

    current_price = safe_float(
        alert.get("current_price")
    )

    df = load_paper_trades(
        output_path
    )

    df = update_open_trades(
        df,
        current_price=current_price
    )

    decision_name = decision.get(
        "decision"
    )

    entry_signal = alert.get(
        "entry_signal",
        False
    )

    if (
        decision_name not in ALLOWED_DECISIONS
        or not entry_signal
    ):

        save_paper_trades(
            df,
            output_path
        )

        return {
            "logged": False,
            "reason": "La decisión no permite registrar trade o no hay señal de entrada.",
            "paper_trades_path": output_path,
            "total_trades": len(df)
        }

    trade_record = build_trade_record(
        decision_payload
    )

    if open_trade_exists_for_same_setup(
        df,
        trade_record
    ):

        save_paper_trades(
            df,
            output_path
        )

        return {
            "logged": False,
            "reason": "Ya existe un paper trade abierto para este mismo setup Fibonacci.",
            "trade_id": trade_record["trade_id"],
            "paper_trades_path": output_path,
            "total_trades": len(df)
        }

    if trade_exists(
        df,
        trade_record["trade_id"]
    ):

        save_paper_trades(
            df,
            output_path
        )

        return {
            "logged": False,
            "reason": "Trade duplicado. No se registró nuevamente.",
            "trade_id": trade_record["trade_id"],
            "paper_trades_path": output_path,
            "total_trades": len(df)
        }

    new_row = pd.DataFrame(
        [trade_record]
    )

    df = pd.concat(
        [
            df,
            new_row
        ],
        ignore_index=True
    )

    save_paper_trades(
        df,
        output_path
    )

    return {
        "logged": True,
        "reason": "Paper trade registrado correctamente.",
        "trade_id": trade_record["trade_id"],
        "paper_trades_path": output_path,
        "total_trades": len(df)
    }

def summarize_paper_trades(
    path=PAPER_TRADES_FILE
):

    df = load_paper_trades(
        path
    )

    if len(df) == 0:

        return {
            "total_trades": 0,
            "open_trades": 0,
            "closed_trades": 0,
            "status_counts": {}
        }

    if "status" not in df.columns:

        return {
            "total_trades": len(df),
            "open_trades": 0,
            "closed_trades": len(df),
            "status_counts": {}
        }

    status_counts = (
        df["status"]
        .value_counts()
        .to_dict()
    )

    open_trades = df[
        df["status"].isin(
            OPEN_STATUSES
        )
    ]

    closed_trades = df[
        ~df["status"].isin(
            OPEN_STATUSES
        )
    ]

    return {
        "total_trades": len(df),
        "open_trades": len(open_trades),
        "closed_trades": len(closed_trades),
        "status_counts": status_counts
    }