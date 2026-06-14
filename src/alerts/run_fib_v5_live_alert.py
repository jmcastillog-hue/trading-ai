import os
import sys
import json
from datetime import datetime

import pandas as pd
from binance.client import Client

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
    validate_data,
    clean_data
)

from src.alerts.fib_v5_alert_engine_v2 import (
    generate_fib_v5_alert_v2
)


SYMBOL = "BTCUSDT"

HTF_INTERVAL = "4h"
LTF_INTERVAL = "30m"

HTF_LIMIT = 1000
LTF_LIMIT = 1000

HTF_OUTPUT = "data/btcusdt_4h_live.csv"
LTF_OUTPUT = "data/btcusdt_30m_live.csv"

REPORT_TXT = "reports/fib_v5_live_alert_report.txt"
REPORT_JSON = "reports/fib_v5_live_alert_report.json"


def download_klines(
    symbol,
    interval,
    limit,
    output_path
):

    client = Client()

    print(
        f"Descargando {symbol} {interval} | velas: {limit}"
    )

    klines = client.get_klines(
        symbol=symbol,
        interval=interval,
        limit=limit
    )

    rows = []

    for k in klines:

        rows.append({
            "timestamp": pd.to_datetime(
                k[0],
                unit="ms"
            ),
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5])
        })

    df = pd.DataFrame(
        rows
    )

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    df.to_csv(
        output_path,
        index=False
    )

    print(
        f"Archivo actualizado: {output_path}"
    )

    return df


def prepare_market_data(
    df
):

    validate_data(
        df
    )

    df = clean_data(
        df
    )

    return df


def format_float(
    value,
    decimals=2
):

    if value is None:
        return "None"

    try:
        return f"{float(value):.{decimals}f}"

    except Exception:
        return str(value)


def build_alert_report_text(
    alert
):

    lines = []

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    lines.append(
        "=== FIB V5 LIVE ALERT ENGINE ==="
    )

    lines.append(
        ""
    )

    lines.append(
        f"generated_at: {now}"
    )

    lines.append(
        f"symbol: {SYMBOL}"
    )

    lines.append(
        f"htf: {HTF_INTERVAL}"
    )

    lines.append(
        f"ltf: {LTF_INTERVAL}"
    )

    lines.append(
        ""
    )

    lines.append(
        f"setup_active: {alert.get('setup_active')}"
    )

    lines.append(
        f"state: {alert.get('state')}"
    )

    lines.append(
        f"bias: {alert.get('bias')}"
    )

    lines.append(
        f"current_price: {format_float(alert.get('current_price'))}"
    )

    lines.append(
        f"comment: {alert.get('comment')}"
    )

    candidates = alert.get(
        "candidates",
        []
    )

    lines.append(
        ""
    )

    lines.append(
        f"candidates_scanned: {len(candidates)}"
    )

    for index, candidate in enumerate(
        candidates,
        start=1
    ):

        impulse = candidate.get(
            "impulse",
            {}
        )

        lines.append(
            ""
        )

        lines.append(
            f"--- CANDIDATO #{index} ---"
        )

        lines.append(
            f"state: {candidate.get('state')}"
        )

        lines.append(
            f"active: {candidate.get('setup_active')}"
        )

        lines.append(
            f"entry_signal: {candidate.get('entry_signal')}"
        )

        lines.append(
            f"impulse_high: {format_float(impulse.get('high_price'))}"
        )

        lines.append(
            f"impulse_low: {format_float(impulse.get('low_price'))}"
        )

        lines.append(
            f"drop_pct: {format_float(impulse.get('drop_pct'))}%"
        )

        lines.append(
            f"zone: {format_float(candidate.get('entry_zone_low'))} - {format_float(candidate.get('entry_zone_high'))}"
        )

        lines.append(
            f"stop: {format_float(candidate.get('stop_price'))}"
        )

        lines.append(
            f"target: {format_float(candidate.get('target_price'))}"
        )

        lines.append(
            f"distance_to_zone_pct: {format_float(candidate.get('distance_to_zone_pct'))}%"
        )

    if alert.get(
        "setup_active"
    ):

        lines.append(
            ""
        )

        lines.append(
            "=== MEJOR SETUP ACTIVO ==="
        )

        lines.append(
            f"state: {alert.get('state')}"
        )

        lines.append(
            f"entry_zone_low: {format_float(alert.get('entry_zone_low'))}"
        )

        lines.append(
            f"entry_zone_high: {format_float(alert.get('entry_zone_high'))}"
        )

        lines.append(
            f"stop_price: {format_float(alert.get('stop_price'))}"
        )

        lines.append(
            f"target_price: {format_float(alert.get('target_price'))}"
        )

        lines.append(
            f"entry_signal: {alert.get('entry_signal')}"
        )

        if alert.get(
            "entry_signal"
        ):

            lines.append(
                ""
            )

            lines.append(
                "--- PLAN OPERATIVO V5 ---"
            )

            lines.append(
                f"entry_price: {format_float(alert.get('entry_price'))}"
            )

            lines.append(
                f"tp1_price: {format_float(alert.get('tp1_price'))}"
            )

            lines.append(
                f"cerrar_en_tp1: {format_float(alert.get('tp1_close_weight') * 100, 0)}%"
            )

            lines.append(
                "mover_restante_a: BREAKEVEN"
            )

            lines.append(
                f"tp2_price: {format_float(alert.get('target_price'))}"
            )

        else:

            lines.append(
                ""
            )

            lines.append(
                "--- PLAN DE ESPERA ---"
            )

            lines.append(
                "No hay entrada todavía."
            )

            lines.append(
                "Esperar cierre de vela bajista 30m dentro de la zona Fibonacci."
            )

    lines.append(
        ""
    )

    lines.append(
        "Nota: Este reporte es solo una alerta técnica. No ejecuta operaciones ni constituye recomendación financiera."
    )

    return "\n".join(
        lines
    )


def save_reports(
    alert,
    report_text
):

    os.makedirs(
        "reports",
        exist_ok=True
    )

    with open(
        REPORT_TXT,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            report_text
        )

    json_safe_alert = json.loads(
        json.dumps(
            alert,
            default=str
        )
    )

    with open(
        REPORT_JSON,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            json_safe_alert,
            file,
            indent=4,
            ensure_ascii=False
        )


def main():

    print(
        "\n=== ACTUALIZANDO DATOS ===\n"
    )

    htf_df = download_klines(
        symbol=SYMBOL,
        interval=HTF_INTERVAL,
        limit=HTF_LIMIT,
        output_path=HTF_OUTPUT
    )

    ltf_df = download_klines(
        symbol=SYMBOL,
        interval=LTF_INTERVAL,
        limit=LTF_LIMIT,
        output_path=LTF_OUTPUT
    )

    htf_df = prepare_market_data(
        htf_df
    )

    ltf_df = prepare_market_data(
        ltf_df
    )

    print(
        "\n=== EJECUTANDO ALERT ENGINE V5 ===\n"
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

    report_text = build_alert_report_text(
        alert
    )

    print(
        report_text
    )

    save_reports(
        alert,
        report_text
    )

    print(
        f"\nReporte TXT guardado en: {REPORT_TXT}"
    )

    print(
        f"Reporte JSON guardado en: {REPORT_JSON}"
    )


if __name__ == "__main__":
    main()