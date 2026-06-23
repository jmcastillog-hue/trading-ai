from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class ForwardEvidenceDashboardConfig:
    min_resolved_observations: int = 100
    preferred_resolved_observations: int = 300
    sample_mode: bool = True
    paper_trade_execution_allowed: bool = False
    real_capital_allowed: bool = False
    live_alerts_allowed: bool = False
    exchange_execution_allowed: bool = False
    automation_allowed: bool = False


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


def safe_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    text = str(value).strip().lower()

    if text in {"true", "1", "yes", "y"}:
        return True

    if text in {"false", "0", "no", "n", ""}:
        return False

    return default


def first_row(df: pd.DataFrame) -> dict[str, Any]:
    if df is None or df.empty:
        return {}

    return df.iloc[0].to_dict()


def validate_dashboard_inputs(
    quality_summary_df: pd.DataFrame,
    metrics_summary_df: pd.DataFrame,
    global_metrics_df: pd.DataFrame,
    context_summary_df: pd.DataFrame,
    context_analysis_df: pd.DataFrame,
    risk_summary_df: pd.DataFrame,
    risk_by_context_df: pd.DataFrame,
) -> pd.DataFrame:
    checks = [
        ("quality_summary_has_rows", quality_summary_df is not None and not quality_summary_df.empty),
        ("metrics_summary_has_rows", metrics_summary_df is not None and not metrics_summary_df.empty),
        ("global_metrics_has_rows", global_metrics_df is not None and not global_metrics_df.empty),
        ("context_summary_has_rows", context_summary_df is not None and not context_summary_df.empty),
        ("context_analysis_has_rows", context_analysis_df is not None and not context_analysis_df.empty),
        ("risk_summary_has_rows", risk_summary_df is not None and not risk_summary_df.empty),
        ("risk_by_context_has_rows", risk_by_context_df is not None and not risk_by_context_df.empty),
    ]

    rows = []

    for check_name, passed in checks:
        rows.append(
            {
                "check_name": check_name,
                "passed": bool(passed),
                "severity": "ERROR",
                "details": "OK" if passed else "MISSING_OR_EMPTY",
            }
        )

    return pd.DataFrame(rows)


def build_dashboard_summary_df(
    quality_summary_df: pd.DataFrame,
    metrics_summary_df: pd.DataFrame,
    global_metrics_df: pd.DataFrame,
    context_summary_df: pd.DataFrame,
    risk_summary_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    config: ForwardEvidenceDashboardConfig,
) -> pd.DataFrame:
    quality = first_row(quality_summary_df)
    metrics = first_row(metrics_summary_df)
    global_metrics = first_row(global_metrics_df)
    context = first_row(context_summary_df)
    risk = first_row(risk_summary_df)

    validation_passed = bool(validation_df["passed"].all()) if not validation_df.empty else False

    resolved_observations = safe_int(
        quality.get(
            "resolved_observations",
            metrics.get("resolved_observations", risk.get("resolved_observations", 0)),
        )
    )

    minimum_sample_reached = resolved_observations >= config.min_resolved_observations
    preferred_sample_reached = resolved_observations >= config.preferred_resolved_observations

    dataset_quality_decision = safe_str(
        quality.get("dataset_quality_decision", "DATASET_NOT_READY"),
        "DATASET_NOT_READY",
    )

    ready_for_phase_4_2_metrics = safe_bool(
        quality.get("ready_for_phase_4_2_metrics", False),
        False,
    )

    metrics_decision = safe_str(
        metrics.get("metrics_decision", "METRICS_NOT_AVAILABLE"),
        "METRICS_NOT_AVAILABLE",
    )

    context_decision = safe_str(
        context.get("analyzer_decision", "CONTEXT_ANALYZER_NOT_AVAILABLE"),
        "CONTEXT_ANALYZER_NOT_AVAILABLE",
    )

    risk_decision = safe_str(
        risk.get("analyzer_decision", "RISK_REGIME_ANALYZER_NOT_AVAILABLE"),
        "RISK_REGIME_ANALYZER_NOT_AVAILABLE",
    )

    no_execution_allowed = not any(
        [
            config.paper_trade_execution_allowed,
            config.real_capital_allowed,
            config.live_alerts_allowed,
            config.exchange_execution_allowed,
            config.automation_allowed,
        ]
    )

    if not validation_passed:
        evidence_report_decision = "FORWARD_EVIDENCE_REPORT_INPUT_VALIDATION_FAILED"
    elif config.sample_mode:
        evidence_report_decision = "FORWARD_EVIDENCE_REPORT_SAMPLE_ONLY"
    elif dataset_quality_decision != "DATASET_READY" or not ready_for_phase_4_2_metrics:
        evidence_report_decision = "FORWARD_EVIDENCE_REPORT_BLOCKED_BY_DATASET_QUALITY"
    elif not minimum_sample_reached:
        evidence_report_decision = "FORWARD_EVIDENCE_REPORT_INSUFFICIENT_FORWARD_EVIDENCE"
    else:
        evidence_report_decision = "FORWARD_EVIDENCE_REPORT_COMPLETED"

    readiness_state = (
        "DATASET_NOT_READY"
        if not minimum_sample_reached or dataset_quality_decision != "DATASET_READY"
        else "DATASET_READY"
    )

    execution_state = "NO_EXECUTION_ALLOWED" if no_execution_allowed else "EXECUTION_FLAGS_REVIEW_REQUIRED"

    return pd.DataFrame(
        [
            {
                "validation_passed": validation_passed,
                "sample_mode": config.sample_mode,
                "dataset_quality_decision": dataset_quality_decision,
                "ready_for_phase_4_2_metrics": ready_for_phase_4_2_metrics,
                "metrics_decision": metrics_decision,
                "context_decision": context_decision,
                "risk_regime_decision": risk_decision,
                "readiness_state": readiness_state,
                "execution_state": execution_state,
                "total_observations": safe_int(quality.get("total_observations", 0)),
                "resolved_observations": resolved_observations,
                "min_resolved_observations": config.min_resolved_observations,
                "preferred_resolved_observations": config.preferred_resolved_observations,
                "minimum_sample_reached": minimum_sample_reached,
                "preferred_sample_reached": preferred_sample_reached,
                "sample_gap_to_minimum": max(
                    config.min_resolved_observations - resolved_observations,
                    0,
                ),
                "sample_gap_to_preferred": max(
                    config.preferred_resolved_observations - resolved_observations,
                    0,
                ),
                "sum_result_r": safe_float(global_metrics.get("sum_result_r", 0.0)),
                "avg_result_r": safe_float(global_metrics.get("avg_result_r", 0.0)),
                "win_rate": safe_float(global_metrics.get("win_rate", 0.0)),
                "profit_factor": safe_float(global_metrics.get("profit_factor", 0.0)),
                "max_drawdown_r": safe_float(global_metrics.get("max_drawdown_r", 0.0)),
                "global_worst_result_r": safe_float(risk.get("global_worst_result_r", 0.0)),
                "global_worst_mae_r": safe_float(risk.get("global_worst_mae_r", 0.0)),
                "global_max_consecutive_losses": safe_int(
                    risk.get("global_max_consecutive_losses", 0)
                ),
                "contexts_analyzed": safe_int(context.get("contexts_analyzed", 0)),
                "provisional_positive_contexts": safe_int(
                    context.get("provisional_positive_contexts", 0)
                ),
                "provisional_negative_contexts": safe_int(
                    context.get("provisional_negative_contexts", 0)
                ),
                "insufficient_contexts": safe_int(context.get("insufficient_contexts", 0)),
                "buckets_analyzed": safe_int(risk.get("buckets_analyzed", 0)),
                "insufficient_buckets": safe_int(risk.get("insufficient_buckets", 0)),
                "high_risk_events": safe_int(risk.get("high_risk_events", 0)),
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "evidence_report_decision": evidence_report_decision,
            }
        ]
    )


def build_evidence_kpi_df(summary_df: pd.DataFrame) -> pd.DataFrame:
    if summary_df.empty:
        return pd.DataFrame()

    row = first_row(summary_df)

    kpis = [
        ("Readiness", "Dataset quality", row.get("dataset_quality_decision", "")),
        ("Readiness", "Evidence report decision", row.get("evidence_report_decision", "")),
        ("Readiness", "Execution state", row.get("execution_state", "")),
        ("Sample", "Resolved observations", row.get("resolved_observations", 0)),
        ("Sample", "Minimum required", row.get("min_resolved_observations", 100)),
        ("Sample", "Gap to minimum", row.get("sample_gap_to_minimum", 0)),
        ("Sample", "Preferred required", row.get("preferred_resolved_observations", 300)),
        ("Sample", "Gap to preferred", row.get("sample_gap_to_preferred", 0)),
        ("Performance", "Sum result R", row.get("sum_result_r", 0.0)),
        ("Performance", "Average result R", row.get("avg_result_r", 0.0)),
        ("Performance", "Win rate", row.get("win_rate", 0.0)),
        ("Performance", "Profit factor", row.get("profit_factor", 0.0)),
        ("Risk", "Max drawdown R", row.get("max_drawdown_r", 0.0)),
        ("Risk", "Worst result R", row.get("global_worst_result_r", 0.0)),
        ("Risk", "Worst MAE R", row.get("global_worst_mae_r", 0.0)),
        ("Risk", "Max consecutive losses", row.get("global_max_consecutive_losses", 0)),
        ("Context", "Contexts analyzed", row.get("contexts_analyzed", 0)),
        ("Context", "Provisional positive contexts", row.get("provisional_positive_contexts", 0)),
        ("Context", "Provisional negative contexts", row.get("provisional_negative_contexts", 0)),
        ("Context", "Insufficient contexts", row.get("insufficient_contexts", 0)),
    ]

    return pd.DataFrame(
        [
            {
                "section": section,
                "metric": metric,
                "value": value,
            }
            for section, metric, value in kpis
        ]
    )


def build_readiness_requirements_df(summary_df: pd.DataFrame) -> pd.DataFrame:
    if summary_df.empty:
        return pd.DataFrame()

    row = first_row(summary_df)
    resolved_observations = safe_int(row.get("resolved_observations", 0))
    min_resolved_observations = safe_int(row.get("min_resolved_observations", 100))
    preferred_resolved_observations = safe_int(row.get("preferred_resolved_observations", 300))

    requirements = [
        {
            "requirement": "Minimum resolved forward observations",
            "current_value": resolved_observations,
            "required_value": min_resolved_observations,
            "passed": resolved_observations >= min_resolved_observations,
            "gap": max(min_resolved_observations - resolved_observations, 0),
            "severity": "BLOCKER",
        },
        {
            "requirement": "Preferred resolved forward observations",
            "current_value": resolved_observations,
            "required_value": preferred_resolved_observations,
            "passed": resolved_observations >= preferred_resolved_observations,
            "gap": max(preferred_resolved_observations - resolved_observations, 0),
            "severity": "INFO",
        },
        {
            "requirement": "Dataset quality ready",
            "current_value": row.get("dataset_quality_decision", "DATASET_NOT_READY"),
            "required_value": "DATASET_READY",
            "passed": row.get("dataset_quality_decision") == "DATASET_READY",
            "gap": "",
            "severity": "BLOCKER",
        },
        {
            "requirement": "Metrics readiness",
            "current_value": row.get("ready_for_phase_4_2_metrics", False),
            "required_value": True,
            "passed": safe_bool(row.get("ready_for_phase_4_2_metrics", False), False),
            "gap": "",
            "severity": "BLOCKER",
        },
        {
            "requirement": "Execution restriction",
            "current_value": row.get("execution_state", "NO_EXECUTION_ALLOWED"),
            "required_value": "NO_EXECUTION_ALLOWED",
            "passed": row.get("execution_state") == "NO_EXECUTION_ALLOWED",
            "gap": "",
            "severity": "CONTROL",
        },
    ]

    return pd.DataFrame(requirements)


def select_top_rows(
    df: pd.DataFrame,
    columns: list[str],
    max_rows: int = 10,
) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=columns)

    existing_columns = [column for column in columns if column in df.columns]

    if not existing_columns:
        return pd.DataFrame()

    return df[existing_columns].head(max_rows).copy()


def build_markdown_table(df: pd.DataFrame) -> str:
    if df is None or df.empty:
        return "_Sin registros._"

    table_df = df.copy()

    for column in table_df.columns:
        table_df[column] = table_df[column].map(lambda value: safe_str(value, ""))

    headers = list(table_df.columns)

    header_line = "| " + " | ".join(headers) + " |"
    separator_line = "| " + " | ".join(["---"] * len(headers)) + " |"

    body_lines = []

    for _, row in table_df.iterrows():
        values = [
            safe_str(row.get(column, "")).replace("|", "/")
            for column in headers
        ]

        body_lines.append("| " + " | ".join(values) + " |")

    return "\n".join([header_line, separator_line] + body_lines)


def build_forward_evidence_markdown_report(
    summary_df: pd.DataFrame,
    kpi_df: pd.DataFrame,
    readiness_requirements_df: pd.DataFrame,
    context_analysis_df: pd.DataFrame,
    risk_by_context_df: pd.DataFrame,
    risk_by_market_cost_regime_df: pd.DataFrame,
    risk_event_log_df: pd.DataFrame,
) -> str:
    summary = first_row(summary_df)

    context_table = select_top_rows(
        context_analysis_df,
        [
            "context_name",
            "resolved_observations",
            "wins",
            "losses",
            "avg_result_r",
            "profit_factor",
            "analysis_signal",
            "risk_label",
        ],
    )

    risk_context_table = select_top_rows(
        risk_by_context_df,
        [
            "context_name",
            "market_regime",
            "resolved_observations",
            "avg_result_r",
            "profit_factor",
            "max_drawdown_r",
            "worst_result_r",
            "worst_mae_r",
            "risk_signal",
            "risk_label",
        ],
    )

    market_cost_table = select_top_rows(
        risk_by_market_cost_regime_df,
        [
            "market_regime",
            "cost_regime",
            "resolved_observations",
            "avg_result_r",
            "profit_factor",
            "worst_result_r",
            "worst_mae_r",
            "risk_signal",
            "risk_label",
        ],
    )

    event_table = select_top_rows(
        risk_event_log_df,
        [
            "signal_id",
            "context_name",
            "market_regime",
            "cost_profile",
            "direction",
            "resolution_status",
            "result_r",
            "mae_r",
            "risk_event_type",
            "risk_event_severity",
        ],
    )

    return f"""# Forward Evidence Dashboard V1

## Executive decision

| Field | Value |
|---|---|
| Evidence report decision | {summary.get("evidence_report_decision", "")} |
| Dataset quality decision | {summary.get("dataset_quality_decision", "")} |
| Readiness state | {summary.get("readiness_state", "")} |
| Execution state | {summary.get("execution_state", "")} |
| Sample mode | {summary.get("sample_mode", "")} |
| Resolved observations | {summary.get("resolved_observations", 0)} / {summary.get("min_resolved_observations", 100)} |
| Preferred observations | {summary.get("resolved_observations", 0)} / {summary.get("preferred_resolved_observations", 300)} |

## Key metrics

{build_markdown_table(kpi_df)}

## Readiness requirements

{build_markdown_table(readiness_requirements_df)}

## Context evidence

{build_markdown_table(context_table)}

## Risk by context

{build_markdown_table(risk_context_table)}

## Risk by market + cost regime

{build_markdown_table(market_cost_table)}

## Risk event log

{build_markdown_table(event_table)}

## Operational restriction

This report does not enable real capital, executed paper trading, live alerts, exchange execution, or automation.

## Technical conclusion

The current evidence is structurally valid but statistically insufficient. The system remains in forward observation and evidence-building mode until minimum forward evidence requirements are met.
"""


def build_evidence_notes_df(summary_df: pd.DataFrame) -> pd.DataFrame:
    if summary_df.empty:
        return pd.DataFrame()

    row = first_row(summary_df)
    notes = []

    notes.append(
        {
            "note_type": "executive_decision",
            "severity": "CONTROL",
            "message": safe_str(row.get("evidence_report_decision")),
        }
    )

    notes.append(
        {
            "note_type": "dataset_readiness",
            "severity": "BLOCKER",
            "message": (
                f"Dataset remains {row.get('dataset_quality_decision')} with "
                f"{row.get('resolved_observations')}/"
                f"{row.get('min_resolved_observations')} resolved observations."
            ),
        }
    )

    notes.append(
        {
            "note_type": "sample_interpretation",
            "severity": "CONTROL",
            "message": "Current performance, context and risk readings are sample-only.",
        }
    )

    notes.append(
        {
            "note_type": "execution_restriction",
            "severity": "CONTROL",
            "message": (
                "No real capital, executed paper trading, live alerts, exchange execution, "
                "or automation is allowed by this report."
            ),
        }
    )

    return pd.DataFrame(notes)


def run_forward_evidence_dashboard(
    quality_summary_df: pd.DataFrame,
    metrics_summary_df: pd.DataFrame,
    global_metrics_df: pd.DataFrame,
    context_summary_df: pd.DataFrame,
    context_analysis_df: pd.DataFrame,
    risk_summary_df: pd.DataFrame,
    risk_by_context_df: pd.DataFrame,
    risk_by_market_cost_regime_df: pd.DataFrame,
    risk_event_log_df: pd.DataFrame,
    config: ForwardEvidenceDashboardConfig | None = None,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    str,
]:
    if config is None:
        config = ForwardEvidenceDashboardConfig()

    validation_df = validate_dashboard_inputs(
        quality_summary_df=quality_summary_df,
        metrics_summary_df=metrics_summary_df,
        global_metrics_df=global_metrics_df,
        context_summary_df=context_summary_df,
        context_analysis_df=context_analysis_df,
        risk_summary_df=risk_summary_df,
        risk_by_context_df=risk_by_context_df,
    )

    summary_df = build_dashboard_summary_df(
        quality_summary_df=quality_summary_df,
        metrics_summary_df=metrics_summary_df,
        global_metrics_df=global_metrics_df,
        context_summary_df=context_summary_df,
        risk_summary_df=risk_summary_df,
        validation_df=validation_df,
        config=config,
    )

    kpi_df = build_evidence_kpi_df(summary_df)
    readiness_requirements_df = build_readiness_requirements_df(summary_df)
    notes_df = build_evidence_notes_df(summary_df)

    markdown_report = build_forward_evidence_markdown_report(
        summary_df=summary_df,
        kpi_df=kpi_df,
        readiness_requirements_df=readiness_requirements_df,
        context_analysis_df=context_analysis_df,
        risk_by_context_df=risk_by_context_df,
        risk_by_market_cost_regime_df=risk_by_market_cost_regime_df,
        risk_event_log_df=risk_event_log_df,
    )

    return (
        summary_df,
        validation_df,
        kpi_df,
        readiness_requirements_df,
        notes_df,
        markdown_report,
    )