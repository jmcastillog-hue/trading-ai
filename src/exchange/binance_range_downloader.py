from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import time
import requests
import pandas as pd


BASE_URLS = {
    "spot": "https://api.binance.com/api/v3/klines",
    "usdt_futures": "https://fapi.binance.com/fapi/v1/klines",
}


def date_to_milliseconds(date_text: str) -> int:
    """
    Convierte fecha YYYY-MM-DD a timestamp en milisegundos UTC.
    """
    dt = datetime.strptime(date_text, "%Y-%m-%d")
    dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def download_binance_klines_range(
    symbol: str,
    interval: str,
    start_date: str,
    end_date: str,
    market_type: str,
    output_path: str | Path,
    limit: int = 1000,
    sleep_seconds: float = 0.25,
) -> pd.DataFrame:
    """
    Descarga velas de Binance en un rango de fechas.

    No requiere API key.
    """

    if market_type not in BASE_URLS:
        raise ValueError(f"market_type inválido: {market_type}")

    base_url = BASE_URLS[market_type]

    start_ms = date_to_milliseconds(start_date)
    end_ms = date_to_milliseconds(end_date)

    all_rows = []
    current_start = start_ms

    print(f"Descargando {symbol} {interval} desde {start_date} hasta {end_date}")
    print(f"Mercado: {market_type}")

    while current_start < end_ms:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": current_start,
            "endTime": end_ms,
            "limit": limit,
        }

        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()

        rows = response.json()

        if not rows:
            break

        all_rows.extend(rows)

        last_open_time = rows[-1][0]
        current_start = last_open_time + 1

        print(f"Velas descargadas: {len(all_rows)}")

        time.sleep(sleep_seconds)

        if len(rows) < limit:
            break

    columns = [
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_asset_volume",
        "number_of_trades",
        "taker_buy_base_volume",
        "taker_buy_quote_volume",
        "ignore",
    ]

    df = pd.DataFrame(all_rows, columns=columns)

    if df.empty:
        raise RuntimeError("No se descargaron datos.")

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)

    numeric_cols = [
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df[["timestamp", "open", "high", "low", "close", "volume"]]
    df = df.dropna()
    df = df.drop_duplicates(subset=["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Archivo guardado: {output_path}")
    print(f"Total velas finales: {len(df)}")

    return df