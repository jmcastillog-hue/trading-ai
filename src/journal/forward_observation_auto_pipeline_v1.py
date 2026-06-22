from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.journal.forward_observation_candidate_detector_v1 import (
    ForwardObservationCandidateDetectorConfig,
    build_candidate_detector_summary,
    detect_forward_observation_candidates,
)
from src.journal.manual_observation_processor_v1 import (
    ManualObservationProcessorConfig,
    process_manual_observation_file,
)


@dataclass(frozen=True)
class ForwardObservationAutoPipelineConfig:
    duplicate_policy: str = "SKIP"
    min_forward_signals: int = 100
    preferred_forward_signals: int = 300
    max_candidate_theoretical_risk_pct: float = 0.0050
    max_watchlist_theoretical_risk_pct: float = 0.0025
    allow_resolution_from_intake: bool = True
    paper_trade_execution_allowed: bool = False
    real_capital_allowed: bool = False


def save_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def build_processor_config(
    config: ForwardObservationAutoPipelineConfig,
) -> ManualObservationProcessorConfig:
    return ManualObservationProcessorConfig(
        duplicate_policy=config.duplicate_policy,
        create_input_file_if_missing=True,
        min_forward_signals=config.min_forward_signals,
        preferred_forward_signals=config.preferred_forward_signals,
        max_candidate_theoretical_risk_pct=config.max_candidate_theoretical_risk_pct,
        max_watchlist_theoretical_risk_pct=config.max_watchlist_theoretical_risk_pct,
        allow_resolution_from_intake=config.allow_resolution_from_intake,
    )


def build_empty_processor_summary(
    records_path: Path,
    dataset_path: Path,
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "input_path": str(records_path),
                "dataset_path": str(dataset_path),
                "input_rows": 0,
                "new_rows_to_process": 0,
                "skipped_duplicate_rows": 0,
                "accepted_rows": 0,
                "rejected_rows": 0,
                "dataset_rows_after": 0,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "processor_decision": "PROCESSOR_NOT_RUN_NO_GENERATED_RECORDS",
            }
        ]
    )


def build_forward_observation_auto_pipeline_summary(
    source_signals_df: pd.DataFrame,
    records_df: pd.DataFrame,
    detector_accepted_df: pd.DataFrame,
    detector_rejected_df: pd.DataFrame,
    detector_validation_df: pd.DataFrame,
    processor_accepted_df: pd.DataFrame,
    processor_rejected_df: pd.DataFrame,
    skipped_duplicates_df: pd.DataFrame,
    processor_errors_df: pd.DataFrame,
    journal_summary_df: pd.DataFrame,
) -> pd.DataFrame:
    detector_validation_passed = (
        bool(detector_validation_df["passed"].all())
        if not detector_validation_df.empty and "passed" in detector_validation_df.columns
        else False
    )

    source_rows = len(source_signals_df)
    detector_accepted = len(detector_accepted_df)
    detector_rejected = len(detector_rejected_df)
    generated_records = len(records_df)
    processor_accepted = len(processor_accepted_df)
    processor_rejected = len(processor_rejected_df)
    skipped_duplicates = len(skipped_duplicates_df)
    processor_errors = len(processor_errors_df)

    total_signals = 0
    observable_signals = 0
    resolved_signals = 0

    if not journal_summary_df.empty:
        first_row = journal_summary_df.iloc[0]
        total_signals = int(first_row.get("total_signals", 0))
        observable_signals = int(first_row.get("observable_signals", 0))
        resolved_signals = int(first_row.get("resolved_signals", 0))

    if not detector_validation_passed:
        pipeline_decision = "PIPELINE_DETECTOR_INPUT_VALIDATION_FAILED"
    elif generated_records == 0:
        pipeline_decision = "PIPELINE_COMPLETED_NO_GENERATED_RECORDS"
    elif processor_errors > 0:
        pipeline_decision = "PIPELINE_COMPLETED_WITH_PROCESSOR_ERRORS"
    elif processor_rejected > 0:
        pipeline_decision = "PIPELINE_COMPLETED_WITH_PROCESSOR_REJECTIONS"
    elif processor_accepted == generated_records:
        pipeline_decision = "PIPELINE_COMPLETED_ACCEPTED_RECORDS"
    else:
        pipeline_decision = "PIPELINE_REVIEW_REQUIRED"

    return pd.DataFrame(
        [
            {
                "source_rows": source_rows,
                "detector_validation_passed": detector_validation_passed,
                "detector_accepted_candidates": detector_accepted,
                "detector_rejected_candidates": detector_rejected,
                "generated_records": generated_records,
                "processor_accepted_rows": processor_accepted,
                "processor_rejected_rows": processor_rejected,
                "skipped_duplicate_rows": skipped_duplicates,
                "processor_error_rows": processor_errors,
                "journal_total_signals": total_signals,
                "journal_observable_signals": observable_signals,
                "journal_resolved_signals": resolved_signals,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "pipeline_decision": pipeline_decision,
            }
        ]
    )


def run_forward_observation_auto_pipeline(
    source_signals_df: pd.DataFrame,
    phase_template_df: pd.DataFrame,
    records_path: Path,
    dataset_path: Path,
    detector_config: ForwardObservationCandidateDetectorConfig | None = None,
    pipeline_config: ForwardObservationAutoPipelineConfig | None = None,
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
    pd.DataFrame,
]:
    if detector_config is None:
        detector_config = ForwardObservationCandidateDetectorConfig()

    if pipeline_config is None:
        pipeline_config = ForwardObservationAutoPipelineConfig()

    (
        records_df,
        detector_accepted_df,
        detector_rejected_df,
        detector_validation_df,
    ) = detect_forward_observation_candidates(
        signals_df=source_signals_df,
        config=detector_config,
    )

    detector_summary_df = build_candidate_detector_summary(
        records_df=records_df,
        accepted_df=detector_accepted_df,
        rejected_df=detector_rejected_df,
        validation_df=detector_validation_df,
    )

    save_df(records_df, records_path)

    processor_config = build_processor_config(pipeline_config)

    if records_df.empty:
        journal_df = pd.DataFrame()
        processor_accepted_df = pd.DataFrame()
        processor_rejected_df = pd.DataFrame()
        skipped_df = pd.DataFrame()
        validation_summary_df = pd.DataFrame()
        journal_summary_df = pd.DataFrame()
        processor_errors_df = pd.DataFrame()
        processor_summary_df = build_empty_processor_summary(
            records_path=records_path,
            dataset_path=dataset_path,
        )
    else:
        (
            journal_df,
            processor_accepted_df,
            processor_rejected_df,
            skipped_df,
            validation_summary_df,
            journal_summary_df,
            processor_errors_df,
            processor_summary_df,
        ) = process_manual_observation_file(
            input_path=records_path,
            phase_template_df=phase_template_df,
            dataset_path=dataset_path,
            config=processor_config,
        )

    pipeline_summary_df = build_forward_observation_auto_pipeline_summary(
        source_signals_df=source_signals_df,
        records_df=records_df,
        detector_accepted_df=detector_accepted_df,
        detector_rejected_df=detector_rejected_df,
        detector_validation_df=detector_validation_df,
        processor_accepted_df=processor_accepted_df,
        processor_rejected_df=processor_rejected_df,
        skipped_duplicates_df=skipped_df,
        processor_errors_df=processor_errors_df,
        journal_summary_df=journal_summary_df,
    )

    return (
        records_df,
        detector_summary_df,
        detector_validation_df,
        detector_accepted_df,
        detector_rejected_df,
        journal_df,
        processor_accepted_df,
        processor_rejected_df,
        skipped_df,
        validation_summary_df,
        journal_summary_df,
        processor_errors_df,
        processor_summary_df,
        pipeline_summary_df,
    )