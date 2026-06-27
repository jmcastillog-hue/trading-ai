from __future__ import annotations

import argparse

from src.orchestration.profile_based_interval_forward_evidence_runner_v1 import (
    ProfileBasedIntervalForwardEvidenceRunnerConfig,
    run_profile_based_interval_forward_evidence_runner,
)


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * 100)


def print_df(df):
    if df.empty:
        print("Sin registros.")
        return

    print(df.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run controlled interval forward evidence by named profile."
    )
    parser.add_argument(
        "profile_name",
        nargs="?",
        default="DEV_TEST",
        help="Profile name. Example: DEV_TEST, SHORT_OBSERVATION, HALF_HOUR_MONITOR.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("PROFILE BASED INTERVAL FORWARD EVIDENCE RUNNER V1")
    print("=" * 100)
    print("Purpose: run controlled interval evidence using a named profile")
    print("Restriction: profile-based evidence orchestration only. No execution.")
    print(f"Selected profile: {args.profile_name}")
    print()

    config = ProfileBasedIntervalForwardEvidenceRunnerConfig()

    result = run_profile_based_interval_forward_evidence_runner(
        profile_name=args.profile_name,
        config=config,
    )

    print_section("PROFILE BASED SUMMARY")
    print_df(result["summary"])

    print_section("SELECTED PROFILE DECISION")
    print_df(result["selected_profile_decision"])

    print_section("SELECTED PROFILE REGISTRY")
    print_df(result["selected_profile_registry"])

    print_section("INTERVAL RUNNER SUMMARY")
    print_df(result["interval_summary"])

    print_section("INTERVAL CYCLE RECORDS")
    print_df(result["cycle_records"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/profile_based_interval_forward_evidence_runner_v1/profile_based_interval_summary_v1.csv")
    print("- reports/profile_based_interval_forward_evidence_runner_v1/profile_based_selected_profile_decision_v1.csv")
    print("- reports/profile_based_interval_forward_evidence_runner_v1/profile_based_selected_profile_registry_v1.csv")
    print("- reports/profile_based_interval_forward_evidence_runner_v1/profile_based_selected_profile_checks_v1.csv")
    print("- reports/profile_based_interval_forward_evidence_runner_v1/profile_based_interval_runner_summary_v1.csv")
    print("- reports/profile_based_interval_forward_evidence_runner_v1/profile_based_interval_cycle_records_v1.csv")
    print()
    print("Restriccion: este workflow ejecuta evidencia por perfil. No habilita ejecucion.")


if __name__ == "__main__":
    main()