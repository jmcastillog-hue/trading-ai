from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from src.journal.forward_evidence_accumulation_controller_v1 import (
    ForwardEvidenceAccumulationControllerConfig,
    run_forward_evidence_accumulation_controller,
)
from src.journal.forward_evidence_dataset_persistence_v1 import (
    ForwardEvidenceDatasetPersistenceConfig,
    all_execution_flags_false,
    persist_forward_evidence_dataset,
    read_forward_evidence_dataset,
)


@dataclass(frozen=True)
class PersistentForwardEvidenceCycleRunnerConfig:
    dataset_path: str = "data/forward_evidence/forward_evidence_dataset_v1.csv"
    backup_dir: str = "data/forward_evidence/backups"
    snapshot_dir: str = "data/forward_evidence/snapshots"
    min_forward_observations: int = 100
    preferred_forward_observations: int = 300
    timestamp_column: str = "timestamp"
    same_bar_policy: str = "CONSERVATIVE_STOP"
    max_bars_after_observation: int = 96
    create_backup_before_write: bool = True
    create_snapshot_after_write: bool = True
    cycle_runner_name: str = "PERSISTENT_FORWARD_EVIDENCE_CYCLE_RUNNER_V1"
    paper_trade_execution_allowed: bool = False
    real_capital_allowed: bool = False
    live_alerts_allowed: bool = False
    exchange_execution_allowed: bool = False
    automation_allowed: bool = False


def safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except Exception:
        pass

    return str(value).strip()


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or pd.isna(value):
            return default
        return int(value)
    except Exception:
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def summary_value(
    summary_df: pd.DataFrame,
    column: str,
    default: Any = 0,
) -> Any:
    if summary_df is None or summary_df.empty:
        return default

    if column not in summary_df.columns:
        return default

    try:
        return summary_df.iloc[0][column]
    except Exception:
        return default


def dataframe_validation_passed(validation_df: pd.DataFrame) -> bool:
    if validation_df is None or validation_df.empty:
        return False

    if "passed" not in validation_df.columns:
        return False

    return bool(validation_df["passed"].all())


def build_cycle_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def create_dataset_backup(
    dataset_path: Path,
    backup_dir: Path,
    cycle_id: str,
) -> Path | None:
    if not dataset_path.exists():
        return None

    backup_dir.mkdir(parents=True, exist_ok=True)

    backup_path = backup_dir / (
        f"{dataset_path.stem}_backup_{cycle_id}{dataset_path.suffix}"
    )

    shutil.copy2(dataset_path, backup_path)

    return backup_path


def create_dataset_snapshot(
    dataset_path: Path,
    snapshot_dir: Path,
    cycle_id: str,
) -> Path | None:
    if not dataset_path.exists():
        return None

    snapshot_dir.mkdir(parents=True, exist_ok=True)

    snapshot_path = snapshot_dir / (
        f"{dataset_path.stem}_snapshot_{cycle_id}{dataset_path.suffix}"
    )

    shutil.copy2(dataset_path, snapshot_path)

    return snapshot_path


def write_dataset_atomically(
    dataset_df: pd.DataFrame,
    dataset_path: Path,
) -> Path:
    dataset_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = dataset_path.with_name(
        f"{dataset_path.name}.tmp"
    )

    try:
        dataset_df.to_csv(temporary_path, index=False)
        os.replace(temporary_path, dataset_path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()

    return dataset_path


def build_cycle_validation_df(
    controller_summary_df: pd.DataFrame,
    controller_validation_df: pd.DataFrame,
    persistence_summary_df: pd.DataFrame,
    persistence_validation_df: pd.DataFrame,
    dataset_after_df: pd.DataFrame,
    dataset_path: Path,
    existing_rows_before: int,
    new_rows_added: int,
    updated_rows: int,
    write_required: bool,
    write_performed: bool,
) -> pd.DataFrame:
    rows = []

    rows.append(
        {
            "check_name": "controller_summary_exists",
            "passed": not controller_summary_df.empty,
            "severity": "ERROR",
            "details": f"rows={len(controller_summary_df)}",
        }
    )

    rows.append(
        {
            "check_name": "controller_validation_passed",
            "passed": dataframe_validation_passed(controller_validation_df),
            "severity": "ERROR",
            "details": "accumulation controller validation must pass",
        }
    )

    rows.append(
        {
            "check_name": "persistence_summary_exists",
            "passed": not persistence_summary_df.empty,
            "severity": "ERROR",
            "details": f"rows={len(persistence_summary_df)}",
        }
    )

    rows.append(
        {
            "check_name": "persistence_validation_passed",
            "passed": dataframe_validation_passed(persistence_validation_df),
            "severity": "ERROR",
            "details": "dataset persistence validation must pass",
        }
    )

    rows.append(
        {
            "check_name": "dataset_after_exists",
            "passed": not dataset_after_df.empty,
            "severity": "ERROR",
            "details": f"rows={len(dataset_after_df)}",
        }
    )

    expected_minimum_rows = existing_rows_before + new_rows_added

    rows.append(
        {
            "check_name": "dataset_row_count_consistent",
            "passed": len(dataset_after_df) >= expected_minimum_rows,
            "severity": "ERROR",
            "details": (
                f"dataset_after={len(dataset_after_df)}, "
                f"existing_before={existing_rows_before}, "
                f"new_rows={new_rows_added}, "
                f"updated_rows={updated_rows}"
            ),
        }
    )

    rows.append(
        {
            "check_name": "all_execution_flags_false",
            "passed": all_execution_flags_false(dataset_after_df),
            "severity": "ERROR",
            "details": "persistent cycle must never enable execution",
        }
    )

    rows.append(
        {
            "check_name": "dataset_write_completed_when_required",
            "passed": (not write_required) or write_performed,
            "severity": "ERROR",
            "details": (
                f"write_required={write_required}, "
                f"write_performed={write_performed}"
            ),
        }
    )

    rows.append(
        {
            "check_name": "dataset_file_exists_after_write",
            "passed": (
                dataset_path.exists()
                if write_required
                else True
            ),
            "severity": "ERROR",
            "details": str(dataset_path),
        }
    )

    return pd.DataFrame(rows)


def build_cycle_summary_df(
    cycle_id: str,
    controller_summary_df: pd.DataFrame,
    persistence_summary_df: pd.DataFrame,
    cycle_validation_df: pd.DataFrame,
    dataset_path: Path,
    backup_path: Path | None,
    snapshot_path: Path | None,
    write_required: bool,
    write_performed: bool,
    config: PersistentForwardEvidenceCycleRunnerConfig,
) -> pd.DataFrame:
    validation_passed = dataframe_validation_passed(cycle_validation_df)

    existing_rows_before = safe_int(
        summary_value(
            persistence_summary_df,
            "existing_rows_before",
            0,
        )
    )

    incoming_rows = safe_int(
        summary_value(
            persistence_summary_df,
            "incoming_rows",
            0,
        )
    )

    new_rows_added = safe_int(
        summary_value(
            persistence_summary_df,
            "new_rows_added",
            0,
        )
    )

    updated_rows = safe_int(
        summary_value(
            persistence_summary_df,
            "updated_rows",
            0,
        )
    )

    duplicate_rows_skipped = safe_int(
        summary_value(
            persistence_summary_df,
            "duplicate_rows_skipped",
            0,
        )
    )

    invalid_rows = safe_int(
        summary_value(
            persistence_summary_df,
            "invalid_rows",
            0,
        )
    )

    dataset_rows_after = safe_int(
        summary_value(
            persistence_summary_df,
            "dataset_rows_after",
            0,
        )
    )

    closed_observations = safe_int(
        summary_value(
            persistence_summary_df,
            "closed_observations",
            0,
        )
    )

    open_observations = safe_int(
        summary_value(
            persistence_summary_df,
            "open_observations",
            0,
        )
    )

    error_observations = safe_int(
        summary_value(
            persistence_summary_df,
            "error_observations",
            0,
        )
    )

    wins = safe_int(
        summary_value(
            persistence_summary_df,
            "wins",
            0,
        )
    )

    losses = safe_int(
        summary_value(
            persistence_summary_df,
            "losses",
            0,
        )
    )

    avg_result_r = safe_float(
        summary_value(
            persistence_summary_df,
            "avg_result_r",
            0.0,
        )
    )

    sum_result_r = safe_float(
        summary_value(
            persistence_summary_df,
            "sum_result_r",
            0.0,
        )
    )

    cumulative_closed_observations = safe_int(
        summary_value(
            persistence_summary_df,
            "cumulative_closed_observations",
            0,
        )
    )

    sample_gap_to_minimum = safe_int(
        summary_value(
            persistence_summary_df,
            "sample_gap_to_minimum",
            config.min_forward_observations,
        )
    )

    sample_gap_to_preferred = safe_int(
        summary_value(
            persistence_summary_df,
            "sample_gap_to_preferred",
            config.preferred_forward_observations,
        )
    )

    readiness_state = safe_str(
        summary_value(
            persistence_summary_df,
            "readiness_state",
            "FORWARD_SAMPLE_INSUFFICIENT",
        )
    )

    controller_decision = safe_str(
        summary_value(
            controller_summary_df,
            "controller_decision",
            "",
        )
    )

    persistence_decision = safe_str(
        summary_value(
            persistence_summary_df,
            "persistence_decision",
            "",
        )
    )

    if not validation_passed:
        cycle_decision = "PERSISTENT_CYCLE_VALIDATION_FAILED"
    elif invalid_rows > 0:
        cycle_decision = "PERSISTENT_CYCLE_COMPLETED_WITH_INVALID_ROWS"
    elif new_rows_added > 0 and updated_rows > 0:
        cycle_decision = "PERSISTENT_CYCLE_COMPLETED_NEW_AND_UPDATED_EVIDENCE"
    elif new_rows_added > 0:
        cycle_decision = "PERSISTENT_CYCLE_COMPLETED_NEW_EVIDENCE"
    elif updated_rows > 0:
        cycle_decision = "PERSISTENT_CYCLE_COMPLETED_UPDATED_EVIDENCE"
    elif duplicate_rows_skipped > 0:
        cycle_decision = "PERSISTENT_CYCLE_COMPLETED_DUPLICATES_ONLY"
    else:
        cycle_decision = "PERSISTENT_CYCLE_COMPLETED_NO_CHANGES"

    return pd.DataFrame(
        [
            {
                "cycle_id": cycle_id,
                "validation_passed": validation_passed,
                "incoming_rows": incoming_rows,
                "existing_rows_before": existing_rows_before,
                "new_rows_added": new_rows_added,
                "updated_rows": updated_rows,
                "duplicate_rows_skipped": duplicate_rows_skipped,
                "invalid_rows": invalid_rows,
                "dataset_rows_after": dataset_rows_after,
                "closed_observations": closed_observations,
                "open_observations": open_observations,
                "error_observations": error_observations,
                "wins": wins,
                "losses": losses,
                "avg_result_r": round(avg_result_r, 6),
                "sum_result_r": round(sum_result_r, 6),
                "cumulative_closed_observations": cumulative_closed_observations,
                "minimum_sample_reached": (
                    cumulative_closed_observations
                    >= config.min_forward_observations
                ),
                "preferred_sample_reached": (
                    cumulative_closed_observations
                    >= config.preferred_forward_observations
                ),
                "sample_gap_to_minimum": sample_gap_to_minimum,
                "sample_gap_to_preferred": sample_gap_to_preferred,
                "readiness_state": readiness_state,
                "dataset_write_required": write_required,
                "dataset_write_performed": write_performed,
                "dataset_path": str(dataset_path),
                "backup_created": backup_path is not None,
                "backup_path": (
                    str(backup_path)
                    if backup_path is not None
                    else ""
                ),
                "snapshot_created": snapshot_path is not None,
                "snapshot_path": (
                    str(snapshot_path)
                    if snapshot_path is not None
                    else ""
                ),
                "controller_decision": controller_decision,
                "persistence_decision": persistence_decision,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "cycle_decision": cycle_decision,
            }
        ]
    )


def run_persistent_forward_evidence_cycle(
    source_signals_df: pd.DataFrame,
    ohlc_df: pd.DataFrame,
    price_levels_df: pd.DataFrame | None = None,
    config: PersistentForwardEvidenceCycleRunnerConfig | None = None,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    if config is None:
        config = PersistentForwardEvidenceCycleRunnerConfig()

    cycle_id = build_cycle_id()

    dataset_path = Path(config.dataset_path)
    backup_dir = Path(config.backup_dir)
    snapshot_dir = Path(config.snapshot_dir)

    existing_dataset_df = read_forward_evidence_dataset(dataset_path)

    (
        controller_summary_df,
        controller_validation_df,
        runner_summary_df,
        runner_validation_df,
        resolver_summary_df,
        resolver_validation_df,
        generated_observations_df,
        detector_accepted_df,
        detector_rejected_df,
        accepted_new_df,
        duplicate_observations_df,
        priced_dataset_df,
        resolved_closed_df,
        still_open_df,
        controller_dataset_after_resolution_df,
    ) = run_forward_evidence_accumulation_controller(
        source_signals_df=source_signals_df,
        existing_dataset_df=existing_dataset_df,
        ohlc_df=ohlc_df,
        price_levels_df=price_levels_df,
        config=ForwardEvidenceAccumulationControllerConfig(
            min_forward_observations=config.min_forward_observations,
            preferred_forward_observations=config.preferred_forward_observations,
            timestamp_column=config.timestamp_column,
            same_bar_policy=config.same_bar_policy,
            max_bars_after_observation=config.max_bars_after_observation,
            paper_trade_execution_allowed=False,
            real_capital_allowed=False,
            live_alerts_allowed=False,
            exchange_execution_allowed=False,
            automation_allowed=False,
        ),
    )

    (
        persistence_summary_df,
        persistence_validation_df,
        persistence_new_rows_df,
        persistence_updated_rows_df,
        persistence_duplicate_rows_df,
        persistence_invalid_rows_df,
        dataset_after_df,
    ) = persist_forward_evidence_dataset(
        incoming_dataset_df=controller_dataset_after_resolution_df,
        existing_dataset_df=existing_dataset_df,
        config=ForwardEvidenceDatasetPersistenceConfig(
            min_forward_observations=config.min_forward_observations,
            preferred_forward_observations=config.preferred_forward_observations,
            paper_trade_execution_allowed=False,
            real_capital_allowed=False,
            live_alerts_allowed=False,
            exchange_execution_allowed=False,
            automation_allowed=False,
        ),
    )

    new_rows_added = len(persistence_new_rows_df)
    updated_rows = len(persistence_updated_rows_df)

    write_required = new_rows_added > 0 or updated_rows > 0

    prewrite_validation_passed = (
        dataframe_validation_passed(controller_validation_df)
        and dataframe_validation_passed(persistence_validation_df)
        and all_execution_flags_false(dataset_after_df)
    )

    backup_path = None
    snapshot_path = None
    write_performed = False

    if write_required and prewrite_validation_passed:
        if (
            config.create_backup_before_write
            and dataset_path.exists()
        ):
            backup_path = create_dataset_backup(
                dataset_path=dataset_path,
                backup_dir=backup_dir,
                cycle_id=cycle_id,
            )

        write_dataset_atomically(
            dataset_df=dataset_after_df,
            dataset_path=dataset_path,
        )

        write_performed = True

        if config.create_snapshot_after_write:
            snapshot_path = create_dataset_snapshot(
                dataset_path=dataset_path,
                snapshot_dir=snapshot_dir,
                cycle_id=cycle_id,
            )

    cycle_validation_df = build_cycle_validation_df(
        controller_summary_df=controller_summary_df,
        controller_validation_df=controller_validation_df,
        persistence_summary_df=persistence_summary_df,
        persistence_validation_df=persistence_validation_df,
        dataset_after_df=dataset_after_df,
        dataset_path=dataset_path,
        existing_rows_before=len(existing_dataset_df),
        new_rows_added=new_rows_added,
        updated_rows=updated_rows,
        write_required=write_required,
        write_performed=write_performed,
    )

    cycle_summary_df = build_cycle_summary_df(
        cycle_id=cycle_id,
        controller_summary_df=controller_summary_df,
        persistence_summary_df=persistence_summary_df,
        cycle_validation_df=cycle_validation_df,
        dataset_path=dataset_path,
        backup_path=backup_path,
        snapshot_path=snapshot_path,
        write_required=write_required,
        write_performed=write_performed,
        config=config,
    )

    return (
        cycle_summary_df,
        cycle_validation_df,
        controller_summary_df,
        controller_validation_df,
        persistence_summary_df,
        persistence_validation_df,
        persistence_new_rows_df,
        persistence_updated_rows_df,
        persistence_duplicate_rows_df,
        persistence_invalid_rows_df,
        resolved_closed_df,
        still_open_df,
        dataset_after_df,
    )