from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ContextScenario:
    context_name: str
    mtf_state: str
    elliott_state: str
    liquidity_state: str
    volatility_state: str
    manual_conviction: str
    max_risk_ceiling_pct: float
    description: str


def safe_float(value, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def build_context_scenarios() -> list[ContextScenario]:
    return [
        ContextScenario(
            context_name="MIXED_OR_UNCLEAR_CONTEXT",
            mtf_state="MIXED",
            elliott_state="UNCLEAR",
            liquidity_state="UNCLEAR",
            volatility_state="NORMAL",
            manual_conviction="LOW",
            max_risk_ceiling_pct=0.0025,
            description="Contexto mixto o poco claro. Solo permite modo defensivo.",
        ),
        ContextScenario(
            context_name="NORMAL_VALIDATION_CONTEXT",
            mtf_state="PARTIAL_ALIGNMENT",
            elliott_state="NEUTRAL",
            liquidity_state="ACCEPTABLE",
            volatility_state="NORMAL",
            manual_conviction="MEDIUM",
            max_risk_ceiling_pct=0.0050,
            description="Contexto normal de validacion. Riesgo recomendado cercano a 0.50%.",
        ),
        ContextScenario(
            context_name="STRONG_MTF_CONTEXT",
            mtf_state="ALIGNED",
            elliott_state="IMPULSE_OR_CONTINUATION",
            liquidity_state="CLEAR",
            volatility_state="NORMAL",
            manual_conviction="HIGH",
            max_risk_ceiling_pct=0.0100,
            description="MTF alineado y liquidez clara. Puede permitir riesgo base.",
        ),
        ContextScenario(
            context_name="WAVE_3_OPPORTUNITY_CONTEXT",
            mtf_state="ALIGNED",
            elliott_state="PROBABLE_WAVE_3",
            liquidity_state="CLEAR",
            volatility_state="EXPANSION",
            manual_conviction="HIGH",
            max_risk_ceiling_pct=0.0150,
            description="Contexto excepcional tipo onda 3 probable. Puede permitir modo agresivo.",
        ),
        ContextScenario(
            context_name="WAVE_5_CAUTION_CONTEXT",
            mtf_state="ALIGNED",
            elliott_state="PROBABLE_WAVE_5",
            liquidity_state="CLEAR",
            volatility_state="LATE_TREND",
            manual_conviction="HIGH",
            max_risk_ceiling_pct=0.0100,
            description="Onda 5 probable. Permite oportunidad con penalizacion por agotamiento.",
        ),
        ContextScenario(
            context_name="STRESS_OR_DEGRADED_CONTEXT",
            mtf_state="CONFLICT",
            elliott_state="UNCLEAR",
            liquidity_state="WEAK",
            volatility_state="STRESS",
            manual_conviction="LOW",
            max_risk_ceiling_pct=0.0,
            description="Contexto degradado. Debe bloquear o exigir solo observacion.",
        ),
    ]


def normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()


def cost_decision_score(cost_decision: str) -> int:
    decision = normalize_text(cost_decision)

    if decision == "COST_AWARE_PASS":
        return 3

    if decision == "COST_AWARE_WEAK_PASS":
        return 2

    if decision == "COST_AWARE_NEAR_BREAKEVEN":
        return 1

    return 0


def monte_carlo_decision_score(decision: str) -> int:
    decision = normalize_text(decision)

    if decision == "MONTE_CARLO_PASS":
        return 4

    if decision == "MONTE_CARLO_EDGE_WITH_SEQUENCE_RISK":
        return 3

    if decision == "MONTE_CARLO_WEAK_PASS_WITH_SEQUENCE_RISK":
        return 2

    if decision == "MONTE_CARLO_HIGH_SEQUENCE_RISK":
        return 1

    return 0


def position_size_decision_score(decision: str) -> int:
    decision = normalize_text(decision)

    if decision == "POSITION_SIZE_ROBUST":
        return 4

    if decision == "POSITION_SIZE_BASE_ACCEPTABLE":
        return 3

    if decision == "POSITION_SIZE_AGGRESSIVE_ONLY_WITH_CONTEXT":
        return 2

    if decision == "POSITION_SIZE_EXTREME_DIAGNOSTIC_ONLY":
        return 1

    return 0


def context_score(context: ContextScenario) -> int:
    score = 0

    if context.mtf_state == "ALIGNED":
        score += 3
    elif context.mtf_state == "PARTIAL_ALIGNMENT":
        score += 2
    elif context.mtf_state == "MIXED":
        score += 1

    if context.elliott_state == "PROBABLE_WAVE_3":
        score += 3
    elif context.elliott_state == "PROBABLE_WAVE_5":
        score += 1
    elif context.elliott_state == "IMPULSE_OR_CONTINUATION":
        score += 2

    if context.liquidity_state == "CLEAR":
        score += 2
    elif context.liquidity_state == "ACCEPTABLE":
        score += 1

    if context.volatility_state == "EXPANSION":
        score += 1
    elif context.volatility_state == "STRESS":
        score -= 3
    elif context.volatility_state == "LATE_TREND":
        score -= 1

    if context.manual_conviction == "HIGH":
        score += 1
    elif context.manual_conviction == "LOW":
        score -= 1

    return score


def route_label_for_risk(risk_per_trade_pct: float) -> str:
    if risk_per_trade_pct <= 0:
        return "RISK_BLOCKED"

    if risk_per_trade_pct <= 0.0025:
        return "RISK_DEFENSIVE"

    if risk_per_trade_pct <= 0.0050:
        return "RISK_VALIDATION"

    if risk_per_trade_pct <= 0.0100:
        return "RISK_BASE"

    if risk_per_trade_pct <= 0.0150:
        return "RISK_AGGRESSIVE_CONTEXT_ONLY"

    return "RISK_REJECTED"


def build_reason(
    context: ContextScenario,
    cost_decision: str,
    monte_carlo_decision: str,
    position_decision: str,
    selected_risk: float,
) -> str:
    return (
        f"context={context.context_name}; "
        f"cost={cost_decision}; "
        f"monte_carlo={monte_carlo_decision}; "
        f"position_size={position_decision}; "
        f"selected_risk={selected_risk:.2%}; "
        f"ceiling={context.max_risk_ceiling_pct:.2%}"
    )


def select_position_size_for_context(
    position_rows: pd.DataFrame,
    context: ContextScenario,
    cost_decision: str,
    monte_carlo_decision: str,
) -> dict:
    if position_rows.empty:
        return {
            "recommended_risk_per_trade_pct": 0.0,
            "route_decision": "RISK_BLOCKED",
            "reason": "No position sizing rows available.",
        }

    cost_score = cost_decision_score(cost_decision)
    mc_score = monte_carlo_decision_score(monte_carlo_decision)
    ctx_score = context_score(context)

    if context.max_risk_ceiling_pct <= 0:
        return {
            "recommended_risk_per_trade_pct": 0.0,
            "route_decision": "RISK_BLOCKED",
            "reason": "Context ceiling is zero.",
        }

    if cost_score == 0:
        return {
            "recommended_risk_per_trade_pct": 0.0,
            "route_decision": "RISK_BLOCKED",
            "reason": "Cost-aware decision failed.",
        }

    if mc_score == 0:
        return {
            "recommended_risk_per_trade_pct": 0.0,
            "route_decision": "RISK_BLOCKED",
            "reason": "Monte Carlo decision failed.",
        }

    allowed = position_rows.copy()
    allowed["risk_per_trade_pct"] = pd.to_numeric(
        allowed["risk_per_trade_pct"],
        errors="coerce",
    )

    allowed = allowed.dropna(subset=["risk_per_trade_pct"])
    allowed = allowed[allowed["risk_per_trade_pct"] <= context.max_risk_ceiling_pct]

    if allowed.empty:
        return {
            "recommended_risk_per_trade_pct": 0.0,
            "route_decision": "RISK_BLOCKED",
            "reason": "No position size under context ceiling.",
        }

    allowed["position_score"] = allowed["decision"].apply(position_size_decision_score)

    if ctx_score < 3:
        allowed = allowed[allowed["risk_per_trade_pct"] <= 0.0025]
    elif ctx_score < 6:
        allowed = allowed[allowed["risk_per_trade_pct"] <= 0.0050]
    elif ctx_score < 9:
        allowed = allowed[allowed["risk_per_trade_pct"] <= 0.0100]
    else:
        allowed = allowed[allowed["risk_per_trade_pct"] <= 0.0150]

    if mc_score <= 1:
        allowed = allowed[allowed["risk_per_trade_pct"] <= 0.0050]

    if cost_score <= 2:
        allowed = allowed[allowed["risk_per_trade_pct"] <= 0.0050]

    allowed = allowed[allowed["position_score"] >= 2]

    if allowed.empty:
        return {
            "recommended_risk_per_trade_pct": 0.0,
            "route_decision": "RISK_BLOCKED",
            "reason": "No acceptable position size after risk filters.",
        }

    selected = allowed.sort_values(
        by=[
            "risk_per_trade_pct",
            "position_score",
        ],
        ascending=[
            False,
            False,
        ],
    ).iloc[0]

    selected_risk = safe_float(selected["risk_per_trade_pct"], 0.0)
    route_decision = route_label_for_risk(selected_risk)

    reason = build_reason(
        context=context,
        cost_decision=cost_decision,
        monte_carlo_decision=monte_carlo_decision,
        position_decision=str(selected["decision"]),
        selected_risk=selected_risk,
    )

    return {
        "recommended_risk_per_trade_pct": selected_risk,
        "route_decision": route_decision,
        "reason": reason,
        "selected_position_decision": selected["decision"],
        "context_score": ctx_score,
        "cost_score": cost_score,
        "monte_carlo_score": mc_score,
    }


def build_context_risk_routes(
    cost_df: pd.DataFrame,
    monte_carlo_df: pd.DataFrame,
    position_df: pd.DataFrame,
    contexts: list[ContextScenario] | None = None,
) -> pd.DataFrame:
    if contexts is None:
        contexts = build_context_scenarios()

    if cost_df.empty:
        raise ValueError("cost_df is empty")

    if monte_carlo_df.empty:
        raise ValueError("monte_carlo_df is empty")

    if position_df.empty:
        raise ValueError("position_df is empty")

    rows = []

    profiles = sorted(position_df["cost_profile"].dropna().unique().tolist())

    for cost_profile in profiles:
        cost_rows = cost_df[cost_df["cost_profile"] == cost_profile]
        mc_rows = monte_carlo_df[monte_carlo_df["cost_profile"] == cost_profile]
        pos_rows = position_df[position_df["cost_profile"] == cost_profile]

        cost_decision = (
            str(cost_rows["cost_decision"].iloc[0])
            if not cost_rows.empty and "cost_decision" in cost_rows.columns
            else "UNKNOWN"
        )

        monte_carlo_decision = (
            str(mc_rows["decision"].iloc[0])
            if not mc_rows.empty and "decision" in mc_rows.columns
            else "UNKNOWN"
        )

        for context in contexts:
            route = select_position_size_for_context(
                position_rows=pos_rows,
                context=context,
                cost_decision=cost_decision,
                monte_carlo_decision=monte_carlo_decision,
            )

            rows.append(
                {
                    "cost_profile": cost_profile,
                    "context_name": context.context_name,
                    "mtf_state": context.mtf_state,
                    "elliott_state": context.elliott_state,
                    "liquidity_state": context.liquidity_state,
                    "volatility_state": context.volatility_state,
                    "manual_conviction": context.manual_conviction,
                    "context_ceiling_pct": context.max_risk_ceiling_pct,
                    "cost_decision": cost_decision,
                    "monte_carlo_decision": monte_carlo_decision,
                    "recommended_risk_per_trade_pct": route.get(
                        "recommended_risk_per_trade_pct",
                        0.0,
                    ),
                    "route_decision": route.get("route_decision", "RISK_BLOCKED"),
                    "selected_position_decision": route.get(
                        "selected_position_decision",
                        "NONE",
                    ),
                    "context_score": route.get("context_score", context_score(context)),
                    "cost_score": route.get("cost_score", cost_decision_score(cost_decision)),
                    "monte_carlo_score": route.get(
                        "monte_carlo_score",
                        monte_carlo_decision_score(monte_carlo_decision),
                    ),
                    "reason": route.get("reason", ""),
                    "description": context.description,
                }
            )

    return pd.DataFrame(rows)


def summarize_router_routes(routes_df: pd.DataFrame) -> pd.DataFrame:
    if routes_df.empty:
        return pd.DataFrame()

    return routes_df.sort_values(
        by=[
            "cost_profile",
            "recommended_risk_per_trade_pct",
            "context_score",
        ],
        ascending=[
            True,
            False,
            False,
        ],
    ).reset_index(drop=True)


def summarize_router_by_profile(routes_df: pd.DataFrame) -> pd.DataFrame:
    if routes_df.empty:
        return pd.DataFrame()

    grouped = (
        routes_df.groupby("cost_profile")
        .agg(
            contexts=("context_name", "count"),
            blocked_contexts=("route_decision", lambda x: int((x == "RISK_BLOCKED").sum())),
            max_recommended_risk=("recommended_risk_per_trade_pct", "max"),
            avg_recommended_risk=("recommended_risk_per_trade_pct", "mean"),
            aggressive_contexts=(
                "route_decision",
                lambda x: int((x == "RISK_AGGRESSIVE_CONTEXT_ONLY").sum()),
            ),
            base_contexts=(
                "route_decision",
                lambda x: int((x == "RISK_BASE").sum()),
            ),
            validation_contexts=(
                "route_decision",
                lambda x: int((x == "RISK_VALIDATION").sum()),
            ),
            defensive_contexts=(
                "route_decision",
                lambda x: int((x == "RISK_DEFENSIVE").sum()),
            ),
        )
        .reset_index()
    )

    return grouped.sort_values(
        by=[
            "max_recommended_risk",
            "avg_recommended_risk",
        ],
        ascending=[
            False,
            False,
        ],
    )