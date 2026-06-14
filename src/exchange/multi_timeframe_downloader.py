from binance.client import Client
import pandas as pd
import os


DOWNLOAD_JOBS = [
    {
        "symbol": "BTCUSDT",
        "interval": "15m",
        "limit": 1000,
        "output": "data/btcusdt_15m.csv"
    },
    {
        "symbol": "BTCUSDT",
        "interval": "30m",
        "limit": 1000,
        "output": "data/btcusdt_30m.csv"
    },
    {
        "symbol": "BTCUSDT",
        "interval": "1h",
        "limit": 1000,
        "output": "data/btcusdt_1h.csv"
    },
    {
        "symbol": "BTCUSDT",
        "interval": "4h",
        "limit": 1000,
        "output": "data/btcusdt_4h.csv"
    },
    {
        "symbol": "BTCUSDT",
        "interval": "1d",
        "limit": 1000,
        "output": "data/btcusdt_1d.csv"
    },
    {
        "symbol": "BTCUSDT",
        "interval": "1w",
        "limit": 500,
        "output": "data/btcusdt_1w.csv"
    }
]


def download_klines(
    symbol,
    interval,
    limit,
    output
):

    client = Client()

    print(
        f"\nDescargando {symbol} {interval}..."
    )

    klines = client.get_klines(
        symbol=symbol,
        interval=interval,
        limit=limit
    )

    data = []

    for k in klines:

        data.append({
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

    df = pd.DataFrame(data)

    folder = os.path.dirname(output)

    if folder:
        os.makedirs(
            folder,
            exist_ok=True
        )

    df.to_csv(
        output,
        index=False
    )

    print(
        f"Archivo guardado: {output}"
    )

    print(
        f"Velas descargadas: {len(df)}"
    )


def main():

    for job in DOWNLOAD_JOBS:

        download_klines(
            symbol=job["symbol"],
            interval=job["interval"],
            limit=job["limit"],
            output=job["output"]
        )


if __name__ == "__main__":
    main()