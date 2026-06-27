from pathlib import Path

import pandas as pd

from src.journal.operational_persistent_cycle_integration_v1 import (
    OperationalPersistentCycleIntegrationConfig,
    run_operational_persistent_cycle_integration,
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


def main() -> None:
    print("OPERATIONAL PERSISTENT CYCLE INTEGRATION V1")
    print("=" * 100)
    print("Purpose: connect validated operational inputs to persistent forward evidence dataset")
    print("Restriction: persistence only. No execution.")
    print()

    reports_dir = (
        Path("reports")
        / "operational_persistent_cycle_integration_v1"
    )

    reports_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    workflow_errors = []

    try:
        (
            integration_summary_df,
            adapter_summary_df,
            adapter_validation_df,
            file_inventory_df,
            generated_observations_df,
            rejected_observations_df,
            persistence_summary_df,
            final_dataset_df,
            adapter_rejected_files_df,
        ) = run_operational_persistent_cycle_integration(
            config=OperationalPersistentCycleIntegrationConfig(
                operational_root="data/forward_evidence/operational",
                min_forward_observations=100,
                preferred_forward_observations=300,
                paper_trade_execution_allowed=False,
                real_capital_allowed=False,
                live_alerts_allowed=False,
                exchange_execution_allowed=False,
                automation_allowed=False,
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

        integration_summary_df = pd.DataFrame(
            [
                {
                    "validation_passed": False,
                    "adapter_decision": "",
                    "input_ready_for_cycle": False,
                    "generated_observations": 0,
                    "rejected_observations": 0,
                    "closed_observations": 0,
                    "open_observations": 0,
                    "new_rows_added": 0,
                    "updated_rows": 0,
                    "duplicate_rows_skipped": 0,
                    "dataset_rows_after": 0,
                    "dataset_write_required": False,
                    "dataset_write_performed": False,
                    "backup_created": False,
                    "snapshot_created": False,
                    "paper_trade_execution_allowed": False,
                    "real_capital_allowed": False,
                    "live_alerts_allowed": False,
                    "exchange_execution_allowed": False,
                    "automation_allowed": False,
                    "execution_allowed": False,
                    "integration_decision": "OPERATIONAL_INTEGRATION_WORKFLOW_ERROR",
                }
            ]
        )

        adapter_summary_df = pd.DataFrame()
        adapter_validation_df = pd.DataFrame(workflow_errors)
        file_inventory_df = pd.DataFrame()
        generated_observations_df = pd.DataFrame()
        rejected_observations_df = pd.DataFrame()
        persistence_summary_df = pd.DataFrame()
        final_dataset_df = pd.DataFrame()
        adapter_rejected_files_df = pd.DataFrame()

    save_df(
        integration_summary_df,
        reports_dir / "operational_integration_summary_v1.csv",
    )

    save_df(
        adapter_summary_df,
        reports_dir / "operational_integration_adapter_summary_v1.csv",
    )

    save_df(
        adapter_validation_df,
        reports_dir / "operational_integration_adapter_validation_v1.csv",
    )

    save_df(
        file_inventory_df,
        reports_dir / "operational_integration_file_inventory_v1.csv",
    )

    save_df(
        generated_observations_df,
        reports_dir / "operational_integration_generated_observations_v1.csv",
    )

    save_df(
        rejected_observations_df,
        reports_dir / "operational_integration_rejected_observations_v1.csv",
    )

    save_df(
        persistence_summary_df,
        reports_dir / "operational_integration_persistence_summary_v1.csv",
    )

    save_df(
        final_dataset_df,
        reports_dir / "operational_integration_dataset_preview_v1.csv",
    )

    save_df(
        adapter_rejected_files_df,
        reports_dir / "operational_integration_adapter_rejected_files_v1.csv",
    )

    print_section("OPERATIONAL INTEGRATION SUMMARY")
    print_selected(
        integration_summary_df,
        [
            "validation_passed",
            "adapter_decision",
            "input_ready_for_cycle",
            "signal_files_found",
            "ohlc_files_found",
            "price_level_files_found",
            "adapted_signal_rows",
            "adapted_ohlc_rows",
            "adapted_price_level_rows",
            "generated_observations",
            "rejected_observations",
            "closed_observations",
            "open_observations",
            "error_observations",
            "wins",
            "losses",
            "new_rows_added",
            "updated_rows",
            "duplicate_rows_skipped",
            "invalid_rows",
            "dataset_rows_after",
            "dataset_write_required",
            "dataset_write_performed",
            "backup_created",
            "snapshot_created",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "live_alerts_allowed",
            "exchange_execution_allowed",
            "automation_allowed",
            "execution_allowed",
            "integration_decision",
        ],
    )

    print_section("ADAPTER SUMMARY")
    print_selected(
        adapter_summary_df,
        [
            "validation_passed",
            "validation_error_count",
            "signal_files_found",
            "ohlc_files_found",
            "price_level_files_found",
            "adapted_signal_rows",
            "adapted_ohlc_rows",
            "adapted_price_level_rows",
            "rejected_files",
            "input_ready_for_cycle",
            "processing_allowed",
            "execution_allowed",
            "adapter_decision",
        ],
    )

    print_section("FILE INVENTORY")
    print_selected(
        file_inventory_df,
        [
            "input_type",
            "directory",
            "directory_exists",
            "csv_files_found",
            "files",
        ],
    )

    print_section("GENERATED OBSERVATIONS")
    print_selected(
        generated_observations_df,
        [
            "signal_id",
            "observed_at",
            "symbol",
            "timeframe",
            "signal_type",
            "router_decision",
            "context_name",
            "cost_profile",
            "direction",
            "entry_price",
            "stop_price",
            "target_price",
            "resolution_status",
            "result_r",
            "mfe_r",
            "mae_r",
            "bars_to_resolution",
        ],
    )

    print_section("REJECTED OBSERVATIONS")
    print_selected(
        rejected_observations_df,
        [
            "observed_at",
            "symbol",
            "timeframe",
            "context_name",
            "cost_profile",
            "direction",
            "rejection_reason",
            "details",
            "source_file",
        ],
    )

    print_section("PERSISTENCE SUMMARY")
    print_selected(
        persistence_summary_df,
        [
            "new_rows_added",
            "updated_rows",
            "duplicate_rows_skipped",
            "invalid_rows",
            "dataset_rows_after",
            "dataset_write_required",
        ],
    )

    print_section("DATASET PREVIEW")
    print_selected(
        final_dataset_df.tail(10) if not final_dataset_df.empty else final_dataset_df,
        [
            "signal_id",
            "observed_at",
            "symbol",
            "timeframe",
            "context_name",
            "cost_profile",
            "direction",
            "entry_price",
            "stop_price",
            "target_price",
            "resolution_status",
            "result_r",
            "mfe_r",
            "mae_r",
            "bars_to_resolution",
        ],
    )

    print_section("ADAPTER VALIDATION")
    print_selected(
        adapter_validation_df,
        [
            "input_type",
            "source_file",
            "check_name",
            "passed",
            "severity",
            "details",
        ],
    )

    print_section("ADAPTER REJECTED FILES")
    print_selected(
        adapter_rejected_files_df,
        [
            "input_type",
            "source_file",
            "rejection_reason",
            "details",
        ],
    )

    print()
    print("ARCHIVOS PRINCIPALES")
    print("=" * 100)
    print("- Dataset operativo: data/forward_evidence/operational/forward_evidence_dataset_v1.csv")
    print("- Señales: data/forward_evidence/operational/input/signals/")
    print("- OHLC: data/forward_evidence/operational/input/ohlc/")
    print("- Price levels: data/forward_evidence/operational/input/price_levels/")
    print("- Backups: data/forward_evidence/operational/backups/")
    print("- Snapshots: data/forward_evidence/operational/snapshots/")
    print(f"- Reportes: {reports_dir}")

    print()
    print(
        "Restriccion: esta integracion persiste evidencia forward. "
        "No habilita ejecucion operativa."
    )


if __name__ == "__main__":
    main()