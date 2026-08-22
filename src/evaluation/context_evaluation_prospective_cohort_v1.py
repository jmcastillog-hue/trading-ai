from __future__ import annotations

import hashlib
import json
import os
import shutil
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.context.context_feature_pack_v1_level_a_standard import (
    PACK_FILENAME as CONTEXT_PACK_FILENAME,
    validate_context_feature_pack_v1_package,
)
from src.evaluation.context_evaluation_engine_v1 import (
    COHORT_MANIFEST_SCHEMA_VERSION,
    load_context_evaluation_engine_policy_v1,
    validate_cohort_manifest_v1,
    validate_hypothesis_manifest_v1,
)
from src.long_side.forward_outcome_labeler_v1 import (
    validate_forward_outcome_label_package,
)

CAPABILITY = "CONTEXT_EVALUATION_PROSPECTIVE_COHORT_V1"
POLICY_SCHEMA_VERSION = "CONTEXT_EVALUATION_PROSPECTIVE_COHORT_POLICY_V1"
PLAN_SCHEMA_VERSION = "CONTEXT_EVALUATION_PROSPECTIVE_COHORT_PLAN_V1"
ROOT_SCHEMA_VERSION = "CONTEXT_EVALUATION_PROSPECTIVE_COHORT_ROOT_V1"
ADMISSION_SCHEMA_VERSION = "CONTEXT_EVALUATION_PROSPECTIVE_ADMISSION_V1"
BINDING_SCHEMA_VERSION = "CONTEXT_EVALUATION_PROSPECTIVE_OUTCOME_BINDING_V1"
MATERIALIZATION_SCHEMA_VERSION = "CONTEXT_EVALUATION_PROSPECTIVE_COHORT_MATERIALIZATION_V1"

INITIALIZE_AUTHORIZATION = "INITIALIZE_CONTEXT_EVALUATION_PROSPECTIVE_COHORT_V1"
ADMISSION_AUTHORIZATION = "PREPARE_CONTEXT_EVALUATION_PROSPECTIVE_ADMISSION_V1"
BINDING_AUTHORIZATION = "PREPARE_CONTEXT_EVALUATION_PROSPECTIVE_OUTCOME_BINDING_V1"
MATERIALIZE_AUTHORIZATION = "MATERIALIZE_CONTEXT_EVALUATION_ENGINE_COHORT_V1"

MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS = 10
IMPLEMENTATION_OR_REPAIR_ATTEMPT = 1
POLICY_PATH = Path("src/evaluation/resources/context_evaluation_prospective_cohort_policy_v1.json")
OFFICIAL_APPEND_GATE_NAME = "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
OFFICIAL_DATASET = Path("data/forward/long_forward_observation_dataset_v1.csv")
OFFICIAL_MANIFEST = Path("data/forward/long_forward_observation_dataset_v1.manifest.csv")
OFFICIAL_LOCK = Path("data/forward/long_forward_observation_dataset_v1.lock")

ROOT_PLAN_FILENAME = "cohort_plan.json"
ROOT_BINDING_FILENAME = "hypothesis_binding.json"
ROOT_CHECKS_FILENAME = "cohort_root_checks.json"
ROOT_MANIFEST_FILENAME = "root_manifest.sha256"
ADMISSION_RECEIPT_FILENAME = "admission_receipt.json"
ADMISSION_CHECKS_FILENAME = "admission_checks.json"
BINDING_RECEIPT_FILENAME = "outcome_binding_receipt.json"
BINDING_CHECKS_FILENAME = "outcome_binding_checks.json"
PACKAGE_MANIFEST_FILENAME = "manifest.sha256"
MATERIALIZED_COHORT_FILENAME = "cohort_manifest.json"
MATERIALIZED_AUDIT_FILENAME = "cohort_materialization_audit.json"
MATERIALIZED_CHECKS_FILENAME = "cohort_materialization_checks.json"
OUTCOME_FILENAME = "forward_outcomes.json"
OUTCOME_DESCRIPTOR_FILENAME = "observation_descriptor.json"
BAR_DURATION = timedelta(minutes=15)

FORBIDDEN_PLAN_KEYS = (
    "price", "close", "open", "high", "low", "volume", "direction",
    "signal", "candidate", "return", "forward_return", "result", "mfe",
    "mae", "threshold", "score", "regime", "volatility", "feature",
)

class ContextEvaluationProspectiveCohortError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _req(ok: bool, code: str, message: str) -> None:
    if not ok:
        raise ContextEvaluationProspectiveCohortError(code, message)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _parse_utc(value: Any, field: str) -> datetime:
    try:
        dt = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContextEvaluationProspectiveCohortError("TIMESTAMP_INVALID", field) from exc
    _req(dt.tzinfo is not None, "TIMESTAMP_TIMEZONE_REQUIRED", field)
    return dt.astimezone(timezone.utc)


def _utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_sha(value: Any) -> bool:
    text = str(value or "")
    return len(text) == 64 and all(c in "0123456789abcdef" for c in text)


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")


def _canonical_json_sha256(value: Any) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest()


def _read_json(path: Path, code: str) -> dict[str, Any]:
    _req(path.is_file() and not path.is_symlink(), code, str(path))
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContextEvaluationProspectiveCohortError(code, str(path)) from exc
    _req(isinstance(value, Mapping), code, str(path))
    return dict(value)


def _write_new(path: Path, value: Any, *, raw: bool = False) -> None:
    payload = value if raw else _json_bytes(value)
    with path.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _gate_off() -> None:
    _req(os.environ.get(OFFICIAL_APPEND_GATE_NAME) != "1", "OFFICIAL_APPEND_GATE_ENABLED", OFFICIAL_APPEND_GATE_NAME)


def _official(repo: Path) -> dict[str, str]:
    dataset = repo / OFFICIAL_DATASET
    manifest = repo / OFFICIAL_MANIFEST
    lock = repo / OFFICIAL_LOCK
    _req(dataset.is_file() and not dataset.is_symlink(), "OFFICIAL_DATASET_INVALID", str(dataset))
    _req(manifest.is_file() and not manifest.is_symlink(), "OFFICIAL_MANIFEST_INVALID", str(manifest))
    _req(not lock.exists() and not lock.is_symlink(), "OFFICIAL_LOCK_PRESENT", str(lock))
    return {"dataset_sha256": _sha(dataset), "manifest_sha256": _sha(manifest)}


def _write_manifest(directory: Path, filename: str, names: Sequence[str]) -> None:
    lines = [f"{_sha(directory / name)}  {name}" for name in sorted(names)]
    _write_new(directory / filename, ("\n".join(lines) + "\n").encode("utf-8"), raw=True)


def _validate_manifest(directory: Path, filename: str, names: Sequence[str]) -> None:
    path = directory / filename
    _req(path.is_file() and not path.is_symlink(), "PACKAGE_MANIFEST_MISSING", str(path))
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    _req(len(lines) == len(names), "PACKAGE_MANIFEST_ENTRY_COUNT_INVALID", str(len(lines)))
    expected = set(names)
    seen = set()
    for line in lines:
        parts = line.split("  ", 1)
        _req(len(parts) == 2 and _is_sha(parts[0]), "PACKAGE_MANIFEST_LINE_INVALID", line)
        digest, name = parts
        _req(name in expected, "PACKAGE_MANIFEST_SCOPE_INVALID", name)
        target = directory / name
        _req(target.is_file() and not target.is_symlink(), "PACKAGE_MANIFEST_PAYLOAD_MISSING", name)
        _req(_sha(target) == digest, "PACKAGE_MANIFEST_HASH_MISMATCH", name)
        seen.add(name)
    _req(seen == expected, "PACKAGE_MANIFEST_SCOPE_INVALID", str(sorted(seen)))


def validate_context_evaluation_prospective_cohort_policy_v1(policy: Mapping[str, Any]) -> dict[str, Any]:
    _req(isinstance(policy, Mapping), "POLICY_INVALID", "mapping required")
    _req(policy.get("schema_version") == POLICY_SCHEMA_VERSION, "POLICY_SCHEMA_INVALID", str(policy.get("schema_version")))
    _req(policy.get("capability") == CAPABILITY, "POLICY_CAPABILITY_INVALID", str(policy.get("capability")))
    effective = _parse_utc(policy.get("policy_effective_from_utc"), "policy_effective_from_utc")
    frozen = _parse_utc(policy.get("preregistered_hypothesis_frozen_at_utc"), "preregistered_hypothesis_frozen_at_utc")
    _req(effective == frozen, "POLICY_EFFECTIVE_FREEZE_MISMATCH", _utc(effective))
    _req(policy.get("expected_hypothesis_manifest_schema") == "CONTEXT_EVALUATION_HYPOTHESIS_MANIFEST_V1", "POLICY_HYPOTHESIS_SCHEMA_INVALID", "schema")
    _req(policy.get("expected_engine_cohort_manifest_schema") == COHORT_MANIFEST_SCHEMA_VERSION, "POLICY_ENGINE_COHORT_SCHEMA_INVALID", "schema")
    _req(policy.get("sampling_mode") == "PREDECLARED_UTC_CONTEXT_ANCHORS", "POLICY_SAMPLING_MODE_INVALID", str(policy.get("sampling_mode")))
    exact = {"slot_alignment_minutes":15,"minimum_slot_spacing_bars":16,"bar_minutes":15,"minimum_plan_slots":10,"preferred_plan_slots":30,"maximum_plan_slots":1000,"earliest_preregistered_horizon_bars":2,"maximum_preregistered_horizon_bars":16}
    for field, expected in exact.items():
        _req(policy.get(field) == expected, "POLICY_INTEGER_INVALID", field)
    for field in ("admission_must_precede_earliest_outcome_completion","admission_requires_exact_context_anchor_match","admission_requires_context_cutoff_not_before_hypothesis_freeze","admission_requires_predeclared_slot","outcome_binding_requires_all_preregistered_horizons_available"):
        _req(policy.get(field) is True, "POLICY_REQUIRED_GUARD_INVALID", field)
    for field in ("admission_may_read_forward_outcomes","outcome_binding_may_select_on_outcome_value","materializer_manual_subset_selection_allowed","missing_slot_silently_dropped","mutable_receipts_allowed","network_fetch_allowed","market_data_fetch_allowed","model_fit_allowed","p_value_generation_allowed","significance_claim_allowed","feature_ranking_allowed","quality_gate_evaluation_allowed","edge_claim_allowed","signal_semantics","paper_trade_execution_allowed","real_capital_allowed","live_alerts_allowed","exchange_execution_allowed","automation_allowed","official_append_allowed"):
        _req(policy.get(field) is False, "POLICY_FORBIDDEN_CAPABILITY_ENABLED", field)
    _req(bool(str(policy.get("preregistered_hypothesis_manifest_path", "")).strip()), "POLICY_HYPOTHESIS_PATH_INVALID", "path")
    _req(_is_sha(policy.get("preregistered_hypothesis_manifest_sha256")), "POLICY_HYPOTHESIS_SHA_INVALID", "sha")
    return {**exact,"policy_effective_from_utc":_utc(effective),"preregistered_hypothesis_frozen_at_utc":_utc(frozen),"preregistered_hypothesis_manifest_path":policy["preregistered_hypothesis_manifest_path"],"preregistered_hypothesis_manifest_sha256":policy["preregistered_hypothesis_manifest_sha256"]}


def load_context_evaluation_prospective_cohort_policy_v1(repo_root: Path | str) -> tuple[dict[str, Any], str]:
    repo = Path(repo_root).resolve()
    path = repo / POLICY_PATH
    value = _read_json(path, "POLICY_FILE_INVALID")
    validate_context_evaluation_prospective_cohort_policy_v1(value)
    return value, _sha(path)


def load_bound_hypothesis_manifest_v1(repo_root: Path | str, *, policy: Mapping[str, Any]) -> tuple[dict[str, Any], str, tuple[int, ...]]:
    repo = Path(repo_root).resolve()
    p = validate_context_evaluation_prospective_cohort_policy_v1(policy)
    path = repo / p["preregistered_hypothesis_manifest_path"]
    _req(path.is_file() and not path.is_symlink(), "HYPOTHESIS_MANIFEST_FILE_INVALID", str(path))
    raw = _read_json(path, "HYPOTHESIS_MANIFEST_FILE_INVALID")
    actual = _canonical_json_sha256(raw)
    _req(actual == p["preregistered_hypothesis_manifest_sha256"], "HYPOTHESIS_MANIFEST_SHA_MISMATCH", actual)
    engine_policy, _ = load_context_evaluation_engine_policy_v1(repo)
    validated = validate_hypothesis_manifest_v1(raw, policy=engine_policy)
    _req(validated["frozen_at_utc"] == p["preregistered_hypothesis_frozen_at_utc"], "HYPOTHESIS_FREEZE_MISMATCH", validated["frozen_at_utc"])
    horizons = tuple(sorted({int(item["horizon_bars"]) for item in validated["hypotheses"]}))
    _req(min(horizons) == p["earliest_preregistered_horizon_bars"], "HYPOTHESIS_EARLIEST_HORIZON_MISMATCH", str(horizons))
    _req(max(horizons) == p["maximum_preregistered_horizon_bars"], "HYPOTHESIS_MAX_HORIZON_MISMATCH", str(horizons))
    return validated, actual, horizons


def validate_prospective_cohort_plan_v1(plan: Mapping[str, Any], *, policy: Mapping[str, Any], hypothesis_manifest: Mapping[str, Any], hypothesis_manifest_sha256: str) -> dict[str, Any]:
    p = validate_context_evaluation_prospective_cohort_policy_v1(policy)
    _req(isinstance(plan, Mapping), "PLAN_INVALID", "mapping required")
    expected_fields = {"schema_version","cohort_id","plan_frozen_at_utc","hypothesis_manifest_sha256","hypothesis_frozen_at_utc","sampling_mode","slots"}
    _req(set(plan) == expected_fields, "PLAN_FIELDS_INVALID", str(sorted(plan)))
    _req(plan.get("schema_version") == PLAN_SCHEMA_VERSION, "PLAN_SCHEMA_INVALID", str(plan.get("schema_version")))
    cohort_id = str(plan.get("cohort_id", "")).strip()
    _req(bool(cohort_id), "PLAN_COHORT_ID_INVALID", cohort_id)
    _req(plan.get("sampling_mode") == "PREDECLARED_UTC_CONTEXT_ANCHORS", "PLAN_SAMPLING_MODE_INVALID", str(plan.get("sampling_mode")))
    _req(plan.get("hypothesis_manifest_sha256") == hypothesis_manifest_sha256, "PLAN_HYPOTHESIS_SHA_MISMATCH", str(plan.get("hypothesis_manifest_sha256")))
    _req(plan.get("hypothesis_frozen_at_utc") == hypothesis_manifest["frozen_at_utc"], "PLAN_HYPOTHESIS_FREEZE_MISMATCH", str(plan.get("hypothesis_frozen_at_utc")))
    plan_frozen = _parse_utc(plan.get("plan_frozen_at_utc"), "plan_frozen_at_utc")
    hypothesis_frozen = _parse_utc(hypothesis_manifest["frozen_at_utc"], "hypothesis_frozen_at_utc")
    _req(plan_frozen >= hypothesis_frozen, "PLAN_FROZEN_BEFORE_HYPOTHESIS_FREEZE", _utc(plan_frozen))
    slots = plan.get("slots")
    _req(isinstance(slots, list), "PLAN_SLOTS_INVALID", "list required")
    _req(p["minimum_plan_slots"] <= len(slots) <= p["maximum_plan_slots"], "PLAN_SLOT_COUNT_INVALID", str(len(slots)))
    normalized=[]; ids=[]; anchors=[]
    for item in slots:
        _req(isinstance(item, Mapping), "PLAN_SLOT_INVALID", str(item))
        _req(set(item) == {"slot_id","context_anchor_open_utc"}, "PLAN_SLOT_FIELDS_INVALID", str(sorted(item)))
        slot_id = str(item.get("slot_id", "")).strip(); _req(bool(slot_id), "PLAN_SLOT_ID_INVALID", slot_id)
        anchor = _parse_utc(item.get("context_anchor_open_utc"), "context_anchor_open_utc")
        _req(anchor.second == 0 and anchor.microsecond == 0 and anchor.minute % p["slot_alignment_minutes"] == 0, "PLAN_SLOT_NOT_15M_ALIGNED", _utc(anchor))
        _req(anchor > plan_frozen, "PLAN_SLOT_NOT_AFTER_PLAN_FREEZE", _utc(anchor))
        ids.append(slot_id); anchors.append(anchor); normalized.append({"slot_id":slot_id,"context_anchor_open_utc":_utc(anchor)})
    _req(len(ids) == len(set(ids)), "PLAN_SLOT_IDS_DUPLICATE", str(ids))
    _req(len(anchors) == len(set(anchors)), "PLAN_SLOT_ANCHORS_DUPLICATE", "anchors")
    _req(anchors == sorted(anchors), "PLAN_SLOT_ANCHORS_NOT_SORTED", "anchors")
    spacing = BAR_DURATION * p["minimum_slot_spacing_bars"]
    for previous, current in zip(anchors, anchors[1:]):
        _req(current - previous >= spacing, "PLAN_SLOT_SPACING_TOO_SHORT", f"{_utc(previous)}->{_utc(current)}")
    return {"schema_version":PLAN_SCHEMA_VERSION,"cohort_id":cohort_id,"plan_frozen_at_utc":_utc(plan_frozen),"hypothesis_manifest_sha256":hypothesis_manifest_sha256,"hypothesis_frozen_at_utc":hypothesis_manifest["frozen_at_utc"],"sampling_mode":"PREDECLARED_UTC_CONTEXT_ANCHORS","slots":normalized}


def validate_admission_candidate_v1(*, pack: Mapping[str, Any], plan: Mapping[str, Any], hypothesis_frozen_at_utc: str, earliest_horizon_bars: int, admitted_at_utc: datetime) -> dict[str, Any]:
    observation_id = str(pack.get("observation_id", "")).strip(); _req(bool(observation_id), "ADMISSION_OBSERVATION_ID_INVALID", observation_id)
    anchor = _parse_utc(pack.get("context_anchor_open_utc"), "context_anchor_open_utc")
    cutoff = _parse_utc(pack.get("context_cutoff_utc"), "context_cutoff_utc")
    frozen = _parse_utc(hypothesis_frozen_at_utc, "hypothesis_frozen_at_utc")
    plan_frozen = _parse_utc(plan["plan_frozen_at_utc"], "plan_frozen_at_utc")
    matches = [slot for slot in plan["slots"] if slot["context_anchor_open_utc"] == _utc(anchor)]
    _req(len(matches) == 1, "ADMISSION_ANCHOR_NOT_PREDECLARED", _utc(anchor))
    _req(cutoff >= frozen, "ADMISSION_CONTEXT_BEFORE_HYPOTHESIS_FREEZE", _utc(cutoff))
    admitted = admitted_at_utc.astimezone(timezone.utc)
    _req(admitted >= plan_frozen, "ADMISSION_BEFORE_PLAN_FREEZE", _utc(admitted))
    _req(admitted >= cutoff, "ADMISSION_BEFORE_CONTEXT_CUTOFF", _utc(admitted))
    deadline = anchor + BAR_DURATION * int(earliest_horizon_bars)
    _req(admitted < deadline, "ADMISSION_AFTER_EARLIEST_OUTCOME_COMPLETION", f"{_utc(admitted)}>={_utc(deadline)}")
    return {"slot_id":matches[0]["slot_id"],"observation_id":observation_id,"context_anchor_open_utc":_utc(anchor),"context_cutoff_utc":_utc(cutoff),"admitted_at_utc":_utc(admitted),"earliest_outcome_completion_utc":_utc(deadline)}


def validate_binding_candidate_v1(*, admission: Mapping[str, Any], descriptor: Mapping[str, Any], outcomes: Mapping[str, Any], required_horizons: Sequence[int]) -> dict[str, Any]:
    _req(descriptor.get("observation_id") == admission["observation_id"], "BINDING_OBSERVATION_ID_MISMATCH", str(descriptor.get("observation_id")))
    synchronized = outcomes.get("synchronized_context_outcome")
    _req(isinstance(synchronized, Mapping), "BINDING_SYNCHRONIZED_OUTCOME_INVALID", "branch")
    _req(synchronized.get("context_available_at_utc") == admission["context_cutoff_utc"], "BINDING_CONTEXT_CUTOFF_MISMATCH", str(synchronized.get("context_available_at_utc")))
    _req(synchronized.get("anchor_open_time_utc") == admission["context_anchor_open_utc"], "BINDING_CONTEXT_ANCHOR_MISMATCH", str(synchronized.get("anchor_open_time_utc")))
    labels = synchronized.get("labels"); _req(isinstance(labels, Mapping), "BINDING_LABELS_INVALID", "labels")
    available=[]
    for horizon in required_horizons:
        label = labels.get(str(horizon)); _req(isinstance(label, Mapping), "BINDING_REQUIRED_HORIZON_MISSING", str(horizon))
        _req(int(label.get("horizon_bars")) == int(horizon), "BINDING_HORIZON_ID_MISMATCH", str(horizon))
        _req(label.get("label_status") == "AVAILABLE", "BINDING_REQUIRED_HORIZON_NOT_AVAILABLE", str(horizon))
        available.append(int(horizon))
    return {"observation_id":admission["observation_id"],"required_horizons_available":available}


def _root_load(repo: Path, root: Path) -> dict[str, Any]:
    _req(root.is_dir() and not root.is_symlink(), "COHORT_ROOT_INVALID", str(root))
    _req(not _inside(root, repo), "COHORT_ROOT_INSIDE_REPOSITORY_PROHIBITED", str(root))
    _validate_manifest(root, ROOT_MANIFEST_FILENAME, (ROOT_BINDING_FILENAME,ROOT_CHECKS_FILENAME,ROOT_PLAN_FILENAME))
    _req((root/"admissions").is_dir() and (root/"bindings").is_dir(), "COHORT_ROOT_SUBDIRECTORY_INVALID", str(root))
    policy, policy_sha = load_context_evaluation_prospective_cohort_policy_v1(repo)
    hyp, hyp_sha, horizons = load_bound_hypothesis_manifest_v1(repo, policy=policy)
    plan = validate_prospective_cohort_plan_v1(_read_json(root/ROOT_PLAN_FILENAME,"COHORT_ROOT_PLAN_INVALID"),policy=policy,hypothesis_manifest=hyp,hypothesis_manifest_sha256=hyp_sha)
    binding = _read_json(root/ROOT_BINDING_FILENAME,"COHORT_ROOT_BINDING_INVALID")
    _req(binding.get("root_schema_version") == ROOT_SCHEMA_VERSION, "COHORT_ROOT_BINDING_SCHEMA_INVALID", "schema")
    _req(binding.get("cohort_id") == plan["cohort_id"], "COHORT_ROOT_BINDING_COHORT_MISMATCH", "cohort")
    _req(binding.get("hypothesis_manifest_sha256") == hyp_sha, "COHORT_ROOT_BINDING_HYPOTHESIS_MISMATCH", "hypothesis")
    _req(tuple(binding.get("preregistered_horizons_bars",())) == horizons, "COHORT_ROOT_BINDING_HORIZONS_MISMATCH", "horizons")
    checks = _read_json(root/ROOT_CHECKS_FILENAME,"COHORT_ROOT_CHECKS_INVALID")
    _req(checks.get("policy_resource_sha256") == policy_sha, "COHORT_ROOT_POLICY_SHA_MISMATCH", "policy")
    return {"policy":policy,"policy_sha256":policy_sha,"hypothesis":hyp,"hypothesis_sha256":hyp_sha,"horizons":horizons,"plan":plan}


def initialize_prospective_cohort_v1(*, repo_root: Path | str, plan_json: Path | str, cohort_root: Path | str, authorization: str | None = None) -> dict[str, Any]:
    _req(authorization == INITIALIZE_AUTHORIZATION, "INITIALIZE_AUTHORIZATION_REQUIRED", "authorization"); _gate_off()
    repo=Path(repo_root).resolve(); plan_path=Path(plan_json).resolve(); root=Path(cohort_root).resolve()
    _req((repo/".git").is_dir(), "REPOSITORY_ROOT_INVALID", str(repo))
    _req(_inside(plan_path, repo), "PLAN_MUST_BE_REPOSITORY_ARTIFACT", str(plan_path))
    _req(plan_path.is_file() and not plan_path.is_symlink(), "PLAN_FILE_INVALID", str(plan_path))
    _req(not _inside(root,repo), "COHORT_ROOT_INSIDE_REPOSITORY_PROHIBITED", str(root))
    _req(root.parent.is_dir() and not root.parent.is_symlink(), "COHORT_ROOT_PARENT_INVALID", str(root.parent))
    _req(not root.exists() and not root.is_symlink(), "COHORT_ROOT_ALREADY_EXISTS", str(root))
    before=_official(repo); policy,policy_sha=load_context_evaluation_prospective_cohort_policy_v1(repo); hyp,hyp_sha,horizons=load_bound_hypothesis_manifest_v1(repo,policy=policy)
    plan=validate_prospective_cohort_plan_v1(_read_json(plan_path,"PLAN_FILE_INVALID"),policy=policy,hypothesis_manifest=hyp,hypothesis_manifest_sha256=hyp_sha)
    temp=root.parent/f".{root.name}.tmp-{uuid.uuid4().hex}"
    try:
        temp.mkdir(); (temp/"admissions").mkdir(); (temp/"bindings").mkdir()
        _write_new(temp/ROOT_PLAN_FILENAME,plan)
        _write_new(temp/ROOT_BINDING_FILENAME,{"root_schema_version":ROOT_SCHEMA_VERSION,"capability":CAPABILITY,"cohort_id":plan["cohort_id"],"hypothesis_manifest_sha256":hyp_sha,"hypothesis_frozen_at_utc":hyp["frozen_at_utc"],"preregistered_horizons_bars":list(horizons),"earliest_preregistered_horizon_bars":min(horizons),"maximum_preregistered_horizon_bars":max(horizons),"plan_sha256":_sha(temp/ROOT_PLAN_FILENAME)})
        _write_new(temp/ROOT_CHECKS_FILENAME,{"root_schema_version":ROOT_SCHEMA_VERSION,"capability":CAPABILITY,"cohort_id":plan["cohort_id"],"policy_resource_sha256":policy_sha,"source_plan_sha256":_sha(plan_path),"canonical_plan_sha256":_sha(temp/ROOT_PLAN_FILENAME),"network_request_executed":False,"market_data_fetched":False,"forward_outcomes_read":False,"quality_gate_evaluated":False,"edge_established":False,"official_append_executed":False})
        _write_manifest(temp,ROOT_MANIFEST_FILENAME,(ROOT_BINDING_FILENAME,ROOT_CHECKS_FILENAME,ROOT_PLAN_FILENAME)); temp.rename(root)
    except Exception:
        if temp.exists(): shutil.rmtree(temp,ignore_errors=True)
        if root.exists(): shutil.rmtree(root,ignore_errors=True)
        raise
    _req(_official(repo)==before,"OFFICIAL_ARTIFACT_CHANGED","initialization"); _root_load(repo,root)
    return {"capability":CAPABILITY,"cohort_id":plan["cohort_id"],"planned_slots":len(plan["slots"]),"preregistered_horizons_bars":list(horizons),"forward_outcomes_read":False,"network_request_executed":False,"market_data_fetched":False,"official_append_executed":False}


def _admission_dir(root: Path, slot_id: str) -> Path: return root/"admissions"/slot_id

def _binding_dir(root: Path, slot_id: str) -> Path: return root/"bindings"/slot_id


def validate_admission_receipt_v1(directory: Path | str) -> dict[str, Any]:
    root=Path(directory).resolve(); _validate_manifest(root,PACKAGE_MANIFEST_FILENAME,(ADMISSION_CHECKS_FILENAME,ADMISSION_RECEIPT_FILENAME))
    receipt=_read_json(root/ADMISSION_RECEIPT_FILENAME,"ADMISSION_RECEIPT_INVALID"); checks=_read_json(root/ADMISSION_CHECKS_FILENAME,"ADMISSION_CHECKS_INVALID")
    _req(receipt.get("schema_version")==ADMISSION_SCHEMA_VERSION,"ADMISSION_SCHEMA_INVALID","schema")
    _req(_is_sha(receipt.get("context_pack_manifest_sha256")),"ADMISSION_CONTEXT_SHA_INVALID","sha")
    for field in ("forward_outcome_package_read","outcome_value_used_for_admission","market_data_fetched","network_request_executed","signal_generated","official_append_executed"):
        _req(checks.get(field) is False,"ADMISSION_CHECK_STATE_INVALID",field)
    return receipt


def prepare_context_admission_v1(*, repo_root: Path | str, cohort_root: Path | str, context_pack_directory: Path | str, authorization: str | None = None) -> dict[str, Any]:
    _req(authorization==ADMISSION_AUTHORIZATION,"ADMISSION_AUTHORIZATION_REQUIRED","authorization"); _gate_off()
    repo=Path(repo_root).resolve(); root=Path(cohort_root).resolve(); context=Path(context_pack_directory).resolve(); loaded=_root_load(repo,root)
    _req(not _inside(context,repo),"CONTEXT_PACKAGE_INSIDE_REPOSITORY_PROHIBITED",str(context)); validate_context_feature_pack_v1_package(context)
    pack=_read_json(context/CONTEXT_PACK_FILENAME,"CONTEXT_PACK_INVALID")
    candidate=validate_admission_candidate_v1(pack=pack,plan=loaded["plan"],hypothesis_frozen_at_utc=loaded["hypothesis"]["frozen_at_utc"],earliest_horizon_bars=min(loaded["horizons"]),admitted_at_utc=_now_utc())
    slot_id=candidate["slot_id"]; target=_admission_dir(root,slot_id); _req(not target.exists() and not target.is_symlink(),"ADMISSION_ALREADY_EXISTS",slot_id); _req(not _binding_dir(root,slot_id).exists(),"BINDING_EXISTS_BEFORE_ADMISSION",slot_id)
    manifest=context/PACKAGE_MANIFEST_FILENAME; _req(manifest.is_file() and not manifest.is_symlink(),"CONTEXT_PACKAGE_MANIFEST_INVALID",str(manifest)); before=_official(repo)
    temp=target.parent/f".{slot_id}.tmp-{uuid.uuid4().hex}"
    try:
        temp.mkdir(); receipt={"schema_version":ADMISSION_SCHEMA_VERSION,"capability":CAPABILITY,"cohort_id":loaded["plan"]["cohort_id"],**candidate,"context_pack_directory":str(context),"context_pack_manifest_sha256":_sha(manifest),"hypothesis_manifest_sha256":loaded["hypothesis_sha256"],"hypothesis_frozen_at_utc":loaded["hypothesis"]["frozen_at_utc"],"plan_sha256":_sha(root/ROOT_PLAN_FILENAME)}
        _write_new(temp/ADMISSION_RECEIPT_FILENAME,receipt); _write_new(temp/ADMISSION_CHECKS_FILENAME,{"schema_version":ADMISSION_SCHEMA_VERSION,"capability":CAPABILITY,"slot_predeclared":True,"context_anchor_exact_match":True,"context_cutoff_not_before_hypothesis_freeze":True,"admission_before_earliest_outcome_completion":True,"forward_outcome_package_read":False,"outcome_value_used_for_admission":False,"market_data_fetched":False,"network_request_executed":False,"signal_generated":False,"official_append_executed":False}); _write_manifest(temp,PACKAGE_MANIFEST_FILENAME,(ADMISSION_CHECKS_FILENAME,ADMISSION_RECEIPT_FILENAME)); validate_admission_receipt_v1(temp); temp.rename(target)
    except Exception:
        if temp.exists(): shutil.rmtree(temp,ignore_errors=True)
        if target.exists(): shutil.rmtree(target,ignore_errors=True)
        raise
    _req(_official(repo)==before,"OFFICIAL_ARTIFACT_CHANGED","admission")
    return {"capability":CAPABILITY,"cohort_id":loaded["plan"]["cohort_id"],"slot_id":slot_id,"observation_id":candidate["observation_id"],"admission_directory":str(target),"admitted_at_utc":candidate["admitted_at_utc"],"earliest_outcome_completion_utc":candidate["earliest_outcome_completion_utc"],"forward_outcome_package_read":False,"outcome_value_used_for_admission":False,"network_request_executed":False,"official_append_executed":False}


def validate_outcome_binding_receipt_v1(directory: Path | str) -> dict[str, Any]:
    root=Path(directory).resolve(); _validate_manifest(root,PACKAGE_MANIFEST_FILENAME,(BINDING_CHECKS_FILENAME,BINDING_RECEIPT_FILENAME)); receipt=_read_json(root/BINDING_RECEIPT_FILENAME,"BINDING_RECEIPT_INVALID"); checks=_read_json(root/BINDING_CHECKS_FILENAME,"BINDING_CHECKS_INVALID")
    _req(receipt.get("schema_version")==BINDING_SCHEMA_VERSION,"BINDING_SCHEMA_INVALID","schema"); _req(_is_sha(receipt.get("outcome_package_manifest_sha256")),"BINDING_OUTCOME_SHA_INVALID","sha"); _req("forward_return" not in receipt,"BINDING_OUTCOME_VALUE_PRESENT","forward_return")
    for field in ("outcome_value_copied_to_receipt","outcome_value_used_for_binding_selection","feature_ranking_performed","quality_gate_evaluated","edge_established","signal_generated","network_request_executed","official_append_executed"):
        _req(checks.get(field) is False,"BINDING_CHECK_STATE_INVALID",field)
    return receipt


def prepare_outcome_binding_v1(*, repo_root: Path | str, cohort_root: Path | str, slot_id: str, outcome_package_directory: Path | str, authorization: str | None = None) -> dict[str, Any]:
    _req(authorization==BINDING_AUTHORIZATION,"BINDING_AUTHORIZATION_REQUIRED","authorization"); _gate_off()
    repo=Path(repo_root).resolve(); root=Path(cohort_root).resolve(); outcome=Path(outcome_package_directory).resolve(); loaded=_root_load(repo,root); slot_id=str(slot_id).strip(); _req(slot_id in {s["slot_id"] for s in loaded["plan"]["slots"]},"BINDING_SLOT_NOT_PREDECLARED",slot_id)
    admission_dir=_admission_dir(root,slot_id); target=_binding_dir(root,slot_id); _req(admission_dir.is_dir() and not admission_dir.is_symlink(),"BINDING_ADMISSION_MISSING",slot_id); _req(not target.exists() and not target.is_symlink(),"BINDING_ALREADY_EXISTS",slot_id); admission=validate_admission_receipt_v1(admission_dir)
    _req(not _inside(outcome,repo),"OUTCOME_PACKAGE_INSIDE_REPOSITORY_PROHIBITED",str(outcome)); validate_forward_outcome_label_package(outcome)
    descriptor=_read_json(outcome/OUTCOME_DESCRIPTOR_FILENAME,"OUTCOME_DESCRIPTOR_INVALID"); outcomes=_read_json(outcome/OUTCOME_FILENAME,"OUTCOME_PACKAGE_INVALID"); maturity=validate_binding_candidate_v1(admission=admission,descriptor=descriptor,outcomes=outcomes,required_horizons=loaded["horizons"])
    manifest=outcome/PACKAGE_MANIFEST_FILENAME; _req(manifest.is_file() and not manifest.is_symlink(),"OUTCOME_PACKAGE_MANIFEST_INVALID",str(manifest)); before=_official(repo); temp=target.parent/f".{slot_id}.tmp-{uuid.uuid4().hex}"
    try:
        temp.mkdir(); receipt={"schema_version":BINDING_SCHEMA_VERSION,"capability":CAPABILITY,"cohort_id":loaded["plan"]["cohort_id"],"slot_id":slot_id,"observation_id":admission["observation_id"],"context_anchor_open_utc":admission["context_anchor_open_utc"],"context_cutoff_utc":admission["context_cutoff_utc"],"admission_manifest_sha256":_sha(admission_dir/PACKAGE_MANIFEST_FILENAME),"outcome_package_directory":str(outcome),"outcome_package_manifest_sha256":_sha(manifest),"required_horizons_available":maturity["required_horizons_available"],"bound_at_utc":_utc(_now_utc())}
        _write_new(temp/BINDING_RECEIPT_FILENAME,receipt); _write_new(temp/BINDING_CHECKS_FILENAME,{"schema_version":BINDING_SCHEMA_VERSION,"capability":CAPABILITY,"observation_id_exact_match":True,"context_cutoff_exact_match":True,"context_anchor_exact_match":True,"all_preregistered_horizons_available":True,"outcome_value_copied_to_receipt":False,"outcome_value_used_for_binding_selection":False,"feature_ranking_performed":False,"quality_gate_evaluated":False,"edge_established":False,"signal_generated":False,"network_request_executed":False,"official_append_executed":False}); _write_manifest(temp,PACKAGE_MANIFEST_FILENAME,(BINDING_CHECKS_FILENAME,BINDING_RECEIPT_FILENAME)); validate_outcome_binding_receipt_v1(temp); temp.rename(target)
    except Exception:
        if temp.exists(): shutil.rmtree(temp,ignore_errors=True)
        if target.exists(): shutil.rmtree(target,ignore_errors=True)
        raise
    _req(_official(repo)==before,"OFFICIAL_ARTIFACT_CHANGED","binding")
    return {"capability":CAPABILITY,"cohort_id":loaded["plan"]["cohort_id"],"slot_id":slot_id,"observation_id":admission["observation_id"],"binding_directory":str(target),"required_horizons_available":maturity["required_horizons_available"],"outcome_value_copied_to_receipt":False,"outcome_value_used_for_binding_selection":False,"network_request_executed":False,"official_append_executed":False}


def materialize_engine_cohort_manifest_v1(*, repo_root: Path | str, cohort_root: Path | str, output_directory: Path | str, authorization: str | None = None) -> dict[str, Any]:
    _req(authorization==MATERIALIZE_AUTHORIZATION,"MATERIALIZE_AUTHORIZATION_REQUIRED","authorization"); _gate_off()
    repo=Path(repo_root).resolve(); root=Path(cohort_root).resolve(); output=Path(output_directory).resolve(); loaded=_root_load(repo,root)
    _req(not _inside(output,repo),"MATERIALIZE_OUTPUT_INSIDE_REPOSITORY_PROHIBITED",str(output)); _req(output.parent.is_dir() and not output.parent.is_symlink(),"MATERIALIZE_OUTPUT_PARENT_INVALID",str(output.parent)); _req(not output.exists() and not output.is_symlink(),"MATERIALIZE_OUTPUT_ALREADY_EXISTS",str(output))
    entries=[]; audit=[]; seen=set()
    for slot in loaded["plan"]["slots"]:
        sid=slot["slot_id"]; adir=_admission_dir(root,sid); bdir=_binding_dir(root,sid)
        if not adir.exists(): audit.append({"slot_id":sid,"context_anchor_open_utc":slot["context_anchor_open_utc"],"status":"SLOT_NOT_ADMITTED","observation_id":None}); continue
        admission=validate_admission_receipt_v1(adir); _req(admission["context_anchor_open_utc"]==slot["context_anchor_open_utc"],"MATERIALIZE_ADMISSION_ANCHOR_MISMATCH",sid)
        cdir=Path(admission["context_pack_directory"]).resolve(); validate_context_feature_pack_v1_package(cdir); _req(_sha(cdir/PACKAGE_MANIFEST_FILENAME)==admission["context_pack_manifest_sha256"],"MATERIALIZE_CONTEXT_PACKAGE_CHANGED",sid)
        if not bdir.exists(): audit.append({"slot_id":sid,"context_anchor_open_utc":slot["context_anchor_open_utc"],"status":"ADMITTED_OUTCOME_NOT_BOUND","observation_id":admission["observation_id"]}); continue
        binding=validate_outcome_binding_receipt_v1(bdir); _req(binding["observation_id"]==admission["observation_id"],"MATERIALIZE_BINDING_OBSERVATION_MISMATCH",sid)
        odir=Path(binding["outcome_package_directory"]).resolve(); validate_forward_outcome_label_package(odir); _req(_sha(odir/PACKAGE_MANIFEST_FILENAME)==binding["outcome_package_manifest_sha256"],"MATERIALIZE_OUTCOME_PACKAGE_CHANGED",sid)
        oid=admission["observation_id"]; _req(oid not in seen,"MATERIALIZE_OBSERVATION_ID_DUPLICATE",oid); seen.add(oid)
        entries.append({"observation_id":oid,"context_pack_directory":admission["context_pack_directory"],"context_pack_manifest_sha256":admission["context_pack_manifest_sha256"],"outcome_package_directory":binding["outcome_package_directory"],"outcome_package_manifest_sha256":binding["outcome_package_manifest_sha256"]}); audit.append({"slot_id":sid,"context_anchor_open_utc":slot["context_anchor_open_utc"],"status":"BOUND_READY_FOR_ENGINE","observation_id":oid})
    _req(entries,"MATERIALIZE_NO_BOUND_ENTRIES","no entries"); entries.sort(key=lambda x:x["observation_id"]); cohort={"schema_version":COHORT_MANIFEST_SCHEMA_VERSION,"cohort_id":loaded["plan"]["cohort_id"],"entries":entries}; engine_policy,_=load_context_evaluation_engine_policy_v1(repo); validate_cohort_manifest_v1(cohort,policy=engine_policy)
    counts={status:sum(1 for item in audit if item["status"]==status) for status in ("BOUND_READY_FOR_ENGINE","ADMITTED_OUTCOME_NOT_BOUND","SLOT_NOT_ADMITTED")}
    audit_obj={"schema_version":MATERIALIZATION_SCHEMA_VERSION,"capability":CAPABILITY,"cohort_id":loaded["plan"]["cohort_id"],"planned_slot_count":len(loaded["plan"]["slots"]),"engine_entry_count":len(entries),"status_counts":counts,"slots":audit,"all_bound_admissions_included":True,"manual_subset_selection_performed":False,"outcome_values_used_for_subset_selection":False}
    checks={"schema_version":MATERIALIZATION_SCHEMA_VERSION,"capability":CAPABILITY,"plan_driven_materialization":True,"all_bound_admissions_included":True,"manual_subset_selection_performed":False,"outcome_values_used_for_subset_selection":False,"network_request_executed":False,"market_data_fetched":False,"model_fit_performed":False,"p_values_generated":False,"significance_assigned":False,"feature_ranking_performed":False,"quality_gate_evaluated":False,"edge_established":False,"signal_generated":False,"official_append_executed":False}
    before=_official(repo); temp=output.parent/f".{output.name}.tmp-{uuid.uuid4().hex}"
    try:
        temp.mkdir(); _write_new(temp/MATERIALIZED_COHORT_FILENAME,cohort); _write_new(temp/MATERIALIZED_AUDIT_FILENAME,audit_obj); _write_new(temp/MATERIALIZED_CHECKS_FILENAME,checks); _write_manifest(temp,PACKAGE_MANIFEST_FILENAME,(MATERIALIZED_AUDIT_FILENAME,MATERIALIZED_CHECKS_FILENAME,MATERIALIZED_COHORT_FILENAME)); temp.rename(output)
    except Exception:
        if temp.exists(): shutil.rmtree(temp,ignore_errors=True)
        if output.exists(): shutil.rmtree(output,ignore_errors=True)
        raise
    _req(_official(repo)==before,"OFFICIAL_ARTIFACT_CHANGED","materialization")
    return {"capability":CAPABILITY,"cohort_id":loaded["plan"]["cohort_id"],"output_directory":str(output),"planned_slot_count":len(loaded["plan"]["slots"]),"engine_entry_count":len(entries),"status_counts":counts,"all_bound_admissions_included":True,"manual_subset_selection_performed":False,"outcome_values_used_for_subset_selection":False,"network_request_executed":False,"quality_gate_evaluated":False,"edge_established":False,"official_append_executed":False}


__all__ = [
    "ADMISSION_AUTHORIZATION","ADMISSION_SCHEMA_VERSION","BINDING_AUTHORIZATION","BINDING_SCHEMA_VERSION","CAPABILITY","IMPLEMENTATION_OR_REPAIR_ATTEMPT","INITIALIZE_AUTHORIZATION","MATERIALIZE_AUTHORIZATION","MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS","MATERIALIZATION_SCHEMA_VERSION","PLAN_SCHEMA_VERSION","POLICY_SCHEMA_VERSION","ROOT_SCHEMA_VERSION","ContextEvaluationProspectiveCohortError","initialize_prospective_cohort_v1","load_bound_hypothesis_manifest_v1","load_context_evaluation_prospective_cohort_policy_v1","materialize_engine_cohort_manifest_v1","prepare_context_admission_v1","prepare_outcome_binding_v1","validate_admission_candidate_v1","validate_admission_receipt_v1","validate_binding_candidate_v1","validate_context_evaluation_prospective_cohort_policy_v1","validate_outcome_binding_receipt_v1","validate_prospective_cohort_plan_v1",
]
