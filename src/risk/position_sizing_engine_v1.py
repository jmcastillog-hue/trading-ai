from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class PositionSizingScenario:
    scenario_name: str
    risk_per_trade_pct: float
    mode: str
    description: str


@dataclass(frozen=True)
class PositionSizingConfig:
    simulations: int = 10000
    random_seed: int = 42
    min_trades: int = 30
    initial_equity: float = 1.0
    sample_with_replacement: bool = True


def safe_float(value, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def build_position_sizing_scenarios() -> list[PositionSizingScenario]:
    return [
        PositionSizingScenario(
            scenario_name="RISK_0_25_DEFENSIVE",
            risk_per_trade_pct=0.0025,
            mode="DEFENSIVE",
            description="Riesgo muy bajo para validar estabilidad sin presion psicologica.",
        ),
        PositionSizingScenario(
            scenario_name="RISK_0_50_CONSERVATIVE",
            risk_per_trade_pct=0.0050,
            mode="CONSERVATIVE",
            description="Riesgo conservador para una estrategia aun en validacion.",
        ),
        PositionSizingScenario(
            scenario_name="RISK_1_00_BASE",
            risk_per_trade_pct=0.0100,
            mode="BASE",
            description="Riesgo base del sistema para comparar contra Fase 2.2 y 2.3.",
        ),
        PositionSizingScenario(
            scenario_name="RISK_1_50_AGGRESSIVE",
            risk_per_trade_pct=0.0150,
            mode="AGGRESSIVE",
            description="Riesgo agresivo controlado, solo aceptable con edge robusto.",
        ),
        PositionSizingScenario(
            scenario_name="RISK_2_00_OPPORTUNITY",
            risk_per_trade_pct=0.0200,
            mode="OPPORTUNITY",
            description="Riesgo de oportunidad; requiere contexto macro/MTF fuerte.",
        ),
        PositionSizingScenario(
            scenario_name="RISK_3_00_EXTREME",
            risk_per_trade_pct=0.0300,
            mode="EXTREME",
            description="Riesgo extremo; solo para diagnostico, no operativo por defecto.",
        ),
    ]


def calculate_equity_curve(
    result_r_values: np.ndarray,
    risk_per_trade_pct: float,
    initial_equity: float = 1.0,
) -> np.ndarray:
    equity_values = []
    equity = initial_equity

    for result_r in result_r_values:
        trade_return = float(result_r) * risk_per_trade_pct
        equity *= 1.0 + trade_return
        equity_values.append(equity)

    return np.array(equity_values, dtype=float)


def calculate_max_drawdown(equity_curve: np.ndarray) -> float:
    if len(equity_curve) == 0:
        return 0.0

    peaks = np.maximum.accumulate(equity_curve)
    drawdowns = equity_curve / peaks - 1.0

    return float(drawdowns.min())


def calculate_max_losing_streak(result_r_values: np.ndarray) -> int:
    max_streak = 0
    current_streak = 0

    for value in result_r_values:
        if value <= 0:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0

    return int(max_streak)


def prepare_profile_results(
    trades_df: pd.DataFrame,
    cost_profile: str,
) -> pd.DataFrame:
    if trades_df.empty:
        return pd.DataFrame()

    required_columns = [
        "cost_profile",
        "cost_adjusted_result_r",
    ]

    for column in required_columns:
        if column not in trades_df.columns:
            raise ValueError(f"Missing required column: {column}")

    profile_df = trades_df[trades_df["cost_profile"] == cost_profile].copy()

    profile_df["cost_adjusted_result_r"] = pd.to_numeric(
        profile_df["cost_adjusted_result_r"],
        errors="coerce",
    )

    profile_df = profile_df.dropna(subset=["cost_adjusted_result_r"])

    return profile_df.reset_index(drop=True)


def percentile(series: pd.Series, q: float) -> float:
    return float(series.quantile(q))


def classify_position_sizing_summary(summary: dict) -> str:
    sample_trades = int(summary.get("sample_trades", 0))
    risk_pct = safe_float(summary.get("risk_per_trade_pct"), 0.0)
    p05_return = safe_float(summary.get("p05_return"), 0.0)
    p01_return = safe_float(summary.get("p01_return"), 0.0)
    p01_drawdown = safe_float(summary.get("p01_max_drawdown"), 0.0)
    probability_negative = safe_float(summary.get("probability_negative_return"), 1.0)
    probability_dd_20 = safe_float(summary.get("probability_drawdown_below_20pct"), 1.0)
    probability_dd_30 = safe_float(summary.get("probability_drawdown_below_30pct"), 1.0)
    p99_losing_streak = safe_float(summary.get("p99_losing_streak"), 99.0)

    if sample_trades < 30:
        return "TOO_FEW_TRADES"

    if (
        risk_pct <= 0.005
        and p05_return > 0.0
        and p01_drawdown > -0.15
        and probability_negative <= 0.05
        and p99_losing_streak <= 12
    ):
        return "POSITION_SIZE_ROBUST"

    if (
        risk_pct <= 0.010
        and p05_return > 0.0
        and p01_return > -0.10
        and p01_drawdown > -0.25
        and probability_negative <= 0.05
        and probability_dd_20 <= 0.05
    ):
        return "POSITION_SIZE_BASE_ACCEPTABLE"

    if (
        risk_pct <= 0.020
        and p05_return > -0.10
        and p01_drawdown > -0.40
        and probability_negative <= 0.15
        and probability_dd_30 <= 0.15
    ):
        return "POSITION_SIZE_AGGRESSIVE_ONLY_WITH_CONTEXT"

    if (
        risk_pct <= 0.030
        and p01_drawdown > -0.55
        and probability_negative <= 0.30
    ):
        return "POSITION_SIZE_EXTREME_DIAGNOSTIC_ONLY"

    return "POSITION_SIZE_REJECTED"


def run_position_sizing_for_profile(
    trades_df: pd.DataFrame,
    cost_profile: str,
    scenario: PositionSizingScenario,
    config: PositionSizingConfig | None = None,
) -> tuple[pd.DataFrame, dict]:
    if config is None:
        config = PositionSizingConfig()

    profile_df = prepare_profile_results(
        trades_df=trades_df,
        cost_profile=cost_profile,
    )

    if len(profile_df) < config.min_trades:
        summary = {
            "cost_profile": cost_profile,
            "scenario_name": scenario.scenario_name,
            "risk_per_trade_pct": scenario.risk_per_trade_pct,
            "mode": scenario.mode,
            "simulations": 0,
            "sample_trades": int(len(profile_df)),
            "decision": "TOO_FEW_TRADES",
        }

        return pd.DataFrame(), summary

    result_r_values = profile_df["cost_adjusted_result_r"].to_numpy(dtype=float)
    trade_count = len(result_r_values)

    rng = np.random.default_rng(config.random_seed)

    rows = []

    for simulation_id in range(config.simulations):
        if config.sample_with_replacement:
            indexes = rng.integers(
                low=0,
                high=trade_count,
                size=trade_count,
            )
        else:
            indexes = rng.permutation(trade_count)

        simulated_r = result_r_values[indexes]

        equity_curve = calculate_equity_curve(
            result_r_values=simulated_r,
            risk_per_trade_pct=scenario.risk_per_trade_pct,
            initial_equity=config.initial_equity,
        )

        final_equity = float(equity_curve[-1])
        total_return = final_equity / config.initial_equity - 1.0
        max_drawdown = calculate_max_drawdown(equity_curve)
        max_losing_streak = calculate_max_losing_streak(simulated_r)

        rows.append(
            {
                "cost_profile": cost_profile,
                "scenario_name": scenario.scenario_name,
                "risk_per_trade_pct": scenario.risk_per_trade_pct,
                "mode": scenario.mode,
                "simulation_id": simulation_id,
                "trade_count": trade_count,
                "final_equity": final_equity,
                "total_return": total_return,
                "max_drawdown": max_drawdown,
                "max_losing_streak": max_losing_streak,
                "avg_result_r": float(simulated_r.mean()),
                "win_rate": float((simulated_r > 0).mean()),
            }
        )

    simulations_df = pd.DataFrame(rows)

    summary = summarize_position_sizing_result(
        simulations_df=simulations_df,
        raw_result_r_values=result_r_values,
        cost_profile=cost_profile,
        scenario=scenario,
        config=config,
    )

    return simulations_df, summary


def summarize_position_sizing_result(
    simulations_df: pd.DataFrame,
    raw_result_r_values: np.ndarray,
    cost_profile: str,
    scenario: PositionSizingScenario,
    config: PositionSizingConfig,
) -> dict:
    if simulations_df.empty:
        return {
            "cost_profile": cost_profile,
            "scenario_name": scenario.scenario_name,
            "risk_per_trade_pct": scenario.risk_per_trade_pct,
            "mode": scenario.mode,
            "simulations": 0,
            "sample_trades": int(len(raw_result_r_values)),
            "decision": "TOO_FEW_TRADES",
        }

    total_returns = pd.to_numeric(
        simulations_df["total_return"],
        errors="coerce",
    ).fillna(0.0)

    max_drawdowns = pd.to_numeric(
        simulations_df["max_drawdown"],
        errors="coerce",
    ).fillna(0.0)

    losing_streaks = pd.to_numeric(
        simulations_df["max_losing_streak"],
        errors="coerce",
    ).fillna(0)

    raw_equity_curve = calculate_equity_curve(
        result_r_values=raw_result_r_values,
        risk_per_trade_pct=scenario.risk_per_trade_pct,
        initial_equity=config.initial_equity,
    )

    raw_sequence_return = float(raw_equity_curve[-1] / config.initial_equity - 1.0)
    raw_sequence_drawdown = calculate_max_drawdown(raw_equity_curve)
    raw_sequence_losing_streak = calculate_max_losing_streak(raw_result_r_values)

    summary = {
        "cost_profile": cost_profile,
        "scenario_name": scenario.scenario_name,
        "risk_per_trade_pct": scenario.risk_per_trade_pct,
        "mode": scenario.mode,
        "description": scenario.description,
        "simulations": int(len(simulations_df)),
        "sample_trades": int(len(raw_result_r_values)),
        "raw_sequence_return": raw_sequence_return,
        "raw_sequence_max_drawdown": raw_sequence_drawdown,
        "raw_sequence_max_losing_streak": raw_sequence_losing_streak,
        "median_return": percentile(total_returns, 0.50),
        "p05_return": percentile(total_returns, 0.05),
        "p01_return": percentile(total_returns, 0.01),
        "p95_return": percentile(total_returns, 0.95),
        "median_max_drawdown": percentile(max_drawdowns, 0.50),
        "p05_max_drawdown": percentile(max_drawdowns, 0.05),
        "p01_max_drawdown": percentile(max_drawdowns, 0.01),
        "p95_max_drawdown": percentile(max_drawdowns, 0.95),
        "median_losing_streak": percentile(losing_streaks, 0.50),
        "p95_losing_streak": percentile(losing_streaks, 0.95),
        "p99_losing_streak": percentile(losing_streaks, 0.99),
        "probability_negative_return": float((total_returns < 0).mean()),
        "probability_drawdown_below_15pct": float((max_drawdowns <= -0.15).mean()),
        "probability_drawdown_below_20pct": float((max_drawdowns <= -0.20).mean()),
        "probability_drawdown_below_30pct": float((max_drawdowns <= -0.30).mean()),
        "avg_result_r": float(np.mean(raw_result_r_values)),
        "win_rate": float((raw_result_r_values > 0).mean()),
    }

    summary["decision"] = classify_position_sizing_summary(summary)

    return summary


def summarize_position_sizing_profiles(summary_df: pd.DataFrame) -> pd.DataFrame:
    if summary_df.empty:
        return pd.DataFrame()

    return summary_df.sort_values(
        by=[
            "cost_profile",
            "risk_per_trade_pct",
        ],
        ascending=[
            True,
            True,
        ],
    ).reset_index(drop=True)


def select_recommended_size(summary_df: pd.DataFrame) -> pd.DataFrame:
    if summary_df.empty:
        return pd.DataFrame()

    allowed_decisions = [
        "POSITION_SIZE_ROBUST",
        "POSITION_SIZE_BASE_ACCEPTABLE",
        "POSITION_SIZE_AGGRESSIVE_ONLY_WITH_CONTEXT",
    ]

    allowed = summary_df[summary_df["decision"].isin(allowed_decisions)].copy()

    if allowed.empty:
        return pd.DataFrame()

    allowed["decision_rank"] = allowed["decision"].map(
        {
            "POSITION_SIZE_ROBUST": 1,
            "POSITION_SIZE_BASE_ACCEPTABLE": 2,
            "POSITION_SIZE_AGGRESSIVE_ONLY_WITH_CONTEXT": 3,
        }
    )

    recommended = (
        allowed.sort_values(
            by=[
                "cost_profile",
                "decision_rank",
                "risk_per_trade_pct",
            ],
            ascending=[
                True,
                True,
                False,
            ],
        )
        .groupby("cost_profile")
        .head(1)
        .reset_index(drop=True)
    )

    return recommended.drop(columns=["decision_rank"])