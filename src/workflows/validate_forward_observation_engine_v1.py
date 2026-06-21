from pathlib import Path

import pandas as pd

from src.paper_trading.forward_observation_engine_v1 import (
    ForwardObservationConfig,
    build_forward_observation_plan,
    build_forward_observation_specification,
    summarize_forward_observation_plan,
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
    print("FORWARD OBSERVATION ENGINE V1")
    print("=" * 100)
    print("Input: Fase 2.5 + 2.6 reports")
    print("Purpose: generate observation-only paper trading specification")
    print()

    readiness_profile_path = (
        Path("reports")
        / "paper_trading_readiness_gate_v1"
        / "paper_trading_readiness_v1_profile_decisions.csv"
    )

    readiness_global_path = (
        Path("reports")
        / "paper_trading_readiness_gate_v1"
        / "paper_trading_readiness_v1_global_decision.csv"
    )

    router_routes_path = (
        Path("reports")
        / "context_risk_router_v1"
        / "context_risk_router_v1_routes.csv"
    )

    errors = []

    try:
        readiness_profile_df = load_csv_or_fail(readiness_profile_path)
        readiness_global_df = load_csv_or_fail(readiness_global_path)
        router_routes_df = load_csv_or_fail(router_routes_path)

        config = ForwardObservationConfig(
            min_forward_signals=100,
            preferred_forward_signals=300,
            max_theoretical_risk_pct=0.0050,
            allow_aggressive_observation=True,
            require_manual_review=True,
        )

        plan_df = build_forward_observation_plan(
            readiness_profile_df=readiness_profile_df,
            readiness_global_df=readiness_global_df,
            router_routes_df=router_routes_df,
            config=config,
        )

        summary_df = summarize_forward_observation_plan(plan_df)

        specification_lines = build_forward_observation_specification(
            plan_df=plan_df,
            summary_df=summary_df,
            config=config,
        )

    except Exception as exc:
        errors.append({"error": repr(exc)})
        plan_df = pd.DataFrame()
        summary_df = pd.DataFrame()
        specification_lines = [
            "# Paper Trading Specification / Forward Observation V1",
            "",
            "NOT READY",
            "",
            repr(exc),
        ]

    errors_df = pd.DataFrame(errors)

    reports_dir = Path("reports") / "forward_observation_engine_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    plan_output = reports_dir / "forward_observation_v1_plan.csv"
    summary_output = reports_dir / "forward_observation_v1_summary.csv"
    specification_output = reports_dir / "forward_observation_v1_specification.md"
    errors_output = reports_dir / "forward_observation_v1_errors.csv"

    plan_df.to_csv(plan_output, index=False)
    summary_df.to_csv(summary_output, index=False)
    errors_df.to_csv(errors_output, index=False)

    specification_output.write_text(
        "\n".join(specification_lines),
        encoding="utf-8",
    )

    print_section("FORWARD OBSERVATION V1 SUMMARY")
    if summary_df.empty:
        print("Sin resultados.")
    else:
        print(summary_df.to_string(index=False))

    print_section("FORWARD OBSERVATION V1 PLAN")
    if plan_df.empty:
        print("Sin resultados.")
    else:
        display_columns = [
            "cost_profile",
            "readiness_decision",
            "context_name",
            "route_decision",
            "observation_permission",
            "theoretical_risk_pct",
            "paper_trade_execution_allowed",
            "real_capital_allowed",
            "forward_observation_allowed",
        ]

        print(plan_df[display_columns].to_string(index=False))

    print_section("FORWARD OBSERVATION V1 ERRORS")
    if errors_df.empty:
        print("Sin errores.")
    else:
        print(errors_df.to_string(index=False))

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {plan_output}")
    print(f"- {summary_output}")
    print(f"- {specification_output}")
    print(f"- {errors_output}")


if __name__ == "__main__":
    main()