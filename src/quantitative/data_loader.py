import pandas as pd


REQUIRED_COLUMNS = [
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume"
]


def load_csv(file_path: str) -> pd.DataFrame:
    """
    Carga un archivo CSV.
    """

    df = pd.read_csv(file_path)

    return df


def validate_data(df: pd.DataFrame) -> bool:
    """
    Verifica que existan las columnas necesarias.
    """

    missing = [
        col
        for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Columnas faltantes: {missing}"
        )

    return True


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpieza básica.
    """

    df = df.dropna()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    return df