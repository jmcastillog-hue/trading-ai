from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.journal.manual_observation_processor_v1 import MANUAL_OBSERVATION_COLUMNS


@dataclass(frozen=True)
class SystemForwardObservationCandidate:
    observed_at: str
    symbol: str
    timeframe: str
    cost_profile: str
    context_name: str
    direction: str
    entry_theoretical: float
    stop_theoretical: float
    risk_reward: float = 2.5
    invalidation_level: float | None = None
    invalidation_reason: str = "System-generated structural invalidation level."
    manual_reviewer: str = "SYSTEM_GENERATED_REVIEW_REQUIRED"
    manual_notes: str = "System-generated forward observation. Human review required before interpretation."
    data_source: str = "SYSTEM_FORWARD_OBSERVATION_RECORD_BUILDER_V1"
    screenshot_path: str = ""


def normalize_direction(direction: str) -> str:
    return str(direction).strip().upper()


def calculate_target_theoretical(
    direction: str,
    entry_theoretical: float,
    stop_theoretical: float,
    risk_reward: float,
) -> float:
    direction = normalize_direction(direction)

    entry = float(entry_theoretical)
    stop = float(stop_theoretical)
    rr = float(risk_reward)

    risk_distance = abs(stop - entry)

    if risk_distance <= 0:
        raise ValueError("Risk distance must be greater than zero.")

    if direction == "SHORT":
        return entry - (risk_distance * rr)

    if direction == "LONG":
        return entry + (risk_distance * rr)

    raise ValueError(f"Unsupported direction: {direction}")


def validate_candidate(candidate: SystemForwardObservationCandidate) -> list[dict]:
    errors = []

    direction = normalize_direction(candidate.direction)

    if direction not in {"SHORT", "LONG"}:
        errors.append(
            {
                "severity": "ERROR",
                "field": "direction",
                "message": "Direction must be SHORT or LONG.",
            }
        )

    entry = float(candidate.entry_theoretical)
    stop = float(candidate.stop_theoretical)

    if entry <= 0:
        errors.append(
            {
                "severity": "ERROR",
                "field": "entry_theoretical",
                "message": "Entry must be greater than zero.",
            }
        )

    if stop <= 0:
        errors.append(
            {
                "severity": "ERROR",
                "field": "stop_theoretical",
                "message": "Stop must be greater than zero.",
            }
        )

    if candidate.risk_reward <= 0:
        errors.append(
            {
                "severity": "ERROR",
                "field": "risk_reward",
                "message": "Risk/reward must be greater than zero.",
            }
        )

    if direction == "SHORT" and stop <= entry:
        errors.append(
            {
                "severity": "ERROR",
                "field": "stop_theoretical",
                "message": "For SHORT observations, stop must be above entry.",
            }
        )

    if direction == "LONG" and stop >= entry:
        errors.append(
            {
                "severity": "ERROR",
                "field": "stop_theoretical",
                "message": "For LONG observations, stop must be below entry.",
            }
        )

    return errors


def build_system_forward_observation_record(
    candidate: SystemForwardObservationCandidate,
) -> dict:
    errors = validate_candidate(candidate)

    if errors:
        raise ValueError(f"Invalid system observation candidate: {errors}")

    direction = normalize_direction(candidate.direction)

    target = calculate_target_theoretical(
        direction=direction,
        entry_theoretical=candidate.entry_theoretical,
        stop_theoretical=candidate.stop_theoretical,
        risk_reward=candidate.risk_reward,
    )

    invalidation_level = (
        candidate.invalidation_level
        if candidate.invalidation_level is not None
        else candidate.stop_theoretical
    )

    record = {
        "observed_at": candidate.observed_at,
        "symbol": str(candidate.symbol).strip().upper(),
        "timeframe": str(candidate.timeframe).strip(),
        "cost_profile": str(candidate.cost_profile).strip().upper(),
        "context_name": str(candidate.context_name).strip().upper(),
        "direction": direction,
        "entry_theoretical": float(candidate.entry_theoretical),
        "stop_theoretical": float(candidate.stop_theoretical),
        "target_theoretical": float(target),
        "invalidation_level": float(invalidation_level),
        "invalidation_reason": candidate.invalidation_reason,
        "manual_reviewer": candidate.manual_reviewer,
        "manual_notes": candidate.manual_notes,
        "resolve_now": False,
        "observed_exit": "",
        "exit_reason": "",
        "max_favorable_excursion_r": "",
        "max_adverse_excursion_r": "",
        "bars_to_resolution": "",
        "data_source": candidate.data_source,
        "screenshot_path": candidate.screenshot_path,
    }

    return {column: record.get(column, "") for column in MANUAL_OBSERVATION_COLUMNS}


def build_system_forward_observation_records(
    candidates: list[SystemForwardObservationCandidate],
) -> pd.DataFrame:
    rows = []

    for candidate in candidates:
        rows.append(build_system_forward_observation_record(candidate))

    return pd.DataFrame(rows, columns=MANUAL_OBSERVATION_COLUMNS)


def build_sample_system_forward_observation_candidates() -> list[SystemForwardObservationCandidate]:
    return [
        SystemForwardObservationCandidate(
            observed_at="2026-06-21 03:00:00",
            symbol="BTCUSDT",
            timeframe="15m",
            cost_profile="BINANCE_SCALP_BASE_ESTIMATE",
            context_name="NORMAL_VALIDATION_CONTEXT",
            direction="SHORT",
            entry_theoretical=65000.0,
            stop_theoretical=65500.0,
            risk_reward=2.5,
            invalidation_reason="System SHORT invalidation: stop above pullback structure.",
            manual_notes=(
                "System-generated SHORT observation from candidate context. "
                "No execution. Forward observation only."
            ),
        ),
        SystemForwardObservationCandidate(
            observed_at="2026-06-21 04:00:00",
            symbol="BTCUSDT",
            timeframe="15m",
            cost_profile="QUANTFURY_SWING_BASE_ESTIMATE",
            context_name="WAVE_5_CAUTION_CONTEXT",
            direction="SHORT",
            entry_theoretical=65200.0,
            stop_theoretical=66000.0,
            risk_reward=2.5,
            invalidation_reason="System SHORT invalidation: stop above wave caution structure.",
            manual_notes=(
                "System-generated SHORT observation in wave caution context. "
                "No execution. Human review required."
            ),
        ),
    ]


def validate_system_records_dataframe(records_df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    missing_columns = [
        column for column in MANUAL_OBSERVATION_COLUMNS if column not in records_df.columns
    ]

    rows.append(
        {
            "check_name": "all_required_columns_present",
            "passed": len(missing_columns) == 0,
            "details": ", ".join(missing_columns) if missing_columns else "OK",
        }
    )

    rows.append(
        {
            "check_name": "has_rows",
            "passed": len(records_df) > 0,
            "details": f"rows={len(records_df)}",
        }
    )

    if not records_df.empty and "resolve_now" in records_df.columns:
        resolve_values = records_df["resolve_now"].astype(str).str.lower().tolist()
        rows.append(
            {
                "check_name": "records_are_unresolved_by_default",
                "passed": all(value in {"false", "0"} for value in resolve_values),
                "details": ", ".join(resolve_values),
            }
        )

    if not records_df.empty and "manual_reviewer" in records_df.columns:
        rows.append(
            {
                "check_name": "manual_review_required",
                "passed": bool(
                    records_df["manual_reviewer"]
                    .astype(str)
                    .str.contains("REVIEW_REQUIRED")
                    .all()
                ),
                "details": "manual_reviewer must require review",
            }
        )

    return pd.DataFrame(rows)


def save_system_records(records_df: pd.DataFrame, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    records_df.to_csv(output_path, index=False)
    return output_path