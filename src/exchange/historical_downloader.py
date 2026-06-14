from binance.client import Client
import pandas as pd
import os


DOWNLOAD_JOBS = [
    {
        "symbol": "BTCUSDT",
        "interval": "30m",
        "start": "1 Jan, 2025",
        "output": "data/btcusdt_30m_history.csv"
    },
    {
        "symbol": "BTCUSDT",
        "interval": "1h",
        "start": "1 Jan, 2025",
        "output": "data/btcusdt_1h_history.csv"
    },
    {
        "symbol": "BTCUSDT",
        "interval": "4h",
        "start": "1 Jan, 2024",
        "output": "data/btcusdt_4h_history.csv"
    },
    {
        "symbol": "BTCUSDT",
        "interval": "1d",
        "start": "1 Jan, 2022",
        "output": "data/btcusdt_1d_history.csv"
    }
]


def download_historical_klines(
    symbol,
    interval,
    start,
    output
):

    client = Client()

    print(
        f"\nDescargando histórico {symbol} {interval} desde {start}..."
    )

    klines = client.get_historical_klines(
        symbol=symbol,
        interval=interval,
        start_str=start
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

        download_historical_klines(
            symbol=job["symbol"],
            interval=job["interval"],
            start=job["start"],
            output=job["output"]
        )


if __name__ == "__main__":
    main()