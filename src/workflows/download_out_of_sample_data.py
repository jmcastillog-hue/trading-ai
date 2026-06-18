from src.exchange.binance_range_downloader import download_binance_klines_range


def main():
    """
    Dataset out-of-sample.

    Usaremos un rango histórico anterior y separado para evitar validar
    sobre las mismas velas usadas en la selección de parámetros.
    """

    datasets = [
        {
            "symbol": "BTCUSDT",
            "interval": "15m",
            "start_date": "2024-01-01",
            "end_date": "2024-03-01",
            "market_type": "spot",
            "output_path": "data/oos_btcusdt_15m_2024_01_03.csv",
        },
        {
            "symbol": "BTCUSDT",
            "interval": "1h",
            "start_date": "2024-01-01",
            "end_date": "2024-03-01",
            "market_type": "spot",
            "output_path": "data/oos_btcusdt_1h_2024_01_03.csv",
        },
        {
            "symbol": "BTCUSDT",
            "interval": "4h",
            "start_date": "2024-01-01",
            "end_date": "2024-03-01",
            "market_type": "spot",
            "output_path": "data/oos_btcusdt_4h_2024_01_03.csv",
        },
    ]

    print("DESCARGA OUT-OF-SAMPLE BTCUSDT")
    print("=" * 70)

    for dataset in datasets:
        print()
        download_binance_klines_range(**dataset)

    print()
    print("Descarga out-of-sample completada.")


if __name__ == "__main__":
    main()