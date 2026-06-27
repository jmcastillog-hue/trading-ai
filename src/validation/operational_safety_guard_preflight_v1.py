from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd


EXECUTION_FLAG_COLUMNS = [
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "live_alerts_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
    "execution_allowed",
]


FORBIDDEN_OPERATIONAL_PATTERNS = [
    "create_order(",
    "futures_create_order(",
    "order_market_",
    "order_limit_",
    "place_order(",
    "send_order(",
]


@dataclass(frozen=True)
class OperationalSafetyGuardPreflightConfig:
    require_clean_git: bool = False
    allowed_branch_prefixes: tuple[str, ...] = ("main", "fase-")
    reports_dir: Path = Path("reports/operational_safety_guard_preflight_v1")

    required_files: tuple[Path, ...] = (
        Path("docs/PHASE_5_OPERATIONAL_EVIDENCE_RUNBOOK.md"),
        Path("docs/PHASE_5_OPERATIONAL_EVIDENCE_CLOSURE.md"),
        Path("docs/PHASE_6_FORWARD_EVIDENCE_OPERATIONS_CHECKLIST.md"),
        Path("docs/PHASE_6_FORWARD_EVIDENCE_RUN_LOG.md"),
        Path("docs/PHASE_6_OPERATIONAL_SAFETY_GUARD_PREFLIGHT.md"),
        Path("src/workflows/run_operational_forward_evidence_bootstrap_v1.py"),
        Path("src/workflows/run_operational_input_file_validator_adapter_v1.py"),
        Path("src/workflows/run_operational_persistent_cycle_integration_v1.py"),
        Path("src/journal/forward_evidence_run_log_v1.py"),
        Path("src/workflows/run_forward_evidence_run_log_v1.py"),
        Path("src/validation/operational_safety_guard_preflight_v1.py"),
        Path("src/workflows/run_operational_safety_guard_preflight_v1.py"),
    )

    required_directories: tuple[Path, ...] = (
        Path("data/forward_evidence/operational"),
        Path("data/forward_evidence/operational/input/signals"),
        Path("data/forward_evidence/operational/input/ohlc"),
        Path("data/forward_evidence/operational/input/price_levels"),
        Path("data/forward_evidence/operational/backups"),
        Path("data/forward_evidence/operational/snapshots"),
        Path("data/forward_evidence/operational/templates"),
        Path("data/forward_evidence/operational/run_logs"),
    )

    required_runtime_files: tuple[Path, ...] = (
        Path("data/forward_evidence/operational/forward_evidence_dataset_v1.csv"),
        Path("data/forward_evidence/operational/run_logs/forward_evidence_run_log_v1.csv"),
    )

    flag_report_paths: tuple[Path, ...] = (
        Path(
            "reports/operational_persistent_cycle_integration_v1/"
            "operational_integration_summary_v1.csv"
        ),
        Path(
            "reports/forward_evidence_run_log_v1/"
            "forward_evidence_run_log_summary_v1.csv"
        ),
    )

    files_to_scan_for_forbidden_patterns: tuple[Path, ...] = (
        Path("src/journal/operational_persistent_cycle_integration_v1.py"),
        Path("src/workflows/run_operational_persistent_cycle_integration_v1.py"),
        Path("src/journal/forward_evidence_run_log_v1.py"),
        Path("src/workflows/run_forward_evidence_run_log_v1.py"),
        Path("src/workflows/run_operational_safety_guard_preflight_v1.py"),
    )


def run_git_command(args: list[str]) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            return "UNKNOWN"
        return completed.stdout.strip()
    except Exception:
        return "UNKNOWN"


def get_git_branch() -> str:
    branch = run_git_command(["branch", "--show-current"])
    return branch or "UNKNOWN"


def get_git_commit() -> str:
    commit = run_git_command(["rev-parse", "--short", "HEAD"])
    return commit or "UNKNOWN"


def get_git_status_short() -> str:
    status = run_git_command(["status", "--short"])
    return status if status != "UNKNOWN" else ""


def safe_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if pd.isna(value):
        return False

    normalized = str(value).strip().lower()
    return normalized in {"true", "1", "yes", "y"}


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def read_csv_or_empty(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def build_check(
    check_name: str,
    passed: bool,
    severity: str,
    source: str,
    details: str,
    blocker: bool,
) -> dict[str, Any]:
    return {
        "check_name": check_name,
        "passed": passed,
        "severity": severity,
        "source": source,
        "details": details,
        "blocker": blocker,
    }


def build_required_file_checks(
    config: OperationalSafetyGuardPreflightConfig,
) -> list[dict[str, Any]]:
    rows = []

    for path in config.required_files:
        passed = path.exists() and path.is_file()

        rows.append(
            build_check(
                check_name="required_file_exists",
                passed=passed,
                severity="INFO" if passed else "ERROR",
                source=str(path),
                details="OK" if passed else "Required file is missing.",
                blocker=not passed,
            )
        )

    return rows


def build_required_directory_checks(
    config: OperationalSafetyGuardPreflightConfig,
) -> list[dict[str, Any]]:
    rows = []

    for path in config.required_directories:
        passed = path.exists() and path.is_dir()

        rows.append(
            build_check(
                check_name="required_directory_exists",
                passed=passed,
                severity="INFO" if passed else "ERROR",
                source=str(path),
                details="OK" if passed else "Required operational directory is missing.",
                blocker=not passed,
            )
        )

    return rows


def build_runtime_file_checks(
    config: OperationalSafetyGuardPreflightConfig,
) -> list[dict[str, Any]]:
    rows = []

    for path in config.required_runtime_files:
        passed = path.exists() and path.is_file()

        rows.append(
            build_check(
                check_name="required_runtime_file_exists",
                passed=passed,
                severity="INFO" if passed else "ERROR",
                source=str(path),
                details="OK" if passed else "Required operational runtime file is missing.",
                blocker=not passed,
            )
        )

    return rows


def build_git_checks(
    config: OperationalSafetyGuardPreflightConfig,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = []

    branch = get_git_branch()
    commit = get_git_commit()
    status_short = get_git_status_short()
    working_tree_clean = status_short.strip() == ""

    branch_allowed = any(
        branch == prefix or branch.startswith(prefix)
        for prefix in config.allowed_branch_prefixes
    )

    rows.append(
        build_check(
            check_name="git_branch_allowed",
            passed=branch_allowed,
            severity="INFO" if branch_allowed else "ERROR",
            source="git",
            details=f"branch={branch}",
            blocker=not branch_allowed,
        )
    )

    rows.append(
        build_check(
            check_name="git_commit_available",
            passed=commit != "UNKNOWN",
            severity="INFO" if commit != "UNKNOWN" else "ERROR",
            source="git",
            details=f"commit={commit}",
            blocker=commit == "UNKNOWN",
        )
    )

    dirty_is_blocker = config.require_clean_git and not working_tree_clean

    rows.append(
        build_check(
            check_name="git_working_tree_clean",
            passed=working_tree_clean,
            severity="INFO"
            if working_tree_clean
            else ("ERROR" if dirty_is_blocker else "WARNING"),
            source="git",
            details="clean"
            if working_tree_clean
            else f"dirty_entries={len(status_short.splitlines())}",
            blocker=dirty_is_blocker,
        )
    )

    git_meta = {
        "git_branch": branch,
        "git_commit": commit,
        "git_working_tree_clean": working_tree_clean,
        "git_dirty_entries": len(status_short.splitlines()) if status_short else 0,
        "require_clean_git": config.require_clean_git,
    }

    return rows, git_meta


def build_execution_flag_checks(
    config: OperationalSafetyGuardPreflightConfig,
) -> list[dict[str, Any]]:
    rows = []

    for path in config.flag_report_paths:
        df = read_csv_or_empty(path)

        if df.empty:
            rows.append(
                build_check(
                    check_name="execution_flag_report_available",
                    passed=False,
                    severity="WARNING",
                    source=str(path),
                    details="Report not available or empty. Not blocking during development validation.",
                    blocker=False,
                )
            )
            continue

        first_row = df.iloc[0].to_dict()

        for flag_column in EXECUTION_FLAG_COLUMNS:
            value = safe_bool(first_row.get(flag_column, False))
            passed = not value

            rows.append(
                build_check(
                    check_name=f"execution_flag_false:{flag_column}",
                    passed=passed,
                    severity="INFO" if passed else "ERROR",
                    source=str(path),
                    details=f"{flag_column}={value}",
                    blocker=not passed,
                )
            )

    return rows


def build_forbidden_pattern_checks(
    config: OperationalSafetyGuardPreflightConfig,
) -> list[dict[str, Any]]:
    rows = []

    for path in config.files_to_scan_for_forbidden_patterns:
        if not path.exists():
            rows.append(
                build_check(
                    check_name="scan_file_exists",
                    passed=False,
                    severity="ERROR",
                    source=str(path),
                    details="File to scan is missing.",
                    blocker=True,
                )
            )
            continue

        text = read_text(path)

        for pattern in FORBIDDEN_OPERATIONAL_PATTERNS:
            found = pattern in text
            rows.append(
                build_check(
                    check_name="forbidden_execution_pattern_absent",
                    passed=not found,
                    severity="INFO" if not found else "ERROR",
                    source=str(path),
                    details=pattern,
                    blocker=found,
                )
            )

    return rows


def build_safety_checks_df(
    config: OperationalSafetyGuardPreflightConfig,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    rows = []

    git_rows, git_meta = build_git_checks(config)
    rows.extend(git_rows)

    rows.extend(build_required_file_checks(config))
    rows.extend(build_required_directory_checks(config))
    rows.extend(build_runtime_file_checks(config))
    rows.extend(build_execution_flag_checks(config))
    rows.extend(build_forbidden_pattern_checks(config))

    return pd.DataFrame(rows), git_meta


def build_blockers_df(safety_checks_df: pd.DataFrame) -> pd.DataFrame:
    if safety_checks_df.empty:
        return pd.DataFrame(
            [
                {
                    "check_name": "no_checks_generated",
                    "source": "preflight",
                    "details": "No safety checks were generated.",
                }
            ]
        )

    blockers_df = safety_checks_df[
        safety_checks_df["blocker"].astype(bool)
    ].copy()

    return blockers_df


def build_summary_df(
    safety_checks_df: pd.DataFrame,
    blockers_df: pd.DataFrame,
    git_meta: dict[str, Any],
) -> pd.DataFrame:
    blocker_count = len(blockers_df)
    warning_count = int(safety_checks_df["severity"].eq("WARNING").sum())
    error_count = int(safety_checks_df["severity"].eq("ERROR").sum())

    preflight_passed = blocker_count == 0

    if not preflight_passed:
        preflight_decision = "OPERATIONAL_PREFLIGHT_BLOCKED"
    elif warning_count > 0:
        preflight_decision = "OPERATIONAL_PREFLIGHT_VALIDATED_WITH_WARNINGS"
    else:
        preflight_decision = "OPERATIONAL_PREFLIGHT_VALIDATED"

    validation_decision = (
        "PHASE_6_3_OPERATIONAL_SAFETY_GUARD_PREFLIGHT_VALIDATED"
        if preflight_passed
        else "PHASE_6_3_OPERATIONAL_SAFETY_GUARD_PREFLIGHT_FAILED"
    )

    return pd.DataFrame(
        [
            {
                "preflight_passed": preflight_passed,
                "total_checks": len(safety_checks_df),
                "blocker_count": blocker_count,
                "warning_count": warning_count,
                "error_count": error_count,
                "git_branch": git_meta.get("git_branch"),
                "git_commit": git_meta.get("git_commit"),
                "git_working_tree_clean": git_meta.get("git_working_tree_clean"),
                "git_dirty_entries": git_meta.get("git_dirty_entries"),
                "require_clean_git": git_meta.get("require_clean_git"),
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "preflight_decision": preflight_decision,
                "validation_decision": validation_decision,
            }
        ]
    )


def save_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def run_operational_safety_guard_preflight(
    config: OperationalSafetyGuardPreflightConfig | None = None,
) -> dict[str, pd.DataFrame]:
    active_config = config or OperationalSafetyGuardPreflightConfig()

    safety_checks_df, git_meta = build_safety_checks_df(active_config)
    blockers_df = build_blockers_df(safety_checks_df)
    summary_df = build_summary_df(
        safety_checks_df=safety_checks_df,
        blockers_df=blockers_df,
        git_meta=git_meta,
    )

    active_config.reports_dir.mkdir(parents=True, exist_ok=True)

    save_df(
        summary_df,
        active_config.reports_dir / "operational_safety_guard_preflight_summary_v1.csv",
    )
    save_df(
        safety_checks_df,
        active_config.reports_dir / "operational_safety_guard_preflight_checks_v1.csv",
    )
    save_df(
        blockers_df,
        active_config.reports_dir / "operational_safety_guard_preflight_blockers_v1.csv",
    )

    return {
        "summary": summary_df,
        "safety_checks": safety_checks_df,
        "blockers": blockers_df,
    }