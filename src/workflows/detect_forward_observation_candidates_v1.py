from pathlib import Path

import pandas as pd

from src.journal.forward_observation_candidate_detector_v1 import (
    ForwardObservationCandidateDetectorConfig,
    build_candidate_detector_summary,
    build_sample_strategy_signal_candidates,
    detect_forward_observation_candidates,
)
from src.journal.manual_observation_processor_v1 import (
    ManualObservationProcessorConfig,
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
    print("FORWARD OBSERVATION CANDIDATE DETECTOR V1")
    print("=" * 100)
    print("Purpose: detect observable strategy candidates and convert them into forward observation records")
    print("Restriction: observational records only. No execution.")
    print()

    reports_dir = Path("reports") / "forward_observation_candidate_detector_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    phase_template_path = (
        Path("reports")
        / "forward_signal_journal_v1"
        / "forward_signal_journal_v1_template.csv"
    )

    source_signals_path = reports_dir / "candidate_detector_source_signals_v1.csv"
    system_records_path = reports_dir / "candidate_detector_system_records_v1.csv"
    detector_summary_path = reports_dir / "candidate_detector_summary_v1.csv"
    detector_validation_path = reports_dir / "candidate_detector_validation_v1.csv"
    detector_accepted_path = reports_dir / "candidate_detector_accepted_candidates_v1.csv"
    detector_rejected_path = reports_dir / "candidate_detector_rejected_candidates_v1.csv"

    validation_dataset_path = reports_dir / "candidate_detector_validation_dataset_v1.csv"
    duplicate_dataset_path = reports_dir / "candidate_detector_duplicate_validation_dataset_v1.csv"

    processor_summary_path = reports_dir / "candidate_detector_processor_summary_v1.csv"
    validation_summary_path = reports_dir / "candidate_detector_validation_summary_v1.csv"
    journal_summary_path = reports_dir / "candidate_detector_journal_summary_v1.csv"
    accepted_path = reports_dir / "candidate_detector_processor_accepted_v1.csv"
    rejected_path = reports_dir / "candidate_detector_processor_rejected_v1.csv"
    skipped_duplicates_path = reports_dir / "candidate_detector_skipped_duplicates_v1.csv"
    errors_path = reports_dir / "candidate_detector_errors_v1.csv"

    errors = []

    try:
        source_signals_df = build_sample_strategy_signal_candidates()
        save_df(source_signals_df, source_signals_path)

        detector_config = ForwardObservationCandidateDetectorConfig()

        (
            records_df,
            detector_accepted_df,
            detector_rejected_df,
            detector_validation_df,
        ) = detect_forward_observation_candidates(
            signals_df=source_signals_df,
            config=detector_config,
        )

        detector_summary_df = build_candidate_detector_summary(
            records_df=records_df,
            accepted_df=detector_accepted_df,
            rejected_df=detector_rejected_df,
            validation_df=detector_validation_df,
        )

        save_df(records_df, system_records_path)
        save_df(detector_summary_df, detector_summary_path)
        save_df(detector_validation_df, detector_validation_path)
        save_df(detector_accepted_df, detector_accepted_path)
        save_df(detector_rejected_df, detector_rejected_path)

        if validation_dataset_path.exists():
            validation_dataset_path.unlink()

        phase_template_df = load_csv_or_fail(phase_template_path)

        processor_config = ManualObservationProcessorConfig(
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
            processor_accepted_df,
            processor_rejected_df,
            skipped_df,
            validation_summary_df,
            journal_summary_df,
            errors_df,
            processor_summary_df,
        ) = process_manual_observation_file(
            input_path=system_records_path,
            phase_template_df=phase_template_df,
            dataset_path=validation_dataset_path,
            config=processor_config,
        )

        if duplicate_dataset_path.exists():
            duplicate_dataset_path.unlink()

        first_duplicate_run = process_manual_observation_file(
            input_path=system_records_path,
            phase_template_df=phase_template_df,
            dataset_path=duplicate_dataset_path,
            config=processor_config,
        )

        second_duplicate_run = process_manual_observation_file(
            input_path=system_records_path,
            phase_template_df=phase_template_df,
            dataset_path=duplicate_dataset_path,
            config=processor_config,
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

        source_signals_df = pd.DataFrame()
        records_df = pd.DataFrame()
        detector_summary_df = pd.DataFrame()
        detector_validation_df = pd.DataFrame()
        detector_accepted_df = pd.DataFrame()
        detector_rejected_df = pd.DataFrame()
        processor_summary_df = pd.DataFrame()
        validation_summary_df = pd.DataFrame()
        journal_summary_df = pd.DataFrame()
        processor_accepted_df = pd.DataFrame()
        processor_rejected_df = pd.DataFrame()
        duplicate_skipped_df = pd.DataFrame()
        errors_df = pd.DataFrame(errors)

    save_df(processor_summary_df, processor_summary_path)
    save_df(validation_summary_df, validation_summary_path)
    save_df(journal_summary_df, journal_summary_path)
    save_df(processor_accepted_df, accepted_path)
    save_df(processor_rejected_df, rejected_path)
    save_df(duplicate_skipped_df, skipped_duplicates_path)
    save_df(errors_df, errors_path)

    print_section("SOURCE SIGNALS")
    if source_signals_df.empty:
        print("Sin señales fuente.")
    else:
        print(
            source_signals_df[
                [
                    "observed_at",
                    "symbol",
                    "timeframe",
                    "signal_type",
                    "router_decision",
                    "context_name",
                    "direction",
                    "entry_price",
                    "stop_price",
                ]
            ].to_string(index=False)
        )

    print_section("DETECTOR SUMMARY")
    if detector_summary_df.empty:
        print("Sin resumen de detector.")
    else:
        print(detector_summary_df.to_string(index=False))

    print_section("DETECTOR VALIDATION")
    if detector_validation_df.empty:
        print("Sin validacion de detector.")
    else:
        print(detector_validation_df.to_string(index=False))

    print_section("DETECTOR ACCEPTED CANDIDATES")
    if detector_accepted_df.empty:
        print("Sin candidatos aceptados.")
    else:
        print(detector_accepted_df.to_string(index=False))

    print_section("DETECTOR REJECTED CANDIDATES")
    if detector_rejected_df.empty:
        print("Sin candidatos rechazados.")
    else:
        print(detector_rejected_df.to_string(index=False))

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

    print_section("PROCESSOR SUMMARY")
    if processor_summary_df.empty:
        print("Sin resumen de processor.")
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

    print_section("PROCESSOR ACCEPTED")
    if processor_accepted_df.empty:
        print("Sin aceptadas por processor.")
    else:
        print(
            processor_accepted_df[
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

    print_section("PROCESSOR REJECTED")
    if processor_rejected_df.empty:
        print("Sin rechazadas por processor.")
    else:
        print(processor_rejected_df.to_string(index=False))

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
    print(f"- {source_signals_path}")
    print(f"- {system_records_path}")
    print(f"- {detector_summary_path}")
    print(f"- {detector_validation_path}")
    print(f"- {detector_accepted_path}")
    print(f"- {detector_rejected_path}")
    print(f"- {processor_summary_path}")
    print(f"- {validation_summary_path}")
    print(f"- {journal_summary_path}")
    print(f"- {accepted_path}")
    print(f"- {rejected_path}")
    print(f"- {skipped_duplicates_path}")
    print(f"- {errors_path}")

    print()
    print("Restriccion: este flujo detecta candidatos observacionales. No ejecuta operaciones.")


if __name__ == "__main__":
    main()