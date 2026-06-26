from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class ForwardEvidenceDatasetPersistenceConfig:
    min_forward_observations: int = 100
    preferred_forward_observations: int = 300
    duplicate_key_column: str = "signal_id"
    persistence_source: str = "FORWARD_EVIDENCE_DATASET_PERSISTENCE_V1"
    paper_trade_execution_allowed: bool = False
    real_capital_allowed: bool = False
    live_alerts_allowed: bool = False
    exchange_execution_allowed: bool = False
    automation_allowed: bool = False


CLOSED_RESOLUTION_STATUSES = {
    "TARGET_HIT",
    "STOP_HIT",
    "TIME_EXIT",
    "MANUAL_CLOSE",
}

OPEN_RESOLUTION_STATUSES = {
    "OPEN",
    "OPEN_UNRESOLVED",
    "OPEN_NO_FUTURE_DATA",
}

EXECUTION_FLAG_COLUMNS = [
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "live_alerts_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
]

REQUIRED_PERSISTENCE_COLUMNS = [
    "signal_id",
    "observed_at",
    "symbol",
    "timeframe",
    "cost_profile",
    "context_name",
    "direction",
    "entry_price",
    "stop_price",
    "target_price",
    "resolution_status",
    "result_r",
    "mfe_r",
    "mae_r",
    "bars_to_resolution",
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "live_alerts_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
]


def safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except Exception:
        pass

    return str(value).strip()


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or pd.isna(value):
            return default
        return int(value)
    except Exception:
        return default


def is_true_like(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    text = safe_str(value).lower()

    return text in {"true", "1", "yes", "y", "si", "sí"}


def resolution_category(status: Any) -> str:
    normalized = safe_str(status).upper()

    if normalized in CLOSED_RESOLUTION_STATUSES:
        return "CLOSED"

    if normalized in OPEN_RESOLUTION_STATUSES:
        return "OPEN"

    if normalized.startswith("RESOLUTION_ERROR"):
        return "ERROR"

    if normalized == "":
        return "UNKNOWN"

    return "REVIEW"


def build_readiness_state(
    cumulative_closed_observations: int,
    config: ForwardEvidenceDatasetPersistenceConfig,
) -> str:
    if cumulative_closed_observations >= config.preferred_forward_observations:
        return "PREFERRED_FORWARD_SAMPLE_REACHED_REVIEW_REQUIRED"

    if cumulative_closed_observations >= config.min_forward_observations:
        return "MINIMUM_FORWARD_SAMPLE_REACHED_REVIEW_REQUIRED"

    return "FORWARD_SAMPLE_INSUFFICIENT"


def normalize_evidence_dataset(
    dataset_df: pd.DataFrame | None,
    config: ForwardEvidenceDatasetPersistenceConfig,
) -> pd.DataFrame:
    if dataset_df is None or dataset_df.empty:
        df = pd.DataFrame(columns=REQUIRED_PERSISTENCE_COLUMNS)
    else:
        df = dataset_df.copy()

    for column in REQUIRED_PERSISTENCE_COLUMNS:
        if column not in df.columns:
            df[column] = ""

    for column in [
        "signal_id",
        "observed_at",
        "symbol",
        "timeframe",
        "cost_profile",
        "context_name",
        "direction",
        "resolution_status",
    ]:
        df[column] = df[column].map(lambda value: safe_str(value))

    for column in ["entry_price", "stop_price", "target_price"]:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0.0)

    for column in ["result_r", "mfe_r", "mae_r", "bars_to_resolution"]:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0.0)

    df["symbol"] = df["symbol"].str.upper()
    df["timeframe"] = df["timeframe"].str.lower()
    df["cost_profile"] = df["cost_profile"].str.upper()
    df["context_name"] = df["context_name"].str.upper()
    df["direction"] = df["direction"].str.upper()
    df["resolution_status"] = df["resolution_status"].str.upper()

    for column in EXECUTION_FLAG_COLUMNS:
        df[column] = False

    if "persistence_source" not in df.columns:
        df["persistence_source"] = config.persistence_source

    if "persistence_status" not in df.columns:
        df["persistence_status"] = ""

    if "persistence_note" not in df.columns:
        df["persistence_note"] = ""

    return df


def align_dataset_columns(
    existing_df: pd.DataFrame,
    incoming_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    all_columns = list(dict.fromkeys(list(existing_df.columns) + list(incoming_df.columns)))

    existing_aligned = existing_df.copy()
    incoming_aligned = incoming_df.copy()

    for column in all_columns:
        if column not in existing_aligned.columns:
            existing_aligned[column] = ""

        if column not in incoming_aligned.columns:
            incoming_aligned[column] = ""

    return existing_aligned[all_columns], incoming_aligned[all_columns], all_columns


def should_update_existing_row(existing_row: pd.Series, incoming_row: pd.Series) -> bool:
    existing_category = resolution_category(existing_row.get("resolution_status"))
    incoming_category = resolution_category(incoming_row.get("resolution_status"))

    if existing_category == "OPEN" and incoming_category in {"CLOSED", "ERROR", "REVIEW"}:
        return True

    if existing_category == "ERROR" and incoming_category == "CLOSED":
        return True

    return False


def count_by_resolution_category(dataset_df: pd.DataFrame) -> dict[str, int]:
    if dataset_df.empty or "resolution_status" not in dataset_df.columns:
        return {
            "closed_observations": 0,
            "open_observations": 0,
            "error_observations": 0,
            "review_observations": 0,
        }

    categories = dataset_df["resolution_status"].map(resolution_category)

    return {
        "closed_observations": int((categories == "CLOSED").sum()),
        "open_observations": int((categories == "OPEN").sum()),
        "error_observations": int((categories == "ERROR").sum()),
        "review_observations": int((categories == "REVIEW").sum()),
    }


def all_execution_flags_false(dataset_df: pd.DataFrame) -> bool:
    if dataset_df.empty:
        return True

    for column in EXECUTION_FLAG_COLUMNS:
        if column not in dataset_df.columns:
            return False

        if dataset_df[column].map(is_true_like).any():
            return False

    return True


def validate_persistence_output(
    incoming_df: pd.DataFrame,
    existing_before_df: pd.DataFrame,
    new_rows_df: pd.DataFrame,
    updated_rows_df: pd.DataFrame,
    duplicate_rows_df: pd.DataFrame,
    dataset_after_df: pd.DataFrame,
    config: ForwardEvidenceDatasetPersistenceConfig,
) -> pd.DataFrame:
    rows = []

    for column in REQUIRED_PERSISTENCE_COLUMNS:
        passed = column in dataset_after_df.columns

        rows.append(
            {
                "check_name": f"required_column:{column}",
                "passed": passed,
                "severity": "ERROR" if not passed else "INFO",
                "details": "OK" if passed else "MISSING",
            }
        )

    duplicate_key = config.duplicate_key_column

    rows.append(
        {
            "check_name": "duplicate_key_exists",
            "passed": duplicate_key in dataset_after_df.columns,
            "severity": "ERROR",
            "details": duplicate_key,
        }
    )

    if duplicate_key in dataset_after_df.columns and not dataset_after_df.empty:
        missing_key_count = int(
            dataset_after_df[duplicate_key]
            .map(lambda value: safe_str(value) == "")
            .sum()
        )
        duplicate_key_count = int(dataset_after_df[duplicate_key].duplicated().sum())
    else:
        missing_key_count = 0
        duplicate_key_count = 0

    rows.append(
        {
            "check_name": "no_missing_signal_ids",
            "passed": missing_key_count == 0,
            "severity": "ERROR",
            "details": f"missing_signal_ids={missing_key_count}",
        }
    )

    rows.append(
        {
            "check_name": "no_duplicate_signal_ids_after_persistence",
            "passed": duplicate_key_count == 0,
            "severity": "ERROR",
            "details": f"duplicate_signal_ids={duplicate_key_count}",
        }
    )

    rows.append(
        {
            "check_name": "all_execution_flags_false",
            "passed": all_execution_flags_false(dataset_after_df),
            "severity": "ERROR",
            "details": "persistence must never enable execution flags",
        }
    )

    expected_min_rows = len(existing_before_df) + len(new_rows_df)

    rows.append(
        {
            "check_name": "dataset_row_count_at_least_existing_plus_new",
            "passed": len(dataset_after_df) >= expected_min_rows,
            "severity": "ERROR",
            "details": (
                f"dataset_after={len(dataset_after_df)}, "
                f"existing_before={len(existing_before_df)}, "
                f"new_rows={len(new_rows_df)}, "
                f"updated_rows={len(updated_rows_df)}, "
                f"duplicates={len(duplicate_rows_df)}, "
                f"incoming={len(incoming_df)}"
            ),
        }
    )

    return pd.DataFrame(rows)


def build_persistence_summary_df(
    incoming_df: pd.DataFrame,
    existing_before_df: pd.DataFrame,
    new_rows_df: pd.DataFrame,
    updated_rows_df: pd.DataFrame,
    duplicate_rows_df: pd.DataFrame,
    invalid_rows_df: pd.DataFrame,
    dataset_after_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    config: ForwardEvidenceDatasetPersistenceConfig,
) -> pd.DataFrame:
    validation_passed = (
        bool(validation_df["passed"].all())
        if validation_df is not None and not validation_df.empty and "passed" in validation_df.columns
        else False
    )

    counts = count_by_resolution_category(dataset_after_df)

    wins = 0
    losses = 0
    avg_result_r = 0.0
    sum_result_r = 0.0

    if not dataset_after_df.empty and "result_r" in dataset_after_df.columns:
        closed_mask = dataset_after_df["resolution_status"].map(resolution_category).eq("CLOSED")
        closed_df = dataset_after_df[closed_mask].copy()

        if not closed_df.empty:
            wins = int((closed_df["result_r"] > 0).sum())
            losses = int((closed_df["result_r"] < 0).sum())
            avg_result_r = round(float(closed_df["result_r"].mean()), 6)
            sum_result_r = round(float(closed_df["result_r"].sum()), 6)

    cumulative_closed_observations = counts["closed_observations"]

    readiness_state = build_readiness_state(
        cumulative_closed_observations=cumulative_closed_observations,
        config=config,
    )

    if not validation_passed:
        persistence_decision = "PERSISTENCE_VALIDATION_FAILED"
    elif len(invalid_rows_df) > 0:
        persistence_decision = "PERSISTENCE_COMPLETED_WITH_INVALID_ROWS"
    elif len(new_rows_df) > 0 and len(updated_rows_df) > 0:
        persistence_decision = "PERSISTENCE_COMPLETED_NEW_AND_UPDATED_ROWS"
    elif len(new_rows_df) > 0:
        persistence_decision = "PERSISTENCE_COMPLETED_NEW_ROWS_ADDED"
    elif len(updated_rows_df) > 0:
        persistence_decision = "PERSISTENCE_COMPLETED_EXISTING_ROWS_UPDATED"
    elif len(duplicate_rows_df) > 0:
        persistence_decision = "PERSISTENCE_COMPLETED_DUPLICATES_SKIPPED"
    else:
        persistence_decision = "PERSISTENCE_COMPLETED_NO_ROWS"

    return pd.DataFrame(
        [
            {
                "validation_passed": validation_passed,
                "incoming_rows": len(incoming_df),
                "existing_rows_before": len(existing_before_df),
                "new_rows_added": len(new_rows_df),
                "updated_rows": len(updated_rows_df),
                "duplicate_rows_skipped": len(duplicate_rows_df),
                "invalid_rows": len(invalid_rows_df),
                "dataset_rows_after": len(dataset_after_df),
                "closed_observations": counts["closed_observations"],
                "open_observations": counts["open_observations"],
                "error_observations": counts["error_observations"],
                "review_observations": counts["review_observations"],
                "wins": wins,
                "losses": losses,
                "avg_result_r": avg_result_r,
                "sum_result_r": sum_result_r,
                "cumulative_closed_observations": cumulative_closed_observations,
                "min_forward_observations": config.min_forward_observations,
                "preferred_forward_observations": config.preferred_forward_observations,
                "minimum_sample_reached": cumulative_closed_observations
                >= config.min_forward_observations,
                "preferred_sample_reached": cumulative_closed_observations
                >= config.preferred_forward_observations,
                "sample_gap_to_minimum": max(
                    config.min_forward_observations - cumulative_closed_observations,
                    0,
                ),
                "sample_gap_to_preferred": max(
                    config.preferred_forward_observations - cumulative_closed_observations,
                    0,
                ),
                "readiness_state": readiness_state,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "persistence_decision": persistence_decision,
            }
        ]
    )


def persist_forward_evidence_dataset(
    incoming_dataset_df: pd.DataFrame,
    existing_dataset_df: pd.DataFrame | None = None,
    config: ForwardEvidenceDatasetPersistenceConfig | None = None,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    if config is None:
        config = ForwardEvidenceDatasetPersistenceConfig()

    existing_before_df = normalize_evidence_dataset(existing_dataset_df, config)
    incoming_df = normalize_evidence_dataset(incoming_dataset_df, config)

    existing_before_df, incoming_df, all_columns = align_dataset_columns(
        existing_before_df,
        incoming_df,
    )

    dataset_after_df = existing_before_df.copy()

    duplicate_key = config.duplicate_key_column

    new_rows = []
    updated_rows = []
    duplicate_rows = []
    invalid_rows = []

    seen_incoming_ids: set[str] = set()

    existing_id_to_index = {
        safe_str(row[duplicate_key]): idx
        for idx, row in dataset_after_df.iterrows()
        if safe_str(row.get(duplicate_key)) != ""
    }

    for _, incoming_row in incoming_df.iterrows():
        incoming_id = safe_str(incoming_row.get(duplicate_key))

        if incoming_id == "":
            invalid_row = incoming_row.copy()
            invalid_row["persistence_status"] = "PERSISTENCE_SKIPPED_MISSING_SIGNAL_ID"
            invalid_row["persistence_note"] = "Missing duplicate key"
            invalid_rows.append(invalid_row)
            continue

        if incoming_id in seen_incoming_ids:
            duplicate_row = incoming_row.copy()
            duplicate_row["persistence_status"] = "PERSISTENCE_SKIPPED_DUPLICATE_IN_INCOMING_BATCH"
            duplicate_row["persistence_note"] = "Duplicate signal_id inside incoming batch"
            duplicate_rows.append(duplicate_row)
            continue

        seen_incoming_ids.add(incoming_id)

        incoming_row = incoming_row.copy()
        incoming_row["persistence_source"] = config.persistence_source

        if incoming_id not in existing_id_to_index:
            incoming_row["persistence_status"] = "PERSISTENCE_NEW_ROW_ADDED"
            incoming_row["persistence_note"] = "New evidence row added"

            dataset_after_df = pd.concat(
                [
                    dataset_after_df,
                    pd.DataFrame([incoming_row], columns=all_columns),
                ],
                ignore_index=True,
            )

            existing_id_to_index[incoming_id] = len(dataset_after_df) - 1
            new_rows.append(incoming_row)
            continue

        existing_idx = existing_id_to_index[incoming_id]
        existing_row = dataset_after_df.loc[existing_idx].copy()

        if should_update_existing_row(existing_row, incoming_row):
            incoming_row["persistence_status"] = "PERSISTENCE_EXISTING_ROW_UPDATED"
            incoming_row["persistence_note"] = (
                "Existing open/error evidence row updated with more resolved incoming row"
            )

            for column in all_columns:
                dataset_after_df.at[existing_idx, column] = incoming_row.get(column, "")

            updated_rows.append(incoming_row)
            continue

        duplicate_row = incoming_row.copy()
        duplicate_row["persistence_status"] = "PERSISTENCE_SKIPPED_DUPLICATE_EXISTING_ROW"
        duplicate_row["persistence_note"] = "Signal_id already exists with equal or stronger status"
        duplicate_rows.append(duplicate_row)

    dataset_after_df = normalize_evidence_dataset(dataset_after_df, config)

    new_rows_df = normalize_evidence_dataset(pd.DataFrame(new_rows), config)
    updated_rows_df = normalize_evidence_dataset(pd.DataFrame(updated_rows), config)
    duplicate_rows_df = normalize_evidence_dataset(pd.DataFrame(duplicate_rows), config)
    invalid_rows_df = normalize_evidence_dataset(pd.DataFrame(invalid_rows), config)

    validation_df = validate_persistence_output(
        incoming_df=incoming_df,
        existing_before_df=existing_before_df,
        new_rows_df=new_rows_df,
        updated_rows_df=updated_rows_df,
        duplicate_rows_df=duplicate_rows_df,
        dataset_after_df=dataset_after_df,
        config=config,
    )

    summary_df = build_persistence_summary_df(
        incoming_df=incoming_df,
        existing_before_df=existing_before_df,
        new_rows_df=new_rows_df,
        updated_rows_df=updated_rows_df,
        duplicate_rows_df=duplicate_rows_df,
        invalid_rows_df=invalid_rows_df,
        dataset_after_df=dataset_after_df,
        validation_df=validation_df,
        config=config,
    )

    return (
        summary_df,
        validation_df,
        new_rows_df,
        updated_rows_df,
        duplicate_rows_df,
        invalid_rows_df,
        dataset_after_df,
    )


def read_forward_evidence_dataset(dataset_path: str | Path) -> pd.DataFrame:
    path = Path(dataset_path)

    if not path.exists():
        return pd.DataFrame(columns=REQUIRED_PERSISTENCE_COLUMNS)

    return pd.read_csv(path)


def write_forward_evidence_dataset(
    dataset_df: pd.DataFrame,
    dataset_path: str | Path,
) -> Path:
    path = Path(dataset_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    dataset_df.to_csv(path, index=False)

    return path