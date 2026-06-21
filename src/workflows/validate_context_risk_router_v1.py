from pathlib import Path

import pandas as pd

from src.risk.context_risk_router_v1 import (
    build_context_risk_routes,
    summarize_router_by_profile,
    summarize_router_routes,
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
    print("CONTEXT-BASED RISK ROUTER V1")
    print("=" * 100)
    print("Input: Fase 2.2 + Fase 2.3 + Fase 2.4 reports")
    print("Purpose: route risk size according to cost, sequence risk and market context")
    print()

    cost_path = (
        Path("reports")
        / "cost_aware_filter_v1"
        / "cost_aware_v1_aggregate_summary.csv"
    )

    monte_carlo_path = (
        Path("reports")
        / "monte_carlo_risk_engine_v1"
        / "monte_carlo_v1_aggregate.csv"
    )

    position_path = (
        Path("reports")
        / "position_sizing_engine_v1"
        / "position_sizing_v1_aggregate.csv"
    )

    cost_df = load_csv_or_fail(cost_path)
    monte_carlo_df = load_csv_or_fail(monte_carlo_path)
    position_df = load_csv_or_fail(position_path)

    routes_df = build_context_risk_routes(
        cost_df=cost_df,
        monte_carlo_df=monte_carlo_df,
        position_df=position_df,
    )

    aggregate_df = summarize_router_routes(routes_df)
    profile_summary_df = summarize_router_by_profile(routes_df)

    reports_dir = Path("reports") / "context_risk_router_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    routes_output = reports_dir / "context_risk_router_v1_routes.csv"
    aggregate_output = reports_dir / "context_risk_router_v1_aggregate.csv"
    profile_summary_output = reports_dir / "context_risk_router_v1_profile_summary.csv"

    routes_df.to_csv(routes_output, index=False)
    aggregate_df.to_csv(aggregate_output, index=False)
    profile_summary_df.to_csv(profile_summary_output, index=False)

    print_section("CONTEXT RISK ROUTER V1 PROFILE SUMMARY")
    if profile_summary_df.empty:
        print("Sin resultados.")
    else:
        print(profile_summary_df.to_string(index=False))

    print_section("CONTEXT RISK ROUTER V1 ROUTES")
    if aggregate_df.empty:
        print("Sin resultados.")
    else:
        display_columns = [
            "cost_profile",
            "context_name",
            "cost_decision",
            "monte_carlo_decision",
            "recommended_risk_per_trade_pct",
            "route_decision",
            "selected_position_decision",
            "context_score",
        ]

        print(aggregate_df[display_columns].to_string(index=False))

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {routes_output}")
    print(f"- {aggregate_output}")
    print(f"- {profile_summary_output}")


if __name__ == "__main__":
    main()