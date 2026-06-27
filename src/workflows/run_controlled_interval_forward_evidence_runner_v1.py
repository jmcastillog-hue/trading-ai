from src.orchestration.controlled_interval_forward_evidence_runner_v1 import (
    ControlledIntervalForwardEvidenceRunnerConfig,
    run_controlled_interval_forward_evidence_runner,
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
    print("CONTROLLED INTERVAL FORWARD EVIDENCE RUNNER V1")
    print("=" * 100)
    print("Purpose: run controlled forward evidence cycles by interval")
    print("Restriction: interval evidence orchestration only. No execution.")
    print()

    config = ControlledIntervalForwardEvidenceRunnerConfig(
        max_cycles=2,
        interval_seconds=5,
        require_clean_git=False,
        stop_on_failed_cycle=True,
        stop_on_execution_flag=True,
    )

    result = run_controlled_interval_forward_evidence_runner(config=config)

    print_section("CONTROLLED INTERVAL SUMMARY")
    print_df(result["summary"])

    print_section("CONTROLLED INTERVAL CYCLE RECORDS")
    print_df(result["cycle_records"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/controlled_interval_forward_evidence_runner_v1/controlled_interval_summary_v1.csv")
    print("- reports/controlled_interval_forward_evidence_runner_v1/controlled_interval_cycle_records_v1.csv")
    print()
    print("Restriccion: este runner repite ciclos de evidencia. No habilita ejecucion.")


if __name__ == "__main__":
    main()