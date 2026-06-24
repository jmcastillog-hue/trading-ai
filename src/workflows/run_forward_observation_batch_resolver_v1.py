from pathlib import Path

import pandas as pd

from src.journal.forward_observation_batch_resolver_v1 import (
    ForwardObservationBatchResolverConfig,
    run_forward_observation_batch_resolver,
)
from src.journal.forward_observation_batch_runner_v1 import (
    ForwardObservationBatchRunnerConfig,
    run_forward_observation_batch_runner,
)
from src.journal.forward_observation_candidate_detector_v1 import (
    build_sample_strategy_signal_candidates,
)
from src.journal.forward_observation_resolution_engine_v1 import (
    build_sample_resolution_ohlc_data,
)


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * 100)


def save_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def print_selected(df: pd.DataFrame, columns: list[str]) -> None:
    if df.empty:
        print("Sin registros.")
        return

    existing_columns = [column for column in columns if column in df.columns]

    if not existing_columns:
        print(df.to_string(index=False))
        return

    print(df[existing_columns].to_string(index=False))


def enrich_sample_price_levels(observations_df: pd.DataFrame) -> pd.DataFrame:
    df = observations_df.copy()

    if df.empty:
        return df

    for column in ["entry_price", "stop_price", "target_price"]:
        if column not in df.columns:
            df[column] = 0.0

        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0.0)

    for idx, row in df.iterrows():
        context_name = str(row.get("context_name", "")).upper()
        cost_profile = str(row.get("cost_profile", "")).upper()

        if (
            "NORMAL_VALIDATION_CONTEXT" in context_name
            or "BINANCE_SCALP_BASE_ESTIMATE" in cost_profile
        ):
            df.at[idx, "entry_price"] = 65000.0
            df.at[idx, "stop_price"] = 65500.0
            df.at[idx, "target_price"] = 63750.0
            continue

        if (
            "WAVE_5_CAUTION_CONTEXT" in context_name
            or "QUANTFURY_SWING_BASE_ESTIMATE" in cost_profile
        ):
            df.at[idx, "entry_price"] = 65200.0
            df.at[idx, "stop_price"] = 66000.0
            df.at[idx, "target_price"] = 63200.0
            continue

    return df


def main() -> None:
    print("FORWARD OBSERVATION BATCH RESOLVER V1")
    print("=" * 100)
    print("Purpose: resolve open forward observations against future OHLC data")
    print("Restriction: resolution only. No execution.")
    print()

    reports_dir = Path("reports") / "forward_observation_batch_resolver_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    source_signals_path = reports_dir / "batch_resolver_source_signals_v1.csv"
    runner_summary_path = reports_dir / "batch_resolver_runner_summary_v1.csv"
    open_dataset_path = reports_dir / "batch_resolver_open_dataset_v1.csv"
    priced_open_dataset_path = reports_dir / "batch_resolver_priced_open_dataset_v1.csv"
    ohlc_path = reports_dir / "batch_resolver_sample_ohlc_v1.csv"

    resolver_summary_path = reports_dir / "batch_resolver_summary_v1.csv"
    resolver_validation_path = reports_dir / "batch_resolver_validation_v1.csv"
    source_observations_path = reports_dir / "batch_resolver_source_observations_v1.csv"
    resolution_input_path = reports_dir / "batch_resolver_resolution_input_v1.csv"
    invalid_price_path = reports_dir / "batch_resolver_invalid_price_rows_v1.csv"
    resolved_all_path = reports_dir / "batch_resolver_resolved_all_v1.csv"
    resolved_closed_path = reports_dir / "batch_resolver_resolved_closed_v1.csv"
    still_open_path = reports_dir / "batch_resolver_still_open_v1.csv"
    resolution_errors_path = reports_dir / "batch_resolver_resolution_errors_v1.csv"
    dataset_after_resolution_path = reports_dir / "batch_resolver_dataset_after_resolution_v1.csv"

    workflow_errors = []

    try:
        source_signals_df = build_sample_strategy_signal_candidates()

        (
            runner_summary_df,
            runner_validation_df,
            generated_observations_df,
            detector_accepted_df,
            detector_rejected_df,
            accepted_new_df,
            duplicate_df,
            open_dataset_df,
        ) = run_forward_observation_batch_runner(
            source_signals_df=source_signals_df,
            existing_dataset_df=pd.DataFrame(),
            config=ForwardObservationBatchRunnerConfig(
                min_forward_observations=100,
                preferred_forward_observations=300,
                paper_trade_execution_allowed=False,
                real_capital_allowed=False,
                live_alerts_allowed=False,
                exchange_execution_allowed=False,
                automation_allowed=False,
            ),
        )

        priced_open_dataset_df = enrich_sample_price_levels(open_dataset_df)
        ohlc_df = build_sample_resolution_ohlc_data()

        (
            resolver_summary_df,
            resolver_validation_df,
            source_observations_df,
            resolution_input_df,
            invalid_price_df,
            resolved_all_df,
            resolved_closed_df,
            still_open_df,
            resolution_errors_df,
            dataset_after_resolution_df,
        ) = run_forward_observation_batch_resolver(
            observations_df=priced_open_dataset_df,
            ohlc_df=ohlc_df,
            config=ForwardObservationBatchResolverConfig(
                min_forward_observations=100,
                preferred_forward_observations=300,
                timestamp_column="timestamp",
                same_bar_policy="CONSERVATIVE_STOP",
                max_bars_after_observation=96,
                paper_trade_execution_allowed=False,
                real_capital_allowed=False,
                live_alerts_allowed=False,
                exchange_execution_allowed=False,
                automation_allowed=False,
            ),
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
        runner_summary_df = pd.DataFrame()
        open_dataset_df = pd.DataFrame()
        priced_open_dataset_df = pd.DataFrame()
        ohlc_df = pd.DataFrame()

        resolver_summary_df = pd.DataFrame()
        resolver_validation_df = pd.DataFrame(workflow_errors)
        source_observations_df = pd.DataFrame()
        resolution_input_df = pd.DataFrame()
        invalid_price_df = pd.DataFrame()
        resolved_all_df = pd.DataFrame()
        resolved_closed_df = pd.DataFrame()
        still_open_df = pd.DataFrame()
        resolution_errors_df = pd.DataFrame()
        dataset_after_resolution_df = pd.DataFrame()

    save_df(source_signals_df, source_signals_path)
    save_df(runner_summary_df, runner_summary_path)
    save_df(open_dataset_df, open_dataset_path)
    save_df(priced_open_dataset_df, priced_open_dataset_path)
    save_df(ohlc_df, ohlc_path)

    save_df(resolver_summary_df, resolver_summary_path)
    save_df(resolver_validation_df, resolver_validation_path)
    save_df(source_observations_df, source_observations_path)
    save_df(resolution_input_df, resolution_input_path)
    save_df(invalid_price_df, invalid_price_path)
    save_df(resolved_all_df, resolved_all_path)
    save_df(resolved_closed_df, resolved_closed_path)
    save_df(still_open_df, still_open_path)
    save_df(resolution_errors_df, resolution_errors_path)
    save_df(dataset_after_resolution_df, dataset_after_resolution_path)

    print_section("RUNNER SUMMARY")
    print_selected(
        runner_summary_df,
        [
            "validation_passed",
            "source_signal_rows",
            "detector_accepted_candidates",
            "detector_rejected_candidates",
            "accepted_new_observations",
            "dataset_rows_after",
            "batch_decision",
        ],
    )

    print_section("BATCH RESOLVER SUMMARY")
    print_selected(
        resolver_summary_df,
        [
            "validation_passed",
            "source_observations",
            "resolution_input_observations",
            "invalid_price_observations",
            "already_resolved_or_other_observations",
            "resolved_all_observations",
            "closed_observations",
            "open_observations",
            "error_observations",
            "wins",
            "losses",
            "avg_result_r",
            "sum_result_r",
            "dataset_rows_after_resolution",
            "minimum_sample_reached",
            "preferred_sample_reached",
            "sample_gap_to_minimum",
            "sample_gap_to_preferred",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "live_alerts_allowed",
            "exchange_execution_allowed",
            "automation_allowed",
            "batch_resolver_decision",
        ],
    )

    print_section("RESOLUTION INPUT")
    print_selected(
        resolution_input_df,
        [
            "signal_id",
            "observed_at",
            "symbol",
            "timeframe",
            "cost_profile",
            "context_name",
            "direction",
            "entry_price",
            "stop_price",
            "target_price",
            "resolution_status",
        ],
    )

    print_section("RESOLVED CLOSED OBSERVATIONS")
    print_selected(
        resolved_closed_df,
        [
            "signal_id",
            "observed_at",
            "symbol",
            "timeframe",
            "cost_profile",
            "context_name",
            "direction",
            "resolution_status",
            "result_r",
            "mfe_r",
            "mae_r",
            "bars_to_resolution",
            "batch_resolution_status",
        ],
    )

    print_section("STILL OPEN OBSERVATIONS")
    print_selected(
        still_open_df,
        [
            "signal_id",
            "observed_at",
            "symbol",
            "timeframe",
            "context_name",
            "direction",
            "resolution_status",
        ],
    )

    print_section("RESOLUTION ERRORS")
    print_selected(
        resolution_errors_df,
        [
            "signal_id",
            "observed_at",
            "symbol",
            "timeframe",
            "context_name",
            "direction",
            "resolution_status",
        ],
    )

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {source_signals_path}")
    print(f"- {runner_summary_path}")
    print(f"- {open_dataset_path}")
    print(f"- {priced_open_dataset_path}")
    print(f"- {ohlc_path}")
    print(f"- {resolver_summary_path}")
    print(f"- {resolver_validation_path}")
    print(f"- {source_observations_path}")
    print(f"- {resolution_input_path}")
    print(f"- {invalid_price_path}")
    print(f"- {resolved_all_path}")
    print(f"- {resolved_closed_path}")
    print(f"- {still_open_path}")
    print(f"- {resolution_errors_path}")
    print(f"- {dataset_after_resolution_path}")

    print()
    print("Restriccion: este batch resolver resuelve observaciones. No habilita ejecucion operativa.")


if __name__ == "__main__":
    main()