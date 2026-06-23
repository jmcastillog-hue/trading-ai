from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from src.metrics.forward_performance_metrics_v1 import (
    build_equity_curve_df,
    calculate_consecutive_streak,
    calculate_profit_factor,
    normalize_metrics_dataset,
)


@dataclass(frozen=True)
class ForwardRiskRegimeBreakdownConfig:
    min_resolved_observations: int = 100
    preferred_resolved_observations: int = 300
    min_resolved_per_bucket: int = 30
    dangerous_avg_result_r_threshold: float = -0.25
    fragile_avg_result_r_threshold: float = 0.0
    dangerous_profit_factor_threshold: float = 0.75
    fragile_profit_factor_threshold: float = 1.00
    dangerous_single_loss_r_threshold: float = -2.50
    fragile_single_loss_r_threshold: float = -1.00
    dangerous_mae_r_threshold: float = -2.00
    fragile_mae_r_threshold: float = -1.00
    dangerous_consecutive_losses_threshold: int = 4
    fragile_consecutive_losses_threshold: int = 2
    sample_mode: bool = True
    dataset_quality_decision: str = "DATASET_NOT_READY"
    ready_for_phase_4_2_metrics: bool = False
    paper_trade_execution_allowed: bool = False
    real_capital_allowed: bool = False
    live_alerts_allowed: bool = False
    exchange_execution_allowed: bool = False
    automation_allowed: bool = False


REQUIRED_COLUMNS = [
    "signal_id",
    "observed_at",
    "symbol",
    "timeframe",
    "cost_profile",
    "context_name",
    "direction",
    "resolution_status",
    "result_r",
    "mfe_r",
    "mae_r",
    "bars_to_resolution",
]


def safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except Exception:
        pass

    return str(value).strip()


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or pd.isna(value):
            return default
        return int(value)
    except Exception:
        return default


def validate_risk_regime_input(dataset_df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for column in REQUIRED_COLUMNS:
        passed = column in dataset_df.columns

        rows.append(
            {
                "check_name": f"required_column:{column}",
                "passed": passed,
                "severity": "ERROR",
                "details": "OK" if passed else "MISSING",
            }
        )

    rows.append(
        {
            "check_name": "has_rows",
            "passed": len(dataset_df) > 0,
            "severity": "ERROR",
            "details": f"rows={len(dataset_df)}",
        }
    )

    return pd.DataFrame(rows)


def infer_market_regime(context_name: str) -> str:
    context = safe_str(context_name).upper()

    if "STRESS" in context or "DEGRADED" in context or "BLOCKED" in context:
        return "DEGRADED_OR_STRESS_REGIME"

    if "WAVE_5" in context or "CAUTION" in context:
        return "CAUTION_REGIME"

    if "WAVE_3" in context or "OPPORTUNITY" in context:
        return "OPPORTUNITY_REGIME"

    if "STRONG" in context or "MTF" in context:
        return "STRONG_CONTEXT_REGIME"

    if "NORMAL" in context:
        return "NORMAL_VALIDATION_REGIME"

    if "MIXED" in context or "UNCLEAR" in context:
        return "MIXED_OR_UNCLEAR_REGIME"

    return "UNCLASSIFIED_REGIME"


def infer_cost_regime(cost_profile: str) -> str:
    profile = safe_str(cost_profile).upper()

    if "EXTREME" in profile:
        return "EXTREME_COST_REGIME"

    if "STRESS" in profile:
        return "STRESS_COST_REGIME"

    if "BINANCE" in profile and "SCALP" in profile:
        return "BINANCE_SCALP_BASE_REGIME"

    if "QUANTFURY" in profile and "SWING" in profile:
        return "QUANTFURY_SWING_BASE_REGIME"

    if "BINANCE" in profile:
        return "BINANCE_REGIME"

    if "QUANTFURY" in profile:
        return "QUANTFURY_REGIME"

    return "UNCLASSIFIED_COST_REGIME"


def enrich_regime_columns(metrics_df: pd.DataFrame) -> pd.DataFrame:
    df = metrics_df.copy()

    if "context_name" not in df.columns:
        df["context_name"] = ""

    if "cost_profile" not in df.columns:
        df["cost_profile"] = ""

    df["market_regime"] = df["context_name"].map(infer_market_regime)
    df["cost_regime"] = df["cost_profile"].map(infer_cost_regime)

    df["is_caution_regime"] = df["market_regime"].eq("CAUTION_REGIME")
    df["is_degraded_or_stress_regime"] = df["market_regime"].eq(
        "DEGRADED_OR_STRESS_REGIME"
    ) | df["cost_regime"].isin(
        {
            "STRESS_COST_REGIME",
            "EXTREME_COST_REGIME",
        }
    )

    return df


def calculate_group_risk_metrics(group_df: pd.DataFrame) -> dict[str, Any]:
    resolved_df = group_df[group_df["is_closed"]].copy()

    total_observations = len(group_df)
    resolved_observations = len(resolved_df)
    open_observations = int(group_df["is_open"].sum()) if not group_df.empty else 0
    error_observations = int(group_df["is_error"].sum()) if not group_df.empty else 0

    if resolved_df.empty:
        return {
            "total_observations": total_observations,
            "resolved_observations": 0,
            "open_observations": open_observations,
            "error_observations": error_observations,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0,
            "loss_rate": 0.0,
            "avg_result_r": 0.0,
            "sum_result_r": 0.0,
            "profit_factor": 0.0,
            "gross_profit_r": 0.0,
            "gross_loss_r": 0.0,
            "max_drawdown_r": 0.0,
            "ending_equity_r": 0.0,
            "best_result_r": 0.0,
            "worst_result_r": 0.0,
            "avg_mfe_r": 0.0,
            "avg_mae_r": 0.0,
            "worst_mae_r": 0.0,
            "avg_bars_to_resolution": 0.0,
            "max_consecutive_wins": 0,
            "max_consecutive_losses": 0,
            "downside_trade_ratio": 0.0,
        }

    wins = int((resolved_df["result_r"] > 0).sum())
    losses = int((resolved_df["result_r"] < 0).sum())

    gross_profit_r = float(resolved_df.loc[resolved_df["result_r"] > 0, "result_r"].sum())
    gross_loss_r = abs(float(resolved_df.loc[resolved_df["result_r"] < 0, "result_r"].sum()))

    equity_curve_df = build_equity_curve_df(resolved_df)

    if equity_curve_df.empty:
        max_drawdown_r = 0.0
        ending_equity_r = 0.0
    else:
        max_drawdown_r = round(float(equity_curve_df["drawdown_r"].min()), 6)
        ending_equity_r = round(float(equity_curve_df["equity_r"].iloc[-1]), 6)

    win_sequence = (resolved_df["result_r"] > 0).tolist()
    loss_sequence = (resolved_df["result_r"] < 0).tolist()

    return {
        "total_observations": total_observations,
        "resolved_observations": resolved_observations,
        "open_observations": open_observations,
        "error_observations": error_observations,
        "wins": wins,
        "losses": losses,
        "win_rate": round(float((resolved_df["result_r"] > 0).mean()), 6),
        "loss_rate": round(float((resolved_df["result_r"] < 0).mean()), 6),
        "avg_result_r": round(float(resolved_df["result_r"].mean()), 6),
        "sum_result_r": round(float(resolved_df["result_r"].sum()), 6),
        "profit_factor": calculate_profit_factor(resolved_df),
        "gross_profit_r": round(gross_profit_r, 6),
        "gross_loss_r": round(gross_loss_r, 6),
        "max_drawdown_r": max_drawdown_r,
        "ending_equity_r": ending_equity_r,
        "best_result_r": round(float(resolved_df["result_r"].max()), 6),
        "worst_result_r": round(float(resolved_df["result_r"].min()), 6),
        "avg_mfe_r": round(float(resolved_df["mfe_r"].mean()), 6),
        "avg_mae_r": round(float(resolved_df["mae_r"].mean()), 6),
        "worst_mae_r": round(float(resolved_df["mae_r"].min()), 6),
        "avg_bars_to_resolution": round(float(resolved_df["bars_to_resolution"].mean()), 6),
        "max_consecutive_wins": calculate_consecutive_streak(win_sequence),
        "max_consecutive_losses": calculate_consecutive_streak(loss_sequence),
        "downside_trade_ratio": round(float((resolved_df["result_r"] < 0).mean()), 6),
    }


def classify_risk_bucket(
    risk_row: pd.Series,
    config: ForwardRiskRegimeBreakdownConfig,
) -> tuple[str, str, str]:
    resolved = safe_int(risk_row.get("resolved_observations"))
    avg_result_r = safe_float(risk_row.get("avg_result_r"))
    profit_factor = safe_float(risk_row.get("profit_factor"))
    worst_result_r = safe_float(risk_row.get("worst_result_r"))
    worst_mae_r = safe_float(risk_row.get("worst_mae_r"))
    max_consecutive_losses = safe_int(risk_row.get("max_consecutive_losses"))

    if resolved <= 0:
        return (
            "NO_RESOLVED_RISK_DATA",
            "INSUFFICIENT_DATA",
            "No resolved observations available for this risk bucket.",
        )

    if resolved < config.min_resolved_per_bucket:
        if avg_result_r > 0:
            return (
                "PROVISIONAL_POSITIVE_RISK_BUCKET_INSUFFICIENT_SAMPLE",
                "INSUFFICIENT_SAMPLE",
                (
                    f"Positive risk bucket, but only {resolved}/"
                    f"{config.min_resolved_per_bucket} resolved observations."
                ),
            )

        if avg_result_r < 0:
            return (
                "PROVISIONAL_NEGATIVE_RISK_BUCKET_INSUFFICIENT_SAMPLE",
                "INSUFFICIENT_SAMPLE",
                (
                    f"Negative risk bucket, but only {resolved}/"
                    f"{config.min_resolved_per_bucket} resolved observations."
                ),
            )

        return (
            "PROVISIONAL_NEUTRAL_RISK_BUCKET_INSUFFICIENT_SAMPLE",
            "INSUFFICIENT_SAMPLE",
            (
                f"Neutral risk bucket, but only {resolved}/"
                f"{config.min_resolved_per_bucket} resolved observations."
            ),
        )

    if (
        avg_result_r <= config.dangerous_avg_result_r_threshold
        or profit_factor < config.dangerous_profit_factor_threshold
        or worst_result_r <= config.dangerous_single_loss_r_threshold
        or worst_mae_r <= config.dangerous_mae_r_threshold
        or max_consecutive_losses >= config.dangerous_consecutive_losses_threshold
    ):
        return (
            "DANGEROUS_RISK_REGIME_CANDIDATE",
            "DANGEROUS",
            "Bucket breaches dangerous risk thresholds.",
        )

    if (
        avg_result_r <= config.fragile_avg_result_r_threshold
        or profit_factor < config.fragile_profit_factor_threshold
        or worst_result_r <= config.fragile_single_loss_r_threshold
        or worst_mae_r <= config.fragile_mae_r_threshold
        or max_consecutive_losses >= config.fragile_consecutive_losses_threshold
    ):
        return (
            "FRAGILE_RISK_REGIME_CANDIDATE",
            "FRAGILE",
            "Bucket shows fragile or weak risk characteristics.",
        )

    return (
        "NORMAL_RISK_REGIME_CANDIDATE",
        "NORMAL",
        "Bucket does not breach risk thresholds.",
    )


def build_risk_breakdown_df(
    metrics_df: pd.DataFrame,
    group_columns: list[str],
    analysis_scope: str,
    config: ForwardRiskRegimeBreakdownConfig,
) -> pd.DataFrame:
    if metrics_df.empty:
        return pd.DataFrame()

    rows = []

    for group_key, group_df in metrics_df.groupby(group_columns, dropna=False):
        group_values = group_key if isinstance(group_key, tuple) else (group_key,)

        row = {
            "analysis_scope": analysis_scope,
            "paper_trade_execution_allowed": False,
            "real_capital_allowed": False,
            "live_alerts_allowed": False,
            "exchange_execution_allowed": False,
            "automation_allowed": False,
        }

        for column, value in zip(group_columns, group_values):
            row[column] = value

        row.update(calculate_group_risk_metrics(group_df))

        risk_signal, risk_label, risk_reason = classify_risk_bucket(
            pd.Series(row),
            config,
        )

        row["risk_signal"] = risk_signal
        row["risk_label"] = risk_label
        row["risk_reason"] = risk_reason
        row["sample_sufficient_for_bucket"] = (
            safe_int(row.get("resolved_observations")) >= config.min_resolved_per_bucket
        )

        if "context_name" in row:
            row["market_regime"] = infer_market_regime(row["context_name"])

        if "cost_profile" in row:
            row["cost_regime"] = infer_cost_regime(row["cost_profile"])

        rows.append(row)

    result_df = pd.DataFrame(rows)

    if result_df.empty:
        return result_df

    return result_df.sort_values(
        by=["sample_sufficient_for_bucket", "resolved_observations", "avg_result_r"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


def build_risk_event_log(metrics_df: pd.DataFrame) -> pd.DataFrame:
    if metrics_df.empty:
        return pd.DataFrame()

    resolved_df = metrics_df[metrics_df["is_closed"]].copy()

    if resolved_df.empty:
        return pd.DataFrame()

    rows = []

    for _, row in resolved_df.iterrows():
        result_r = safe_float(row.get("result_r"))
        mae_r = safe_float(row.get("mae_r"))

        if result_r < 0:
            event_type = "LOSS_EVENT"
        elif result_r > 0:
            event_type = "WIN_EVENT"
        else:
            event_type = "BREAKEVEN_EVENT"

        if result_r <= -2.5 or mae_r <= -2.0:
            severity = "HIGH"
        elif result_r < 0 or mae_r <= -1.0:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        rows.append(
            {
                "signal_id": row.get("signal_id", ""),
                "observed_at": row.get("observed_at", ""),
                "symbol": row.get("symbol", ""),
                "timeframe": row.get("timeframe", ""),
                "context_name": row.get("context_name", ""),
                "market_regime": row.get("market_regime", ""),
                "cost_profile": row.get("cost_profile", ""),
                "cost_regime": row.get("cost_regime", ""),
                "direction": row.get("direction", ""),
                "resolution_status": row.get("resolution_status", ""),
                "result_r": result_r,
                "mfe_r": safe_float(row.get("mfe_r")),
                "mae_r": mae_r,
                "bars_to_resolution": safe_float(row.get("bars_to_resolution")),
                "risk_event_type": event_type,
                "risk_event_severity": severity,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
            }
        )

    result_df = pd.DataFrame(rows)

    return result_df.sort_values(
        by=["risk_event_severity", "observed_at"],
        ascending=[True, True],
    ).reset_index(drop=True)


def build_risk_regime_summary_df(
    dataset_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    risk_by_context_df: pd.DataFrame,
    risk_event_log_df: pd.DataFrame,
    config: ForwardRiskRegimeBreakdownConfig,
) -> pd.DataFrame:
    validation_passed = bool(validation_df["passed"].all()) if not validation_df.empty else False

    metrics_df = enrich_regime_columns(normalize_metrics_dataset(dataset_df))
    resolved_observations = int(metrics_df["is_closed"].sum()) if not metrics_df.empty else 0
    total_observations = len(metrics_df)

    minimum_sample_reached = resolved_observations >= config.min_resolved_observations
    preferred_sample_reached = resolved_observations >= config.preferred_resolved_observations

    global_risk = calculate_group_risk_metrics(metrics_df)

    if risk_by_context_df.empty:
        buckets_analyzed = 0
        insufficient_buckets = 0
        provisional_positive_buckets = 0
        provisional_negative_buckets = 0
        normal_buckets = 0
        fragile_buckets = 0
        dangerous_buckets = 0
    else:
        buckets_analyzed = len(risk_by_context_df)
        insufficient_buckets = int(risk_by_context_df["risk_label"].eq("INSUFFICIENT_SAMPLE").sum())
        provisional_positive_buckets = int(
            risk_by_context_df["risk_signal"]
            .eq("PROVISIONAL_POSITIVE_RISK_BUCKET_INSUFFICIENT_SAMPLE")
            .sum()
        )
        provisional_negative_buckets = int(
            risk_by_context_df["risk_signal"]
            .eq("PROVISIONAL_NEGATIVE_RISK_BUCKET_INSUFFICIENT_SAMPLE")
            .sum()
        )
        normal_buckets = int(risk_by_context_df["risk_label"].eq("NORMAL").sum())
        fragile_buckets = int(risk_by_context_df["risk_label"].eq("FRAGILE").sum())
        dangerous_buckets = int(risk_by_context_df["risk_label"].eq("DANGEROUS").sum())

    high_risk_events = 0

    if not risk_event_log_df.empty:
        high_risk_events = int(risk_event_log_df["risk_event_severity"].eq("HIGH").sum())

    if not validation_passed:
        analyzer_decision = "RISK_REGIME_ANALYZER_INPUT_VALIDATION_FAILED"
    elif config.sample_mode:
        analyzer_decision = "RISK_REGIME_ANALYZER_VALIDATED_SAMPLE_ONLY"
    elif not config.ready_for_phase_4_2_metrics:
        analyzer_decision = "RISK_REGIME_ANALYZER_BLOCKED_BY_DATASET_QUALITY_GATE"
    elif not minimum_sample_reached:
        analyzer_decision = "RISK_REGIME_ANALYZER_INSUFFICIENT_FORWARD_EVIDENCE"
    else:
        analyzer_decision = "RISK_REGIME_ANALYZER_COMPLETED"

    return pd.DataFrame(
        [
            {
                "validation_passed": validation_passed,
                "dataset_quality_decision": config.dataset_quality_decision,
                "ready_for_phase_4_2_metrics": config.ready_for_phase_4_2_metrics,
                "sample_mode": config.sample_mode,
                "total_observations": total_observations,
                "resolved_observations": resolved_observations,
                "min_resolved_observations": config.min_resolved_observations,
                "preferred_resolved_observations": config.preferred_resolved_observations,
                "minimum_sample_reached": minimum_sample_reached,
                "preferred_sample_reached": preferred_sample_reached,
                "buckets_analyzed": buckets_analyzed,
                "insufficient_buckets": insufficient_buckets,
                "provisional_positive_buckets": provisional_positive_buckets,
                "provisional_negative_buckets": provisional_negative_buckets,
                "normal_buckets": normal_buckets,
                "fragile_buckets": fragile_buckets,
                "dangerous_buckets": dangerous_buckets,
                "high_risk_events": high_risk_events,
                "global_sum_result_r": global_risk["sum_result_r"],
                "global_avg_result_r": global_risk["avg_result_r"],
                "global_profit_factor": global_risk["profit_factor"],
                "global_max_drawdown_r": global_risk["max_drawdown_r"],
                "global_worst_result_r": global_risk["worst_result_r"],
                "global_worst_mae_r": global_risk["worst_mae_r"],
                "global_max_consecutive_losses": global_risk["max_consecutive_losses"],
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "analyzer_decision": analyzer_decision,
            }
        ]
    )


def build_risk_regime_notes_df(
    summary_df: pd.DataFrame,
    config: ForwardRiskRegimeBreakdownConfig,
) -> pd.DataFrame:
    if summary_df.empty:
        return pd.DataFrame(
            [
                {
                    "note_type": "risk_regime_analyzer",
                    "severity": "WARNING",
                    "message": "No risk regime summary generated.",
                }
            ]
        )

    summary = summary_df.iloc[0]
    resolved = safe_int(summary.get("resolved_observations"))
    notes = []

    if resolved < config.min_resolved_observations:
        notes.append(
            {
                "note_type": "sample_size",
                "severity": "CONTROL",
                "message": (
                    f"Risk/regime conclusions are not operational: "
                    f"{resolved}/{config.min_resolved_observations} resolved observations."
                ),
            }
        )

    if safe_int(summary.get("global_max_consecutive_losses")) > 0:
        notes.append(
            {
                "note_type": "sequence_risk",
                "severity": "INFO",
                "message": (
                    f"Observed max consecutive losses in sample: "
                    f"{safe_int(summary.get('global_max_consecutive_losses'))}."
                ),
            }
        )

    if safe_float(summary.get("global_max_drawdown_r")) < 0:
        notes.append(
            {
                "note_type": "drawdown",
                "severity": "INFO",
                "message": (
                    f"Observed max drawdown in sample: "
                    f"{safe_float(summary.get('global_max_drawdown_r'))}R."
                ),
            }
        )

    if config.sample_mode:
        notes.append(
            {
                "note_type": "sample_mode",
                "severity": "CONTROL",
                "message": "Risk/regime analyzer validated in sample mode only.",
            }
        )

    notes.append(
        {
            "note_type": "execution_restriction",
            "severity": "CONTROL",
            "message": (
                "This analyzer does not enable real capital, executed paper trading, "
                "live alerts, exchange execution, or automation."
            ),
        }
    )

    return pd.DataFrame(notes)


def run_forward_risk_regime_breakdown_analyzer(
    dataset_df: pd.DataFrame,
    config: ForwardRiskRegimeBreakdownConfig | None = None,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    if config is None:
        config = ForwardRiskRegimeBreakdownConfig()

    validation_df = validate_risk_regime_input(dataset_df)

    metrics_df = normalize_metrics_dataset(dataset_df)
    metrics_df = enrich_regime_columns(metrics_df)

    risk_by_context_df = build_risk_breakdown_df(
        metrics_df=metrics_df,
        group_columns=["context_name"],
        analysis_scope="CONTEXT",
        config=config,
    )

    risk_by_cost_profile_df = build_risk_breakdown_df(
        metrics_df=metrics_df,
        group_columns=["cost_profile"],
        analysis_scope="COST_PROFILE",
        config=config,
    )

    risk_by_direction_df = build_risk_breakdown_df(
        metrics_df=metrics_df,
        group_columns=["direction"],
        analysis_scope="DIRECTION",
        config=config,
    )

    risk_by_context_cost_profile_df = build_risk_breakdown_df(
        metrics_df=metrics_df,
        group_columns=["context_name", "cost_profile"],
        analysis_scope="CONTEXT_COST_PROFILE",
        config=config,
    )

    risk_by_market_cost_regime_df = build_risk_breakdown_df(
        metrics_df=metrics_df,
        group_columns=["market_regime", "cost_regime"],
        analysis_scope="MARKET_COST_REGIME",
        config=config,
    )

    risk_by_resolution_status_df = build_risk_breakdown_df(
        metrics_df=metrics_df,
        group_columns=["resolution_status"],
        analysis_scope="RESOLUTION_STATUS",
        config=config,
    )

    risk_event_log_df = build_risk_event_log(metrics_df)

    summary_df = build_risk_regime_summary_df(
        dataset_df=dataset_df,
        validation_df=validation_df,
        risk_by_context_df=risk_by_context_df,
        risk_event_log_df=risk_event_log_df,
        config=config,
    )

    notes_df = build_risk_regime_notes_df(
        summary_df=summary_df,
        config=config,
    )

    return (
        summary_df,
        validation_df,
        risk_by_context_df,
        risk_by_cost_profile_df,
        risk_by_direction_df,
        risk_by_context_cost_profile_df,
        risk_by_market_cost_regime_df,
        risk_by_resolution_status_df,
        risk_event_log_df,
        notes_df,
    )