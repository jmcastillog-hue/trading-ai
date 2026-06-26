from pathlib import Path

import pandas as pd

from src.journal.forward_evidence_accumulation_controller_v1 import (
    ForwardEvidenceAccumulationControllerConfig,
    run_forward_evidence_accumulation_controller,
)
from src.journal.forward_evidence_dataset_persistence_v1 import (
    ForwardEvidenceDatasetPersistenceConfig,
    persist_forward_evidence_dataset,
    read_forward_evidence_dataset,
    write_forward_evidence_dataset,
)
from src.journal.forward_observation_candidate_detector_v1 import (
    build_sample_strategy_signal_candidates,
)
from src.journal.forward_observation_resolution_engine_v1 import (
    build_sample_resolution_ohlc_data,
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


def build_sample_price_level_overrides() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "signal_id": "",
                "context_name": "NORMAL_VALIDATION_CONTEXT",
                "cost_profile": "BINANCE_SCALP_BASE_ESTIMATE",
                "direction": "SHORT",
                "entry_price": 65000.0,
                "stop_price": 65500.0,
                "target_price": 63750.0,
                "price_level_source": "SAMPLE_PRICE_LEVEL_OVERRIDE_NORMAL_CONTEXT",
            },
            {
                "signal_id": "",
                "context_name": "WAVE_5_CAUTION_CONTEXT",
                "cost_profile": "QUANTFURY_SWING_BASE_ESTIMATE",
                "direction": "SHORT",
                "entry_price": 65200.0,
                "stop_price": 66000.0,
                "target_price": 63200.0,
                "price_level_source": "SAMPLE_PRICE_LEVEL_OVERRIDE_WAVE_5_CAUTION",
            },
        ]
    )


def main() -> None:
    print("FORWARD EVIDENCE DATASET PERSISTENCE V1")
    print("=" * 100)
    print("Purpose: persist resolved forward evidence into an accumulated dataset")
    print("Restriction: dataset persistence only. No execution.")
    print()

    reports_dir = Path("reports") / "forward_evidence_dataset_persistence_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    validation_dataset_path = (
        Path("data")
        / "forward_evidence"
        / "forward_evidence_dataset_v1_validation_sample.csv"
    )

    if validation_dataset_path.exists():
        validation_dataset_path.unlink()

    source_signals_path = reports_dir / "persistence_source_signals_v1.csv"
    price_levels_path = reports_dir / "persistence_price_level_overrides_v1.csv"
    sample_ohlc_path = reports_dir / "persistence_sample_ohlc_v1.csv"

    controller_summary_path = reports_dir / "persistence_controller_summary_v1.csv"
    controller_validation_path = reports_dir / "persistence_controller_validation_v1.csv"
    controller_dataset_after_resolution_path = (
        reports_dir / "persistence_controller_dataset_after_resolution_v1.csv"
    )

    persistence_summary_path = reports_dir / "persistence_summary_v1.csv"
    persistence_validation_path = reports_dir / "persistence_validation_v1.csv"
    persistence_new_rows_path = reports_dir / "persistence_new_rows_v1.csv"
    persistence_updated_rows_path = reports_dir / "persistence_updated_rows_v1.csv"
    persistence_duplicates_path = reports_dir / "persistence_duplicate_rows_v1.csv"
    persistence_invalid_rows_path = reports_dir / "persistence_invalid_rows_v1.csv"
    persistence_dataset_after_path = reports_dir / "persistence_dataset_after_v1.csv"

    duplicate_test_summary_path = reports_dir / "persistence_duplicate_test_summary_v1.csv"
    duplicate_test_validation_path = reports_dir / "persistence_duplicate_test_validation_v1.csv"
    duplicate_test_duplicates_path = reports_dir / "persistence_duplicate_test_duplicates_v1.csv"
    duplicate_test_dataset_after_path = reports_dir / "persistence_duplicate_test_dataset_after_v1.csv"

    workflow_errors = []

    try:
        source_signals_df = build_sample_strategy_signal_candidates()
        price_levels_df = build_sample_price_level_overrides()
        ohlc_df = build_sample_resolution_ohlc_data()

        (
            controller_summary_df,
            controller_validation_df,
            runner_summary_df,
            runner_validation_df,
            resolver_summary_df,
            resolver_validation_df,
            generated_observations_df,
            detector_accepted_df,
            detector_rejected_df,
            accepted_new_df,
            duplicate_df,
            priced_dataset_df,
            resolved_closed_df,
            still_open_df,
            controller_dataset_after_resolution_df,
        ) = run_forward_evidence_accumulation_controller(
            source_signals_df=source_signals_df,
            existing_dataset_df=pd.DataFrame(),
            ohlc_df=ohlc_df,
            price_levels_df=price_levels_df,
            config=ForwardEvidenceAccumulationControllerConfig(
                min_forward_observations=100,
                preferred_forward_observations=300,
                timestamp_column="timestamp",
                same_bar_policy="CONSERVATIVE_STOP",
                max_bars_after_observation=96,
                paper_trade_execution_allowed=False,
                real_capital_allowed=False,
                live_alerts_allowed=False,
                exchange_execution_allowed=False,
                automation_allowed=False,
            ),
        )

        persistence_config = ForwardEvidenceDatasetPersistenceConfig(
            min_forward_observations=100,
            preferred_forward_observations=300,
            paper_trade_execution_allowed=False,
            real_capital_allowed=False,
            live_alerts_allowed=False,
            exchange_execution_allowed=False,
            automation_allowed=False,
        )

        existing_dataset_before_df = read_forward_evidence_dataset(validation_dataset_path)

        (
            persistence_summary_df,
            persistence_validation_df,
            persistence_new_rows_df,
            persistence_updated_rows_df,
            persistence_duplicate_rows_df,
            persistence_invalid_rows_df,
            persistence_dataset_after_df,
        ) = persist_forward_evidence_dataset(
            incoming_dataset_df=controller_dataset_after_resolution_df,
            existing_dataset_df=existing_dataset_before_df,
            config=persistence_config,
        )

        write_forward_evidence_dataset(
            dataset_df=persistence_dataset_after_df,
            dataset_path=validation_dataset_path,
        )

        existing_dataset_for_duplicate_test_df = read_forward_evidence_dataset(
            validation_dataset_path
        )

        (
            duplicate_test_summary_df,
            duplicate_test_validation_df,
            duplicate_test_new_rows_df,
            duplicate_test_updated_rows_df,
            duplicate_test_duplicate_rows_df,
            duplicate_test_invalid_rows_df,
            duplicate_test_dataset_after_df,
        ) = persist_forward_evidence_dataset(
            incoming_dataset_df=controller_dataset_after_resolution_df,
            existing_dataset_df=existing_dataset_for_duplicate_test_df,
            config=persistence_config,
        )

        write_forward_evidence_dataset(
            dataset_df=duplicate_test_dataset_after_df,
            dataset_path=validation_dataset_path,
        )

    except Exception as exc:
        workflow_errors.append(
            {
                "check_name": "workflow_error",
                "passed": False,
                "severity": "ERROR",
                "details": repr(exc),
            }
        )

        source_signals_df = pd.DataFrame()
        price_levels_df = pd.DataFrame()
        ohlc_df = pd.DataFrame()

        controller_summary_df = pd.DataFrame()
        controller_validation_df = pd.DataFrame()
        controller_dataset_after_resolution_df = pd.DataFrame()

        persistence_summary_df = pd.DataFrame()
        persistence_validation_df = pd.DataFrame(workflow_errors)
        persistence_new_rows_df = pd.DataFrame()
        persistence_updated_rows_df = pd.DataFrame()
        persistence_duplicate_rows_df = pd.DataFrame()
        persistence_invalid_rows_df = pd.DataFrame()
        persistence_dataset_after_df = pd.DataFrame()

        duplicate_test_summary_df = pd.DataFrame()
        duplicate_test_validation_df = pd.DataFrame()
        duplicate_test_duplicate_rows_df = pd.DataFrame()
        duplicate_test_dataset_after_df = pd.DataFrame()

    save_df(source_signals_df, source_signals_path)
    save_df(price_levels_df, price_levels_path)
    save_df(ohlc_df, sample_ohlc_path)

    save_df(controller_summary_df, controller_summary_path)
    save_df(controller_validation_df, controller_validation_path)
    save_df(
        controller_dataset_after_resolution_df,
        controller_dataset_after_resolution_path,
    )

    save_df(persistence_summary_df, persistence_summary_path)
    save_df(persistence_validation_df, persistence_validation_path)
    save_df(persistence_new_rows_df, persistence_new_rows_path)
    save_df(persistence_updated_rows_df, persistence_updated_rows_path)
    save_df(persistence_duplicate_rows_df, persistence_duplicates_path)
    save_df(persistence_invalid_rows_df, persistence_invalid_rows_path)
    save_df(persistence_dataset_after_df, persistence_dataset_after_path)

    save_df(duplicate_test_summary_df, duplicate_test_summary_path)
    save_df(duplicate_test_validation_df, duplicate_test_validation_path)
    save_df(duplicate_test_duplicate_rows_df, duplicate_test_duplicates_path)
    save_df(duplicate_test_dataset_after_df, duplicate_test_dataset_after_path)

    print_section("ACCUMULATION CONTROLLER SUMMARY")
    print_selected(
        controller_summary_df,
        [
            "controller_validation_passed",
            "source_signal_rows",
            "new_observations",
            "closed_observations",
            "open_observations",
            "error_observations",
            "avg_result_r",
            "sum_result_r",
            "cumulative_closed_observations",
            "readiness_state",
            "controller_decision",
        ],
    )

    print_section("PERSISTENCE SUMMARY")
    print_selected(
        persistence_summary_df,
        [
            "validation_passed",
            "incoming_rows",
            "existing_rows_before",
            "new_rows_added",
            "updated_rows",
            "duplicate_rows_skipped",
            "invalid_rows",
            "dataset_rows_after",
            "closed_observations",
            "open_observations",
            "error_observations",
            "wins",
            "losses",
            "avg_result_r",
            "sum_result_r",
            "cumulative_closed_observations",
            "minimum_sample_reached",
            "preferred_sample_reached",
            "sample_gap_to_minimum",
            "sample_gap_to_preferred",
            "readiness_state",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "live_alerts_allowed",
            "exchange_execution_allowed",
            "automation_allowed",
            "persistence_decision",
        ],
    )

    print_section("PERSISTENCE NEW ROWS")
    print_selected(
        persistence_new_rows_df,
        [
            "signal_id",
            "observed_at",
            "symbol",
            "timeframe",
            "context_name",
            "cost_profile",
            "direction",
            "resolution_status",
            "result_r",
            "persistence_status",
        ],
    )

    print_section("PERSISTENCE DUPLICATE ROWS")
    print_selected(
        persistence_duplicate_rows_df,
        [
            "signal_id",
            "observed_at",
            "symbol",
            "timeframe",
            "context_name",
            "cost_profile",
            "direction",
            "resolution_status",
            "persistence_status",
        ],
    )

    print_section("PERSISTED DATASET AFTER FIRST RUN")
    print_selected(
        persistence_dataset_after_df,
        [
            "signal_id",
            "observed_at",
            "symbol",
            "timeframe",
            "context_name",
            "cost_profile",
            "direction",
            "resolution_status",
            "result_r",
            "mfe_r",
            "mae_r",
            "bars_to_resolution",
            "persistence_status",
        ],
    )

    print_section("DUPLICATE TEST SUMMARY")
    print_selected(
        duplicate_test_summary_df,
        [
            "validation_passed",
            "incoming_rows",
            "existing_rows_before",
            "new_rows_added",
            "updated_rows",
            "duplicate_rows_skipped",
            "invalid_rows",
            "dataset_rows_after",
            "closed_observations",
            "open_observations",
            "error_observations",
            "cumulative_closed_observations",
            "sample_gap_to_minimum",
            "sample_gap_to_preferred",
            "readiness_state",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "live_alerts_allowed",
            "exchange_execution_allowed",
            "automation_allowed",
            "persistence_decision",
        ],
    )

    print_section("DUPLICATE TEST DUPLICATE ROWS")
    print_selected(
        duplicate_test_duplicate_rows_df,
        [
            "signal_id",
            "observed_at",
            "symbol",
            "timeframe",
            "context_name",
            "cost_profile",
            "direction",
            "resolution_status",
            "persistence_status",
        ],
    )

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {source_signals_path}")
    print(f"- {price_levels_path}")
    print(f"- {sample_ohlc_path}")
    print(f"- {controller_summary_path}")
    print(f"- {controller_validation_path}")
    print(f"- {controller_dataset_after_resolution_path}")
    print(f"- {persistence_summary_path}")
    print(f"- {persistence_validation_path}")
    print(f"- {persistence_new_rows_path}")
    print(f"- {persistence_updated_rows_path}")
    print(f"- {persistence_duplicates_path}")
    print(f"- {persistence_invalid_rows_path}")
    print(f"- {persistence_dataset_after_path}")
    print(f"- {duplicate_test_summary_path}")
    print(f"- {duplicate_test_validation_path}")
    print(f"- {duplicate_test_duplicates_path}")
    print(f"- {duplicate_test_dataset_after_path}")
    print(f"- {validation_dataset_path}")

    print()
    print("Restriccion: este modulo persiste evidencia. No habilita ejecucion operativa.")


if __name__ == "__main__":
    main()