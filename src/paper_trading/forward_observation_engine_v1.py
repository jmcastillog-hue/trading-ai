from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ForwardObservationConfig:
    min_forward_signals: int = 100
    preferred_forward_signals: int = 300
    max_theoretical_risk_pct: float = 0.0050
    allow_aggressive_observation: bool = True
    require_manual_review: bool = True


def safe_float(value, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def safe_int(value, default: int = 0) -> int:
    try:
        if value is None or pd.isna(value):
            return default
        return int(value)
    except Exception:
        return default


def normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()


def build_observation_status(readiness_decision: str) -> str:
    decision = normalize_text(readiness_decision)

    if decision == "PAPER_TRADING_READY":
        return "READY_FOR_CONTROLLED_PAPER_TRADING_PLAN"

    if decision == "PAPER_TRADING_CANDIDATE":
        return "FORWARD_OBSERVATION_READY"

    if decision == "WATCHLIST_READY":
        return "WATCHLIST_OBSERVATION_ONLY"

    return "NOT_ELIGIBLE_FOR_OBSERVATION"


def route_observation_permission(route_decision: str) -> str:
    route = normalize_text(route_decision)

    if route == "RISK_BLOCKED":
        return "BLOCKED"

    if route == "RISK_DEFENSIVE":
        return "OBSERVE_DEFENSIVE_ONLY"

    if route == "RISK_VALIDATION":
        return "OBSERVE_VALIDATION"

    if route == "RISK_BASE":
        return "OBSERVE_BASE"

    if route == "RISK_AGGRESSIVE_CONTEXT_ONLY":
        return "OBSERVE_AGGRESSIVE_CONTEXT_ONLY"

    return "BLOCKED"


def cap_theoretical_risk(
    route_risk_pct: float,
    readiness_decision: str,
    config: ForwardObservationConfig,
) -> float:
    decision = normalize_text(readiness_decision)

    route_risk_pct = safe_float(route_risk_pct, 0.0)

    if route_risk_pct <= 0:
        return 0.0

    if decision == "PAPER_TRADING_CANDIDATE":
        return min(route_risk_pct, config.max_theoretical_risk_pct)

    if decision == "PAPER_TRADING_READY":
        return min(route_risk_pct, 0.0100)

    if decision == "WATCHLIST_READY":
        return min(route_risk_pct, 0.0025)

    return 0.0


def build_required_evidence(
    readiness_decision: str,
    config: ForwardObservationConfig,
) -> str:
    decision = normalize_text(readiness_decision)

    if decision == "PAPER_TRADING_READY":
        return (
            f"Minimum {config.min_forward_signals} controlled paper trades; "
            "risk capped; manual review required; no real capital."
        )

    if decision == "PAPER_TRADING_CANDIDATE":
        return (
            f"Minimum {config.min_forward_signals} forward-observed signals before paper trading; "
            f"preferred {config.preferred_forward_signals}; "
            "record context, route, theoretical entry, invalidation, target, result in R."
        )

    if decision == "WATCHLIST_READY":
        return (
            "Observation only; must improve sequence risk or stress behavior before candidate status."
        )

    return "No observation plan; failed validation gate."


def build_forward_observation_plan(
    readiness_profile_df: pd.DataFrame,
    readiness_global_df: pd.DataFrame,
    router_routes_df: pd.DataFrame,
    config: ForwardObservationConfig | None = None,
) -> pd.DataFrame:
    if config is None:
        config = ForwardObservationConfig()

    if readiness_profile_df.empty:
        raise ValueError("readiness_profile_df is empty")

    if router_routes_df.empty:
        raise ValueError("router_routes_df is empty")

    rows = []

    global_decision = (
        str(readiness_global_df["global_readiness_decision"].iloc[0])
        if not readiness_global_df.empty and "global_readiness_decision" in readiness_global_df.columns
        else "UNKNOWN"
    )

    for _, profile_row in readiness_profile_df.iterrows():
        cost_profile = str(profile_row.get("cost_profile", "UNKNOWN"))
        readiness_decision = str(profile_row.get("readiness_decision", "UNKNOWN"))

        observation_status = build_observation_status(readiness_decision)
        required_evidence = build_required_evidence(
            readiness_decision=readiness_decision,
            config=config,
        )

        profile_routes = router_routes_df[
            router_routes_df["cost_profile"] == cost_profile
        ].copy()

        if profile_routes.empty:
            rows.append(
                {
                    "cost_profile": cost_profile,
                    "global_readiness_decision": global_decision,
                    "readiness_decision": readiness_decision,
                    "context_name": "NO_ROUTE_AVAILABLE",
                    "route_decision": "RISK_BLOCKED",
                    "observation_permission": "BLOCKED",
                    "observation_status": observation_status,
                    "theoretical_risk_pct": 0.0,
                    "real_capital_allowed": False,
                    "paper_trade_execution_allowed": False,
                    "forward_observation_allowed": False,
                    "manual_review_required": config.require_manual_review,
                    "required_evidence": required_evidence,
                    "notes": "No router route available for profile.",
                }
            )
            continue

        for _, route_row in profile_routes.iterrows():
            route_decision = str(route_row.get("route_decision", "RISK_BLOCKED"))
            route_risk = safe_float(
                route_row.get("recommended_risk_per_trade_pct"),
                0.0,
            )

            permission = route_observation_permission(route_decision)
            theoretical_risk = cap_theoretical_risk(
                route_risk_pct=route_risk,
                readiness_decision=readiness_decision,
                config=config,
            )

            forward_allowed = (
                observation_status in [
                    "FORWARD_OBSERVATION_READY",
                    "READY_FOR_CONTROLLED_PAPER_TRADING_PLAN",
                    "WATCHLIST_OBSERVATION_ONLY",
                ]
                and permission != "BLOCKED"
                and theoretical_risk > 0
            )

            paper_execution_allowed = False
            real_capital_allowed = False

            notes = (
                "Forward observation only. "
                "No paper execution, no real capital, no live alerts."
            )

            if permission == "OBSERVE_AGGRESSIVE_CONTEXT_ONLY":
                notes = (
                    "Aggressive context may be observed, but theoretical risk is capped. "
                    "No execution allowed in V1."
                )

            if readiness_decision == "WATCHLIST_READY":
                notes = (
                    "Watchlist only due to blockers. Observation is diagnostic, not candidate validation."
                )

            if readiness_decision == "NOT_READY":
                notes = "Profile failed readiness gate."

            rows.append(
                {
                    "cost_profile": cost_profile,
                    "global_readiness_decision": global_decision,
                    "readiness_decision": readiness_decision,
                    "context_name": str(route_row.get("context_name", "UNKNOWN")),
                    "mtf_state": str(route_row.get("mtf_state", "UNKNOWN")),
                    "elliott_state": str(route_row.get("elliott_state", "UNKNOWN")),
                    "liquidity_state": str(route_row.get("liquidity_state", "UNKNOWN")),
                    "volatility_state": str(route_row.get("volatility_state", "UNKNOWN")),
                    "route_decision": route_decision,
                    "observation_permission": permission,
                    "observation_status": observation_status,
                    "router_recommended_risk_pct": route_risk,
                    "theoretical_risk_pct": theoretical_risk,
                    "real_capital_allowed": real_capital_allowed,
                    "paper_trade_execution_allowed": paper_execution_allowed,
                    "forward_observation_allowed": forward_allowed,
                    "manual_review_required": config.require_manual_review,
                    "required_evidence": required_evidence,
                    "notes": notes,
                }
            )

    return pd.DataFrame(rows)


def summarize_forward_observation_plan(plan_df: pd.DataFrame) -> pd.DataFrame:
    if plan_df.empty:
        return pd.DataFrame()

    grouped = (
        plan_df.groupby("cost_profile")
        .agg(
            contexts=("context_name", "count"),
            observable_contexts=(
                "forward_observation_allowed",
                lambda x: int(pd.Series(x).astype(bool).sum()),
            ),
            blocked_contexts=(
                "observation_permission",
                lambda x: int((pd.Series(x) == "BLOCKED").sum()),
            ),
            max_theoretical_risk_pct=("theoretical_risk_pct", "max"),
            avg_theoretical_risk_pct=("theoretical_risk_pct", "mean"),
            paper_execution_allowed=(
                "paper_trade_execution_allowed",
                lambda x: bool(pd.Series(x).astype(bool).any()),
            ),
            real_capital_allowed=(
                "real_capital_allowed",
                lambda x: bool(pd.Series(x).astype(bool).any()),
            ),
        )
        .reset_index()
    )

    return grouped.sort_values(
        by=[
            "max_theoretical_risk_pct",
            "observable_contexts",
        ],
        ascending=[
            False,
            False,
        ],
    )


def build_forward_observation_specification(
    plan_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    config: ForwardObservationConfig | None = None,
) -> list[str]:
    if config is None:
        config = ForwardObservationConfig()

    lines = []

    lines.append("# Paper Trading Specification / Forward Observation V1")
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append("This phase does not authorize paper trading execution.")
    lines.append("It authorizes forward observation only.")
    lines.append("")
    lines.append("## Hard restrictions")
    lines.append("")
    lines.append("- Real capital: NOT ALLOWED")
    lines.append("- Live exchange execution: NOT ALLOWED")
    lines.append("- Binance execution: NOT ALLOWED")
    lines.append("- Quantfury execution: NOT ALLOWED")
    lines.append("- Live alerts as trading signals: NOT ALLOWED")
    lines.append("- Paper trade execution: NOT ALLOWED in this V1")
    lines.append("")
    lines.append("## Observation requirements")
    lines.append("")
    lines.append(f"- Minimum forward-observed signals: {config.min_forward_signals}")
    lines.append(f"- Preferred forward-observed signals: {config.preferred_forward_signals}")
    lines.append("- Every signal must be recorded with context, route decision and theoretical risk.")
    lines.append("- Every signal must include theoretical entry, stop, target, result in R and reason for invalidation.")
    lines.append("- Manual review is mandatory before any future paper trading module.")
    lines.append("")
    lines.append("## Profile summary")
    lines.append("")

    if summary_df.empty:
        lines.append("No profile summary available.")
    else:
        for _, row in summary_df.iterrows():
            lines.append(
                "- "
                f"{row['cost_profile']}: "
                f"observable_contexts={row['observable_contexts']}, "
                f"max_theoretical_risk={safe_float(row['max_theoretical_risk_pct']):.2%}, "
                f"paper_execution_allowed={row['paper_execution_allowed']}, "
                f"real_capital_allowed={row['real_capital_allowed']}"
            )

    lines.append("")
    lines.append("## Allowed observation logic")
    lines.append("")

    if plan_df.empty:
        lines.append("No observation plan available.")
    else:
        observable = plan_df[plan_df["forward_observation_allowed"] == True].copy()

        if observable.empty:
            lines.append("No contexts are observable.")
        else:
            for _, row in observable.iterrows():
                lines.append(
                    "- "
                    f"{row['cost_profile']} | "
                    f"{row['context_name']} | "
                    f"{row['observation_permission']} | "
                    f"theoretical_risk={safe_float(row['theoretical_risk_pct']):.2%}"
                )

    lines.append("")
    lines.append("## Advancement rule")
    lines.append("")
    lines.append(
        "The project may only move to a dedicated paper trading module after enough "
        "forward-observed signals are collected and reviewed. Passing this specification "
        "does not imply profitability and does not authorize capital deployment."
    )

    return lines