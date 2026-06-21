from pathlib import Path

import pandas as pd

from src.journal.forward_signal_journal_v1 import ForwardSignalJournalConfig
from src.journal.forward_signal_recorder_v1 import (
    ForwardObservedSignalInput,
    append_forward_observed_signal,
    load_journal_or_empty,
    resolve_forward_signal,
    save_journal,
    validate_recorded_journal,
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
    print("FORWARD SIGNAL RECORDER V1")
    print("=" * 100)
    print("Input: Fase 2.8 journal template")
    print("Purpose: append and validate forward-observed theoretical signals")
    print()

    template_path = (
        Path("reports")
        / "forward_signal_journal_v1"
        / "forward_signal_journal_v1_template.csv"
    )

    reports_dir = Path("reports") / "forward_signal_recorder_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    journal_path = reports_dir / "forward_signal_recorder_v1_journal.csv"
    validation_output = reports_dir / "forward_signal_recorder_v1_validation.csv"

    if journal_path.exists():
        journal_path.unlink()

    validation_summary_output = reports_dir / "forward_signal_recorder_v1_validation_summary.csv"
    summary_output = reports_dir / "forward_signal_recorder_v1_summary.csv"
    errors_output = reports_dir / "forward_signal_recorder_v1_errors.csv"

    errors = []

    try:
        template_df = load_csv_or_fail(template_path)

        journal_df = load_journal_or_empty(journal_path)

        sample_signal = ForwardObservedSignalInput(
            observed_at="2026-06-21 00:00:00",
            symbol="BTCUSDT",
            timeframe="15m",
            cost_profile="BINANCE_SCALP_BASE_ESTIMATE",
            context_name="NORMAL_VALIDATION_CONTEXT",
            direction="SHORT",
            entry_theoretical=65000.0,
            stop_theoretical=65500.0,
            target_theoretical=63750.0,
            invalidation_level=65500.0,
            invalidation_reason="Stop theoretical above invalidation zone.",
            manual_reviewer="manual_review_required",
            manual_notes=(
                "Synthetic validation row. This is not a real signal and not a trade."
            ),
            data_source="forward_signal_recorder_v1_validation",
            screenshot_path="",
        )

        journal_df = append_forward_observed_signal(
            journal_df=journal_df,
            template_df=template_df,
            signal_input=sample_signal,
        )

        last_signal_id = str(journal_df["signal_id"].iloc[-1])

        journal_df = resolve_forward_signal(
            journal_df=journal_df,
            signal_id=last_signal_id,
            observed_exit=63750.0,
            exit_reason="THEORETICAL_TARGET_REACHED_SYNTHETIC_VALIDATION",
            max_favorable_excursion_r=2.5,
            max_adverse_excursion_r=-0.25,
            bars_to_resolution=24,
        )

        config = ForwardSignalJournalConfig(
            min_forward_signals=100,
            preferred_forward_signals=300,
            max_candidate_theoretical_risk_pct=0.0050,
            max_watchlist_theoretical_risk_pct=0.0025,
        )

        validation_df, validation_summary_df, summary_df = validate_recorded_journal(
            journal_df=journal_df,
            config=config,
        )

        save_journal(journal_df, journal_path)

    except Exception as exc:
        errors.append({"error": repr(exc)})
        journal_df = pd.DataFrame()
        validation_df = pd.DataFrame()
        validation_summary_df = pd.DataFrame()
        summary_df = pd.DataFrame()

    errors_df = pd.DataFrame(errors)

    validation_df.to_csv(validation_output, index=False)
    validation_summary_df.to_csv(validation_summary_output, index=False)
    summary_df.to_csv(summary_output, index=False)
    errors_df.to_csv(errors_output, index=False)

    print_section("FORWARD SIGNAL RECORDER V1 VALIDATION SUMMARY")
    if validation_summary_df.empty:
        print("Sin resultados.")
    else:
        print(validation_summary_df.to_string(index=False))

    print_section("FORWARD SIGNAL RECORDER V1 JOURNAL SUMMARY")
    if summary_df.empty:
        print("Sin resultados.")
    else:
        print(summary_df.to_string(index=False))

    print_section("FORWARD SIGNAL RECORDER V1 JOURNAL TAIL")
    if journal_df.empty:
        print("Sin journal.")
    else:
        display_columns = [
            "signal_id",
            "symbol",
            "timeframe",
            "cost_profile",
            "context_name",
            "signal_state",
            "entry_theoretical",
            "stop_theoretical",
            "target_theoretical",
            "theoretical_risk_pct",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "observation_status",
            "result_r",
        ]

        print(journal_df[display_columns].tail(10).to_string(index=False))

    print_section("FORWARD SIGNAL RECORDER V1 ERRORS")
    if errors_df.empty:
        print("Sin errores.")
    else:
        print(errors_df.to_string(index=False))

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {journal_path}")
    print(f"- {validation_output}")
    print(f"- {validation_summary_output}")
    print(f"- {summary_output}")
    print(f"- {errors_output}")


if __name__ == "__main__":
    main()