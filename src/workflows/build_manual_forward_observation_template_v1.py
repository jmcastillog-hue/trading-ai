from pathlib import Path

import pandas as pd

from src.journal.forward_observation_intake_v1 import (
    ForwardObservationIntakeConfig,
    process_forward_observation_intake,
)
from src.journal.manual_forward_observation_template_v1 import (
    save_manual_forward_observation_bundle,
    validate_manual_forward_observation_bundle,
)


def print_section(title: str):
    print()
    print(title)
    print("=" * 100)


def load_csv_or_fail(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")

    return pd.read_csv(path)


def main():
    print("MANUAL FORWARD OBSERVATION CSV TEMPLATE V1")
    print("=" * 100)
    print("Purpose: generate a manual CSV template for prospective observation only")
    print()

    template_output_dir = Path("templates") / "forward_observation"
    reports_dir = Path("reports") / "manual_forward_observation_template_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    validation_report_path = reports_dir / "manual_forward_observation_template_v1_validation.csv"
    intake_validation_dataset_path = reports_dir / "manual_forward_observation_template_v1_dataset.csv"
    intake_accepted_path = reports_dir / "manual_forward_observation_template_v1_accepted.csv"
    intake_rejected_path = reports_dir / "manual_forward_observation_template_v1_rejected.csv"
    intake_validation_summary_path = reports_dir / "manual_forward_observation_template_v1_validation_summary.csv"
    intake_journal_summary_path = reports_dir / "manual_forward_observation_template_v1_journal_summary.csv"
    intake_errors_path = reports_dir / "manual_forward_observation_template_v1_errors.csv"

    errors = []

    try:
        generated_paths = save_manual_forward_observation_bundle(template_output_dir)

        validation_df = validate_manual_forward_observation_bundle(template_output_dir)

        phase_2_8_template_path = (
            Path("reports")
            / "forward_signal_journal_v1"
            / "forward_signal_journal_v1_template.csv"
        )

        phase_2_8_template_df = load_csv_or_fail(phase_2_8_template_path)

        sample_intake_df = load_csv_or_fail(generated_paths["sample_path"])

        if intake_validation_dataset_path.exists():
            intake_validation_dataset_path.unlink()

        config = ForwardObservationIntakeConfig(
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
            validation_summary_df,
            journal_summary_df,
            processing_errors_df,
        ) = process_forward_observation_intake(
            intake_df=sample_intake_df,
            template_df=phase_2_8_template_df,
            journal_path=intake_validation_dataset_path,
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
        generated_paths = {}
        validation_df = pd.DataFrame()
        journal_df = pd.DataFrame()
        accepted_df = pd.DataFrame()
        rejected_df = pd.DataFrame()
        validation_summary_df = pd.DataFrame()
        journal_summary_df = pd.DataFrame()
        processing_errors_df = pd.DataFrame()

    workflow_errors_df = pd.DataFrame(errors)

    if workflow_errors_df.empty:
        errors_df = processing_errors_df
    elif processing_errors_df.empty:
        errors_df = workflow_errors_df
    else:
        errors_df = pd.concat(
            [workflow_errors_df, processing_errors_df],
            ignore_index=True,
        )

    validation_df.to_csv(validation_report_path, index=False)
    accepted_df.to_csv(intake_accepted_path, index=False)
    rejected_df.to_csv(intake_rejected_path, index=False)
    validation_summary_df.to_csv(intake_validation_summary_path, index=False)
    journal_summary_df.to_csv(intake_journal_summary_path, index=False)
    errors_df.to_csv(intake_errors_path, index=False)

    print_section("MANUAL FORWARD OBSERVATION TEMPLATE FILES")
    if not generated_paths:
        print("Sin archivos generados.")
    else:
        for name, path in generated_paths.items():
            print(f"{name}: {path}")

    print_section("MANUAL FORWARD OBSERVATION TEMPLATE VALIDATION")
    if validation_df.empty:
        print("Sin resultados.")
    else:
        print(validation_df.to_string(index=False))

    print_section("MANUAL FORWARD OBSERVATION SAMPLE INTAKE SUMMARY")
    if validation_summary_df.empty:
        print("Sin resultados.")
    else:
        print(validation_summary_df.to_string(index=False))

    print_section("MANUAL FORWARD OBSERVATION JOURNAL SUMMARY")
    if journal_summary_df.empty:
        print("Sin resultados.")
    else:
        print(journal_summary_df.to_string(index=False))

    print_section("MANUAL FORWARD OBSERVATION ACCEPTED")
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

    print_section("MANUAL FORWARD OBSERVATION REJECTED")
    if rejected_df.empty:
        print("Sin rechazadas.")
    else:
        print(rejected_df.to_string(index=False))

    print_section("MANUAL FORWARD OBSERVATION ERRORS")
    if errors_df.empty:
        print("Sin errores.")
    else:
        print(errors_df.to_string(index=False))

    print()
    print("ARCHIVOS DE REPORTE")
    print("=" * 100)
    print(f"- {validation_report_path}")
    print(f"- {intake_validation_dataset_path}")
    print(f"- {intake_accepted_path}")
    print(f"- {intake_rejected_path}")
    print(f"- {intake_validation_summary_path}")
    print(f"- {intake_journal_summary_path}")
    print(f"- {intake_errors_path}")


if __name__ == "__main__":
    main()