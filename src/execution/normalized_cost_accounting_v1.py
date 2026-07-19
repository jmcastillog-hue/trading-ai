from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.execution.cost_aware_filter_v1 import CostProfile


ACCOUNTING_CONTRACT = "FRICTIONLESS_GROSS_R_TO_SINGLE_PROFILE_NET_R_V1"
SOURCE_BASIS = "NEXT_OPEN_SHORT_RAW_ENTRY_AND_EXIT_REFERENCES"
DECISION_STATUS = "DIAGNOSTIC_ONLY_NOT_DECISION_ELIGIBLE"
DRAWDOWN_ORDER_CONTRACT = (
    "EXIT_TIME_UTC_THEN_ENTRY_TIME_UTC_THEN_SYMBOL_SOURCE_ROW_V1"
)
WINDOW_UNIT_CONTRACT = "SYMBOL_X_SPLIT_NAME_CONFIGURED_COHORT_V1"

REQUIRED_SHORT_COLUMNS = {
    "direction",
    "raw_entry_reference",
    "raw_exit_reference",
    "position_units",
    "risk_amount",
    "gross_pnl",
    "fees",
    "result_r",
}


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def validate_short_trade_schema(trades: pd.DataFrame) -> list[str]:
    return sorted(REQUIRED_SHORT_COLUMNS - set(trades.columns))


def reconstruct_short_frictionless_trade(row: pd.Series) -> dict[str, float | str]:
    direction = str(row.get("direction", "")).upper()
    if direction != "SHORT":
        raise ValueError(f"Unsupported direction for SHORT normalizer: {direction}")

    raw_entry = safe_float(row.get("raw_entry_reference"))
    raw_exit = safe_float(row.get("raw_exit_reference"))
    units = safe_float(row.get("position_units"))
    risk_amount = safe_float(row.get("risk_amount"))
    engine_gross_pnl = safe_float(row.get("gross_pnl"))
    internal_fees = safe_float(row.get("fees"))
    internal_net_result_r = safe_float(row.get("result_r"))

    if raw_entry <= 0 or raw_exit <= 0 or units <= 0 or risk_amount <= 0:
        raise ValueError("Trade has non-positive raw price, units or risk amount.")

    frictionless_gross_pnl = (raw_entry - raw_exit) * units
    frictionless_gross_result_r = frictionless_gross_pnl / risk_amount
    engine_gross_result_r = engine_gross_pnl / risk_amount
    internal_fee_result_r = internal_fees / risk_amount
    embedded_spread_result_r = (
        frictionless_gross_result_r - engine_gross_result_r
    )
    reconstructed_internal_net_result_r = (
        frictionless_gross_result_r
        - embedded_spread_result_r
        - internal_fee_result_r
    )
    reconciliation_delta_r = (
        reconstructed_internal_net_result_r - internal_net_result_r
    )
    risk_pct_of_raw_entry = risk_amount / (units * raw_entry)
    if risk_pct_of_raw_entry <= 0:
        raise ValueError("Trade has non-positive risk percentage.")

    return {
        "accounting_contract": ACCOUNTING_CONTRACT,
        "source_basis": SOURCE_BASIS,
        "frictionless_gross_pnl": frictionless_gross_pnl,
        "frictionless_gross_result_r": frictionless_gross_result_r,
        "engine_gross_result_r_after_embedded_spread": engine_gross_result_r,
        "embedded_spread_result_r": embedded_spread_result_r,
        "internal_fee_result_r": internal_fee_result_r,
        "reconstructed_internal_net_result_r": reconstructed_internal_net_result_r,
        "internal_net_result_r": internal_net_result_r,
        "internal_reconciliation_delta_r": reconciliation_delta_r,
        "risk_pct_of_raw_entry": risk_pct_of_raw_entry,
    }


def apply_single_cost_profile(
    row: pd.Series,
    profile: CostProfile,
) -> dict[str, float | str | bool]:
    reconstructed = reconstruct_short_frictionless_trade(row)
    risk_pct = safe_float(reconstructed["risk_pct_of_raw_entry"])
    if risk_pct <= 0:
        raise ValueError("Cannot apply cost profile with non-positive risk percentage.")

    fee_cost_r = profile.fee_pct_round_trip / risk_pct
    spread_cost_r = profile.spread_pct_round_trip / risk_pct
    slippage_cost_r = profile.slippage_pct_round_trip / risk_pct
    funding_or_time_cost_r = profile.funding_or_time_cost_pct / risk_pct
    safety_buffer_cost_r = profile.safety_buffer_pct / risk_pct
    profile_total_cost_r = (
        fee_cost_r
        + spread_cost_r
        + slippage_cost_r
        + funding_or_time_cost_r
        + safety_buffer_cost_r
    )
    frictionless_gross_r = safe_float(
        reconstructed["frictionless_gross_result_r"]
    )
    internal_net_r = safe_float(reconstructed["internal_net_result_r"])
    normalized_net_r = frictionless_gross_r - profile_total_cost_r
    legacy_double_counted_r = internal_net_r - profile_total_cost_r
    embedded_internal_cost_r = (
        safe_float(reconstructed["embedded_spread_result_r"])
        + safe_float(reconstructed["internal_fee_result_r"])
    )

    return {
        **reconstructed,
        "cost_profile": profile.name,
        "platform": profile.platform,
        "execution_mode": profile.mode,
        "profile_fee_pct_round_trip": profile.fee_pct_round_trip,
        "profile_spread_pct_round_trip": profile.spread_pct_round_trip,
        "profile_slippage_pct_round_trip": profile.slippage_pct_round_trip,
        "profile_funding_or_time_cost_pct": profile.funding_or_time_cost_pct,
        "profile_safety_buffer_pct": profile.safety_buffer_pct,
        "profile_total_cost_pct": profile.total_cost_pct,
        "fee_cost_r": fee_cost_r,
        "spread_cost_r": spread_cost_r,
        "slippage_cost_r": slippage_cost_r,
        "funding_or_time_cost_r": funding_or_time_cost_r,
        "safety_buffer_cost_r": safety_buffer_cost_r,
        "profile_total_cost_r": profile_total_cost_r,
        "normalized_net_result_r": normalized_net_r,
        "normalized_return_at_profile_risk": (
            normalized_net_r * profile.risk_per_trade_pct
        ),
        "legacy_double_counted_result_r": legacy_double_counted_r,
        "embedded_internal_cost_r": embedded_internal_cost_r,
        "normalization_delta_vs_legacy_r": (
            normalized_net_r - legacy_double_counted_r
        ),
        "cost_application_count": 1,
        "cost_decision_status": DECISION_STATUS,
        "normalized_cost_decision_allowed": False,
        "candidate_reclassification_allowed": False,
        "execution_allowed": False,
    }


def normalize_short_trades(
    trades: pd.DataFrame,
    profiles: list[CostProfile],
) -> pd.DataFrame:
    if trades is None or trades.empty:
        return pd.DataFrame()
    missing_columns = validate_short_trade_schema(trades)
    if missing_columns:
        raise ValueError(
            "Missing required SHORT accounting columns: "
            + ", ".join(missing_columns)
        )
    if not profiles:
        raise ValueError("At least one cost profile is required.")

    rows: list[dict[str, Any]] = []
    for source_index, trade in trades.reset_index(drop=True).iterrows():
        base = trade.to_dict()
        for profile in profiles:
            rows.append(
                {
                    **base,
                    "source_trade_row": int(source_index),
                    **apply_single_cost_profile(trade, profile),
                }
            )
    return pd.DataFrame(rows)


def calculate_max_drawdown_r(values: list[float]) -> float:
    equity = 0.0
    peak = 0.0
    max_drawdown = 0.0
    for value in values:
        equity += value
        peak = max(peak, equity)
        max_drawdown = min(max_drawdown, equity - peak)
    return max_drawdown


def order_trades_for_realized_drawdown(group: pd.DataFrame) -> pd.DataFrame:
    """Order realized outcomes without depending on source concatenation order."""
    required = {"exit_time", "entry_time", "source_trade_row"}
    missing = sorted(required - set(group.columns))
    if missing:
        raise ValueError(
            "Missing chronological drawdown columns: " + ", ".join(missing)
        )

    ordered = group.copy()
    ordered["_drawdown_exit_time"] = pd.to_datetime(
        ordered["exit_time"], errors="coerce", utc=True
    )
    ordered["_drawdown_entry_time"] = pd.to_datetime(
        ordered["entry_time"], errors="coerce", utc=True
    )
    if (
        ordered["_drawdown_exit_time"].isna().any()
        or ordered["_drawdown_entry_time"].isna().any()
    ):
        raise ValueError("Drawdown timestamps must be complete and parseable.")

    if "symbol" not in ordered.columns:
        ordered["symbol"] = ""
    ordered["_drawdown_source_row"] = pd.to_numeric(
        ordered["source_trade_row"], errors="coerce"
    )
    if ordered["_drawdown_source_row"].isna().any():
        raise ValueError("source_trade_row must be numeric for drawdown ordering.")

    return ordered.sort_values(
        [
            "_drawdown_exit_time",
            "_drawdown_entry_time",
            "symbol",
            "_drawdown_source_row",
        ],
        kind="stable",
    )


def calculate_window_stability(
    group: pd.DataFrame,
    symbols: list[str],
    split_names: list[str],
) -> dict[str, int | float | str]:
    """Count every configured symbol/window unit, including zero-trade units."""
    required = {"symbol", "split_name", "normalized_net_result_r"}
    missing = sorted(required - set(group.columns))
    if missing:
        raise ValueError(
            "Missing positive-window columns: " + ", ".join(missing)
        )
    if not symbols or not split_names:
        raise ValueError("Window stability requires symbols and split names.")

    window_index = pd.MultiIndex.from_product(
        [symbols, split_names], names=["symbol", "split_name"]
    )
    observed = group.groupby(
        ["symbol", "split_name"], sort=True, observed=True
    )["normalized_net_result_r"].agg(["sum", "size"])
    windows = observed.reindex(window_index, fill_value=0)
    configured_count = int(len(windows))
    observed_count = int((windows["size"] > 0).sum())
    positive_count = int(
        ((windows["size"] > 0) & (windows["sum"] > 0)).sum()
    )
    return {
        "window_unit_contract": WINDOW_UNIT_CONTRACT,
        "configured_window_rows": configured_count,
        "observed_window_rows": observed_count,
        "zero_trade_window_rows": configured_count - observed_count,
        "positive_window_rows": positive_count,
        "positive_window_rate": positive_count / configured_count,
        "minimum_window_trade_count": int(windows["size"].min()),
        "maximum_window_trade_count": int(windows["size"].max()),
    }


def summarize_normalized_trades(
    normalized: pd.DataFrame,
    configured_symbols: list[str] | None = None,
    configured_split_names: list[str] | None = None,
) -> pd.DataFrame:
    if normalized is None or normalized.empty:
        return pd.DataFrame()
    required_window_columns = {"symbol", "split_name"}
    missing_window_columns = sorted(
        required_window_columns - set(normalized.columns)
    )
    if missing_window_columns:
        raise ValueError(
            "Missing normalized summary window columns: "
            + ", ".join(missing_window_columns)
        )
    symbol_universe = list(configured_symbols or []) or sorted(
        normalized["symbol"].astype(str).unique()
    )
    split_universe = list(configured_split_names or []) or sorted(
        normalized["split_name"].astype(str).unique()
    )
    rows: list[dict[str, Any]] = []
    scopes = [("ALL_SYMBOLS", normalized)]
    if "symbol" in normalized.columns:
        scopes.extend(
            (str(symbol), group.copy())
            for symbol, group in normalized.groupby("symbol", sort=True)
        )
    for scope, scoped in scopes:
        for profile_name, group in scoped.groupby("cost_profile", sort=True):
            ordered_group = order_trades_for_realized_drawdown(group)
            results = pd.to_numeric(
                ordered_group["normalized_net_result_r"], errors="coerce"
            ).dropna()
            legacy = pd.to_numeric(
                group["legacy_double_counted_result_r"], errors="coerce"
            ).dropna()
            costs = pd.to_numeric(
                group["profile_total_cost_r"], errors="coerce"
            ).dropna()
            wins = results[results > 0]
            losses = results[results <= 0]
            gross_profit = float(wins.sum())
            gross_loss = abs(float(losses.sum()))
            profit_factor = (
                gross_profit / gross_loss
                if gross_loss > 0
                else (999.0 if gross_profit > 0 else 0.0)
            )
            scope_symbols = (
                symbol_universe if scope == "ALL_SYMBOLS" else [scope]
            )
            window_metrics = calculate_window_stability(
                group,
                symbols=scope_symbols,
                split_names=split_universe,
            )
            rows.append(
                {
                    "scope": scope,
                    "cost_profile": profile_name,
                    "trade_rows": len(results),
                    "normalized_total_result_r": float(results.sum()),
                    "normalized_average_result_r": float(results.mean()),
                    "normalized_profit_factor": profit_factor,
                    "normalized_max_drawdown_r": calculate_max_drawdown_r(
                        results.tolist()
                    ),
                    "drawdown_order_contract": DRAWDOWN_ORDER_CONTRACT,
                    **window_metrics,
                    "legacy_double_counted_total_result_r": float(legacy.sum()),
                    "normalization_delta_total_r": float(
                        results.sum() - legacy.sum()
                    ),
                    "average_profile_cost_r": float(costs.mean()),
                    "internal_reconciliation_max_abs_delta_r": float(
                        pd.to_numeric(
                            group["internal_reconciliation_delta_r"],
                            errors="coerce",
                        ).abs().max()
                    ),
                    "cost_application_count_min": int(
                        pd.to_numeric(
                            group["cost_application_count"], errors="coerce"
                        ).min()
                    ),
                    "cost_application_count_max": int(
                        pd.to_numeric(
                            group["cost_application_count"], errors="coerce"
                        ).max()
                    ),
                    "cost_decision_status": DECISION_STATUS,
                    "normalized_cost_decision_allowed": False,
                    "candidate_reclassification_allowed": False,
                    "execution_allowed": False,
                }
            )
    return pd.DataFrame(rows)


def accounting_identity_holds(
    normalized: pd.DataFrame,
    tolerance: float = 1e-10,
) -> bool:
    if normalized is None or normalized.empty:
        return False
    reconciliation = pd.to_numeric(
        normalized["internal_reconciliation_delta_r"], errors="coerce"
    )
    single_application = pd.to_numeric(
        normalized["cost_application_count"], errors="coerce"
    ).eq(1)
    component_sum = (
        pd.to_numeric(normalized["fee_cost_r"], errors="coerce")
        + pd.to_numeric(normalized["spread_cost_r"], errors="coerce")
        + pd.to_numeric(normalized["slippage_cost_r"], errors="coerce")
        + pd.to_numeric(normalized["funding_or_time_cost_r"], errors="coerce")
        + pd.to_numeric(normalized["safety_buffer_cost_r"], errors="coerce")
    )
    total = pd.to_numeric(normalized["profile_total_cost_r"], errors="coerce")
    normalized_identity = (
        pd.to_numeric(
            normalized["frictionless_gross_result_r"], errors="coerce"
        )
        - total
    )
    normalized_net = pd.to_numeric(
        normalized["normalized_net_result_r"], errors="coerce"
    )
    return bool(
        reconciliation.notna().all()
        and np.isclose(reconciliation, 0.0, atol=tolerance, rtol=1e-10).all()
        and single_application.all()
        and np.isclose(component_sum, total, atol=tolerance, rtol=1e-10).all()
        and np.isclose(
            normalized_identity,
            normalized_net,
            atol=tolerance,
            rtol=1e-10,
        ).all()
    )
