from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any


PHASE = "10.42R.2I"
SCHEMA_VERSION = "CONTROLLED_HISTORICAL_EVALUATION_HARNESS_DESIGN_V1"
SOURCE_PHASE_2H_COMMIT = "5777da3d52908de15841c0e814290577ae4dffba"
SOURCE_PHASE_2H_PROTOCOL_SHA256 = (
    "a42a8da21d1afd231be37376de8ecdfc0306dc8db2375bacb5f2de567947e493"
)
RECOMMENDED_NEXT_PHASE = (
    "PHASE_10_42R_2J_FROZEN_RECOVERY_CANDIDATE_HISTORICAL_INPUT_"
    "MANIFEST_BINDING_AND_INTEGRITY_VALIDATION_V1"
)
REPAIR_POLICY = (
    "REPAIR_LINE_CLOSED_AFTER_2G_2H_NO_NEW_REPAIR_SUBPHASE_UNLESS_"
    "CONCRETE_REPRODUCIBLE_BLOCKER"
)
FINITE_COMPLETION_ROUTE = (
    "2I_HARNESS_DESIGN",
    "2J_INPUT_MANIFEST_BINDING_AND_INTEGRITY",
    "2K_CONTROLLED_KNOWN_EVIDENCE_EVALUATION",
    "2L_INDEPENDENT_RESULT_AUDIT_AND_DISPOSITION",
)

EXPECTED_SOURCE_HASHES = {
    "PHASE_10_42R_2H_MANIFEST.sha256":
        "23d12dd10bbc99d4caa39894f3831b121485d7aa86b602355b23c7961ae54df2",
    "docs/PHASE_10_42R_2H_FROZEN_RECOVERY_CANDIDATE_CONTROLLED_HISTORICAL_EVALUATION_PREREGISTRATION.md":
        "ca845711397f29f5c0bede77109bbf8c30eb8605f603eb5c494a9807f740b01c",
    "src/validation/frozen_recovery_candidate_controlled_historical_evaluation_preregistration_v1.py":
        "89c2d1fed13b1585be90931115c9a834b9009a4f895ee8785cfc14a5910fbcf4",
    "docs/PHASE_10_42R_2G_FROZEN_RECOVERY_CANDIDATE_CORRECTION_INDEPENDENT_SYNTHETIC_ACCEPTANCE.md":
        "d92d8e1240ff39e4d8942ca628f8c0ccfbd8a38f15a617f12b3b51a1f39a98da",
    "src/analysis/frozen_recovery_candidate_implementation_v2.py":
        "ccf3cc05823515fa56e9e1183eb51ab903503e310aa037248847ad7445b2cc1e",
}

FORBIDDEN_ARTIFACT_PATHS = (
    "data/holdout/strategy_recovery_retrospective_lockbox_2026h1_v1.csv",
    "data/holdout/strategy_recovery_prospective_20260720_20270120_v1.csv",
    "data/forward/long_forward_observation_dataset_v1.csv",
)

FORBIDDEN_IMPORT_PREFIXES = (
    "pandas",
    "numpy",
    "scipy",
    "src.backtesting",
    "src.exchange",
    "src.analysis",
    "src.execution",
    "src.long_side",
    "src.journal",
)

SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
TIMEFRAMES = ("15m", "1h", "4h")
VARIANTS = (
    "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N48_V01",
    "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_N96_V02",
    "RCV_SHORT_BREAKDOWN_RETEST_F02_N48_V01",
    "RCV_SHORT_BREAKDOWN_RETEST_F02_N96_V02",
    "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_S000_V01",
    "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_S025_V02",
)
FAMILIES = (
    "RCV_SHORT_UPSIDE_SWEEP_REVERSAL_F01_V1",
    "RCV_SHORT_BREAKDOWN_RETEST_F02_V1",
    "RCV_SHORT_EMA_PULLBACK_CONTINUATION_F03_V1",
)
COST_PROFILE_IDS = (
    "BINANCE_SCALP_BASE_ESTIMATE",
    "BINANCE_SCALP_STRESS_ESTIMATE",
    "QUANTFURY_SWING_BASE_ESTIMATE",
    "QUANTFURY_SWING_STRESS_ESTIMATE",
    "EXTREME_COST_STRESS_TEST",
)

PERMISSIONS = {
    name: False
    for name in (
        "real_data_access_allowed",
        "historical_evaluation_allowed",
        "historical_input_binding_allowed",
        "historical_file_hashing_allowed",
        "historical_schema_parsing_allowed",
        "retrospective_lockbox_access_allowed",
        "prospective_holdout_access_allowed",
        "performance_metrics_allowed",
        "candidate_comparison_allowed",
        "candidate_ranking_allowed",
        "winner_selection_allowed",
        "candidate_mutation_allowed",
        "forward_observation_allowed",
        "official_dataset_write_allowed",
        "evidence_persistence_allowed",
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
}


@dataclass(frozen=True)
class Check:
    check_id: str
    check_name: str
    passed: bool
    details: str
    blocker: bool


@dataclass(frozen=True)
class ManifestField:
    position: int
    name: str
    field_type: str
    required_before_first_byte_read: bool
    immutable_after_binding: bool
    description: str


@dataclass(frozen=True)
class DatasetSlotTemplate:
    evaluation_order: int
    slot_id: str
    symbol: str
    timeframe: str
    role: str
    evidence_window_id: str
    binding_state: str
    relative_path: str
    file_sha256: str
    content_read_allowed_in_phase_2i: bool


@dataclass(frozen=True)
class HarnessComponent:
    evaluation_order: int
    component_id: str
    responsibility: str
    depends_on: tuple[str, ...]
    reads_market_content_in_phase_2i: bool
    writes_result_artifacts_in_phase_2i: bool
    implemented_in_phase_2i: bool


@dataclass(frozen=True)
class StateTransition:
    evaluation_order: int
    from_state: str
    event: str
    to_state: str
    permitted_in_phase_2i: bool
    fail_closed: bool


@dataclass(frozen=True)
class FailureMode:
    failure_id: str
    category: str
    detection_contract: str
    terminal_state: str
    blocks_all_downstream_stages: bool


@dataclass(frozen=True)
class AuditArtifactDesign:
    evaluation_order: int
    artifact_id: str
    future_relative_path_template: str
    format: str
    production_stage: str
    write_allowed_in_phase_2i: bool
    required_for_future_reproducibility: bool


@dataclass(frozen=True)
class RunInvariant:
    invariant_id: str
    category: str
    invariant: str
    enforced_fail_closed: bool
    mutable_after_first_historical_read: bool


@dataclass(frozen=True)
class HarnessDesign:
    schema_version: str
    source_phase_2h_commit: str
    source_phase_2h_protocol_sha256: str
    repair_policy: str
    finite_completion_route: tuple[str, ...]
    symbols: tuple[str, ...]
    timeframes: tuple[str, ...]
    variants: tuple[str, ...]
    families: tuple[str, ...]
    cost_profile_ids: tuple[str, ...]
    manifest_fields: tuple[ManifestField, ...]
    dataset_slots: tuple[DatasetSlotTemplate, ...]
    components: tuple[HarnessComponent, ...]
    state_transitions: tuple[StateTransition, ...]
    failure_modes: tuple[FailureMode, ...]
    audit_artifacts: tuple[AuditArtifactDesign, ...]
    invariants: tuple[RunInvariant, ...]
    permissions: tuple[tuple[str, bool], ...]


class HarnessDesignFailure(RuntimeError):
    pass


def normalized_source_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_manifest_fields() -> tuple[ManifestField, ...]:
    rows = (
        ("slot_id", "STRING", True, True, "Unique logical 3x3 slot identifier."),
        ("symbol", "ENUM", True, True, "One fixed symbol from the preregistered cohort."),
        ("timeframe", "ENUM", True, True, "One fixed timeframe: 15m, 1h or 4h."),
        ("role", "ENUM", True, True, "Signal/execution clock or closed-context-only role."),
        ("evidence_window_id", "ENUM", True, True, "Known evidence only for the first evaluation."),
        ("relative_path", "POSIX_RELATIVE_PATH", True, True, "Repository-relative path; no absolute or parent traversal."),
        ("file_sha256", "LOWER_HEX_64", True, True, "Immutable byte-level SHA-256 before parsing."),
        ("size_bytes", "NON_NEGATIVE_INTEGER", True, True, "Exact physical byte size."),
        ("row_count", "POSITIVE_INTEGER", True, True, "Exact parsed data-row count excluding header."),
        ("first_open_time_utc", "RFC3339_UTC", True, True, "First bar open timestamp."),
        ("last_close_time_utc", "RFC3339_UTC", True, True, "Last bar close timestamp."),
        ("expected_columns_json", "CANONICAL_JSON_ARRAY", True, True, "Exact ordered schema contract."),
        ("timestamp_unit", "ENUM", True, True, "UTC timestamp representation and precision."),
        ("interval_seconds", "POSITIVE_INTEGER", True, True, "900, 3600 or 14400 according to timeframe."),
        ("source_provider", "STRING", True, True, "Declared market-data provider."),
        ("source_market", "STRING", True, True, "Declared venue and market type."),
        ("acquisition_method", "STRING", True, True, "How the immutable source file was produced."),
        ("acquisition_time_utc", "RFC3339_UTC", True, True, "Acquisition or export timestamp."),
        ("provenance_sha256", "LOWER_HEX_64", True, True, "Hash of canonical provenance record."),
        ("duplicate_open_time_count", "NON_NEGATIVE_INTEGER", True, True, "Must equal zero."),
        ("duplicate_close_time_count", "NON_NEGATIVE_INTEGER", True, True, "Must equal zero."),
        ("missing_interval_count", "NON_NEGATIVE_INTEGER", True, True, "Coverage diagnostic frozen before evaluation."),
        ("invalid_ohlcv_row_count", "NON_NEGATIVE_INTEGER", True, True, "Must equal zero."),
        ("binding_state", "ENUM", True, True, "BOUND_VERIFIED required before evaluator enablement."),
        ("manifest_row_sha256", "LOWER_HEX_64", True, True, "Hash of the canonical manifest row excluding this field."),
    )
    return tuple(
        ManifestField(index, name, field_type, before_read, immutable, description)
        for index, (name, field_type, before_read, immutable, description)
        in enumerate(rows, start=1)
    )


def build_dataset_slots() -> tuple[DatasetSlotTemplate, ...]:
    slots = []
    order = 1
    for symbol in SYMBOLS:
        for timeframe in TIMEFRAMES:
            role = (
                "PRIMARY_SIGNAL_AND_SIMULATED_EXECUTION"
                if timeframe == "15m"
                else "CLOSED_CONTEXT_ONLY"
            )
            slots.append(DatasetSlotTemplate(
                evaluation_order=order,
                slot_id=f"{symbol}_{timeframe.upper()}_KNOWN_2022_2025",
                symbol=symbol,
                timeframe=timeframe,
                role=role,
                evidence_window_id="KNOWN_EVIDENCE_2022_2025",
                binding_state="UNBOUND_DESIGN_ONLY",
                relative_path="",
                file_sha256="",
                content_read_allowed_in_phase_2i=False,
            ))
            order += 1
    return tuple(slots)


def build_components() -> tuple[HarnessComponent, ...]:
    rows = (
        ("C01_SOURCE_ANCHOR_VERIFIER", "Verify frozen code, protocol and commit anchors.", ()),
        ("C02_INPUT_MANIFEST_BINDER", "Bind the nine logical slots without evaluating market content.", ("C01_SOURCE_ANCHOR_VERIFIER",)),
        ("C03_BYTE_INTEGRITY_VERIFIER", "Verify file size and SHA-256 before schema parsing.", ("C02_INPUT_MANIFEST_BINDER",)),
        ("C04_SCHEMA_AND_COVERAGE_VALIDATOR", "Validate ordered columns, timestamps, intervals and OHLCV integrity.", ("C03_BYTE_INTEGRITY_VERIFIER",)),
        ("C05_CLOSED_MTF_ALIGNMENT_ENGINE", "Expose 1H and 4H context only after each source candle close.", ("C04_SCHEMA_AND_COVERAGE_VALIDATOR",)),
        ("C06_FROZEN_VARIANT_EVALUATOR", "Evaluate the six corrected frozen variants in fixed order.", ("C05_CLOSED_MTF_ALIGNMENT_ENGINE",)),
        ("C07_NEXT_OPEN_ORDER_ENGINE", "Construct fail-closed next-15m-open SHORT orders.", ("C06_FROZEN_VARIANT_EVALUATOR",)),
        ("C08_POSITION_AND_EXIT_ENGINE", "Enforce non-overlap, 2.5R, stop-first and bar-240 exit.", ("C07_NEXT_OPEN_ORDER_ENGINE",)),
        ("C09_SINGLE_PROFILE_COST_ACCOUNTING", "Reconstruct gross R and apply one frozen cost profile exactly once.", ("C08_POSITION_AND_EXIT_ENGINE",)),
        ("C10_METRIC_AND_SLICE_AGGREGATOR", "Build only preregistered metrics and slices.", ("C09_SINGLE_PROFILE_COST_ACCOUNTING",)),
        ("C11_MULTIPLICITY_CONTROLLER", "Apply the inherited six-test Holm contract in fixed order.", ("C10_METRIC_AND_SLICE_AGGREGATOR",)),
        ("C12_GATE_CLASSIFIER", "Classify every variant against all gates without ranking or winner selection.", ("C11_MULTIPLICITY_CONTROLLER",)),
        ("C13_AUDIT_BUNDLE_WRITER", "Persist a reproducible future audit bundle only after successful evaluation.", ("C12_GATE_CLASSIFIER",)),
    )
    return tuple(
        HarnessComponent(
            evaluation_order=index,
            component_id=component_id,
            responsibility=responsibility,
            depends_on=dependencies,
            reads_market_content_in_phase_2i=False,
            writes_result_artifacts_in_phase_2i=False,
            implemented_in_phase_2i=False,
        )
        for index, (component_id, responsibility, dependencies)
        in enumerate(rows, start=1)
    )


def build_state_transitions() -> tuple[StateTransition, ...]:
    rows = (
        ("DESIGN_UNINITIALIZED", "BUILD_DESIGN", "DESIGN_DRAFTED", True, True),
        ("DESIGN_DRAFTED", "VERIFY_SOURCE_ANCHORS", "SOURCE_ANCHORS_VERIFIED", True, True),
        ("SOURCE_ANCHORS_VERIFIED", "FREEZE_MANIFEST_SCHEMA", "MANIFEST_SCHEMA_FROZEN", True, True),
        ("MANIFEST_SCHEMA_FROZEN", "FREEZE_COMPONENT_GRAPH", "COMPONENT_GRAPH_FROZEN", True, True),
        ("COMPONENT_GRAPH_FROZEN", "FREEZE_FAILURE_GUARDS", "FAILURE_GUARDS_FROZEN", True, True),
        ("FAILURE_GUARDS_FROZEN", "FREEZE_AUDIT_CONTRACT", "AUDIT_CONTRACT_FROZEN", True, True),
        ("AUDIT_CONTRACT_FROZEN", "VALIDATE_DESIGN", "DESIGN_VALIDATED", True, True),
        ("DESIGN_VALIDATED", "CLOSE_PHASE", "DESIGN_FROZEN_TERMINAL", True, True),
        ("DESIGN_FROZEN_TERMINAL", "BIND_INPUT_MANIFEST", "INPUT_BINDING_PHASE_REQUIRED", False, True),
        ("INPUT_BINDING_PHASE_REQUIRED", "READ_MARKET_BYTES", "BLOCKED_WRONG_PHASE", False, True),
        ("INPUT_BINDING_PHASE_REQUIRED", "RUN_HISTORICAL_EVALUATION", "BLOCKED_WRONG_PHASE", False, True),
        ("DESIGN_FROZEN_TERMINAL", "OPEN_LOCKBOX", "BLOCKED_LOCKBOX_SEALED", False, True),
    )
    return tuple(
        StateTransition(index, from_state, event, to_state, permitted, fail_closed)
        for index, (from_state, event, to_state, permitted, fail_closed)
        in enumerate(rows, start=1)
    )


def build_failure_modes() -> tuple[FailureMode, ...]:
    rows = (
        ("F001", "SOURCE", "Frozen source commit or normalized hash mismatch."),
        ("F002", "MANIFEST", "Not exactly nine logical dataset slots."),
        ("F003", "MANIFEST", "Duplicate symbol/timeframe/evidence-window slot."),
        ("F004", "PATH", "Absolute path, parent traversal or path outside repository."),
        ("F005", "INTEGRITY", "Missing file, size mismatch or SHA-256 mismatch."),
        ("F006", "SCHEMA", "Ordered columns differ from the frozen schema."),
        ("F007", "TIMESTAMP", "Non-UTC, unparsable, duplicate or non-monotonic timestamps."),
        ("F008", "COVERAGE", "File coverage does not contain the preregistered known-evidence interval."),
        ("F009", "INTERVAL", "Unexpected interval spacing without frozen missing-bar classification."),
        ("F010", "OHLCV", "NaN, infinity, negative volume or structurally invalid OHLC row."),
        ("F011", "MTF", "1H or 4H context exposed before source-candle close."),
        ("F012", "SIGNAL", "Variant identity differs from the six-item frozen registry."),
        ("F013", "ORDER", "Fill is not exactly next 15m open or gap stop is invalid."),
        ("F014", "POSITION", "Overlapping position or non-boolean position state."),
        ("F015", "EXIT", "Exit resolution differs from stop-first, target or bar-240 contract."),
        ("F016", "COST", "Fee, spread or slippage double-counted or unknown profile used."),
        ("F017", "METRIC", "Unregistered metric, slice deletion or chronological order violation."),
        ("F018", "MULTIPLICITY", "P-value count/order/method differs from frozen contract."),
        ("F019", "INTERPRETATION", "Comparison, ranking, winner or operational approval attempted."),
        ("F020", "LOCKBOX", "Retrospective lockbox or prospective holdout access attempted."),
    )
    return tuple(
        FailureMode(
            failure_id=failure_id,
            category=category,
            detection_contract=contract,
            terminal_state="BLOCKED_FAIL_CLOSED",
            blocks_all_downstream_stages=True,
        )
        for failure_id, category, contract in rows
    )


def build_audit_artifacts() -> tuple[AuditArtifactDesign, ...]:
    rows = (
        ("A01_INPUT_MANIFEST", "reports/phase_10_42r_2k/{run_id}/input_manifest.json", "JSON", "PRE_EVALUATION"),
        ("A02_SOURCE_ANCHORS", "reports/phase_10_42r_2k/{run_id}/source_anchors.json", "JSON", "PRE_EVALUATION"),
        ("A03_ENVIRONMENT", "reports/phase_10_42r_2k/{run_id}/environment.json", "JSON", "PRE_EVALUATION"),
        ("A04_DATA_QUALITY", "reports/phase_10_42r_2k/{run_id}/data_quality.json", "JSON", "PRE_EVALUATION"),
        ("A05_SIGNAL_LEDGER", "reports/phase_10_42r_2k/{run_id}/signal_ledger.csv", "CSV", "EVALUATION"),
        ("A06_ORDER_LEDGER", "reports/phase_10_42r_2k/{run_id}/order_ledger.csv", "CSV", "EVALUATION"),
        ("A07_TRADE_LEDGER", "reports/phase_10_42r_2k/{run_id}/trade_ledger.csv", "CSV", "EVALUATION"),
        ("A08_METRIC_TABLE", "reports/phase_10_42r_2k/{run_id}/metric_table.csv", "CSV", "POST_EVALUATION"),
        ("A09_MULTIPLICITY_TABLE", "reports/phase_10_42r_2k/{run_id}/multiplicity_table.csv", "CSV", "POST_EVALUATION"),
        ("A10_GATE_CLASSIFICATION", "reports/phase_10_42r_2k/{run_id}/gate_classification.csv", "CSV", "POST_EVALUATION"),
        ("A11_CHECK_LEDGER", "reports/phase_10_42r_2k/{run_id}/check_ledger.csv", "CSV", "POST_EVALUATION"),
        ("A12_RUN_SUMMARY", "reports/phase_10_42r_2k/{run_id}/run_summary.json", "JSON", "POST_EVALUATION"),
    )
    return tuple(
        AuditArtifactDesign(
            evaluation_order=index,
            artifact_id=artifact_id,
            future_relative_path_template=path,
            format=format_name,
            production_stage=stage,
            write_allowed_in_phase_2i=False,
            required_for_future_reproducibility=True,
        )
        for index, (artifact_id, path, format_name, stage)
        in enumerate(rows, start=1)
    )


def build_invariants() -> tuple[RunInvariant, ...]:
    rows = (
        ("I001", "SOURCE", "2H commit and protocol hash must match exactly."),
        ("I002", "REGISTRY", "Exactly six variants and three families in frozen order."),
        ("I003", "DATASET", "Exactly nine known-evidence slots: three symbols x three timeframes."),
        ("I004", "PATH", "All input paths are repository-relative and immutable after binding."),
        ("I005", "INTEGRITY", "Every input file is size- and SHA-256-verified before parsing."),
        ("I006", "SCHEMA", "All datasets share the frozen ordered OHLCV schema."),
        ("I007", "TIME", "All timestamps are UTC, unique and strictly increasing."),
        ("I008", "COVERAGE", "Known-evidence coverage is half-open [2022-01-01, 2026-01-01)."),
        ("I009", "LOCKBOX", "Retrospective and prospective lockboxes remain inaccessible."),
        ("I010", "MTF", "Higher-timeframe context is available only after source close."),
        ("I011", "SIGNAL", "Signals are computed only from completed 15m bars."),
        ("I012", "FILL", "Accepted SHORT orders fill only at the next 15m open."),
        ("I013", "POSITION", "Only one position may be active at a time."),
        ("I014", "EXIT", "2.5R, stop-first simultaneous and bar-240 time exit are immutable."),
        ("I015", "COST", "Exactly one frozen round-trip cost profile is applied per result view."),
        ("I016", "METRIC", "Only preregistered metrics and slices may be produced."),
        ("I017", "DRAWDOWN", "Chronological drawdown ordering is immutable."),
        ("I018", "MULTIPLICITY", "Six p-values form one fixed-order Holm pool at alpha 0.05."),
        ("I019", "INTERPRETATION", "The evaluator classifies but never ranks or selects a winner."),
        ("I020", "OPERATIONS", "No research result enables paper, capital, alerts, execution or automation."),
        ("I021", "REPRODUCIBILITY", "The complete audit bundle must be internally hash-linked."),
        ("I022", "MUTATION", "Any contract change creates a new version and invalidates prior unopened claims."),
        ("I023", "REPAIR", "No new repair subphase without a concrete reproducible blocker."),
        ("I024", "TERMINATION", "After all design checks pass, 2I closes and advances to 2J."),
    )
    return tuple(
        RunInvariant(invariant_id, category, invariant, True, False)
        for invariant_id, category, invariant in rows
    )


def build_design() -> HarnessDesign:
    return HarnessDesign(
        schema_version=SCHEMA_VERSION,
        source_phase_2h_commit=SOURCE_PHASE_2H_COMMIT,
        source_phase_2h_protocol_sha256=SOURCE_PHASE_2H_PROTOCOL_SHA256,
        repair_policy=REPAIR_POLICY,
        finite_completion_route=FINITE_COMPLETION_ROUTE,
        symbols=SYMBOLS,
        timeframes=TIMEFRAMES,
        variants=VARIANTS,
        families=FAMILIES,
        cost_profile_ids=COST_PROFILE_IDS,
        manifest_fields=build_manifest_fields(),
        dataset_slots=build_dataset_slots(),
        components=build_components(),
        state_transitions=build_state_transitions(),
        failure_modes=build_failure_modes(),
        audit_artifacts=build_audit_artifacts(),
        invariants=build_invariants(),
        permissions=tuple(sorted(PERMISSIONS.items())),
    )


def design_sha256(design: HarnessDesign | None = None) -> str:
    payload = json.dumps(
        asdict(design or build_design()),
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate_design_object(design: HarnessDesign) -> tuple[str, ...]:
    expected = build_design()
    failures = []
    for field_name in expected.__dataclass_fields__:
        if getattr(design, field_name) != getattr(expected, field_name):
            failures.append(field_name)
    return tuple(failures)


def _append(checks: list[Check], name: str, passed: bool, details: str) -> None:
    checks.append(Check(
        check_id=f"2I-CHECK-{len(checks)+1:03d}",
        check_name=name,
        passed=bool(passed),
        details=details,
        blocker=not bool(passed),
    ))


def _source_is_isolated(path: Path) -> tuple[bool, str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    forbidden = sorted(
        item for item in imports
        if any(
            item == prefix or item.startswith(prefix + ".")
            for prefix in FORBIDDEN_IMPORT_PREFIXES
        )
    )
    return not forbidden, "forbidden_imports=" + ",".join(forbidden)


def _source_commit_is_ancestor(root: Path) -> tuple[bool, str]:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", SOURCE_PHASE_2H_COMMIT, "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0, f"returncode={result.returncode}"


def _component_graph_is_ordered_acyclic(
    components: tuple[HarnessComponent, ...],
) -> bool:
    order = {component.component_id: component.evaluation_order for component in components}
    return all(
        dependency in order and order[dependency] < component.evaluation_order
        for component in components
        for dependency in component.depends_on
    )


def _design_checks(design: HarnessDesign) -> tuple[tuple[str, bool, str], ...]:
    slots = design.dataset_slots
    fields = design.manifest_fields
    components = design.components
    transitions = design.state_transitions
    failures = design.failure_modes
    artifacts = design.audit_artifacts
    invariants = design.invariants
    return (
        ("manifest_field_count_twenty_five", len(fields) == 25, str(len(fields))),
        ("manifest_field_order_exact", tuple(field.position for field in fields) == tuple(range(1, 26)), "1..25"),
        ("manifest_identity_fields_required", tuple(field.name for field in fields[:7]) == (
            "slot_id", "symbol", "timeframe", "role", "evidence_window_id", "relative_path", "file_sha256",
        ), ",".join(field.name for field in fields[:7])),
        ("all_manifest_fields_immutable", all(field.immutable_after_binding for field in fields), "all immutable"),
        ("dataset_slot_count_nine", len(slots) == 9, str(len(slots))),
        ("dataset_cross_product_exact", {(slot.symbol, slot.timeframe) for slot in slots} == {
            (symbol, timeframe) for symbol in SYMBOLS for timeframe in TIMEFRAMES
        }, "3x3"),
        ("all_slots_unbound_and_unread", all(
            slot.binding_state == "UNBOUND_DESIGN_ONLY"
            and slot.relative_path == ""
            and slot.file_sha256 == ""
            and not slot.content_read_allowed_in_phase_2i
            for slot in slots
        ), "unbound design only"),
        ("known_evidence_only", all(slot.evidence_window_id == "KNOWN_EVIDENCE_2022_2025" for slot in slots), "known evidence"),
        ("component_count_thirteen", len(components) == 13, str(len(components))),
        ("component_orders_exact", tuple(component.evaluation_order for component in components) == tuple(range(1, 14)), "1..13"),
        ("component_graph_ordered_acyclic", _component_graph_is_ordered_acyclic(components), "dependency order"),
        ("components_not_implemented_in_design", all(not component.implemented_in_phase_2i for component in components), "design only"),
        ("components_do_not_read_or_write_in_2i", all(
            not component.reads_market_content_in_phase_2i
            and not component.writes_result_artifacts_in_phase_2i
            for component in components
        ), "zero runtime side effects"),
        ("state_transition_count_twelve", len(transitions) == 12, str(len(transitions))),
        ("design_terminal_state_exact", any(
            transition.to_state == "DESIGN_FROZEN_TERMINAL"
            and transition.permitted_in_phase_2i
            for transition in transitions
        ), "terminal frozen"),
        ("runtime_events_blocked_in_2i", all(
            not transition.permitted_in_phase_2i
            for transition in transitions
            if transition.event in ("BIND_INPUT_MANIFEST", "READ_MARKET_BYTES", "RUN_HISTORICAL_EVALUATION", "OPEN_LOCKBOX")
        ), "runtime blocked"),
        ("all_transitions_fail_closed", all(transition.fail_closed for transition in transitions), "fail closed"),
        ("failure_mode_count_twenty", len(failures) == 20, str(len(failures))),
        ("all_failure_modes_terminal", all(
            failure.terminal_state == "BLOCKED_FAIL_CLOSED"
            and failure.blocks_all_downstream_stages
            for failure in failures
        ), "all terminal blockers"),
        ("audit_artifact_count_twelve", len(artifacts) == 12, str(len(artifacts))),
        ("audit_artifact_paths_future_2k_only", all("phase_10_42r_2k" in artifact.future_relative_path_template for artifact in artifacts), "2K templates"),
        ("audit_writes_blocked_in_2i", all(not artifact.write_allowed_in_phase_2i for artifact in artifacts), "writes false"),
        ("invariant_count_twenty_four", len(invariants) == 24, str(len(invariants))),
        ("all_invariants_fail_closed_immutable", all(
            invariant.enforced_fail_closed
            and not invariant.mutable_after_first_historical_read
            for invariant in invariants
        ), "locked"),
        ("repair_policy_closes_recursive_repairs", design.repair_policy == REPAIR_POLICY and "NO_NEW_REPAIR_SUBPHASE" in design.repair_policy, design.repair_policy),
        ("finite_completion_route_exact", design.finite_completion_route == FINITE_COMPLETION_ROUTE and len(design.finite_completion_route) == 4, ",".join(design.finite_completion_route)),
        ("source_protocol_hash_locked", design.source_phase_2h_protocol_sha256 == SOURCE_PHASE_2H_PROTOCOL_SHA256, design.source_phase_2h_protocol_sha256),
        ("registry_and_cost_scope_exact", len(design.variants) == 6 and len(design.families) == 3 and design.cost_profile_ids == COST_PROFILE_IDS, "6/3/5"),
        ("all_permissions_false", all(not value for _, value in design.permissions), str(len(design.permissions))),
        ("design_object_exact", not validate_design_object(design), ",".join(validate_design_object(design))),
        ("design_hash_deterministic", design_sha256(design) == design_sha256(build_design()), design_sha256(design)),
    )


def validate_phase_10_42r_2i(
    *, preflight_only: bool = False, root: Path | None = None
) -> dict[str, Any]:
    project_root = (root or Path.cwd()).resolve()
    checks: list[Check] = []

    passed, details = _source_commit_is_ancestor(project_root)
    _append(checks, "source_phase_2h_commit_is_ancestor", passed, details)

    for relative_path, expected_hash in EXPECTED_SOURCE_HASHES.items():
        path = project_root / relative_path
        actual = normalized_source_sha256(path) if path.is_file() else ""
        _append(
            checks,
            "source_anchor_" + relative_path.replace("/", "_"),
            path.is_file() and actual == expected_hash,
            f"expected={expected_hash},actual={actual}",
        )

    module_path = project_root / (
        "src/validation/frozen_recovery_candidate_controlled_"
        "historical_evaluation_harness_design_v1.py"
    )
    _append(checks, "phase_2i_source_exists", module_path.is_file(), str(module_path))
    isolated, details = _source_is_isolated(module_path) if module_path.is_file() else (False, "missing")
    _append(checks, "phase_2i_source_is_static_and_isolated", isolated, details)

    existing = tuple(
        path for path in FORBIDDEN_ARTIFACT_PATHS
        if (project_root / path).exists()
    )
    _append(checks, "lockboxes_and_official_dataset_absent", not existing, ",".join(existing))
    _append(checks, "harness_design_build_deterministic", build_design() == build_design(), design_sha256())
    _append(checks, "all_permissions_false", all(not value for value in PERMISSIONS.values()), str(len(PERMISSIONS)))
    _append(checks, "no_market_result_or_lockbox_content_read", True, "source hashes and path existence only")

    preflight_count = len(checks)
    design = build_design()

    if not preflight_only:
        for name, ok, detail in _design_checks(design):
            _append(checks, name, ok, detail)

    failed = tuple(check for check in checks if not check.passed)
    validation_passed = not failed
    decision = (
        "PREFLIGHT_PASSED"
        if preflight_only and validation_passed
        else "CONTROLLED_HISTORICAL_EVALUATION_HARNESS_DESIGN_FROZEN"
        if validation_passed
        else "CONTROLLED_HISTORICAL_EVALUATION_HARNESS_DESIGN_BLOCKED"
    )

    summary = {
        "phase": PHASE,
        "preflight_only": preflight_only,
        "source_phase_2h_commit": SOURCE_PHASE_2H_COMMIT,
        "source_phase_2h_protocol_sha256": SOURCE_PHASE_2H_PROTOCOL_SHA256,
        "harness_design_sha256": design_sha256(design),
        "source_anchor_count": len(EXPECTED_SOURCE_HASHES),
        "manifest_field_count": len(design.manifest_fields),
        "dataset_slot_template_count": len(design.dataset_slots),
        "component_count": len(design.components),
        "state_transition_count": len(design.state_transitions),
        "failure_mode_count": len(design.failure_modes),
        "audit_artifact_design_count": len(design.audit_artifacts),
        "run_invariant_count": len(design.invariants),
        "variant_count": len(design.variants),
        "family_count": len(design.families),
        "cost_profile_count": len(design.cost_profile_ids),
        "finite_completion_phase_count": len(design.finite_completion_route),
        "preflight_check_count": preflight_count,
        "design_check_count": 0 if preflight_only else len(checks) - preflight_count,
        "total_check_count": len(checks),
        "failed_check_count": len(failed),
        "blocker_count": len(failed),
        "real_data_content_read_count": 0,
        "historical_file_hash_read_count": 0,
        "historical_schema_parse_count": 0,
        "historical_evaluation_count": 0,
        "backtest_execution_count": 0,
        "retrospective_lockbox_access_count": 0,
        "prospective_holdout_access_count": 0,
        "performance_metric_count": 0,
        "candidate_comparison_count": 0,
        "candidate_ranking_count": 0,
        "winner_selection_count": 0,
        "result_artifact_write_count": 0,
        "permissions_enabled_count": sum(PERMISSIONS.values()),
        "repair_phase_count": 0,
        "repair_cycle_open": False,
        "harness_implemented": False,
        "historical_evaluation_allowed": False,
        "design_frozen": bool(validation_passed and not preflight_only),
        "validation_decision": decision,
        "validation_passed": validation_passed,
        "recommended_next_phase": RECOMMENDED_NEXT_PHASE if validation_passed and not preflight_only else "NONE",
    }
    return {
        "summary": summary,
        "checks": tuple(asdict(check) for check in checks),
        "failed_checks": tuple(asdict(check) for check in failed),
        "design": asdict(design),
        "permissions": dict(design.permissions),
    }


def require_valid_harness_design(
    *, preflight_only: bool = False, root: Path | None = None
) -> dict[str, Any]:
    result = validate_phase_10_42r_2i(preflight_only=preflight_only, root=root)
    if not result["summary"]["validation_passed"]:
        names = ", ".join(item["check_name"] for item in result["failed_checks"])
        raise HarnessDesignFailure("Phase 10.42R.2I failed: " + names)
    return result


__all__ = [
    "COST_PROFILE_IDS", "DatasetSlotTemplate", "EXPECTED_SOURCE_HASHES",
    "FAMILIES", "FINITE_COMPLETION_ROUTE", "FORBIDDEN_ARTIFACT_PATHS",
    "HarnessComponent", "HarnessDesign", "HarnessDesignFailure",
    "ManifestField", "PERMISSIONS", "PHASE", "RECOMMENDED_NEXT_PHASE",
    "REPAIR_POLICY", "RunInvariant", "SCHEMA_VERSION", "SOURCE_PHASE_2H_COMMIT",
    "SOURCE_PHASE_2H_PROTOCOL_SHA256", "SYMBOLS", "StateTransition",
    "TIMEFRAMES", "VARIANTS", "build_audit_artifacts", "build_components",
    "build_dataset_slots", "build_design", "build_failure_modes",
    "build_invariants", "build_manifest_fields", "build_state_transitions",
    "design_sha256", "normalized_source_sha256", "replace",
    "require_valid_harness_design", "validate_design_object",
    "validate_phase_10_42r_2i",
]
