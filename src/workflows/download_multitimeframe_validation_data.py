from src.exchange.binance_historical_downloader import download_binance_klines


def main():
    datasets = [
        {
            "symbol": "BTCUSDT",
            "interval": "15m",
            "total_candles": 5000,
            "market_type": "spot",
            "output_path": "data/btcusdt_15m_validation.csv",
        },
        {
            "symbol": "BTCUSDT",
            "interval": "30m",
            "total_candles": 5000,
            "market_type": "spot",
            "output_path": "data/btcusdt_30m_validation.csv",
        },
        {
            "symbol": "BTCUSDT",
            "interval": "1h",
            "total_candles": 5000,
            "market_type": "spot",
            "output_path": "data/btcusdt_1h_validation.csv",
        },
        {
            "symbol": "BTCUSDT",
            "interval": "4h",
            "total_candles": 5000,
            "market_type": "spot",
            "output_path": "data/btcusdt_4h_validation.csv",
        },
    ]

    print("DESCARGA MULTI-TIMEFRAME BTCUSDT")
    print("=" * 60)

    for dataset in datasets:
        print()
        print(f"Descargando {dataset['symbol']} {dataset['interval']}...")
        print("-" * 60)

        download_binance_klines(
            symbol=dataset["symbol"],
            interval=dataset["interval"],
            total_candles=dataset["total_candles"],
            market_type=dataset["market_type"],
            output_path=dataset["output_path"],
        )

    print()
    print("Descarga multi-timeframe completada.")


if __name__ == "__main__":
    main()