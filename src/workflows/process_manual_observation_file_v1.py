from pathlib import Path

import pandas as pd

from src.journal.manual_observation_processor_v1 import (
    ManualObservationProcessorConfig,
    ensure_manual_observation_input_file,
    load_csv_or_fail,
    process_manual_observation_file,
)


def print_section(title: str):
    print()
    print(title)
    print("=" * 100)


def save_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def main():
    print("MANUAL OBSERVATION PROCESSOR V1")
    print("=" * 100)
    print("Purpose: process manual forward-observation CSV files without execution")
    print()

    manual_template_path = (
        Path("templates")
        / "forward_observation"
        / "manual_forward_observation_template_v1.csv"
    )

    sample_input_path = (
        Path("templates")
        / "forward_observation"
        / "manual_forward_observation_sample_v1.csv"
    )

    phase_template_path = (
        Path("reports")
        / "forward_signal_journal_v1"
        / "forward_signal_journal_v1_template.csv"
    )

    production_input_path = (
        Path("data")
        / "forward_observation"
        / "manual_observations_v1.csv"
    )

    production_dataset_path = (
        Path("data")
        / "forward_observation"
        / "forward_observation_dataset_v1.csv"
    )

    reports_dir = Path("reports") / "manual_observation_processor_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    validation_dataset_path = reports_dir / "manual_observation_processor_v1_validation_dataset.csv"
    processor_summary_path = reports_dir / "manual_observation_processor_v1_processor_summary.csv"
    validation_summary_path = reports_dir / "manual_observation_processor_v1_validation_summary.csv"
    journal_summary_path = reports_dir / "manual_observation_processor_v1_journal_summary.csv"
    accepted_path = reports_dir / "manual_observation_processor_v1_accepted.csv"
    rejected_path = reports_dir / "manual_observation_processor_v1_rejected.csv"
    skipped_path = reports_dir / "manual_observation_processor_v1_skipped_duplicates.csv"
    errors_path = reports_dir / "manual_observation_processor_v1_errors.csv"
    input_status_path = reports_dir / "manual_observation_processor_v1_input_status.csv"

    errors = []

    config = ManualObservationProcessorConfig(
        duplicate_policy="SKIP",
        create_input_file_if_missing=True,
        min_forward_signals=100,
        preferred_forward_signals=300,
        max_candidate_theoretical_risk_pct=0.0050,
        max_watchlist_theoretical_risk_pct=0.0025,
        allow_resolution_from_intake=True,
    )

    try:
        input_status = ensure_manual_observation_input_file(
            input_path=production_input_path,
            template_path=manual_template_path,
            config=config,
        )

        input_status["production_dataset_path"] = str(production_dataset_path)

        input_status_df = pd.DataFrame([input_status])

        if validation_dataset_path.exists():
            validation_dataset_path.unlink()

        phase_template_df = load_csv_or_fail(phase_template_path)

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
            input_path=sample_input_path,
            phase_template_df=phase_template_df,
            dataset_path=validation_dataset_path,
            config=config,
        )

    except Exception as exc:
        errors.append(
            {
                "severity": "ERROR",
                "check_name": "workflow_error",
                "details": repr(exc),
            }
        )

        input_status_df = pd.DataFrame()
        journal_df = pd.DataFrame()
        accepted_df = pd.DataFrame()
        rejected_df = pd.DataFrame()
        skipped_df = pd.DataFrame()
        validation_summary_df = pd.DataFrame()
        journal_summary_df = pd.DataFrame()
        processor_summary_df = pd.DataFrame()
        errors_df = pd.DataFrame(errors)

    save_df(input_status_df, input_status_path)
    save_df(processor_summary_df, processor_summary_path)
    save_df(validation_summary_df, validation_summary_path)
    save_df(journal_summary_df, journal_summary_path)
    save_df(accepted_df, accepted_path)
    save_df(rejected_df, rejected_path)
    save_df(skipped_df, skipped_path)
    save_df(errors_df, errors_path)

    print_section("MANUAL OBSERVATION PROCESSOR INPUT STATUS")
    if input_status_df.empty:
        print("Sin estado de input.")
    else:
        print(input_status_df.to_string(index=False))

    print_section("MANUAL OBSERVATION PROCESSOR SUMMARY")
    if processor_summary_df.empty:
        print("Sin resumen.")
    else:
        print(processor_summary_df.to_string(index=False))

    print_section("MANUAL OBSERVATION PROCESSOR VALIDATION SUMMARY")
    if validation_summary_df.empty:
        print("Sin resultados.")
    else:
        print(validation_summary_df.to_string(index=False))

    print_section("MANUAL OBSERVATION PROCESSOR JOURNAL SUMMARY")
    if journal_summary_df.empty:
        print("Sin resultados.")
    else:
        print(journal_summary_df.to_string(index=False))

    print_section("MANUAL OBSERVATION PROCESSOR ACCEPTED")
    if accepted_df.empty:
        print("Sin aceptadas.")
    else:
        display_columns = [
            "signal_id",
            "observed_at",
            "symbol",
            "timeframe",
            "cost_profile",
            "context_name",
            "direction",
            "resolve_now",
        ]

        print(accepted_df[display_columns].to_string(index=False))

    print_section("MANUAL OBSERVATION PROCESSOR REJECTED")
    if rejected_df.empty:
        print("Sin rechazadas.")
    else:
        print(rejected_df.to_string(index=False))

    print_section("MANUAL OBSERVATION PROCESSOR SKIPPED DUPLICATES")
    if skipped_df.empty:
        print("Sin duplicados omitidos.")
    else:
        print(skipped_df.to_string(index=False))

    print_section("MANUAL OBSERVATION PROCESSOR ERRORS")
    if errors_df.empty:
        print("Sin errores.")
    else:
        print(errors_df.to_string(index=False))

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {validation_dataset_path}")
    print(f"- {input_status_path}")
    print(f"- {processor_summary_path}")
    print(f"- {validation_summary_path}")
    print(f"- {journal_summary_path}")
    print(f"- {accepted_path}")
    print(f"- {rejected_path}")
    print(f"- {skipped_path}")
    print(f"- {errors_path}")

    print()
    print("ARCHIVO MANUAL DE TRABAJO")
    print("=" * 100)
    print(f"- {production_input_path}")
    print()
    print("Restriccion: este flujo sigue siendo solo observacional. No ejecuta operaciones.")


if __name__ == "__main__":
    main()