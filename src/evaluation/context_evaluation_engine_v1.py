from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import statistics
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.context.context_feature_pack_v1_level_a_standard import (
    FEATURE_IDS,
    PACK_SCHEMA_VERSION,
    validate_context_feature_pack_v1_package,
)
from src.long_side.forward_outcome_labeler_v1 import (
    FORWARD_HORIZONS_BARS,
    OUTCOME_SCHEMA_VERSION,
    validate_forward_outcome_label_package,
)

CAPABILITY = "CONTEXT_EVALUATION_ENGINE_V1"
ENGINE_SCHEMA_VERSION = "CONTEXT_EVALUATION_ENGINE_V1_SCHEMA_V1"
PACKAGE_SCHEMA_VERSION = "CONTEXT_EVALUATION_ENGINE_V1_PACKAGE_V1"
POLICY_SCHEMA_VERSION = "CONTEXT_EVALUATION_ENGINE_POLICY_V1"
HYPOTHESIS_MANIFEST_SCHEMA_VERSION = (
    "CONTEXT_EVALUATION_HYPOTHESIS_MANIFEST_V1"
)
COHORT_MANIFEST_SCHEMA_VERSION = "CONTEXT_EVALUATION_COHORT_MANIFEST_V1"
PACKAGE_AUTHORIZATION = "PREPARE_CONTEXT_EVALUATION_ENGINE_V1"

MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS = 10
IMPLEMENTATION_OR_REPAIR_ATTEMPT = 1

POLICY_PATH = Path(
    "src/evaluation/resources/context_evaluation_engine_policy_v1.json"
)

RESULTS_FILENAME = "evaluation_results.json"
AUDIT_FILENAME = "evaluation_audit.json"
CHECKS_FILENAME = "evaluation_checks.json"
MANIFEST_FILENAME = "manifest.sha256"

CONTEXT_PACK_FILENAME = "context_feature_pack.json"
OUTCOME_FILENAME = "forward_outcomes.json"
OUTCOME_DESCRIPTOR_FILENAME = "observation_descriptor.json"

OFFICIAL_APPEND_GATE_NAME = "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
OFFICIAL_DATASET = Path("data/forward/long_forward_observation_dataset_v1.csv")
OFFICIAL_MANIFEST = Path(
    "data/forward/long_forward_observation_dataset_v1.manifest.csv"
)
OFFICIAL_LOCK = Path("data/forward/long_forward_observation_dataset_v1.lock")

BAR_DURATION = timedelta(minutes=15)
SUPPORTED_PREDICTOR_TYPES = ("BINARY", "CATEGORICAL", "CONTINUOUS")
ALLOWED_TRANSFORM = "IDENTITY"
OUTCOME_BRANCH = "synchronized_context_outcome"
OUTCOME_FIELD = "forward_return"

FALSE_PERMISSION_FIELDS = (
    "quality_gate_evaluated",
    "edge_established",
    "feature_promotion_allowed",
    "feature_ranking_performed",
    "best_hypothesis_selected",
    "p_values_generated",
    "significance_assigned",
    "multiple_testing_winner_selected",
    "threshold_search_performed",
    "predictor_transform_search_performed",
    "model_fit_performed",
    "hyperparameter_search_performed",
    "direction_inferred",
    "signal_generated",
    "live_alerts_allowed",
    "paper_trade_execution_allowed",
    "real_capital_allowed",
    "exchange_execution_allowed",
    "automation_allowed",
    "official_append_executed",
)


class ContextEvaluationEngineError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def _req(ok: bool, code: str, message: str) -> None:
    if not ok:
        raise ContextEvaluationEngineError(code, message)


def _parse_utc(value: Any, field: str) -> datetime:
    try:
        dt = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContextEvaluationEngineError("TIMESTAMP_INVALID", field) from exc
    _req(dt.tzinfo is not None, "TIMESTAMP_TIMEZONE_REQUIRED", field)
    return dt.astimezone(timezone.utc)


def _utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _valid_sha(value: Any) -> bool:
    text = str(value)
    return len(text) == 64 and all(c in "0123456789abcdef" for c in text)


def _read_json_mapping(path: Path, code: str) -> dict[str, Any]:
    _req(path.is_file() and not path.is_symlink(), code, str(path))
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContextEvaluationEngineError(code, str(path)) from exc
    _req(isinstance(value, Mapping), code, str(path))
    return dict(value)


def _write_json_new(path: Path, value: Any) -> None:
    payload = (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
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
    _req(
        os.environ.get(OFFICIAL_APPEND_GATE_NAME) != "1",
        "OFFICIAL_APPEND_GATE_ENABLED",
        OFFICIAL_APPEND_GATE_NAME,
    )


def _official(repo: Path) -> dict[str, str]:
    dataset = repo / OFFICIAL_DATASET
    manifest = repo / OFFICIAL_MANIFEST
    lock = repo / OFFICIAL_LOCK

    _req(
        dataset.is_file() and not dataset.is_symlink(),
        "OFFICIAL_DATASET_INVALID",
        str(dataset),
    )
    _req(
        manifest.is_file() and not manifest.is_symlink(),
        "OFFICIAL_MANIFEST_INVALID",
        str(manifest),
    )
    _req(
        not lock.exists() and not lock.is_symlink(),
        "OFFICIAL_LOCK_PRESENT",
        str(lock),
    )
    return {
        "dataset_sha256": _sha(dataset),
        "manifest_sha256": _sha(manifest),
    }


def validate_context_evaluation_engine_policy_v1(
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    _req(isinstance(policy, Mapping), "POLICY_INVALID", "mapping required")
    _req(
        policy.get("schema_version") == POLICY_SCHEMA_VERSION,
        "POLICY_SCHEMA_INVALID",
        str(policy.get("schema_version")),
    )
    _req(
        policy.get("capability") == CAPABILITY,
        "POLICY_CAPABILITY_INVALID",
        str(policy.get("capability")),
    )
    _req(
        policy.get("expected_pack_schema_version") == PACK_SCHEMA_VERSION,
        "POLICY_PACK_SCHEMA_INVALID",
        str(policy.get("expected_pack_schema_version")),
    )
    _req(
        policy.get("expected_outcome_schema_version") == OUTCOME_SCHEMA_VERSION,
        "POLICY_OUTCOME_SCHEMA_INVALID",
        str(policy.get("expected_outcome_schema_version")),
    )
    _req(
        policy.get("hypothesis_manifest_schema_version")
        == HYPOTHESIS_MANIFEST_SCHEMA_VERSION,
        "POLICY_HYPOTHESIS_SCHEMA_INVALID",
        str(policy.get("hypothesis_manifest_schema_version")),
    )
    _req(
        policy.get("cohort_manifest_schema_version")
        == COHORT_MANIFEST_SCHEMA_VERSION,
        "POLICY_COHORT_SCHEMA_INVALID",
        str(policy.get("cohort_manifest_schema_version")),
    )

    effective = _parse_utc(
        policy.get("policy_effective_from_utc"),
        "policy_effective_from_utc",
    )

    _req(
        tuple(policy.get("supported_horizons_bars", ()))
        == tuple(FORWARD_HORIZONS_BARS),
        "POLICY_HORIZONS_INVALID",
        str(policy.get("supported_horizons_bars")),
    )
    _req(
        policy.get("outcome_branch") == OUTCOME_BRANCH,
        "POLICY_OUTCOME_BRANCH_INVALID",
        str(policy.get("outcome_branch")),
    )
    _req(
        policy.get("outcome_field") == OUTCOME_FIELD,
        "POLICY_OUTCOME_FIELD_INVALID",
        str(policy.get("outcome_field")),
    )
    _req(
        tuple(policy.get("predictor_types", ()))
        == SUPPORTED_PREDICTOR_TYPES,
        "POLICY_PREDICTOR_TYPES_INVALID",
        str(policy.get("predictor_types")),
    )
    _req(
        policy.get("allowed_transform") == ALLOWED_TRANSFORM,
        "POLICY_TRANSFORM_INVALID",
        str(policy.get("allowed_transform")),
    )

    integer_exact = {
        "min_hypotheses": 1,
        "max_hypotheses": 32,
        "min_cohort_entries": 1,
        "max_cohort_entries": 10000,
        "min_non_overlapping_observations": 10,
        "preferred_non_overlapping_observations": 30,
        "min_binary_group_observations": 5,
        "min_categorical_group_observations": 5,
        "max_categorical_levels": 8,
    }
    for field, expected in integer_exact.items():
        _req(
            policy.get(field) == expected,
            "POLICY_INTEGER_INVALID",
            field,
        )

    required_true = (
        "hypothesis_freeze_not_before_policy_required",
        "observation_not_before_hypothesis_freeze_required",
        "point_in_time_feature_required",
        "context_anchor_exact_match_required",
        "context_cutoff_exact_match_required",
        "non_overlapping_outcome_windows_required",
    )
    for field in required_true:
        _req(
            policy.get(field) is True,
            "POLICY_REQUIRED_GUARD_INVALID",
            field,
        )

    required_false = (
        "missing_feature_imputation_allowed",
        "late_feature_as_zero_allowed",
        "threshold_search_allowed",
        "predictor_transform_search_allowed",
        "model_fit_allowed",
        "hyperparameter_search_allowed",
        "p_value_generation_allowed",
        "significance_claim_allowed",
        "multiple_testing_winner_selection_allowed",
        "feature_ranking_allowed",
        "edge_claim_allowed",
        "feature_promotion_allowed",
        "quality_gate_evaluation_allowed",
        "directional_semantics",
        "signal_semantics",
        "paper_trade_execution_allowed",
        "real_capital_allowed",
        "live_alerts_allowed",
        "exchange_execution_allowed",
        "automation_allowed",
        "official_append_allowed",
    )
    for field in required_false:
        _req(
            policy.get(field) is False,
            "POLICY_FORBIDDEN_CAPABILITY_ENABLED",
            field,
        )

    return {
        "policy_effective_from_utc": _utc(effective),
        "supported_horizons_bars": tuple(FORWARD_HORIZONS_BARS),
        **integer_exact,
    }


def load_context_evaluation_engine_policy_v1(
    repo_root: Path | str,
) -> tuple[dict[str, Any], str]:
    repo = Path(repo_root).resolve()
    path = repo / POLICY_PATH
    policy = _read_json_mapping(path, "POLICY_FILE_INVALID")
    validate_context_evaluation_engine_policy_v1(policy)
    return policy, _sha(path)


def validate_hypothesis_manifest_v1(
    manifest: Mapping[str, Any],
    *,
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    _req(
        isinstance(manifest, Mapping),
        "HYPOTHESIS_MANIFEST_INVALID",
        "mapping required",
    )
    _req(
        set(manifest)
        == {"schema_version", "manifest_id", "frozen_at_utc", "hypotheses"},
        "HYPOTHESIS_MANIFEST_FIELDS_INVALID",
        str(sorted(manifest)),
    )
    _req(
        manifest.get("schema_version") == HYPOTHESIS_MANIFEST_SCHEMA_VERSION,
        "HYPOTHESIS_MANIFEST_SCHEMA_INVALID",
        str(manifest.get("schema_version")),
    )
    manifest_id = str(manifest.get("manifest_id", "")).strip()
    _req(bool(manifest_id), "HYPOTHESIS_MANIFEST_ID_INVALID", manifest_id)

    frozen_at = _parse_utc(
        manifest.get("frozen_at_utc"),
        "hypothesis_manifest.frozen_at_utc",
    )
    policy_effective = _parse_utc(
        policy["policy_effective_from_utc"],
        "policy_effective_from_utc",
    )
    _req(
        frozen_at >= policy_effective,
        "HYPOTHESIS_FROZEN_BEFORE_ENGINE_POLICY",
        _utc(frozen_at),
    )

    hypotheses = manifest.get("hypotheses")
    _req(
        isinstance(hypotheses, list),
        "HYPOTHESES_INVALID",
        "list required",
    )
    _req(
        policy["min_hypotheses"]
        <= len(hypotheses)
        <= policy["max_hypotheses"],
        "HYPOTHESIS_COUNT_INVALID",
        str(len(hypotheses)),
    )

    normalized = []
    ids = []
    fingerprints = []

    required_fields = {
        "hypothesis_id",
        "feature_id",
        "payload_path",
        "predictor_type",
        "horizon_bars",
        "outcome_field",
        "transform",
    }

    for item in hypotheses:
        _req(
            isinstance(item, Mapping),
            "HYPOTHESIS_INVALID",
            str(item),
        )
        _req(
            set(item) == required_fields,
            "HYPOTHESIS_FIELDS_INVALID",
            str(sorted(item)),
        )

        hypothesis_id = str(item.get("hypothesis_id", "")).strip()
        feature_id = str(item.get("feature_id", "")).strip()
        predictor_type = str(item.get("predictor_type", "")).strip()
        transform = str(item.get("transform", "")).strip()
        outcome_field = str(item.get("outcome_field", "")).strip()

        _req(bool(hypothesis_id), "HYPOTHESIS_ID_INVALID", hypothesis_id)
        _req(feature_id in FEATURE_IDS, "HYPOTHESIS_FEATURE_ID_INVALID", feature_id)
        _req(
            predictor_type in SUPPORTED_PREDICTOR_TYPES,
            "HYPOTHESIS_PREDICTOR_TYPE_INVALID",
            predictor_type,
        )
        _req(
            transform == ALLOWED_TRANSFORM,
            "HYPOTHESIS_TRANSFORM_INVALID",
            transform,
        )
        _req(
            outcome_field == OUTCOME_FIELD,
            "HYPOTHESIS_OUTCOME_FIELD_INVALID",
            outcome_field,
        )

        try:
            horizon = int(item.get("horizon_bars"))
        except (TypeError, ValueError) as exc:
            raise ContextEvaluationEngineError(
                "HYPOTHESIS_HORIZON_INVALID",
                str(item.get("horizon_bars")),
            ) from exc

        _req(
            horizon in FORWARD_HORIZONS_BARS,
            "HYPOTHESIS_HORIZON_INVALID",
            str(horizon),
        )

        payload_path = item.get("payload_path")
        _req(
            isinstance(payload_path, list)
            and 1 <= len(payload_path) <= 8,
            "HYPOTHESIS_PAYLOAD_PATH_INVALID",
            str(payload_path),
        )
        normalized_path = []
        for key in payload_path:
            _req(
                isinstance(key, str)
                and bool(key.strip())
                and len(key) <= 128,
                "HYPOTHESIS_PAYLOAD_KEY_INVALID",
                str(key),
            )
            normalized_path.append(key)

        ids.append(hypothesis_id)
        fingerprints.append(
            (
                feature_id,
                tuple(normalized_path),
                predictor_type,
                horizon,
                outcome_field,
                transform,
            )
        )
        normalized.append(
            {
                "hypothesis_id": hypothesis_id,
                "feature_id": feature_id,
                "payload_path": normalized_path,
                "predictor_type": predictor_type,
                "horizon_bars": horizon,
                "outcome_field": outcome_field,
                "transform": transform,
            }
        )

    _req(len(ids) == len(set(ids)), "HYPOTHESIS_IDS_DUPLICATE", str(ids))
    _req(ids == sorted(ids), "HYPOTHESIS_IDS_NOT_SORTED", str(ids))
    _req(
        len(fingerprints) == len(set(fingerprints)),
        "HYPOTHESIS_DEFINITIONS_DUPLICATE",
        str(fingerprints),
    )

    return {
        "schema_version": HYPOTHESIS_MANIFEST_SCHEMA_VERSION,
        "manifest_id": manifest_id,
        "frozen_at_utc": _utc(frozen_at),
        "hypotheses": normalized,
    }


def validate_cohort_manifest_v1(
    manifest: Mapping[str, Any],
    *,
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    _req(
        isinstance(manifest, Mapping),
        "COHORT_MANIFEST_INVALID",
        "mapping required",
    )
    _req(
        set(manifest) == {"schema_version", "cohort_id", "entries"},
        "COHORT_MANIFEST_FIELDS_INVALID",
        str(sorted(manifest)),
    )
    _req(
        manifest.get("schema_version") == COHORT_MANIFEST_SCHEMA_VERSION,
        "COHORT_MANIFEST_SCHEMA_INVALID",
        str(manifest.get("schema_version")),
    )

    cohort_id = str(manifest.get("cohort_id", "")).strip()
    _req(bool(cohort_id), "COHORT_ID_INVALID", cohort_id)

    entries = manifest.get("entries")
    _req(isinstance(entries, list), "COHORT_ENTRIES_INVALID", "list required")
    _req(
        policy["min_cohort_entries"]
        <= len(entries)
        <= policy["max_cohort_entries"],
        "COHORT_ENTRY_COUNT_INVALID",
        str(len(entries)),
    )

    required = {
        "observation_id",
        "context_pack_directory",
        "context_pack_manifest_sha256",
        "outcome_package_directory",
        "outcome_package_manifest_sha256",
    }
    normalized = []
    ids = []
    context_dirs = []
    outcome_dirs = []

    for item in entries:
        _req(isinstance(item, Mapping), "COHORT_ENTRY_INVALID", str(item))
        _req(
            set(item) == required,
            "COHORT_ENTRY_FIELDS_INVALID",
            str(sorted(item)),
        )

        observation_id = str(item.get("observation_id", "")).strip()
        context_dir = str(item.get("context_pack_directory", "")).strip()
        outcome_dir = str(item.get("outcome_package_directory", "")).strip()
        context_sha = str(item.get("context_pack_manifest_sha256", ""))
        outcome_sha = str(item.get("outcome_package_manifest_sha256", ""))

        _req(bool(observation_id), "COHORT_OBSERVATION_ID_INVALID", observation_id)
        _req(bool(context_dir), "COHORT_CONTEXT_DIRECTORY_INVALID", context_dir)
        _req(bool(outcome_dir), "COHORT_OUTCOME_DIRECTORY_INVALID", outcome_dir)
        _req(_valid_sha(context_sha), "COHORT_CONTEXT_MANIFEST_SHA_INVALID", context_sha)
        _req(_valid_sha(outcome_sha), "COHORT_OUTCOME_MANIFEST_SHA_INVALID", outcome_sha)

        ids.append(observation_id)
        context_dirs.append(context_dir)
        outcome_dirs.append(outcome_dir)

        normalized.append(
            {
                "observation_id": observation_id,
                "context_pack_directory": context_dir,
                "context_pack_manifest_sha256": context_sha,
                "outcome_package_directory": outcome_dir,
                "outcome_package_manifest_sha256": outcome_sha,
            }
        )

    _req(len(ids) == len(set(ids)), "COHORT_OBSERVATION_IDS_DUPLICATE", str(ids))
    _req(ids == sorted(ids), "COHORT_OBSERVATION_IDS_NOT_SORTED", str(ids))
    _req(
        len(context_dirs) == len(set(context_dirs)),
        "COHORT_CONTEXT_DIRECTORIES_DUPLICATE",
        str(context_dirs),
    )
    _req(
        len(outcome_dirs) == len(set(outcome_dirs)),
        "COHORT_OUTCOME_DIRECTORIES_DUPLICATE",
        str(outcome_dirs),
    )

    return {
        "schema_version": COHORT_MANIFEST_SCHEMA_VERSION,
        "cohort_id": cohort_id,
        "entries": normalized,
    }


def _resolve_payload_path(
    payload: Mapping[str, Any],
    path: Sequence[str],
) -> Any:
    current: Any = payload
    for key in path:
        _req(
            isinstance(current, Mapping),
            "PAYLOAD_PATH_TRAVERSES_NON_MAPPING",
            ".".join(path),
        )
        _req(
            key in current,
            "PAYLOAD_PATH_KEY_MISSING",
            ".".join(path),
        )
        current = current[key]
    return current


def _normalize_predictor(value: Any, predictor_type: str) -> Any:
    if predictor_type == "CONTINUOUS":
        _req(
            not isinstance(value, bool),
            "CONTINUOUS_PREDICTOR_BOOLEAN_INVALID",
            str(value),
        )
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ContextEvaluationEngineError(
                "CONTINUOUS_PREDICTOR_INVALID",
                str(value),
            ) from exc
        _req(
            math.isfinite(number),
            "CONTINUOUS_PREDICTOR_INVALID",
            str(value),
        )
        return number

    if predictor_type == "BINARY":
        _req(
            isinstance(value, bool),
            "BINARY_PREDICTOR_INVALID",
            str(value),
        )
        return bool(value)

    if predictor_type == "CATEGORICAL":
        _req(
            isinstance(value, str)
            and bool(value.strip())
            and len(value) <= 128,
            "CATEGORICAL_PREDICTOR_INVALID",
            str(value),
        )
        return value

    raise ContextEvaluationEngineError(
        "PREDICTOR_TYPE_INVALID",
        predictor_type,
    )


def _find_feature(
    pack: Mapping[str, Any],
    feature_id: str,
) -> Mapping[str, Any]:
    features = pack.get("features")
    _req(isinstance(features, list), "PACK_FEATURES_INVALID", feature_id)
    matches = [
        item
        for item in features
        if isinstance(item, Mapping)
        and item.get("feature_id") == feature_id
    ]
    _req(
        len(matches) == 1,
        "PACK_FEATURE_NOT_UNIQUE",
        feature_id,
    )
    return matches[0]


def _load_cohort_entry(
    entry: Mapping[str, Any],
) -> dict[str, Any]:
    context_dir = Path(entry["context_pack_directory"]).resolve()
    outcome_dir = Path(entry["outcome_package_directory"]).resolve()

    validate_context_feature_pack_v1_package(context_dir)
    validate_forward_outcome_label_package(outcome_dir)

    context_manifest = context_dir / MANIFEST_FILENAME
    outcome_manifest = outcome_dir / MANIFEST_FILENAME

    _req(
        _sha(context_manifest)
        == entry["context_pack_manifest_sha256"],
        "COHORT_CONTEXT_MANIFEST_HASH_MISMATCH",
        entry["observation_id"],
    )
    _req(
        _sha(outcome_manifest)
        == entry["outcome_package_manifest_sha256"],
        "COHORT_OUTCOME_MANIFEST_HASH_MISMATCH",
        entry["observation_id"],
    )

    pack = _read_json_mapping(
        context_dir / CONTEXT_PACK_FILENAME,
        "CONTEXT_PACK_FILE_INVALID",
    )
    outcomes = _read_json_mapping(
        outcome_dir / OUTCOME_FILENAME,
        "OUTCOME_FILE_INVALID",
    )
    descriptor = _read_json_mapping(
        outcome_dir / OUTCOME_DESCRIPTOR_FILENAME,
        "OUTCOME_DESCRIPTOR_FILE_INVALID",
    )

    observation_id = str(entry["observation_id"])
    _req(
        pack.get("observation_id") == observation_id,
        "PACK_OBSERVATION_ID_MISMATCH",
        observation_id,
    )
    _req(
        outcomes.get("observation_id") == observation_id,
        "OUTCOME_OBSERVATION_ID_MISMATCH",
        observation_id,
    )
    _req(
        descriptor.get("observation_id") == observation_id,
        "DESCRIPTOR_OBSERVATION_ID_MISMATCH",
        observation_id,
    )

    synchronized = outcomes.get(OUTCOME_BRANCH)
    _req(
        isinstance(synchronized, Mapping),
        "SYNCHRONIZED_OUTCOME_BRANCH_INVALID",
        observation_id,
    )

    pack_cutoff = _parse_utc(
        pack.get("context_cutoff_utc"),
        "pack.context_cutoff_utc",
    )
    outcome_cutoff = _parse_utc(
        synchronized.get("context_available_at_utc"),
        "outcome.context_available_at_utc",
    )
    descriptor_cutoff = _parse_utc(
        descriptor.get("synchronized_context_available_at_utc"),
        "descriptor.synchronized_context_available_at_utc",
    )
    _req(
        pack_cutoff == outcome_cutoff == descriptor_cutoff,
        "CONTEXT_CUTOFF_MISMATCH",
        observation_id,
    )

    pack_anchor = _parse_utc(
        pack.get("context_anchor_open_utc"),
        "pack.context_anchor_open_utc",
    )
    outcome_anchor = _parse_utc(
        synchronized.get("anchor_open_time_utc"),
        "outcome.anchor_open_time_utc",
    )
    _req(
        pack_anchor == outcome_anchor,
        "CONTEXT_ANCHOR_MISMATCH",
        observation_id,
    )

    _req(
        tuple(outcomes.get("forward_horizons_bars", ()))
        == tuple(FORWARD_HORIZONS_BARS),
        "OUTCOME_HORIZONS_MISMATCH",
        observation_id,
    )

    return {
        "observation_id": observation_id,
        "pack": pack,
        "outcomes": outcomes,
        "descriptor": descriptor,
        "context_cutoff_utc": _utc(pack_cutoff),
        "context_anchor_open_utc": _utc(pack_anchor),
        "context_package_manifest_sha256": entry[
            "context_pack_manifest_sha256"
        ],
        "outcome_package_manifest_sha256": entry[
            "outcome_package_manifest_sha256"
        ],
    }


def _extract_record(
    *,
    loaded: Mapping[str, Any],
    hypothesis: Mapping[str, Any],
    frozen_at_utc: str,
) -> dict[str, Any]:
    observation_id = str(loaded["observation_id"])
    feature_id = str(hypothesis["feature_id"])
    horizon = int(hypothesis["horizon_bars"])
    anchor = _parse_utc(
        loaded["context_anchor_open_utc"],
        "context_anchor_open_utc",
    )
    cutoff = _parse_utc(
        loaded["context_cutoff_utc"],
        "context_cutoff_utc",
    )
    frozen_at = _parse_utc(frozen_at_utc, "frozen_at_utc")

    base = {
        "observation_id": observation_id,
        "hypothesis_id": hypothesis["hypothesis_id"],
        "feature_id": feature_id,
        "horizon_bars": horizon,
        "context_cutoff_utc": _utc(cutoff),
        "context_anchor_open_utc": _utc(anchor),
        "post_hypothesis_freeze": cutoff >= frozen_at,
        "feature_status": None,
        "point_in_time_eligible": False,
        "outcome_status": None,
        "inclusion_status": "EXCLUDED",
        "exclusion_reason": None,
        "predictor_value": None,
        "outcome_value": None,
        "used_for_effect_estimate": False,
    }

    if cutoff < frozen_at:
        base["exclusion_reason"] = "OBSERVATION_PRE_HYPOTHESIS_FREEZE"
        return base

    feature = _find_feature(loaded["pack"], feature_id)
    base["feature_status"] = feature.get("status")
    base["point_in_time_eligible"] = bool(
        feature.get("point_in_time_eligible")
    )

    if feature.get("status") != "AVAILABLE":
        base["exclusion_reason"] = "FEATURE_NOT_AVAILABLE"
        return base

    if feature.get("point_in_time_eligible") is not True:
        base["exclusion_reason"] = "FEATURE_NOT_POINT_IN_TIME_ELIGIBLE"
        return base

    payload = feature.get("payload")
    _req(
        isinstance(payload, Mapping),
        "ELIGIBLE_FEATURE_PAYLOAD_INVALID",
        feature_id,
    )

    raw_predictor = _resolve_payload_path(
        payload,
        hypothesis["payload_path"],
    )
    predictor = _normalize_predictor(
        raw_predictor,
        hypothesis["predictor_type"],
    )

    synchronized = loaded["outcomes"][OUTCOME_BRANCH]
    labels = synchronized.get("labels")
    _req(
        isinstance(labels, Mapping),
        "SYNCHRONIZED_LABELS_INVALID",
        observation_id,
    )
    label = labels.get(str(horizon))
    _req(
        isinstance(label, Mapping),
        "HORIZON_LABEL_MISSING",
        f"{observation_id}:{horizon}",
    )
    _req(
        int(label.get("horizon_bars")) == horizon,
        "HORIZON_LABEL_ID_MISMATCH",
        f"{observation_id}:{horizon}",
    )

    base["outcome_status"] = label.get("label_status")

    if label.get("label_status") != "AVAILABLE":
        base["exclusion_reason"] = "OUTCOME_NOT_AVAILABLE"
        return base

    try:
        outcome = float(label.get(OUTCOME_FIELD))
    except (TypeError, ValueError) as exc:
        raise ContextEvaluationEngineError(
            "OUTCOME_VALUE_INVALID",
            f"{observation_id}:{horizon}",
        ) from exc
    _req(
        math.isfinite(outcome),
        "OUTCOME_VALUE_INVALID",
        f"{observation_id}:{horizon}",
    )

    base["predictor_value"] = predictor
    base["outcome_value"] = outcome
    base["inclusion_status"] = "USABLE_BEFORE_OVERLAP_PURGE"
    base["exclusion_reason"] = None
    return base


def _purge_overlapping_windows(
    records: Sequence[Mapping[str, Any]],
    *,
    horizon_bars: int,
) -> tuple[list[dict[str, Any]], set[str]]:
    ordered = sorted(
        (dict(item) for item in records),
        key=lambda item: (
            item["context_anchor_open_utc"],
            item["observation_id"],
        ),
    )
    selected: list[dict[str, Any]] = []
    purged_ids: set[str] = set()
    previous_window_end: datetime | None = None
    window = BAR_DURATION * int(horizon_bars)

    for item in ordered:
        anchor = _parse_utc(
            item["context_anchor_open_utc"],
            "context_anchor_open_utc",
        )
        if previous_window_end is None or anchor >= previous_window_end:
            item["used_for_effect_estimate"] = True
            item["inclusion_status"] = "USED_NON_OVERLAPPING"
            selected.append(item)
            previous_window_end = anchor + window
        else:
            purged_ids.add(str(item["observation_id"]))

    return selected, purged_ids


def _mean(values: Sequence[float]) -> float:
    return float(statistics.fmean(values))


def _median(values: Sequence[float]) -> float:
    return float(statistics.median(values))


def _average_ranks(values: Sequence[float]) -> list[float]:
    indexed = sorted(
        enumerate(values),
        key=lambda pair: (pair[1], pair[0]),
    )
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        average_rank = ((i + 1) + j) / 2.0
        for k in range(i, j):
            ranks[indexed[k][0]] = average_rank
        i = j
    return ranks


def _pearson(
    x: Sequence[float],
    y: Sequence[float],
) -> float | None:
    _req(len(x) == len(y), "CORRELATION_LENGTH_MISMATCH", "x/y")
    if len(x) < 2:
        return None
    mx = _mean(x)
    my = _mean(y)
    dx = [value - mx for value in x]
    dy = [value - my for value in y]
    denom_x = math.sqrt(sum(value * value for value in dx))
    denom_y = math.sqrt(sum(value * value for value in dy))
    if denom_x == 0 or denom_y == 0:
        return None
    return float(
        sum(a * b for a, b in zip(dx, dy)) / (denom_x * denom_y)
    )


def _spearman(
    x: Sequence[float],
    y: Sequence[float],
) -> float | None:
    if len(x) < 2:
        return None
    return _pearson(_average_ranks(x), _average_ranks(y))


def _split_halves(
    records: Sequence[Mapping[str, Any]],
) -> tuple[list[Mapping[str, Any]], list[Mapping[str, Any]]]:
    midpoint = len(records) // 2
    return list(records[:midpoint]), list(records[midpoint:])


def _continuous_effect(
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    x = [float(item["predictor_value"]) for item in records]
    y = [float(item["outcome_value"]) for item in records]
    first, second = _split_halves(records)

    first_rho = (
        _spearman(
            [float(item["predictor_value"]) for item in first],
            [float(item["outcome_value"]) for item in first],
        )
        if len(first) >= 2
        else None
    )
    second_rho = (
        _spearman(
            [float(item["predictor_value"]) for item in second],
            [float(item["outcome_value"]) for item in second],
        )
        if len(second) >= 2
        else None
    )

    return {
        "effect_metric": "SPEARMAN_RHO",
        "effect_value": _spearman(x, y),
        "predictor_mean": _mean(x),
        "predictor_median": _median(x),
        "forward_return_mean": _mean(y),
        "forward_return_median": _median(y),
        "first_half_effect_value": first_rho,
        "second_half_effect_value": second_rho,
    }


def _binary_effect(
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    false_values = [
        float(item["outcome_value"])
        for item in records
        if item["predictor_value"] is False
    ]
    true_values = [
        float(item["outcome_value"])
        for item in records
        if item["predictor_value"] is True
    ]

    first, second = _split_halves(records)

    def half_diff(rows: Sequence[Mapping[str, Any]]) -> float | None:
        f = [
            float(item["outcome_value"])
            for item in rows
            if item["predictor_value"] is False
        ]
        t = [
            float(item["outcome_value"])
            for item in rows
            if item["predictor_value"] is True
        ]
        if not f or not t:
            return None
        return _mean(t) - _mean(f)

    return {
        "effect_metric": "MEAN_FORWARD_RETURN_DIFFERENCE_TRUE_MINUS_FALSE",
        "effect_value": (
            _mean(true_values) - _mean(false_values)
            if false_values and true_values
            else None
        ),
        "false_count": len(false_values),
        "true_count": len(true_values),
        "false_forward_return_mean": (
            _mean(false_values) if false_values else None
        ),
        "true_forward_return_mean": (
            _mean(true_values) if true_values else None
        ),
        "false_forward_return_median": (
            _median(false_values) if false_values else None
        ),
        "true_forward_return_median": (
            _median(true_values) if true_values else None
        ),
        "first_half_effect_value": half_diff(first),
        "second_half_effect_value": half_diff(second),
    }


def _categorical_effect(
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    grouped: dict[str, list[float]] = {}
    for item in records:
        key = str(item["predictor_value"])
        grouped.setdefault(key, []).append(float(item["outcome_value"]))

    levels = []
    for key in sorted(grouped):
        values = grouped[key]
        levels.append(
            {
                "level": key,
                "count": len(values),
                "forward_return_mean": _mean(values),
                "forward_return_median": _median(values),
            }
        )

    return {
        "effect_metric": "CATEGORICAL_GROUP_SUMMARY_ONLY",
        "effect_value": None,
        "categorical_level_count": len(levels),
        "levels": levels,
        "first_half_effect_value": None,
        "second_half_effect_value": None,
    }


def evaluate_context_cohort_v1(
    *,
    loaded_observations: Sequence[Mapping[str, Any]],
    hypothesis_manifest: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    p = validate_context_evaluation_engine_policy_v1(policy)
    hypotheses = validate_hypothesis_manifest_v1(
        hypothesis_manifest,
        policy={**policy, **p},
    )
    frozen_at = hypotheses["frozen_at_utc"]

    loaded_ids = [str(item["observation_id"]) for item in loaded_observations]
    _req(
        len(loaded_ids) == len(set(loaded_ids)),
        "LOADED_OBSERVATION_IDS_DUPLICATE",
        str(loaded_ids),
    )

    results = []
    audit_rows = []

    for hypothesis in hypotheses["hypotheses"]:
        raw_rows = [
            _extract_record(
                loaded=item,
                hypothesis=hypothesis,
                frozen_at_utc=frozen_at,
            )
            for item in loaded_observations
        ]
        usable_before_purge = [
            item
            for item in raw_rows
            if item["inclusion_status"] == "USABLE_BEFORE_OVERLAP_PURGE"
        ]
        selected, purged_ids = _purge_overlapping_windows(
            usable_before_purge,
            horizon_bars=hypothesis["horizon_bars"],
        )
        selected_by_id = {
            str(item["observation_id"]): item
            for item in selected
        }

        for row in raw_rows:
            oid = str(row["observation_id"])
            if oid in selected_by_id:
                row = selected_by_id[oid]
            elif oid in purged_ids:
                row["inclusion_status"] = "EXCLUDED"
                row["exclusion_reason"] = "OVERLAPPING_FORWARD_WINDOW"
                row["used_for_effect_estimate"] = False
            audit_rows.append(row)

        n_raw = len(loaded_observations)
        n_usable = len(usable_before_purge)
        n_selected = len(selected)
        predictor_type = hypothesis["predictor_type"]

        result = {
            "hypothesis_id": hypothesis["hypothesis_id"],
            "feature_id": hypothesis["feature_id"],
            "payload_path": list(hypothesis["payload_path"]),
            "predictor_type": predictor_type,
            "horizon_bars": int(hypothesis["horizon_bars"]),
            "outcome_branch": OUTCOME_BRANCH,
            "outcome_field": OUTCOME_FIELD,
            "transform": ALLOWED_TRANSFORM,
            "cohort_observations": n_raw,
            "usable_before_overlap_purge": n_usable,
            "non_overlapping_observations": n_selected,
            "coverage_ratio_before_overlap_purge": (
                n_usable / n_raw if n_raw else 0.0
            ),
            "minimum_non_overlapping_sample_reached": (
                n_selected >= p["min_non_overlapping_observations"]
            ),
            "preferred_non_overlapping_sample_reached": (
                n_selected >= p["preferred_non_overlapping_observations"]
            ),
            "analysis_status": None,
            "effect": None,
            "p_value": None,
            "significance_assigned": False,
            "edge_claim": False,
            "feature_promotion_allowed": False,
        }

        if n_selected < p["min_non_overlapping_observations"]:
            result["analysis_status"] = (
                "INSUFFICIENT_NON_OVERLAPPING_SAMPLE"
            )
            results.append(result)
            continue

        if predictor_type == "CONTINUOUS":
            effect = _continuous_effect(selected)
            if effect["effect_value"] is None:
                result["analysis_status"] = "DEGENERATE_CONTINUOUS_SERIES"
            else:
                result["analysis_status"] = "DESCRIPTIVE_ESTIMATE_AVAILABLE"
            result["effect"] = effect

        elif predictor_type == "BINARY":
            effect = _binary_effect(selected)
            result["effect"] = effect
            if (
                effect["false_count"]
                < p["min_binary_group_observations"]
                or effect["true_count"]
                < p["min_binary_group_observations"]
            ):
                result["analysis_status"] = (
                    "INSUFFICIENT_BINARY_GROUP_SAMPLE"
                )
            else:
                result["analysis_status"] = (
                    "DESCRIPTIVE_ESTIMATE_AVAILABLE"
                )

        else:
            effect = _categorical_effect(selected)
            result["effect"] = effect
            levels = effect["levels"]
            if len(levels) > p["max_categorical_levels"]:
                result["analysis_status"] = "TOO_MANY_CATEGORICAL_LEVELS"
            elif any(
                item["count"]
                < p["min_categorical_group_observations"]
                for item in levels
            ):
                result["analysis_status"] = (
                    "INSUFFICIENT_CATEGORICAL_GROUP_SAMPLE"
                )
            else:
                result["analysis_status"] = (
                    "DESCRIPTIVE_ESTIMATE_AVAILABLE"
                )

        results.append(result)

    results.sort(key=lambda item: item["hypothesis_id"])
    audit_rows.sort(
        key=lambda item: (
            item["hypothesis_id"],
            item["context_anchor_open_utc"],
            item["observation_id"],
        )
    )

    available_estimates = sum(
        1
        for item in results
        if item["analysis_status"] == "DESCRIPTIVE_ESTIMATE_AVAILABLE"
    )

    summary = {
        "engine_schema_version": ENGINE_SCHEMA_VERSION,
        "capability": CAPABILITY,
        "hypothesis_manifest_id": hypotheses["manifest_id"],
        "hypothesis_manifest_frozen_at_utc": hypotheses["frozen_at_utc"],
        "hypothesis_count": len(results),
        "cohort_observation_count": len(loaded_observations),
        "descriptive_estimates_available": available_estimates,
        "evaluation_decision": "DESCRIPTIVE_ONLY_NO_EDGE_CLAIM",
        "results": results,
        **{field: False for field in FALSE_PERMISSION_FIELDS},
    }

    audit = {
        "audit_schema_version": "CONTEXT_EVALUATION_ENGINE_V1_AUDIT_V1",
        "capability": CAPABILITY,
        "hypothesis_manifest_id": hypotheses["manifest_id"],
        "row_count": len(audit_rows),
        "rows": audit_rows,
        "missing_feature_imputation_performed": False,
        "late_feature_as_zero_performed": False,
        "primary_rule_outcome_used": False,
        "synchronized_context_outcome_only": True,
        "overlap_purge_performed": True,
        "old_pre_freeze_observation_promoted": False,
    }

    validate_context_evaluation_results_v1(summary)
    validate_context_evaluation_audit_v1(audit)

    return summary, audit


def validate_context_evaluation_results_v1(
    results: Mapping[str, Any],
) -> dict[str, Any]:
    _req(isinstance(results, Mapping), "RESULTS_INVALID", "mapping required")
    _req(
        results.get("engine_schema_version") == ENGINE_SCHEMA_VERSION,
        "RESULTS_SCHEMA_INVALID",
        str(results.get("engine_schema_version")),
    )
    _req(
        results.get("capability") == CAPABILITY,
        "RESULTS_CAPABILITY_INVALID",
        str(results.get("capability")),
    )
    _req(
        results.get("evaluation_decision")
        == "DESCRIPTIVE_ONLY_NO_EDGE_CLAIM",
        "RESULTS_DECISION_INVALID",
        str(results.get("evaluation_decision")),
    )
    rows = results.get("results")
    _req(isinstance(rows, list), "RESULT_ROWS_INVALID", "list required")
    _req(
        int(results.get("hypothesis_count", -1)) == len(rows),
        "RESULT_HYPOTHESIS_COUNT_INVALID",
        str(results.get("hypothesis_count")),
    )

    ids = []
    for item in rows:
        _req(isinstance(item, Mapping), "RESULT_ROW_INVALID", str(item))
        ids.append(str(item.get("hypothesis_id", "")))
        _req(
            item.get("outcome_branch") == OUTCOME_BRANCH,
            "RESULT_OUTCOME_BRANCH_INVALID",
            str(item.get("outcome_branch")),
        )
        _req(
            item.get("outcome_field") == OUTCOME_FIELD,
            "RESULT_OUTCOME_FIELD_INVALID",
            str(item.get("outcome_field")),
        )
        _req(
            item.get("transform") == ALLOWED_TRANSFORM,
            "RESULT_TRANSFORM_INVALID",
            str(item.get("transform")),
        )
        _req(
            item.get("p_value") is None,
            "RESULT_P_VALUE_PRESENT",
            str(item.get("p_value")),
        )
        _req(
            item.get("significance_assigned") is False,
            "RESULT_SIGNIFICANCE_INVALID",
            str(item.get("hypothesis_id")),
        )
        _req(
            item.get("edge_claim") is False
            and item.get("feature_promotion_allowed") is False,
            "RESULT_EDGE_OR_PROMOTION_INVALID",
            str(item.get("hypothesis_id")),
        )

    _req(ids == sorted(ids), "RESULT_HYPOTHESIS_ORDER_INVALID", str(ids))
    _req(len(ids) == len(set(ids)), "RESULT_HYPOTHESIS_IDS_DUPLICATE", str(ids))

    for field in FALSE_PERMISSION_FIELDS:
        _req(
            results.get(field) is False,
            "RESULT_PERMISSION_INVALID",
            field,
        )

    return {
        "hypothesis_count": len(rows),
        "descriptive_estimates_available": int(
            results["descriptive_estimates_available"]
        ),
        "evaluation_decision": results["evaluation_decision"],
    }


def validate_context_evaluation_audit_v1(
    audit: Mapping[str, Any],
) -> dict[str, Any]:
    _req(isinstance(audit, Mapping), "AUDIT_INVALID", "mapping required")
    _req(
        audit.get("audit_schema_version")
        == "CONTEXT_EVALUATION_ENGINE_V1_AUDIT_V1",
        "AUDIT_SCHEMA_INVALID",
        str(audit.get("audit_schema_version")),
    )
    _req(
        audit.get("capability") == CAPABILITY,
        "AUDIT_CAPABILITY_INVALID",
        str(audit.get("capability")),
    )
    rows = audit.get("rows")
    _req(isinstance(rows, list), "AUDIT_ROWS_INVALID", "list required")
    _req(
        int(audit.get("row_count", -1)) == len(rows),
        "AUDIT_ROW_COUNT_INVALID",
        str(audit.get("row_count")),
    )

    _req(
        audit.get("missing_feature_imputation_performed") is False,
        "AUDIT_IMPUTATION_INVALID",
        "missing feature",
    )
    _req(
        audit.get("late_feature_as_zero_performed") is False,
        "AUDIT_LATE_ZERO_INVALID",
        "late feature",
    )
    _req(
        audit.get("primary_rule_outcome_used") is False,
        "AUDIT_PRIMARY_OUTCOME_INVALID",
        "primary outcome",
    )
    _req(
        audit.get("synchronized_context_outcome_only") is True,
        "AUDIT_CONTEXT_OUTCOME_INVALID",
        "context outcome",
    )
    _req(
        audit.get("overlap_purge_performed") is True,
        "AUDIT_OVERLAP_PURGE_INVALID",
        "overlap",
    )
    _req(
        audit.get("old_pre_freeze_observation_promoted") is False,
        "AUDIT_RETROSPECTIVE_PROMOTION_INVALID",
        "pre-freeze",
    )

    return {"row_count": len(rows)}


def _write_manifest(directory: Path) -> None:
    names = (AUDIT_FILENAME, CHECKS_FILENAME, RESULTS_FILENAME)
    lines = [
        f"{_sha(directory / name)}  {name}"
        for name in sorted(names)
    ]
    path = directory / MANIFEST_FILENAME
    with path.open("xb") as handle:
        handle.write(("\n".join(lines) + "\n").encode("utf-8"))


def _validate_manifest(directory: Path) -> int:
    path = directory / MANIFEST_FILENAME
    _req(
        path.is_file() and not path.is_symlink(),
        "PACKAGE_MANIFEST_MISSING",
        str(path),
    )
    lines = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    _req(
        len(lines) == 3,
        "PACKAGE_MANIFEST_ENTRY_COUNT_INVALID",
        str(len(lines)),
    )
    expected_names = {AUDIT_FILENAME, CHECKS_FILENAME, RESULTS_FILENAME}
    seen = set()
    for line in lines:
        parts = line.split("  ", 1)
        _req(
            len(parts) == 2 and len(parts[0]) == 64,
            "PACKAGE_MANIFEST_LINE_INVALID",
            line,
        )
        digest, name = parts
        _req(
            name in expected_names,
            "PACKAGE_MANIFEST_SCOPE_INVALID",
            name,
        )
        target = directory / name
        _req(
            target.is_file() and not target.is_symlink(),
            "PACKAGE_MANIFEST_PAYLOAD_MISSING",
            name,
        )
        _req(
            _sha(target) == digest,
            "PACKAGE_MANIFEST_HASH_MISMATCH",
            name,
        )
        seen.add(name)
    _req(
        seen == expected_names,
        "PACKAGE_MANIFEST_SCOPE_INVALID",
        str(sorted(seen)),
    )
    return len(lines)


def validate_context_evaluation_engine_v1_package(
    directory: Path | str,
) -> dict[str, Any]:
    root = Path(directory).resolve()
    _req(
        root.is_dir() and not root.is_symlink(),
        "PACKAGE_DIRECTORY_INVALID",
        str(root),
    )
    entries = _validate_manifest(root)
    results = _read_json_mapping(
        root / RESULTS_FILENAME,
        "PACKAGE_RESULTS_INVALID",
    )
    audit = _read_json_mapping(
        root / AUDIT_FILENAME,
        "PACKAGE_AUDIT_INVALID",
    )
    checks = _read_json_mapping(
        root / CHECKS_FILENAME,
        "PACKAGE_CHECKS_INVALID",
    )

    results_validation = validate_context_evaluation_results_v1(results)
    audit_validation = validate_context_evaluation_audit_v1(audit)

    _req(
        checks.get("package_schema_version") == PACKAGE_SCHEMA_VERSION,
        "PACKAGE_SCHEMA_INVALID",
        str(checks.get("package_schema_version")),
    )
    _req(
        checks.get("capability") == CAPABILITY,
        "PACKAGE_CAPABILITY_INVALID",
        str(checks.get("capability")),
    )

    false_checks = (
        "real_network_request_executed",
        "git_network_request_executed",
        "market_data_fetched",
        "model_fit_performed",
        "p_values_generated",
        "significance_assigned",
        "feature_ranking_performed",
        "quality_gate_evaluated",
        "edge_established",
        "signal_generated",
        "official_append_executed",
        "official_dataset_changed",
        "official_manifest_changed",
    )
    for field in false_checks:
        _req(
            checks.get(field) is False,
            "PACKAGE_CHECK_INVALID",
            field,
        )

    return {
        **results_validation,
        **audit_validation,
        "manifest_entries": entries,
    }


def prepare_context_evaluation_engine_v1_package(
    *,
    repo_root: Path | str,
    hypothesis_manifest_json: Path | str,
    cohort_manifest_json: Path | str,
    output_directory: Path | str,
    authorization: str | None = None,
) -> dict[str, Any]:
    _req(
        authorization == PACKAGE_AUTHORIZATION,
        "PACKAGE_AUTHORIZATION_REQUIRED",
        "authorization",
    )
    _gate_off()

    repo = Path(repo_root).resolve()
    hypothesis_path = Path(hypothesis_manifest_json).resolve()
    cohort_path = Path(cohort_manifest_json).resolve()
    output = Path(output_directory).resolve()

    _req((repo / ".git").is_dir(), "REPOSITORY_ROOT_INVALID", str(repo))
    _req(
        not _inside(output, repo),
        "OUTPUT_INSIDE_REPOSITORY_PROHIBITED",
        str(output),
    )
    _req(
        output.parent.is_dir() and not output.parent.is_symlink(),
        "OUTPUT_PARENT_INVALID",
        str(output.parent),
    )
    _req(
        not output.exists() and not output.is_symlink(),
        "OUTPUT_ALREADY_EXISTS",
        str(output),
    )
    _req(
        not _inside(hypothesis_path, repo),
        "HYPOTHESIS_MANIFEST_INSIDE_REPOSITORY_PROHIBITED",
        str(hypothesis_path),
    )
    _req(
        not _inside(cohort_path, repo),
        "COHORT_MANIFEST_INSIDE_REPOSITORY_PROHIBITED",
        str(cohort_path),
    )

    official_before = _official(repo)
    policy, policy_sha = load_context_evaluation_engine_policy_v1(repo)
    p = validate_context_evaluation_engine_policy_v1(policy)

    hypothesis_raw = _read_json_mapping(
        hypothesis_path,
        "HYPOTHESIS_MANIFEST_FILE_INVALID",
    )
    cohort_raw = _read_json_mapping(
        cohort_path,
        "COHORT_MANIFEST_FILE_INVALID",
    )
    hypothesis = validate_hypothesis_manifest_v1(
        hypothesis_raw,
        policy={**policy, **p},
    )
    cohort = validate_cohort_manifest_v1(
        cohort_raw,
        policy={**policy, **p},
    )

    loaded = []
    for entry in cohort["entries"]:
        context_dir = Path(entry["context_pack_directory"]).resolve()
        outcome_dir = Path(entry["outcome_package_directory"]).resolve()
        _req(
            not _inside(context_dir, repo),
            "CONTEXT_PACKAGE_INSIDE_REPOSITORY_PROHIBITED",
            str(context_dir),
        )
        _req(
            not _inside(outcome_dir, repo),
            "OUTCOME_PACKAGE_INSIDE_REPOSITORY_PROHIBITED",
            str(outcome_dir),
        )
        loaded.append(_load_cohort_entry(entry))

    results, audit = evaluate_context_cohort_v1(
        loaded_observations=loaded,
        hypothesis_manifest=hypothesis,
        policy={**policy, **p},
    )

    _req(
        _official(repo) == official_before,
        "OFFICIAL_ARTIFACT_CHANGED",
        "before output",
    )
    _gate_off()

    temp = output.parent / f".{output.name}.tmp-{uuid.uuid4().hex}"
    _req(
        not temp.exists(),
        "TEMPORARY_OUTPUT_COLLISION",
        str(temp),
    )

    try:
        temp.mkdir()
        _write_json_new(temp / RESULTS_FILENAME, results)
        _write_json_new(temp / AUDIT_FILENAME, audit)

        checks = {
            "package_schema_version": PACKAGE_SCHEMA_VERSION,
            "capability": CAPABILITY,
            "policy_resource_sha256": policy_sha,
            "hypothesis_manifest_sha256": _sha(hypothesis_path),
            "cohort_manifest_sha256": _sha(cohort_path),
            "hypothesis_manifest_id": hypothesis["manifest_id"],
            "cohort_id": cohort["cohort_id"],
            "cohort_entry_count": len(cohort["entries"]),
            "hypothesis_count": len(hypothesis["hypotheses"]),
            "outcome_branch": OUTCOME_BRANCH,
            "outcome_field": OUTCOME_FIELD,
            "non_overlapping_outcome_windows_required": True,
            "real_network_request_executed": False,
            "git_network_request_executed": False,
            "market_data_fetched": False,
            "model_fit_performed": False,
            "p_values_generated": False,
            "significance_assigned": False,
            "feature_ranking_performed": False,
            "quality_gate_evaluated": False,
            "edge_established": False,
            "signal_generated": False,
            "official_append_executed": False,
            "official_dataset_changed": False,
            "official_manifest_changed": False,
        }
        _write_json_new(temp / CHECKS_FILENAME, checks)
        _write_manifest(temp)
        validate_context_evaluation_engine_v1_package(temp)
        temp.rename(output)
    except Exception:
        if temp.exists():
            shutil.rmtree(temp, ignore_errors=True)
        if output.exists():
            shutil.rmtree(output, ignore_errors=True)
        raise

    _req(
        _official(repo) == official_before,
        "OFFICIAL_ARTIFACT_CHANGED",
        "after output",
    )
    _gate_off()

    validation = validate_context_evaluation_engine_v1_package(output)

    return {
        "capability": CAPABILITY,
        "output_directory": str(output),
        "hypothesis_count": validation["hypothesis_count"],
        "descriptive_estimates_available": validation[
            "descriptive_estimates_available"
        ],
        "evaluation_decision": validation["evaluation_decision"],
        "real_network_request_executed": False,
        "market_data_fetched": False,
        "model_fit_performed": False,
        "p_values_generated": False,
        "significance_assigned": False,
        "feature_ranking_performed": False,
        "quality_gate_evaluated": False,
        "edge_established": False,
        "signal_generated": False,
        "official_append_executed": False,
    }


__all__ = [
    "ALLOWED_TRANSFORM",
    "BAR_DURATION",
    "CAPABILITY",
    "COHORT_MANIFEST_SCHEMA_VERSION",
    "ENGINE_SCHEMA_VERSION",
    "HYPOTHESIS_MANIFEST_SCHEMA_VERSION",
    "IMPLEMENTATION_OR_REPAIR_ATTEMPT",
    "MAX_IMPLEMENTATION_OR_REPAIR_ATTEMPTS",
    "OUTCOME_BRANCH",
    "OUTCOME_FIELD",
    "PACKAGE_AUTHORIZATION",
    "PACKAGE_SCHEMA_VERSION",
    "SUPPORTED_PREDICTOR_TYPES",
    "ContextEvaluationEngineError",
    "evaluate_context_cohort_v1",
    "load_context_evaluation_engine_policy_v1",
    "prepare_context_evaluation_engine_v1_package",
    "validate_cohort_manifest_v1",
    "validate_context_evaluation_audit_v1",
    "validate_context_evaluation_engine_policy_v1",
    "validate_context_evaluation_engine_v1_package",
    "validate_context_evaluation_results_v1",
    "validate_hypothesis_manifest_v1",
]
