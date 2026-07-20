from __future__ import annotations

import csv
import hashlib
import json
import math
import shutil
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd


PHASE = "10.42R.2L"
SCHEMA_VERSION = "INDEPENDENT_RESULT_AUDIT_AND_DISPOSITION_V1"
SOURCE_PHASE_2K_COMMIT = "0a5440a70e91e833925a4147ac2863baa7666b1e"
SOURCE_PHASE_2K_RUN_ID = "known_evidence_2022_2025_v1_5c1ccb1c9fec_9243ae595f7d"
SOURCE_PHASE_2K_BUNDLE_ROOT_SHA256 = (
    "2938dcf9596281a8416b9ecd6f7431cbebee89559063bfe100a11258f76cbd02"
)
SOURCE_PHASE_2K_ENGINE_SHA256 = (
    "9243ae595f7d22bc2653ba34098bec5f1b6bc2a1e79c4114b8ea35fd83c3a4fd"
)
SOURCE_PHASE_2J_BINDING_ROOT_SHA256 = (
    "5c1ccb1c9fecdad2e196558a946944f5b9f89f258c5ef591a65d4c4c480d8c14"
)
SOURCE_SPECIFICATION_ROOT_SHA256 = (
    "0872b2bf7355e8a9b35d5b4e0e05d3edf291006862ce9ee5eae847910ef4c015"
)
SOURCE_CORRECTED_IMPLEMENTATION_SHA256 = (
    "ccf3cc05823515fa56e9e1183eb51ab903503e310aa037248847ad7445b2cc1e"
)
SOURCE_PHASE_2K_DIR = Path("reports/phase_10_42r_2k") / SOURCE_PHASE_2K_RUN_ID
REPORTS_ROOT = Path("reports/phase_10_42r_2l")
AUDIT_ID = (
    "independent_result_audit_v1_"
    + SOURCE_PHASE_2K_BUNDLE_ROOT_SHA256[:12]
    + "_"
    + SOURCE_PHASE_2K_ENGINE_SHA256[:12]
)
RECOMMENDED_NEXT_ROUTE = (
    "RETURN_TO_PHASE_10_42R_MASTER_DISPOSITION_AND_"
    "OPENCLAW_READ_ONLY_INTEGRATION_PLANNING"
)
FINAL_DECISION = (
    "INDEPENDENT_RESULT_AUDIT_CONFIRMED_ALL_VARIANTS_REJECTED_"
    "RECOVERY_LINE_CLOSED_NO_LOCKBOX_OPENED"
)

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
ROOT_HASH_ARTIFACTS = AUDIT_ARTIFACTS[:-1]

OUTPUT_ARTIFACTS = (
    "source_bundle_inventory.csv",
    "independent_metric_reproduction.csv",
    "independent_multiplicity_reproduction.csv",
    "independent_gate_reproduction.csv",
    "variant_disposition.csv",
    "audit_check_ledger.csv",
    "audit_summary.json",
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
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
EXPECTED_REGIME_COMBINATIONS = tuple(
    f"REGIME_1H={one}|REGIME_4H={four}"
    for one in ("BEARISH", "STRONG_BEARISH")
    for four in ("BEARISH", "STRONG_BEARISH")
)
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
# The split IDs are the authoritative labels written by Phase 2K. One textual
# start label above is descriptive only; the IDs drive every reproduction.
SPLIT_IDS = tuple(item[0] for item in SPLITS)

PRIMARY_COST_PROFILE = "BINANCE_SCALP_BASE_ESTIMATE"
STRESS_COST_PROFILE = "BINANCE_SCALP_STRESS_ESTIMATE"
BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED_BASE = 10_420_200
FAMILY_WISE_ALPHA = 0.05
SOURCE_PHASE_2K_INTERNAL_CHECK_COUNT = 12
DRAWDOWN_ORDER_CONTRACT = (
    "EXIT_TIME_UTC_THEN_ENTRY_TIME_UTC_THEN_SYMBOL_"
    "THEN_SOURCE_TRADE_ROW_ASCENDING"
)


@dataclass(frozen=True)
class CostProfile:
    order: int
    name: str
    fee_pct_round_trip: float
    spread_pct_round_trip: float
    slippage_pct_round_trip: float

    @property
    def total_cost_pct(self) -> float:
        return (
            self.fee_pct_round_trip
            + self.spread_pct_round_trip
            + self.slippage_pct_round_trip
        )


COST_PROFILES = (
    CostProfile(1, PRIMARY_COST_PROFILE, 0.0008, 0.0004, 0.0004),
    CostProfile(2, STRESS_COST_PROFILE, 0.0012, 0.0008, 0.0008),
    CostProfile(3, "QUANTFURY_SWING_BASE_ESTIMATE", 0.0, 0.0035, 0.0005),
    CostProfile(4, "QUANTFURY_SWING_STRESS_ESTIMATE", 0.0, 0.0060, 0.0010),
    CostProfile(5, "EXTREME_COST_STRESS_TEST", 0.0015, 0.0080, 0.0020),
)


@dataclass(frozen=True)
class AuditCheck:
    check_id: str
    check_name: str
    passed: bool
    details: str
    blocker: bool


class IndependentAuditFailure(RuntimeError):
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


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no", ""}:
        return False
    raise IndependentAuditFailure(f"Cannot parse boolean value: {value!r}")


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise IndependentAuditFailure(f"JSON object required: {path}")
    return value


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def _append_check(
    checks: list[AuditCheck],
    name: str,
    passed: bool,
    details: str,
    *,
    blocker: bool = True,
) -> None:
    ok = bool(passed)
    checks.append(
        AuditCheck(
            check_id=f"2L-CHECK-{len(checks) + 1:03d}",
            check_name=name,
            passed=ok,
            details=str(details),
            blocker=bool(blocker and not ok),
        )
    )


def calculate_max_drawdown_r(values: Sequence[float]) -> float:
    equity = 0.0
    peak = 0.0
    maximum_drawdown = 0.0
    for raw in values:
        equity += float(raw)
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


def build_normalized_trade_profiles(trades: pd.DataFrame) -> pd.DataFrame:
    required = {
        "evaluation_order",
        "family_id",
        "variant_id",
        "symbol",
        "split_name",
        "signal_time_utc",
        "entry_time_utc",
        "exit_time_utc",
        "signal_close",
        "signal_atr14",
        "trend_regime",
        "risk_pct_of_entry",
        "frictionless_gross_result_r",
        "result_eligible",
        "source_trade_row",
    }
    missing = sorted(required - set(trades.columns))
    if missing:
        raise IndependentAuditFailure("Trade ledger missing columns: " + ",".join(missing))
    eligible_mask = trades["result_eligible"].map(parse_bool)
    eligible = trades.loc[eligible_mask].copy()
    numeric_columns = (
        "evaluation_order",
        "signal_close",
        "signal_atr14",
        "risk_pct_of_entry",
        "frictionless_gross_result_r",
        "source_trade_row",
    )
    for column in numeric_columns:
        eligible[column] = pd.to_numeric(eligible[column], errors="raise")
    if eligible["risk_pct_of_entry"].le(0).any():
        raise IndependentAuditFailure("risk_pct_of_entry must be positive")
    eligible["signal_time_utc"] = pd.to_datetime(
        eligible["signal_time_utc"], errors="raise", utc=True
    )
    eligible["calendar_year"] = eligible["signal_time_utc"].dt.year.astype(int)
    eligible["volatility_proxy"] = (
        eligible["signal_atr14"].astype(float)
        / eligible["signal_close"].astype(float)
    )
    eligible["volatility_tercile"] = ""
    for variant_id, group in eligible.groupby("variant_id", sort=False):
        values = group["volatility_proxy"].astype(float)
        lower = float(values.quantile(1.0 / 3.0, interpolation="linear"))
        upper = float(values.quantile(2.0 / 3.0, interpolation="linear"))
        labels = np.select(
            (values <= lower, values <= upper),
            ("LOW", "MID"),
            default="HIGH",
        )
        eligible.loc[group.index, "volatility_tercile"] = labels
    rows: list[pd.DataFrame] = []
    for profile in COST_PROFILES:
        current = eligible.copy()
        current["cost_profile_order"] = profile.order
        current["cost_profile"] = profile.name
        current["profile_total_cost_pct"] = profile.total_cost_pct
        current["profile_total_cost_r"] = (
            profile.total_cost_pct / current["risk_pct_of_entry"].astype(float)
        )
        current["normalized_net_result_r"] = (
            current["frictionless_gross_result_r"].astype(float)
            - current["profile_total_cost_r"].astype(float)
        )
        current["cost_application_count"] = 1
        rows.append(current)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def _window_metrics(
    group: pd.DataFrame,
    symbols: Sequence[str],
    split_names: Sequence[str],
) -> dict[str, Any]:
    index = pd.MultiIndex.from_product(
        [list(symbols), list(split_names)], names=["symbol", "split_name"]
    )
    if group.empty:
        windows = pd.DataFrame(index=index, data={"sum": 0.0, "size": 0})
    else:
        observed = group.groupby(
            ["symbol", "split_name"], sort=True, observed=True
        )["normalized_net_result_r"].agg(["sum", "size"])
        unexpected = observed.index.difference(index)
        if len(unexpected):
            raise IndependentAuditFailure(f"Unexpected window units: {list(unexpected)}")
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
    ordered = group.copy()
    if ordered.empty:
        net_values: list[float] = []
        gross_values: list[float] = []
    else:
        ordered["_exit"] = pd.to_datetime(ordered["exit_time_utc"], utc=True)
        ordered["_entry"] = pd.to_datetime(ordered["entry_time_utc"], utc=True)
        ordered = ordered.sort_values(
            ["_exit", "_entry", "symbol", "source_trade_row"], kind="stable"
        )
        net_values = ordered["normalized_net_result_r"].astype(float).tolist()
        gross_values = ordered["frictionless_gross_result_r"].astype(float).tolist()
    windows = _window_metrics(group, symbols=symbols, split_names=split_names)
    return {
        "trade_count": len(net_values),
        "normalized_total_result_r": float(sum(net_values)),
        "normalized_average_result_r": float(np.mean(net_values)) if net_values else 0.0,
        "normalized_profit_factor": profit_factor(net_values),
        "normalized_max_drawdown_r": calculate_max_drawdown_r(net_values),
        "frictionless_gross_average_result_r": (
            float(np.mean(gross_values)) if gross_values else 0.0
        ),
        "frictionless_profit_factor": profit_factor(gross_values),
        **windows,
        "drawdown_order_contract": DRAWDOWN_ORDER_CONTRACT,
    }


def build_independent_metric_table(normalized: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    slice_specs = (
        ("AGGREGATE", None),
        ("SYMBOL", "symbol"),
        ("CALENDAR_YEAR", "calendar_year"),
        ("VOLATILITY_TERCILE", "volatility_tercile"),
        ("CLOSED_MTF_TREND_REGIME", "trend_regime"),
        ("SIGNAL_FAMILY", "family_id"),
    )
    for evaluation_order, variant_id in enumerate(VARIANT_IDS, start=1):
        family_id = VARIANT_FAMILY_MAP[variant_id]
        variant_frame = normalized.loc[normalized["variant_id"].eq(variant_id)]
        for profile in COST_PROFILES:
            profile_frame = variant_frame.loc[
                variant_frame["cost_profile"].eq(profile.name)
            ]
            for dimension, column in slice_specs:
                if column is None:
                    groups: Iterable[tuple[str, pd.DataFrame]] = (("ALL", profile_frame),)
                else:
                    if column == "symbol":
                        values: Sequence[Any] = SYMBOLS
                    elif column == "calendar_year":
                        values = (2023, 2024, 2025)
                    elif column == "volatility_tercile":
                        values = ("LOW", "MID", "HIGH")
                    elif column == "trend_regime":
                        values = EXPECTED_REGIME_COMBINATIONS
                    elif column == "family_id":
                        values = (family_id,)
                    else:
                        raise IndependentAuditFailure(f"Unsupported slice: {column}")
                    groups = tuple(
                        (str(value), profile_frame.loc[profile_frame[column].eq(value)])
                        for value in values
                    )
                for value, group in groups:
                    selected_symbols = (value,) if dimension == "SYMBOL" else SYMBOLS
                    selected_splits = SPLIT_IDS
                    if dimension == "CALENDAR_YEAR":
                        year = int(value)
                        selected_splits = tuple(
                            split_id for split_id in SPLIT_IDS if f"TO_{year}" in split_id
                            or f"TO_{year}01" in split_id
                        )
                        # Phase 2K selected windows by test start year. Its IDs have the
                        # test start directly after TO_.
                        selected_splits = tuple(
                            split_id
                            for split_id in SPLIT_IDS
                            if split_id.split("_TO_")[1].startswith(str(year))
                        )
                    rows.append(
                        {
                            "evaluation_order": evaluation_order,
                            "variant_id": variant_id,
                            "family_id": family_id,
                            "cost_profile": profile.name,
                            "slice_dimension": dimension,
                            "slice_value": value,
                            **_summarize_metric_group(
                                group,
                                symbols=selected_symbols,
                                split_names=selected_splits,
                            ),
                        }
                    )
    return pd.DataFrame(rows).sort_values(
        ["evaluation_order", "cost_profile", "slice_dimension", "slice_value"],
        kind="stable",
    ).reset_index(drop=True)


def cluster_bootstrap_p_value(
    primary: pd.DataFrame,
    *,
    evaluation_order: int,
    resamples: int = BOOTSTRAP_RESAMPLES,
) -> tuple[float, float]:
    values = primary["normalized_net_result_r"].astype(float)
    observed = float(values.mean()) if len(values) else 0.0
    cluster_index = pd.MultiIndex.from_product(
        [SYMBOLS, SPLIT_IDS], names=["symbol", "split_name"]
    )
    if primary.empty:
        cluster_sum = pd.Series(0.0, index=cluster_index)
        cluster_count = pd.Series(0, index=cluster_index)
    else:
        grouped = primary.groupby(
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


def build_independent_multiplicity_table(normalized: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for evaluation_order, variant_id in enumerate(VARIANT_IDS, start=1):
        primary = normalized.loc[
            normalized["variant_id"].eq(variant_id)
            & normalized["cost_profile"].eq(PRIMARY_COST_PROFILE)
        ]
        observed, p_value = cluster_bootstrap_p_value(
            primary, evaluation_order=evaluation_order
        )
        rows.append(
            {
                "evaluation_order": evaluation_order,
                "variant_id": variant_id,
                "family_id": VARIANT_FAMILY_MAP[variant_id],
                "primary_cost_profile": PRIMARY_COST_PROFILE,
                "observed_average_net_r": observed,
                "trade_count": int(len(primary)),
                "cluster_count": 36,
                "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
                "bootstrap_seed": BOOTSTRAP_SEED_BASE + evaluation_order,
                "unadjusted_p_value": p_value,
                "p_value_method": "CENTERED_SYMBOL_WINDOW_CLUSTER_BOOTSTRAP_EXPECTANCY_V1",
                "multiplicity_method": "HOLM_BONFERRONI_FWER_OVER_ALL_FROZEN_VARIANTS_V1",
            }
        )
    return pd.DataFrame(holm_adjust_p_values(rows)).sort_values(
        "evaluation_order"
    ).reset_index(drop=True)


def _metric_row(
    metrics: pd.DataFrame,
    variant_id: str,
    profile: str,
    dimension: str,
    value: str,
) -> pd.Series:
    rows = metrics.loc[
        metrics["variant_id"].eq(variant_id)
        & metrics["cost_profile"].eq(profile)
        & metrics["slice_dimension"].eq(dimension)
        & metrics["slice_value"].astype(str).eq(str(value))
    ]
    if len(rows) != 1:
        raise IndependentAuditFailure(
            f"Expected one metric row for {variant_id}/{profile}/{dimension}/{value}"
        )
    return rows.iloc[0]


def build_independent_gate_table(
    metrics: pd.DataFrame,
    multiplicity: pd.DataFrame,
    trades: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    result_eligible = trades["result_eligible"].map(parse_bool)
    for variant_id in VARIANT_IDS:
        base = _metric_row(metrics, variant_id, PRIMARY_COST_PROFILE, "AGGREGATE", "ALL")
        stress = _metric_row(metrics, variant_id, STRESS_COST_PROFILE, "AGGREGATE", "ALL")
        symbol_rows = metrics.loc[
            metrics["variant_id"].eq(variant_id)
            & metrics["cost_profile"].eq(PRIMARY_COST_PROFILE)
            & metrics["slice_dimension"].eq("SYMBOL")
        ]
        year_rows = metrics.loc[
            metrics["variant_id"].eq(variant_id)
            & metrics["cost_profile"].eq(PRIMARY_COST_PROFILE)
            & metrics["slice_dimension"].eq("CALENDAR_YEAR")
        ]
        volatility_rows = metrics.loc[
            metrics["variant_id"].eq(variant_id)
            & metrics["cost_profile"].eq(PRIMARY_COST_PROFILE)
            & metrics["slice_dimension"].eq("VOLATILITY_TERCILE")
        ]
        regime_rows = metrics.loc[
            metrics["variant_id"].eq(variant_id)
            & metrics["cost_profile"].eq(PRIMARY_COST_PROFILE)
            & metrics["slice_dimension"].eq("CLOSED_MTF_TREND_REGIME")
        ]
        mult = multiplicity.loc[multiplicity["variant_id"].eq(variant_id)].iloc[0]
        variant_mask = trades["variant_id"].eq(variant_id)
        unresolved = int((~result_eligible.loc[variant_mask]).sum())
        stability = {
            "base_positive_window_rate_at_least_0_50": float(base["positive_window_rate"]) >= 0.50,
            "stress_positive_window_rate_at_least_0_45": float(stress["positive_window_rate"]) >= 0.45,
            "volatility_terciles_nonempty_nonnegative": bool(
                len(volatility_rows) == 3
                and (volatility_rows["trade_count"].astype(int) > 0).all()
                and (volatility_rows["normalized_average_result_r"].astype(float) >= 0.0).all()
            ),
            "all_four_closed_mtf_regimes_nonempty_nonnegative": bool(
                len(regime_rows) == 4
                and (regime_rows["trade_count"].astype(int) > 0).all()
                and (regime_rows["normalized_average_result_r"].astype(float) >= 0.0).all()
            ),
            "five_cost_profiles_published": bool(
                metrics.loc[
                    metrics["variant_id"].eq(variant_id)
                    & metrics["slice_dimension"].eq("AGGREGATE")
                ]["cost_profile"].nunique() == 5
            ),
            "no_unresolved_or_invalidated_trade": unresolved == 0,
        }
        gate_values = (
            ("GATE_001", "aggregate_trade_count", ">=", 100, int(base["trade_count"]), int(base["trade_count"]) >= 100),
            ("GATE_002", "trade_count_each_symbol", ">=", 20, int(symbol_rows["trade_count"].astype(int).min()), bool(len(symbol_rows) == 3 and (symbol_rows["trade_count"].astype(int) >= 20).all())),
            ("GATE_003", "binance_base_profit_factor", ">=", 1.05, float(base["normalized_profit_factor"]), float(base["normalized_profit_factor"]) >= 1.05),
            ("GATE_004", "binance_base_expectancy_aggregate", ">", 0.0, float(base["normalized_average_result_r"]), float(base["normalized_average_result_r"]) > 0.0),
            ("GATE_005", "binance_base_expectancy_each_symbol", ">", 0.0, float(symbol_rows["normalized_average_result_r"].astype(float).min()), bool(len(symbol_rows) == 3 and (symbol_rows["normalized_average_result_r"].astype(float) > 0.0).all())),
            ("GATE_006", "binance_base_expectancy_each_year", ">=", 0.0, float(year_rows["normalized_average_result_r"].astype(float).min()), bool(len(year_rows) == 3 and (year_rows["normalized_average_result_r"].astype(float) >= 0.0).all())),
            ("GATE_007", "binance_stress_expectancy", ">=", 0.0, float(stress["normalized_average_result_r"]), float(stress["normalized_average_result_r"]) >= 0.0),
            ("GATE_008", "binance_stress_profit_factor", ">=", 1.0, float(stress["normalized_profit_factor"]), float(stress["normalized_profit_factor"]) >= 1.0),
            ("GATE_009", "holm_adjusted_p_value", "<=", 0.05, float(mult["holm_adjusted_p_value"]), float(mult["holm_adjusted_p_value"]) <= 0.05),
            ("GATE_010", "all_predeclared_stability_slices", "==", "NON_FAILING", canonical_json(stability), all(stability.values())),
        )
        all_passed = all(bool(item[5]) for item in gate_values)
        evaluation_order = int(mult["evaluation_order"])
        for gate_order, item in enumerate(gate_values, start=1):
            gate_id, metric, operator, threshold, observed, passed = item
            rows.append(
                {
                    "evaluation_order": evaluation_order,
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


def frames_equivalent(
    left: pd.DataFrame,
    right: pd.DataFrame,
    *,
    float_tolerance: float = 1e-9,
    relative_tolerance: float = 1e-12,
) -> tuple[bool, str]:
    if list(left.columns) != list(right.columns):
        return False, f"columns differ: {list(left.columns)} != {list(right.columns)}"
    if len(left) != len(right):
        return False, f"row count differs: {len(left)} != {len(right)}"

    def cell_equal(a: Any, b: Any) -> bool:
        if pd.isna(a) and pd.isna(b):
            return True
        a_text = str(a).strip()
        b_text = str(b).strip()
        boolean_tokens = {"true", "false"}
        if a_text.lower() in boolean_tokens and b_text.lower() in boolean_tokens:
            return a_text.lower() == b_text.lower()
        try:
            a_number = float(a_text)
            b_number = float(b_text)
            if math.isfinite(a_number) and math.isfinite(b_number):
                return math.isclose(
                    a_number,
                    b_number,
                    rel_tol=relative_tolerance,
                    abs_tol=float_tolerance,
                )
        except (TypeError, ValueError):
            pass
        return a_text == b_text

    for column in left.columns:
        for row_index, (a, b) in enumerate(zip(left[column], right[column])):
            if not cell_equal(a, b):
                return (
                    False,
                    f"column {column} differs at row {row_index}: {a!r} != {b!r}",
                )
    return True, "frames equivalent"


def build_variant_disposition(gates: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for evaluation_order, variant_id in enumerate(VARIANT_IDS, start=1):
        current = gates.loc[gates["variant_id"].eq(variant_id)].copy()
        current["passed"] = current["passed"].map(parse_bool)
        failed = current.loc[~current["passed"]]
        all_passed = failed.empty and len(current) == 10
        rows.append(
            {
                "evaluation_order": evaluation_order,
                "family_id": VARIANT_FAMILY_MAP[variant_id],
                "variant_id": variant_id,
                "mandatory_gate_count": int(len(current)),
                "passed_gate_count": int(current["passed"].sum()),
                "failed_gate_count": int((~current["passed"]).sum()),
                "failed_gate_ids": "|".join(failed["gate_id"].astype(str).tolist()),
                "failed_gate_metrics": "|".join(failed["metric"].astype(str).tolist()),
                "known_evidence_all_gates_passed": all_passed,
                "disposition": (
                    "KNOWN_EVIDENCE_GATES_PASSED_BUT_NO_PROMOTION_OR_LOCKBOX_PERMISSION"
                    if all_passed
                    else "REJECTED_AFTER_INDEPENDENT_KNOWN_EVIDENCE_AUDIT_NO_LOCKBOX_OPENING"
                ),
                "ranking_allowed": False,
                "winner_selection_allowed": False,
                "lockbox_opening_allowed": False,
                "paper_trading_allowed": False,
                "real_capital_allowed": False,
                "operational_approval_allowed": False,
            }
        )
    return pd.DataFrame(rows)


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


def _atomic_publish(temp_dir: Path, final_dir: Path) -> str:
    if final_dir.exists():
        expected = sorted(path.name for path in temp_dir.iterdir() if path.is_file())
        actual = sorted(path.name for path in final_dir.iterdir() if path.is_file())
        if expected != actual:
            raise IndependentAuditFailure("Existing audit inventory differs")
        for name in expected:
            if sha256_file(temp_dir / name) != sha256_file(final_dir / name):
                raise IndependentAuditFailure(f"Existing audit artifact differs: {name}")
        shutil.rmtree(temp_dir)
        return "IDEMPOTENT_EXISTING_AUDIT_VERIFIED"
    final_dir.parent.mkdir(parents=True, exist_ok=True)
    temp_dir.rename(final_dir)
    return "NEW_AUDIT_ATOMICALLY_PUBLISHED"


def run_independent_result_audit(
    *,
    root: Path | None = None,
    write_outputs: bool = True,
) -> dict[str, Any]:
    project_root = (root or Path.cwd()).resolve()
    bundle_dir = project_root / SOURCE_PHASE_2K_DIR
    checks: list[AuditCheck] = []

    _append_check(checks, "source_bundle_directory_exists", bundle_dir.is_dir(), str(bundle_dir))
    if not bundle_dir.is_dir():
        raise IndependentAuditFailure(f"Phase 2K bundle not found: {bundle_dir}")

    actual_names = sorted(path.name for path in bundle_dir.iterdir() if path.is_file())
    expected_names = sorted(AUDIT_ARTIFACTS)
    _append_check(checks, "source_bundle_inventory_exact", actual_names == expected_names, canonical_json(actual_names))

    run_summary = _read_json(bundle_dir / "run_summary.json")
    source_anchors = _read_json(bundle_dir / "source_anchors.json")
    input_manifest = _read_json(bundle_dir / "input_manifest.json")
    data_quality = _read_json(bundle_dir / "data_quality.json")

    inventory_rows: list[dict[str, Any]] = []
    actual_hashes: dict[str, str] = {}
    for name in AUDIT_ARTIFACTS:
        path = bundle_dir / name
        digest = sha256_file(path)
        inventory_rows.append(
            {"artifact_order": len(inventory_rows) + 1, "artifact_name": name, "size_bytes": path.stat().st_size, "sha256": digest}
        )
        if name in ROOT_HASH_ARTIFACTS:
            actual_hashes[name] = digest
    inventory = pd.DataFrame(inventory_rows)
    declared_hashes = run_summary.get("artifact_hashes", {})
    _append_check(checks, "artifact_hash_manifest_exact", actual_hashes == declared_hashes, canonical_json(actual_hashes))
    reproduced_root = sha256_bytes(canonical_json(actual_hashes).encode("utf-8"))
    _append_check(checks, "bundle_root_reproduces", reproduced_root == run_summary.get("bundle_root_sha256"), reproduced_root)
    _append_check(checks, "bundle_root_matches_frozen_2k", reproduced_root == SOURCE_PHASE_2K_BUNDLE_ROOT_SHA256, reproduced_root)
    _append_check(checks, "run_id_exact", run_summary.get("run_id") == SOURCE_PHASE_2K_RUN_ID, str(run_summary.get("run_id")))
    _append_check(checks, "source_anchor_phase_exact", source_anchors.get("phase") == "10.42R.2K", canonical_json(source_anchors))
    phase_2k_engine_path = project_root / "src/evaluation/frozen_recovery_candidate_controlled_known_evidence_evaluation_v1.py"
    actual_engine_hash = (
        normalized_source_sha256(phase_2k_engine_path)
        if phase_2k_engine_path.is_file()
        else ""
    )
    _append_check(
        checks,
        "source_engine_hash_exact",
        source_anchors.get("engine_source_sha256") == SOURCE_PHASE_2K_ENGINE_SHA256
        and actual_engine_hash == SOURCE_PHASE_2K_ENGINE_SHA256,
        canonical_json(
            {
                "declared": source_anchors.get("engine_source_sha256"),
                "actual": actual_engine_hash,
            }
        ),
    )
    _append_check(checks, "binding_root_exact", run_summary.get("binding_root_sha256") == SOURCE_PHASE_2J_BINDING_ROOT_SHA256 and input_manifest.get("binding_root_sha256") == SOURCE_PHASE_2J_BINDING_ROOT_SHA256, str(run_summary.get("binding_root_sha256")))
    _append_check(checks, "specification_and_implementation_anchors_exact", source_anchors.get("source_specification_root_sha256") == SOURCE_SPECIFICATION_ROOT_SHA256 and source_anchors.get("source_corrected_implementation_sha256") == SOURCE_CORRECTED_IMPLEMENTATION_SHA256, canonical_json(source_anchors))
    _append_check(checks, "source_run_summary_decision_exact", run_summary.get("validation_decision") == "CONTROLLED_KNOWN_EVIDENCE_EVALUATION_COMPLETED_NO_WINNER" and run_summary.get("known_evidence_only") is True and run_summary.get("operational_approval_granted") is False, canonical_json({"decision": run_summary.get("validation_decision"), "known_evidence_only": run_summary.get("known_evidence_only"), "operational_approval_granted": run_summary.get("operational_approval_granted")}))

    signal_ledger = _read_csv(bundle_dir / "signal_ledger.csv")
    order_ledger = _read_csv(bundle_dir / "order_ledger.csv")
    trade_ledger = _read_csv(bundle_dir / "trade_ledger.csv")
    metric_table = _read_csv(bundle_dir / "metric_table.csv")
    multiplicity_table = _read_csv(bundle_dir / "multiplicity_table.csv")
    gate_table = _read_csv(bundle_dir / "gate_classification.csv")
    source_check_ledger = _read_csv(bundle_dir / "check_ledger.csv")

    expected_counts = {
        "signal_row_count": 9216,
        "order_row_count": 9216,
        "trade_row_count": 5689,
        "eligible_trade_count": 5689,
        "metric_row_count": 450,
        "multiplicity_row_count": 6,
        "gate_row_count": 60,
        "check_count": SOURCE_PHASE_2K_INTERNAL_CHECK_COUNT,
    }
    actual_counts = {
        "signal_row_count": len(signal_ledger),
        "order_row_count": len(order_ledger),
        "trade_row_count": len(trade_ledger),
        "eligible_trade_count": int(trade_ledger["result_eligible"].map(parse_bool).sum()),
        "metric_row_count": len(metric_table),
        "multiplicity_row_count": len(multiplicity_table),
        "gate_row_count": len(gate_table),
        "check_count": len(source_check_ledger),
    }
    _append_check(checks, "published_row_counts_exact", actual_counts == expected_counts, canonical_json(actual_counts))
    _append_check(checks, "run_summary_counts_reconcile", all(int(run_summary.get(key, -1)) == value for key, value in actual_counts.items()), canonical_json(actual_counts))
    _append_check(checks, "signal_and_order_ledgers_one_to_one", len(signal_ledger) == len(order_ledger) and signal_ledger[["evaluation_order", "variant_id", "symbol", "signal_bar_index"]].astype(str).equals(order_ledger[["evaluation_order", "variant_id", "symbol", "signal_bar_index"]].astype(str)), str(len(signal_ledger)))
    _append_check(checks, "all_source_checks_pass", source_check_ledger["passed"].map(parse_bool).all() and not source_check_ledger["blocker"].map(parse_bool).any(), str(len(source_check_ledger)))
    _append_check(checks, "source_validation_no_failures", int(run_summary.get("failed_check_count", -1)) == 0 and int(run_summary.get("blocker_count", -1)) == 0, canonical_json({"failed": run_summary.get("failed_check_count"), "blockers": run_summary.get("blocker_count")}))
    _append_check(checks, "no_synthetic_gap_fill", int(data_quality.get("synthetic_gap_fill_count", -1)) == 0 and int(run_summary.get("synthetic_gap_fill_count", -1)) == 0, canonical_json(data_quality))
    _append_check(checks, "all_trades_resolved_and_eligible", trade_ledger["result_eligible"].map(parse_bool).all() and int(run_summary.get("unresolved_or_invalidated_trade_count", -1)) == 0, str(len(trade_ledger)))

    normalized = build_normalized_trade_profiles(trade_ledger)
    _append_check(checks, "cost_grid_exact_five_profiles_once", len(normalized) == len(trade_ledger) * 5 and normalized["cost_profile"].nunique() == 5 and normalized["cost_application_count"].eq(1).all(), str(len(normalized)))

    independent_metrics = build_independent_metric_table(normalized)
    metric_ok, metric_details = frames_equivalent(independent_metrics, metric_table)
    _append_check(checks, "metric_table_independently_reproduced", metric_ok, metric_details)

    independent_multiplicity = build_independent_multiplicity_table(normalized)
    multiplicity_ok, multiplicity_details = frames_equivalent(independent_multiplicity, multiplicity_table)
    _append_check(checks, "multiplicity_independently_reproduced", multiplicity_ok, multiplicity_details)

    independent_gates = build_independent_gate_table(independent_metrics, independent_multiplicity, trade_ledger)
    gate_ok, gate_details = frames_equivalent(independent_gates, gate_table)
    _append_check(checks, "gate_table_independently_reproduced", gate_ok, gate_details)

    gate_table["passed"] = gate_table["passed"].map(parse_bool)
    gate_table["override_allowed"] = gate_table["override_allowed"].map(parse_bool)
    gate_table["ranking_allowed"] = gate_table["ranking_allowed"].map(parse_bool)
    gate_table["winner_selection_allowed"] = gate_table["winner_selection_allowed"].map(parse_bool)
    gate_table["operational_approval_allowed"] = gate_table["operational_approval_allowed"].map(parse_bool)
    classifications = gate_table[["variant_id", "variant_gate_classification"]].drop_duplicates()
    _append_check(checks, "all_six_variants_published", tuple(classifications["variant_id"].tolist()) == VARIANT_IDS, canonical_json(classifications.to_dict(orient="records")))
    _append_check(checks, "all_six_variants_failed_one_or_more_gates", len(classifications) == 6 and classifications["variant_gate_classification"].eq("ONE_OR_MORE_GATES_FAILED_KNOWN_EVIDENCE_ONLY").all() and gate_table.groupby("variant_id")["passed"].apply(lambda values: (~values).any()).all(), canonical_json(classifications.to_dict(orient="records")))
    _append_check(checks, "no_overrides_ranking_selection_or_operations", not gate_table["override_allowed"].any() and not gate_table["ranking_allowed"].any() and not gate_table["winner_selection_allowed"].any() and not gate_table["operational_approval_allowed"].any(), "all false")

    permissions = run_summary.get("permissions", {})
    forbidden_permission_keys = (
        "retrospective_lockbox_access_allowed",
        "prospective_holdout_access_allowed",
        "candidate_comparison_allowed",
        "candidate_ranking_allowed",
        "winner_selection_allowed",
        "candidate_mutation_allowed",
        "forward_observation_allowed",
        "official_dataset_write_allowed",
        "signal_generation_enabled",
        "live_alerts_allowed",
        "paper_trade_execution_allowed",
        "real_capital_allowed",
        "market_execution_allowed",
        "exchange_execution_allowed",
        "automation_allowed",
        "execution_allowed",
        "openclaw_operational_integration_allowed",
    )
    _append_check(checks, "forbidden_permissions_all_false", all(permissions.get(key) is False for key in forbidden_permission_keys), canonical_json(permissions))
    _append_check(checks, "lockbox_access_counts_zero", int(run_summary.get("retrospective_lockbox_access_count", -1)) == 0 and int(run_summary.get("prospective_holdout_access_count", -1)) == 0, canonical_json({"retrospective": run_summary.get("retrospective_lockbox_access_count"), "prospective": run_summary.get("prospective_holdout_access_count")}))
    _append_check(checks, "comparison_ranking_winner_counts_zero", int(run_summary.get("candidate_comparison_count", -1)) == 0 and int(run_summary.get("candidate_ranking_count", -1)) == 0 and int(run_summary.get("winner_selection_count", -1)) == 0 and run_summary.get("winner") is None, canonical_json({"comparison": run_summary.get("candidate_comparison_count"), "ranking": run_summary.get("candidate_ranking_count"), "winner": run_summary.get("winner_selection_count")}))

    retrospective = project_root / "data/holdout/strategy_recovery_retrospective_lockbox_2026h1_v1.csv"
    prospective = project_root / "data/holdout/strategy_recovery_prospective_20260720_20270120_v1.csv"
    _append_check(checks, "lockbox_files_remain_absent", not retrospective.exists() and not prospective.exists(), f"retrospective={retrospective.exists()},prospective={prospective.exists()}")

    dispositions = build_variant_disposition(gate_table)
    _append_check(checks, "six_rejection_dispositions_exact", len(dispositions) == 6 and dispositions["failed_gate_count"].gt(0).all() and dispositions["disposition"].eq("REJECTED_AFTER_INDEPENDENT_KNOWN_EVIDENCE_AUDIT_NO_LOCKBOX_OPENING").all(), canonical_json(dispositions.to_dict(orient="records")))
    _append_check(checks, "recovery_line_closure_is_finite", dispositions["known_evidence_all_gates_passed"].eq(False).all(), "no surviving variant")

    failed_checks = [check for check in checks if not check.passed]
    blockers = [check for check in checks if check.blocker]
    if blockers:
        raise IndependentAuditFailure(
            "Independent audit blockers: " + ",".join(item.check_name for item in blockers)
        )

    audit_summary_base = {
        "phase": PHASE,
        "schema_version": SCHEMA_VERSION,
        "source_phase_2k_commit": SOURCE_PHASE_2K_COMMIT,
        "source_phase_2k_run_id": SOURCE_PHASE_2K_RUN_ID,
        "source_phase_2k_bundle_root_sha256": SOURCE_PHASE_2K_BUNDLE_ROOT_SHA256,
        "reproduced_bundle_root_sha256": reproduced_root,
        "source_phase_2k_engine_sha256": SOURCE_PHASE_2K_ENGINE_SHA256,
        "variant_count": 6,
        "family_count": 3,
        "source_artifact_count": 12,
        "signal_row_count": len(signal_ledger),
        "order_row_count": len(order_ledger),
        "trade_row_count": len(trade_ledger),
        "eligible_trade_count": int(trade_ledger["result_eligible"].map(parse_bool).sum()),
        "metric_row_count": len(independent_metrics),
        "multiplicity_row_count": len(independent_multiplicity),
        "gate_row_count": len(independent_gates),
        "rejected_variant_count": int(dispositions["failed_gate_count"].gt(0).sum()),
        "surviving_variant_count": int(dispositions["failed_gate_count"].eq(0).sum()),
        "historical_evaluation_count": 0,
        "backtest_execution_count": 0,
        "performance_metric_reproduction_count": len(independent_metrics),
        "candidate_comparison_count": 0,
        "candidate_ranking_count": 0,
        "winner_selection_count": 0,
        "retrospective_lockbox_access_count": 0,
        "prospective_holdout_access_count": 0,
        "candidate_mutation_count": 0,
        "paper_trade_execution_allowed": False,
        "real_capital_allowed": False,
        "openclaw_operational_integration_allowed": False,
        "audit_check_count": len(checks),
        "failed_check_count": len(failed_checks),
        "blocker_count": len(blockers),
        "recovery_line_closed": True,
        "lockbox_opening_allowed": False,
        "validation_decision": FINAL_DECISION,
        "recommended_next_route": RECOMMENDED_NEXT_ROUTE,
    }

    output_dir = project_root / REPORTS_ROOT / AUDIT_ID
    publish_status = "OUTPUT_WRITES_DISABLED"
    output_root_sha256 = ""
    if write_outputs:
        output_dir.parent.mkdir(parents=True, exist_ok=True)
        temp_dir = Path(tempfile.mkdtemp(prefix=f".{AUDIT_ID}.tmp.", dir=output_dir.parent))
        try:
            _write_csv(temp_dir / "source_bundle_inventory.csv", inventory)
            _write_csv(temp_dir / "independent_metric_reproduction.csv", independent_metrics)
            _write_csv(temp_dir / "independent_multiplicity_reproduction.csv", independent_multiplicity)
            _write_csv(temp_dir / "independent_gate_reproduction.csv", independent_gates)
            _write_csv(temp_dir / "variant_disposition.csv", dispositions)
            check_frame = pd.DataFrame(asdict(check) for check in checks)
            _write_csv(temp_dir / "audit_check_ledger.csv", check_frame)
            output_hashes = {
                name: sha256_file(temp_dir / name)
                for name in OUTPUT_ARTIFACTS[:-1]
            }
            output_root_sha256 = sha256_bytes(
                canonical_json(output_hashes).encode("utf-8")
            )
            summary = {
                **audit_summary_base,
                "audit_artifact_hashes": output_hashes,
                "audit_bundle_root_sha256": output_root_sha256,
            }
            _write_json(temp_dir / "audit_summary.json", summary)
            publish_status = _atomic_publish(temp_dir, output_dir)
        except Exception:
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
            raise
    else:
        summary = {
            **audit_summary_base,
            "audit_artifact_hashes": {},
            "audit_bundle_root_sha256": "",
        }

    return {
        "summary": {
            **summary,
            "output_directory": output_dir.relative_to(project_root).as_posix(),
            "publish_status": publish_status,
            "audit_completed": True,
        },
        "checks": tuple(asdict(check) for check in checks),
        "inventory": inventory,
        "independent_metrics": independent_metrics,
        "independent_multiplicity": independent_multiplicity,
        "independent_gates": independent_gates,
        "dispositions": dispositions,
    }


__all__ = [
    "AUDIT_ARTIFACTS",
    "AUDIT_ID",
    "COST_PROFILES",
    "FINAL_DECISION",
    "IndependentAuditFailure",
    "OUTPUT_ARTIFACTS",
    "PHASE",
    "RECOMMENDED_NEXT_ROUTE",
    "SCHEMA_VERSION",
    "SOURCE_PHASE_2K_BUNDLE_ROOT_SHA256",
    "SOURCE_PHASE_2K_COMMIT",
    "SOURCE_PHASE_2K_DIR",
    "SOURCE_PHASE_2K_ENGINE_SHA256",
    "SOURCE_PHASE_2K_RUN_ID",
    "VARIANT_IDS",
    "build_independent_gate_table",
    "build_independent_metric_table",
    "build_independent_multiplicity_table",
    "build_normalized_trade_profiles",
    "build_variant_disposition",
    "calculate_max_drawdown_r",
    "canonical_json",
    "cluster_bootstrap_p_value",
    "frames_equivalent",
    "holm_adjust_p_values",
    "normalized_source_sha256",
    "parse_bool",
    "profit_factor",
    "run_independent_result_audit",
    "sha256_file",
]
