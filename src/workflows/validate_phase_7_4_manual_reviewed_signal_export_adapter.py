from __future__ import annotations

import pandas as pd

from src.market_input.manual_reviewed_signal_export_adapter_v1 import (
    validate_manual_reviewed_signal_export_adapter,
)


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * 100)


def print_df(df: pd.DataFrame) -> None:
    if df.empty:
        print("Sin registros.")
        return

    print(df.to_string(index=False))


def main() -> None:
    print("PHASE 7.4 MANUAL REVIEWED SIGNAL EXPORT ADAPTER VALIDATOR")
    print("=" * 100)
    print("Purpose: validate manual reviewed watch-only signal export adapter")
    print("Restriction: signal normalization only. No price levels. No execution.")
    print()

    result = validate_manual_reviewed_signal_export_adapter()

    print_section("PHASE 7.4 VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("NORMALIZED SIGNAL OUTPUT PREVIEW")
    print_df(result["output"])

    print_section("VALIDATION CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/phase_7_4_manual_reviewed_signal_export_adapter_v1/manual_reviewed_signal_export_adapter_summary_v1.csv")
    print("- reports/phase_7_4_manual_reviewed_signal_export_adapter_v1/manual_reviewed_signal_export_adapter_output_preview_v1.csv")
    print("- reports/phase_7_4_manual_reviewed_signal_export_adapter_v1/manual_reviewed_signal_export_adapter_checks_v1.csv")
    print("- data/market_input/manual_reviewed_signal_export/input/phase_7_4_manual_reviewed_signal_source_v1.csv")
    print("- data/forward_evidence/operational/input/signals/phase_7_4_manual_reviewed_signal_input_v1.csv")
    print()
    print("Restriccion: este validador no genera niveles, evidencia completa ni ejecucion.")


if __name__ == "__main__":
    main()