from pathlib import Path

import pandas as pd

from src.analysis.context_performance_analyzer_v1 import (
    ContextPerformanceAnalyzerConfig,
    run_context_performance_analyzer,
)
from src.analysis.forward_risk_regime_breakdown_analyzer_v1 import (
    ForwardRiskRegimeBreakdownConfig,
    run_forward_risk_regime_breakdown_analyzer,
)
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
from src.reports.forward_evidence_dashboard_v1 import (
    ForwardEvidenceDashboardConfig,
    run_forward_evidence_dashboard,
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
    print("FORWARD EVIDENCE DASHBOARD / SUMMARY REPORT V1")
    print("=" * 100)
    print("Purpose: consolidate dataset, metrics, context and risk/regime evidence")
    print("Restriction: summary report only. No execution.")
    print()

    reports_dir = Path("reports") / "forward_evidence_dashboard_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    source_signals_path = reports_dir / "evidence_source_signals_v1.csv"
    source_records_path = reports_dir / "evidence_source_records_v1.csv"
    ohlc_path = reports_dir / "evidence_sample_ohlc_v1.csv"
    dataset_path = reports_dir / "evidence_dataset_v1.csv"

    quality_summary_path = reports_dir / "evidence_quality_summary_v1.csv"
    metrics_summary_path = reports_dir / "evidence_metrics_summary_v1.csv"
    global_metrics_path = reports_dir / "evidence_global_metrics_v1.csv"
    context_summary_path = reports_dir / "evidence_context_summary_v1.csv"
    context_analysis_path = reports_dir / "evidence_context_analysis_v1.csv"
    risk_summary_path = reports_dir / "evidence_risk_summary_v1.csv"
    risk_by_context_path = reports_dir / "evidence_risk_by_context_v1.csv"
    risk_by_market_cost_regime_path = reports_dir / "evidence_risk_by_market_cost_regime_v1.csv"
    risk_event_log_path = reports_dir / "evidence_risk_event_log_v1.csv"

    dashboard_summary_path = reports_dir / "forward_evidence_dashboard_summary_v1.csv"
    dashboard_validation_path = reports_dir / "forward_evidence_dashboard_validation_v1.csv"
    dashboard_kpi_path = reports_dir / "forward_evidence_dashboard_kpi_v1.csv"
    dashboard_requirements_path = reports_dir / "forward_evidence_dashboard_requirements_v1.csv"
    dashboard_notes_path = reports_dir / "forward_evidence_dashboard_notes_v1.csv"
    markdown_report_path = reports_dir / "FORWARD_EVIDENCE_DASHBOARD_V1.md"

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

        evidence_dataset_df = ensure_sample_signal_ids(resolved_all_df)

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
            dataset_df=evidence_dataset_df,
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
            dataset_df=evidence_dataset_df,
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

        (
            context_summary_df,
            context_validation_df,
            context_analysis_df,
            cost_profile_analysis_df,
            direction_analysis_df,
            resolution_status_analysis_df,
            context_cost_profile_analysis_df,
            context_notes_df,
        ) = run_context_performance_analyzer(
            dataset_df=evidence_dataset_df,
            config=ContextPerformanceAnalyzerConfig(
                min_resolved_observations=100,
                preferred_resolved_observations=300,
                min_resolved_per_context=30,
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

        (
            risk_summary_df,
            risk_validation_df,
            risk_by_context_df,
            risk_by_cost_profile_df,
            risk_by_direction_df,
            risk_by_context_cost_profile_df,
            risk_by_market_cost_regime_df,
            risk_by_resolution_status_df,
            risk_event_log_df,
            risk_notes_df,
        ) = run_forward_risk_regime_breakdown_analyzer(
            dataset_df=evidence_dataset_df,
            config=ForwardRiskRegimeBreakdownConfig(
                min_resolved_observations=100,
                preferred_resolved_observations=300,
                min_resolved_per_bucket=30,
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

        (
            dashboard_summary_df,
            dashboard_validation_df,
            dashboard_kpi_df,
            dashboard_requirements_df,
            dashboard_notes_df,
            markdown_report,
        ) = run_forward_evidence_dashboard(
            quality_summary_df=quality_summary_df,
            metrics_summary_df=metrics_summary_df,
            global_metrics_df=global_metrics_df,
            context_summary_df=context_summary_df,
            context_analysis_df=context_analysis_df,
            risk_summary_df=risk_summary_df,
            risk_by_context_df=risk_by_context_df,
            risk_by_market_cost_regime_df=risk_by_market_cost_regime_df,
            risk_event_log_df=risk_event_log_df,
            config=ForwardEvidenceDashboardConfig(
                min_resolved_observations=100,
                preferred_resolved_observations=300,
                sample_mode=True,
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
        evidence_dataset_df = pd.DataFrame()
        quality_summary_df = pd.DataFrame()
        metrics_summary_df = pd.DataFrame()
        global_metrics_df = pd.DataFrame()
        context_summary_df = pd.DataFrame()
        context_analysis_df = pd.DataFrame()
        risk_summary_df = pd.DataFrame()
        risk_by_context_df = pd.DataFrame()
        risk_by_market_cost_regime_df = pd.DataFrame()
        risk_event_log_df = pd.DataFrame()
        dashboard_summary_df = pd.DataFrame()
        dashboard_validation_df = pd.DataFrame(workflow_errors)
        dashboard_kpi_df = pd.DataFrame()
        dashboard_requirements_df = pd.DataFrame()
        dashboard_notes_df = pd.DataFrame(workflow_errors)
        markdown_report = f"# Forward Evidence Dashboard V1\n\nWorkflow error: {repr(exc)}\n"

    save_df(source_signals_df, source_signals_path)
    save_df(source_records_df, source_records_path)
    save_df(ohlc_df, ohlc_path)
    save_df(evidence_dataset_df, dataset_path)

    save_df(quality_summary_df, quality_summary_path)
    save_df(metrics_summary_df, metrics_summary_path)
    save_df(global_metrics_df, global_metrics_path)
    save_df(context_summary_df, context_summary_path)
    save_df(context_analysis_df, context_analysis_path)
    save_df(risk_summary_df, risk_summary_path)
    save_df(risk_by_context_df, risk_by_context_path)
    save_df(risk_by_market_cost_regime_df, risk_by_market_cost_regime_path)
    save_df(risk_event_log_df, risk_event_log_path)

    save_df(dashboard_summary_df, dashboard_summary_path)
    save_df(dashboard_validation_df, dashboard_validation_path)
    save_df(dashboard_kpi_df, dashboard_kpi_path)
    save_df(dashboard_requirements_df, dashboard_requirements_path)
    save_df(dashboard_notes_df, dashboard_notes_path)
    markdown_report_path.write_text(markdown_report, encoding="utf-8")

    print_section("FORWARD EVIDENCE DASHBOARD SUMMARY")
    print_selected(
        dashboard_summary_df,
        [
            "validation_passed",
            "sample_mode",
            "dataset_quality_decision",
            "ready_for_phase_4_2_metrics",
            "metrics_decision",
            "context_decision",
            "risk_regime_decision",
            "readiness_state",
            "execution_state",
            "resolved_observations",
            "min_resolved_observations",
            "preferred_resolved_observations",
            "minimum_sample_reached",
            "preferred_sample_reached",
            "sample_gap_to_minimum",
            "sum_result_r",
            "avg_result_r",
            "win_rate",
            "profit_factor",
            "max_drawdown_r",
            "global_worst_result_r",
            "global_worst_mae_r",
            "global_max_consecutive_losses",
            "evidence_report_decision",
        ],
    )

    print_section("DASHBOARD KPI")
    print_selected(
        dashboard_kpi_df,
        [
            "section",
            "metric",
            "value",
        ],
    )

    print_section("READINESS REQUIREMENTS")
    print_selected(
        dashboard_requirements_df,
        [
            "requirement",
            "current_value",
            "required_value",
            "passed",
            "gap",
            "severity",
        ],
    )

    print_section("CONTEXT EVIDENCE")
    print_selected(
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

    print_section("RISK REGIME EVIDENCE")
    print_selected(
        risk_by_market_cost_regime_df,
        [
            "market_regime",
            "cost_regime",
            "resolved_observations",
            "wins",
            "losses",
            "avg_result_r",
            "profit_factor",
            "worst_result_r",
            "worst_mae_r",
            "risk_signal",
            "risk_label",
        ],
    )

    print_section("DASHBOARD NOTES")
    print_selected(
        dashboard_notes_df,
        [
            "note_type",
            "severity",
            "message",
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
    print(f"- {metrics_summary_path}")
    print(f"- {global_metrics_path}")
    print(f"- {context_summary_path}")
    print(f"- {context_analysis_path}")
    print(f"- {risk_summary_path}")
    print(f"- {risk_by_context_path}")
    print(f"- {risk_by_market_cost_regime_path}")
    print(f"- {risk_event_log_path}")
    print(f"- {dashboard_summary_path}")
    print(f"- {dashboard_validation_path}")
    print(f"- {dashboard_kpi_path}")
    print(f"- {dashboard_requirements_path}")
    print(f"- {dashboard_notes_path}")
    print(f"- {markdown_report_path}")

    print()
    print("Restriccion: este dashboard consolida evidencia. No habilita ejecucion operativa.")


if __name__ == "__main__":
    main()