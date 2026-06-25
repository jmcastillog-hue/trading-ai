from pathlib import Path

import pandas as pd

from src.journal.forward_evidence_accumulation_controller_v1 import (
    ForwardEvidenceAccumulationControllerConfig,
    run_forward_evidence_accumulation_controller,
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


def build_sample_price_level_overrides() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "signal_id": "",
                "context_name": "NORMAL_VALIDATION_CONTEXT",
                "cost_profile": "BINANCE_SCALP_BASE_ESTIMATE",
                "direction": "SHORT",
                "entry_price": 65000.0,
                "stop_price": 65500.0,
                "target_price": 63750.0,
                "price_level_source": "SAMPLE_PRICE_LEVEL_OVERRIDE_NORMAL_CONTEXT",
            },
            {
                "signal_id": "",
                "context_name": "WAVE_5_CAUTION_CONTEXT",
                "cost_profile": "QUANTFURY_SWING_BASE_ESTIMATE",
                "direction": "SHORT",
                "entry_price": 65200.0,
                "stop_price": 66000.0,
                "target_price": 63200.0,
                "price_level_source": "SAMPLE_PRICE_LEVEL_OVERRIDE_WAVE_5_CAUTION",
            },
        ]
    )


def main() -> None:
    print("FORWARD EVIDENCE ACCUMULATION CONTROLLER V1")
    print("=" * 100)
    print("Purpose: run accumulation cycle from candidate signals to resolved forward evidence")
    print("Restriction: evidence accumulation only. No execution.")
    print()

    reports_dir = Path("reports") / "forward_evidence_accumulation_controller_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    source_signals_path = reports_dir / "accumulation_source_signals_v1.csv"
    price_levels_path = reports_dir / "accumulation_price_level_overrides_v1.csv"
    sample_ohlc_path = reports_dir / "accumulation_sample_ohlc_v1.csv"

    controller_summary_path = reports_dir / "accumulation_controller_summary_v1.csv"
    controller_validation_path = reports_dir / "accumulation_controller_validation_v1.csv"

    runner_summary_path = reports_dir / "accumulation_runner_summary_v1.csv"
    runner_validation_path = reports_dir / "accumulation_runner_validation_v1.csv"

    resolver_summary_path = reports_dir / "accumulation_resolver_summary_v1.csv"
    resolver_validation_path = reports_dir / "accumulation_resolver_validation_v1.csv"

    generated_observations_path = reports_dir / "accumulation_generated_observations_v1.csv"
    detector_accepted_path = reports_dir / "accumulation_detector_accepted_v1.csv"
    detector_rejected_path = reports_dir / "accumulation_detector_rejected_v1.csv"
    accepted_new_path = reports_dir / "accumulation_accepted_new_v1.csv"
    duplicate_path = reports_dir / "accumulation_duplicates_v1.csv"
    priced_dataset_path = reports_dir / "accumulation_priced_dataset_v1.csv"
    resolved_closed_path = reports_dir / "accumulation_resolved_closed_v1.csv"
    still_open_path = reports_dir / "accumulation_still_open_v1.csv"
    dataset_after_resolution_path = reports_dir / "accumulation_dataset_after_resolution_v1.csv"

    workflow_errors = []

    try:
        source_signals_df = build_sample_strategy_signal_candidates()
        price_levels_df = build_sample_price_level_overrides()
        ohlc_df = build_sample_resolution_ohlc_data()
        existing_dataset_df = pd.DataFrame()

        (
            controller_summary_df,
            controller_validation_df,
            runner_summary_df,
            runner_validation_df,
            resolver_summary_df,
            resolver_validation_df,
            generated_observations_df,
            detector_accepted_df,
            detector_rejected_df,
            accepted_new_df,
            duplicate_df,
            priced_dataset_df,
            resolved_closed_df,
            still_open_df,
            dataset_after_resolution_df,
        ) = run_forward_evidence_accumulation_controller(
            source_signals_df=source_signals_df,
            existing_dataset_df=existing_dataset_df,
            ohlc_df=ohlc_df,
            price_levels_df=price_levels_df,
            config=ForwardEvidenceAccumulationControllerConfig(
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
                "check_name": "workflow_error",
                "passed": False,
                "severity": "ERROR",
                "details": repr(exc),
            }
        )

        source_signals_df = pd.DataFrame()
        price_levels_df = pd.DataFrame()
        ohlc_df = pd.DataFrame()

        controller_summary_df = pd.DataFrame()
        controller_validation_df = pd.DataFrame(workflow_errors)

        runner_summary_df = pd.DataFrame()
        runner_validation_df = pd.DataFrame()

        resolver_summary_df = pd.DataFrame()
        resolver_validation_df = pd.DataFrame()

        generated_observations_df = pd.DataFrame()
        detector_accepted_df = pd.DataFrame()
        detector_rejected_df = pd.DataFrame()
        accepted_new_df = pd.DataFrame()
        duplicate_df = pd.DataFrame()
        priced_dataset_df = pd.DataFrame()
        resolved_closed_df = pd.DataFrame()
        still_open_df = pd.DataFrame()
        dataset_after_resolution_df = pd.DataFrame()

    save_df(source_signals_df, source_signals_path)
    save_df(price_levels_df, price_levels_path)
    save_df(ohlc_df, sample_ohlc_path)

    save_df(controller_summary_df, controller_summary_path)
    save_df(controller_validation_df, controller_validation_path)

    save_df(runner_summary_df, runner_summary_path)
    save_df(runner_validation_df, runner_validation_path)

    save_df(resolver_summary_df, resolver_summary_path)
    save_df(resolver_validation_df, resolver_validation_path)

    save_df(generated_observations_df, generated_observations_path)
    save_df(detector_accepted_df, detector_accepted_path)
    save_df(detector_rejected_df, detector_rejected_path)
    save_df(accepted_new_df, accepted_new_path)
    save_df(duplicate_df, duplicate_path)
    save_df(priced_dataset_df, priced_dataset_path)
    save_df(resolved_closed_df, resolved_closed_path)
    save_df(still_open_df, still_open_path)
    save_df(dataset_after_resolution_df, dataset_after_resolution_path)

    print_section("ACCUMULATION CONTROLLER SUMMARY")
    print_selected(
        controller_summary_df,
        [
            "controller_validation_passed",
            "source_signal_rows",
            "detector_accepted_candidates",
            "detector_rejected_candidates",
            "generated_observations",
            "new_observations",
            "duplicate_observations",
            "resolution_input_observations",
            "closed_observations",
            "open_observations",
            "error_observations",
            "wins",
            "losses",
            "avg_result_r",
            "sum_result_r",
            "cumulative_closed_observations",
            "minimum_sample_reached",
            "preferred_sample_reached",
            "sample_gap_to_minimum",
            "sample_gap_to_preferred",
            "readiness_state",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "live_alerts_allowed",
            "exchange_execution_allowed",
            "automation_allowed",
            "controller_decision",
        ],
    )

    print_section("RUNNER SUMMARY")
    print_selected(
        runner_summary_df,
        [
            "validation_passed",
            "source_signal_rows",
            "detector_accepted_candidates",
            "detector_rejected_candidates",
            "generated_observations",
            "accepted_new_observations",
            "skipped_duplicate_observations",
            "dataset_rows_after",
            "batch_decision",
        ],
    )

    print_section("RESOLVER SUMMARY")
    print_selected(
        resolver_summary_df,
        [
            "validation_passed",
            "source_observations",
            "resolution_input_observations",
            "closed_observations",
            "open_observations",
            "error_observations",
            "wins",
            "losses",
            "avg_result_r",
            "sum_result_r",
            "dataset_rows_after_resolution",
            "batch_resolver_decision",
        ],
    )

    print_section("PRICE LEVEL OVERRIDES")
    print_selected(
        price_levels_df,
        [
            "context_name",
            "cost_profile",
            "direction",
            "entry_price",
            "stop_price",
            "target_price",
            "price_level_source",
        ],
    )

    print_section("PRICED DATASET BEFORE RESOLUTION")
    print_selected(
        priced_dataset_df,
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
            "price_level_source",
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

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {source_signals_path}")
    print(f"- {price_levels_path}")
    print(f"- {sample_ohlc_path}")
    print(f"- {controller_summary_path}")
    print(f"- {controller_validation_path}")
    print(f"- {runner_summary_path}")
    print(f"- {runner_validation_path}")
    print(f"- {resolver_summary_path}")
    print(f"- {resolver_validation_path}")
    print(f"- {generated_observations_path}")
    print(f"- {detector_accepted_path}")
    print(f"- {detector_rejected_path}")
    print(f"- {accepted_new_path}")
    print(f"- {duplicate_path}")
    print(f"- {priced_dataset_path}")
    print(f"- {resolved_closed_path}")
    print(f"- {still_open_path}")
    print(f"- {dataset_after_resolution_path}")

    print()
    print("Restriccion: este controlador acumula evidencia. No habilita ejecucion operativa.")


if __name__ == "__main__":
    main()