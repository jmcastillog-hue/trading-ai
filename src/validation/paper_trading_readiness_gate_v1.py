from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ReadinessDecision:
    decision: str
    rank: int
    description: str


READINESS_DECISIONS = {
    "NOT_READY": ReadinessDecision(
        decision="NOT_READY",
        rank=0,
        description="No cumple criterios minimos para pasar a paper trading.",
    ),
    "WATCHLIST_READY": ReadinessDecision(
        decision="WATCHLIST_READY",
        rank=1,
        description="Puede quedar en vigilancia, pero no como candidato directo a paper trading.",
    ),
    "PAPER_TRADING_CANDIDATE": ReadinessDecision(
        decision="PAPER_TRADING_CANDIDATE",
        rank=2,
        description="Puede considerarse candidato para una fase futura de paper trading controlado.",
    ),
    "PAPER_TRADING_READY": ReadinessDecision(
        decision="PAPER_TRADING_READY",
        rank=3,
        description="Cumple criterios para iniciar paper trading controlado.",
    ),
}


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


def get_first_value(
    df: pd.DataFrame,
    column: str,
    default=None,
):
    if df.empty or column not in df.columns:
        return default

    value = df[column].iloc[0]

    if pd.isna(value):
        return default

    return value


def decision_rank(decision: str) -> int:
    normalized = normalize_text(decision)

    if normalized in READINESS_DECISIONS:
        return READINESS_DECISIONS[normalized].rank

    return -1


def cost_decision_score(decision: str) -> int:
    decision = normalize_text(decision)

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


def position_decision_score(decision: str) -> int:
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


def walk_forward_decision_score(decision: str) -> int:
    decision = normalize_text(decision)

    if decision == "WALK_FORWARD_PASS":
        return 3

    if decision == "WALK_FORWARD_WEAK_PASS":
        return 2

    if decision == "WALK_FORWARD_NEAR_BREAKEVEN":
        return 1

    return 0


def extract_official_walk_forward_status(walk_forward_df: pd.DataFrame) -> dict:
    if walk_forward_df.empty:
        return {
            "walk_forward_mode": "UNKNOWN",
            "walk_forward_decision": "UNKNOWN",
            "walk_forward_score": 0,
            "walk_forward_total_trades": 0,
            "walk_forward_compound_return": 0.0,
            "walk_forward_worst_drawdown": 0.0,
            "walk_forward_positive_rate": 0.0,
        }

    df = walk_forward_df.copy()

    if "evaluation_mode" in df.columns:
        official = df[df["evaluation_mode"] == "OFFICIAL_FIXED"].copy()
    else:
        official = pd.DataFrame()

    if official.empty:
        official = df.head(1).copy()

    decision = str(get_first_value(official, "walk_forward_decision", "UNKNOWN"))

    return {
        "walk_forward_mode": str(get_first_value(official, "evaluation_mode", "UNKNOWN")),
        "walk_forward_decision": decision,
        "walk_forward_score": walk_forward_decision_score(decision),
        "walk_forward_total_trades": safe_int(
            get_first_value(official, "total_test_trades", 0),
            0,
        ),
        "walk_forward_compound_return": safe_float(
            get_first_value(official, "compound_test_return", 0.0),
            0.0,
        ),
        "walk_forward_worst_drawdown": safe_float(
            get_first_value(official, "worst_test_drawdown", 0.0),
            0.0,
        ),
        "walk_forward_positive_rate": safe_float(
            get_first_value(official, "positive_test_rate", 0.0),
            0.0,
        ),
    }


def classify_profile_readiness(row: dict) -> str:
    wf_score = safe_int(row.get("walk_forward_score"), 0)
    cost_score = safe_int(row.get("cost_score"), 0)
    mc_score = safe_int(row.get("monte_carlo_score"), 0)
    pos_score = safe_int(row.get("position_score"), 0)

    contexts = safe_int(row.get("router_contexts"), 0)
    blocked_contexts = safe_int(row.get("router_blocked_contexts"), contexts)

    max_router_risk = safe_float(row.get("router_max_recommended_risk"), 0.0)
    recommended_risk = safe_float(row.get("recommended_position_risk_pct"), 0.0)

    monte_carlo_decision = normalize_text(row.get("monte_carlo_decision"))
    cost_decision = normalize_text(row.get("cost_decision"))

    if wf_score == 0:
        return "NOT_READY"

    if cost_score == 0:
        return "NOT_READY"

    if mc_score == 0:
        return "NOT_READY"

    if max_router_risk <= 0:
        return "NOT_READY"

    if contexts > 0 and blocked_contexts >= contexts:
        return "NOT_READY"

    if pos_score == 0:
        return "NOT_READY"

    if monte_carlo_decision == "MONTE_CARLO_HIGH_SEQUENCE_RISK":
        return "WATCHLIST_READY"

    if cost_decision == "COST_AWARE_WEAK_PASS":
        return "WATCHLIST_READY"

    if (
        wf_score >= 3
        and cost_score >= 3
        and mc_score >= 4
        and pos_score >= 3
        and recommended_risk <= 0.0100
        and max_router_risk <= 0.0150
        and blocked_contexts <= 1
    ):
        return "PAPER_TRADING_READY"

    if (
        wf_score >= 2
        and cost_score >= 3
        and mc_score >= 3
        and pos_score >= 3
        and recommended_risk <= 0.0100
        and max_router_risk <= 0.0150
        and blocked_contexts <= 1
    ):
        return "PAPER_TRADING_CANDIDATE"

    if (
        wf_score >= 2
        and cost_score >= 2
        and mc_score >= 1
        and pos_score >= 2
    ):
        return "WATCHLIST_READY"

    return "NOT_READY"


def build_blockers(row: dict) -> str:
    blockers = []

    if safe_int(row.get("walk_forward_score"), 0) == 0:
        blockers.append("walk_forward_failed_or_missing")

    if safe_int(row.get("cost_score"), 0) == 0:
        blockers.append("cost_aware_failed_or_missing")

    if safe_int(row.get("monte_carlo_score"), 0) == 0:
        blockers.append("monte_carlo_failed_or_missing")

    if safe_int(row.get("position_score"), 0) == 0:
        blockers.append("position_sizing_failed_or_missing")

    contexts = safe_int(row.get("router_contexts"), 0)
    blocked_contexts = safe_int(row.get("router_blocked_contexts"), 0)

    if contexts > 0 and blocked_contexts >= contexts:
        blockers.append("all_contexts_blocked")

    if safe_float(row.get("router_max_recommended_risk"), 0.0) <= 0:
        blockers.append("router_max_risk_zero")

    if normalize_text(row.get("monte_carlo_decision")) == "MONTE_CARLO_HIGH_SEQUENCE_RISK":
        blockers.append("high_sequence_risk")

    if normalize_text(row.get("cost_decision")) == "COST_AWARE_WEAK_PASS":
        blockers.append("weak_cost_profile")

    if not blockers:
        return "none"

    return ";".join(blockers)


def build_next_action(decision: str) -> str:
    decision = normalize_text(decision)

    if decision == "PAPER_TRADING_READY":
        return (
            "Create controlled paper trading plan with strict limits; "
            "do not use real capital."
        )

    if decision == "PAPER_TRADING_CANDIDATE":
        return (
            "Prepare paper trading specification and forward-observation rules; "
            "do not execute paper trades yet without a dedicated paper trading module."
        )

    if decision == "WATCHLIST_READY":
        return (
            "Keep on watchlist; improve sequence risk, stress behavior or context filters."
        )

    return (
        "Do not advance; identify failed validation layer before continuing."
    )


def build_profile_readiness_decisions(
    walk_forward_df: pd.DataFrame,
    cost_df: pd.DataFrame,
    monte_carlo_df: pd.DataFrame,
    position_recommended_df: pd.DataFrame,
    router_profile_df: pd.DataFrame,
) -> pd.DataFrame:
    wf_status = extract_official_walk_forward_status(walk_forward_df)

    profiles = sorted(
        set(cost_df.get("cost_profile", pd.Series(dtype=str)).dropna().tolist())
        | set(monte_carlo_df.get("cost_profile", pd.Series(dtype=str)).dropna().tolist())
        | set(position_recommended_df.get("cost_profile", pd.Series(dtype=str)).dropna().tolist())
        | set(router_profile_df.get("cost_profile", pd.Series(dtype=str)).dropna().tolist())
    )

    rows = []

    for profile in profiles:
        cost_row = cost_df[cost_df["cost_profile"] == profile] if "cost_profile" in cost_df.columns else pd.DataFrame()
        mc_row = monte_carlo_df[monte_carlo_df["cost_profile"] == profile] if "cost_profile" in monte_carlo_df.columns else pd.DataFrame()
        pos_row = position_recommended_df[position_recommended_df["cost_profile"] == profile] if "cost_profile" in position_recommended_df.columns else pd.DataFrame()
        router_row = router_profile_df[router_profile_df["cost_profile"] == profile] if "cost_profile" in router_profile_df.columns else pd.DataFrame()

        cost_decision = str(get_first_value(cost_row, "cost_decision", "UNKNOWN"))
        monte_carlo_decision = str(get_first_value(mc_row, "decision", "UNKNOWN"))
        position_decision = str(get_first_value(pos_row, "decision", "UNKNOWN"))

        recommended_position_risk = safe_float(
            get_first_value(pos_row, "risk_per_trade_pct", 0.0),
            0.0,
        )

        row = {
            "cost_profile": profile,
            **wf_status,
            "cost_decision": cost_decision,
            "cost_score": cost_decision_score(cost_decision),
            "cost_compound_return": safe_float(
                get_first_value(cost_row, "compound_return", 0.0),
                0.0,
            ),
            "cost_avg_profit_factor": safe_float(
                get_first_value(cost_row, "avg_profit_factor", 0.0),
                0.0,
            ),
            "cost_worst_drawdown": safe_float(
                get_first_value(cost_row, "worst_drawdown", 0.0),
                0.0,
            ),
            "monte_carlo_decision": monte_carlo_decision,
            "monte_carlo_score": monte_carlo_decision_score(monte_carlo_decision),
            "monte_carlo_p05_return": safe_float(
                get_first_value(mc_row, "p05_return", 0.0),
                0.0,
            ),
            "monte_carlo_p01_return": safe_float(
                get_first_value(mc_row, "p01_return", 0.0),
                0.0,
            ),
            "monte_carlo_p01_drawdown": safe_float(
                get_first_value(mc_row, "p01_max_drawdown", 0.0),
                0.0,
            ),
            "monte_carlo_p99_losing_streak": safe_float(
                get_first_value(mc_row, "p99_losing_streak", 0.0),
                0.0,
            ),
            "monte_carlo_negative_probability": safe_float(
                get_first_value(mc_row, "probability_negative_return", 1.0),
                1.0,
            ),
            "recommended_position_scenario": str(
                get_first_value(pos_row, "scenario_name", "NONE")
            ),
            "recommended_position_risk_pct": recommended_position_risk,
            "recommended_position_decision": position_decision,
            "position_score": position_decision_score(position_decision),
            "router_contexts": safe_int(
                get_first_value(router_row, "contexts", 0),
                0,
            ),
            "router_blocked_contexts": safe_int(
                get_first_value(router_row, "blocked_contexts", 0),
                0,
            ),
            "router_max_recommended_risk": safe_float(
                get_first_value(router_row, "max_recommended_risk", 0.0),
                0.0,
            ),
            "router_avg_recommended_risk": safe_float(
                get_first_value(router_row, "avg_recommended_risk", 0.0),
                0.0,
            ),
            "router_aggressive_contexts": safe_int(
                get_first_value(router_row, "aggressive_contexts", 0),
                0,
            ),
            "router_base_contexts": safe_int(
                get_first_value(router_row, "base_contexts", 0),
                0,
            ),
            "router_validation_contexts": safe_int(
                get_first_value(router_row, "validation_contexts", 0),
                0,
            ),
            "router_defensive_contexts": safe_int(
                get_first_value(router_row, "defensive_contexts", 0),
                0,
            ),
        }

        readiness_decision = classify_profile_readiness(row)

        row["readiness_decision"] = readiness_decision
        row["readiness_rank"] = decision_rank(readiness_decision)
        row["blockers"] = build_blockers(row)
        row["next_action"] = build_next_action(readiness_decision)

        rows.append(row)

    return pd.DataFrame(rows)


def build_global_readiness_decision(profile_df: pd.DataFrame) -> pd.DataFrame:
    if profile_df.empty:
        return pd.DataFrame(
            [
                {
                    "global_readiness_decision": "NOT_READY",
                    "best_profile": "NONE",
                    "reason": "No profile readiness decisions available.",
                    "next_action": build_next_action("NOT_READY"),
                }
            ]
        )

    ordered = profile_df.sort_values(
        by=[
            "readiness_rank",
            "recommended_position_risk_pct",
            "router_max_recommended_risk",
        ],
        ascending=[
            False,
            False,
            False,
        ],
    ).reset_index(drop=True)

    best = ordered.iloc[0]

    decision = str(best["readiness_decision"])

    candidate_profiles = profile_df[
        profile_df["readiness_rank"] == safe_int(best["readiness_rank"], 0)
    ]["cost_profile"].tolist()

    reason = (
        f"Best decision={decision}; "
        f"best_profile={best['cost_profile']}; "
        f"candidate_profiles={candidate_profiles}; "
        f"blockers={best['blockers']}"
    )

    return pd.DataFrame(
        [
            {
                "global_readiness_decision": decision,
                "best_profile": best["cost_profile"],
                "candidate_profiles": ",".join(candidate_profiles),
                "best_recommended_position_risk_pct": safe_float(
                    best.get("recommended_position_risk_pct"),
                    0.0,
                ),
                "best_router_max_risk_pct": safe_float(
                    best.get("router_max_recommended_risk"),
                    0.0,
                ),
                "reason": reason,
                "next_action": build_next_action(decision),
            }
        ]
    )


def summarize_profile_readiness(profile_df: pd.DataFrame) -> pd.DataFrame:
    if profile_df.empty:
        return pd.DataFrame()

    return profile_df.sort_values(
        by=[
            "readiness_rank",
            "recommended_position_risk_pct",
            "router_max_recommended_risk",
        ],
        ascending=[
            False,
            False,
            False,
        ],
    ).reset_index(drop=True)