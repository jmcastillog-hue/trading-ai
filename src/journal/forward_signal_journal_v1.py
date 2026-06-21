from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class ForwardSignalJournalConfig:
    min_forward_signals: int = 100
    preferred_forward_signals: int = 300
    max_candidate_theoretical_risk_pct: float = 0.0050
    max_watchlist_theoretical_risk_pct: float = 0.0025


FORWARD_SIGNAL_JOURNAL_COLUMNS = [
    "signal_id",
    "created_at",
    "observed_at",
    "symbol",
    "timeframe",
    "strategy_candidate",
    "cost_profile",
    "readiness_decision",
    "context_name",
    "route_decision",
    "observation_permission",
    "forward_observation_allowed",
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "direction",
    "signal_state",
    "entry_theoretical",
    "stop_theoretical",
    "target_theoretical",
    "risk_reward_theoretical",
    "theoretical_risk_pct",
    "position_mode",
    "invalidation_level",
    "invalidation_reason",
    "mtf_state",
    "elliott_state",
    "liquidity_state",
    "volatility_state",
    "manual_review_required",
    "manual_review_status",
    "manual_reviewer",
    "manual_notes",
    "entry_triggered",
    "exit_observed",
    "exit_reason",
    "result_r",
    "result_pct",
    "max_favorable_excursion_r",
    "max_adverse_excursion_r",
    "bars_to_resolution",
    "observation_status",
    "data_source",
    "screenshot_path",
    "notes",
]


def safe_float(value, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def safe_bool(value, default: bool = False) -> bool:
    if value is None or pd.isna(value):
        return default

    if isinstance(value, bool):
        return value

    value_text = str(value).strip().lower()

    if value_text in ["true", "1", "yes", "y", "si", "sí"]:
        return True

    if value_text in ["false", "0", "no", "n"]:
        return False

    return default


def normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()


def build_empty_forward_signal_journal() -> pd.DataFrame:
    return pd.DataFrame(columns=FORWARD_SIGNAL_JOURNAL_COLUMNS)


def build_signal_id(
    symbol: str,
    timeframe: str,
    cost_profile: str,
    context_name: str,
    row_number: int,
) -> str:
    symbol = normalize_text(symbol) or "UNKNOWN"
    timeframe = normalize_text(timeframe) or "TF"
    cost_profile = normalize_text(cost_profile) or "PROFILE"
    context_name = normalize_text(context_name) or "CONTEXT"

    return f"FSJ-{symbol}-{timeframe}-{cost_profile}-{context_name}-{row_number:04d}"


def map_position_mode(theoretical_risk_pct: float) -> str:
    risk = safe_float(theoretical_risk_pct, 0.0)

    if risk <= 0:
        return "BLOCKED"

    if risk <= 0.0025:
        return "DEFENSIVE"

    if risk <= 0.0050:
        return "VALIDATION"

    if risk <= 0.0100:
        return "BASE"

    if risk <= 0.0150:
        return "AGGRESSIVE_CONTEXT_ONLY"

    return "REJECTED"


def build_forward_signal_template_from_plan(
    plan_df: pd.DataFrame,
    symbol: str = "BTCUSDT",
    timeframe: str = "15m",
) -> pd.DataFrame:
    if plan_df.empty:
        return build_empty_forward_signal_journal()

    rows = []

    observable = plan_df[
        plan_df["forward_observation_allowed"].apply(lambda value: safe_bool(value))
    ].copy()

    observable = observable.reset_index(drop=True)

    for index, row in observable.iterrows():
        theoretical_risk = safe_float(row.get("theoretical_risk_pct"), 0.0)

        signal_row = {
            "signal_id": build_signal_id(
                symbol=symbol,
                timeframe=timeframe,
                cost_profile=str(row.get("cost_profile", "UNKNOWN")),
                context_name=str(row.get("context_name", "UNKNOWN")),
                row_number=index + 1,
            ),
            "created_at": "",
            "observed_at": "",
            "symbol": symbol,
            "timeframe": timeframe,
            "strategy_candidate": "TARGET_SHORT_FIB_V5_MTF_V3_1 + FIXED_RR_2_5",
            "cost_profile": str(row.get("cost_profile", "UNKNOWN")),
            "readiness_decision": str(row.get("readiness_decision", "UNKNOWN")),
            "context_name": str(row.get("context_name", "UNKNOWN")),
            "route_decision": str(row.get("route_decision", "UNKNOWN")),
            "observation_permission": str(row.get("observation_permission", "UNKNOWN")),
            "forward_observation_allowed": safe_bool(
                row.get("forward_observation_allowed"),
                False,
            ),
            "paper_trade_execution_allowed": False,
            "real_capital_allowed": False,
            "direction": "SHORT",
            "signal_state": "OBSERVATION_TEMPLATE",
            "entry_theoretical": "",
            "stop_theoretical": "",
            "target_theoretical": "",
            "risk_reward_theoretical": 2.5,
            "theoretical_risk_pct": theoretical_risk,
            "position_mode": map_position_mode(theoretical_risk),
            "invalidation_level": "",
            "invalidation_reason": "",
            "mtf_state": str(row.get("mtf_state", "UNKNOWN")),
            "elliott_state": str(row.get("elliott_state", "UNKNOWN")),
            "liquidity_state": str(row.get("liquidity_state", "UNKNOWN")),
            "volatility_state": str(row.get("volatility_state", "UNKNOWN")),
            "manual_review_required": True,
            "manual_review_status": "PENDING",
            "manual_reviewer": "",
            "manual_notes": "",
            "entry_triggered": False,
            "exit_observed": False,
            "exit_reason": "",
            "result_r": "",
            "result_pct": "",
            "max_favorable_excursion_r": "",
            "max_adverse_excursion_r": "",
            "bars_to_resolution": "",
            "observation_status": "TEMPLATE_ONLY_NOT_A_TRADE",
            "data_source": "forward_observation_engine_v1",
            "screenshot_path": "",
            "notes": "Template row only. No execution allowed.",
        }

        rows.append(signal_row)

    if not rows:
        return build_empty_forward_signal_journal()

    return pd.DataFrame(rows, columns=FORWARD_SIGNAL_JOURNAL_COLUMNS)


def validate_forward_signal_journal(
    journal_df: pd.DataFrame,
    config: ForwardSignalJournalConfig | None = None,
) -> tuple[pd.DataFrame, dict]:
    if config is None:
        config = ForwardSignalJournalConfig()

    validation_rows = []

    missing_columns = [
        column for column in FORWARD_SIGNAL_JOURNAL_COLUMNS
        if column not in journal_df.columns
    ]

    for column in missing_columns:
        validation_rows.append(
            {
                "severity": "ERROR",
                "check_name": "missing_column",
                "details": column,
            }
        )

    if missing_columns:
        return pd.DataFrame(validation_rows), {
            "total_rows": int(len(journal_df)),
            "valid_rows": 0,
            "error_count": int(len(validation_rows)),
            "warning_count": 0,
            "journal_decision": "JOURNAL_INVALID",
        }

    df = journal_df.copy()

    total_rows = int(len(df))
    valid_rows = 0

    for index, row in df.iterrows():
        row_number = index + 1

        paper_allowed = safe_bool(row.get("paper_trade_execution_allowed"), False)
        capital_allowed = safe_bool(row.get("real_capital_allowed"), False)
        forward_allowed = safe_bool(row.get("forward_observation_allowed"), False)
        manual_required = safe_bool(row.get("manual_review_required"), True)

        theoretical_risk = safe_float(row.get("theoretical_risk_pct"), 0.0)
        readiness = normalize_text(row.get("readiness_decision"))
        signal_state = normalize_text(row.get("signal_state"))

        if paper_allowed:
            validation_rows.append(
                {
                    "severity": "ERROR",
                    "check_name": "paper_execution_must_be_false",
                    "details": f"row={row_number}",
                }
            )

        if capital_allowed:
            validation_rows.append(
                {
                    "severity": "ERROR",
                    "check_name": "real_capital_must_be_false",
                    "details": f"row={row_number}",
                }
            )

        if not manual_required:
            validation_rows.append(
                {
                    "severity": "WARNING",
                    "check_name": "manual_review_should_be_required",
                    "details": f"row={row_number}",
                }
            )

        if forward_allowed and theoretical_risk <= 0:
            validation_rows.append(
                {
                    "severity": "WARNING",
                    "check_name": "observable_signal_without_theoretical_risk",
                    "details": f"row={row_number}",
                }
            )

        if readiness == "PAPER_TRADING_CANDIDATE":
            if theoretical_risk > config.max_candidate_theoretical_risk_pct:
                validation_rows.append(
                    {
                        "severity": "ERROR",
                        "check_name": "candidate_risk_above_cap",
                        "details": (
                            f"row={row_number}; "
                            f"risk={theoretical_risk:.4f}; "
                            f"cap={config.max_candidate_theoretical_risk_pct:.4f}"
                        ),
                    }
                )

        if readiness == "WATCHLIST_READY":
            if theoretical_risk > config.max_watchlist_theoretical_risk_pct:
                validation_rows.append(
                    {
                        "severity": "ERROR",
                        "check_name": "watchlist_risk_above_cap",
                        "details": (
                            f"row={row_number}; "
                            f"risk={theoretical_risk:.4f}; "
                            f"cap={config.max_watchlist_theoretical_risk_pct:.4f}"
                        ),
                    }
                )

        if signal_state not in [
            "OBSERVATION_TEMPLATE",
            "FORWARD_OBSERVED",
            "RESOLVED",
            "INVALIDATED",
            "SKIPPED",
            "WATCHLIST_ONLY",
        ]:
            validation_rows.append(
                {
                    "severity": "WARNING",
                    "check_name": "unknown_signal_state",
                    "details": f"row={row_number}; state={signal_state}",
                }
            )

        valid_rows += 1

    validation_df = pd.DataFrame(validation_rows)

    if validation_df.empty:
        error_count = 0
        warning_count = 0
    else:
        error_count = int((validation_df["severity"] == "ERROR").sum())
        warning_count = int((validation_df["severity"] == "WARNING").sum())

    if error_count > 0:
        decision = "JOURNAL_INVALID"
    elif total_rows < config.min_forward_signals:
        decision = "JOURNAL_STRUCTURE_VALID_NEEDS_FORWARD_DATA"
    elif total_rows < config.preferred_forward_signals:
        decision = "JOURNAL_MINIMUM_SAMPLE_READY"
    else:
        decision = "JOURNAL_PREFERRED_SAMPLE_READY"

    summary = {
        "total_rows": total_rows,
        "valid_rows": valid_rows,
        "error_count": error_count,
        "warning_count": warning_count,
        "min_forward_signals": config.min_forward_signals,
        "preferred_forward_signals": config.preferred_forward_signals,
        "journal_decision": decision,
    }

    return validation_df, summary


def summarize_forward_signal_journal(journal_df: pd.DataFrame) -> pd.DataFrame:
    if journal_df.empty:
        return pd.DataFrame(
            [
                {
                    "total_signals": 0,
                    "observable_signals": 0,
                    "resolved_signals": 0,
                    "avg_result_r": 0.0,
                    "win_rate": 0.0,
                    "paper_trade_execution_allowed": False,
                    "real_capital_allowed": False,
                }
            ]
        )

    df = journal_df.copy()

    if "forward_observation_allowed" in df.columns:
        observable_signals = int(
            df["forward_observation_allowed"].apply(lambda value: safe_bool(value)).sum()
        )
    else:
        observable_signals = 0

    if "observation_status" in df.columns:
        resolved_signals = int(
            df["observation_status"]
            .astype(str)
            .str.upper()
            .isin(["RESOLVED", "INVALIDATED"])
            .sum()
        )
    else:
        resolved_signals = 0

    if "result_r" in df.columns:
        result_r = pd.to_numeric(df["result_r"], errors="coerce")
        avg_result_r = (
            float(result_r.dropna().mean())
            if len(result_r.dropna()) > 0
            else 0.0
        )
        win_rate = (
            float((result_r.dropna() > 0).mean())
            if len(result_r.dropna()) > 0
            else 0.0
        )
    else:
        avg_result_r = 0.0
        win_rate = 0.0

    paper_allowed = (
        bool(df["paper_trade_execution_allowed"].apply(lambda value: safe_bool(value)).any())
        if "paper_trade_execution_allowed" in df.columns
        else False
    )

    capital_allowed = (
        bool(df["real_capital_allowed"].apply(lambda value: safe_bool(value)).any())
        if "real_capital_allowed" in df.columns
        else False
    )

    return pd.DataFrame(
        [
            {
                "total_signals": int(len(df)),
                "observable_signals": observable_signals,
                "resolved_signals": resolved_signals,
                "avg_result_r": avg_result_r,
                "win_rate": win_rate,
                "paper_trade_execution_allowed": paper_allowed,
                "real_capital_allowed": capital_allowed,
            }
        ]
    )


def build_forward_signal_journal_specification(
    output_dir: Path,
) -> list[str]:
    lines = []

    lines.append("# Forward Signal Journal V1")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This journal records forward-observed theoretical signals. "
        "It does not authorize paper trading execution or real capital."
    )
    lines.append("")
    lines.append("## Hard restrictions")
    lines.append("")
    lines.append("- Paper trade execution: NOT ALLOWED")
    lines.append("- Real capital: NOT ALLOWED")
    lines.append("- Exchange execution: NOT ALLOWED")
    lines.append("- Live alerts as trade signals: NOT ALLOWED")
    lines.append("")
    lines.append("## Minimum evidence")
    lines.append("")
    lines.append("- Minimum forward-observed signals: 100")
    lines.append("- Preferred forward-observed signals: 300")
    lines.append("- Each observation must include theoretical entry, stop, target and result in R.")
    lines.append("- Each observation must include manual review notes.")
    lines.append("")
    lines.append("## Journal columns")
    lines.append("")

    for column in FORWARD_SIGNAL_JOURNAL_COLUMNS:
        lines.append(f"- {column}")

    lines.append("")
    lines.append("## Generated files")
    lines.append("")
    lines.append(f"- {output_dir / 'forward_signal_journal_v1_empty.csv'}")
    lines.append(f"- {output_dir / 'forward_signal_journal_v1_template.csv'}")
    lines.append(f"- {output_dir / 'forward_signal_journal_v1_validation.csv'}")
    lines.append(f"- {output_dir / 'forward_signal_journal_v1_summary.csv'}")

    return lines