from pathlib import Path
import pandas as pd

from src.market_structure.directional_context_filter_v3 import (
    enrich_with_directional_context_v3,
)


ROBUST_ALLOW_PAIRS = {
    (
        "SHORT",
        "SHORT_CAUTION",
        "BEARISH_TREND",
        "BEARISH_OVEREXTENDED",
    ),
}


REJECT_PAIRS = {
    (
        "SHORT",
        "SHORT_ONLY",
        "BEARISH_TREND",
        "BEARISH_TREND",
    ),
    (
        "SHORT",
        "SHORT_ONLY",
        "BEARISH_TREND",
        "BEARISH_BIAS",
    ),
    (
        "SHORT",
        "SHORT_ONLY",
        "BEARISH_BIAS",
        "BEARISH_BIAS",
    ),
    (
        "LONG",
        "LONG_ONLY",
        "BULLISH_TREND",
        "BULLISH_BIAS",
    ),
    (
        "LONG",
        "LONG_ONLY",
        "BULLISH_BIAS",
        "BULLISH_MOMENTUM",
    ),
    (
        "LONG",
        "LONG_CAUTION",
        "BULLISH_TREND",
        "BULLISH_OVEREXTENDED",
    ),
}


def get_context_pair(row: pd.Series, direction: str) -> tuple[str, str, str, str]:
    return (
        direction,
        str(row.get("directional_context_v3", "UNKNOWN")),
        str(row.get("bias_1h_v3", "UNKNOWN")),
        str(row.get("bias_4h_v3", "UNKNOWN")),
    )


def classify_directional_context_v3_1(row: pd.Series, direction: str) -> str:
    pair = get_context_pair(row, direction)

    if pair in ROBUST_ALLOW_PAIRS:
        return "ALLOW_ROBUST_PAIR"

    if pair in REJECT_PAIRS:
        return "BLOCK_REJECTED_PAIR"

    return "MONITOR_NOT_ALLOWED"


def long_allowed_by_directional_context_v3_1(row: pd.Series) -> bool:
    decision = classify_directional_context_v3_1(row, "LONG")
    return decision == "ALLOW_ROBUST_PAIR"


def short_allowed_by_directional_context_v3_1(row: pd.Series) -> bool:
    decision = classify_directional_context_v3_1(row, "SHORT")
    return decision == "ALLOW_ROBUST_PAIR"


def add_directional_context_v3_1_columns(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["long_context_decision_v3_1"] = result.apply(
        lambda row: classify_directional_context_v3_1(row, "LONG"),
        axis=1,
    )

    result["short_context_decision_v3_1"] = result.apply(
        lambda row: classify_directional_context_v3_1(row, "SHORT"),
        axis=1,
    )

    result["long_allowed_v3_1"] = result.apply(
        long_allowed_by_directional_context_v3_1,
        axis=1,
    )

    result["short_allowed_v3_1"] = result.apply(
        short_allowed_by_directional_context_v3_1,
        axis=1,
    )

    return result


def enrich_with_directional_context_v3_1(
    entry_csv_path: str | Path,
    h1_csv_path: str | Path,
    h4_csv_path: str | Path,
    output_path: str | Path | None = None,
) -> pd.DataFrame:
    enriched_v3 = enrich_with_directional_context_v3(
        entry_csv_path=entry_csv_path,
        h1_csv_path=h1_csv_path,
        h4_csv_path=h4_csv_path,
        output_path=None,
    )

    enriched_v3_1 = add_directional_context_v3_1_columns(enriched_v3)

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        enriched_v3_1.to_csv(output_path, index=False)

    return enriched_v3_1