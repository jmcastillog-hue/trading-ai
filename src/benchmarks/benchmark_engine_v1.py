from __future__ import annotations

import random
from typing import Callable

import pandas as pd


def context_only_v3_1_short_strategy(df: pd.DataFrame, index: int, config=None) -> str:
    row = df.iloc[index]

    if bool(row.get("short_allowed_v3_1", False)):
        return "SHORT"

    return "NONE"


def ema_trend_short_strategy(df: pd.DataFrame, index: int, config=None) -> str:
    if index < 250:
        return "NONE"

    row = df.iloc[index]

    close = row.get("close")
    ema20 = row.get("aev1_ema20")
    ema50 = row.get("aev1_ema50")
    ema20_slope = row.get("aev1_ema20_slope_5")

    if pd.isna(close) or pd.isna(ema20) or pd.isna(ema50) or pd.isna(ema20_slope):
        return "NONE"

    if close < ema20 and ema20 < ema50 and ema20_slope < 0:
        return "SHORT"

    return "NONE"


def collect_signal_indices(
    df: pd.DataFrame,
    strategy_func: Callable,
    config=None,
    start_index: int = 250,
) -> list[int]:
    indices = []

    for index in range(start_index, len(df) - 2):
        try:
            signal = strategy_func(df, index, config)
        except Exception:
            signal = "NONE"

        if signal == "SHORT":
            indices.append(index)

    return indices


def build_random_short_strategy(
    selected_indices: set[int],
) -> Callable:
    def random_short_strategy(df: pd.DataFrame, index: int, config=None) -> str:
        if index in selected_indices:
            return "SHORT"

        return "NONE"

    return random_short_strategy


def select_random_indices(
    df: pd.DataFrame,
    sample_size: int,
    seed: int,
    start_index: int = 250,
) -> set[int]:
    valid_indices = list(range(start_index, len(df) - 2))

    if not valid_indices or sample_size <= 0:
        return set()

    rng = random.Random(seed)

    sample_size = min(sample_size, len(valid_indices))

    return set(rng.sample(valid_indices, sample_size))


def build_random_baseline_strategies(
    df: pd.DataFrame,
    reference_strategy_func: Callable,
    config=None,
    seeds: list[int] | None = None,
) -> list[dict]:
    if seeds is None:
        seeds = [11, 22, 33]

    reference_indices = collect_signal_indices(
        df=df,
        strategy_func=reference_strategy_func,
        config=config,
    )

    sample_size = len(reference_indices)

    strategies = []

    for seed in seeds:
        selected_indices = select_random_indices(
            df=df,
            sample_size=sample_size,
            seed=seed,
        )

        strategies.append(
            {
                "strategy_name": f"RANDOM_SHORT_SAME_COUNT_SEED_{seed}",
                "strategy_func": build_random_short_strategy(selected_indices),
            }
        )

    return strategies