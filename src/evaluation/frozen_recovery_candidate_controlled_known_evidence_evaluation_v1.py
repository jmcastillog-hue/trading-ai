from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import shutil
import sys
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd


PHASE = "10.42R.2K"
SCHEMA_VERSION = "CONTROLLED_KNOWN_EVIDENCE_EVALUATION_V1"
SOURCE_PHASE_2J_COMMIT = "384f032599a75e203ea02f9a8cc6ea6ceda1ed81"
SOURCE_PHASE_2J_BINDING_ROOT_SHA256 = (
    "5c1ccb1c9fecdad2e196558a946944f5b9f89f258c5ef591a65d4c4c480d8c14"
)
SOURCE_PHASE_2H_PROTOCOL_SHA256 = (
    "a42a8da21d1afd231be37376de8ecdfc0306dc8db2375bacb5f2de567947e493"
)
SOURCE_PHASE_2I_HARNESS_DESIGN_SHA256 = (
    "ee62064148bdb119c7b3390d7dab3db338b4d5b50a1eaf7adb44d4c9dffd5dbb"
)
SOURCE_CORRECTED_IMPLEMENTATION_SHA256 = (
    "ccf3cc05823515fa56e9e1183eb51ab903503e310aa037248847ad7445b2cc1e"
)
SOURCE_SPECIFICATION_ROOT_SHA256 = (
    "0872b2bf7355e8a9b35d5b4e0e05d3edf291006862ce9ee5eae847910ef4c015"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_42R_2L_FROZEN_RECOVERY_CANDIDATE_"
    "INDEPENDENT_RESULT_AUDIT_AND_DISPOSITION_V1"
)

REPORTS_ROOT = Path("reports/phase_10_42r_2k")
RUN_ID_PREFIX = "known_evidence_2022_2025_v1"
KNOWN_EVIDENCE_START = pd.Timestamp("2022-01-01T00:00:00Z")
OOS_START = pd.Timestamp("2023-01-01T00:00:00Z")
KNOWN_EVIDENCE_END_EXCLUSIVE = pd.Timestamp("2026-01-01T00:00:00Z")

SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
TIMEFRAMES = ("15m", "1h", "4h")
ALLOWED_BEARISH_REGIMES = frozenset({"BEARISH", "STRONG_BEARISH"})
EXPECTED_REGIME_COMBINATIONS = tuple(
    f"REGIME_1H={one}|REGIME_4H={four}"
    for one in ("BEARISH", "STRONG_BEARISH")
    for four in ("BEARISH", "STRONG_BEARISH")
)
FIXED_REWARD_TO_RISK = 2.5
MAXIMUM_TRADE_BARS = 240
BASE_TIMEFRAME_SECONDS = 900
BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED_BASE = 10_420_200
FAMILY_WISE_ALPHA = 0.05
PRIMARY_COST_PROFILE = "BINANCE_SCALP_BASE_ESTIMATE"
STRESS_COST_PROFILE = "BINANCE_SCALP_STRESS_ESTIMATE"
ACCOUNTING_CONTRACT = "FRICTIONLESS_GROSS_R_TO_SINGLE_PROFILE_NET_R_V1"
DRAWDOWN_ORDER_CONTRACT = (
    "EXIT_TIME_UTC_THEN_ENTRY_TIME_UTC_THEN_SYMBOL_"
    "THEN_SOURCE_TRADE_ROW_ASCENDING"
)
GAP_POLICY = (
    "PRESERVE_DECLARED_SOURCE_GAPS_NO_SYNTHETIC_FILL_"
    "NEXT_OPEN_MUST_BE_CONTIGUOUS_EXIT_SCANS_OBSERVED_BARS"
)

VARIANT_IDS = (
    "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N48_V01",
    "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N96_V02",
    "RCV_SHORT_BREAKDOWN_RETEST_F02_N48_V01",
    "RCV_SHORT_BREAKDOWN_RETEST_F02_N96_V02",
    "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_S000_V01",
    "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_S025_V02",
)
FAMILY_IDS = (
    "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_V1",
    "RCV_SHORT_BREAKDOWN_RETEST_F02_V1",
    "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_V1",
)
VARIANT_FAMILY_MAP = {
    VARIANT_IDS[0]: FAMILY_IDS[0],
    VARIANT_IDS[1]: FAMILY_IDS[0],
    VARIANT_IDS[2]: FAMILY_IDS[1],
    VARIANT_IDS[3]: FAMILY_IDS[1],
    VARIANT_IDS[4]: FAMILY_IDS[2],
    VARIANT_IDS[5]: FAMILY_IDS[2],
}

SPLITS = (
    ("WF_202201_202301_TO_202301_202304", "2023-01-01", "2023-04-01"),
    ("WF_202204_202304_TO_202304_202307", "2023-04-01", "2023-07-01"),
    ("WF_202207_202307_TO_202307_202310", "2023-07-01", "2023-10-01"),
    ("WF_202210_202310_TO_202310_202401", "2023-10-01", "2024-01-01"),
    ("WF_202301_202401_TO_202401_202404", "2024-01-01", "2024-04-01"),
    ("WF_202304_202404_TO_202404_202407", "2024-04-01", "2024-07-01"),
    ("WF_202307_202407_TO_202407_202410", "2024-07-01", "2024-10-01"),
    ("WF_202310_202410_TO_202410_202501", "2024-10-01", "2025-01-01"),
    ("WF_202401_202501_TO_202501_202504", "2025-01-01", "2025-04-01"),
    ("WF_202404_202504_TO_202504_202507", "2025-04-01", "2025-07-01"),
    ("WF_202407_202507_TO_202507_202510", "2025-07-01", "2025-10-01"),
    ("WF_202410_202510_TO_202510_202601", "2025-10-01", "2026-01-01"),
)
SPLIT_IDS = tuple(item[0] for item in SPLITS)

AUDIT_ARTIFACTS = (
    "input_manifest.json",
    "source_anchors.json",
    "environment.json",
    "data_quality.json",
    "signal_ledger.csv",
    "order_ledger.csv",
    "trade_ledger.csv",
    "metric_table.csv",
    "multiplicity_table.csv",
    "gate_classification.csv",
    "check_ledger.csv",
    "run_summary.json",
)

SIGNAL_LEDGER_COLUMNS = (
    "evaluation_order", "family_id", "variant_id", "symbol",
    "signal_bar_index", "signal_time_utc", "split_name",
    "signal_open", "signal_high", "signal_low", "signal_close",
    "signal_atr14", "stop_price", "regime_1h", "regime_4h",
    "trend_regime", "signal_decision",
)
ORDER_LEDGER_COLUMNS = SIGNAL_LEDGER_COLUMNS + (
    "fill_bar_index", "entry_time_utc", "entry_price", "target_price",
    "order_accepted", "order_reason",
)
TRADE_LEDGER_COLUMNS = (
    "evaluation_order", "family_id", "variant_id", "symbol", "split_name",
    "signal_bar_index", "entry_bar_index", "exit_bar_index",
    "signal_time_utc", "entry_time_utc", "exit_time_utc",
    "signal_close", "signal_atr14", "regime_1h", "regime_4h",
    "trend_regime", "entry_price", "stop_price", "target_price",
    "exit_price", "risk_distance", "risk_pct_of_entry",
    "elapsed_trade_bars", "exit_reason", "gap_crossing_count",
    "frictionless_gross_result_r", "result_eligible",
    "invalidation_reason", "position_release_time_utc",
)

PERMISSIONS = {
    "real_data_access_allowed": True,
    "historical_input_binding_allowed": True,
    "historical_file_hashing_allowed": True,
    "historical_schema_parsing_allowed": True,
    "historical_evaluation_allowed": True,
    "performance_metrics_allowed": True,
    "result_artifact_write_allowed": True,
    "retrospective_lockbox_access_allowed": False,
    "prospective_holdout_access_allowed": False,
    "candidate_comparison_allowed": False,
    "candidate_ranking_allowed": False,
    "winner_selection_allowed": False,
    "candidate_mutation_allowed": False,
    "forward_observation_allowed": False,
    "official_dataset_write_allowed": False,
    "signal_generation_enabled": False,
    "live_alerts_allowed": False,
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "market_execution_allowed": False,
    "exchange_execution_allowed": False,
    "automation_allowed": False,
    "execution_allowed": False,
    "openclaw_operational_integration_allowed": False,
}
ALLOWED_TRUE_PERMISSIONS = {
    "real_data_access_allowed",
    "historical_input_binding_allowed",
    "historical_file_hashing_allowed",
    "historical_schema_parsing_allowed",
    "historical_evaluation_allowed",
    "performance_metrics_allowed",
    "result_artifact_write_allowed",
}

FORBIDDEN_ARTIFACT_PATHS = (
    Path("data/holdout/strategy_recovery_retrospective_lockbox_2026h1_v1.csv"),
    Path("data/holdout/strategy_recovery_prospective_20260720_20270120_v1.csv"),
    Path("data/forward/long_forward_observation_dataset_v1.csv"),
)


@dataclass(frozen=True)
class CostProfile:
    profile_order: int
    name: str
    fee_pct_round_trip: float
    spread_pct_round_trip: float
    slippage_pct_round_trip: float
    role: str

    @property
    def total_cost_pct(self) -> float:
        return (
            self.fee_pct_round_trip
            + self.spread_pct_round_trip
            + self.slippage_pct_round_trip
        )


COST_PROFILES = (
    CostProfile(1, PRIMARY_COST_PROFILE, 0.0008, 0.0004, 0.0004, "PRIMARY_BASE_GATE"),
    CostProfile(2, STRESS_COST_PROFILE, 0.0012, 0.0008, 0.0008, "PRIMARY_STRESS_GATE"),
    CostProfile(3, "QUANTFURY_SWING_BASE_ESTIMATE", 0.0, 0.0035, 0.0005, "SECONDARY_DIAGNOSTIC"),
    CostProfile(4, "QUANTFURY_SWING_STRESS_ESTIMATE", 0.0, 0.0060, 0.0010, "SECONDARY_DIAGNOSTIC"),
    CostProfile(5, "EXTREME_COST_STRESS_TEST", 0.0015, 0.0080, 0.0020, "EXTREME_DIAGNOSTIC"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    check_name: str
    passed: bool
    details: str
    blocker: bool


@dataclass(frozen=True)
class SimpleVariantCatalogRow:
    evaluation_order: int
    variant_id: str
    family_id: str


class ControlledEvaluationFailure(RuntimeError):
    pass


def canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_source_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return sha256_bytes(text.encode("utf-8"))


def build_run_id(engine_source_sha256: str) -> str:
    if len(engine_source_sha256) != 64:
        raise ControlledEvaluationFailure("Engine source SHA-256 must be 64 hex characters")
    return (
        f"{RUN_ID_PREFIX}_"
        f"{SOURCE_PHASE_2J_BINDING_ROOT_SHA256[:12]}_"
        f"{engine_source_sha256[:12]}"
    )


def _validate_permissions() -> bool:
    enabled = {name for name, value in PERMISSIONS.items() if value}
    return enabled == ALLOWED_TRUE_PERMISSIONS


def _append_check(
    checks: list[Check],
    name: str,
    passed: bool,
    details: str,
    *,
    blocker: bool | None = None,
) -> None:
    ok = bool(passed)
    checks.append(
        Check(
            check_id=f"2K-CHECK-{len(checks) + 1:03d}",
            check_name=name,
            passed=ok,
            details=str(details),
            blocker=(not ok) if blocker is None else bool(blocker and not ok),
        )
    )


def split_name_for_timestamp(value: pd.Timestamp) -> str:
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize("UTC")
    else:
        timestamp = timestamp.tz_convert("UTC")
    for split_name, start, end in SPLITS:
        if pd.Timestamp(start, tz="UTC") <= timestamp < pd.Timestamp(end, tz="UTC"):
            return split_name
    return ""


def classify_regime_values(
    close: pd.Series,
    ema20: pd.Series,
    ema50: pd.Series,
    ema200: pd.Series,
) -> pd.Series:
    conditions = (
        (close > ema20) & (ema20 > ema50) & (ema50 > ema200),
        (close > ema50) & (ema20 > ema50),
        (close < ema20) & (ema20 < ema50) & (ema50 < ema200),
        (close < ema50) & (ema20 < ema50),
    )
    return pd.Series(
        np.select(
            conditions,
            ("STRONG_BULLISH", "BULLISH", "STRONG_BEARISH", "BEARISH"),
            default="NEUTRAL",
        ),
        index=close.index,
        dtype="object",
    )


def continuity_segment_ids(
    timestamps: pd.Series,
    *,
    expected_duration: pd.Timedelta,
) -> pd.Series:
    parsed = pd.to_datetime(timestamps, errors="coerce", utc=True)
    if parsed.isna().any():
        raise ControlledEvaluationFailure("Continuity timestamps must be complete UTC values")
    discontinuity = parsed.diff().ne(expected_duration)
    if len(discontinuity):
        discontinuity.iloc[0] = True
    return discontinuity.cumsum().astype(int)


def build_regime_features(frame: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    if timeframe not in {"1h", "4h"}:
        raise ControlledEvaluationFailure(f"Unsupported context timeframe: {timeframe}")
    duration = pd.Timedelta(hours=1 if timeframe == "1h" else 4)
    result = frame.loc[:, ["open_time_utc", "close"]].copy()
    result["continuity_segment_id"] = continuity_segment_ids(
        result["open_time_utc"],
        expected_duration=duration,
    )
    grouped = result.groupby("continuity_segment_id", sort=False)["close"]
    for span in (20, 50, 200):
        result[f"ema{span}"] = grouped.transform(
            lambda values, span=span: values.ewm(
                span=span,
                adjust=False,
            ).mean()
        )
    regime = classify_regime_values(
        result["close"], result["ema20"], result["ema50"], result["ema200"]
    )
    continuous_history_rows = result.groupby(
        "continuity_segment_id", sort=False
    ).cumcount() + 1
    regime = regime.where(continuous_history_rows >= 200, "UNKNOWN")
    result[f"regime_{timeframe}"] = regime
    result[f"source_open_time_{timeframe}_utc"] = result["open_time_utc"]
    availability_column = f"feature_available_at_{timeframe}"
    result[availability_column] = result["open_time_utc"] + duration
    return result.loc[
        :,
        [
            availability_column,
            f"source_open_time_{timeframe}_utc",
            f"regime_{timeframe}",
        ],
    ].sort_values(availability_column).reset_index(drop=True)


def attach_closed_mtf_context(
    frame_15m: pd.DataFrame,
    frame_1h: pd.DataFrame,
    frame_4h: pd.DataFrame,
) -> pd.DataFrame:
    result = frame_15m.copy()
    result["signal_close_available_at"] = (
        result["open_time_utc"] + pd.Timedelta(minutes=15)
    )
    one_hour = build_regime_features(frame_1h, "1h")
    four_hour = build_regime_features(frame_4h, "4h")
    result = pd.merge_asof(
        result.sort_values("signal_close_available_at"),
        one_hour,
        left_on="signal_close_available_at",
        right_on="feature_available_at_1h",
        direction="backward",
        allow_exact_matches=True,
    )
    result = pd.merge_asof(
        result.sort_values("signal_close_available_at"),
        four_hour,
        left_on="signal_close_available_at",
        right_on="feature_available_at_4h",
        direction="backward",
        allow_exact_matches=True,
    )
    result["regime_1h"] = result["regime_1h"].fillna("UNKNOWN")
    result["regime_4h"] = result["regime_4h"].fillna("UNKNOWN")
    age_1h = (
        result["signal_close_available_at"] - result["feature_available_at_1h"]
    )
    age_4h = (
        result["signal_close_available_at"] - result["feature_available_at_4h"]
    )
    result["context_1h_fresh"] = age_1h.ge(pd.Timedelta(0)) & age_1h.lt(
        pd.Timedelta(hours=1)
    )
    result["context_4h_fresh"] = age_4h.ge(pd.Timedelta(0)) & age_4h.lt(
        pd.Timedelta(hours=4)
    )
    result["context_allowed"] = (
        result["context_1h_fresh"]
        & result["context_4h_fresh"]
        & result["regime_1h"].isin(ALLOWED_BEARISH_REGIMES)
        & result["regime_4h"].isin(ALLOWED_BEARISH_REGIMES)
    )
    result["trend_regime"] = (
        "REGIME_1H=" + result["regime_1h"].astype(str)
        + "|REGIME_4H=" + result["regime_4h"].astype(str)
    )
    return result.sort_values("open_time_utc").reset_index(drop=True)


def prepare_signal_features(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["continuity_segment_id"] = continuity_segment_ids(
        result["open_time_utc"],
        expected_duration=pd.Timedelta(seconds=BASE_TIMEFRAME_SECONDS),
    )
    group_key = result["continuity_segment_id"]
    previous_close = result.groupby(group_key, sort=False)["close"].shift(1)
    true_range = pd.concat(
        (
            result["high"] - result["low"],
            (result["high"] - previous_close).abs(),
            (result["low"] - previous_close).abs(),
        ),
        axis=1,
    ).max(axis=1)
    result["atr14"] = true_range.groupby(group_key, sort=False).transform(
        lambda values: values.ewm(
            alpha=1.0 / 14.0,
            adjust=False,
            min_periods=14,
        ).mean()
    )
    for span in (20, 50, 200):
        result[f"ema{span}"] = result.groupby(
            group_key, sort=False
        )["close"].transform(
            lambda values, span=span: values.ewm(
                span=span,
                adjust=False,
                min_periods=span,
            ).mean()
        )
    result["ema20_previous"] = result.groupby(
        group_key, sort=False
    )["ema20"].shift(1)
    result["prior_close"] = previous_close
    return result


def _ensure_boolean_array(values: pd.Series | np.ndarray, length: int) -> np.ndarray:
    array = np.asarray(values, dtype=bool)
    if array.shape != (length,):
        raise ControlledEvaluationFailure(f"Boolean array shape mismatch: {array.shape}")
    return array


def build_signal_candidate_arrays(
    frame: pd.DataFrame,
    implementation: Any,
) -> tuple[np.ndarray, np.ndarray]:
    length = len(frame)
    family_id = str(implementation.family_id)
    parameters = dict(implementation.parameters)
    context = frame["context_allowed"].to_numpy(dtype=bool)
    opens = frame["open"].to_numpy(dtype=float)
    highs = frame["high"].to_numpy(dtype=float)
    lows = frame["low"].to_numpy(dtype=float)
    closes = frame["close"].to_numpy(dtype=float)
    atr = frame["atr14"].to_numpy(dtype=float)
    stop = np.full(length, np.nan, dtype=float)

    if family_id == "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_V1":
        lookback = int(parameters["prior_high_lookback_bars"])
        prior_high_series = frame.groupby(
            "continuity_segment_id", sort=False
        )["high"].shift(1)
        prior_high = prior_high_series.groupby(
            frame["continuity_segment_id"], sort=False
        ).transform(
            lambda values: values.rolling(
                lookback, min_periods=lookback
            ).max()
        ).to_numpy(dtype=float)
        body = np.abs(closes - opens)
        upper_wick = highs - np.maximum(opens, closes)
        mask = (
            context
            & np.isfinite(prior_high)
            & np.isfinite(atr)
            & (atr > 0.0)
            & (highs > prior_high)
            & (closes < prior_high)
            & (closes < opens)
            & (body > 0.0)
            & (
                upper_wick
                >= float(parameters["wick_to_body_minimum"]) * body
            )
        )
        stop[mask] = highs[mask] + float(parameters["stop_atr_buffer"]) * atr[mask]
        return _ensure_boolean_array(mask, length), stop

    if family_id == "RCV_SHORT_BREAKDOWN_RETEST_F02_V1":
        lookback = int(parameters["support_lookback_bars"])
        retest_window = int(parameters["retest_window_bars"])
        support_base = frame.groupby(
            "continuity_segment_id", sort=False
        )["low"].shift(1)
        support_series = support_base.groupby(
            frame["continuity_segment_id"], sort=False
        ).transform(
            lambda values: values.rolling(
                lookback, min_periods=lookback
            ).min()
        ).to_numpy(dtype=float)
        breakdown = (
            np.isfinite(support_series)
            & np.isfinite(atr)
            & (atr > 0.0)
            & (
                closes
                < support_series
                - float(parameters["break_atr"]) * atr
            )
        )
        mask = np.zeros(length, dtype=bool)
        tolerance = float(parameters["retest_tolerance_atr"])
        stop_buffer = float(parameters["stop_atr_buffer"])
        for current_index in range(length):
            if not context[current_index] or not np.isfinite(atr[current_index]) or atr[current_index] <= 0.0:
                continue
            first_index = max(0, current_index - retest_window)
            support = math.nan
            for breakdown_index in range(current_index - 1, first_index - 1, -1):
                if (
                    breakdown_index >= 0
                    and frame.at[breakdown_index, "continuity_segment_id"]
                    == frame.at[current_index, "continuity_segment_id"]
                    and breakdown[breakdown_index]
                ):
                    support = float(support_series[breakdown_index])
                    break
            if not math.isfinite(support):
                continue
            passed = bool(
                highs[current_index]
                >= support - tolerance * atr[current_index]
                and closes[current_index] < support
                and closes[current_index] < opens[current_index]
            )
            if passed:
                mask[current_index] = True
                stop[current_index] = (
                    max(highs[current_index], support)
                    + stop_buffer * atr[current_index]
                )
        return mask, stop

    if family_id == "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_V1":
        ema20 = frame["ema20"].to_numpy(dtype=float)
        ema50 = frame["ema50"].to_numpy(dtype=float)
        ema200 = frame["ema200"].to_numpy(dtype=float)
        ema20_previous = frame["ema20_previous"].to_numpy(dtype=float)
        prior_close = frame["prior_close"].to_numpy(dtype=float)
        separation = np.divide(
            ema50 - ema20,
            atr,
            out=np.full(length, np.nan, dtype=float),
            where=np.isfinite(atr) & (atr > 0.0),
        )
        mask = (
            context
            & np.isfinite(ema20)
            & np.isfinite(ema50)
            & np.isfinite(ema200)
            & np.isfinite(ema20_previous)
            & np.isfinite(prior_close)
            & np.isfinite(atr)
            & (atr > 0.0)
            & (ema20 < ema50)
            & (ema50 < ema200)
            & (
                separation
                >= float(parameters["minimum_ema20_ema50_separation_atr"])
            )
            & (prior_close < ema20_previous)
            & (highs >= ema20)
            & (closes < ema20)
            & (closes < opens)
        )
        stop[mask] = highs[mask] + float(parameters["stop_atr_buffer"]) * atr[mask]
        return _ensure_boolean_array(mask, length), stop

    raise ControlledEvaluationFailure(f"Unknown frozen family: {family_id}")


def _resolve_short_trade(
    frame: pd.DataFrame,
    entry_index: int,
    entry_price: float,
    stop_price: float,
    target_price: float,
) -> dict[str, Any]:
    last_index = min(len(frame) - 1, entry_index + MAXIMUM_TRADE_BARS - 1)
    gap_crossing_count = 0
    previous_open = frame.at[entry_index, "open_time_utc"]
    for index in range(entry_index, last_index + 1):
        open_time = frame.at[index, "open_time_utc"]
        if index > entry_index:
            delta = open_time - previous_open
            if delta != pd.Timedelta(seconds=BASE_TIMEFRAME_SECONDS):
                missing_intervals = max(
                    1,
                    int(delta.total_seconds() // BASE_TIMEFRAME_SECONDS) - 1,
                )
                gap_crossing_count += missing_intervals
                previous_index = index - 1
                return {
                    "resolved": False,
                    "exit_index": previous_index,
                    "exit_price": math.nan,
                    "exit_reason": "SOURCE_GAP_CROSSED_OUTCOME_UNOBSERVABLE",
                    "elapsed_trade_bars": max(0, previous_index - entry_index + 1),
                    "gap_crossing_count": gap_crossing_count,
                    "result_eligible": False,
                    "invalidation_reason": (
                        "DECLARED_SOURCE_GAP_CROSSED_BEFORE_OBSERVED_EXIT"
                    ),
                    "position_release_time_utc": (
                        frame.at[entry_index, "open_time_utc"]
                        + pd.Timedelta(
                            seconds=BASE_TIMEFRAME_SECONDS * MAXIMUM_TRADE_BARS
                        )
                    ),
                }
        previous_open = open_time
        high = float(frame.at[index, "high"])
        low = float(frame.at[index, "low"])
        elapsed = index - entry_index + 1
        stop_hit = high >= stop_price
        target_hit = low <= target_price
        if stop_hit:
            return {
                "resolved": True,
                "exit_index": index,
                "exit_price": stop_price,
                "exit_reason": "STOP_FIRST_SIMULTANEOUS" if target_hit else "STOP",
                "elapsed_trade_bars": elapsed,
                "gap_crossing_count": gap_crossing_count,
                "result_eligible": True,
                "invalidation_reason": "",
                "position_release_time_utc": frame.at[index, "close_time_utc"],
            }
        if target_hit:
            return {
                "resolved": True,
                "exit_index": index,
                "exit_price": target_price,
                "exit_reason": "TARGET",
                "elapsed_trade_bars": elapsed,
                "gap_crossing_count": gap_crossing_count,
                "result_eligible": True,
                "invalidation_reason": "",
                "position_release_time_utc": frame.at[index, "close_time_utc"],
            }
        if elapsed == MAXIMUM_TRADE_BARS:
            return {
                "resolved": True,
                "exit_index": index,
                "exit_price": float(frame.at[index, "close"]),
                "exit_reason": "TIME_EXIT",
                "elapsed_trade_bars": elapsed,
                "gap_crossing_count": gap_crossing_count,
                "result_eligible": True,
                "invalidation_reason": "",
                "position_release_time_utc": frame.at[index, "close_time_utc"],
            }
    return {
        "resolved": False,
        "exit_index": last_index,
        "exit_price": math.nan,
        "exit_reason": "RIGHT_CENSORED_OPEN_POSITION",
        "elapsed_trade_bars": max(0, last_index - entry_index + 1),
        "gap_crossing_count": gap_crossing_count,
        "result_eligible": False,
        "invalidation_reason": "INSUFFICIENT_FUTURE_BARS_BEFORE_KNOWN_EVIDENCE_END",
        "position_release_time_utc": KNOWN_EVIDENCE_END_EXCLUSIVE,
    }


def evaluate_variant_on_symbol(
    frame: pd.DataFrame,
    implementation: Any,
    symbol: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    mask, stop_prices = build_signal_candidate_arrays(frame, implementation)
    signal_rows: list[dict[str, Any]] = []
    order_rows: list[dict[str, Any]] = []
    trade_rows: list[dict[str, Any]] = []
    active_until_time = KNOWN_EVIDENCE_START

    signal_indices = np.flatnonzero(mask)
    for signal_index_value in signal_indices:
        signal_index = int(signal_index_value)
        fill_index = signal_index + 1
        if fill_index >= len(frame):
            continue
        entry_time = frame.at[fill_index, "open_time_utc"]
        split_name = split_name_for_timestamp(entry_time)
        if not split_name:
            continue

        signal_time = frame.at[signal_index, "signal_close_available_at"]
        stop_price = float(stop_prices[signal_index])
        base_signal = {
            "evaluation_order": int(implementation.evaluation_order),
            "family_id": str(implementation.family_id),
            "variant_id": str(implementation.variant_id),
            "symbol": symbol,
            "signal_bar_index": signal_index,
            "signal_time_utc": signal_time.isoformat(),
            "split_name": split_name,
            "signal_open": float(frame.at[signal_index, "open"]),
            "signal_high": float(frame.at[signal_index, "high"]),
            "signal_low": float(frame.at[signal_index, "low"]),
            "signal_close": float(frame.at[signal_index, "close"]),
            "signal_atr14": float(frame.at[signal_index, "atr14"]),
            "stop_price": stop_price,
            "regime_1h": str(frame.at[signal_index, "regime_1h"]),
            "regime_4h": str(frame.at[signal_index, "regime_4h"]),
            "trend_regime": str(frame.at[signal_index, "trend_regime"]),
            "signal_decision": "SIGNAL",
        }
        signal_rows.append(base_signal)

        position_open = signal_time < active_until_time
        expected_next_open_time = (
            frame.at[signal_index, "open_time_utc"]
            + pd.Timedelta(seconds=BASE_TIMEFRAME_SECONDS)
        )
        next_open_contiguous = frame.at[fill_index, "open_time_utc"] == expected_next_open_time
        entry_price = float(frame.at[fill_index, "open"])
        if position_open:
            order_rows.append(
                {
                    **base_signal,
                    "fill_bar_index": fill_index,
                    "entry_time_utc": entry_time.isoformat(),
                    "entry_price": entry_price,
                    "target_price": math.nan,
                    "order_accepted": False,
                    "order_reason": "OVERLAPPING_POSITION_BLOCKED",
                }
            )
            continue
        if not next_open_contiguous:
            order_rows.append(
                {
                    **base_signal,
                    "fill_bar_index": fill_index,
                    "entry_time_utc": entry_time.isoformat(),
                    "entry_price": entry_price,
                    "target_price": math.nan,
                    "order_accepted": False,
                    "order_reason": "FILL_NOT_NEXT_15M_OPEN",
                }
            )
            continue
        if not math.isfinite(stop_price) or stop_price <= entry_price:
            order_rows.append(
                {
                    **base_signal,
                    "fill_bar_index": fill_index,
                    "entry_time_utc": entry_time.isoformat(),
                    "entry_price": entry_price,
                    "target_price": math.nan,
                    "order_accepted": False,
                    "order_reason": "INVALID_GAP_STOP_NOT_ABOVE_ENTRY",
                }
            )
            continue

        risk_distance = stop_price - entry_price
        target_price = entry_price - FIXED_REWARD_TO_RISK * risk_distance
        order_rows.append(
            {
                **base_signal,
                "fill_bar_index": fill_index,
                "entry_time_utc": entry_time.isoformat(),
                "entry_price": entry_price,
                "target_price": target_price,
                "order_accepted": True,
                "order_reason": "ORDER_ACCEPTED",
            }
        )
        resolution = _resolve_short_trade(
            frame,
            fill_index,
            entry_price,
            stop_price,
            target_price,
        )
        active_until_time = max(
            active_until_time,
            pd.Timestamp(resolution["position_release_time_utc"]),
        )
        exit_index = int(resolution["exit_index"])
        exit_time = frame.at[exit_index, "close_time_utc"]
        gross_result_r = (
            (entry_price - float(resolution["exit_price"])) / risk_distance
            if resolution["result_eligible"]
            else math.nan
        )
        trade_rows.append(
            {
                "evaluation_order": int(implementation.evaluation_order),
                "family_id": str(implementation.family_id),
                "variant_id": str(implementation.variant_id),
                "symbol": symbol,
                "split_name": split_name,
                "signal_bar_index": signal_index,
                "entry_bar_index": fill_index,
                "exit_bar_index": exit_index,
                "signal_time_utc": signal_time.isoformat(),
                "entry_time_utc": entry_time.isoformat(),
                "exit_time_utc": exit_time.isoformat(),
                "signal_close": float(frame.at[signal_index, "close"]),
                "signal_atr14": float(frame.at[signal_index, "atr14"]),
                "regime_1h": str(frame.at[signal_index, "regime_1h"]),
                "regime_4h": str(frame.at[signal_index, "regime_4h"]),
                "trend_regime": str(frame.at[signal_index, "trend_regime"]),
                "entry_price": entry_price,
                "stop_price": stop_price,
                "target_price": target_price,
                "exit_price": float(resolution["exit_price"]),
                "risk_distance": risk_distance,
                "risk_pct_of_entry": risk_distance / entry_price,
                "elapsed_trade_bars": int(resolution["elapsed_trade_bars"]),
                "exit_reason": str(resolution["exit_reason"]),
                "gap_crossing_count": int(resolution["gap_crossing_count"]),
                "frictionless_gross_result_r": gross_result_r,
                "result_eligible": bool(resolution["result_eligible"]),
                "invalidation_reason": str(resolution["invalidation_reason"]),
                "position_release_time_utc": pd.Timestamp(
                    resolution["position_release_time_utc"]
                ).isoformat(),
            }
        )
    return signal_rows, order_rows, trade_rows


def apply_cost_profiles(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        columns = list(trades.columns) + [
            "cost_profile",
            "profile_total_cost_pct",
            "profile_total_cost_r",
            "normalized_net_result_r",
            "cost_application_count",
        ]
        return pd.DataFrame(columns=columns)
    eligible = trades.loc[trades["result_eligible"].astype(bool)].copy()
    rows: list[pd.DataFrame] = []
    for profile in COST_PROFILES:
        current = eligible.copy()
        current["cost_profile_order"] = profile.profile_order
        current["cost_profile"] = profile.name
        current["profile_role"] = profile.role
        current["profile_total_cost_pct"] = profile.total_cost_pct
        current["profile_total_cost_r"] = (
            profile.total_cost_pct / current["risk_pct_of_entry"].astype(float)
        )
        current["normalized_net_result_r"] = (
            current["frictionless_gross_result_r"].astype(float)
            - current["profile_total_cost_r"].astype(float)
        )
        current["cost_application_count"] = 1
        current["accounting_contract"] = ACCOUNTING_CONTRACT
        rows.append(current)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def calculate_max_drawdown_r(values: Sequence[float]) -> float:
    equity = 0.0
    peak = 0.0
    maximum_drawdown = 0.0
    for raw_value in values:
        value = float(raw_value)
        equity += value
        peak = max(peak, equity)
        maximum_drawdown = min(maximum_drawdown, equity - peak)
    return maximum_drawdown


def profit_factor(values: Sequence[float]) -> float:
    numeric = np.asarray(tuple(float(value) for value in values), dtype=float)
    if numeric.size == 0:
        return 0.0
    gross_profit = float(numeric[numeric > 0.0].sum())
    gross_loss = abs(float(numeric[numeric <= 0.0].sum()))
    if gross_loss == 0.0:
        return 999.0 if gross_profit > 0.0 else 0.0
    return gross_profit / gross_loss


def _window_metrics(
    group: pd.DataFrame,
    symbols: Sequence[str],
    split_names: Sequence[str],
) -> dict[str, Any]:
    index = pd.MultiIndex.from_product(
        [list(symbols), list(split_names)],
        names=["symbol", "split_name"],
    )
    if group.empty:
        windows = pd.DataFrame(index=index, data={"sum": 0.0, "size": 0})
    else:
        observed = group.groupby(
            ["symbol", "split_name"], sort=True, observed=True
        )["normalized_net_result_r"].agg(["sum", "size"])
        unexpected = observed.index.difference(index)
        if len(unexpected):
            raise ControlledEvaluationFailure(
                f"Unexpected configured windows: {list(unexpected)}"
            )
        windows = observed.reindex(index, fill_value=0)
    positive = (windows["size"] > 0) & (windows["sum"] > 0.0)
    return {
        "configured_window_count": int(len(windows)),
        "observed_window_count": int((windows["size"] > 0).sum()),
        "zero_trade_window_count": int((windows["size"] == 0).sum()),
        "positive_window_count": int(positive.sum()),
        "positive_window_rate": float(positive.mean()) if len(windows) else 0.0,
        "minimum_window_trade_count": int(windows["size"].min()) if len(windows) else 0,
        "maximum_window_trade_count": int(windows["size"].max()) if len(windows) else 0,
    }


def _summarize_metric_group(
    group: pd.DataFrame,
    *,
    symbols: Sequence[str],
    split_names: Sequence[str],
) -> dict[str, Any]:
    if group.empty:
        net_values: list[float] = []
        gross_values: list[float] = []
        ordered = group
    else:
        ordered = group.copy()
        ordered["_exit"] = pd.to_datetime(ordered["exit_time_utc"], utc=True)
        ordered["_entry"] = pd.to_datetime(ordered["entry_time_utc"], utc=True)
        ordered = ordered.sort_values(
            ["_exit", "_entry", "symbol", "source_trade_row"],
            kind="stable",
        )
        net_values = ordered["normalized_net_result_r"].astype(float).tolist()
        gross_values = ordered["frictionless_gross_result_r"].astype(float).tolist()
    windows = _window_metrics(group, symbols=symbols, split_names=split_names)
    return {
        "trade_count": len(net_values),
        "normalized_total_result_r": float(sum(net_values)),
        "normalized_average_result_r": (
            float(np.mean(net_values)) if net_values else 0.0
        ),
        "normalized_profit_factor": profit_factor(net_values),
        "normalized_max_drawdown_r": calculate_max_drawdown_r(net_values),
        "frictionless_gross_average_result_r": (
            float(np.mean(gross_values)) if gross_values else 0.0
        ),
        "frictionless_profit_factor": profit_factor(gross_values),
        "drawdown_order_contract": DRAWDOWN_ORDER_CONTRACT,
        **windows,
    }


def assign_trade_features(trades: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, dict[str, float]]]:
    if trades.empty:
        result = trades.copy()
        result["calendar_year"] = pd.Series(dtype=int)
        result["volatility_proxy"] = pd.Series(dtype=float)
        result["volatility_tercile"] = pd.Series(dtype=str)
        return result, {}
    result = trades.copy()
    signal_time = pd.to_datetime(result["signal_time_utc"], utc=True)
    result["calendar_year"] = signal_time.dt.year.astype(int)
    result["volatility_proxy"] = (
        result["signal_atr14"].astype(float) / result["signal_close"].astype(float)
    )
    thresholds: dict[str, dict[str, float]] = {}
    result["volatility_tercile"] = ""
    for variant_id, group in result.groupby("variant_id", sort=False):
        values = group["volatility_proxy"].astype(float)
        if values.empty or not np.isfinite(values.to_numpy()).all() or (values <= 0).any():
            raise ControlledEvaluationFailure(
                f"Invalid volatility proxy for {variant_id}"
            )
        lower = float(values.quantile(1.0 / 3.0, interpolation="linear"))
        upper = float(values.quantile(2.0 / 3.0, interpolation="linear"))
        if not math.isfinite(lower) or not math.isfinite(upper) or lower > upper:
            raise ControlledEvaluationFailure(
                f"Invalid volatility thresholds for {variant_id}"
            )
        thresholds[str(variant_id)] = {"lower": lower, "upper": upper}
        labels = np.select(
            (values <= lower, values <= upper),
            ("LOW", "MID"),
            default="HIGH",
        )
        result.loc[group.index, "volatility_tercile"] = labels
    return result, thresholds


def build_metric_table(normalized: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "evaluation_order",
        "variant_id",
        "family_id",
        "cost_profile",
        "slice_dimension",
        "slice_value",
        "trade_count",
        "normalized_total_result_r",
        "normalized_average_result_r",
        "normalized_profit_factor",
        "normalized_max_drawdown_r",
        "frictionless_gross_average_result_r",
        "frictionless_profit_factor",
        "configured_window_count",
        "observed_window_count",
        "zero_trade_window_count",
        "positive_window_count",
        "positive_window_rate",
        "minimum_window_trade_count",
        "maximum_window_trade_count",
        "drawdown_order_contract",
    ]
    rows: list[dict[str, Any]] = []
    variant_catalog = tuple(
        SimpleVariantCatalogRow(
            evaluation_order=evaluation_order,
            variant_id=variant_id,
            family_id=VARIANT_FAMILY_MAP[variant_id],
        )
        for evaluation_order, variant_id in enumerate(VARIANT_IDS, start=1)
    )
    slice_specs = (
        ("AGGREGATE", None),
        ("SYMBOL", "symbol"),
        ("CALENDAR_YEAR", "calendar_year"),
        ("VOLATILITY_TERCILE", "volatility_tercile"),
        ("CLOSED_MTF_TREND_REGIME", "trend_regime"),
        ("SIGNAL_FAMILY", "family_id"),
    )
    for variant in variant_catalog:
        variant_frame = normalized.loc[
            normalized["variant_id"].eq(variant.variant_id)
        ]
        for profile in COST_PROFILES:
            profile_frame = variant_frame.loc[
                variant_frame["cost_profile"].eq(profile.name)
            ]
            for dimension, column in slice_specs:
                if column is None:
                    groups: Iterable[tuple[str, pd.DataFrame]] = (
                        ("ALL", profile_frame),
                    )
                else:
                    expected_values: Sequence[Any]
                    if column == "symbol":
                        expected_values = SYMBOLS
                    elif column == "calendar_year":
                        expected_values = (2023, 2024, 2025)
                    elif column == "volatility_tercile":
                        expected_values = ("LOW", "MID", "HIGH")
                    elif column == "trend_regime":
                        expected_values = EXPECTED_REGIME_COMBINATIONS
                    elif column == "family_id":
                        expected_values = (variant.family_id,)
                    else:
                        expected_values = tuple(
                            sorted(profile_frame[column].dropna().unique())
                        )
                    groups = tuple(
                        (
                            str(value),
                            profile_frame.loc[profile_frame[column].eq(value)],
                        )
                        for value in expected_values
                    )
                for value, group in groups:
                    selected_symbols = (
                        (value,) if dimension == "SYMBOL" else SYMBOLS
                    )
                    selected_splits = SPLIT_IDS
                    if dimension == "CALENDAR_YEAR":
                        selected_splits = tuple(
                            split_name
                            for split_name, start, _ in SPLITS
                            if int(start[:4]) == int(value)
                        )
                    summary = _summarize_metric_group(
                        group,
                        symbols=selected_symbols,
                        split_names=selected_splits,
                    )
                    rows.append(
                        {
                            "evaluation_order": int(variant.evaluation_order),
                            "variant_id": str(variant.variant_id),
                            "family_id": str(variant.family_id),
                            "cost_profile": profile.name,
                            "slice_dimension": dimension,
                            "slice_value": value,
                            **summary,
                        }
                    )
    return pd.DataFrame(rows, columns=columns).sort_values(
        [
            "evaluation_order",
            "cost_profile",
            "slice_dimension",
            "slice_value",
        ],
        kind="stable",
    ).reset_index(drop=True)


def cluster_bootstrap_p_value(
    normalized_primary: pd.DataFrame,
    *,
    evaluation_order: int,
    resamples: int = BOOTSTRAP_RESAMPLES,
) -> tuple[float, float]:
    if resamples <= 0:
        raise ControlledEvaluationFailure("Bootstrap resamples must be positive")
    values = normalized_primary["normalized_net_result_r"].astype(float)
    observed = float(values.mean()) if len(values) else 0.0
    cluster_index = pd.MultiIndex.from_product(
        [SYMBOLS, SPLIT_IDS], names=["symbol", "split_name"]
    )
    if normalized_primary.empty:
        cluster_sum = pd.Series(0.0, index=cluster_index)
        cluster_count = pd.Series(0, index=cluster_index)
    else:
        grouped = normalized_primary.groupby(
            ["symbol", "split_name"], sort=True, observed=True
        )["normalized_net_result_r"].agg(["sum", "size"])
        cluster_sum = grouped["sum"].reindex(cluster_index, fill_value=0.0)
        cluster_count = grouped["size"].reindex(cluster_index, fill_value=0)
    centered_sum = cluster_sum.to_numpy(dtype=float) - (
        cluster_count.to_numpy(dtype=float) * observed
    )
    counts = cluster_count.to_numpy(dtype=int)
    rng = np.random.default_rng(BOOTSTRAP_SEED_BASE + int(evaluation_order))
    draws = rng.integers(0, len(cluster_index), size=(resamples, len(cluster_index)))
    replicate_sums = centered_sum[draws].sum(axis=1)
    replicate_counts = counts[draws].sum(axis=1)
    replicate_statistics = np.divide(
        replicate_sums,
        replicate_counts,
        out=np.zeros(resamples, dtype=float),
        where=replicate_counts > 0,
    )
    p_value = (1.0 + float((replicate_statistics >= observed).sum())) / (
        float(resamples) + 1.0
    )
    return observed, p_value


def holm_adjust_p_values(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(
        (dict(row) for row in rows),
        key=lambda row: (float(row["unadjusted_p_value"]), int(row["evaluation_order"])),
    )
    total = len(ordered)
    running_adjusted = 0.0
    rejection_open = True
    for rank, row in enumerate(ordered, start=1):
        unadjusted = float(row["unadjusted_p_value"])
        adjusted_raw = min(1.0, (total - rank + 1) * unadjusted)
        running_adjusted = max(running_adjusted, adjusted_raw)
        row["holm_rank"] = rank
        row["holm_adjusted_p_value"] = min(1.0, running_adjusted)
        threshold = FAMILY_WISE_ALPHA / (total - rank + 1)
        row["holm_step_threshold"] = threshold
        current_reject = bool(rejection_open and unadjusted <= threshold)
        row["holm_step_reject"] = current_reject
        if not current_reject:
            rejection_open = False
    return sorted(ordered, key=lambda row: int(row["evaluation_order"]))


def build_multiplicity_table(normalized: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    catalog = tuple(
        SimpleVariantCatalogRow(
            evaluation_order=evaluation_order,
            variant_id=variant_id,
            family_id=VARIANT_FAMILY_MAP[variant_id],
        )
        for evaluation_order, variant_id in enumerate(VARIANT_IDS, start=1)
    )
    for variant in catalog:
        primary = normalized.loc[
            normalized["variant_id"].eq(variant.variant_id)
            & normalized["cost_profile"].eq(PRIMARY_COST_PROFILE)
        ]
        observed, p_value = cluster_bootstrap_p_value(
            primary,
            evaluation_order=int(variant.evaluation_order),
        )
        rows.append(
            {
                "evaluation_order": int(variant.evaluation_order),
                "variant_id": str(variant.variant_id),
                "family_id": str(variant.family_id),
                "primary_cost_profile": PRIMARY_COST_PROFILE,
                "observed_average_net_r": observed,
                "trade_count": int(len(primary)),
                "cluster_count": 36,
                "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
                "bootstrap_seed": BOOTSTRAP_SEED_BASE + int(variant.evaluation_order),
                "unadjusted_p_value": p_value,
                "p_value_method": (
                    "CENTERED_SYMBOL_WINDOW_CLUSTER_BOOTSTRAP_EXPECTANCY_V1"
                ),
                "multiplicity_method": (
                    "HOLM_BONFERRONI_FWER_OVER_ALL_FROZEN_VARIANTS_V1"
                ),
            }
        )
    adjusted = holm_adjust_p_values(rows)
    return pd.DataFrame(adjusted).sort_values("evaluation_order").reset_index(drop=True)


def _metric_row(
    metric_table: pd.DataFrame,
    variant_id: str,
    profile: str,
    dimension: str,
    value: str,
) -> pd.Series:
    rows = metric_table.loc[
        metric_table["variant_id"].eq(variant_id)
        & metric_table["cost_profile"].eq(profile)
        & metric_table["slice_dimension"].eq(dimension)
        & metric_table["slice_value"].astype(str).eq(str(value))
    ]
    if len(rows) != 1:
        raise ControlledEvaluationFailure(
            f"Expected one metric row: {variant_id}/{profile}/{dimension}/{value}"
        )
    return rows.iloc[0]


def build_gate_classification(
    metric_table: pd.DataFrame,
    multiplicity_table: pd.DataFrame,
    trades: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for variant_id in VARIANT_IDS:
        aggregate_base = _metric_row(
            metric_table, variant_id, PRIMARY_COST_PROFILE, "AGGREGATE", "ALL"
        )
        aggregate_stress = _metric_row(
            metric_table, variant_id, STRESS_COST_PROFILE, "AGGREGATE", "ALL"
        )
        symbol_rows = metric_table.loc[
            metric_table["variant_id"].eq(variant_id)
            & metric_table["cost_profile"].eq(PRIMARY_COST_PROFILE)
            & metric_table["slice_dimension"].eq("SYMBOL")
        ]
        year_rows = metric_table.loc[
            metric_table["variant_id"].eq(variant_id)
            & metric_table["cost_profile"].eq(PRIMARY_COST_PROFILE)
            & metric_table["slice_dimension"].eq("CALENDAR_YEAR")
        ]
        volatility_rows = metric_table.loc[
            metric_table["variant_id"].eq(variant_id)
            & metric_table["cost_profile"].eq(PRIMARY_COST_PROFILE)
            & metric_table["slice_dimension"].eq("VOLATILITY_TERCILE")
        ]
        regime_rows = metric_table.loc[
            metric_table["variant_id"].eq(variant_id)
            & metric_table["cost_profile"].eq(PRIMARY_COST_PROFILE)
            & metric_table["slice_dimension"].eq("CLOSED_MTF_TREND_REGIME")
        ]
        multiplicity = multiplicity_table.loc[
            multiplicity_table["variant_id"].eq(variant_id)
        ].iloc[0]
        variant_trades = trades.loc[trades["variant_id"].eq(variant_id)]
        unresolved_count = int((~variant_trades["result_eligible"].astype(bool)).sum())

        stability_checks = {
            "base_positive_window_rate_at_least_0_50": (
                float(aggregate_base["positive_window_rate"]) >= 0.50
            ),
            "stress_positive_window_rate_at_least_0_45": (
                float(aggregate_stress["positive_window_rate"]) >= 0.45
            ),
            "volatility_terciles_nonempty_nonnegative": bool(
                len(volatility_rows) == 3
                and (volatility_rows["trade_count"].astype(int) > 0).all()
                and (
                    volatility_rows["normalized_average_result_r"].astype(float)
                    >= 0.0
                ).all()
            ),
            "all_four_closed_mtf_regimes_nonempty_nonnegative": bool(
                len(regime_rows) == 4
                and (regime_rows["trade_count"].astype(int) > 0).all()
                and (
                    regime_rows["normalized_average_result_r"].astype(float)
                    >= 0.0
                ).all()
            ),
            "five_cost_profiles_published": bool(
                metric_table.loc[
                    metric_table["variant_id"].eq(variant_id)
                    & metric_table["slice_dimension"].eq("AGGREGATE")
                ]["cost_profile"].nunique()
                == 5
            ),
            "no_unresolved_or_invalidated_trade": unresolved_count == 0,
        }

        gate_values = (
            (
                "GATE_001",
                "aggregate_trade_count",
                ">=",
                100,
                int(aggregate_base["trade_count"]),
                int(aggregate_base["trade_count"]) >= 100,
            ),
            (
                "GATE_002",
                "trade_count_each_symbol",
                ">=",
                20,
                int(symbol_rows["trade_count"].astype(int).min()),
                bool(
                    len(symbol_rows) == 3
                    and (symbol_rows["trade_count"].astype(int) >= 20).all()
                ),
            ),
            (
                "GATE_003",
                "binance_base_profit_factor",
                ">=",
                1.05,
                float(aggregate_base["normalized_profit_factor"]),
                float(aggregate_base["normalized_profit_factor"]) >= 1.05,
            ),
            (
                "GATE_004",
                "binance_base_expectancy_aggregate",
                ">",
                0.0,
                float(aggregate_base["normalized_average_result_r"]),
                float(aggregate_base["normalized_average_result_r"]) > 0.0,
            ),
            (
                "GATE_005",
                "binance_base_expectancy_each_symbol",
                ">",
                0.0,
                float(symbol_rows["normalized_average_result_r"].astype(float).min()),
                bool(
                    len(symbol_rows) == 3
                    and (
                        symbol_rows["normalized_average_result_r"].astype(float)
                        > 0.0
                    ).all()
                ),
            ),
            (
                "GATE_006",
                "binance_base_expectancy_each_year",
                ">=",
                0.0,
                float(year_rows["normalized_average_result_r"].astype(float).min()),
                bool(
                    len(year_rows) == 3
                    and (
                        year_rows["normalized_average_result_r"].astype(float)
                        >= 0.0
                    ).all()
                ),
            ),
            (
                "GATE_007",
                "binance_stress_expectancy",
                ">=",
                0.0,
                float(aggregate_stress["normalized_average_result_r"]),
                float(aggregate_stress["normalized_average_result_r"]) >= 0.0,
            ),
            (
                "GATE_008",
                "binance_stress_profit_factor",
                ">=",
                1.0,
                float(aggregate_stress["normalized_profit_factor"]),
                float(aggregate_stress["normalized_profit_factor"]) >= 1.0,
            ),
            (
                "GATE_009",
                "holm_adjusted_p_value",
                "<=",
                0.05,
                float(multiplicity["holm_adjusted_p_value"]),
                float(multiplicity["holm_adjusted_p_value"]) <= 0.05,
            ),
            (
                "GATE_010",
                "all_predeclared_stability_slices",
                "==",
                "NON_FAILING",
                canonical_json(stability_checks),
                all(stability_checks.values()),
            ),
        )
        all_passed = all(bool(item[5]) for item in gate_values)
        for gate_order, item in enumerate(gate_values, start=1):
            gate_id, metric, operator, threshold, observed, passed = item
            rows.append(
                {
                    "evaluation_order": int(multiplicity["evaluation_order"]),
                    "variant_id": variant_id,
                    "gate_order": gate_order,
                    "gate_id": gate_id,
                    "metric": metric,
                    "operator": operator,
                    "threshold": threshold,
                    "observed": observed,
                    "passed": bool(passed),
                    "mandatory": True,
                    "override_allowed": False,
                    "variant_gate_classification": (
                        "ALL_GATES_PASSED_KNOWN_EVIDENCE_ONLY"
                        if all_passed
                        else "ONE_OR_MORE_GATES_FAILED_KNOWN_EVIDENCE_ONLY"
                    ),
                    "ranking_allowed": False,
                    "winner_selection_allowed": False,
                    "operational_approval_allowed": False,
                }
            )
    return pd.DataFrame(rows).sort_values(
        ["evaluation_order", "gate_order"]
    ).reset_index(drop=True)


def _load_frozen_implementations() -> tuple[Any, ...]:
    from src.analysis import frozen_recovery_candidate_implementation_v2 as v2

    implementations = tuple(v2.build_verified_implementations())
    if tuple(item.variant_id for item in implementations) != VARIANT_IDS:
        raise ControlledEvaluationFailure("Frozen implementation registry order mismatch")
    if any(
        item.specification_root_sha256 != SOURCE_SPECIFICATION_ROOT_SHA256
        for item in implementations
    ):
        raise ControlledEvaluationFailure("Frozen specification root mismatch")
    return implementations


def _load_dataset(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    expected_columns = (
        "open_time_utc",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time_utc",
    )
    if tuple(frame.columns) != expected_columns:
        raise ControlledEvaluationFailure(
            f"Dataset schema mismatch for {path}: {tuple(frame.columns)}"
        )
    frame["open_time_utc"] = pd.to_datetime(
        frame["open_time_utc"], errors="coerce", utc=True
    )
    frame["close_time_utc"] = pd.to_datetime(
        frame["close_time_utc"], errors="coerce", utc=True
    )
    for column in ("open", "high", "low", "close", "volume"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    if frame.isna().any(axis=None):
        raise ControlledEvaluationFailure(f"Dataset contains invalid values: {path}")
    if not frame["open_time_utc"].is_monotonic_increasing:
        raise ControlledEvaluationFailure(f"Dataset timestamps not increasing: {path}")
    return frame


def _read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _write_csv(path: Path, frame: pd.DataFrame) -> None:
    frame.to_csv(
        path,
        index=False,
        encoding="utf-8",
        lineterminator="\n",
        float_format="%.15g",
    )


def _artifact_hashes(directory: Path, names: Sequence[str]) -> dict[str, str]:
    return {name: sha256_file(directory / name) for name in names}


def _atomic_publish_bundle(temp_dir: Path, final_dir: Path) -> str:
    if final_dir.exists():
        expected_names = sorted(path.name for path in temp_dir.iterdir() if path.is_file())
        actual_names = sorted(path.name for path in final_dir.iterdir() if path.is_file())
        if expected_names != actual_names:
            raise ControlledEvaluationFailure(
                "Existing deterministic run directory has a different artifact inventory"
            )
        for name in expected_names:
            if sha256_file(temp_dir / name) != sha256_file(final_dir / name):
                raise ControlledEvaluationFailure(
                    f"Existing deterministic run artifact differs: {name}"
                )
        shutil.rmtree(temp_dir)
        return "IDEMPOTENT_EXISTING_BUNDLE_VERIFIED"
    final_dir.parent.mkdir(parents=True, exist_ok=True)
    temp_dir.rename(final_dir)
    return "NEW_BUNDLE_ATOMICALLY_PUBLISHED"


def run_controlled_known_evidence_evaluation(
    *,
    root: Path | None = None,
    write_outputs: bool = True,
    progress: bool = False,
) -> dict[str, Any]:
    project_root = (root or Path.cwd()).resolve()
    checks: list[Check] = []

    def emit(message: str) -> None:
        if progress:
            print(message, flush=True)

    emit(f"phase={PHASE}")
    emit(f"schema_version={SCHEMA_VERSION}")
    emit("evaluation_scope=KNOWN_EVIDENCE_2023_2025_WITH_2022_WARMUP")
    emit("lockbox_access_allowed=False")
    emit("ranking_allowed=False")
    emit("winner_selection_allowed=False")

    from src.validation import (
        frozen_recovery_candidate_historical_input_manifest_binding_and_integrity_validation_v1
        as phase_2j,
    )

    binding_validation = phase_2j.validate_phase_10_42r_2j(
        preflight_only=False,
        root=project_root,
    )
    _append_check(
        checks,
        "phase_2j_binding_validation_passed",
        bool(binding_validation["summary"]["validation_passed"]),
        binding_validation["summary"]["validation_decision"],
    )
    _append_check(
        checks,
        "phase_2j_binding_root_exact",
        phase_2j.BINDING_ROOT_SHA256 == SOURCE_PHASE_2J_BINDING_ROOT_SHA256,
        phase_2j.BINDING_ROOT_SHA256,
    )
    _append_check(
        checks,
        "permissions_exact",
        _validate_permissions(),
        canonical_json({name: value for name, value in PERMISSIONS.items() if value}),
    )
    existing_forbidden = [
        path.as_posix()
        for path in FORBIDDEN_ARTIFACT_PATHS
        if (project_root / path).exists()
    ]
    _append_check(
        checks,
        "lockboxes_and_forward_dataset_absent",
        not existing_forbidden,
        ",".join(existing_forbidden),
    )

    pre_evaluation_blockers = [check for check in checks if check.blocker]
    if pre_evaluation_blockers:
        raise ControlledEvaluationFailure(
            "Pre-evaluation integrity checks failed: "
            + ",".join(check.check_name for check in pre_evaluation_blockers)
        )

    engine_path = project_root / (
        "src/evaluation/frozen_recovery_candidate_controlled_"
        "known_evidence_evaluation_v1.py"
    )
    engine_hash = normalized_source_sha256(engine_path)
    run_id = build_run_id(engine_hash)
    final_dir = project_root / REPORTS_ROOT / run_id

    implementations = _load_frozen_implementations()
    expected_datasets = phase_2j.EXPECTED_DATASETS
    input_manifest_rows = _read_csv_dicts(project_root / phase_2j.MANIFEST_PATH)
    provenance_rows = _read_csv_dicts(project_root / phase_2j.PROVENANCE_PATH)
    gap_rows = _read_csv_dicts(project_root / phase_2j.MISSING_INTERVAL_LEDGER_PATH)

    data_quality: dict[str, Any] = {
        "gap_policy": GAP_POLICY,
        "synthetic_gap_fill_count": 0,
        "declared_source_missing_interval_count": len(gap_rows),
        "slots": [],
    }
    all_signals: list[dict[str, Any]] = []
    all_orders: list[dict[str, Any]] = []
    all_trades: list[dict[str, Any]] = []
    evaluated_symbols: set[str] = set()

    for symbol in SYMBOLS:
        emit(f"symbol_start={symbol}")
        paths = {
            timeframe: project_root
            / expected_datasets[
                f"{symbol}_{timeframe.upper()}_KNOWN_EVIDENCE_2022_2025"
            ]["relative_path"]
            for timeframe in TIMEFRAMES
        }
        frames = {timeframe: _load_dataset(path) for timeframe, path in paths.items()}
        context = attach_closed_mtf_context(
            frames["15m"], frames["1h"], frames["4h"]
        )
        featured = prepare_signal_features(context)
        data_quality["slots"].extend(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "relative_path": paths[timeframe].relative_to(project_root).as_posix(),
                "file_sha256": sha256_file(paths[timeframe]),
                "row_count": int(len(frames[timeframe])),
                "first_open_time_utc": frames[timeframe]["open_time_utc"].iloc[0].isoformat(),
                "last_close_time_utc": frames[timeframe]["close_time_utc"].iloc[-1].isoformat(),
                "declared_missing_interval_count": int(
                    expected_datasets[
                        f"{symbol}_{timeframe.upper()}_KNOWN_EVIDENCE_2022_2025"
                    ]["missing_interval_count"]
                ),
            }
            for timeframe in TIMEFRAMES
        )
        for implementation in implementations:
            signals, orders, trades = evaluate_variant_on_symbol(
                featured,
                implementation,
                symbol,
            )
            all_signals.extend(signals)
            all_orders.extend(orders)
            all_trades.extend(trades)
            emit(
                "variant_symbol_completed="
                + canonical_json(
                    {
                        "symbol": symbol,
                        "evaluation_order": int(implementation.evaluation_order),
                        "variant_id": str(implementation.variant_id),
                        "signal_rows": len(signals),
                        "order_rows": len(orders),
                        "trade_rows": len(trades),
                    }
                )
            )
        evaluated_symbols.add(symbol)
        emit(f"symbol_completed={symbol}")

    emit("metric_aggregation_started=True")
    signal_ledger = pd.DataFrame(all_signals, columns=SIGNAL_LEDGER_COLUMNS)
    order_ledger = pd.DataFrame(all_orders, columns=ORDER_LEDGER_COLUMNS)
    trade_ledger = pd.DataFrame(all_trades, columns=TRADE_LEDGER_COLUMNS)
    trade_ledger = trade_ledger.sort_values(
        ["evaluation_order", "symbol", "entry_time_utc", "signal_bar_index"],
        kind="stable",
    ).reset_index(drop=True)
    trade_ledger["source_trade_row"] = trade_ledger.groupby(
        "variant_id", sort=False
    ).cumcount()
    trade_ledger, volatility_thresholds = assign_trade_features(trade_ledger)
    normalized = apply_cost_profiles(trade_ledger)
    metric_table = build_metric_table(normalized)
    multiplicity_table = build_multiplicity_table(normalized)
    gate_classification = build_gate_classification(
        metric_table,
        multiplicity_table,
        trade_ledger,
    )
    emit("metric_aggregation_completed=True")

    _append_check(checks, "six_variants_evaluated", len(implementations) == 6, str(len(implementations)))
    _append_check(
        checks,
        "three_symbols_evaluated",
        evaluated_symbols == set(SYMBOLS),
        canonical_json(sorted(evaluated_symbols)),
    )
    published_profiles = int(metric_table["cost_profile"].nunique())
    _append_check(
        checks,
        "all_five_cost_profiles_published",
        published_profiles == 5,
        str(published_profiles),
    )
    _append_check(checks, "cost_applied_exactly_once", normalized["cost_application_count"].eq(1).all(), str(len(normalized)))
    _append_check(checks, "no_synthetic_gap_fill", data_quality["synthetic_gap_fill_count"] == 0, "0")
    _append_check(checks, "multiplicity_six_rows", len(multiplicity_table) == 6, str(len(multiplicity_table)))
    _append_check(checks, "gate_rows_sixty", len(gate_classification) == 60, str(len(gate_classification)))
    _append_check(checks, "ranking_and_winner_disabled", not PERMISSIONS["candidate_ranking_allowed"] and not PERMISSIONS["winner_selection_allowed"], "false/false")

    failed_checks = [check for check in checks if not check.passed]
    blocker_count = sum(1 for check in checks if check.blocker)
    check_ledger = pd.DataFrame(asdict(check) for check in checks)

    source_anchors = {
        "phase": PHASE,
        "schema_version": SCHEMA_VERSION,
        "source_phase_2j_commit": SOURCE_PHASE_2J_COMMIT,
        "source_phase_2j_binding_root_sha256": SOURCE_PHASE_2J_BINDING_ROOT_SHA256,
        "source_phase_2h_protocol_sha256": SOURCE_PHASE_2H_PROTOCOL_SHA256,
        "source_phase_2i_harness_design_sha256": SOURCE_PHASE_2I_HARNESS_DESIGN_SHA256,
        "source_corrected_implementation_sha256": SOURCE_CORRECTED_IMPLEMENTATION_SHA256,
        "source_specification_root_sha256": SOURCE_SPECIFICATION_ROOT_SHA256,
        "engine_source_sha256": engine_hash,
        "run_id": run_id,
    }
    environment = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
    }
    input_manifest = {
        "binding_root_sha256": SOURCE_PHASE_2J_BINDING_ROOT_SHA256,
        "manifest_rows": input_manifest_rows,
        "provenance_row_count": len(provenance_rows),
        "provenance_sha256": sha256_file(project_root / phase_2j.PROVENANCE_PATH),
        "missing_interval_row_count": len(gap_rows),
        "missing_interval_ledger_sha256": sha256_file(
            project_root / phase_2j.MISSING_INTERVAL_LEDGER_PATH
        ),
    }

    variant_classifications = (
        gate_classification[
            ["evaluation_order", "variant_id", "variant_gate_classification"]
        ]
        .drop_duplicates()
        .sort_values("evaluation_order")
        .to_dict(orient="records")
    )
    run_summary_base = {
        "phase": PHASE,
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "evaluation_window": "2023-01-01T00:00:00Z/2026-01-01T00:00:00Z",
        "warmup_window": "2022-01-01T00:00:00Z/2023-01-01T00:00:00Z",
        "binding_root_sha256": SOURCE_PHASE_2J_BINDING_ROOT_SHA256,
        "variant_count": 6,
        "family_count": 3,
        "symbol_count": 3,
        "cost_profile_count": 5,
        "signal_row_count": int(len(signal_ledger)),
        "order_row_count": int(len(order_ledger)),
        "accepted_order_count": int(order_ledger["order_accepted"].astype(bool).sum()),
        "trade_row_count": int(len(trade_ledger)),
        "eligible_trade_count": int(trade_ledger["result_eligible"].astype(bool).sum()),
        "unresolved_or_invalidated_trade_count": int((~trade_ledger["result_eligible"].astype(bool)).sum()),
        "trade_crossing_declared_gap_count": int((trade_ledger["gap_crossing_count"].astype(int) > 0).sum()),
        "declared_source_missing_interval_count": len(gap_rows),
        "synthetic_gap_fill_count": 0,
        "metric_row_count": int(len(metric_table)),
        "multiplicity_row_count": int(len(multiplicity_table)),
        "gate_row_count": int(len(gate_classification)),
        "check_count": len(checks),
        "failed_check_count": len(failed_checks),
        "blocker_count": blocker_count,
        "historical_evaluation_count": 1,
        "backtest_execution_count": 1,
        "performance_metric_count": int(len(metric_table)),
        "candidate_comparison_count": 0,
        "candidate_ranking_count": 0,
        "winner_selection_count": 0,
        "retrospective_lockbox_access_count": 0,
        "prospective_holdout_access_count": 0,
        "operational_permissions_enabled_count": 0,
        "permissions": PERMISSIONS,
        "volatility_thresholds": volatility_thresholds,
        "variant_classifications": variant_classifications,
        "winner": None,
        "known_evidence_only": True,
        "operational_approval_granted": False,
        "validation_decision": (
            "CONTROLLED_KNOWN_EVIDENCE_EVALUATION_COMPLETED_NO_WINNER"
            if blocker_count == 0
            else "CONTROLLED_KNOWN_EVIDENCE_EVALUATION_COMPLETED_WITH_BLOCKERS_NO_WINNER"
        ),
        "recommended_next_phase": RECOMMENDED_NEXT_PHASE,
    }

    publish_status = "OUTPUT_WRITES_DISABLED"
    artifact_hashes: dict[str, str] = {}
    bundle_root_sha256 = ""
    if write_outputs:
        reports_parent = project_root / REPORTS_ROOT
        reports_parent.mkdir(parents=True, exist_ok=True)
        temp_dir = Path(
            tempfile.mkdtemp(
                prefix=f".{run_id}.tmp.",
                dir=reports_parent,
            )
        )
        try:
            _write_json(temp_dir / "input_manifest.json", input_manifest)
            _write_json(temp_dir / "source_anchors.json", source_anchors)
            _write_json(temp_dir / "environment.json", environment)
            _write_json(temp_dir / "data_quality.json", data_quality)
            _write_csv(temp_dir / "signal_ledger.csv", signal_ledger)
            _write_csv(temp_dir / "order_ledger.csv", order_ledger)
            _write_csv(temp_dir / "trade_ledger.csv", trade_ledger)
            _write_csv(temp_dir / "metric_table.csv", metric_table)
            _write_csv(temp_dir / "multiplicity_table.csv", multiplicity_table)
            _write_csv(temp_dir / "gate_classification.csv", gate_classification)
            _write_csv(temp_dir / "check_ledger.csv", check_ledger)
            artifact_hashes = _artifact_hashes(temp_dir, AUDIT_ARTIFACTS[:-1])
            bundle_root_sha256 = sha256_bytes(
                canonical_json(artifact_hashes).encode("utf-8")
            )
            run_summary = {
                **run_summary_base,
                "artifact_hashes": artifact_hashes,
                "bundle_root_sha256": bundle_root_sha256,
            }
            _write_json(temp_dir / "run_summary.json", run_summary)
            publish_status = _atomic_publish_bundle(temp_dir, final_dir)
            emit(f"audit_bundle_publish_status={publish_status}")
            emit(f"audit_bundle_path={final_dir.relative_to(project_root).as_posix()}")
        except Exception:
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
            raise
    else:
        run_summary = {
            **run_summary_base,
            "artifact_hashes": artifact_hashes,
            "bundle_root_sha256": bundle_root_sha256,
        }

    return {
        "summary": {
            **run_summary,
            "output_directory": final_dir.relative_to(project_root).as_posix(),
            "publish_status": publish_status,
            "evaluation_completed": True,
            "historical_evaluation_allowed": True,
            "ranking_allowed": False,
            "winner_selection_allowed": False,
        },
        "checks": tuple(asdict(check) for check in checks),
        "failed_checks": tuple(asdict(check) for check in failed_checks),
        "signal_ledger": signal_ledger,
        "order_ledger": order_ledger,
        "trade_ledger": trade_ledger,
        "normalized_trade_profiles": normalized,
        "metric_table": metric_table,
        "multiplicity_table": multiplicity_table,
        "gate_classification": gate_classification,
    }


__all__ = [
    "ACCOUNTING_CONTRACT",
    "ALLOWED_TRUE_PERMISSIONS",
    "AUDIT_ARTIFACTS",
    "BOOTSTRAP_RESAMPLES",
    "COST_PROFILES",
    "ControlledEvaluationFailure",
    "EXPECTED_REGIME_COMBINATIONS",
    "FAMILY_WISE_ALPHA",
    "FIXED_REWARD_TO_RISK",
    "GAP_POLICY",
    "MAXIMUM_TRADE_BARS",
    "PERMISSIONS",
    "PHASE",
    "PRIMARY_COST_PROFILE",
    "RECOMMENDED_NEXT_PHASE",
    "REPORTS_ROOT",
    "SCHEMA_VERSION",
    "SOURCE_PHASE_2J_BINDING_ROOT_SHA256",
    "SOURCE_PHASE_2J_COMMIT",
    "SPLITS",
    "STRESS_COST_PROFILE",
    "SYMBOLS",
    "VARIANT_IDS",
    "apply_cost_profiles",
    "assign_trade_features",
    "attach_closed_mtf_context",
    "build_gate_classification",
    "build_metric_table",
    "build_multiplicity_table",
    "build_regime_features",
    "build_run_id",
    "build_signal_candidate_arrays",
    "calculate_max_drawdown_r",
    "canonical_json",
    "classify_regime_values",
    "cluster_bootstrap_p_value",
    "evaluate_variant_on_symbol",
    "holm_adjust_p_values",
    "normalized_source_sha256",
    "prepare_signal_features",
    "profit_factor",
    "run_controlled_known_evidence_evaluation",
    "sha256_file",
    "split_name_for_timestamp",
]
