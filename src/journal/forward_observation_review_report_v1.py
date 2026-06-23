from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class ForwardObservationReviewConfig:
    open_statuses: tuple[str, ...] = (
        "OPEN_UNRESOLVED",
        "OPEN_NO_FUTURE_DATA",
    )
    min_resolved_observations: int = 100
    preferred_resolved_observations: int = 300
    paper_trade_execution_allowed: bool = False
    real_capital_allowed: bool = False


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


def ensure_review_columns(resolved_df: pd.DataFrame) -> pd.DataFrame:
    df = resolved_df.copy()

    text_defaults = {
        "signal_id": "",
        "observed_at": "",
        "resolved_at": "",
        "symbol": "",
        "timeframe": "",
        "cost_profile": "UNKNOWN_COST_PROFILE",
        "context_name": "UNKNOWN_CONTEXT",
        "direction": "UNKNOWN_DIRECTION",
        "resolution_status": "",
        "resolution_reason": "",
    }

    numeric_defaults = {
        "entry_theoretical": 0.0,
        "stop_theoretical": 0.0,
        "target_theoretical": 0.0,
        "result_r": 0.0,
        "mfe_r": 0.0,
        "mae_r": 0.0,
        "bars_to_resolution": 0.0,
        "resolution_price": 0.0,
    }

    for column, default in text_defaults.items():
        if column not in df.columns:
            df[column] = default

        df[column] = df[column].map(lambda value: safe_str(value, default))

    for column, default in numeric_defaults.items():
        if column not in df.columns:
            df[column] = default

        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(default)

    df["resolution_status"] = df["resolution_status"].str.upper()
    df["direction"] = df["direction"].str.upper()
    df["cost_profile"] = df["cost_profile"].str.upper()
    df["context_name"] = df["context_name"].str.upper()

    return df


def add_review_flags(
    resolved_df: pd.DataFrame,
    config: ForwardObservationReviewConfig,
) -> pd.DataFrame:
    df = ensure_review_columns(resolved_df)

    open_statuses = set(config.open_statuses)

    df["is_open"] = df["resolution_status"].isin(open_statuses)
    df["is_error"] = df["resolution_status"].str.startswith("RESOLUTION_ERROR")
    df["is_closed"] = (
        ~df["is_open"]
        & ~df["is_error"]
        & (df["resolution_status"] != "")
    )

    df["is_win"] = df["is_closed"] & (df["result_r"] > 0)
    df["is_loss"] = df["is_closed"] & (df["result_r"] < 0)
    df["is_breakeven"] = df["is_closed"] & (df["result_r"] == 0)

    return df


def calculate_profit_factor(closed_df: pd.DataFrame) -> float:
    if closed_df.empty:
        return 0.0

    gross_profit = float(closed_df.loc[closed_df["result_r"] > 0, "result_r"].sum())
    gross_loss = abs(float(closed_df.loc[closed_df["result_r"] < 0, "result_r"].sum()))

    if gross_loss == 0 and gross_profit > 0:
        return 999.0

    if gross_loss == 0:
        return 0.0

    return round(gross_profit / gross_loss, 6)


def calculate_metric_dict(flagged_df: pd.DataFrame) -> dict[str, Any]:
    total_observations = len(flagged_df)
    closed_df = flagged_df[flagged_df["is_closed"]].copy()
    resolved_observations = len(closed_df)
    open_observations = int(flagged_df["is_open"].sum()) if not flagged_df.empty else 0
    error_observations = int(flagged_df["is_error"].sum()) if not flagged_df.empty else 0

    wins = int(closed_df["is_win"].sum()) if not closed_df.empty else 0
    losses = int(closed_df["is_loss"].sum()) if not closed_df.empty else 0
    breakeven = int(closed_df["is_breakeven"].sum()) if not closed_df.empty else 0

    if resolved_observations > 0:
        win_rate = round(float((closed_df["result_r"] > 0).mean()), 6)
        avg_result_r = round(float(closed_df["result_r"].mean()), 6)
        sum_result_r = round(float(closed_df["result_r"].sum()), 6)
        avg_mfe_r = round(float(closed_df["mfe_r"].mean()), 6)
        avg_mae_r = round(float(closed_df["mae_r"].mean()), 6)
        avg_bars_to_resolution = round(float(closed_df["bars_to_resolution"].mean()), 6)
        best_result_r = round(float(closed_df["result_r"].max()), 6)
        worst_result_r = round(float(closed_df["result_r"].min()), 6)
        profit_factor = calculate_profit_factor(closed_df)
    else:
        win_rate = 0.0
        avg_result_r = 0.0
        sum_result_r = 0.0
        avg_mfe_r = 0.0
        avg_mae_r = 0.0
        avg_bars_to_resolution = 0.0
        best_result_r = 0.0
        worst_result_r = 0.0
        profit_factor = 0.0

    return {
        "total_observations": total_observations,
        "resolved_observations": resolved_observations,
        "open_observations": open_observations,
        "error_observations": error_observations,
        "wins": wins,
        "losses": losses,
        "breakeven": breakeven,
        "win_rate": win_rate,
        "avg_result_r": avg_result_r,
        "sum_result_r": sum_result_r,
        "profit_factor": profit_factor,
        "avg_mfe_r": avg_mfe_r,
        "avg_mae_r": avg_mae_r,
        "avg_bars_to_resolution": avg_bars_to_resolution,
        "best_result_r": best_result_r,
        "worst_result_r": worst_result_r,
    }


def aggregate_metrics_by_group(
    flagged_df: pd.DataFrame,
    group_columns: list[str],
) -> pd.DataFrame:
    if flagged_df.empty:
        return pd.DataFrame()

    rows = []

    for group_key, group_df in flagged_df.groupby(group_columns, dropna=False):
        if len(group_columns) == 1:
            group_values = group_key if isinstance(group_key, tuple) else (group_key,)
        else:
            group_values = group_key if isinstance(group_key, tuple) else (group_key,)

        row = {}

        for column, value in zip(group_columns, group_values):
            row[column] = value

        row.update(calculate_metric_dict(group_df))
        rows.append(row)

    result = pd.DataFrame(rows)

    if result.empty:
        return result

    return result.sort_values(
        by=["resolved_observations", "avg_result_r"],
        ascending=[False, False],
    ).reset_index(drop=True)


def build_review_summary(
    flagged_df: pd.DataFrame,
    errors_df: pd.DataFrame,
    config: ForwardObservationReviewConfig,
) -> pd.DataFrame:
    metrics = calculate_metric_dict(flagged_df)

    external_error_rows = len(errors_df) if errors_df is not None and not errors_df.empty else 0
    total_error_rows = metrics["error_observations"] + external_error_rows
    resolved_observations = metrics["resolved_observations"]

    minimum_sample_reached = resolved_observations >= config.min_resolved_observations
    preferred_sample_reached = resolved_observations >= config.preferred_resolved_observations

    if metrics["total_observations"] == 0:
        review_decision = "REVIEW_NO_OBSERVATIONS"
    elif total_error_rows > 0:
        review_decision = "REVIEW_COMPLETED_WITH_ERRORS"
    elif resolved_observations < config.min_resolved_observations:
        review_decision = "REVIEW_COMPLETED_INSUFFICIENT_FORWARD_SAMPLE"
    elif resolved_observations < config.preferred_resolved_observations:
        review_decision = "REVIEW_COMPLETED_MINIMUM_SAMPLE_REACHED"
    else:
        review_decision = "REVIEW_COMPLETED_PREFERRED_SAMPLE_REACHED"

    row = {
        **metrics,
        "external_error_rows": external_error_rows,
        "total_error_rows": total_error_rows,
        "min_resolved_observations": config.min_resolved_observations,
        "preferred_resolved_observations": config.preferred_resolved_observations,
        "minimum_sample_reached": minimum_sample_reached,
        "preferred_sample_reached": preferred_sample_reached,
        "paper_trade_execution_allowed": False,
        "real_capital_allowed": False,
        "review_decision": review_decision,
    }

    return pd.DataFrame([row])


def build_review_notes(
    summary_df: pd.DataFrame,
    config: ForwardObservationReviewConfig,
) -> pd.DataFrame:
    if summary_df.empty:
        return pd.DataFrame(
            [
                {
                    "note_type": "review",
                    "severity": "WARNING",
                    "message": "No hay observaciones para revisar.",
                }
            ]
        )

    summary = summary_df.iloc[0]
    notes = []

    resolved = int(summary.get("resolved_observations", 0))
    total_errors = int(summary.get("total_error_rows", 0))

    if resolved < config.min_resolved_observations:
        notes.append(
            {
                "note_type": "sample_size",
                "severity": "INFO",
                "message": (
                    f"Muestra insuficiente para decisión operativa: "
                    f"{resolved}/{config.min_resolved_observations} observaciones resueltas."
                ),
            }
        )

    if total_errors > 0:
        notes.append(
            {
                "note_type": "errors",
                "severity": "WARNING",
                "message": f"Existen {total_errors} filas de error que requieren revisión.",
            }
        )

    notes.append(
        {
            "note_type": "execution_restriction",
            "severity": "CONTROL",
            "message": (
                "Este reporte no habilita capital real, paper trading ejecutado, "
                "alertas live ni ejecución Binance/Quantfury."
            ),
        }
    )

    notes.append(
        {
            "note_type": "next_step",
            "severity": "INFO",
            "message": (
                "Usar este reporte como insumo para cierre de Fase 3 y luego "
                "para el quality gate de Fase 4."
            ),
        }
    )

    return pd.DataFrame(notes)


def build_review_errors_df(
    flagged_df: pd.DataFrame,
    errors_df: pd.DataFrame,
) -> pd.DataFrame:
    status_errors_df = flagged_df[flagged_df["is_error"]].copy()

    if not status_errors_df.empty:
        status_errors_df["error_source"] = "resolution_status"

    external_errors_df = pd.DataFrame()

    if errors_df is not None and not errors_df.empty:
        external_errors_df = errors_df.copy()
        external_errors_df["error_source"] = "external_errors_df"

    if status_errors_df.empty and external_errors_df.empty:
        return pd.DataFrame()

    return pd.concat(
        [status_errors_df, external_errors_df],
        ignore_index=True,
        sort=False,
    )


def format_df_for_markdown(title: str, df: pd.DataFrame) -> list[str]:
    lines = [f"## {title}", ""]

    if df.empty:
        lines.append("Sin registros.")
        lines.append("")
        return lines

    lines.append("```text")
    lines.append(df.to_string(index=False))
    lines.append("```")
    lines.append("")

    return lines


def build_forward_observation_review_markdown(
    summary_df: pd.DataFrame,
    by_context_df: pd.DataFrame,
    by_cost_profile_df: pd.DataFrame,
    by_direction_df: pd.DataFrame,
    by_resolution_status_df: pd.DataFrame,
    winners_df: pd.DataFrame,
    losers_df: pd.DataFrame,
    open_df: pd.DataFrame,
    review_errors_df: pd.DataFrame,
    review_notes_df: pd.DataFrame,
) -> str:
    lines = [
        "# Forward Observation Review Report V1",
        "",
        "Reporte de revisión observacional. No habilita ejecución.",
        "",
        "Restricciones:",
        "",
        "- No capital real.",
        "- No paper trading ejecutado.",
        "- No alertas live.",
        "- No Binance/Quantfury execution.",
        "- No automatización operativa.",
        "",
    ]

    lines.extend(format_df_for_markdown("Review Summary", summary_df))
    lines.extend(format_df_for_markdown("Metrics by Context", by_context_df))
    lines.extend(format_df_for_markdown("Metrics by Cost Profile", by_cost_profile_df))
    lines.extend(format_df_for_markdown("Metrics by Direction", by_direction_df))
    lines.extend(format_df_for_markdown("Metrics by Resolution Status", by_resolution_status_df))
    lines.extend(format_df_for_markdown("Winners", winners_df))
    lines.extend(format_df_for_markdown("Losers", losers_df))
    lines.extend(format_df_for_markdown("Open Observations", open_df))
    lines.extend(format_df_for_markdown("Review Errors", review_errors_df))
    lines.extend(format_df_for_markdown("Review Notes", review_notes_df))

    return "\n".join(lines)


def build_forward_observation_review_report(
    resolved_observations_df: pd.DataFrame,
    errors_df: pd.DataFrame | None = None,
    config: ForwardObservationReviewConfig | None = None,
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
    pd.DataFrame,
    str,
]:
    if config is None:
        config = ForwardObservationReviewConfig()

    if errors_df is None:
        errors_df = pd.DataFrame()

    flagged_df = add_review_flags(
        resolved_df=resolved_observations_df,
        config=config,
    )

    summary_df = build_review_summary(
        flagged_df=flagged_df,
        errors_df=errors_df,
        config=config,
    )

    by_context_df = aggregate_metrics_by_group(
        flagged_df=flagged_df,
        group_columns=["context_name"],
    )

    by_cost_profile_df = aggregate_metrics_by_group(
        flagged_df=flagged_df,
        group_columns=["cost_profile"],
    )

    by_direction_df = aggregate_metrics_by_group(
        flagged_df=flagged_df,
        group_columns=["direction"],
    )

    by_resolution_status_df = aggregate_metrics_by_group(
        flagged_df=flagged_df,
        group_columns=["resolution_status"],
    )

    winners_df = flagged_df[flagged_df["is_win"]].copy().sort_values(
        by="result_r",
        ascending=False,
    )

    losers_df = flagged_df[flagged_df["is_loss"]].copy().sort_values(
        by="result_r",
        ascending=True,
    )

    open_df = flagged_df[flagged_df["is_open"]].copy()

    review_errors_df = build_review_errors_df(
        flagged_df=flagged_df,
        errors_df=errors_df,
    )

    review_notes_df = build_review_notes(
        summary_df=summary_df,
        config=config,
    )

    markdown_report = build_forward_observation_review_markdown(
        summary_df=summary_df,
        by_context_df=by_context_df,
        by_cost_profile_df=by_cost_profile_df,
        by_direction_df=by_direction_df,
        by_resolution_status_df=by_resolution_status_df,
        winners_df=winners_df,
        losers_df=losers_df,
        open_df=open_df,
        review_errors_df=review_errors_df,
        review_notes_df=review_notes_df,
    )

    return (
        summary_df,
        by_context_df,
        by_cost_profile_df,
        by_direction_df,
        by_resolution_status_df,
        winners_df,
        losers_df,
        open_df,
        review_errors_df,
        review_notes_df,
        markdown_report,
    )