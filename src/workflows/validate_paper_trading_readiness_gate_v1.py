from pathlib import Path

import pandas as pd

from src.validation.paper_trading_readiness_gate_v1 import (
    build_global_readiness_decision,
    build_profile_readiness_decisions,
    summarize_profile_readiness,
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
    print("PAPER TRADING READINESS GATE V1")
    print("=" * 100)
    print("Input: Fase 2.1 + 2.2 + 2.3 + 2.4 + 2.5 reports")
    print("Purpose: emit a formal readiness decision before paper trading")
    print()

    walk_forward_path = (
        Path("reports")
        / "walk_forward_engine_v1"
        / "walk_forward_v1_summary.csv"
    )

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

    position_recommended_path = (
        Path("reports")
        / "position_sizing_engine_v1"
        / "position_sizing_v1_recommended.csv"
    )

    router_profile_path = (
        Path("reports")
        / "context_risk_router_v1"
        / "context_risk_router_v1_profile_summary.csv"
    )

    errors = []

    try:
        walk_forward_df = load_csv_or_fail(walk_forward_path)
        cost_df = load_csv_or_fail(cost_path)
        monte_carlo_df = load_csv_or_fail(monte_carlo_path)
        position_recommended_df = load_csv_or_fail(position_recommended_path)
        router_profile_df = load_csv_or_fail(router_profile_path)

        profile_df = build_profile_readiness_decisions(
            walk_forward_df=walk_forward_df,
            cost_df=cost_df,
            monte_carlo_df=monte_carlo_df,
            position_recommended_df=position_recommended_df,
            router_profile_df=router_profile_df,
        )

        profile_summary_df = summarize_profile_readiness(profile_df)
        global_df = build_global_readiness_decision(profile_summary_df)

    except Exception as exc:
        errors.append({"error": repr(exc)})
        profile_summary_df = pd.DataFrame()
        global_df = pd.DataFrame(
            [
                {
                    "global_readiness_decision": "NOT_READY",
                    "best_profile": "NONE",
                    "candidate_profiles": "",
                    "best_recommended_position_risk_pct": 0.0,
                    "best_router_max_risk_pct": 0.0,
                    "reason": repr(exc),
                    "next_action": "Fix missing or invalid validation report inputs.",
                }
            ]
        )

    errors_df = pd.DataFrame(errors)

    reports_dir = Path("reports") / "paper_trading_readiness_gate_v1"
    reports_dir.mkdir(parents=True, exist_ok=True)

    profile_output = reports_dir / "paper_trading_readiness_v1_profile_decisions.csv"
    global_output = reports_dir / "paper_trading_readiness_v1_global_decision.csv"
    errors_output = reports_dir / "paper_trading_readiness_v1_errors.csv"

    profile_summary_df.to_csv(profile_output, index=False)
    global_df.to_csv(global_output, index=False)
    errors_df.to_csv(errors_output, index=False)

    print_section("PAPER TRADING READINESS V1 GLOBAL DECISION")
    print(global_df.to_string(index=False))

    print_section("PAPER TRADING READINESS V1 PROFILE DECISIONS")
    if profile_summary_df.empty:
        print("Sin resultados.")
    else:
        display_columns = [
            "cost_profile",
            "readiness_decision",
            "cost_decision",
            "monte_carlo_decision",
            "recommended_position_risk_pct",
            "router_max_recommended_risk",
            "router_blocked_contexts",
            "blockers",
            "next_action",
        ]

        print(profile_summary_df[display_columns].to_string(index=False))

    print_section("PAPER TRADING READINESS V1 ERRORS")
    if errors_df.empty:
        print("Sin errores.")
    else:
        print(errors_df.to_string(index=False))

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {profile_output}")
    print(f"- {global_output}")
    print(f"- {errors_output}")


if __name__ == "__main__":
    main()