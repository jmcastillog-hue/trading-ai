from src.journal.forward_evidence_run_log_v1 import run_forward_evidence_run_log


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
    print("FORWARD EVIDENCE RUN LOG V1")
    print("=" * 100)
    print("Purpose: append latest operational evidence cycle summary to persistent run log")
    print("Restriction: logging only. No execution.")
    print()

    result = run_forward_evidence_run_log()

    print_section("RUN LOG SUMMARY")
    print_df(result["summary"])

    print_section("LATEST RUN LOG ENTRY")
    print_df(result["latest_entry"])

    print_section("RUN LOG TAIL")
    print_df(result["run_log_tail"])

    print()
    print("ARCHIVOS PRINCIPALES")
    print("=" * 100)
    print("- data/forward_evidence/operational/run_logs/forward_evidence_run_log_v1.csv")
    print("- reports/forward_evidence_run_log_v1/forward_evidence_run_log_summary_v1.csv")
    print("- reports/forward_evidence_run_log_v1/forward_evidence_latest_run_log_entry_v1.csv")
    print("- reports/forward_evidence_run_log_v1/forward_evidence_run_log_tail_v1.csv")
    print()
    print("Restriccion: este workflow registra evidencia. No habilita ejecucion.")


if __name__ == "__main__":
    main()