from pathlib import Path

import pandas as pd

from src.journal.forward_signal_journal_v1 import (
    ForwardSignalJournalConfig,
    build_empty_forward_signal_journal,
    build_forward_signal_journal_specification,
    build_forward_signal_template_from_plan,
    summarize_forward_signal_journal,
    validate_forward_signal_journal,
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
    print("FORWARD SIGNAL JOURNAL V1")
    print("=" * 100)
    print("Input: Fase 2.7 forward observation plan")
    print("Purpose: create forward signal journal structure and validation")
    print()

    forward_plan_path = (
        Path("reports")
        / "forward_observation_engine_v1"
        / "forward_observation_v1_plan.csv"
    )

    reports_dir = Path("reports") / "forward_signal_journal_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    errors = []

    try:
        plan_df = load_csv_or_fail(forward_plan_path)

        config = ForwardSignalJournalConfig(
            min_forward_signals=100,
            preferred_forward_signals=300,
            max_candidate_theoretical_risk_pct=0.0050,
            max_watchlist_theoretical_risk_pct=0.0025,
        )

        empty_journal_df = build_empty_forward_signal_journal()

        template_df = build_forward_signal_template_from_plan(
            plan_df=plan_df,
            symbol="BTCUSDT",
            timeframe="15m",
        )

        validation_df, validation_summary = validate_forward_signal_journal(
            journal_df=template_df,
            config=config,
        )

        journal_summary_df = summarize_forward_signal_journal(template_df)
        validation_summary_df = pd.DataFrame([validation_summary])

        specification_lines = build_forward_signal_journal_specification(
            output_dir=reports_dir,
        )

    except Exception as exc:
        errors.append({"error": repr(exc)})
        empty_journal_df = pd.DataFrame()
        template_df = pd.DataFrame()
        validation_df = pd.DataFrame()
        validation_summary_df = pd.DataFrame()
        journal_summary_df = pd.DataFrame()
        specification_lines = [
            "# Forward Signal Journal V1",
            "",
            "NOT READY",
            "",
            repr(exc),
        ]

    errors_df = pd.DataFrame(errors)

    empty_output = reports_dir / "forward_signal_journal_v1_empty.csv"
    template_output = reports_dir / "forward_signal_journal_v1_template.csv"
    validation_output = reports_dir / "forward_signal_journal_v1_validation.csv"
    validation_summary_output = reports_dir / "forward_signal_journal_v1_validation_summary.csv"
    summary_output = reports_dir / "forward_signal_journal_v1_summary.csv"
    specification_output = reports_dir / "forward_signal_journal_v1_specification.md"
    errors_output = reports_dir / "forward_signal_journal_v1_errors.csv"

    empty_journal_df.to_csv(empty_output, index=False)
    template_df.to_csv(template_output, index=False)
    validation_df.to_csv(validation_output, index=False)
    validation_summary_df.to_csv(validation_summary_output, index=False)
    journal_summary_df.to_csv(summary_output, index=False)
    errors_df.to_csv(errors_output, index=False)

    specification_output.write_text(
        "\n".join(specification_lines),
        encoding="utf-8",
    )

    print_section("FORWARD SIGNAL JOURNAL V1 VALIDATION SUMMARY")
    if validation_summary_df.empty:
        print("Sin resultados.")
    else:
        print(validation_summary_df.to_string(index=False))

    print_section("FORWARD SIGNAL JOURNAL V1 JOURNAL SUMMARY")
    if journal_summary_df.empty:
        print("Sin resultados.")
    else:
        print(journal_summary_df.to_string(index=False))

    print_section("FORWARD SIGNAL JOURNAL V1 TEMPLATE")
    if template_df.empty:
        print("Sin template.")
    else:
        display_columns = [
            "signal_id",
            "symbol",
            "timeframe",
            "cost_profile",
            "readiness_decision",
            "context_name",
            "observation_permission",
            "theoretical_risk_pct",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "forward_observation_allowed",
            "observation_status",
        ]

        print(template_df[display_columns].to_string(index=False))

    print_section("FORWARD SIGNAL JOURNAL V1 ERRORS")
    if errors_df.empty:
        print("Sin errores.")
    else:
        print(errors_df.to_string(index=False))

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {empty_output}")
    print(f"- {template_output}")
    print(f"- {validation_output}")
    print(f"- {validation_summary_output}")
    print(f"- {summary_output}")
    print(f"- {specification_output}")
    print(f"- {errors_output}")


if __name__ == "__main__":
    main()