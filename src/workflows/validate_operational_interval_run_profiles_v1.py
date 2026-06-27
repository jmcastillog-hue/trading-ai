from src.orchestration.operational_interval_run_profiles_v1 import (
    validate_operational_interval_run_profiles,
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


def main() -> None:
    print("OPERATIONAL INTERVAL RUN PROFILES V1")
    print("=" * 100)
    print("Purpose: validate named interval profiles for forward evidence collection")
    print("Restriction: profile validation only. No execution.")
    print()

    result = validate_operational_interval_run_profiles()

    print_section("PROFILE VALIDATION SUMMARY")
    print_df(result["summary"])

    print_section("PROFILE DECISIONS")
    print_df(result["decisions"])

    print_section("PROFILE REGISTRY")
    print_df(result["profiles"])

    print_section("PROFILE CHECKS")
    print_df(result["checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/operational_interval_run_profiles_v1/operational_interval_profiles_summary_v1.csv")
    print("- reports/operational_interval_run_profiles_v1/operational_interval_profiles_registry_v1.csv")
    print("- reports/operational_interval_run_profiles_v1/operational_interval_profiles_checks_v1.csv")
    print("- reports/operational_interval_run_profiles_v1/operational_interval_profiles_decisions_v1.csv")
    print()
    print("Restriccion: este workflow valida perfiles. No ejecuta ciclos.")


if __name__ == "__main__":
    main()