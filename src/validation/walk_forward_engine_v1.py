from __future__ import annotations

import copy
from dataclasses import is_dataclass, replace
from typing import Callable

import pandas as pd

from src.exits.active_exit_manager_v1 import (
    build_exit_profile,
    run_active_exit_backtest,
)


def safe_float(value, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def override_config(config, **updates):
    if is_dataclass(config):
        try:
            return replace(config, **updates)
        except TypeError:
            cloned = copy.copy(config)
            for key, value in updates.items():
                setattr(cloned, key, value)
            return cloned

    if isinstance(config, dict):
        cloned = dict(config)
        cloned.update(updates)
        return cloned

    cloned = copy.copy(config)

    for key, value in updates.items():
        setattr(cloned, key, value)

    return cloned


def build_fixed_rr_exit_profile(
    risk_reward: float,
    profile_name: str,
) -> dict:
    base = build_exit_profile("FIXED_RR_2_5")
    base["name"] = profile_name
    base["risk_reward"] = risk_reward
    return base


def build_walk_forward_candidates() -> list[dict]:
    return [
        {
            "candidate_name": "OFFICIAL_RR_2_5_ATR_1_25_HOLD_48",
            "risk_reward": 2.5,
            "atr_multiplier": 1.25,
            "max_holding_bars": 48,
            "is_official": True,
        },
        {
            "candidate_name": "RR_2_0_ATR_1_25_HOLD_48",
            "risk_reward": 2.0,
            "atr_multiplier": 1.25,
            "max_holding_bars": 48,
            "is_official": False,
        },
        {
            "candidate_name": "RR_3_0_ATR_1_25_HOLD_48",
            "risk_reward": 3.0,
            "atr_multiplier": 1.25,
            "max_holding_bars": 48,
            "is_official": False,
        },
        {
            "candidate_name": "RR_2_5_ATR_1_00_HOLD_48",
            "risk_reward": 2.5,
            "atr_multiplier": 1.0,
            "max_holding_bars": 48,
            "is_official": False,
        },
        {
            "candidate_name": "RR_2_5_ATR_1_50_HOLD_48",
            "risk_reward": 2.5,
            "atr_multiplier": 1.5,
            "max_holding_bars": 48,
            "is_official": False,
        },
        {
            "candidate_name": "RR_2_5_ATR_1_25_HOLD_32",
            "risk_reward": 2.5,
            "atr_multiplier": 1.25,
            "max_holding_bars": 32,
            "is_official": False,
        },
        {
            "candidate_name": "RR_2_5_ATR_1_25_HOLD_64",
            "risk_reward": 2.5,
            "atr_multiplier": 1.25,
            "max_holding_bars": 64,
            "is_official": False,
        },
    ]


def calculate_selection_score(summary: dict) -> float:
    trades = int(summary.get("total_trades", 0))
    total_return = safe_float(summary.get("total_return_pct"), 0.0)
    profit_factor = safe_float(summary.get("profit_factor"), 0.0)
    expectancy_r = safe_float(summary.get("expectancy_r"), 0.0)
    max_drawdown = abs(safe_float(summary.get("max_drawdown_pct"), 0.0))

    if trades < 5:
        return -999.0

    score = 0.0
    score += total_return * 3.0
    score += expectancy_r * 2.0
    score += min(profit_factor, 3.0) * 0.5
    score -= max_drawdown * 2.0

    return score


def classify_walk_forward_result(row: pd.Series) -> str:
    tests = int(row.get("test_windows", 0))
    trades = int(row.get("total_test_trades", 0))
    compound_return = safe_float(row.get("compound_test_return"), 0.0)
    avg_pf = safe_float(row.get("avg_test_profit_factor"), 0.0)
    worst_dd = safe_float(row.get("worst_test_drawdown"), 0.0)
    positive_rate = safe_float(row.get("positive_test_rate"), 0.0)

    if tests == 0 or trades < 30:
        return "TOO_FEW_TRADES"

    if (
        compound_return > 0.20
        and avg_pf >= 1.20
        and worst_dd > -0.15
        and positive_rate >= 0.55
    ):
        return "WALK_FORWARD_PASS"

    if (
        compound_return > 0.00
        and avg_pf >= 1.05
        and worst_dd > -0.15
        and positive_rate >= 0.45
    ):
        return "WALK_FORWARD_WEAK_PASS"

    if (
        compound_return > -0.05
        and avg_pf >= 0.95
        and worst_dd > -0.12
    ):
        return "WALK_FORWARD_NEAR_BREAKEVEN"

    return "WALK_FORWARD_FAILED"


def slice_by_date(
    df: pd.DataFrame,
    start_date: str,
    end_date: str,
    timestamp_col: str = "timestamp",
) -> pd.DataFrame:
    result = df.copy()

    if timestamp_col not in result.columns:
        raise ValueError(f"Missing timestamp column: {timestamp_col}")

    result[timestamp_col] = pd.to_datetime(result[timestamp_col], errors="coerce")

    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)

    mask = (result[timestamp_col] >= start) & (result[timestamp_col] < end)

    sliced = result.loc[mask].copy()
    sliced = sliced.reset_index(drop=True)

    return sliced


def run_candidate_backtest(
    df: pd.DataFrame,
    strategy_func: Callable,
    base_config,
    candidate: dict,
) -> tuple[pd.DataFrame, dict]:
    config = override_config(
        base_config,
        atr_multiplier=candidate["atr_multiplier"],
        max_holding_bars=candidate["max_holding_bars"],
    )

    exit_profile = build_fixed_rr_exit_profile(
        risk_reward=candidate["risk_reward"],
        profile_name=candidate["candidate_name"],
    )

    return run_active_exit_backtest(
        df=df,
        strategy_func=strategy_func,
        config=config,
        exit_profile=exit_profile,
    )


def select_best_candidate(
    train_df: pd.DataFrame,
    strategy_func: Callable,
    base_config,
    candidates: list[dict],
) -> tuple[dict, pd.DataFrame]:
    rows = []

    best_candidate = None
    best_score = -999999.0

    for candidate in candidates:
        _, summary = run_candidate_backtest(
            df=train_df,
            strategy_func=strategy_func,
            base_config=base_config,
            candidate=candidate,
        )

        score = calculate_selection_score(summary)

        row = {
            "candidate_name": candidate["candidate_name"],
            "risk_reward": candidate["risk_reward"],
            "atr_multiplier": candidate["atr_multiplier"],
            "max_holding_bars": candidate["max_holding_bars"],
            "is_official": bool(candidate["is_official"]),
            "train_trades": int(summary.get("total_trades", 0)),
            "train_return": safe_float(summary.get("total_return_pct"), 0.0),
            "train_profit_factor": summary.get("profit_factor", None),
            "train_expectancy_r": safe_float(summary.get("expectancy_r"), 0.0),
            "train_drawdown": safe_float(summary.get("max_drawdown_pct"), 0.0),
            "selection_score": score,
        }

        rows.append(row)

        if score > best_score:
            best_score = score
            best_candidate = candidate

    return best_candidate, pd.DataFrame(rows)


def summarize_walk_forward_tests(results_df: pd.DataFrame) -> pd.DataFrame:
    if results_df.empty:
        return pd.DataFrame()

    rows = []

    for evaluation_mode, group in results_df.groupby("evaluation_mode"):
        group = group.copy()

        returns = pd.to_numeric(group["test_return"], errors="coerce").fillna(0.0)
        pfs = pd.to_numeric(group["test_profit_factor"], errors="coerce")
        trades = pd.to_numeric(group["test_trades"], errors="coerce").fillna(0)

        row = {
            "evaluation_mode": evaluation_mode,
            "test_windows": int(len(group)),
            "total_test_trades": int(trades.sum()),
            "compound_test_return": float((1 + returns).prod() - 1),
            "avg_test_return": float(returns.mean()),
            "median_test_return": float(returns.median()),
            "avg_test_profit_factor": (
                float(pfs.dropna().mean()) if len(pfs.dropna()) else 0.0
            ),
            "avg_test_expectancy_r": float(
                pd.to_numeric(group["test_expectancy_r"], errors="coerce").mean()
            ),
            "worst_test_drawdown": float(
                pd.to_numeric(group["test_drawdown"], errors="coerce").min()
            ),
            "positive_tests": int((returns > 0).sum()),
            "negative_tests": int((returns <= 0).sum()),
            "positive_test_rate": float((returns > 0).mean()),
        }

        row["walk_forward_decision"] = classify_walk_forward_result(pd.Series(row))

        rows.append(row)

    return pd.DataFrame(rows)


def summarize_selected_candidates(results_df: pd.DataFrame) -> pd.DataFrame:
    if results_df.empty:
        return pd.DataFrame()

    selected = results_df[results_df["evaluation_mode"] == "WALK_FORWARD_SELECTED"]

    if selected.empty:
        return pd.DataFrame()

    summary = (
        selected.groupby("selected_candidate_name")
        .agg(
            selections=("selected_candidate_name", "count"),
            total_test_trades=("test_trades", "sum"),
            avg_test_return=("test_return", "mean"),
            compound_test_return=("test_return", lambda x: float((1 + x).prod() - 1)),
            avg_test_pf=("test_profit_factor", "mean"),
            avg_test_expectancy_r=("test_expectancy_r", "mean"),
            worst_test_drawdown=("test_drawdown", "min"),
            positive_test_rate=("test_return", lambda x: float((x > 0).mean())),
        )
        .reset_index()
    )

    return summary.sort_values(by="selections", ascending=False)