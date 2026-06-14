import os
import sys
import json

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

from src.regime.mtf_trend_regime_engine import (
    generate_mtf_trend_regime,
    build_mtf_regime_report_text
)


SYMBOL = "BTCUSDT"

TIMEFRAMES = {
    "1d": {
        "interval": "1d",
        "limit": 1000,
        "output": "data/btcusdt_1d_live.csv"
    },
    "4h": {
        "interval": "4h",
        "limit": 1000,
        "output": "data/btcusdt_4h_live.csv"
    },
    "1h": {
        "interval": "1h",
        "limit": 1000,
        "output": "data/btcusdt_1h_live.csv"
    },
    "30m": {
        "interval": "30m",
        "limit": 1000,
        "output": "data/btcusdt_30m_live.csv"
    }
}

REPORT_TXT = "reports/mtf_trend_regime_report.txt"
REPORT_JSON = "reports/mtf_trend_regime_report.json"


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

    for kline in klines:

        rows.append({
            "timestamp": pd.to_datetime(
                kline[0],
                unit="ms"
            ),
            "open": float(kline[1]),
            "high": float(kline[2]),
            "low": float(kline[3]),
            "close": float(kline[4]),
            "volume": float(kline[5])
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


def save_reports(
    regime,
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

    json_safe = json.loads(
        json.dumps(
            regime,
            default=str
        )
    )

    with open(
        REPORT_JSON,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            json_safe,
            file,
            indent=4,
            ensure_ascii=False
        )


def main():

    print(
        "\n=== ACTUALIZANDO DATOS MTF ===\n"
    )

    timeframe_data = {}

    for timeframe_label, config in TIMEFRAMES.items():

        df = download_klines(
            symbol=SYMBOL,
            interval=config["interval"],
            limit=config["limit"],
            output_path=config["output"]
        )

        timeframe_data[timeframe_label] = df

    print(
        "\n=== EJECUTANDO MTF TREND REGIME ENGINE ===\n"
    )

    regime = generate_mtf_trend_regime(
        timeframe_data
    )

    report_text = build_mtf_regime_report_text(
        regime
    )

    print(
        report_text
    )

    save_reports(
        regime,
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