from pathlib import Path

import pandas as pd

from src.journal.operational_forward_evidence_bootstrap_v1 import (
    OperationalForwardEvidenceBootstrapConfig,
    build_price_level_template_df,
    build_schema_dictionary_df,
    run_operational_forward_evidence_bootstrap,
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
    print("OPERATIONAL FORWARD EVIDENCE DATASET BOOTSTRAP V1")
    print("=" * 100)
    print("Purpose: prepare operational forward evidence directories, dataset, and templates")
    print("Restriction: bootstrap only. No execution.")
    print()

    reports_dir = (
        Path("reports")
        / "operational_forward_evidence_bootstrap_v1"
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
            paths_df,
            directory_status_df,
            dataset_df,
            signal_template_df,
            ohlc_template_df,
        ) = run_operational_forward_evidence_bootstrap(
            config=OperationalForwardEvidenceBootstrapConfig(
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

        price_level_template_df = build_price_level_template_df()
        schema_dictionary_df = build_schema_dictionary_df()

    except Exception as exc:
        workflow_errors.append(
            {
                "check_name": "workflow_error",
                "passed": False,
                "severity": "ERROR",
                "details": repr(exc),
            }
        )

        summary_df = pd.DataFrame()
        validation_df = pd.DataFrame(workflow_errors)
        paths_df = pd.DataFrame()
        directory_status_df = pd.DataFrame()
        dataset_df = pd.DataFrame()
        signal_template_df = pd.DataFrame()
        ohlc_template_df = pd.DataFrame()
        price_level_template_df = pd.DataFrame()
        schema_dictionary_df = pd.DataFrame()

    save_df(
        summary_df,
        reports_dir / "operational_bootstrap_summary_v1.csv",
    )

    save_df(
        validation_df,
        reports_dir / "operational_bootstrap_validation_v1.csv",
    )

    save_df(
        paths_df,
        reports_dir / "operational_bootstrap_paths_v1.csv",
    )

    save_df(
        directory_status_df,
        reports_dir / "operational_bootstrap_directory_status_v1.csv",
    )

    save_df(
        dataset_df,
        reports_dir / "operational_bootstrap_dataset_preview_v1.csv",
    )

    save_df(
        signal_template_df,
        reports_dir / "operational_bootstrap_signal_template_v1.csv",
    )

    save_df(
        ohlc_template_df,
        reports_dir / "operational_bootstrap_ohlc_template_v1.csv",
    )

    save_df(
        price_level_template_df,
        reports_dir / "operational_bootstrap_price_level_template_v1.csv",
    )

    save_df(
        schema_dictionary_df,
        reports_dir / "operational_bootstrap_schema_dictionary_v1.csv",
    )

    print_section("OPERATIONAL BOOTSTRAP SUMMARY")
    print_selected(
        summary_df,
        [
            "validation_passed",
            "dataset_created",
            "dataset_exists",
            "dataset_rows",
            "signal_template_created",
            "ohlc_template_created",
            "price_level_template_created",
            "schema_dictionary_created",
            "input_dirs_created",
            "signal_input_files",
            "ohlc_input_files",
            "price_level_input_files",
            "input_ready_for_processing",
            "processing_blocked_without_real_inputs",
            "readiness_state",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "live_alerts_allowed",
            "exchange_execution_allowed",
            "automation_allowed",
            "execution_allowed",
            "bootstrap_decision",
        ],
    )

    print_section("VALIDATION")
    print_selected(
        validation_df,
        [
            "check_name",
            "passed",
            "severity",
            "details",
        ],
    )

    print_section("OPERATIONAL PATHS")
    print_selected(
        paths_df,
        [
            "path_key",
            "path",
            "exists",
            "is_file",
            "is_dir",
        ],
    )

    print_section("DATASET PREVIEW")
    print_selected(
        dataset_df,
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
        ],
    )

    print_section("SIGNAL INPUT TEMPLATE COLUMNS")
    print(",".join(signal_template_df.columns.tolist()))

    print_section("OHLC INPUT TEMPLATE COLUMNS")
    print(",".join(ohlc_template_df.columns.tolist()))

    print_section("PRICE LEVEL TEMPLATE COLUMNS")
    print(",".join(price_level_template_df.columns.tolist()))

    print()
    print("ARCHIVOS PRINCIPALES")
    print("=" * 100)
    print("- Dataset operativo: data/forward_evidence/operational/forward_evidence_dataset_v1.csv")
    print("- Señales exportadas: data/forward_evidence/operational/input/signals/")
    print("- OHLC exportado: data/forward_evidence/operational/input/ohlc/")
    print("- Niveles de precio: data/forward_evidence/operational/input/price_levels/")
    print("- Backups: data/forward_evidence/operational/backups/")
    print("- Snapshots: data/forward_evidence/operational/snapshots/")
    print("- Templates: data/forward_evidence/operational/templates/")
    print(f"- Reportes: {reports_dir}")

    print()
    print(
        "Restriccion: este bootstrap prepara estructura operativa. "
        "No habilita ejecucion operativa."
    )


if __name__ == "__main__":
    main()