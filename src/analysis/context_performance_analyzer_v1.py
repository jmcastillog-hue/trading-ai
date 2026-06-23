from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from src.metrics.forward_performance_metrics_v1 import (
    build_group_metrics_df,
    normalize_metrics_dataset,
)


@dataclass(frozen=True)
class ContextPerformanceAnalyzerConfig:
    min_resolved_observations: int = 100
    preferred_resolved_observations: int = 300
    min_resolved_per_context: int = 30
    strong_avg_result_r_threshold: float = 0.20
    weak_avg_result_r_threshold: float = 0.00
    strong_profit_factor_threshold: float = 1.25
    weak_profit_factor_threshold: float = 1.00
    strong_win_rate_threshold: float = 0.45
    dangerous_avg_result_r_threshold: float = -0.25
    dangerous_profit_factor_threshold: float = 0.75
    sample_mode: bool = True
    dataset_quality_decision: str = "DATASET_NOT_READY"
    ready_for_phase_4_2_metrics: bool = False
    paper_trade_execution_allowed: bool = False
    real_capital_allowed: bool = False
    live_alerts_allowed: bool = False
    exchange_execution_allowed: bool = False
    automation_allowed: bool = False


REQUIRED_METRIC_COLUMNS = [
    "resolved_observations",
    "wins",
    "losses",
    "win_rate",
    "avg_result_r",
    "sum_result_r",
    "profit_factor",
    "max_drawdown_r",
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


def validate_context_analyzer_input(dataset_df: pd.DataFrame) -> pd.DataFrame:
    required_columns = [
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

    rows = []

    for column in required_columns:
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


def classify_group_performance(
    row: pd.Series,
    config: ContextPerformanceAnalyzerConfig,
) -> tuple[str, str, str]:
    resolved = safe_int(row.get("resolved_observations"))
    avg_result_r = safe_float(row.get("avg_result_r"))
    profit_factor = safe_float(row.get("profit_factor"))
    win_rate = safe_float(row.get("win_rate"))

    if resolved <= 0:
        return (
            "NO_RESOLVED_OBSERVATIONS",
            "INSUFFICIENT_DATA",
            "No resolved observations available.",
        )

    if resolved < config.min_resolved_per_context:
        if avg_result_r > 0:
            return (
                "PROVISIONAL_POSITIVE_INSUFFICIENT_SAMPLE",
                "INSUFFICIENT_SAMPLE",
                (
                    f"Positive sample, but only {resolved}/"
                    f"{config.min_resolved_per_context} observations."
                ),
            )

        if avg_result_r < 0:
            return (
                "PROVISIONAL_NEGATIVE_INSUFFICIENT_SAMPLE",
                "INSUFFICIENT_SAMPLE",
                (
                    f"Negative sample, but only {resolved}/"
                    f"{config.min_resolved_per_context} observations."
                ),
            )

        return (
            "PROVISIONAL_NEUTRAL_INSUFFICIENT_SAMPLE",
            "INSUFFICIENT_SAMPLE",
            (
                f"Neutral sample, but only {resolved}/"
                f"{config.min_resolved_per_context} observations."
            ),
        )

    if (
        avg_result_r >= config.strong_avg_result_r_threshold
        and profit_factor >= config.strong_profit_factor_threshold
        and win_rate >= config.strong_win_rate_threshold
    ):
        return (
            "CONTEXT_STRONG_CANDIDATE",
            "POTENTIALLY_SUPPORTIVE",
            "Context meets provisional positive performance thresholds.",
        )

    if (
        avg_result_r <= config.dangerous_avg_result_r_threshold
        or profit_factor < config.dangerous_profit_factor_threshold
    ):
        return (
            "CONTEXT_DANGEROUS_CANDIDATE",
            "POTENTIALLY_DANGEROUS",
            "Context shows negative or poor risk-adjusted performance.",
        )

    if (
        avg_result_r <= config.weak_avg_result_r_threshold
        or profit_factor < config.weak_profit_factor_threshold
    ):
        return (
            "CONTEXT_WEAK_CANDIDATE",
            "WEAK_OR_UNCLEAR",
            "Context is not favorable enough for positive classification.",
        )

    return (
        "CONTEXT_NEUTRAL_OR_REVIEW_REQUIRED",
        "REVIEW_REQUIRED",
        "Context is not clearly strong, weak, or dangerous.",
    )


def analyze_group_metrics(
    metrics_df: pd.DataFrame,
    group_columns: list[str],
    analysis_scope: str,
    config: ContextPerformanceAnalyzerConfig,
) -> pd.DataFrame:
    if metrics_df.empty:
        return pd.DataFrame()

    rows = []

    for _, row in metrics_df.iterrows():
        analysis_signal, risk_label, reason = classify_group_performance(row, config)

        output_row = {
            "analysis_scope": analysis_scope,
            "analysis_signal": analysis_signal,
            "risk_label": risk_label,
            "analysis_reason": reason,
            "sample_sufficient_for_context": (
                safe_int(row.get("resolved_observations"))
                >= config.min_resolved_per_context
            ),
            "paper_trade_execution_allowed": False,
            "real_capital_allowed": False,
            "live_alerts_allowed": False,
            "exchange_execution_allowed": False,
            "automation_allowed": False,
        }

        for column in group_columns:
            output_row[column] = row.get(column, "")

        for column in REQUIRED_METRIC_COLUMNS:
            output_row[column] = row.get(column, 0)

        rows.append(output_row)

    result_df = pd.DataFrame(rows)

    if result_df.empty:
        return result_df

    sort_columns = [
        "sample_sufficient_for_context",
        "resolved_observations",
        "avg_result_r",
    ]

    return result_df.sort_values(
        by=sort_columns,
        ascending=[False, False, False],
    ).reset_index(drop=True)


def build_context_analyzer_summary(
    dataset_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    context_analysis_df: pd.DataFrame,
    config: ContextPerformanceAnalyzerConfig,
) -> pd.DataFrame:
    validation_passed = bool(validation_df["passed"].all()) if not validation_df.empty else False

    normalized_df = normalize_metrics_dataset(dataset_df)
    resolved_observations = int(normalized_df["is_closed"].sum()) if not normalized_df.empty else 0
    total_observations = len(normalized_df)

    minimum_sample_reached = resolved_observations >= config.min_resolved_observations
    preferred_sample_reached = resolved_observations >= config.preferred_resolved_observations

    if context_analysis_df.empty:
        provisional_positive_contexts = 0
        provisional_negative_contexts = 0
        strong_contexts = 0
        dangerous_contexts = 0
        insufficient_contexts = 0
        contexts_analyzed = 0
    else:
        contexts_analyzed = len(context_analysis_df)
        provisional_positive_contexts = int(
            context_analysis_df["analysis_signal"]
            .eq("PROVISIONAL_POSITIVE_INSUFFICIENT_SAMPLE")
            .sum()
        )
        provisional_negative_contexts = int(
            context_analysis_df["analysis_signal"]
            .eq("PROVISIONAL_NEGATIVE_INSUFFICIENT_SAMPLE")
            .sum()
        )
        strong_contexts = int(
            context_analysis_df["analysis_signal"].eq("CONTEXT_STRONG_CANDIDATE").sum()
        )
        dangerous_contexts = int(
            context_analysis_df["analysis_signal"].eq("CONTEXT_DANGEROUS_CANDIDATE").sum()
        )
        insufficient_contexts = int(
            context_analysis_df["risk_label"].eq("INSUFFICIENT_SAMPLE").sum()
        )

    if not validation_passed:
        analyzer_decision = "CONTEXT_ANALYZER_INPUT_VALIDATION_FAILED"
    elif config.sample_mode:
        analyzer_decision = "CONTEXT_ANALYZER_VALIDATED_SAMPLE_ONLY"
    elif not config.ready_for_phase_4_2_metrics:
        analyzer_decision = "CONTEXT_ANALYZER_BLOCKED_BY_DATASET_QUALITY_GATE"
    elif not minimum_sample_reached:
        analyzer_decision = "CONTEXT_ANALYZER_INSUFFICIENT_FORWARD_EVIDENCE"
    else:
        analyzer_decision = "CONTEXT_ANALYZER_COMPLETED"

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
                "contexts_analyzed": contexts_analyzed,
                "provisional_positive_contexts": provisional_positive_contexts,
                "provisional_negative_contexts": provisional_negative_contexts,
                "strong_contexts": strong_contexts,
                "dangerous_contexts": dangerous_contexts,
                "insufficient_contexts": insufficient_contexts,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "analyzer_decision": analyzer_decision,
            }
        ]
    )


def build_context_analyzer_notes(
    summary_df: pd.DataFrame,
    config: ContextPerformanceAnalyzerConfig,
) -> pd.DataFrame:
    if summary_df.empty:
        return pd.DataFrame(
            [
                {
                    "note_type": "analyzer",
                    "severity": "WARNING",
                    "message": "No analyzer summary generated.",
                }
            ]
        )

    summary = summary_df.iloc[0]
    notes = []

    resolved = safe_int(summary.get("resolved_observations"))

    if resolved < config.min_resolved_observations:
        notes.append(
            {
                "note_type": "sample_size",
                "severity": "CONTROL",
                "message": (
                    f"Context conclusions are not operational: "
                    f"{resolved}/{config.min_resolved_observations} resolved observations."
                ),
            }
        )

    if config.sample_mode:
        notes.append(
            {
                "note_type": "sample_mode",
                "severity": "CONTROL",
                "message": "Analyzer validated in sample mode only.",
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


def run_context_performance_analyzer(
    dataset_df: pd.DataFrame,
    config: ContextPerformanceAnalyzerConfig | None = None,
) -> tuple[
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
        config = ContextPerformanceAnalyzerConfig()

    validation_df = validate_context_analyzer_input(dataset_df)
    normalized_df = normalize_metrics_dataset(dataset_df)

    by_context_metrics_df = build_group_metrics_df(normalized_df, ["context_name"])
    by_cost_profile_metrics_df = build_group_metrics_df(normalized_df, ["cost_profile"])
    by_direction_metrics_df = build_group_metrics_df(normalized_df, ["direction"])
    by_resolution_status_metrics_df = build_group_metrics_df(normalized_df, ["resolution_status"])
    by_context_cost_profile_metrics_df = build_group_metrics_df(
        normalized_df,
        ["context_name", "cost_profile"],
    )

    context_analysis_df = analyze_group_metrics(
        metrics_df=by_context_metrics_df,
        group_columns=["context_name"],
        analysis_scope="CONTEXT",
        config=config,
    )

    cost_profile_analysis_df = analyze_group_metrics(
        metrics_df=by_cost_profile_metrics_df,
        group_columns=["cost_profile"],
        analysis_scope="COST_PROFILE",
        config=config,
    )

    direction_analysis_df = analyze_group_metrics(
        metrics_df=by_direction_metrics_df,
        group_columns=["direction"],
        analysis_scope="DIRECTION",
        config=config,
    )

    resolution_status_analysis_df = analyze_group_metrics(
        metrics_df=by_resolution_status_metrics_df,
        group_columns=["resolution_status"],
        analysis_scope="RESOLUTION_STATUS",
        config=config,
    )

    context_cost_profile_analysis_df = analyze_group_metrics(
        metrics_df=by_context_cost_profile_metrics_df,
        group_columns=["context_name", "cost_profile"],
        analysis_scope="CONTEXT_COST_PROFILE",
        config=config,
    )

    summary_df = build_context_analyzer_summary(
        dataset_df=dataset_df,
        validation_df=validation_df,
        context_analysis_df=context_analysis_df,
        config=config,
    )

    notes_df = build_context_analyzer_notes(
        summary_df=summary_df,
        config=config,
    )

    return (
        summary_df,
        validation_df,
        context_analysis_df,
        cost_profile_analysis_df,
        direction_analysis_df,
        resolution_status_analysis_df,
        context_cost_profile_analysis_df,
        notes_df,
    )