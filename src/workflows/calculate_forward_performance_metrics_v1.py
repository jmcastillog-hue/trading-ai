from pathlib import Path

import pandas as pd

from src.journal.forward_observation_candidate_detector_v1 import (
    ForwardObservationCandidateDetectorConfig,
    build_sample_strategy_signal_candidates,
    detect_forward_observation_candidates,
)
from src.journal.forward_observation_resolution_engine_v1 import (
    ForwardObservationResolutionConfig,
    build_sample_resolution_ohlc_data,
    resolve_forward_observations,
)
from src.metrics.forward_performance_metrics_v1 import (
    ForwardPerformanceMetricsConfig,
    run_forward_performance_metrics,
)
from src.validation.forward_dataset_quality_gate_v1 import (
    ForwardDatasetQualityGateConfig,
    run_forward_dataset_quality_gate,
)


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * 100)


def save_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def print_selected(df: pd.DataFrame, columns: list[str]) -> None:
    if df.empty:
        print("Sin registros.")
        return

    existing_columns = [column for column in columns if column in df.columns]

    if not existing_columns:
        print(df.to_string(index=False))
        return

    print(df[existing_columns].to_string(index=False))


def build_sample_signal_id(row: pd.Series) -> str:
    observed_at = pd.to_datetime(row.get("observed_at"), errors="coerce")

    if pd.isna(observed_at):
        timestamp_part = "UNKNOWN_TIME"
    else:
        timestamp_part = observed_at.strftime("%Y%m%dT%H%M%S")

    symbol = str(row.get("symbol", "UNKNOWN")).upper().replace(" ", "_")
    timeframe = str(row.get("timeframe", "UNKNOWN")).upper().replace(" ", "_")
    cost_profile = str(row.get("cost_profile", "UNKNOWN_COST_PROFILE")).upper().replace(" ", "_")
    context_name = str(row.get("context_name", "UNKNOWN_CONTEXT")).upper().replace(" ", "_")

    return f"FSR-{timestamp_part}-{symbol}-{timeframe}-{cost_profile}-{context_name}"


def ensure_sample_signal_ids(dataset_df: pd.DataFrame) -> pd.DataFrame:
    df = dataset_df.copy()

    if "signal_id" not in df.columns:
        df["signal_id"] = ""

    df["signal_id"] = df.apply(
        lambda row: (
            str(row.get("signal_id")).strip()
            if str(row.get("signal_id")).strip() not in {"", "nan", "None"}
            else build_sample_signal_id(row)
        ),
        axis=1,
    )

    return df


def main() -> None:
    print("FORWARD PERFORMANCE METRICS V1")
    print("=" * 100)
    print("Purpose: calculate forward performance metrics in R")
    print("Restriction: metrics engine validation only. No execution.")
    print()

    reports_dir = Path("reports") / "forward_performance_metrics_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    source_signals_path = reports_dir / "metrics_source_signals_v1.csv"
    source_records_path = reports_dir / "metrics_source_records_v1.csv"
    ohlc_path = reports_dir / "metrics_sample_ohlc_v1.csv"
    dataset_path = reports_dir / "metrics_dataset_v1.csv"

    quality_summary_path = reports_dir / "metrics_quality_gate_summary_v1.csv"
    quality_checks_path = reports_dir / "metrics_quality_gate_checks_v1.csv"

    metrics_summary_path = reports_dir / "metrics_summary_v1.csv"
    metrics_validation_path = reports_dir / "metrics_validation_v1.csv"
    global_metrics_path = reports_dir / "metrics_global_v1.csv"
    by_context_path = reports_dir / "metrics_by_context_v1.csv"
    by_cost_profile_path = reports_dir / "metrics_by_cost_profile_v1.csv"
    by_direction_path = reports_dir / "metrics_by_direction_v1.csv"
    by_resolution_status_path = reports_dir / "metrics_by_resolution_status_v1.csv"
    equity_curve_path = reports_dir / "metrics_equity_curve_v1.csv"
    drawdown_summary_path = reports_dir / "metrics_drawdown_summary_v1.csv"

    workflow_errors = []

    try:
        source_signals_df = build_sample_strategy_signal_candidates()

        (
            source_records_df,
            detector_accepted_df,
            detector_rejected_df,
            detector_validation_df,
        ) = detect_forward_observation_candidates(
            signals_df=source_signals_df,
            config=ForwardObservationCandidateDetectorConfig(),
        )

        ohlc_df = build_sample_resolution_ohlc_data()

        (
            resolved_all_df,
            resolved_closed_df,
            open_df,
            resolution_errors_df,
            ohlc_validation_df,
            resolution_summary_df,
        ) = resolve_forward_observations(
            observations_df=source_records_df,
            ohlc_df=ohlc_df,
            config=ForwardObservationResolutionConfig(
                timestamp_column="timestamp",
                same_bar_policy="CONSERVATIVE_STOP",
                max_bars_after_observation=96,
                paper_trade_execution_allowed=False,
                real_capital_allowed=False,
            ),
        )

        metrics_dataset_df = ensure_sample_signal_ids(resolved_all_df)

        (
            quality_summary_df,
            quality_checks_df,
            quality_df,
            quality_by_context_df,
            quality_by_cost_profile_df,
            quality_by_direction_df,
            quality_by_resolution_status_df,
            duplicate_signal_ids_df,
            error_rows_df,
        ) = run_forward_dataset_quality_gate(
            dataset_df=metrics_dataset_df,
            config=ForwardDatasetQualityGateConfig(
                min_resolved_observations=100,
                preferred_resolved_observations=300,
                max_error_rows=0,
                max_duplicate_signal_ids=0,
                min_unique_contexts=1,
                min_unique_cost_profiles=1,
                min_unique_directions=1,
                max_open_ratio=0.50,
                paper_trade_execution_allowed=False,
                real_capital_allowed=False,
                live_alerts_allowed=False,
                exchange_execution_allowed=False,
                automation_allowed=False,
            ),
        )

        quality_row = quality_summary_df.iloc[0] if not quality_summary_df.empty else {}

        (
            metrics_summary_df,
            metrics_validation_df,
            normalized_metrics_df,
            global_metrics_df,
            by_context_df,
            by_cost_profile_df,
            by_direction_df,
            by_resolution_status_df,
            equity_curve_df,
            drawdown_summary_df,
        ) = run_forward_performance_metrics(
            dataset_df=metrics_dataset_df,
            config=ForwardPerformanceMetricsConfig(
                min_resolved_observations=100,
                preferred_resolved_observations=300,
                sample_mode=True,
                dataset_quality_decision=str(
                    quality_row.get("dataset_quality_decision", "DATASET_NOT_READY")
                ),
                ready_for_phase_4_2_metrics=bool(
                    quality_row.get("ready_for_phase_4_2_metrics", False)
                ),
                paper_trade_execution_allowed=False,
                real_capital_allowed=False,
                live_alerts_allowed=False,
                exchange_execution_allowed=False,
                automation_allowed=False,
            ),
        )

    except Exception as exc:
        workflow_errors.append(
            {
                "severity": "ERROR",
                "check_name": "workflow_error",
                "details": repr(exc),
            }
        )

        source_signals_df = pd.DataFrame()
        source_records_df = pd.DataFrame()
        ohlc_df = pd.DataFrame()
        metrics_dataset_df = pd.DataFrame()
        quality_summary_df = pd.DataFrame()
        quality_checks_df = pd.DataFrame(workflow_errors)
        metrics_summary_df = pd.DataFrame()
        metrics_validation_df = pd.DataFrame(workflow_errors)
        global_metrics_df = pd.DataFrame()
        by_context_df = pd.DataFrame()
        by_cost_profile_df = pd.DataFrame()
        by_direction_df = pd.DataFrame()
        by_resolution_status_df = pd.DataFrame()
        equity_curve_df = pd.DataFrame()
        drawdown_summary_df = pd.DataFrame()

    save_df(source_signals_df, source_signals_path)
    save_df(source_records_df, source_records_path)
    save_df(ohlc_df, ohlc_path)
    save_df(metrics_dataset_df, dataset_path)

    save_df(quality_summary_df, quality_summary_path)
    save_df(quality_checks_df, quality_checks_path)

    save_df(metrics_summary_df, metrics_summary_path)
    save_df(metrics_validation_df, metrics_validation_path)
    save_df(global_metrics_df, global_metrics_path)
    save_df(by_context_df, by_context_path)
    save_df(by_cost_profile_df, by_cost_profile_path)
    save_df(by_direction_df, by_direction_path)
    save_df(by_resolution_status_df, by_resolution_status_path)
    save_df(equity_curve_df, equity_curve_path)
    save_df(drawdown_summary_df, drawdown_summary_path)

    print_section("QUALITY GATE SUMMARY")
    print_selected(
        quality_summary_df,
        [
            "total_observations",
            "resolved_observations",
            "minimum_sample_reached",
            "preferred_sample_reached",
            "ready_for_phase_4_2_metrics",
            "dataset_quality_decision",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "live_alerts_allowed",
            "exchange_execution_allowed",
            "automation_allowed",
        ],
    )

    print_section("METRICS SUMMARY")
    print_selected(
        metrics_summary_df,
        [
            "validation_passed",
            "dataset_quality_decision",
            "ready_for_phase_4_2_metrics",
            "sample_mode",
            "resolved_observations",
            "minimum_sample_reached",
            "preferred_sample_reached",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "live_alerts_allowed",
            "exchange_execution_allowed",
            "automation_allowed",
            "metrics_decision",
        ],
    )

    print_section("GLOBAL METRICS")
    print_selected(
        global_metrics_df,
        [
            "total_observations",
            "resolved_observations",
            "open_observations",
            "error_observations",
            "wins",
            "losses",
            "breakeven",
            "win_rate",
            "loss_rate",
            "avg_result_r",
            "sum_result_r",
            "expectancy_r",
            "profit_factor",
            "payoff_ratio",
            "avg_win_r",
            "avg_loss_r",
            "best_result_r",
            "worst_result_r",
            "avg_mfe_r",
            "avg_mae_r",
            "avg_bars_to_resolution",
            "max_consecutive_wins",
            "max_consecutive_losses",
            "max_drawdown_r",
        ],
    )

    print_section("BY CONTEXT")
    print_selected(
        by_context_df,
        [
            "context_name",
            "resolved_observations",
            "wins",
            "losses",
            "win_rate",
            "avg_result_r",
            "sum_result_r",
            "profit_factor",
            "max_drawdown_r",
        ],
    )

    print_section("BY COST PROFILE")
    print_selected(
        by_cost_profile_df,
        [
            "cost_profile",
            "resolved_observations",
            "wins",
            "losses",
            "win_rate",
            "avg_result_r",
            "sum_result_r",
            "profit_factor",
            "max_drawdown_r",
        ],
    )

    print_section("BY DIRECTION")
    print_selected(
        by_direction_df,
        [
            "direction",
            "resolved_observations",
            "wins",
            "losses",
            "win_rate",
            "avg_result_r",
            "sum_result_r",
            "profit_factor",
            "max_drawdown_r",
        ],
    )

    print_section("BY RESOLUTION STATUS")
    print_selected(
        by_resolution_status_df,
        [
            "resolution_status",
            "resolved_observations",
            "wins",
            "losses",
            "win_rate",
            "avg_result_r",
            "sum_result_r",
            "profit_factor",
            "max_drawdown_r",
        ],
    )

    print_section("EQUITY CURVE")
    print_selected(
        equity_curve_df,
        [
            "trade_index",
            "signal_id",
            "resolution_status",
            "result_r",
            "equity_r",
            "equity_peak_r",
            "drawdown_r",
        ],
    )

    print_section("DRAWDOWN SUMMARY")
    print_selected(
        drawdown_summary_df,
        [
            "trades",
            "ending_equity_r",
            "max_equity_r",
            "max_drawdown_r",
            "max_drawdown_trade_index",
        ],
    )

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {source_signals_path}")
    print(f"- {source_records_path}")
    print(f"- {ohlc_path}")
    print(f"- {dataset_path}")
    print(f"- {quality_summary_path}")
    print(f"- {quality_checks_path}")
    print(f"- {metrics_summary_path}")
    print(f"- {metrics_validation_path}")
    print(f"- {global_metrics_path}")
    print(f"- {by_context_path}")
    print(f"- {by_cost_profile_path}")
    print(f"- {by_direction_path}")
    print(f"- {by_resolution_status_path}")
    print(f"- {equity_curve_path}")
    print(f"- {drawdown_summary_path}")

    print()
    print("Restriccion: este motor calcula metricas. No habilita ejecucion operativa.")


if __name__ == "__main__":
    main()