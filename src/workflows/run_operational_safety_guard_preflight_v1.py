from src.validation.operational_safety_guard_preflight_v1 import (
    OperationalSafetyGuardPreflightConfig,
    run_operational_safety_guard_preflight,
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
    print("OPERATIONAL SAFETY GUARD PREFLIGHT V1")
    print("=" * 100)
    print("Purpose: validate safety conditions before operational evidence processing")
    print("Restriction: safety validation only. No execution.")
    print()

    config = OperationalSafetyGuardPreflightConfig(
        require_clean_git=False,
    )

    result = run_operational_safety_guard_preflight(config=config)

    print_section("PREFLIGHT SUMMARY")
    print_df(result["summary"])

    print_section("BLOCKERS")
    print_df(result["blockers"])

    print_section("SAFETY CHECKS")
    print_df(result["safety_checks"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/operational_safety_guard_preflight_v1/operational_safety_guard_preflight_summary_v1.csv")
    print("- reports/operational_safety_guard_preflight_v1/operational_safety_guard_preflight_checks_v1.csv")
    print("- reports/operational_safety_guard_preflight_v1/operational_safety_guard_preflight_blockers_v1.csv")
    print()
    print("Restriccion: este preflight valida seguridad. No habilita ejecucion.")


if __name__ == "__main__":
    main()