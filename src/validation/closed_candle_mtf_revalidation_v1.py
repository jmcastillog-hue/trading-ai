from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Any

import pandas as pd

from src.backtesting.backtesting_engine_v3 import BacktestConfig
from src.execution.cost_aware_filter_v1 import (
    aggregate_cost_summaries,
    apply_cost_profile_to_trades,
    build_cost_profiles,
    summarize_cost_adjusted_trades,
)
from src.long_side.long_baseline_readiness_gate_v1 import (
    validate_long_baseline_readiness_gate,
)
from src.market_structure.directional_context_filter_v3 import (
    classify_directional_context_v3,
    classify_tf_bias,
    long_allowed_by_directional_context_v3,
    normalize_ohlcv_columns,
    prepare_directional_features,
    short_allowed_by_directional_context_v3,
)
from src.market_structure.directional_context_filter_v3_1 import (
    add_directional_context_v3_1_columns,
)
from src.market_structure.mtf_regime_filter import (
    build_regime_df,
    load_ohlcv,
)
from src.risk.monte_carlo_risk_engine_v1 import (
    MonteCarloConfig,
    run_monte_carlo_for_profile,
)
from src.strategies.fib_v5_mtf_strategy import fib_v5_short_with_mtf_filter
from src.validation.walk_forward_engine_v1 import (
    build_walk_forward_candidates,
    classify_walk_forward_result,
    run_candidate_backtest,
    slice_by_date,
)


REPORTS_DIR = Path(
    "reports/phase_10_42r_2_short_long_closed_candle_mtf_revalidation_v1"
)
DATA_DIR = Path("data/walk_forward_engine_v1")

SHORT_CANDIDATE = "TARGET_SHORT_FIB_V5_MTF_V3_1 + FIXED_RR_2_5"
LONG_PRIMARY = "LONG_BASE_FAILED_BREAKDOWN_V1"
LONG_SECONDARY = "LONG_BASE_LIQUIDITY_SWEEP_V1"

SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
TIMEFRAMES = ("15m", "1h", "4h")
START_DATE = "2022-01-01"
END_DATE = "2026-01-01"

MODE_LEGACY = "LEGACY_OPEN_TIMESTAMP_DIAGNOSTIC_ONLY"
MODE_CORRECTED = "CLOSED_CANDLE_CORRECTED"
STRESS_PROFILE = "BINANCE_SCALP_STRESS_ESTIMATE"

MIN_ROWS = {
    "15m": 130_000,
    "1h": 34_000,
    "4h": 8_500,
}
EXPECTED_LAST_OPEN = {
    "15m": pd.Timestamp("2025-12-31 23:45:00"),
    "1h": pd.Timestamp("2025-12-31 23:00:00"),
    "4h": pd.Timestamp("2025-12-31 20:00:00"),
}

OFFICIAL_DATASET_PATH = Path("data/forward/long_forward_observation_dataset_v1.csv")
OFFICIAL_TEMP_PATH = OFFICIAL_DATASET_PATH.with_suffix(".tmp")
OFFICIAL_LOCK_PATH = OFFICIAL_DATASET_PATH.with_suffix(".lock")
OFFICIAL_MANIFEST_PATH = OFFICIAL_DATASET_PATH.with_suffix(".manifest.csv")
OFFICIAL_BACKUP_PATH = (
    OFFICIAL_DATASET_PATH.parent / "backups" / OFFICIAL_DATASET_PATH.stem
)

AFFECTED_IMPORT_MARKERS = {
    "src.market_structure.mtf_regime_filter",
    "src.market_structure.directional_context_filter_v3",
    "src.market_structure.directional_context_filter_v3_1",
}
LONG_REVALIDATION_SOURCES = (
    Path("src/long_side/long_historical_baseline_backtest_v1.py"),
    Path("src/long_side/long_oos_baseline_validation_v1.py"),
    Path("src/long_side/long_walk_forward_baseline_validation_v1.py"),
    Path("src/long_side/long_cost_aware_baseline_validation_v1.py"),
    Path("src/long_side/long_monte_carlo_baseline_validation_v1.py"),
    Path("src/long_side/long_baseline_readiness_gate_v1.py"),
)

PASSING_WALK_FORWARD_DECISIONS = {
    "WALK_FORWARD_PASS",
    "WALK_FORWARD_WEAK_PASS",
}
PASSING_COST_DECISIONS = {
    "COST_AWARE_PASS",
    "COST_AWARE_WEAK_PASS",
}
PASSING_MONTE_CARLO_DECISIONS = {
    "MONTE_CARLO_PASS",
    "MONTE_CARLO_EDGE_WITH_SEQUENCE_RISK",
    "MONTE_CARLO_WEAK_PASS_WITH_SEQUENCE_RISK",
}

SAFETY_FLAGS = {
    "signal_generation_enabled": False,
    "forward_observation_allowed": False,
    "official_dataset_write_allowed": False,
    "evidence_persistence_allowed": False,
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "live_alerts_allowed": False,
    "market_execution_allowed": False,
    "exchange_execution_allowed": False,
    "automation_allowed": False,
    "execution_allowed": False,
    "openclaw_operational_integration_allowed": False,
}


def build_short_config() -> BacktestConfig:
    return BacktestConfig(
        initial_capital=1000.0,
        risk_per_trade=0.01,
        risk_reward=2.5,
        fee_rate=0.001,
        spread_rate=0.0002,
        atr_period=14,
        atr_multiplier=1.25,
        max_holding_bars=48,
        direction_mode="short_only",
    )


def short_mtf_with_directional_context_v3_1(
    df: pd.DataFrame,
    index: int,
    config: Any = None,
) -> str:
    base_signal = fib_v5_short_with_mtf_filter(df, index, config)
    if base_signal != "SHORT":
        return "NONE"
    return "SHORT" if bool(df.iloc[index].get("short_allowed_v3_1", False)) else "NONE"


def build_walk_forward_splits() -> list[dict[str, str]]:
    starts = (
        ("2022-01-01", "2023-01-01", "2023-01-01", "2023-04-01"),
        ("2022-04-01", "2023-04-01", "2023-04-01", "2023-07-01"),
        ("2022-07-01", "2023-07-01", "2023-07-01", "2023-10-01"),
        ("2022-10-01", "2023-10-01", "2023-10-01", "2024-01-01"),
        ("2023-01-01", "2024-01-01", "2024-01-01", "2024-04-01"),
        ("2023-04-01", "2024-04-01", "2024-04-01", "2024-07-01"),
        ("2023-07-01", "2024-07-01", "2024-07-01", "2024-10-01"),
        ("2023-10-01", "2024-10-01", "2024-10-01", "2025-01-01"),
        ("2024-01-01", "2025-01-01", "2025-01-01", "2025-04-01"),
        ("2024-04-01", "2025-04-01", "2025-04-01", "2025-07-01"),
        ("2024-07-01", "2025-07-01", "2025-07-01", "2025-10-01"),
        ("2024-10-01", "2025-10-01", "2025-10-01", "2026-01-01"),
    )
    rows: list[dict[str, str]] = []
    for train_start, train_end, test_start, test_end in starts:
        rows.append(
            {
                "split_name": (
                    f"WF_{train_start[:7].replace('-', '')}_"
                    f"{train_end[:7].replace('-', '')}_TO_"
                    f"{test_start[:7].replace('-', '')}_"
                    f"{test_end[:7].replace('-', '')}"
                ),
                "train_start": train_start,
                "train_end": train_end,
                "test_start": test_start,
                "test_end": test_end,
            }
        )
    return rows


def file_sha256(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dataset_path(symbol: str, timeframe: str) -> Path:
    base_name = f"{symbol.lower()}_2022_2025"
    return DATA_DIR / f"{base_name}_{timeframe}.csv"


def profile_dataset(symbol: str, timeframe: str, path: Path) -> dict[str, Any]:
    base = {
        "symbol": symbol,
        "timeframe": timeframe,
        "path": str(path),
        "exists": path.exists() and path.is_file(),
        "size_bytes": path.stat().st_size if path.exists() and path.is_file() else 0,
        "sha256": file_sha256(path),
        "rows": 0,
        "first_open_timestamp": "",
        "last_open_timestamp": "",
        "invalid_timestamp_rows": 0,
        "duplicate_timestamp_rows": 0,
        "invalid_ohlc_rows": 0,
        "minimum_rows_required": MIN_ROWS[timeframe],
        "coverage_start_required": START_DATE,
        "coverage_end_required": str(EXPECTED_LAST_OPEN[timeframe]),
        "dataset_valid": False,
        "validation_note": "missing_dataset",
    }

    if not base["exists"]:
        return base

    try:
        raw = pd.read_csv(path)
        raw.columns = [str(column).strip().lower() for column in raw.columns]
        if "open_time" in raw.columns and "timestamp" not in raw.columns:
            raw = raw.rename(columns={"open_time": "timestamp"})

        required = {"timestamp", "open", "high", "low", "close"}
        missing = sorted(required - set(raw.columns))
        if missing:
            base["validation_note"] = "missing_columns=" + ",".join(missing)
            return base

        timestamps = pd.to_datetime(raw["timestamp"], errors="coerce")
        invalid_timestamps = int(timestamps.isna().sum())
        duplicate_timestamps = int(timestamps.dropna().duplicated().sum())

        numeric = raw[["open", "high", "low", "close"]].apply(
            pd.to_numeric,
            errors="coerce",
        )
        valid_prices = numeric.notna().all(axis=1) & numeric.gt(0).all(axis=1)
        valid_ranges = (
            numeric["high"].ge(numeric[["open", "close"]].max(axis=1))
            & numeric["low"].le(numeric[["open", "close"]].min(axis=1))
            & numeric["high"].ge(numeric["low"])
        )
        invalid_ohlc = int((~(valid_prices & valid_ranges)).sum())

        valid_ts = timestamps.dropna().sort_values()
        first_timestamp = valid_ts.iloc[0] if not valid_ts.empty else pd.NaT
        last_timestamp = valid_ts.iloc[-1] if not valid_ts.empty else pd.NaT

        row_count = int(len(raw))
        coverage_valid = bool(
            pd.notna(first_timestamp)
            and pd.notna(last_timestamp)
            and first_timestamp <= pd.Timestamp(START_DATE)
            and last_timestamp >= EXPECTED_LAST_OPEN[timeframe]
        )
        dataset_valid = bool(
            row_count >= MIN_ROWS[timeframe]
            and invalid_timestamps == 0
            and duplicate_timestamps == 0
            and invalid_ohlc == 0
            and coverage_valid
        )

        base.update(
            {
                "rows": row_count,
                "first_open_timestamp": str(first_timestamp),
                "last_open_timestamp": str(last_timestamp),
                "invalid_timestamp_rows": invalid_timestamps,
                "duplicate_timestamp_rows": duplicate_timestamps,
                "invalid_ohlc_rows": invalid_ohlc,
                "dataset_valid": dataset_valid,
                "validation_note": "valid" if dataset_valid else "profile_failed",
            }
        )
        return base
    except Exception as exc:
        base["validation_note"] = f"read_error={type(exc).__name__}:{exc}"
        return base


def prepare_dataset_manifest(allow_download: bool = False) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for symbol in SYMBOLS:
        for timeframe in TIMEFRAMES:
            path = dataset_path(symbol, timeframe)
            if allow_download and not path.exists():
                from src.workflows.validate_long_v2_candidate_robust import (
                    download_binance_klines_range,
                )

                download_binance_klines_range(
                    symbol=symbol,
                    interval=timeframe,
                    start_date=START_DATE,
                    end_date=END_DATE,
                    output_path=path,
                )
            rows.append(profile_dataset(symbol, timeframe, path))
    return pd.DataFrame(rows)


def _set_feature_timing_mode(
    frame: pd.DataFrame,
    timeframe: str,
    mode: str,
) -> pd.DataFrame:
    result = frame.copy()
    source_column = f"source_open_timestamp_{timeframe}"
    if source_column not in result.columns:
        raise ValueError(f"Missing source timestamp column: {source_column}")
    if mode == MODE_LEGACY:
        result["timestamp"] = pd.to_datetime(result[source_column], errors="coerce")
    elif mode != MODE_CORRECTED:
        raise ValueError(f"Unsupported timing mode: {mode}")
    return result.sort_values("timestamp").reset_index(drop=True)


def build_mtf_regime_context(
    csv_15m: Path,
    csv_1h: Path,
    csv_4h: Path,
    mode: str,
) -> pd.DataFrame:
    entry = load_ohlcv(csv_15m)
    h1 = _set_feature_timing_mode(build_regime_df(csv_1h, "1h"), "1h", mode)
    h4 = _set_feature_timing_mode(build_regime_df(csv_4h, "4h"), "4h", mode)

    result = pd.merge_asof(
        entry.sort_values("timestamp"),
        h1,
        on="timestamp",
        direction="backward",
    )
    result = pd.merge_asof(
        result.sort_values("timestamp"),
        h4,
        on="timestamp",
        direction="backward",
    )
    result["regime_1h"] = result["regime_1h"].fillna("UNKNOWN")
    result["regime_4h"] = result["regime_4h"].fillna("UNKNOWN")
    return result


def build_directional_context(
    csv_15m: Path,
    csv_1h: Path,
    csv_4h: Path,
    mode: str,
) -> pd.DataFrame:
    entry = normalize_ohlcv_columns(pd.read_csv(csv_15m))
    h1 = _set_feature_timing_mode(
        prepare_directional_features(pd.read_csv(csv_1h), "1h"),
        "1h",
        mode,
    )
    h4 = _set_feature_timing_mode(
        prepare_directional_features(pd.read_csv(csv_4h), "4h"),
        "4h",
        mode,
    )

    result = pd.merge_asof(
        entry.sort_values("timestamp"),
        h1,
        on="timestamp",
        direction="backward",
    )
    result = pd.merge_asof(
        result.sort_values("timestamp"),
        h4,
        on="timestamp",
        direction="backward",
    )
    result["bias_1h_v3"] = result.apply(
        lambda row: classify_tf_bias(row, "1h"), axis=1
    )
    result["bias_4h_v3"] = result.apply(
        lambda row: classify_tf_bias(row, "4h"), axis=1
    )
    result["directional_context_v3"] = result.apply(
        classify_directional_context_v3,
        axis=1,
    )
    result["long_allowed_v3"] = result["directional_context_v3"].map(
        long_allowed_by_directional_context_v3
    )
    result["short_allowed_v3"] = result["directional_context_v3"].map(
        short_allowed_by_directional_context_v3
    )
    return add_directional_context_v3_1_columns(result)


def build_combined_context_dataset(
    csv_15m: Path,
    csv_1h: Path,
    csv_4h: Path,
    mode: str,
) -> pd.DataFrame:
    mtf = build_mtf_regime_context(csv_15m, csv_1h, csv_4h, mode)
    directional = build_directional_context(csv_15m, csv_1h, csv_4h, mode)

    directional_columns = [
        "timestamp",
        "bias_1h_v3",
        "bias_4h_v3",
        "directional_context_v3",
        "long_allowed_v3",
        "short_allowed_v3",
        "long_context_decision_v3_1",
        "short_context_decision_v3_1",
        "long_allowed_v3_1",
        "short_allowed_v3_1",
    ]
    result = pd.merge_asof(
        mtf.sort_values("timestamp"),
        directional[directional_columns].sort_values("timestamp"),
        on="timestamp",
        direction="nearest",
        tolerance=pd.Timedelta(minutes=1),
    )

    text_defaults = {
        "bias_1h_v3": "UNKNOWN",
        "bias_4h_v3": "UNKNOWN",
        "directional_context_v3": "NO_TRADE",
        "long_context_decision_v3_1": "MONITOR_NOT_ALLOWED",
        "short_context_decision_v3_1": "MONITOR_NOT_ALLOWED",
    }
    for column, default in text_defaults.items():
        result[column] = result[column].fillna(default)
    for column in (
        "long_allowed_v3",
        "short_allowed_v3",
        "long_allowed_v3_1",
        "short_allowed_v3_1",
    ):
        result[column] = result[column].fillna(False).astype(bool)

    result["mtf_timing_mode"] = mode
    return result.reset_index(drop=True)


def build_context_shift_diagnostic(
    symbol: str,
    corrected: pd.DataFrame,
    legacy: pd.DataFrame,
) -> dict[str, Any]:
    compare_columns = [
        "timestamp",
        "regime_1h",
        "regime_4h",
        "bias_1h_v3",
        "bias_4h_v3",
        "directional_context_v3",
        "short_allowed_v3_1",
    ]
    aligned = corrected[compare_columns].merge(
        legacy[compare_columns],
        on="timestamp",
        how="inner",
        suffixes=("_corrected", "_legacy"),
        validate="one_to_one",
    )

    row: dict[str, Any] = {
        "symbol": symbol,
        "corrected_rows": int(len(corrected)),
        "legacy_rows": int(len(legacy)),
        "rows_compared": int(len(aligned)),
    }
    for column in compare_columns[1:]:
        row[f"{column}_changed_rows"] = int(
            aligned[f"{column}_corrected"].ne(aligned[f"{column}_legacy"]).sum()
        )

    for mode_name, frame in (("corrected", corrected), ("legacy", legacy)):
        for timeframe in ("1h", "4h"):
            available_column = f"feature_available_at_{timeframe}"
            available = pd.to_datetime(frame[available_column], errors="coerce")
            timestamps = pd.to_datetime(frame["timestamp"], errors="coerce")
            row[f"{mode_name}_early_exposure_rows_{timeframe}"] = int(
                (available.notna() & timestamps.lt(available)).sum()
            )

    row["corrected_closed_candle_invariant_passed"] = bool(
        row["corrected_early_exposure_rows_1h"] == 0
        and row["corrected_early_exposure_rows_4h"] == 0
    )
    row["legacy_control_reproduces_lookahead"] = bool(
        row["legacy_early_exposure_rows_1h"] > 0
        and row["legacy_early_exposure_rows_4h"] > 0
    )
    return row


def _official_short_candidate() -> dict[str, Any]:
    candidates = [
        candidate
        for candidate in build_walk_forward_candidates()
        if bool(candidate.get("is_official"))
    ]
    if len(candidates) != 1:
        raise ValueError("Expected exactly one official fixed SHORT candidate.")
    return candidates[0]


def run_short_windows(
    symbol: str,
    mode: str,
    market_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    candidate = _official_short_candidate()
    config = build_short_config()
    metric_rows: list[dict[str, Any]] = []
    trade_frames: list[pd.DataFrame] = []

    for split in build_walk_forward_splits():
        test_df = slice_by_date(
            market_df,
            split["test_start"],
            split["test_end"],
        )
        trades, summary = run_candidate_backtest(
            df=test_df,
            strategy_func=short_mtf_with_directional_context_v3_1,
            base_config=config,
            candidate=candidate,
        )
        metric_rows.append(
            {
                "symbol": symbol,
                "timing_mode": mode,
                "split_name": split["split_name"],
                "test_start": split["test_start"],
                "test_end": split["test_end"],
                "test_trades": int(summary.get("total_trades", 0)),
                "test_return": float(summary.get("total_return_pct", 0.0)),
                "test_profit_factor": summary.get("profit_factor"),
                "test_expectancy_r": float(summary.get("expectancy_r", 0.0)),
                "test_drawdown": float(summary.get("max_drawdown_pct", 0.0)),
                "test_win_rate": float(summary.get("win_rate", 0.0)),
            }
        )
        if not trades.empty:
            trades = trades.copy()
            trades["symbol"] = symbol
            trades["timing_mode"] = mode
            trades["split_name"] = split["split_name"]
            trades["test_start"] = split["test_start"]
            trades["test_end"] = split["test_end"]
            trade_frames.append(trades)

    metrics = pd.DataFrame(metric_rows)
    trades = (
        pd.concat(trade_frames, ignore_index=True)
        if trade_frames
        else pd.DataFrame()
    )
    return metrics, trades


def aggregate_short_metrics(window_metrics: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for mode, group in window_metrics.groupby("timing_mode", sort=True):
        returns = pd.to_numeric(group["test_return"], errors="coerce").fillna(0.0)
        pfs = pd.to_numeric(group["test_profit_factor"], errors="coerce")
        trades = pd.to_numeric(group["test_trades"], errors="coerce").fillna(0)
        row = {
            "timing_mode": mode,
            "test_windows": int(len(group)),
            "total_test_trades": int(trades.sum()),
            "compound_test_return": float((1 + returns).prod() - 1),
            "avg_test_return": float(returns.mean()),
            "median_test_return": float(returns.median()),
            "avg_test_profit_factor": (
                float(pfs.dropna().mean()) if not pfs.dropna().empty else 0.0
            ),
            "avg_test_expectancy_r": float(
                pd.to_numeric(group["test_expectancy_r"], errors="coerce").mean()
            ),
            "worst_test_drawdown": float(
                pd.to_numeric(group["test_drawdown"], errors="coerce").min()
            ),
            "positive_tests": int((returns > 0).sum()),
            "negative_tests": int((returns <= 0).sum()),
            "positive_test_rate": float((returns > 0).mean()),
        }
        row["walk_forward_decision"] = classify_walk_forward_result(pd.Series(row))
        rows.append(row)
    return pd.DataFrame(rows)


def compare_short_aggregates(aggregate: pd.DataFrame) -> pd.DataFrame:
    corrected = aggregate[aggregate["timing_mode"].eq(MODE_CORRECTED)]
    legacy = aggregate[aggregate["timing_mode"].eq(MODE_LEGACY)]
    if corrected.empty or legacy.empty:
        return pd.DataFrame()
    corrected_row = corrected.iloc[0]
    legacy_row = legacy.iloc[0]
    return pd.DataFrame(
        [
            {
                "candidate_id": SHORT_CANDIDATE,
                "legacy_total_trades": int(legacy_row["total_test_trades"]),
                "corrected_total_trades": int(corrected_row["total_test_trades"]),
                "trade_count_delta": int(
                    corrected_row["total_test_trades"]
                    - legacy_row["total_test_trades"]
                ),
                "legacy_compound_return": float(legacy_row["compound_test_return"]),
                "corrected_compound_return": float(
                    corrected_row["compound_test_return"]
                ),
                "compound_return_delta": float(
                    corrected_row["compound_test_return"]
                    - legacy_row["compound_test_return"]
                ),
                "legacy_avg_profit_factor": float(
                    legacy_row["avg_test_profit_factor"]
                ),
                "corrected_avg_profit_factor": float(
                    corrected_row["avg_test_profit_factor"]
                ),
                "profit_factor_delta": float(
                    corrected_row["avg_test_profit_factor"]
                    - legacy_row["avg_test_profit_factor"]
                ),
                "legacy_expectancy_r": float(legacy_row["avg_test_expectancy_r"]),
                "corrected_expectancy_r": float(
                    corrected_row["avg_test_expectancy_r"]
                ),
                "expectancy_r_delta": float(
                    corrected_row["avg_test_expectancy_r"]
                    - legacy_row["avg_test_expectancy_r"]
                ),
                "legacy_decision": str(legacy_row["walk_forward_decision"]),
                "corrected_decision": str(corrected_row["walk_forward_decision"]),
            }
        ]
    )


def build_short_cost_metrics(
    trades: pd.DataFrame,
    window_metrics: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, Any]] = []
    stress_adjusted_frames: list[pd.DataFrame] = []
    window_keys = window_metrics[
        ["timing_mode", "symbol", "split_name"]
    ].drop_duplicates()

    for _, key in window_keys.iterrows():
        mode = str(key["timing_mode"])
        symbol = str(key["symbol"])
        split_name = str(key["split_name"])
        if trades.empty:
            group = pd.DataFrame()
        else:
            group = trades[
                trades["timing_mode"].astype(str).eq(mode)
                & trades["symbol"].astype(str).eq(symbol)
                & trades["split_name"].astype(str).eq(split_name)
            ].copy()
        for profile in build_cost_profiles():
            adjusted = apply_cost_profile_to_trades(group, profile)
            summary = summarize_cost_adjusted_trades(adjusted, profile)
            rows.append(
                {
                    "timing_mode": mode,
                    "symbol": symbol,
                    "split_name": split_name,
                    **summary,
                }
            )
            if mode == MODE_CORRECTED and profile.name == STRESS_PROFILE:
                stress_adjusted_frames.append(adjusted)

    windows = pd.DataFrame(rows)
    aggregate_frames: list[pd.DataFrame] = []
    for mode, group in windows.groupby("timing_mode", sort=True):
        mode_aggregate = aggregate_cost_summaries(group)
        mode_aggregate.insert(0, "timing_mode", mode)
        aggregate_frames.append(mode_aggregate)
    aggregate = (
        pd.concat(aggregate_frames, ignore_index=True)
        if aggregate_frames
        else pd.DataFrame()
    )
    stress_adjusted = (
        pd.concat(stress_adjusted_frames, ignore_index=True)
        if stress_adjusted_frames
        else pd.DataFrame()
    )
    return windows, aggregate, stress_adjusted


def imported_modules(path: Path) -> set[str]:
    if not path.exists() or not path.is_file():
        return set()
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def build_long_dependency_audit() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in LONG_REVALIDATION_SOURCES:
        modules = imported_modules(path)
        affected = sorted(
            module
            for module in modules
            if any(
                module == marker or module.startswith(marker + ".")
                for marker in AFFECTED_IMPORT_MARKERS
            )
        )
        rows.append(
            {
                "source_path": str(path),
                "source_exists": path.exists(),
                "direct_import_count": len(modules),
                "affected_mtf_imports": ";".join(affected),
                "independent_of_affected_mtf_modules": path.exists() and not affected,
                "classification": (
                    "UNAFFECTED_15M_STRUCTURAL_CHAIN"
                    if path.exists() and not affected
                    else "AFFECTED_OR_UNRESOLVED"
                ),
            }
        )
    return pd.DataFrame(rows)


def _build_check(
    name: str,
    passed: bool,
    severity: str,
    details: str,
) -> dict[str, Any]:
    return {
        "check_name": name,
        "passed": bool(passed),
        "severity": severity,
        "details": details,
        "blocker": severity == "ERROR" and not bool(passed),
    }


def _official_artifacts_absent() -> bool:
    return not any(
        path.exists()
        for path in (
            OFFICIAL_DATASET_PATH,
            OFFICIAL_TEMP_PATH,
            OFFICIAL_LOCK_PATH,
            OFFICIAL_MANIFEST_PATH,
            OFFICIAL_BACKUP_PATH,
        )
    )


def _write_outputs(outputs: dict[str, pd.DataFrame]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    for name, frame in outputs.items():
        frame.to_csv(REPORTS_DIR / f"{name}_v1.csv", index=False)


def _preflight_result(manifest: pd.DataFrame) -> dict[str, pd.DataFrame]:
    datasets_valid = bool(
        len(manifest) == len(SYMBOLS) * len(TIMEFRAMES)
        and manifest["dataset_valid"].astype(bool).all()
    )
    checks = pd.DataFrame(
        [
            _build_check(
                "all_revalidation_datasets_valid",
                datasets_valid,
                "ERROR",
                f"valid={int(manifest['dataset_valid'].astype(bool).sum())}/{len(manifest)}",
            ),
            _build_check(
                "official_forward_artifacts_absent",
                _official_artifacts_absent(),
                "ERROR",
                str(OFFICIAL_DATASET_PATH),
            ),
        ]
    )
    summary = pd.DataFrame(
        [
            {
                "phase": "10.42R.2",
                "run_mode": "PREFLIGHT_ONLY",
                "datasets_valid": datasets_valid,
                "scientific_revalidation_completed": False,
                "validation_passed": datasets_valid
                and not checks["blocker"].astype(bool).any(),
                "recommended_action": (
                    "RUN_FULL_REVALIDATION"
                    if datasets_valid
                    else "PROVIDE_DATASETS_OR_RERUN_WITH_ALLOW_DOWNLOAD"
                ),
                **SAFETY_FLAGS,
            }
        ]
    )
    outputs = {
        "summary": summary,
        "checks": checks,
        "dataset_manifest": manifest,
    }
    _write_outputs(outputs)
    return outputs


def run_closed_candle_mtf_revalidation(
    allow_download: bool = False,
    preflight_only: bool = False,
    simulations: int = 10_000,
) -> dict[str, pd.DataFrame]:
    manifest = prepare_dataset_manifest(allow_download=allow_download)
    datasets_valid = bool(
        len(manifest) == len(SYMBOLS) * len(TIMEFRAMES)
        and manifest["dataset_valid"].astype(bool).all()
    )
    if preflight_only or not datasets_valid:
        return _preflight_result(manifest)

    diagnostics: list[dict[str, Any]] = []
    short_window_frames: list[pd.DataFrame] = []
    short_trade_frames: list[pd.DataFrame] = []
    errors: list[dict[str, str]] = []

    for symbol in SYMBOLS:
        paths = {timeframe: dataset_path(symbol, timeframe) for timeframe in TIMEFRAMES}
        try:
            corrected = build_combined_context_dataset(
                paths["15m"], paths["1h"], paths["4h"], MODE_CORRECTED
            )
            legacy = build_combined_context_dataset(
                paths["15m"], paths["1h"], paths["4h"], MODE_LEGACY
            )
            diagnostics.append(
                build_context_shift_diagnostic(symbol, corrected, legacy)
            )
            for mode, frame in ((MODE_CORRECTED, corrected), (MODE_LEGACY, legacy)):
                metrics, trades = run_short_windows(symbol, mode, frame)
                short_window_frames.append(metrics)
                if not trades.empty:
                    short_trade_frames.append(trades)
        except Exception as exc:
            errors.append(
                {
                    "scope": "SHORT_REVALIDATION",
                    "symbol": symbol,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    context_diagnostics = pd.DataFrame(diagnostics)
    short_windows = (
        pd.concat(short_window_frames, ignore_index=True)
        if short_window_frames
        else pd.DataFrame()
    )
    short_trades = (
        pd.concat(short_trade_frames, ignore_index=True)
        if short_trade_frames
        else pd.DataFrame()
    )
    short_aggregate = aggregate_short_metrics(short_windows)
    short_comparison = compare_short_aggregates(short_aggregate)

    if short_windows.empty:
        short_cost_windows, short_cost_aggregate, stress_adjusted = (
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame(),
        )
    else:
        short_cost_windows, short_cost_aggregate, stress_adjusted = (
            build_short_cost_metrics(short_trades, short_windows)
        )

    if stress_adjusted.empty:
        monte_carlo_summary = pd.DataFrame(
            [
                {
                    "cost_profile": STRESS_PROFILE,
                    "simulations": 0,
                    "sample_trades": 0,
                    "decision": "TOO_FEW_TRADES",
                }
            ]
        )
    else:
        _, mc_summary = run_monte_carlo_for_profile(
            stress_adjusted,
            STRESS_PROFILE,
            MonteCarloConfig(
                simulations=simulations,
                random_seed=42,
                min_trades=30,
                sample_with_replacement=True,
            ),
        )
        monte_carlo_summary = pd.DataFrame([mc_summary])

    long_dependency = build_long_dependency_audit()
    long_sources_unaffected = bool(
        not long_dependency.empty
        and long_dependency["independent_of_affected_mtf_modules"].astype(bool).all()
    )
    try:
        long_result = validate_long_baseline_readiness_gate()
        long_summary = long_result["summary"].copy()
        long_readiness = long_result["readiness_gate"].copy()
    except Exception as exc:
        errors.append(
            {
                "scope": "LONG_CONSISTENCY_REVALIDATION",
                "symbol": "BTCUSDT",
                "error": f"{type(exc).__name__}: {exc}",
            }
        )
        long_summary = pd.DataFrame()
        long_readiness = pd.DataFrame()

    manifest = manifest.copy()
    manifest["size_bytes_after"] = manifest["path"].map(
        lambda value: (
            Path(str(value)).stat().st_size
            if Path(str(value)).exists() and Path(str(value)).is_file()
            else 0
        )
    )
    manifest["sha256_after"] = manifest["path"].map(
        lambda value: file_sha256(Path(str(value)))
    )
    manifest["dataset_unchanged_during_run"] = (
        manifest["size_bytes_after"].eq(manifest["size_bytes"])
        & manifest["sha256_after"].eq(manifest["sha256"])
    )
    datasets_unchanged = bool(
        manifest["dataset_unchanged_during_run"].astype(bool).all()
    )

    expected_short_windows = len(SYMBOLS) * len(build_walk_forward_splits()) * 2
    corrected_invariant = bool(
        not context_diagnostics.empty
        and context_diagnostics[
            "corrected_closed_candle_invariant_passed"
        ].astype(bool).all()
    )
    legacy_control = bool(
        not context_diagnostics.empty
        and context_diagnostics["legacy_control_reproduces_lookahead"].astype(bool).all()
    )
    short_run_complete = bool(
        len(short_windows) == expected_short_windows and not errors
    )
    long_validation_passed = bool(
        not long_summary.empty
        and bool(long_summary.iloc[0].get("validation_passed", False))
    )

    primary_row = long_readiness[
        long_readiness.get("candidate_id", pd.Series(dtype=str)).astype(str).eq(
            LONG_PRIMARY
        )
    ]
    secondary_row = long_readiness[
        long_readiness.get("candidate_id", pd.Series(dtype=str)).astype(str).eq(
            LONG_SECONDARY
        )
    ]
    long_decisions_match = bool(
        not primary_row.empty
        and not secondary_row.empty
        and str(primary_row.iloc[0].get("readiness_decision", ""))
        == "LONG_FORWARD_OBSERVATION_CANDIDATE"
        and str(secondary_row.iloc[0].get("readiness_decision", ""))
        == "LONG_SECONDARY_WATCHLIST"
    )

    corrected_aggregate = short_aggregate[
        short_aggregate.get("timing_mode", pd.Series(dtype=str)).eq(MODE_CORRECTED)
    ]
    corrected_cost = short_cost_aggregate[
        short_cost_aggregate.get("timing_mode", pd.Series(dtype=str)).eq(MODE_CORRECTED)
        & short_cost_aggregate.get("cost_profile", pd.Series(dtype=str)).eq(
            STRESS_PROFILE
        )
    ]
    corrected_wf_decision = (
        str(corrected_aggregate.iloc[0]["walk_forward_decision"])
        if not corrected_aggregate.empty
        else "NOT_RUN"
    )
    corrected_cost_decision = (
        str(corrected_cost.iloc[0]["cost_decision"])
        if not corrected_cost.empty
        else "NOT_RUN"
    )
    corrected_mc_decision = str(
        monte_carlo_summary.iloc[0].get("decision", "NOT_RUN")
    )

    scientific_completed = bool(
        datasets_valid
        and datasets_unchanged
        and corrected_invariant
        and legacy_control
        and short_run_complete
        and long_sources_unaffected
        and long_validation_passed
        and long_decisions_match
    )
    short_all_gates_pass = bool(
        scientific_completed
        and corrected_wf_decision in PASSING_WALK_FORWARD_DECISIONS
        and corrected_cost_decision in PASSING_COST_DECISIONS
        and corrected_mc_decision in PASSING_MONTE_CARLO_DECISIONS
    )
    if not scientific_completed:
        short_status = "REVALIDATION_INCOMPLETE"
    elif short_all_gates_pass:
        short_status = "REVALIDATED_RESEARCH_CANDIDATE"
    elif "TOO_FEW_TRADES" in {
        corrected_wf_decision,
        corrected_cost_decision,
        corrected_mc_decision,
    }:
        short_status = "REVALIDATED_INSUFFICIENT_EVIDENCE"
    else:
        short_status = "REVALIDATED_REJECTED"

    long_status = (
        "CERTIFIED_UNAFFECTED_AND_CONSISTENCY_REVALIDATED"
        if scientific_completed
        else "REVALIDATION_INCOMPLETE"
    )

    checks_rows = [
        _build_check(
            "all_revalidation_datasets_valid",
            datasets_valid,
            "ERROR",
            f"valid={int(manifest['dataset_valid'].astype(bool).sum())}/{len(manifest)}",
        ),
        _build_check(
            "dataset_hashes_stable_during_run",
            datasets_unchanged,
            "ERROR",
            "All nine input SHA-256 values must remain unchanged.",
        ),
        _build_check(
            "corrected_context_has_no_early_mtf_exposure",
            corrected_invariant,
            "ERROR",
            "1H/4H availability must be <= every consuming 15m timestamp.",
        ),
        _build_check(
            "legacy_control_reproduces_original_lookahead",
            legacy_control,
            "ERROR",
            "Diagnostic-only legacy mode must expose early 1H/4H rows.",
        ),
        _build_check(
            "all_short_fixed_oos_windows_completed",
            short_run_complete,
            "ERROR",
            f"actual={len(short_windows)} expected={expected_short_windows}",
        ),
        _build_check(
            "long_chain_independent_of_affected_mtf_modules",
            long_sources_unaffected,
            "ERROR",
            "Primary and secondary LONG candidates use the 15m structural chain.",
        ),
        _build_check(
            "long_readiness_chain_revalidated",
            long_validation_passed and long_decisions_match,
            "ERROR",
            "Phase 8.11 decisions must reproduce without execution approval.",
        ),
        _build_check(
            "short_sequence_risk_gate_executed",
            corrected_mc_decision != "NOT_RUN",
            "WARNING" if corrected_mc_decision == "TOO_FEW_TRADES" else "INFO",
            corrected_mc_decision,
        ),
        _build_check(
            "official_forward_artifacts_absent",
            _official_artifacts_absent(),
            "ERROR",
            str(OFFICIAL_DATASET_PATH),
        ),
        _build_check(
            "all_execution_permissions_false",
            not any(SAFETY_FLAGS.values()),
            "ERROR",
            str(SAFETY_FLAGS),
        ),
    ]
    checks = pd.DataFrame(checks_rows)
    validation_passed = bool(
        scientific_completed and not checks["blocker"].astype(bool).any()
    )

    candidate_decisions = pd.DataFrame(
        [
            {
                "candidate_id": SHORT_CANDIDATE,
                "mtf_dependency": "AFFECTED_REVALIDATED_WITH_CLOSED_CANDLES",
                "current_status": short_status,
                "historical_metrics_certified": scientific_completed,
                "strategy_gates_passed": short_all_gates_pass,
                "walk_forward_decision": corrected_wf_decision,
                "stress_cost_decision": corrected_cost_decision,
                "sequence_risk_decision": corrected_mc_decision,
                **SAFETY_FLAGS,
            },
            {
                "candidate_id": LONG_PRIMARY,
                "mtf_dependency": "UNAFFECTED_15M_STRUCTURAL_CHAIN",
                "current_status": long_status,
                "historical_metrics_certified": scientific_completed,
                "strategy_gates_passed": long_validation_passed,
                "walk_forward_decision": "PHASE_8_CHAIN_REPRODUCED",
                "stress_cost_decision": "PHASE_8_CHAIN_REPRODUCED",
                "sequence_risk_decision": "PHASE_8_CHAIN_REPRODUCED",
                **SAFETY_FLAGS,
            },
            {
                "candidate_id": LONG_SECONDARY,
                "mtf_dependency": "UNAFFECTED_15M_STRUCTURAL_CHAIN",
                "current_status": long_status,
                "historical_metrics_certified": scientific_completed,
                "strategy_gates_passed": long_validation_passed,
                "walk_forward_decision": "PHASE_8_CHAIN_REPRODUCED",
                "stress_cost_decision": "PHASE_8_CHAIN_REPRODUCED",
                "sequence_risk_decision": "PHASE_8_CHAIN_REPRODUCED",
                **SAFETY_FLAGS,
            },
        ]
    )

    summary = pd.DataFrame(
        [
            {
                "phase": "10.42R.2",
                "run_mode": "FULL_REVALIDATION",
                "datasets_valid": datasets_valid,
                "short_candidate_status": short_status,
                "long_candidate_status": long_status,
                "short_corrected_walk_forward_decision": corrected_wf_decision,
                "short_corrected_stress_cost_decision": corrected_cost_decision,
                "short_corrected_sequence_risk_decision": corrected_mc_decision,
                "historical_metrics_certified": scientific_completed,
                "scientific_revalidation_completed": scientific_completed,
                "phase_10_43_design_review_allowed": scientific_completed,
                "openclaw_read_only_status_design_allowed": scientific_completed,
                "official_dataset_exists": OFFICIAL_DATASET_PATH.exists(),
                "official_evidence_rows_written": 0,
                "error_rows": len(errors),
                "total_checks": len(checks),
                "blocker_count": int(checks["blocker"].astype(bool).sum()),
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_10_42R_2_CLOSED_CANDLE_MTF_REVALIDATION_COMPLETED"
                    if validation_passed
                    else "PHASE_10_42R_2_CLOSED_CANDLE_MTF_REVALIDATION_FAILED"
                ),
                "recommended_next_phase": (
                    "PHASE_10_42R_3_OPENCLAW_READ_ONLY_RESEARCH_STATUS_CONTRACT_V1"
                    if validation_passed
                    else "REMEDIATE_REVALIDATION_BLOCKERS"
                ),
                **SAFETY_FLAGS,
                "total_project_completed": False,
            }
        ]
    )

    outputs = {
        "summary": summary,
        "checks": checks,
        "dataset_manifest": manifest,
        "context_shift_diagnostics": context_diagnostics,
        "short_window_metrics": short_windows,
        "short_aggregate_metrics": short_aggregate,
        "short_legacy_vs_corrected": short_comparison,
        "short_cost_window_metrics": short_cost_windows,
        "short_cost_aggregate": short_cost_aggregate,
        "short_monte_carlo_summary": monte_carlo_summary,
        "long_source_dependency_audit": long_dependency,
        "long_readiness_revalidation": long_readiness,
        "candidate_decisions": candidate_decisions,
        "errors": pd.DataFrame(errors, columns=["scope", "symbol", "error"]),
    }
    _write_outputs(outputs)
    return outputs
