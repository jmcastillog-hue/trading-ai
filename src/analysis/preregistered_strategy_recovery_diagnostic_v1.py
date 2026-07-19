from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.execution.normalized_cost_accounting_v1 import (
    DRAWDOWN_ORDER_CONTRACT,
    WINDOW_UNIT_CONTRACT,
    calculate_max_drawdown_r,
    order_trades_for_realized_drawdown,
)


DIAGNOSTIC_SIGNAL_FAMILY = (
    "RETIRED_TARGET_SHORT_FIB_V5_MTF_V3_1_FIXED_RR_2_5"
)
DIAGNOSTIC_STATUS = "DESCRIPTIVE_ONLY_NO_SELECTION_NO_RECLASSIFICATION"
VOLATILITY_METHOD = "COHORT_GLOBAL_SIGNAL_ATR_OVER_SIGNAL_CLOSE_QUANTILES_V1"
TREND_REGIME_METHOD = "CLOSED_CANDLE_REGIME_1H_X_REGIME_4H_AT_SIGNAL_V1"
SLICE_DIMENSIONS = (
    "symbol",
    "calendar_year",
    "volatility_tercile",
    "trend_regime",
    "signal_family",
)
VOLATILITY_TERCILES = ("LOW", "MID", "HIGH")

REQUIRED_NORMALIZED_COLUMNS = {
    "source_trade_row",
    "cost_profile",
    "symbol",
    "split_name",
    "signal_time",
    "entry_time",
    "exit_time",
    "signal_atr",
    "signal_close",
    "frictionless_gross_result_r",
    "normalized_net_result_r",
    "profile_total_cost_r",
    "risk_pct_of_raw_entry",
    "cost_application_count",
    "normalized_cost_decision_allowed",
    "candidate_reclassification_allowed",
    "execution_allowed",
}

SOURCE_INVARIANT_COLUMNS = (
    "symbol",
    "split_name",
    "signal_time",
    "entry_time",
    "exit_time",
    "signal_atr",
    "signal_close",
    "frictionless_gross_result_r",
    "risk_pct_of_raw_entry",
)

CONTEXT_COLUMNS = (
    "regime_1h",
    "regime_4h",
)


def validate_normalized_source_grid(
    normalized: pd.DataFrame,
    expected_source_rows: int,
    expected_profiles: list[str],
) -> tuple[bool, str]:
    if normalized is None or normalized.empty:
        return False, "normalized table is empty"
    missing = sorted(REQUIRED_NORMALIZED_COLUMNS - set(normalized.columns))
    if missing:
        return False, "missing columns=" + ",".join(missing)

    source_rows = pd.to_numeric(
        normalized["source_trade_row"], errors="coerce"
    )
    if source_rows.isna().any():
        return False, "source_trade_row contains non-numeric values"

    actual_pairs = list(
        zip(source_rows.astype(int), normalized["cost_profile"].astype(str))
    )
    expected_pairs = {
        (source_row, profile)
        for source_row in range(expected_source_rows)
        for profile in expected_profiles
    }
    grid_valid = bool(
        len(actual_pairs) == len(expected_pairs)
        and len(actual_pairs) == len(set(actual_pairs))
        and set(actual_pairs) == expected_pairs
        and pd.to_numeric(
            normalized["cost_application_count"], errors="coerce"
        ).eq(1).all()
    )

    invariance = normalized.groupby("source_trade_row")[
        list(SOURCE_INVARIANT_COLUMNS)
    ].nunique(dropna=False)
    invariant_valid = bool(not (invariance > 1).any(axis=None))
    financial = normalized[
        [
            "frictionless_gross_result_r",
            "normalized_net_result_r",
            "profile_total_cost_r",
            "risk_pct_of_raw_entry",
        ]
    ].apply(pd.to_numeric, errors="coerce")
    financial_valid = bool(
        financial.notna().all(axis=None)
        and np.isfinite(financial.to_numpy()).all()
        and financial["profile_total_cost_r"].ge(0).all()
        and financial["risk_pct_of_raw_entry"].gt(0).all()
    )
    details = (
        f"rows={len(normalized)}, expected_pairs={len(expected_pairs)}, "
        f"grid_valid={grid_valid}, invariant_valid={invariant_valid}, "
        f"financial_valid={financial_valid}"
    )
    return grid_valid and invariant_valid and financial_valid, details


def build_source_trade_features(
    normalized: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    missing = sorted(REQUIRED_NORMALIZED_COLUMNS - set(normalized.columns))
    if missing:
        raise ValueError("Missing normalized diagnostic columns: " + ", ".join(missing))

    source = (
        normalized.sort_values(["source_trade_row", "cost_profile"])
        .drop_duplicates("source_trade_row", keep="first")
        .loc[:, ["source_trade_row", *SOURCE_INVARIANT_COLUMNS]]
        .copy()
    )
    source["source_trade_row"] = pd.to_numeric(
        source["source_trade_row"], errors="raise"
    ).astype(int)
    source["signal_time_utc"] = pd.to_datetime(
        source["signal_time"], errors="coerce", utc=True
    )
    if source["signal_time_utc"].isna().any():
        raise ValueError("Signal timestamps must be complete and parseable.")
    source["calendar_year"] = source["signal_time_utc"].dt.year.astype(int)
    if set(source["calendar_year"].unique()) != {2023, 2024, 2025}:
        raise ValueError("Source signals must cover exactly calendar years 2023-2025.")

    atr = pd.to_numeric(source["signal_atr"], errors="coerce")
    close = pd.to_numeric(source["signal_close"], errors="coerce")
    source["volatility_proxy"] = atr / close
    if (
        atr.isna().any()
        or close.isna().any()
        or atr.le(0).any()
        or close.le(0).any()
        or not np.isfinite(source["volatility_proxy"]).all()
    ):
        raise ValueError("Volatility inputs must be finite and positive.")

    lower = float(
        source["volatility_proxy"].quantile(1.0 / 3.0, interpolation="linear")
    )
    upper = float(
        source["volatility_proxy"].quantile(2.0 / 3.0, interpolation="linear")
    )
    if not np.isfinite(lower) or not np.isfinite(upper) or lower >= upper:
        raise ValueError("Volatility tercile thresholds are not separable.")
    source["volatility_tercile"] = np.select(
        [
            source["volatility_proxy"].le(lower),
            source["volatility_proxy"].le(upper),
        ],
        ["LOW", "MID"],
        default="HIGH",
    )
    if set(source["volatility_tercile"].astype(str)) != set(VOLATILITY_TERCILES):
        raise ValueError("All three volatility terciles must be represented.")

    thresholds = pd.DataFrame(
        [
            {
                "method": VOLATILITY_METHOD,
                "population": "ALL_KNOWN_SOURCE_TRADES_2022_2025",
                "source_trade_rows": len(source),
                "lower_quantile": 1.0 / 3.0,
                "lower_threshold": lower,
                "upper_quantile": 2.0 / 3.0,
                "upper_threshold": upper,
                "outcome_columns_used": False,
                "selection_allowed": False,
            }
        ]
    )
    return source, thresholds


def attach_closed_candle_context(
    source: pd.DataFrame,
    context: pd.DataFrame,
) -> pd.DataFrame:
    required_context = {"symbol", "timestamp", *CONTEXT_COLUMNS}
    missing = sorted(required_context - set(context.columns))
    if missing:
        raise ValueError("Missing closed-candle context columns: " + ", ".join(missing))

    right = context.loc[:, list(required_context)].copy()
    right["symbol"] = right["symbol"].astype(str)
    right["signal_time_utc"] = pd.to_datetime(
        right["timestamp"], errors="coerce", utc=True
    )
    if right["signal_time_utc"].isna().any():
        raise ValueError("Context timestamps must be complete and parseable.")
    if right.duplicated(["symbol", "signal_time_utc"]).any():
        raise ValueError("Closed-candle context contains duplicate symbol/timestamps.")

    enriched = source.merge(
        right.drop(columns=["timestamp"]),
        on=["symbol", "signal_time_utc"],
        how="left",
        validate="many_to_one",
        indicator=True,
    )
    if not enriched["_merge"].eq("both").all():
        missing_rows = int(enriched["_merge"].ne("both").sum())
        raise ValueError(f"Closed-candle context missing for {missing_rows} source trades.")
    enriched = enriched.drop(columns=["_merge"])

    for column in CONTEXT_COLUMNS:
        enriched[column] = enriched[column].fillna("UNKNOWN").astype(str).str.strip()
    invalid_context = enriched[["regime_1h", "regime_4h"]].apply(
        lambda column: column.str.upper().isin({"", "UNKNOWN", "NAN", "NONE"})
    )
    if invalid_context.any(axis=None):
        raise ValueError("Trend regime cannot be blank or UNKNOWN at a source signal.")

    enriched["trend_regime"] = (
        "REGIME_1H="
        + enriched["regime_1h"]
        + "|REGIME_4H="
        + enriched["regime_4h"]
    )
    enriched["trend_regime_method"] = TREND_REGIME_METHOD
    enriched["signal_family"] = DIAGNOSTIC_SIGNAL_FAMILY
    enriched["diagnostic_status"] = DIAGNOSTIC_STATUS
    enriched["selection_allowed"] = False
    enriched["candidate_reclassification_allowed"] = False
    enriched["execution_allowed"] = False
    return enriched.sort_values("source_trade_row").reset_index(drop=True)


def attach_features_to_normalized(
    normalized: pd.DataFrame,
    features: pd.DataFrame,
) -> pd.DataFrame:
    feature_columns = [
        "source_trade_row",
        "calendar_year",
        "volatility_proxy",
        "volatility_tercile",
        *CONTEXT_COLUMNS,
        "trend_regime",
        "trend_regime_method",
        "signal_family",
    ]
    if features["source_trade_row"].duplicated().any():
        raise ValueError("Diagnostic feature table must be unique by source row.")
    enriched = normalized.merge(
        features[feature_columns],
        on="source_trade_row",
        how="left",
        validate="many_to_one",
        indicator=True,
    )
    if len(enriched) != len(normalized) or not enriched["_merge"].eq("both").all():
        raise ValueError("Diagnostic features do not cover every normalized row.")
    return enriched.drop(columns=["_merge"])


def _profit_factor(values: pd.Series) -> float:
    numeric = pd.to_numeric(values, errors="coerce")
    if numeric.isna().any():
        raise ValueError("Metric input contains non-numeric results.")
    gross_profit = float(numeric[numeric > 0].sum())
    gross_loss = abs(float(numeric[numeric <= 0].sum()))
    if gross_loss == 0:
        return 999.0 if gross_profit > 0 else 0.0
    return gross_profit / gross_loss


def _window_metrics(
    group: pd.DataFrame,
    window_index: pd.MultiIndex,
) -> dict[str, int | float | str]:
    observed = group.groupby(
        ["symbol", "split_name"], sort=True, observed=True
    )["normalized_net_result_r"].agg(["sum", "size"])
    unexpected = observed.index.difference(window_index)
    if len(unexpected):
        raise ValueError(f"Slice contains unexpected window units: {list(unexpected)}")
    windows = observed.reindex(window_index, fill_value=0)
    positive = (windows["size"] > 0) & (windows["sum"] > 0)
    return {
        "window_unit_contract": WINDOW_UNIT_CONTRACT,
        "configured_window_rows": int(len(windows)),
        "observed_window_rows": int((windows["size"] > 0).sum()),
        "zero_trade_window_rows": int((windows["size"] == 0).sum()),
        "positive_window_rows": int(positive.sum()),
        "positive_window_rate": float(positive.mean()),
        "minimum_window_trade_count": int(windows["size"].min()),
        "maximum_window_trade_count": int(windows["size"].max()),
    }


def _configured_window_index(
    dimension: str,
    value: str,
    symbols: list[str],
    split_names: list[str],
    split_years: dict[str, int],
) -> pd.MultiIndex:
    selected_symbols = symbols
    selected_splits = split_names
    if dimension == "symbol":
        selected_symbols = [value]
    elif dimension == "calendar_year":
        selected_splits = [
            split_name
            for split_name in split_names
            if split_years[split_name] == int(value)
        ]
    return pd.MultiIndex.from_product(
        [selected_symbols, selected_splits],
        names=["symbol", "split_name"],
    )


def build_slice_catalog(
    features: pd.DataFrame,
    symbols: list[str],
) -> pd.DataFrame:
    values: dict[str, list[str]] = {
        "symbol": list(symbols),
        "calendar_year": ["2023", "2024", "2025"],
        "volatility_tercile": list(VOLATILITY_TERCILES),
        "trend_regime": sorted(features["trend_regime"].astype(str).unique()),
        "signal_family": [DIAGNOSTIC_SIGNAL_FAMILY],
    }
    rows: list[dict[str, Any]] = []
    for dimension_order, dimension in enumerate(SLICE_DIMENSIONS, start=1):
        for value_order, value in enumerate(values[dimension], start=1):
            rows.append(
                {
                    "dimension_order": dimension_order,
                    "slice_dimension": dimension,
                    "value_order": value_order,
                    "slice_value": value,
                    "diagnostic_status": DIAGNOSTIC_STATUS,
                    "ranking_allowed": False,
                    "selection_allowed": False,
                    "candidate_reclassification_allowed": False,
                }
            )
    return pd.DataFrame(rows)


def build_slice_metrics(
    enriched: pd.DataFrame,
    catalog: pd.DataFrame,
    symbols: list[str],
    split_names: list[str],
    split_years: dict[str, int],
    expected_profiles: list[str],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for catalog_row in catalog.itertuples(index=False):
        dimension = str(catalog_row.slice_dimension)
        value = str(catalog_row.slice_value)
        if dimension == "calendar_year":
            mask = enriched[dimension].astype(int).eq(int(value))
        else:
            mask = enriched[dimension].astype(str).eq(value)
        sliced = enriched.loc[mask].copy()
        if sliced.empty:
            raise ValueError(f"Preregistered slice has no trades: {dimension}={value}")

        window_index = _configured_window_index(
            dimension,
            value,
            symbols,
            split_names,
            split_years,
        )
        for profile_order, profile in enumerate(expected_profiles, start=1):
            group = sliced[sliced["cost_profile"].astype(str).eq(profile)].copy()
            if group.empty:
                raise ValueError(f"Missing profile {profile} for {dimension}={value}")
            ordered = order_trades_for_realized_drawdown(group)
            net = pd.to_numeric(ordered["normalized_net_result_r"], errors="raise")
            gross = pd.to_numeric(
                ordered["frictionless_gross_result_r"], errors="raise"
            )
            costs = pd.to_numeric(group["profile_total_cost_r"], errors="raise")
            risk_pct = pd.to_numeric(group["risk_pct_of_raw_entry"], errors="raise")
            cost_total = float(costs.sum())
            inverse_risk_total = float((1.0 / risk_pct).sum())
            rows.append(
                {
                    "dimension_order": int(catalog_row.dimension_order),
                    "slice_dimension": dimension,
                    "value_order": int(catalog_row.value_order),
                    "slice_value": value,
                    "profile_order": profile_order,
                    "cost_profile": profile,
                    "trade_rows": len(group),
                    "source_trade_rows": int(group["source_trade_row"].nunique()),
                    "normalized_total_result_r": float(net.sum()),
                    "normalized_average_result_r": float(net.mean()),
                    "normalized_profit_factor": _profit_factor(net),
                    "normalized_max_drawdown_r": calculate_max_drawdown_r(
                        net.tolist()
                    ),
                    "drawdown_order_contract": DRAWDOWN_ORDER_CONTRACT,
                    **_window_metrics(group, window_index),
                    "frictionless_total_result_r": float(gross.sum()),
                    "frictionless_average_result_r": float(gross.mean()),
                    "frictionless_profit_factor": _profit_factor(gross),
                    "frictionless_max_drawdown_r": calculate_max_drawdown_r(
                        gross.tolist()
                    ),
                    "profile_total_cost_r": cost_total,
                    "average_profile_cost_r": float(costs.mean()),
                    "gross_edge_to_profile_cost_ratio": (
                        float(gross.sum()) / cost_total if cost_total > 0 else 0.0
                    ),
                    "break_even_total_round_trip_cost_pct": (
                        float(gross.sum()) / inverse_risk_total
                        if inverse_risk_total > 0
                        else 0.0
                    ),
                    "diagnostic_status": DIAGNOSTIC_STATUS,
                    "ranking_allowed": False,
                    "selection_allowed": False,
                    "candidate_reclassification_allowed": False,
                    "execution_allowed": False,
                }
            )
    return pd.DataFrame(rows).sort_values(
        ["dimension_order", "value_order", "profile_order"],
        kind="stable",
    ).reset_index(drop=True)


def build_slice_coverage(
    features: pd.DataFrame,
    catalog: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    expected_source_rows = int(features["source_trade_row"].nunique())
    for dimension in SLICE_DIMENSIONS:
        values = catalog.loc[
            catalog["slice_dimension"].eq(dimension), "slice_value"
        ].astype(str)
        observed = features[dimension].astype(str)
        counts = observed.value_counts()
        missing = sorted(set(values) - set(observed))
        unexpected = sorted(set(observed) - set(values))
        rows.append(
            {
                "slice_dimension": dimension,
                "catalog_value_count": int(len(values)),
                "observed_value_count": int(observed.nunique()),
                "source_trade_rows": int(counts.sum()),
                "expected_source_trade_rows": expected_source_rows,
                "minimum_value_trade_rows": int(counts.min()),
                "maximum_value_trade_rows": int(counts.max()),
                "missing_values": "|".join(missing),
                "unexpected_values": "|".join(unexpected),
                "coverage_complete": bool(
                    not missing
                    and not unexpected
                    and int(counts.sum()) == expected_source_rows
                ),
            }
        )
    return pd.DataFrame(rows)
