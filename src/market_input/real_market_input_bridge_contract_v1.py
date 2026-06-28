from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd


REPORTS_DIR = Path("reports/phase_7_1_real_market_input_bridge_contract_v1")


EXECUTION_FLAGS = {
    "paper_trade_execution_allowed": False,
    "real_capital_allowed": False,
    "live_alerts_allowed": False,
    "exchange_execution_allowed": False,
    "automation_allowed": False,
    "execution_allowed": False,
}


OPERATIONAL_INPUT_DIRECTORIES = {
    "signals": Path("data/forward_evidence/operational/input/signals"),
    "ohlc": Path("data/forward_evidence/operational/input/ohlc"),
    "price_levels": Path("data/forward_evidence/operational/input/price_levels"),
}


REQUIRED_OUTPUT_SCHEMAS = {
    "signals": [
        "observed_at",
        "symbol",
        "timeframe",
        "signal_type",
        "router_decision",
        "cost_profile",
        "context_name",
        "direction",
        "manual_review_required",
        "notes",
    ],
    "ohlc": [
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "symbol",
        "timeframe",
        "data_source",
    ],
    "price_levels": [
        "signal_id",
        "context_name",
        "cost_profile",
        "direction",
        "entry_price",
        "stop_price",
        "target_price",
        "price_level_source",
        "notes",
    ],
}


PHASE_6_REQUIRED_ANCHORS = [
    Path("docs/PHASE_6_OPERATIONAL_EVIDENCE_CLOSURE.md"),
    Path("src/workflows/run_profile_based_interval_forward_evidence_runner_v1.py"),
    Path("src/workflows/run_operational_input_file_validator_adapter_v1.py"),
    Path("src/workflows/run_operational_persistent_cycle_integration_v1.py"),
    Path("data/forward_evidence/operational/forward_evidence_dataset_v1.csv"),
]


@dataclass(frozen=True)
class MarketInputSourceContract:
    source_name: str
    source_class: str
    source_kind: str
    read_only: bool
    execution_capable: bool
    writes_operational_csv: bool
    requires_manual_review: bool
    allowed_output_types: tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class MarketInputBridgeContractConfig:
    reports_dir: Path = REPORTS_DIR


def build_market_input_source_contracts() -> list[MarketInputSourceContract]:
    return [
        MarketInputSourceContract(
            source_name="LOCAL_MARKET_CSV_READ_ONLY",
            source_class="LOCAL_FILE",
            source_kind="OHLC",
            read_only=True,
            execution_capable=False,
            writes_operational_csv=True,
            requires_manual_review=False,
            allowed_output_types=("ohlc",),
            notes="Reads local OHLC CSV exports and normalizes them into operational OHLC input files.",
        ),
        MarketInputSourceContract(
            source_name="BINANCE_PUBLIC_MARKET_DATA_READ_ONLY",
            source_class="PUBLIC_MARKET_DATA",
            source_kind="OHLC",
            read_only=True,
            execution_capable=False,
            writes_operational_csv=True,
            requires_manual_review=False,
            allowed_output_types=("ohlc",),
            notes="Future read-only public market data source. Must not use execution endpoints.",
        ),
        MarketInputSourceContract(
            source_name="MANUAL_REVIEWED_SIGNAL_EXPORT",
            source_class="LOCAL_FILE",
            source_kind="SIGNAL",
            read_only=True,
            execution_capable=False,
            writes_operational_csv=True,
            requires_manual_review=True,
            allowed_output_types=("signals", "price_levels"),
            notes="Reads manually reviewed watch-only signal exports and price levels.",
        ),
        MarketInputSourceContract(
            source_name="FUTURE_STRATEGY_SIGNAL_EXPORT_READ_ONLY",
            source_class="STRATEGY_EXPORT",
            source_kind="SIGNAL",
            read_only=True,
            execution_capable=False,
            writes_operational_csv=True,
            requires_manual_review=True,
            allowed_output_types=("signals", "price_levels"),
            notes="Future non-executing strategy signal export. Must remain watch-only.",
        ),
    ]


def build_check(
    check_group: str,
    check_name: str,
    passed: bool,
    severity: str,
    details: str,
) -> dict[str, Any]:
    return {
        "check_group": check_group,
        "check_name": check_name,
        "passed": passed,
        "severity": severity,
        "details": details,
        "blocker": severity == "ERROR" and not passed,
    }


def build_source_contracts_df(
    source_contracts: list[MarketInputSourceContract],
) -> pd.DataFrame:
    rows = []

    for source_contract in source_contracts:
        row = asdict(source_contract)
        row["allowed_output_types"] = ",".join(source_contract.allowed_output_types)

        for flag_name, flag_value in EXECUTION_FLAGS.items():
            row[flag_name] = flag_value

        rows.append(row)

    return pd.DataFrame(rows)


def build_output_schemas_df() -> pd.DataFrame:
    rows = []

    for output_type, columns in REQUIRED_OUTPUT_SCHEMAS.items():
        for position, column_name in enumerate(columns, start=1):
            rows.append(
                {
                    "output_type": output_type,
                    "column_position": position,
                    "column_name": column_name,
                    "required": True,
                }
            )

    return pd.DataFrame(rows)


def validate_source_contract(
    source_contract: MarketInputSourceContract,
) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    checks.append(
        build_check(
            check_group="source_contract",
            check_name=f"{source_contract.source_name}:read_only",
            passed=source_contract.read_only is True,
            severity="INFO" if source_contract.read_only is True else "ERROR",
            details=f"read_only={source_contract.read_only}",
        )
    )

    checks.append(
        build_check(
            check_group="source_contract",
            check_name=f"{source_contract.source_name}:not_execution_capable",
            passed=source_contract.execution_capable is False,
            severity="INFO" if source_contract.execution_capable is False else "ERROR",
            details=f"execution_capable={source_contract.execution_capable}",
        )
    )

    checks.append(
        build_check(
            check_group="source_contract",
            check_name=f"{source_contract.source_name}:writes_operational_csv",
            passed=source_contract.writes_operational_csv is True,
            severity="INFO" if source_contract.writes_operational_csv is True else "ERROR",
            details=f"writes_operational_csv={source_contract.writes_operational_csv}",
        )
    )

    valid_outputs = set(source_contract.allowed_output_types).issubset(
        set(REQUIRED_OUTPUT_SCHEMAS.keys())
    )

    checks.append(
        build_check(
            check_group="source_contract",
            check_name=f"{source_contract.source_name}:allowed_output_types_valid",
            passed=valid_outputs,
            severity="INFO" if valid_outputs else "ERROR",
            details=",".join(source_contract.allowed_output_types),
        )
    )

    if source_contract.source_kind == "SIGNAL":
        manual_review_required = source_contract.requires_manual_review is True
        checks.append(
            build_check(
                check_group="source_contract",
                check_name=f"{source_contract.source_name}:signal_requires_manual_review",
                passed=manual_review_required,
                severity="INFO" if manual_review_required else "ERROR",
                details=f"requires_manual_review={source_contract.requires_manual_review}",
            )
        )

    return checks


def build_validation_checks_df(
    source_contracts: list[MarketInputSourceContract],
) -> pd.DataFrame:
    checks: list[dict[str, Any]] = []

    for anchor_path in PHASE_6_REQUIRED_ANCHORS:
        exists = anchor_path.exists()
        checks.append(
            build_check(
                check_group="phase_6_anchor",
                check_name=f"anchor_exists:{anchor_path}",
                passed=exists,
                severity="INFO" if exists else "ERROR",
                details=str(anchor_path),
            )
        )

    for input_type, input_dir in OPERATIONAL_INPUT_DIRECTORIES.items():
        exists = input_dir.exists()
        checks.append(
            build_check(
                check_group="operational_input_directory",
                check_name=f"directory_exists:{input_type}",
                passed=exists,
                severity="INFO" if exists else "ERROR",
                details=str(input_dir),
            )
        )

    for output_type, columns in REQUIRED_OUTPUT_SCHEMAS.items():
        has_columns = len(columns) > 0
        checks.append(
            build_check(
                check_group="output_schema",
                check_name=f"schema_defined:{output_type}",
                passed=has_columns,
                severity="INFO" if has_columns else "ERROR",
                details=f"columns={len(columns)}",
            )
        )

    for source_contract in source_contracts:
        checks.extend(validate_source_contract(source_contract))

    for flag_name, flag_value in EXECUTION_FLAGS.items():
        checks.append(
            build_check(
                check_group="execution_restrictions",
                check_name=f"execution_flag_false:{flag_name}",
                passed=flag_value is False,
                severity="INFO" if flag_value is False else "ERROR",
                details=f"{flag_name}={flag_value}",
            )
        )

    has_ohlc_source = any(
        "ohlc" in source_contract.allowed_output_types
        for source_contract in source_contracts
    )
    has_signal_source = any(
        "signals" in source_contract.allowed_output_types
        for source_contract in source_contracts
    )
    has_price_level_source = any(
        "price_levels" in source_contract.allowed_output_types
        for source_contract in source_contracts
    )

    checks.append(
        build_check(
            check_group="contract_coverage",
            check_name="has_ohlc_source",
            passed=has_ohlc_source,
            severity="INFO" if has_ohlc_source else "ERROR",
            details=f"has_ohlc_source={has_ohlc_source}",
        )
    )
    checks.append(
        build_check(
            check_group="contract_coverage",
            check_name="has_signal_source",
            passed=has_signal_source,
            severity="INFO" if has_signal_source else "ERROR",
            details=f"has_signal_source={has_signal_source}",
        )
    )
    checks.append(
        build_check(
            check_group="contract_coverage",
            check_name="has_price_level_source",
            passed=has_price_level_source,
            severity="INFO" if has_price_level_source else "ERROR",
            details=f"has_price_level_source={has_price_level_source}",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="phase_7_contract_does_not_complete_long_side",
            passed=True,
            severity="WARNING",
            details="LONG-side strategy remains future work.",
        )
    )

    checks.append(
        build_check(
            check_group="scope_control",
            check_name="phase_7_contract_does_not_approve_real_entries",
            passed=True,
            severity="WARNING",
            details="Real entries remain unapproved.",
        )
    )

    return pd.DataFrame(checks)


def build_summary_df(
    source_contracts_df: pd.DataFrame,
    output_schemas_df: pd.DataFrame,
    checks_df: pd.DataFrame,
) -> pd.DataFrame:
    blocker_count = int(checks_df["blocker"].astype(bool).sum())
    error_count = int(checks_df["severity"].eq("ERROR").sum())
    warning_count = int(checks_df["severity"].eq("WARNING").sum())

    validation_passed = blocker_count == 0 and error_count == 0

    return pd.DataFrame(
        [
            {
                "phase": "7.1",
                "source_contracts": len(source_contracts_df),
                "output_schema_rows": len(output_schemas_df),
                "total_checks": len(checks_df),
                "warning_count": warning_count,
                "error_count": error_count,
                "blocker_count": blocker_count,
                "phase_6_closed_required": True,
                "real_market_bridge_contract_defined": validation_passed,
                "real_market_fetch_enabled": False,
                "signal_generation_enabled": False,
                "long_side_established": False,
                "real_entries_approved": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "live_alerts_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
                "validation_passed": validation_passed,
                "validation_decision": (
                    "PHASE_7_1_REAL_MARKET_INPUT_BRIDGE_CONTRACT_VALIDATED"
                    if validation_passed
                    else "PHASE_7_1_REAL_MARKET_INPUT_BRIDGE_CONTRACT_FAILED"
                ),
            }
        ]
    )


def save_df(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def validate_real_market_input_bridge_contract(
    config: MarketInputBridgeContractConfig | None = None,
) -> dict[str, pd.DataFrame]:
    active_config = config or MarketInputBridgeContractConfig()
    active_config.reports_dir.mkdir(parents=True, exist_ok=True)

    source_contracts = build_market_input_source_contracts()

    source_contracts_df = build_source_contracts_df(source_contracts)
    output_schemas_df = build_output_schemas_df()
    checks_df = build_validation_checks_df(source_contracts)
    summary_df = build_summary_df(
        source_contracts_df=source_contracts_df,
        output_schemas_df=output_schemas_df,
        checks_df=checks_df,
    )

    save_df(
        summary_df,
        active_config.reports_dir / "real_market_input_bridge_contract_summary_v1.csv",
    )
    save_df(
        source_contracts_df,
        active_config.reports_dir / "real_market_input_source_contracts_v1.csv",
    )
    save_df(
        output_schemas_df,
        active_config.reports_dir / "real_market_input_output_schemas_v1.csv",
    )
    save_df(
        checks_df,
        active_config.reports_dir / "real_market_input_bridge_contract_checks_v1.csv",
    )

    return {
        "summary": summary_df,
        "source_contracts": source_contracts_df,
        "output_schemas": output_schemas_df,
        "checks": checks_df,
    }