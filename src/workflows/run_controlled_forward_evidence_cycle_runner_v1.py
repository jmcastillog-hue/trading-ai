from src.orchestration.controlled_forward_evidence_cycle_runner_v1 import (
    ControlledForwardEvidenceCycleRunnerConfig,
    run_controlled_forward_evidence_cycle,
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
    print("CONTROLLED FORWARD EVIDENCE CYCLE RUNNER V1")
    print("=" * 100)
    print("Purpose: run one controlled forward evidence cycle")
    print("Restriction: evidence orchestration only. No execution.")
    print()

    config = ControlledForwardEvidenceCycleRunnerConfig(
        require_clean_git=False,
        stop_on_preflight_blocker=True,
    )

    result = run_controlled_forward_evidence_cycle(config=config)

    print_section("CONTROLLED CYCLE SUMMARY")
    print_df(result["summary"])

    print_section("COMMAND RESULTS")
    print_df(result["command_results"])

    print_section("PREFLIGHT SUMMARY")
    print_df(result["preflight_summary"])

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print("- reports/controlled_forward_evidence_cycle_runner_v1/controlled_cycle_summary_v1.csv")
    print("- reports/controlled_forward_evidence_cycle_runner_v1/controlled_cycle_command_results_v1.csv")
    print("- reports/controlled_forward_evidence_cycle_runner_v1/controlled_cycle_preflight_summary_v1.csv")
    print()
    print("Restriccion: este runner orquesta evidencia. No habilita ejecucion.")


if __name__ == "__main__":
    main()