from pathlib import Path

import pandas as pd

from src.journal.manual_observation_processor_v1 import (
    ManualObservationProcessorConfig,
    load_csv_or_fail,
    process_manual_observation_file,
)
from src.journal.system_forward_observation_record_builder_v1 import (
    build_sample_system_forward_observation_candidates,
    build_system_forward_observation_records,
    save_system_records,
    validate_system_records_dataframe,
)


def print_section(title: str):
    print()
    print(title)
    print("=" * 100)


def save_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def main():
    print("SYSTEM FORWARD OBSERVATION RECORD BUILDER V1")
    print("=" * 100)
    print("Purpose: build system-generated forward observation records without execution")
    print()

    reports_dir = Path("reports") / "system_forward_observation_record_builder_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    phase_template_path = (
        Path("reports")
        / "forward_signal_journal_v1"
        / "forward_signal_journal_v1_template.csv"
    )

    system_records_path = (
        reports_dir
        / "system_forward_observation_records_v1.csv"
    )

    validation_dataset_path = (
        reports_dir
        / "system_forward_observation_validation_dataset_v1.csv"
    )

    duplicate_dataset_path = (
        reports_dir
        / "system_forward_observation_duplicate_validation_dataset_v1.csv"
    )

    builder_validation_path = reports_dir / "system_forward_observation_builder_validation_v1.csv"
    processor_summary_path = reports_dir / "system_forward_observation_processor_summary_v1.csv"
    validation_summary_path = reports_dir / "system_forward_observation_validation_summary_v1.csv"
    journal_summary_path = reports_dir / "system_forward_observation_journal_summary_v1.csv"
    accepted_path = reports_dir / "system_forward_observation_accepted_v1.csv"
    rejected_path = reports_dir / "system_forward_observation_rejected_v1.csv"
    skipped_duplicates_path = reports_dir / "system_forward_observation_skipped_duplicates_v1.csv"
    errors_path = reports_dir / "system_forward_observation_errors_v1.csv"

    errors = []

    try:
        candidates = build_sample_system_forward_observation_candidates()

        records_df = build_system_forward_observation_records(candidates)
        builder_validation_df = validate_system_records_dataframe(records_df)

        save_system_records(records_df, system_records_path)

        if validation_dataset_path.exists():
            validation_dataset_path.unlink()

        phase_template_df = load_csv_or_fail(phase_template_path)

        config = ManualObservationProcessorConfig(
            duplicate_policy="SKIP",
            create_input_file_if_missing=True,
            min_forward_signals=100,
            preferred_forward_signals=300,
            max_candidate_theoretical_risk_pct=0.0050,
            max_watchlist_theoretical_risk_pct=0.0025,
            allow_resolution_from_intake=True,
        )

        (
            journal_df,
            accepted_df,
            rejected_df,
            skipped_df,
            validation_summary_df,
            journal_summary_df,
            errors_df,
            processor_summary_df,
        ) = process_manual_observation_file(
            input_path=system_records_path,
            phase_template_df=phase_template_df,
            dataset_path=validation_dataset_path,
            config=config,
        )

        if duplicate_dataset_path.exists():
            duplicate_dataset_path.unlink()

        first_duplicate_run = process_manual_observation_file(
            input_path=system_records_path,
            phase_template_df=phase_template_df,
            dataset_path=duplicate_dataset_path,
            config=config,
        )

        second_duplicate_run = process_manual_observation_file(
            input_path=system_records_path,
            phase_template_df=phase_template_df,
            dataset_path=duplicate_dataset_path,
            config=config,
        )

        duplicate_skipped_df = second_duplicate_run[3]

    except Exception as exc:
        errors.append(
            {
                "severity": "ERROR",
                "check_name": "workflow_error",
                "details": repr(exc),
            }
        )

        records_df = pd.DataFrame()
        builder_validation_df = pd.DataFrame()
        processor_summary_df = pd.DataFrame()
        validation_summary_df = pd.DataFrame()
        journal_summary_df = pd.DataFrame()
        accepted_df = pd.DataFrame()
        rejected_df = pd.DataFrame()
        duplicate_skipped_df = pd.DataFrame()
        errors_df = pd.DataFrame(errors)

    save_df(builder_validation_df, builder_validation_path)
    save_df(processor_summary_df, processor_summary_path)
    save_df(validation_summary_df, validation_summary_path)
    save_df(journal_summary_df, journal_summary_path)
    save_df(accepted_df, accepted_path)
    save_df(rejected_df, rejected_path)
    save_df(duplicate_skipped_df, skipped_duplicates_path)
    save_df(errors_df, errors_path)

    print_section("SYSTEM RECORDS")
    if records_df.empty:
        print("Sin registros generados.")
    else:
        print(
            records_df[
                [
                    "observed_at",
                    "symbol",
                    "timeframe",
                    "cost_profile",
                    "context_name",
                    "direction",
                    "entry_theoretical",
                    "stop_theoretical",
                    "target_theoretical",
                    "resolve_now",
                    "data_source",
                ]
            ].to_string(index=False)
        )

    print_section("BUILDER VALIDATION")
    if builder_validation_df.empty:
        print("Sin validacion.")
    else:
        print(builder_validation_df.to_string(index=False))

    print_section("PROCESSOR SUMMARY")
    if processor_summary_df.empty:
        print("Sin resumen.")
    else:
        print(processor_summary_df.to_string(index=False))

    print_section("VALIDATION SUMMARY")
    if validation_summary_df.empty:
        print("Sin validacion de journal.")
    else:
        print(validation_summary_df.to_string(index=False))

    print_section("JOURNAL SUMMARY")
    if journal_summary_df.empty:
        print("Sin resumen de journal.")
    else:
        print(journal_summary_df.to_string(index=False))

    print_section("ACCEPTED")
    if accepted_df.empty:
        print("Sin aceptadas.")
    else:
        print(
            accepted_df[
                [
                    "signal_id",
                    "observed_at",
                    "symbol",
                    "timeframe",
                    "cost_profile",
                    "context_name",
                    "direction",
                    "resolve_now",
                ]
            ].to_string(index=False)
        )

    print_section("REJECTED")
    if rejected_df.empty:
        print("Sin rechazadas.")
    else:
        print(rejected_df.to_string(index=False))

    print_section("DUPLICATE TEST SKIPPED")
    if duplicate_skipped_df.empty:
        print("Sin duplicados omitidos.")
    else:
        print(
            duplicate_skipped_df[
                [
                    "signal_id_preview",
                    "skip_reason",
                ]
            ].to_string(index=False)
        )

    print_section("ERRORS")
    if errors_df.empty:
        print("Sin errores.")
    else:
        print(errors_df.to_string(index=False))

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {system_records_path}")
    print(f"- {builder_validation_path}")
    print(f"- {processor_summary_path}")
    print(f"- {validation_summary_path}")
    print(f"- {journal_summary_path}")
    print(f"- {accepted_path}")
    print(f"- {rejected_path}")
    print(f"- {skipped_duplicates_path}")
    print(f"- {errors_path}")

    print()
    print("Restriccion: este flujo genera registros observacionales. No ejecuta operaciones.")


if __name__ == "__main__":
    main()