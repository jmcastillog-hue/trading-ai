from pathlib import Path

import pandas as pd

from src.journal.forward_observation_candidate_detector_v1 import (
    ForwardObservationCandidateDetectorConfig,
    build_sample_strategy_signal_candidates,
    detect_forward_observation_candidates,
)
from src.journal.forward_observation_resolution_engine_v1 import (
    ForwardObservationResolutionConfig,
    build_sample_resolution_ohlc_data,
    resolve_forward_observations,
)


def print_section(title: str):
    print()
    print(title)
    print("=" * 100)


def save_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def main():
    print("FORWARD OBSERVATION RESOLUTION ENGINE V1")
    print("=" * 100)
    print("Purpose: resolve open forward observations against future OHLC data")
    print("Restriction: observational resolution only. No execution.")
    print()

    reports_dir = Path("reports") / "forward_observation_resolution_engine_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    source_signals_path = reports_dir / "resolution_source_signals_v1.csv"
    source_records_path = reports_dir / "resolution_source_records_v1.csv"
    ohlc_path = reports_dir / "resolution_sample_ohlc_v1.csv"
    resolved_all_path = reports_dir / "resolution_all_observations_v1.csv"
    resolved_closed_path = reports_dir / "resolution_closed_observations_v1.csv"
    open_path = reports_dir / "resolution_open_observations_v1.csv"
    errors_path = reports_dir / "resolution_errors_v1.csv"
    validation_path = reports_dir / "resolution_ohlc_validation_v1.csv"
    summary_path = reports_dir / "resolution_summary_v1.csv"

    workflow_errors = []

    try:
        source_signals_df = build_sample_strategy_signal_candidates()

        (
            source_records_df,
            detector_accepted_df,
            detector_rejected_df,
            detector_validation_df,
        ) = detect_forward_observation_candidates(
            signals_df=source_signals_df,
            config=ForwardObservationCandidateDetectorConfig(),
        )

        ohlc_df = build_sample_resolution_ohlc_data()

        resolution_config = ForwardObservationResolutionConfig(
            timestamp_column="timestamp",
            same_bar_policy="CONSERVATIVE_STOP",
            max_bars_after_observation=96,
            paper_trade_execution_allowed=False,
            real_capital_allowed=False,
        )

        (
            resolved_all_df,
            resolved_closed_df,
            open_df,
            errors_df,
            validation_df,
            summary_df,
        ) = resolve_forward_observations(
            observations_df=source_records_df,
            ohlc_df=ohlc_df,
            config=resolution_config,
        )

    except Exception as exc:
        workflow_errors.append(
            {
                "severity": "ERROR",
                "check_name": "workflow_error",
                "details": repr(exc),
            }
        )

        source_signals_df = pd.DataFrame()
        source_records_df = pd.DataFrame()
        ohlc_df = pd.DataFrame()
        resolved_all_df = pd.DataFrame()
        resolved_closed_df = pd.DataFrame()
        open_df = pd.DataFrame()
        errors_df = pd.DataFrame(workflow_errors)
        validation_df = pd.DataFrame()
        summary_df = pd.DataFrame()

    save_df(source_signals_df, source_signals_path)
    save_df(source_records_df, source_records_path)
    save_df(ohlc_df, ohlc_path)
    save_df(resolved_all_df, resolved_all_path)
    save_df(resolved_closed_df, resolved_closed_path)
    save_df(open_df, open_path)
    save_df(errors_df, errors_path)
    save_df(validation_df, validation_path)
    save_df(summary_df, summary_path)

    print_section("SOURCE RECORDS")
    if source_records_df.empty:
        print("Sin registros fuente.")
    else:
        print(
            source_records_df[
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
                ]
            ].to_string(index=False)
        )

    print_section("OHLC SAMPLE")
    if ohlc_df.empty:
        print("Sin datos OHLC.")
    else:
        print(ohlc_df.to_string(index=False))

    print_section("OHLC VALIDATION")
    if validation_df.empty:
        print("Sin validacion OHLC.")
    else:
        print(validation_df.to_string(index=False))

    print_section("RESOLUTION SUMMARY")
    if summary_df.empty:
        print("Sin resumen de resolucion.")
    else:
        print(summary_df.to_string(index=False))

    print_section("RESOLVED CLOSED OBSERVATIONS")
    if resolved_closed_df.empty:
        print("Sin observaciones cerradas.")
    else:
        print(
            resolved_closed_df[
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
                    "resolution_status",
                    "resolved_at",
                    "result_r",
                    "mfe_r",
                    "mae_r",
                    "bars_to_resolution",
                    "resolution_price",
                ]
            ].to_string(index=False)
        )

    print_section("OPEN OBSERVATIONS")
    if open_df.empty:
        print("Sin observaciones abiertas.")
    else:
        print(
            open_df[
                [
                    "observed_at",
                    "symbol",
                    "timeframe",
                    "context_name",
                    "direction",
                    "resolution_status",
                    "mfe_r",
                    "mae_r",
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
    print(f"- {source_records_path}")
    print(f"- {ohlc_path}")
    print(f"- {resolved_all_path}")
    print(f"- {resolved_closed_path}")
    print(f"- {open_path}")
    print(f"- {errors_path}")
    print(f"- {validation_path}")
    print(f"- {summary_path}")

    print()
    print("Restriccion: este motor resuelve observaciones teoricas. No ejecuta operaciones.")


if __name__ == "__main__":
    main()