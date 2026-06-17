from pathlib import Path
import time
import requests
import pandas as pd


BASE_URLS = {
    "spot": "https://api.binance.com/api/v3/klines",
    "usdt_futures": "https://fapi.binance.com/fapi/v1/klines",
}


def download_binance_klines(
    symbol: str = "BTCUSDT",
    interval: str = "15m",
    total_candles: int = 5000,
    market_type: str = "spot",
    output_path: str | Path = "data/btcusdt_15m_validation.csv",
    pause_seconds: float = 0.2,
) -> pd.DataFrame:
    """
    Descarga velas históricas desde Binance usando endpoint público.

    No requiere API Key.

    market_type:
    - spot
    - usdt_futures
    """

    if market_type not in BASE_URLS:
        raise ValueError(f"market_type inválido: {market_type}")

    url = BASE_URLS[market_type]
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    all_rows = []
    end_time = None
    remaining = total_candles

    while remaining > 0:
        limit = min(1000, remaining)

        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
        }

        if end_time is not None:
            params["endTime"] = end_time

        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()

        rows = response.json()

        if not rows:
            break

        all_rows = rows + all_rows

        first_open_time = rows[0][0]
        end_time = first_open_time - 1

        remaining -= len(rows)

        print(
            f"Descargadas: {len(all_rows)} / {total_candles} "
            f"velas | intervalo={interval} | market={market_type}"
        )

        time.sleep(pause_seconds)

        if len(rows) < limit:
            break

    df = pd.DataFrame(
        all_rows,
        columns=[
            "open_time",
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
        ],
    )

    df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms")

    keep_columns = [
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    df = df[keep_columns].copy()

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna()
    df = df.drop_duplicates(subset=["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    df.to_csv(output_path, index=False)

    print()
    print(f"Archivo guardado: {output_path}")
    print(f"Total velas finales: {len(df)}")
    print(f"Desde: {df['timestamp'].min()}")
    print(f"Hasta: {df['timestamp'].max()}")

    return df


if __name__ == "__main__":
    download_binance_klines(
        symbol="BTCUSDT",
        interval="15m",
        total_candles=5000,
        market_type="spot",
        output_path="data/btcusdt_15m_validation.csv",
    )