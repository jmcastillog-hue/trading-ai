from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.journal.forward_observation_intake_v1 import (
    ForwardObservationIntakeConfig,
    OPTIONAL_RESOLUTION_COLUMNS,
    REQUIRED_INTAKE_COLUMNS,
    process_forward_observation_intake,
)
from src.journal.forward_signal_recorder_v1 import (
    build_record_signal_id,
    load_journal_or_empty,
)


MANUAL_OBSERVATION_COLUMNS = REQUIRED_INTAKE_COLUMNS + OPTIONAL_RESOLUTION_COLUMNS + [
    "data_source",
    "screenshot_path",
]


@dataclass(frozen=True)
class ManualObservationProcessorConfig:
    duplicate_policy: str = "SKIP"
    create_input_file_if_missing: bool = True
    min_forward_signals: int = 100
    preferred_forward_signals: int = 300
    max_candidate_theoretical_risk_pct: float = 0.0050
    max_watchlist_theoretical_risk_pct: float = 0.0025
    allow_resolution_from_intake: bool = True


def load_csv_or_fail(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing required CSV file: {path}")

    return pd.read_csv(path)


def ensure_manual_observation_input_file(
    input_path: Path,
    template_path: Path,
    config: ManualObservationProcessorConfig | None = None,
) -> dict:
    if config is None:
        config = ManualObservationProcessorConfig()

    input_path.parent.mkdir(parents=True, exist_ok=True)

    if input_path.exists():
        return {
            "input_path": str(input_path),
            "template_path": str(template_path),
            "created": False,
            "status": "INPUT_FILE_ALREADY_EXISTS",
        }

    if not config.create_input_file_if_missing:
        return {
            "input_path": str(input_path),
            "template_path": str(template_path),
            "created": False,
            "status": "INPUT_FILE_MISSING_NOT_CREATED",
        }

    if not template_path.exists():
        raise FileNotFoundError(f"Missing manual observation template: {template_path}")

    template_df = pd.read_csv(template_path)

    template_df.head(0).to_csv(input_path, index=False)

    return {
        "input_path": str(input_path),
        "template_path": str(template_path),
        "created": True,
        "status": "INPUT_FILE_CREATED_FROM_TEMPLATE",
    }


def build_signal_id_preview_from_row(row: pd.Series) -> str:
    return build_record_signal_id(
        observed_at=str(row.get("observed_at", "")),
        symbol=str(row.get("symbol", "")),
        timeframe=str(row.get("timeframe", "")),
        cost_profile=str(row.get("cost_profile", "")),
        context_name=str(row.get("context_name", "")),
    )


def add_signal_id_preview(input_df: pd.DataFrame) -> pd.DataFrame:
    df = input_df.copy()

    id_columns = [
        "observed_at",
        "symbol",
        "timeframe",
        "cost_profile",
        "context_name",
    ]

    missing_columns = [column for column in id_columns if column not in df.columns]

    if missing_columns:
        df["signal_id_preview"] = ""
        return df

    df["signal_id_preview"] = df.apply(build_signal_id_preview_from_row, axis=1)

    return df


def get_existing_signal_ids(journal_df: pd.DataFrame) -> set[str]:
    if journal_df.empty:
        return set()

    if "signal_id" not in journal_df.columns:
        return set()

    return set(journal_df["signal_id"].dropna().astype(str).tolist())


def split_new_and_duplicate_observations(
    input_df: pd.DataFrame,
    journal_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if input_df.empty:
        return input_df.copy(), pd.DataFrame()

    existing_signal_ids = get_existing_signal_ids(journal_df)

    preview_df = add_signal_id_preview(input_df)

    if not existing_signal_ids:
        new_df = preview_df.drop(columns=["signal_id_preview"], errors="ignore")
        return new_df, pd.DataFrame()

    duplicate_mask = preview_df["signal_id_preview"].astype(str).isin(existing_signal_ids)

    skipped_df = preview_df.loc[duplicate_mask].copy()
    new_df = preview_df.loc[~duplicate_mask].copy()

    if not skipped_df.empty:
        skipped_df["skip_reason"] = "DUPLICATE_SIGNAL_ID_ALREADY_IN_DATASET"

    new_df = new_df.drop(columns=["signal_id_preview"], errors="ignore")

    return new_df.reset_index(drop=True), skipped_df.reset_index(drop=True)


def build_intake_config(
    config: ManualObservationProcessorConfig,
) -> ForwardObservationIntakeConfig:
    return ForwardObservationIntakeConfig(
        min_forward_signals=config.min_forward_signals,
        preferred_forward_signals=config.preferred_forward_signals,
        max_candidate_theoretical_risk_pct=config.max_candidate_theoretical_risk_pct,
        max_watchlist_theoretical_risk_pct=config.max_watchlist_theoretical_risk_pct,
        allow_resolution_from_intake=config.allow_resolution_from_intake,
    )


def process_manual_observation_file(
    input_path: Path,
    phase_template_df: pd.DataFrame,
    dataset_path: Path,
    config: ManualObservationProcessorConfig | None = None,
) -> tuple[
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
        config = ManualObservationProcessorConfig()

    if not input_path.exists():
        raise FileNotFoundError(f"Missing manual observation input file: {input_path}")

    input_df = pd.read_csv(input_path)

    current_journal_df = load_journal_or_empty(dataset_path)

    new_input_df, skipped_df = split_new_and_duplicate_observations(
        input_df=input_df,
        journal_df=current_journal_df,
    )

    intake_config = build_intake_config(config)

    (
        journal_df,
        accepted_df,
        rejected_df,
        validation_summary_df,
        journal_summary_df,
        errors_df,
    ) = process_forward_observation_intake(
        intake_df=new_input_df,
        template_df=phase_template_df,
        journal_path=dataset_path,
        config=intake_config,
    )

    processor_summary_df = build_processor_summary(
        input_df=input_df,
        new_input_df=new_input_df,
        skipped_df=skipped_df,
        accepted_df=accepted_df,
        rejected_df=rejected_df,
        journal_df=journal_df,
        input_path=input_path,
        dataset_path=dataset_path,
    )

    return (
        journal_df,
        accepted_df,
        rejected_df,
        skipped_df,
        validation_summary_df,
        journal_summary_df,
        errors_df,
        processor_summary_df,
    )


def bool_column_has_true(df: pd.DataFrame, column: str) -> bool:
    if df.empty or column not in df.columns:
        return False

    values = df[column].astype(str).str.strip().str.lower()

    return bool(values.isin(["true", "1", "yes", "y", "si", "sí"]).any())


def build_processor_summary(
    input_df: pd.DataFrame,
    new_input_df: pd.DataFrame,
    skipped_df: pd.DataFrame,
    accepted_df: pd.DataFrame,
    rejected_df: pd.DataFrame,
    journal_df: pd.DataFrame,
    input_path: Path,
    dataset_path: Path,
) -> pd.DataFrame:
    rows = [
        {
            "input_path": str(input_path),
            "dataset_path": str(dataset_path),
            "input_rows": int(len(input_df)),
            "new_rows_to_process": int(len(new_input_df)),
            "skipped_duplicate_rows": int(len(skipped_df)),
            "accepted_rows": int(len(accepted_df)),
            "rejected_rows": int(len(rejected_df)),
            "dataset_rows_after": int(len(journal_df)),
            "paper_trade_execution_allowed": bool_column_has_true(
                journal_df,
                "paper_trade_execution_allowed",
            ),
            "real_capital_allowed": bool_column_has_true(
                journal_df,
                "real_capital_allowed",
            ),
            "processor_decision": classify_processor_result(
                accepted_rows=len(accepted_df),
                rejected_rows=len(rejected_df),
                skipped_rows=len(skipped_df),
                paper_trade_execution_allowed=bool_column_has_true(
                    journal_df,
                    "paper_trade_execution_allowed",
                ),
                real_capital_allowed=bool_column_has_true(
                    journal_df,
                    "real_capital_allowed",
                ),
            ),
        }
    ]

    return pd.DataFrame(rows)


def classify_processor_result(
    accepted_rows: int,
    rejected_rows: int,
    skipped_rows: int,
    paper_trade_execution_allowed: bool,
    real_capital_allowed: bool,
) -> str:
    if paper_trade_execution_allowed or real_capital_allowed:
        return "PROCESSOR_FAILED_EXECUTION_RESTRICTION_BREACH"

    if rejected_rows > 0 and accepted_rows == 0:
        return "PROCESSOR_COMPLETED_ALL_ROWS_REJECTED"

    if accepted_rows > 0 and rejected_rows > 0:
        return "PROCESSOR_COMPLETED_WITH_PARTIAL_REJECTIONS"

    if accepted_rows > 0:
        return "PROCESSOR_COMPLETED_ACCEPTED_ROWS"

    if skipped_rows > 0:
        return "PROCESSOR_COMPLETED_DUPLICATES_SKIPPED"

    return "PROCESSOR_COMPLETED_NO_ROWS_TO_PROCESS"