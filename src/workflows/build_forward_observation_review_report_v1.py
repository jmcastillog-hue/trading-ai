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
from src.journal.forward_observation_review_report_v1 import (
    ForwardObservationReviewConfig,
    build_forward_observation_review_report,
)


def print_section(title: str):
    print()
    print(title)
    print("=" * 100)


def save_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def save_text(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def print_selected(df: pd.DataFrame, columns: list[str]) -> None:
    if df.empty:
        print("Sin registros.")
        return

    existing_columns = [column for column in columns if column in df.columns]

    if not existing_columns:
        print(df.to_string(index=False))
        return

    print(df[existing_columns].to_string(index=False))


def main():
    print("FORWARD OBSERVATION REVIEW REPORT V1")
    print("=" * 100)
    print("Purpose: review resolved forward observations and aggregate performance evidence")
    print("Restriction: review report only. No execution.")
    print()

    reports_dir = Path("reports") / "forward_observation_review_report_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    source_signals_path = reports_dir / "review_source_signals_v1.csv"
    source_records_path = reports_dir / "review_source_records_v1.csv"
    ohlc_path = reports_dir / "review_sample_ohlc_v1.csv"
    resolved_all_path = reports_dir / "review_resolved_all_v1.csv"
    resolved_closed_path = reports_dir / "review_resolved_closed_v1.csv"
    resolution_open_path = reports_dir / "review_resolution_open_v1.csv"
    resolution_errors_path = reports_dir / "review_resolution_errors_v1.csv"
    resolution_summary_path = reports_dir / "review_resolution_summary_v1.csv"

    review_summary_path = reports_dir / "review_summary_v1.csv"
    by_context_path = reports_dir / "review_by_context_v1.csv"
    by_cost_profile_path = reports_dir / "review_by_cost_profile_v1.csv"
    by_direction_path = reports_dir / "review_by_direction_v1.csv"
    by_resolution_status_path = reports_dir / "review_by_resolution_status_v1.csv"
    winners_path = reports_dir / "review_winners_v1.csv"
    losers_path = reports_dir / "review_losers_v1.csv"
    open_path = reports_dir / "review_open_observations_v1.csv"
    review_errors_path = reports_dir / "review_errors_v1.csv"
    review_notes_path = reports_dir / "review_notes_v1.csv"
    markdown_report_path = reports_dir / "forward_observation_review_report_v1.md"

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
            resolution_open_df,
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

        (
            review_summary_df,
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
        ) = build_forward_observation_review_report(
            resolved_observations_df=resolved_all_df,
            errors_df=resolution_errors_df,
            config=ForwardObservationReviewConfig(
                min_resolved_observations=100,
                preferred_resolved_observations=300,
                paper_trade_execution_allowed=False,
                real_capital_allowed=False,
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
        resolved_all_df = pd.DataFrame()
        resolved_closed_df = pd.DataFrame()
        resolution_open_df = pd.DataFrame()
        resolution_errors_df = pd.DataFrame(workflow_errors)
        resolution_summary_df = pd.DataFrame()
        review_summary_df = pd.DataFrame()
        by_context_df = pd.DataFrame()
        by_cost_profile_df = pd.DataFrame()
        by_direction_df = pd.DataFrame()
        by_resolution_status_df = pd.DataFrame()
        winners_df = pd.DataFrame()
        losers_df = pd.DataFrame()
        open_df = pd.DataFrame()
        review_errors_df = pd.DataFrame(workflow_errors)
        review_notes_df = pd.DataFrame()
        markdown_report = "# Forward Observation Review Report V1\n\nWorkflow error."

    save_df(source_signals_df, source_signals_path)
    save_df(source_records_df, source_records_path)
    save_df(ohlc_df, ohlc_path)
    save_df(resolved_all_df, resolved_all_path)
    save_df(resolved_closed_df, resolved_closed_path)
    save_df(resolution_open_df, resolution_open_path)
    save_df(resolution_errors_df, resolution_errors_path)
    save_df(resolution_summary_df, resolution_summary_path)

    save_df(review_summary_df, review_summary_path)
    save_df(by_context_df, by_context_path)
    save_df(by_cost_profile_df, by_cost_profile_path)
    save_df(by_direction_df, by_direction_path)
    save_df(by_resolution_status_df, by_resolution_status_path)
    save_df(winners_df, winners_path)
    save_df(losers_df, losers_path)
    save_df(open_df, open_path)
    save_df(review_errors_df, review_errors_path)
    save_df(review_notes_df, review_notes_path)
    save_text(markdown_report, markdown_report_path)

    print_section("RESOLVED SOURCE OBSERVATIONS")
    print_selected(
        resolved_all_df,
        [
            "observed_at",
            "symbol",
            "timeframe",
            "cost_profile",
            "context_name",
            "direction",
            "resolution_status",
            "resolved_at",
            "result_r",
            "mfe_r",
            "mae_r",
            "bars_to_resolution",
        ],
    )

    print_section("REVIEW SUMMARY")
    print_selected(
        review_summary_df,
        [
            "total_observations",
            "resolved_observations",
            "open_observations",
            "total_error_rows",
            "wins",
            "losses",
            "win_rate",
            "avg_result_r",
            "sum_result_r",
            "profit_factor",
            "avg_mfe_r",
            "avg_mae_r",
            "minimum_sample_reached",
            "preferred_sample_reached",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "review_decision",
        ],
    )

    print_section("BY CONTEXT")
    print_selected(
        by_context_df,
        [
            "context_name",
            "total_observations",
            "resolved_observations",
            "wins",
            "losses",
            "win_rate",
            "avg_result_r",
            "profit_factor",
            "avg_mfe_r",
            "avg_mae_r",
        ],
    )

    print_section("BY COST PROFILE")
    print_selected(
        by_cost_profile_df,
        [
            "cost_profile",
            "total_observations",
            "resolved_observations",
            "wins",
            "losses",
            "win_rate",
            "avg_result_r",
            "profit_factor",
            "avg_mfe_r",
            "avg_mae_r",
        ],
    )

    print_section("BY DIRECTION")
    print_selected(
        by_direction_df,
        [
            "direction",
            "total_observations",
            "resolved_observations",
            "wins",
            "losses",
            "win_rate",
            "avg_result_r",
            "profit_factor",
            "avg_mfe_r",
            "avg_mae_r",
        ],
    )

    print_section("BY RESOLUTION STATUS")
    print_selected(
        by_resolution_status_df,
        [
            "resolution_status",
            "total_observations",
            "resolved_observations",
            "wins",
            "losses",
            "win_rate",
            "avg_result_r",
            "profit_factor",
        ],
    )

    print_section("WINNERS")
    print_selected(
        winners_df,
        [
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
        ],
    )

    print_section("LOSERS")
    print_selected(
        losers_df,
        [
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
        ],
    )

    print_section("OPEN OBSERVATIONS")
    print_selected(
        open_df,
        [
            "observed_at",
            "symbol",
            "timeframe",
            "cost_profile",
            "context_name",
            "direction",
            "resolution_status",
            "mfe_r",
            "mae_r",
        ],
    )

    print_section("REVIEW ERRORS")
    print_selected(
        review_errors_df,
        [
            "severity",
            "signal_id",
            "check_name",
            "details",
            "error_source",
        ],
    )

    print_section("REVIEW NOTES")
    print_selected(
        review_notes_df,
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
    print(f"- {resolved_all_path}")
    print(f"- {resolved_closed_path}")
    print(f"- {resolution_open_path}")
    print(f"- {resolution_errors_path}")
    print(f"- {resolution_summary_path}")
    print(f"- {review_summary_path}")
    print(f"- {by_context_path}")
    print(f"- {by_cost_profile_path}")
    print(f"- {by_direction_path}")
    print(f"- {by_resolution_status_path}")
    print(f"- {winners_path}")
    print(f"- {losers_path}")
    print(f"- {open_path}")
    print(f"- {review_errors_path}")
    print(f"- {review_notes_path}")
    print(f"- {markdown_report_path}")

    print()
    print("Restriccion: este reporte revisa evidencia observacional. No ejecuta operaciones.")


if __name__ == "__main__":
    main()