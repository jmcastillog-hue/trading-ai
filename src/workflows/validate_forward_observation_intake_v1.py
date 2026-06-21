from pathlib import Path

import pandas as pd

from src.journal.forward_observation_intake_v1 import (
    ForwardObservationIntakeConfig,
    build_empty_intake_template,
    build_sample_intake_rows,
    process_forward_observation_intake,
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
    print("FORWARD OBSERVATION INTAKE / DATASET BUILDER V1")
    print("=" * 100)
    print("Input: Fase 2.8 template + synthetic intake rows")
    print("Purpose: build a persistent forward-observation dataset without execution")
    print()

    template_path = (
        Path("reports")
        / "forward_signal_journal_v1"
        / "forward_signal_journal_v1_template.csv"
    )

    reports_dir = Path("reports") / "forward_observation_intake_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    journal_path = reports_dir / "forward_observation_intake_v1_dataset.csv"
    intake_template_output = reports_dir / "forward_observation_intake_v1_empty_template.csv"
    sample_intake_output = reports_dir / "forward_observation_intake_v1_sample_input.csv"
    accepted_output = reports_dir / "forward_observation_intake_v1_accepted.csv"
    rejected_output = reports_dir / "forward_observation_intake_v1_rejected.csv"
    validation_summary_output = reports_dir / "forward_observation_intake_v1_validation_summary.csv"
    journal_summary_output = reports_dir / "forward_observation_intake_v1_journal_summary.csv"
    errors_output = reports_dir / "forward_observation_intake_v1_errors.csv"

    errors = []

    try:
        if journal_path.exists():
            journal_path.unlink()

        template_df = load_csv_or_fail(template_path)

        intake_template_df = build_empty_intake_template()
        sample_intake_df = build_sample_intake_rows()

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
            template_df=template_df,
            journal_path=journal_path,
            config=config,
        )

    except Exception as exc:
        errors.append({"severity": "ERROR", "check_name": "workflow_error", "details": repr(exc)})
        intake_template_df = pd.DataFrame()
        sample_intake_df = pd.DataFrame()
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
            [
                workflow_errors_df,
                processing_errors_df,
            ],
            ignore_index=True,
        )

    intake_template_df.to_csv(intake_template_output, index=False)
    sample_intake_df.to_csv(sample_intake_output, index=False)
    accepted_df.to_csv(accepted_output, index=False)
    rejected_df.to_csv(rejected_output, index=False)
    validation_summary_df.to_csv(validation_summary_output, index=False)
    journal_summary_df.to_csv(journal_summary_output, index=False)
    errors_df.to_csv(errors_output, index=False)

    print_section("FORWARD OBSERVATION INTAKE V1 VALIDATION SUMMARY")
    if validation_summary_df.empty:
        print("Sin resultados.")
    else:
        print(validation_summary_df.to_string(index=False))

    print_section("FORWARD OBSERVATION INTAKE V1 JOURNAL SUMMARY")
    if journal_summary_df.empty:
        print("Sin resultados.")
    else:
        print(journal_summary_df.to_string(index=False))

    print_section("FORWARD OBSERVATION INTAKE V1 ACCEPTED")
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
            "entry_theoretical",
            "stop_theoretical",
            "target_theoretical",
            "resolve_now",
        ]

        print(accepted_df[display_columns].to_string(index=False))

    print_section("FORWARD OBSERVATION INTAKE V1 REJECTED")
    if rejected_df.empty:
        print("Sin rechazadas.")
    else:
        print(rejected_df.to_string(index=False))

    print_section("FORWARD OBSERVATION INTAKE V1 ERRORS")
    if errors_df.empty:
        print("Sin errores.")
    else:
        print(errors_df.to_string(index=False))

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {journal_path}")
    print(f"- {intake_template_output}")
    print(f"- {sample_intake_output}")
    print(f"- {accepted_output}")
    print(f"- {rejected_output}")
    print(f"- {validation_summary_output}")
    print(f"- {journal_summary_output}")
    print(f"- {errors_output}")


if __name__ == "__main__":
    main()