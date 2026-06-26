from pathlib import Path

import pandas as pd

from src.journal.forward_observation_candidate_detector_v1 import (
    build_sample_strategy_signal_candidates,
)
from src.journal.forward_observation_resolution_engine_v1 import (
    build_sample_resolution_ohlc_data,
)
from src.journal.persistent_forward_evidence_cycle_runner_v1 import (
    PersistentForwardEvidenceCycleRunnerConfig,
    run_persistent_forward_evidence_cycle,
)


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * 100)


def save_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def print_selected(
    df: pd.DataFrame,
    columns: list[str],
) -> None:
    if df.empty:
        print("Sin registros.")
        return

    existing_columns = [
        column
        for column in columns
        if column in df.columns
    ]

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
                "price_level_source": (
                    "SAMPLE_PRICE_LEVEL_OVERRIDE_NORMAL_CONTEXT"
                ),
            },
            {
                "signal_id": "",
                "context_name": "WAVE_5_CAUTION_CONTEXT",
                "cost_profile": "QUANTFURY_SWING_BASE_ESTIMATE",
                "direction": "SHORT",
                "entry_price": 65200.0,
                "stop_price": 66000.0,
                "target_price": 63200.0,
                "price_level_source": (
                    "SAMPLE_PRICE_LEVEL_OVERRIDE_WAVE_5_CAUTION"
                ),
            },
        ]
    )


def unpack_cycle_result(
    result: tuple,
) -> dict[str, pd.DataFrame]:
    (
        cycle_summary_df,
        cycle_validation_df,
        controller_summary_df,
        controller_validation_df,
        persistence_summary_df,
        persistence_validation_df,
        persistence_new_rows_df,
        persistence_updated_rows_df,
        persistence_duplicate_rows_df,
        persistence_invalid_rows_df,
        resolved_closed_df,
        still_open_df,
        dataset_after_df,
    ) = result

    return {
        "cycle_summary": cycle_summary_df,
        "cycle_validation": cycle_validation_df,
        "controller_summary": controller_summary_df,
        "controller_validation": controller_validation_df,
        "persistence_summary": persistence_summary_df,
        "persistence_validation": persistence_validation_df,
        "persistence_new_rows": persistence_new_rows_df,
        "persistence_updated_rows": persistence_updated_rows_df,
        "persistence_duplicate_rows": persistence_duplicate_rows_df,
        "persistence_invalid_rows": persistence_invalid_rows_df,
        "resolved_closed": resolved_closed_df,
        "still_open": still_open_df,
        "dataset_after": dataset_after_df,
    }


def main() -> None:
    print("PERSISTENT FORWARD EVIDENCE CYCLE RUNNER V1")
    print("=" * 100)
    print(
        "Purpose: preserve accumulated forward evidence "
        "across repeated cycles"
    )
    print("Restriction: evidence persistence only. No execution.")
    print()

    reports_dir = (
        Path("reports")
        / "persistent_forward_evidence_cycle_runner_v1"
    )

    reports_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    validation_dataset_path = (
        Path("data")
        / "forward_evidence"
        / "forward_evidence_dataset_v1_cycle_validation.csv"
    )

    validation_backup_dir = (
        Path("data")
        / "forward_evidence"
        / "cycle_validation_backups"
    )

    validation_snapshot_dir = (
        Path("data")
        / "forward_evidence"
        / "cycle_validation_snapshots"
    )

    source_signals_df = build_sample_strategy_signal_candidates()
    price_levels_df = build_sample_price_level_overrides()
    ohlc_df = build_sample_resolution_ohlc_data()

    config = PersistentForwardEvidenceCycleRunnerConfig(
        dataset_path=str(validation_dataset_path),
        backup_dir=str(validation_backup_dir),
        snapshot_dir=str(validation_snapshot_dir),
        min_forward_observations=100,
        preferred_forward_observations=300,
        timestamp_column="timestamp",
        same_bar_policy="CONSERVATIVE_STOP",
        max_bars_after_observation=96,
        create_backup_before_write=True,
        create_snapshot_after_write=True,
        paper_trade_execution_allowed=False,
        real_capital_allowed=False,
        live_alerts_allowed=False,
        exchange_execution_allowed=False,
        automation_allowed=False,
    )

    workflow_errors = []

    try:
        first_cycle = unpack_cycle_result(
            run_persistent_forward_evidence_cycle(
                source_signals_df=source_signals_df,
                ohlc_df=ohlc_df,
                price_levels_df=price_levels_df,
                config=config,
            )
        )

        second_cycle = unpack_cycle_result(
            run_persistent_forward_evidence_cycle(
                source_signals_df=source_signals_df,
                ohlc_df=ohlc_df,
                price_levels_df=price_levels_df,
                config=config,
            )
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

        empty = pd.DataFrame()

        first_cycle = {
            "cycle_summary": empty,
            "cycle_validation": pd.DataFrame(workflow_errors),
            "controller_summary": empty,
            "controller_validation": empty,
            "persistence_summary": empty,
            "persistence_validation": empty,
            "persistence_new_rows": empty,
            "persistence_updated_rows": empty,
            "persistence_duplicate_rows": empty,
            "persistence_invalid_rows": empty,
            "resolved_closed": empty,
            "still_open": empty,
            "dataset_after": empty,
        }

        second_cycle = {
            key: pd.DataFrame()
            for key in first_cycle
        }

    save_df(
        source_signals_df,
        reports_dir / "persistent_cycle_source_signals_v1.csv",
    )

    save_df(
        price_levels_df,
        reports_dir / "persistent_cycle_price_levels_v1.csv",
    )

    save_df(
        ohlc_df,
        reports_dir / "persistent_cycle_sample_ohlc_v1.csv",
    )

    for cycle_name, cycle_data in [
        ("first_cycle", first_cycle),
        ("second_cycle", second_cycle),
    ]:
        for output_name, output_df in cycle_data.items():
            save_df(
                output_df,
                reports_dir
                / f"{cycle_name}_{output_name}_v1.csv",
            )

    print_section("FIRST PERSISTENT CYCLE SUMMARY")
    print_selected(
        first_cycle["cycle_summary"],
        [
            "cycle_id",
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
            "dataset_write_required",
            "dataset_write_performed",
            "backup_created",
            "snapshot_created",
            "controller_decision",
            "persistence_decision",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "live_alerts_allowed",
            "exchange_execution_allowed",
            "automation_allowed",
            "cycle_decision",
        ],
    )

    print_section("FIRST CYCLE NEW ROWS")
    print_selected(
        first_cycle["persistence_new_rows"],
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

    print_section("FIRST CYCLE RESOLVED OBSERVATIONS")
    print_selected(
        first_cycle["resolved_closed"],
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
        ],
    )

    print_section("SECOND PERSISTENT CYCLE SUMMARY")
    print_selected(
        second_cycle["cycle_summary"],
        [
            "cycle_id",
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
            "dataset_write_required",
            "dataset_write_performed",
            "backup_created",
            "snapshot_created",
            "persistence_decision",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "live_alerts_allowed",
            "exchange_execution_allowed",
            "automation_allowed",
            "cycle_decision",
        ],
    )

    print_section("SECOND CYCLE DUPLICATE ROWS")
    print_selected(
        second_cycle["persistence_duplicate_rows"],
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

    print_section("PERSISTED DATASET")
    print_selected(
        second_cycle["dataset_after"],
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

    print()
    print("ARCHIVOS PRINCIPALES")
    print("=" * 100)
    print(f"- Dataset: {validation_dataset_path}")
    print(f"- Backups: {validation_backup_dir}")
    print(f"- Snapshots: {validation_snapshot_dir}")
    print(f"- Reportes: {reports_dir}")

    print()
    print(
        "Restriccion: este ciclo persiste evidencia. "
        "No habilita ejecucion operativa."
    )


if __name__ == "__main__":
    main()