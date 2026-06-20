from pathlib import Path
import pandas as pd

from src.workflows.validate_directional_context_filter_v3 import validate_window


BASE_STRATEGIES = [
    "LONG_V2_BASE",
    "SHORT_FIB_V5_MTF_BASE",
    "SHORT_FIB_V5_MTF_LIQUIDITY_V2_BASE",
]


def get_period(window_name: str) -> str:
    if window_name.startswith("2024"):
        return "DISCOVERY_2024"

    if window_name.startswith("2025"):
        return "HOLDOUT_2025"

    return "OTHER"


def current_v3_allows(direction: str, directional_context: str) -> bool:
    if direction == "LONG":
        return directional_context in {
            "LONG_ONLY",
            "LONG_CAUTION",
        }

    if direction == "SHORT":
        return directional_context in {
            "SHORT_ONLY",
            "SHORT_CAUTION",
        }

    return False


def profit_factor(net_pnl: pd.Series):
    gross_profit = float(net_pnl[net_pnl > 0].sum())
    gross_loss = float(net_pnl[net_pnl < 0].sum())

    if gross_loss == 0:
        if gross_profit > 0:
            return None
        return 0.0

    return gross_profit / abs(gross_loss)


def summarize_context_pairs(trades_df: pd.DataFrame, period: str) -> pd.DataFrame:
    if trades_df.empty:
        return pd.DataFrame()

    df = trades_df.copy()

    df = df[df["strategy_name"].isin(BASE_STRATEGIES)].copy()
    df = df[df["period"] == period].copy()

    if df.empty:
        return pd.DataFrame()

    df["net_pnl"] = pd.to_numeric(df["net_pnl"], errors="coerce").fillna(0.0)

    group_cols = [
        "strategy_name",
        "direction",
        "directional_context_v3",
        "bias_1h_v3",
        "bias_4h_v3",
    ]

    rows = []

    for keys, group in df.groupby(group_cols):
        strategy_name, direction, directional_context, bias_1h, bias_4h = keys

        by_window = group.groupby("window_name")["net_pnl"].sum()

        trades = int(len(group))
        wins = int((group["net_pnl"] > 0).sum())
        losses = int((group["net_pnl"] <= 0).sum())

        total_net_pnl = float(group["net_pnl"].sum())
        avg_net_pnl = float(group["net_pnl"].mean())
        win_rate = wins / trades if trades else 0.0

        pf = profit_factor(group["net_pnl"])

        positive_windows = int((by_window > 0).sum())
        negative_windows = int((by_window <= 0).sum())

        rows.append(
            {
                "period": period,
                "strategy_name": strategy_name,
                "direction": direction,
                "directional_context_v3": directional_context,
                "bias_1h_v3": bias_1h,
                "bias_4h_v3": bias_4h,
                "current_v3_allows": current_v3_allows(direction, directional_context),
                "windows": int(group["window_name"].nunique()),
                "positive_windows": positive_windows,
                "negative_windows": negative_windows,
                "trades": trades,
                "wins": wins,
                "losses": losses,
                "win_rate": win_rate,
                "total_net_pnl": total_net_pnl,
                "avg_net_pnl": avg_net_pnl,
                "profit_factor": pf,
            }
        )

    result = pd.DataFrame(rows)
    result = result.sort_values(
        by=["strategy_name", "total_net_pnl"],
        ascending=[True, False],
    )

    return result


def compare_discovery_holdout(discovery_df: pd.DataFrame, holdout_df: pd.DataFrame) -> pd.DataFrame:
    key_cols = [
        "strategy_name",
        "direction",
        "directional_context_v3",
        "bias_1h_v3",
        "bias_4h_v3",
    ]

    if discovery_df.empty and holdout_df.empty:
        return pd.DataFrame()

    discovery = discovery_df.copy()
    holdout = holdout_df.copy()

    discovery = discovery.rename(
        columns={
            "windows": "discovery_windows",
            "positive_windows": "discovery_positive_windows",
            "negative_windows": "discovery_negative_windows",
            "trades": "discovery_trades",
            "win_rate": "discovery_win_rate",
            "total_net_pnl": "discovery_total_net_pnl",
            "avg_net_pnl": "discovery_avg_net_pnl",
            "profit_factor": "discovery_profit_factor",
        }
    )

    holdout = holdout.rename(
        columns={
            "windows": "holdout_windows",
            "positive_windows": "holdout_positive_windows",
            "negative_windows": "holdout_negative_windows",
            "trades": "holdout_trades",
            "win_rate": "holdout_win_rate",
            "total_net_pnl": "holdout_total_net_pnl",
            "avg_net_pnl": "holdout_avg_net_pnl",
            "profit_factor": "holdout_profit_factor",
        }
    )

    keep_discovery = key_cols + [
        "current_v3_allows",
        "discovery_windows",
        "discovery_positive_windows",
        "discovery_negative_windows",
        "discovery_trades",
        "discovery_win_rate",
        "discovery_total_net_pnl",
        "discovery_avg_net_pnl",
        "discovery_profit_factor",
    ]

    keep_holdout = key_cols + [
        "current_v3_allows",
        "holdout_windows",
        "holdout_positive_windows",
        "holdout_negative_windows",
        "holdout_trades",
        "holdout_win_rate",
        "holdout_total_net_pnl",
        "holdout_avg_net_pnl",
        "holdout_profit_factor",
    ]

    comparison = pd.merge(
        discovery[keep_discovery],
        holdout[keep_holdout],
        on=key_cols,
        how="outer",
        suffixes=("_discovery", "_holdout"),
    )

    if "current_v3_allows_discovery" in comparison.columns:
        comparison["current_v3_allows"] = comparison[
            "current_v3_allows_discovery"
        ].fillna(comparison["current_v3_allows_holdout"])
        comparison = comparison.drop(
            columns=[
                col
                for col in [
                    "current_v3_allows_discovery",
                    "current_v3_allows_holdout",
                ]
                if col in comparison.columns
            ]
        )

    numeric_cols = [
        "discovery_windows",
        "discovery_positive_windows",
        "discovery_negative_windows",
        "discovery_trades",
        "discovery_win_rate",
        "discovery_total_net_pnl",
        "discovery_avg_net_pnl",
        "discovery_profit_factor",
        "holdout_windows",
        "holdout_positive_windows",
        "holdout_negative_windows",
        "holdout_trades",
        "holdout_win_rate",
        "holdout_total_net_pnl",
        "holdout_avg_net_pnl",
        "holdout_profit_factor",
    ]

    for col in numeric_cols:
        if col in comparison.columns:
            comparison[col] = pd.to_numeric(comparison[col], errors="coerce").fillna(0.0)

    comparison["current_v3_allows"] = comparison["current_v3_allows"].fillna(False)

    comparison["total_trades_all"] = (
        comparison["discovery_trades"] + comparison["holdout_trades"]
    )

    comparison["total_net_pnl_all"] = (
        comparison["discovery_total_net_pnl"] + comparison["holdout_total_net_pnl"]
    )

    comparison["holdout_decay"] = (
        comparison["holdout_total_net_pnl"] - comparison["discovery_total_net_pnl"]
    )

    comparison["calibration_decision"] = comparison.apply(
        classify_context_pair,
        axis=1,
    )

    comparison["calibration_score"] = comparison.apply(
        score_context_pair,
        axis=1,
    )

    comparison = comparison.sort_values(
        by=["strategy_name", "calibration_score"],
        ascending=[True, False],
    )

    return comparison


def classify_context_pair(row: pd.Series) -> str:
    discovery_trades = int(row.get("discovery_trades", 0))
    holdout_trades = int(row.get("holdout_trades", 0))

    discovery_pnl = float(row.get("discovery_total_net_pnl", 0.0))
    holdout_pnl = float(row.get("holdout_total_net_pnl", 0.0))

    holdout_pf = row.get("holdout_profit_factor", 0.0)
    holdout_pf = 999.0 if pd.isna(holdout_pf) or holdout_pf is None else float(holdout_pf)

    holdout_positive_windows = int(row.get("holdout_positive_windows", 0))
    holdout_negative_windows = int(row.get("holdout_negative_windows", 0))

    current_allowed = bool(row.get("current_v3_allows", False))

    if holdout_trades >= 8 and holdout_pnl > 0 and holdout_pf >= 1.10:
        if discovery_trades >= 5 and discovery_pnl > 0:
            return "V3_1_ALLOW_ROBUST_PAIR"

        return "V3_1_ALLOW_HOLDOUT_POSITIVE"

    if holdout_trades >= 5 and holdout_pnl > 0 and holdout_positive_windows >= holdout_negative_windows:
        return "V3_1_ALLOW_WEAK_PAIR"

    if holdout_trades < 5 and discovery_trades >= 5 and discovery_pnl > 0:
        return "LOW_SAMPLE_MONITOR"

    if current_allowed and holdout_trades >= 5 and holdout_pnl < 0:
        return "CURRENT_V3_ALLOWED_BUT_REJECT"

    if not current_allowed and holdout_trades >= 5 and holdout_pnl > 0:
        return "CURRENT_V3_BLOCKED_BUT_PROMISING"

    if holdout_trades >= 5 and holdout_pnl < 0:
        return "REJECT_PAIR"

    return "INSUFFICIENT_OR_MIXED"


def score_context_pair(row: pd.Series) -> float:
    discovery_pnl = float(row.get("discovery_total_net_pnl", 0.0))
    holdout_pnl = float(row.get("holdout_total_net_pnl", 0.0))

    discovery_trades = float(row.get("discovery_trades", 0.0))
    holdout_trades = float(row.get("holdout_trades", 0.0))

    holdout_positive_windows = float(row.get("holdout_positive_windows", 0.0))
    holdout_negative_windows = float(row.get("holdout_negative_windows", 0.0))

    holdout_pf = row.get("holdout_profit_factor", 0.0)

    if pd.isna(holdout_pf) or holdout_pf is None:
        holdout_pf = 0.0

    holdout_pf = float(holdout_pf)

    score = (
        holdout_pnl * 1.5
        + discovery_pnl * 0.5
        + holdout_pf * 10
        + holdout_positive_windows * 8
        - holdout_negative_windows * 8
        + min(holdout_trades, 30) * 0.5
        + min(discovery_trades, 30) * 0.2
    )

    return score


def print_context_pair_reports(comparison_df: pd.DataFrame):
    print()
    print("V3.1 CONTEXT PAIR RECOMMENDATIONS")
    print("=" * 100)

    if comparison_df.empty:
        print("Sin datos.")
        return

    recommendation_cols = [
        "strategy_name",
        "direction",
        "calibration_decision",
        "current_v3_allows",
        "directional_context_v3",
        "bias_1h_v3",
        "bias_4h_v3",
        "discovery_trades",
        "discovery_total_net_pnl",
        "holdout_trades",
        "holdout_total_net_pnl",
        "holdout_profit_factor",
        "holdout_positive_windows",
        "holdout_negative_windows",
        "calibration_score",
    ]

    print(
        comparison_df[recommendation_cols]
        .sort_values(by="calibration_score", ascending=False)
        .head(40)
        .to_string(index=False)
    )

    print()
    print("CURRENT V3 ALLOWED BUT REJECTED")
    print("=" * 100)

    rejected = comparison_df[
        comparison_df["calibration_decision"] == "CURRENT_V3_ALLOWED_BUT_REJECT"
    ].copy()

    if rejected.empty:
        print("Sin pares permitidos actualmente que deban rechazarse.")
    else:
        print(
            rejected[recommendation_cols]
            .sort_values(by="holdout_total_net_pnl")
            .to_string(index=False)
        )

    print()
    print("CURRENT V3 BLOCKED BUT PROMISING")
    print("=" * 100)

    blocked_promising = comparison_df[
        comparison_df["calibration_decision"] == "CURRENT_V3_BLOCKED_BUT_PROMISING"
    ].copy()

    if blocked_promising.empty:
        print("Sin pares bloqueados prometedores con muestra suficiente.")
    else:
        print(
            blocked_promising[recommendation_cols]
            .sort_values(by="holdout_total_net_pnl", ascending=False)
            .to_string(index=False)
        )

    print()
    print("ROBUST / WEAK ALLOW CANDIDATES")
    print("=" * 100)

    allow_candidates = comparison_df[
        comparison_df["calibration_decision"].isin(
            [
                "V3_1_ALLOW_ROBUST_PAIR",
                "V3_1_ALLOW_HOLDOUT_POSITIVE",
                "V3_1_ALLOW_WEAK_PAIR",
            ]
        )
    ].copy()

    if allow_candidates.empty:
        print("No hay pares suficientemente robustos para permitir directamente.")
    else:
        print(
            allow_candidates[recommendation_cols]
            .sort_values(by="calibration_score", ascending=False)
            .to_string(index=False)
        )


def print_final_decision(comparison_df: pd.DataFrame):
    print()
    print("FINAL V3.1 CALIBRATION DECISION")
    print("=" * 100)

    if comparison_df.empty:
        print("NO_DATA")
        return

    decision_counts = (
        comparison_df.groupby("calibration_decision")
        .agg(
            pairs=("calibration_decision", "count"),
            total_holdout_trades=("holdout_trades", "sum"),
            total_holdout_pnl=("holdout_total_net_pnl", "sum"),
        )
        .reset_index()
        .sort_values(by="total_holdout_pnl", ascending=False)
    )

    print(decision_counts.to_string(index=False))

    print()
    print("Interpretacion:")
    print("- V3 sirve como filtro de daño, pero debe calibrarse por pares.")
    print("- Los pares CURRENT_V3_ALLOWED_BUT_REJECT deben bloquearse en V3.1.")
    print("- Los pares CURRENT_V3_BLOCKED_BUT_PROMISING se revisan, pero no se aceptan sin cautela.")
    print("- No crear estrategia nueva todavía; primero crear whitelist/blacklist V3.1.")


def main():
    symbol = "BTCUSDT"

    windows = [
        ("2024_01_03", "2024-01-01", "2024-03-01"),
        ("2024_03_05", "2024-03-01", "2024-05-01"),
        ("2024_05_07", "2024-05-01", "2024-07-01"),
        ("2024_07_09", "2024-07-01", "2024-09-01"),
        ("2024_09_11", "2024-09-01", "2024-11-01"),
        ("2024_11_2025_01", "2024-11-01", "2025-01-01"),
        ("2025_01_03", "2025-01-01", "2025-03-01"),
        ("2025_03_05", "2025-03-01", "2025-05-01"),
        ("2025_05_07", "2025-05-01", "2025-07-01"),
        ("2025_07_09", "2025-07-01", "2025-09-01"),
        ("2025_09_11", "2025-09-01", "2025-11-01"),
        ("2025_11_2026_01", "2025-11-01", "2026-01-01"),
    ]

    print("DIRECTIONAL CONTEXT PAIR DIAGNOSTICS — V3.1 CALIBRATION")
    print("=" * 100)
    print("Discovery: 2024")
    print("Holdout: 2025")
    print("Using BASE strategies to evaluate all context pairs.")
    print()

    all_results = []
    all_trades = []

    for window_name, start_date, end_date in windows:
        window_results, trades_df = validate_window(
            symbol=symbol,
            window_name=window_name,
            start_date=start_date,
            end_date=end_date,
        )

        all_results.extend(window_results)

        if not trades_df.empty:
            trades_df = trades_df.copy()
            trades_df["period"] = get_period(window_name)
            all_trades.append(trades_df)

    results_df = pd.DataFrame(all_results)

    if all_trades:
        trades_all_df = pd.concat(all_trades, ignore_index=True)
    else:
        trades_all_df = pd.DataFrame()

    discovery_pairs_df = summarize_context_pairs(
        trades_df=trades_all_df,
        period="DISCOVERY_2024",
    )

    holdout_pairs_df = summarize_context_pairs(
        trades_df=trades_all_df,
        period="HOLDOUT_2025",
    )

    comparison_df = compare_discovery_holdout(
        discovery_df=discovery_pairs_df,
        holdout_df=holdout_pairs_df,
    )

    reports_dir = Path("reports") / "directional_context_pair_diagnostics"
    reports_dir.mkdir(parents=True, exist_ok=True)

    trades_output = reports_dir / "directional_context_pair_all_trades.csv"
    discovery_output = reports_dir / "directional_context_pair_discovery_2024.csv"
    holdout_output = reports_dir / "directional_context_pair_holdout_2025.csv"
    comparison_output = reports_dir / "directional_context_pair_comparison.csv"
    window_results_output = reports_dir / "directional_context_pair_window_results.csv"

    trades_all_df.to_csv(trades_output, index=False)
    discovery_pairs_df.to_csv(discovery_output, index=False)
    holdout_pairs_df.to_csv(holdout_output, index=False)
    comparison_df.to_csv(comparison_output, index=False)
    results_df.to_csv(window_results_output, index=False)

    print_context_pair_reports(comparison_df)
    print_final_decision(comparison_df)

    print()
    print("ARCHIVOS GENERADOS")
    print("=" * 100)
    print(f"- {trades_output}")
    print(f"- {discovery_output}")
    print(f"- {holdout_output}")
    print(f"- {comparison_output}")
    print(f"- {window_results_output}")


if __name__ == "__main__":
    main()