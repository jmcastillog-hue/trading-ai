from pathlib import Path

import pandas as pd

from src.risk.position_sizing_engine_v1 import (
    PositionSizingConfig,
    build_position_sizing_scenarios,
    run_position_sizing_for_profile,
    select_recommended_size,
    summarize_position_sizing_profiles,
)


def print_section(title: str):
    print()
    print(title)
    print("=" * 100)


def load_cost_adjusted_trades() -> pd.DataFrame:
    path = Path("reports") / "cost_aware_filter_v1" / "cost_aware_v1_adjusted_trades.csv"

    if not path.exists():
        raise FileNotFoundError(
            f"Missing cost-aware adjusted trades file: {path}. "
            "Run Fase 2.2 workflow first: "
            "python -m src.workflows.validate_cost_aware_filter_v1"
        )

    return pd.read_csv(path)


def main():
    print("POSITION SIZING / SEQUENCE RISK CONTROL V1")
    print("=" * 100)
    print("Input: cost-aware adjusted trades from Fase 2.2")
    print("Purpose: evaluate risk per trade scenarios under sequence risk")
    print()

    trades_df = load_cost_adjusted_trades()

    profiles = sorted(trades_df["cost_profile"].dropna().unique().tolist())
    scenarios = build_position_sizing_scenarios()

    config = PositionSizingConfig(
        simulations=10000,
        random_seed=42,
        min_trades=30,
        initial_equity=1.0,
        sample_with_replacement=True,
    )

    all_simulations = []
    summary_rows = []
    errors = []

    for profile_name in profiles:
        print_section(f"POSITION SIZING PROFILE: {profile_name}")

        for scenario in scenarios:
            try:
                simulations_df, summary = run_position_sizing_for_profile(
                    trades_df=trades_df,
                    cost_profile=profile_name,
                    scenario=scenario,
                    config=config,
                )

                summary_rows.append(summary)

                if not simulations_df.empty:
                    all_simulations.append(simulations_df)

                print(
                    f"{scenario.scenario_name} | "
                    f"risk={scenario.risk_per_trade_pct:.2%} | "
                    f"raw={summary.get('raw_sequence_return', 0.0):.2%} | "
                    f"p05={summary.get('p05_return', 0.0):.2%} | "
                    f"p01_dd={summary.get('p01_max_drawdown', 0.0):.2%} | "
                    f"p99_ls={summary.get('p99_losing_streak', 0.0)} | "
                    f"neg_prob={summary.get('probability_negative_return', 0.0):.2%} | "
                    f"decision={summary.get('decision')}"
                )

            except Exception as exc:
                error_row = {
                    "cost_profile": profile_name,
                    "scenario_name": scenario.scenario_name,
                    "error": repr(exc),
                }

                errors.append(error_row)
                print(error_row)

    if summary_rows:
        summary_df = pd.DataFrame(summary_rows)
    else:
        summary_df = pd.DataFrame()

    if all_simulations:
        simulations_all_df = pd.concat(all_simulations, ignore_index=True)
    else:
        simulations_all_df = pd.DataFrame()

    errors_df = pd.DataFrame(errors)

    aggregate_df = summarize_position_sizing_profiles(summary_df)
    recommended_df = select_recommended_size(summary_df)

    reports_dir = Path("reports") / "position_sizing_engine_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    summary_output = reports_dir / "position_sizing_v1_summary.csv"
    simulations_output = reports_dir / "position_sizing_v1_simulations.csv"
    aggregate_output = reports_dir / "position_sizing_v1_aggregate.csv"
    recommended_output = reports_dir / "position_sizing_v1_recommended.csv"
    errors_output = reports_dir / "position_sizing_v1_errors.csv"

    summary_df.to_csv(summary_output, index=False)
    simulations_all_df.to_csv(simulations_output, index=False)
    aggregate_df.to_csv(aggregate_output, index=False)
    recommended_df.to_csv(recommended_output, index=False)
    errors_df.to_csv(errors_output, index=False)

    print_section("POSITION SIZING V1 AGGREGATE")
    if aggregate_df.empty:
        print("Sin resultados.")
    else:
        print(aggregate_df.to_string(index=False))

    print_section("POSITION SIZING V1 RECOMMENDED")
    if recommended_df.empty:
        print("Sin recomendacion.")
    else:
        print(recommended_df.to_string(index=False))

    print_section("POSITION SIZING V1 ERRORS")
    if errors_df.empty:
        print("Sin errores.")
    else:
        print(errors_df.to_string(index=False))

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {summary_output}")
    print(f"- {simulations_output}")
    print(f"- {aggregate_output}")
    print(f"- {recommended_output}")
    print(f"- {errors_output}")


if __name__ == "__main__":
    main()