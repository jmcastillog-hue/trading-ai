from pathlib import Path

import pandas as pd

from src.journal.forward_observation_batch_runner_v1 import (
    ForwardObservationBatchRunnerConfig,
    run_forward_observation_batch_runner,
)
from src.journal.forward_observation_candidate_detector_v1 import (
    build_sample_strategy_signal_candidates,
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


def main() -> None:
    print("FORWARD OBSERVATION BATCH RUNNER V1")
    print("=" * 100)
    print("Purpose: process candidate signals into forward observations in batch")
    print("Restriction: observation accumulation only. No execution.")
    print()

    reports_dir = Path("reports") / "forward_observation_batch_runner_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    source_signals_path = reports_dir / "batch_source_signals_v1.csv"
    summary_path = reports_dir / "batch_runner_summary_v1.csv"
    validation_path = reports_dir / "batch_runner_validation_v1.csv"
    generated_observations_path = reports_dir / "batch_generated_observations_v1.csv"
    detector_accepted_path = reports_dir / "batch_detector_accepted_v1.csv"
    detector_rejected_path = reports_dir / "batch_detector_rejected_v1.csv"
    accepted_new_path = reports_dir / "batch_accepted_new_observations_v1.csv"
    duplicate_path = reports_dir / "batch_duplicate_observations_v1.csv"
    dataset_after_path = reports_dir / "batch_dataset_after_v1.csv"

    duplicate_test_summary_path = reports_dir / "batch_duplicate_test_summary_v1.csv"
    duplicate_test_skipped_path = reports_dir / "batch_duplicate_test_skipped_v1.csv"

    workflow_errors = []

    try:
        source_signals_df = build_sample_strategy_signal_candidates()

        config = ForwardObservationBatchRunnerConfig(
            min_forward_observations=100,
            preferred_forward_observations=300,
            paper_trade_execution_allowed=False,
            real_capital_allowed=False,
            live_alerts_allowed=False,
            exchange_execution_allowed=False,
            automation_allowed=False,
        )

        (
            summary_df,
            validation_df,
            generated_observations_df,
            detector_accepted_df,
            detector_rejected_df,
            accepted_new_df,
            duplicate_df,
            dataset_after_df,
        ) = run_forward_observation_batch_runner(
            source_signals_df=source_signals_df,
            existing_dataset_df=pd.DataFrame(),
            config=config,
        )

        (
            duplicate_test_summary_df,
            duplicate_test_validation_df,
            duplicate_test_generated_observations_df,
            duplicate_test_detector_accepted_df,
            duplicate_test_detector_rejected_df,
            duplicate_test_accepted_new_df,
            duplicate_test_duplicate_df,
            duplicate_test_dataset_after_df,
        ) = run_forward_observation_batch_runner(
            source_signals_df=source_signals_df,
            existing_dataset_df=dataset_after_df,
            config=config,
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
        summary_df = pd.DataFrame()
        validation_df = pd.DataFrame(workflow_errors)
        generated_observations_df = pd.DataFrame()
        detector_accepted_df = pd.DataFrame()
        detector_rejected_df = pd.DataFrame()
        accepted_new_df = pd.DataFrame()
        duplicate_df = pd.DataFrame()
        dataset_after_df = pd.DataFrame()

        duplicate_test_summary_df = pd.DataFrame()
        duplicate_test_duplicate_df = pd.DataFrame()

    save_df(source_signals_df, source_signals_path)
    save_df(summary_df, summary_path)
    save_df(validation_df, validation_path)
    save_df(generated_observations_df, generated_observations_path)
    save_df(detector_accepted_df, detector_accepted_path)
    save_df(detector_rejected_df, detector_rejected_path)
    save_df(accepted_new_df, accepted_new_path)
    save_df(duplicate_df, duplicate_path)
    save_df(dataset_after_df, dataset_after_path)

    save_df(duplicate_test_summary_df, duplicate_test_summary_path)
    save_df(duplicate_test_duplicate_df, duplicate_test_skipped_path)

    print_section("BATCH RUNNER SUMMARY")
    print_selected(
        summary_df,
        [
            "validation_passed",
            "source_signal_rows",
            "detector_accepted_candidates",
            "detector_rejected_candidates",
            "generated_observations",
            "accepted_new_observations",
            "skipped_duplicate_observations",
            "dataset_rows_after",
            "minimum_sample_reached",
            "preferred_sample_reached",
            "sample_gap_to_minimum",
            "sample_gap_to_preferred",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "live_alerts_allowed",
            "exchange_execution_allowed",
            "automation_allowed",
            "batch_decision",
        ],
    )

    print_section("ACCEPTED NEW OBSERVATIONS")
    print_selected(
        accepted_new_df,
        [
            "signal_id",
            "observed_at",
            "symbol",
            "timeframe",
            "cost_profile",
            "context_name",
            "direction",
            "entry_price",
            "stop_price",
            "target_price",
            "resolution_status",
            "batch_status",
        ],
    )

    print_section("DETECTOR REJECTED CANDIDATES")
    print_selected(
        detector_rejected_df,
        [
            "observed_at",
            "symbol",
            "timeframe",
            "signal_type",
            "router_decision",
            "rejection_reason",
        ],
    )

    print_section("DUPLICATE TEST SUMMARY")
    print_selected(
        duplicate_test_summary_df,
        [
            "validation_passed",
            "source_signal_rows",
            "generated_observations",
            "accepted_new_observations",
            "skipped_duplicate_observations",
            "dataset_rows_after",
            "batch_decision",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "live_alerts_allowed",
            "exchange_execution_allowed",
            "automation_allowed",
        ],
    )

    print_section("DUPLICATE TEST SKIPPED OBSERVATIONS")
    print_selected(
        duplicate_test_duplicate_df,
        [
            "signal_id",
            "observed_at",
            "symbol",
            "timeframe",
            "cost_profile",
            "context_name",
            "direction",
            "batch_status",
        ],
    )

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {source_signals_path}")
    print(f"- {summary_path}")
    print(f"- {validation_path}")
    print(f"- {generated_observations_path}")
    print(f"- {detector_accepted_path}")
    print(f"- {detector_rejected_path}")
    print(f"- {accepted_new_path}")
    print(f"- {duplicate_path}")
    print(f"- {dataset_after_path}")
    print(f"- {duplicate_test_summary_path}")
    print(f"- {duplicate_test_skipped_path}")

    print()
    print("Restriccion: este batch runner acumula observaciones. No habilita ejecucion operativa.")


if __name__ == "__main__":
    main()