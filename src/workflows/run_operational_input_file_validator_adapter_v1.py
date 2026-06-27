from pathlib import Path

import pandas as pd

from src.journal.operational_input_file_validator_adapter_v1 import (
    OperationalInputFileValidatorAdapterConfig,
    run_operational_input_file_validator_adapter,
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
    print("OPERATIONAL INPUT FILE VALIDATOR / ADAPTER V1")
    print("=" * 100)
    print("Purpose: validate exported operational CSV inputs before persistent cycle")
    print("Restriction: validation and adaptation only. No execution.")
    print()

    reports_dir = (
        Path("reports")
        / "operational_input_file_validator_adapter_v1"
    )

    reports_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    workflow_errors = []

    try:
        (
            summary_df,
            validation_df,
            file_inventory_df,
            adapted_signals_df,
            adapted_ohlc_df,
            adapted_price_levels_df,
            rejected_files_df,
        ) = run_operational_input_file_validator_adapter(
            config=OperationalInputFileValidatorAdapterConfig(
                operational_root="data/forward_evidence/operational",
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
                "input_type": "workflow",
                "source_file": "",
                "check_name": "workflow_error",
                "passed": False,
                "severity": "ERROR",
                "details": repr(exc),
            }
        )

        summary_df = pd.DataFrame()
        validation_df = pd.DataFrame(workflow_errors)
        file_inventory_df = pd.DataFrame()
        adapted_signals_df = pd.DataFrame()
        adapted_ohlc_df = pd.DataFrame()
        adapted_price_levels_df = pd.DataFrame()
        rejected_files_df = pd.DataFrame()

    save_df(
        summary_df,
        reports_dir / "operational_input_adapter_summary_v1.csv",
    )

    save_df(
        validation_df,
        reports_dir / "operational_input_adapter_validation_v1.csv",
    )

    save_df(
        file_inventory_df,
        reports_dir / "operational_input_adapter_file_inventory_v1.csv",
    )

    save_df(
        adapted_signals_df,
        reports_dir / "operational_input_adapter_adapted_signals_v1.csv",
    )

    save_df(
        adapted_ohlc_df,
        reports_dir / "operational_input_adapter_adapted_ohlc_v1.csv",
    )

    save_df(
        adapted_price_levels_df,
        reports_dir / "operational_input_adapter_adapted_price_levels_v1.csv",
    )

    save_df(
        rejected_files_df,
        reports_dir / "operational_input_adapter_rejected_files_v1.csv",
    )

    print_section("OPERATIONAL INPUT ADAPTER SUMMARY")
    print_selected(
        summary_df,
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
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "live_alerts_allowed",
            "exchange_execution_allowed",
            "automation_allowed",
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

    print_section("VALIDATION")
    print_selected(
        validation_df,
        [
            "input_type",
            "source_file",
            "check_name",
            "passed",
            "severity",
            "details",
        ],
    )

    print_section("ADAPTED SIGNALS")
    print_selected(
        adapted_signals_df,
        [
            "observed_at",
            "symbol",
            "timeframe",
            "signal_type",
            "router_decision",
            "cost_profile",
            "context_name",
            "direction",
            "manual_review_required",
            "source_file",
        ],
    )

    print_section("ADAPTED OHLC")
    print_selected(
        adapted_ohlc_df,
        [
            "timestamp",
            "symbol",
            "timeframe",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "data_source",
            "source_file",
        ],
    )

    print_section("ADAPTED PRICE LEVELS")
    print_selected(
        adapted_price_levels_df,
        [
            "signal_id",
            "context_name",
            "cost_profile",
            "direction",
            "entry_price",
            "stop_price",
            "target_price",
            "price_level_source",
            "source_file",
        ],
    )

    print_section("REJECTED FILES")
    print_selected(
        rejected_files_df,
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
    print("- Señales: data/forward_evidence/operational/input/signals/")
    print("- OHLC: data/forward_evidence/operational/input/ohlc/")
    print("- Niveles: data/forward_evidence/operational/input/price_levels/")
    print(f"- Reportes: {reports_dir}")

    print()
    print(
        "Restriccion: este adaptador valida archivos. "
        "No habilita ejecucion operativa."
    )


if __name__ == "__main__":
    main()