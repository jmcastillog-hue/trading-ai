from pathlib import Path

import pandas as pd

from src.risk.monte_carlo_risk_engine_v1 import (
    MonteCarloConfig,
    run_monte_carlo_for_profile,
    summarize_all_profiles,
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
    print("MONTE CARLO RISK ENGINE V1")
    print("=" * 100)
    print("Input: cost-aware adjusted trades from Fase 2.2")
    print("Purpose: evaluate sequence risk, drawdown risk and losing streak risk")
    print()

    trades_df = load_cost_adjusted_trades()

    profiles = sorted(trades_df["cost_profile"].dropna().unique().tolist())

    config = MonteCarloConfig(
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
        print_section(f"MONTE CARLO PROFILE: {profile_name}")

        try:
            simulations_df, summary = run_monte_carlo_for_profile(
                trades_df=trades_df,
                profile_name=profile_name,
                config=config,
            )

            summary_rows.append(summary)

            if not simulations_df.empty:
                all_simulations.append(simulations_df)

            print(
                pd.DataFrame([summary]).to_string(index=False)
            )

        except Exception as exc:
            error_row = {
                "cost_profile": profile_name,
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
    aggregate_df = summarize_all_profiles(summary_df)

    reports_dir = Path("reports") / "monte_carlo_risk_engine_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    summary_output = reports_dir / "monte_carlo_v1_summary.csv"
    simulations_output = reports_dir / "monte_carlo_v1_simulations.csv"
    aggregate_output = reports_dir / "monte_carlo_v1_aggregate.csv"
    errors_output = reports_dir / "monte_carlo_v1_errors.csv"

    summary_df.to_csv(summary_output, index=False)
    simulations_all_df.to_csv(simulations_output, index=False)
    aggregate_df.to_csv(aggregate_output, index=False)
    errors_df.to_csv(errors_output, index=False)

    print_section("MONTE CARLO V1 AGGREGATE")
    if aggregate_df.empty:
        print("Sin resultados.")
    else:
        print(aggregate_df.to_string(index=False))

    print_section("MONTE CARLO V1 ERRORS")
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
    print(f"- {errors_output}")


if __name__ == "__main__":
    main()