from binance.client import Client
import pandas as pd
import os
import sys

# Permite importar desde config
sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            ".."
        )
    )
)

from config.binance_config import (
    SYMBOL,
    INTERVAL,
    LIMIT,
    OUTPUT_FILE
)


def download_klines():

    client = Client()

    print(
        f"\nDescargando {LIMIT} velas de {SYMBOL} ({INTERVAL})..."
    )

    klines = client.get_klines(
        symbol=SYMBOL,
        interval=INTERVAL,
        limit=LIMIT
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

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"Archivo guardado: {OUTPUT_FILE}"
    )

    print(
        f"Velas descargadas: {len(df)}"
    )

    return df


if __name__ == "__main__":
    download_klines()