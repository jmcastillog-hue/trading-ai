from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

CAPABILITY = "CONTEXT_EVALUATION_DAILY_EVENING_RUNNER_V3"
COHORT_ID = "CONTEXT_LEVEL_A_DAILY_EVENING_30_V3"
PLAN_RELATIVE = Path(
    "research/context_evaluation/context_evaluation_daily_evening_30_plan_v3.json"
)
EXPECTED_PLAN_SHA256 = (
    "dd53f019ce1f8a52c65a3a3e879a8b56017d0944182aa135303e00b7bc776f6f"
)
EXPECTED_HYPOTHESIS_SHA256 = (
    "4de33a61d2a1456e6bd673ddd044cd0c01bb3369d30595ec57773df1d922442b"
)
EXPECTED_OFFICIAL_DATASET_SHA256 = (
    "e3fa86a461fd46f4d66dc2e03f185e49b7b3438d3cbc33340c01f51310514ff1"
)
EXPECTED_OFFICIAL_MANIFEST_SHA256 = (
    "99fc1f3f0e57bc11ec79c2c08481450a1bda1d7eaf8b84e85962fd25c3d4806e"
)
OFFICIAL_APPEND_GATE = "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
SOURCE_ATTESTATION = "REAL_MARKET_DATA_SOURCE_HUMAN_ATTESTED_NOT_SYNTHETIC"

CONTEXT_TEMPLATE_RELATIVE = Path(
    "research/context_evaluation/reference_runners/context_slot_reference_s008_v1_1.py"
)
OUTCOME_TEMPLATE_RELATIVE = Path(
    "research/context_evaluation/reference_runners/outcome_binding_reference_s008_v1.py"
)
CONTEXT_TEMPLATE_SHA256 = (
    "e97718c5256abd777f0c23395c7df43fe48dceffac1bac20ac50f7675dcc0dac"
)
OUTCOME_TEMPLATE_SHA256 = (
    "3e997bd9197666b26acdcffec269925fbbe1c2b61665f5966a4cf573a9fc7eec"
)

OLD_HEAD = "beefd785be607db17f2faa910674a8fb6268f00b"
OLD_PLAN_SHA256 = (
    "b38d27f8a5eeec320e7b35c11b9c22ab663c047f9b451a218002c746d893ce0b"
)
OLD_COHORT_ID = "CONTEXT_LEVEL_A_ROTATING_DAILY_30_V1"
OLD_PLAN_FILENAME = "context_evaluation_concrete_cohort_plan_v1.json"
OLD_CONTEXT_ANCHOR = "2026-08-30T18:00:00+00:00"
OLD_CONTEXT_RUN_NAME = "S008_20260830T180000Z"
OLD_OBSERVATION_ID = "LONGREVIEW_2ED6D147FC8A4640D3FD2431"

BAR = timedelta(minutes=15)
CAPTURE_GRACE = timedelta(seconds=5)
H16 = timedelta(hours=4)
MINIMUM_PRE_SESSION_BUFFER_SECONDS = 120

DEFAULT_EVIDENCE_ROOT = (
    Path("C:/TAE") if os.name == "nt" else Path.home() / "TAE"
)
EVIDENCE_ROOT = Path(
    os.environ.get("TRADING_AI_EVIDENCE_ROOT", str(DEFAULT_EVIDENCE_ROOT))
).expanduser()
COHORT_ROOT = EVIDENCE_ROOT / "context_evaluation_cohorts" / COHORT_ID
MAX_EVIDENCE_ROOT_CHARS = 64
MAX_PROJECTED_PATH_CHARS = 239

FROZEN_COMPONENT_BLOBS = {
    "src/exchange/long_primary_public_closed_candle_capture_v1.py":
        "51cb7f972e9f0ccdca318d0bea2cfb16bb42b657",
    "src/exchange/public_read_only_microstructure_snapshot_v1_1.py":
        "f7ec588060bd17466ad962972c1615481799ebb6",
    "src/long_side/synchronized_15m_observation_v1_1_microstructure_auth_propagation_v1.py":
        "584aed549182cf018809422727a9b5bd50a84a7a",
    "src/long_side/forward_outcome_labeler_v1.py":
        "e7532fd7b4eb58d81edab3ccbd4e33ea310b88fd",
    "src/context/liquidity_sweep_pattern_context_v1.py":
        "13b172ab2e09782eff0adc0053f8a25395409124",
    "src/context/synchronized_microstructure_context_v1.py":
        "ad476da3a116553d789d5a922d4b33038d3cb4c4",
    "src/context/context_feature_pack_v1_level_a_standard.py":
        "ee32d587d8dd28f887d04942ba24e4ba3b679c62",
    "src/evaluation/context_evaluation_prospective_cohort_v1.py":
        "2c4ad00b9b77fbd9a33fffd7b38fbd47c16da21a",
}


def fail(message: str) -> None:
    raise RuntimeError(message)


def utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def parse_utc(value: Any) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        fail(f"TIMESTAMP_TIMEZONE_REQUIRED: {value}")
    return parsed.astimezone(timezone.utc)


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        fail(
            f"GIT_COMMAND_FAILED rc={result.returncode} "
            f"cmd={' '.join(args)} stderr={result.stderr.strip()}"
        )
    return result.stdout.strip()


def verify_external_root_and_path_budget(repo: Path) -> None:
    if not EVIDENCE_ROOT.is_absolute():
        fail(f"EVIDENCE_ROOT_MUST_BE_ABSOLUTE: {EVIDENCE_ROOT}")
    root = EVIDENCE_ROOT.resolve()
    repo_resolved = repo.resolve()
    home = Path.home().resolve()
    drive_root = Path(root.anchor).resolve()
    if len(str(root)) > MAX_EVIDENCE_ROOT_CHARS:
        fail(
            "EVIDENCE_ROOT_NOT_SHORT "
            f"length={len(str(root))} maximum={MAX_EVIDENCE_ROOT_CHARS}"
        )
    if root in {repo_resolved, home, drive_root}:
        fail(f"EVIDENCE_ROOT_SCOPE_FORBIDDEN: {root}")
    if root in repo_resolved.parents or repo_resolved in root.parents:
        fail(f"EVIDENCE_ROOT_NOT_EXTERNAL_TO_REPOSITORY: {root}")
    longest = (
        root
        / "runs"
        / "D30V3_S030_20261105T213000Z"
        / "synchronized_session"
        / "synchronized_v1_1_session"
        / "microstructure"
        / (".cycle_0001.tmp-" + ("f" * 32))
        / (("x" * 55) + ".json")
    )
    projected = len(str(longest))
    print(f"EVIDENCE_ROOT={root}")
    print(f"EVIDENCE_ROOT_LENGTH={len(str(root))}")
    print(f"MAX_PROJECTED_PATH_LENGTH={projected}")
    if projected > MAX_PROJECTED_PATH_CHARS:
        fail(
            "PATH_BUDGET_TOO_TIGHT "
            f"projected={projected} maximum={MAX_PROJECTED_PATH_CHARS}"
        )
    print("EVIDENCE_ROOT_EXTERNAL_AND_SHORT=True")
    print("WINDOWS_PATH_BUDGET_STATIC_GUARD_VALID=True")


def load_plan(repo: Path) -> dict[str, Any]:
    path = repo / PLAN_RELATIVE
    if not path.is_file() or path.is_symlink():
        fail(f"PLAN_FILE_INVALID: {path}")
    payload = path.read_bytes()
    actual_raw_sha = hashlib.sha256(payload).hexdigest()
    value = json.loads(payload.decode("utf-8"))
    if not isinstance(value, dict):
        fail("PLAN_MAPPING_REQUIRED")
    canonical_sha = hashlib.sha256(canonical_json_bytes(value)).hexdigest()
    print(f"PLAN_FILE_SHA256={actual_raw_sha}")
    print(f"PLAN_CANONICAL_SHA256={canonical_sha}")
    if actual_raw_sha != EXPECTED_PLAN_SHA256:
        fail("PLAN_FILE_NOT_CANONICAL_OR_SHA_CHANGED")
    if canonical_sha != EXPECTED_PLAN_SHA256:
        fail("PLAN_CANONICAL_SHA256_MISMATCH")
    if value.get("cohort_id") != COHORT_ID:
        fail("PLAN_COHORT_ID_MISMATCH")
    if value.get("hypothesis_manifest_sha256") != EXPECTED_HYPOTHESIS_SHA256:
        fail("PLAN_HYPOTHESIS_SHA_MISMATCH")
    return value


def slot_from_plan(plan: dict[str, Any], slot_id: str) -> dict[str, Any]:
    slot_id = str(slot_id).strip().upper()
    matches = [x for x in plan.get("slots", []) if x.get("slot_id") == slot_id]
    if len(matches) != 1:
        fail(f"SLOT_NOT_UNIQUELY_PREDECLARED: {slot_id}")
    return dict(matches[0])


def stamp_for_anchor(anchor: datetime) -> str:
    return anchor.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run_name(slot_id: str, anchor: datetime) -> str:
    return f"D30V3_{slot_id}_{stamp_for_anchor(anchor)}"


def run_root(slot_id: str, anchor: datetime) -> Path:
    return EVIDENCE_ROOT / "runs" / run_name(slot_id, anchor)


def admission_dir(slot_id: str) -> Path:
    return COHORT_ROOT / "admissions" / slot_id


def binding_dir(slot_id: str) -> Path:
    return COHORT_ROOT / "bindings" / slot_id


def verify_template(path: Path, expected_sha: str, label: str) -> str:
    if not path.is_file() or path.is_symlink():
        fail(f"{label}_TEMPLATE_INVALID: {path}")
    actual = sha256_file(path)
    print(f"{label}_TEMPLATE_SHA256={actual}")
    if actual != expected_sha:
        fail(f"{label}_TEMPLATE_SHA256_MISMATCH")
    return path.read_text(encoding="utf-8")


def verify_closed_components(repo: Path) -> None:
    for path, expected_blob in FROZEN_COMPONENT_BLOBS.items():
        actual = git(repo, "hash-object", "--", path)
        if actual != expected_blob:
            fail(
                "FROZEN_COMPONENT_BLOB_CHANGED "
                f"path={path} expected={expected_blob} actual={actual}"
            )
    print("FROZEN_COMPONENT_BLOBS_VERIFIED=True")


def verify_official_artifacts(repo: Path) -> tuple[str, str]:
    if os.environ.get(OFFICIAL_APPEND_GATE) == "1":
        fail("OFFICIAL_APPEND_GATE_ENABLED")
    dataset = repo / "data/forward/long_forward_observation_dataset_v1.csv"
    manifest = repo / "data/forward/long_forward_observation_dataset_v1.manifest.csv"
    lock = repo / "data/forward/long_forward_observation_dataset_v1.lock"
    if lock.exists() or lock.is_symlink():
        fail("OFFICIAL_APPEND_LOCK_PRESENT")
    dataset_sha = sha256_file(dataset)
    manifest_sha = sha256_file(manifest)
    if dataset_sha != EXPECTED_OFFICIAL_DATASET_SHA256:
        fail("OFFICIAL_DATASET_SHA256_MISMATCH")
    if manifest_sha != EXPECTED_OFFICIAL_MANIFEST_SHA256:
        fail("OFFICIAL_MANIFEST_SHA256_MISMATCH")
    print("OFFICIAL_ARTIFACTS_UNCHANGED=True")
    print("OFFICIAL_APPEND_GATE_ENABLED=False")
    return dataset_sha, manifest_sha


def verify_real_repo(repo: Path) -> str:
    if not (repo / ".git").is_dir():
        fail(f"REPOSITORY_INVALID: {repo}")
    verify_external_root_and_path_budget(repo)
    branch = git(repo, "branch", "--show-current")
    head = git(repo, "rev-parse", "HEAD")
    main = git(repo, "rev-parse", "main")
    origin_main = git(repo, "rev-parse", "origin/main")
    status = git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    print(f"ACTIVE_BRANCH={branch}")
    print(f"HEAD={head}")
    print(f"MAIN={main}")
    print(f"ORIGIN_MAIN={origin_main}")
    print(f"WORKING_TREE_CLEAN={status == ''}")
    if branch != "main":
        fail("ACTIVE_BRANCH_NOT_MAIN")
    if head != main or head != origin_main:
        fail("HEAD_MAIN_ORIGIN_MAIN_MISMATCH")
    if status:
        fail("WORKING_TREE_NOT_CLEAN")
    load_plan(repo)
    verify_closed_components(repo)
    verify_official_artifacts(repo)
    return head


def validate_plan_with_frozen_contract(repo: Path) -> dict[str, Any]:
    sys.path.insert(0, str(repo))
    from src.evaluation import context_evaluation_prospective_cohort_v1 as cohort

    plan = load_plan(repo)
    policy, _ = cohort.load_context_evaluation_prospective_cohort_policy_v1(repo)
    hypothesis, hypothesis_sha, _ = cohort.load_bound_hypothesis_manifest_v1(
        repo, policy=policy
    )
    validated = cohort.validate_prospective_cohort_plan_v1(
        plan,
        policy=policy,
        hypothesis_manifest=hypothesis,
        hypothesis_manifest_sha256=hypothesis_sha,
    )
    if len(validated["slots"]) != 30:
        fail("DAILY_EVENING_PLAN_SLOT_COUNT_INVALID")
    expected_ids = [f"S{i:03d}" for i in range(1, 31)]
    actual_ids = [x["slot_id"] for x in validated["slots"]]
    if actual_ids != expected_ids:
        fail("DAILY_EVENING_SLOT_IDS_INVALID")
    anchors = [parse_utc(x["context_anchor_open_utc"]) for x in validated["slots"]]
    spacings = [b - a for a, b in zip(anchors, anchors[1:])]
    if min(spacings) < timedelta(hours=4):
        fail("DAILY_EVENING_MINIMUM_SPACING_INVALID")
    if min(spacings) != timedelta(hours=24):
        fail("DAILY_EVENING_MINIMUM_SPACING_UNEXPECTED")
    if max(spacings) != timedelta(hours=24):
        fail("DAILY_EVENING_MAXIMUM_SPACING_UNEXPECTED")
    print("FROZEN_PLAN_CONTRACT_VALIDATED=True")
    print("PLANNED_SLOT_COUNT=30")
    print("MINIMUM_ACTUAL_SLOT_SPACING_HOURS=24")
    print("MAXIMUM_ACTUAL_SLOT_SPACING_HOURS=24")
    print("H16_WINDOWS_NON_OVERLAPPING=True")
    return validated


def dt_constructor(value: datetime) -> str:
    v = value.astimezone(timezone.utc)
    return (
        f"datetime({v.year}, {v.month}, {v.day}, {v.hour}, {v.minute}, "
        "tzinfo=timezone.utc)"
    )


def transform_context_template(
    repo: Path,
    *,
    slot_id: str,
    anchor: datetime,
    expected_head: str,
) -> str:
    template_path = repo / CONTEXT_TEMPLATE_RELATIVE
    source = verify_template(
        template_path,
        CONTEXT_TEMPLATE_SHA256,
        "CONTEXT",
    )
    name = run_name(slot_id, anchor)
    replacements = [
        (OLD_HEAD, expected_head),
        (OLD_PLAN_SHA256, EXPECTED_PLAN_SHA256),
        (OLD_COHORT_ID, COHORT_ID),
        (OLD_PLAN_FILENAME, PLAN_RELATIVE.name),
        (OLD_CONTEXT_RUN_NAME, name),
        (OLD_CONTEXT_ANCHOR, utc(anchor)),
    ]
    for old, new in replacements:
        if old not in source:
            fail(f"CONTEXT_TEMPLATE_EXPECTED_TOKEN_MISSING: {old}")
        source = source.replace(old, new)
    source = source.replace("S008", slot_id)
    if OLD_COHORT_ID in source or OLD_CONTEXT_RUN_NAME in source:
        fail("CONTEXT_TEMPLATE_TRANSFORM_INCOMPLETE")
    if slot_id != "S008" and "S008" in source:
        fail("CONTEXT_TEMPLATE_SLOT_REPLACEMENT_INCOMPLETE")
    compile(source, f"<daily_evening_context_{slot_id}>", "exec")
    return source


def transform_outcome_template(
    repo: Path,
    *,
    slot_id: str,
    anchor: datetime,
    observation_id: str,
    expected_head: str,
) -> str:
    template_path = repo / OUTCOME_TEMPLATE_RELATIVE
    source = verify_template(
        template_path,
        OUTCOME_TEMPLATE_SHA256,
        "OUTCOME",
    )
    reference = anchor - BAR
    h16 = anchor + H16
    name = run_name(slot_id, anchor)
    replacements = [
        (OLD_HEAD, expected_head),
        (OLD_COHORT_ID, COHORT_ID),
        (OLD_CONTEXT_RUN_NAME, name),
        (OLD_OBSERVATION_ID, observation_id),
        (
            "datetime(2026, 8, 30, 18, 0, tzinfo=timezone.utc)",
            dt_constructor(anchor),
        ),
        (
            "datetime(2026, 8, 30, 17, 45, tzinfo=timezone.utc)",
            dt_constructor(reference),
        ),
        (
            "datetime(2026, 8, 30, 22, 0, tzinfo=timezone.utc)",
            dt_constructor(h16),
        ),
    ]
    for old, new in replacements:
        if old not in source:
            fail(f"OUTCOME_TEMPLATE_EXPECTED_TOKEN_MISSING: {old}")
        source = source.replace(old, new)
    source = source.replace("S008", slot_id)
    if OLD_COHORT_ID in source or OLD_CONTEXT_RUN_NAME in source:
        fail("OUTCOME_TEMPLATE_TRANSFORM_INCOMPLETE")
    if slot_id != "S008" and "S008" in source:
        fail("OUTCOME_TEMPLATE_SLOT_REPLACEMENT_INCOMPLETE")
    compile(source, f"<daily_evening_outcome_{slot_id}>", "exec")
    return source


def namespace_from_source(source: str, name: str) -> dict[str, Any]:
    namespace: dict[str, Any] = {
        "__name__": name,
        "__package__": None,
    }
    exec(compile(source, f"<{name}>", "exec"), namespace, namespace)
    return namespace


def bind_context_namespace_paths(
    namespace: dict[str, Any],
    *,
    slot_id: str,
    anchor: datetime,
) -> None:
    rebound_run_root = EVIDENCE_ROOT / "runs" / run_name(slot_id, anchor)
    namespace["COHORT_ROOT"] = COHORT_ROOT
    namespace["RUN_PARENT"] = EVIDENCE_ROOT / "runs"
    namespace["RUN_ROOT"] = rebound_run_root
    namespace["OFFLINE_PARENT"] = EVIDENCE_ROOT / "ov"


def bind_outcome_namespace_paths(
    namespace: dict[str, Any],
    *,
    slot_id: str,
    anchor: datetime,
) -> None:
    rebound_run_root = EVIDENCE_ROOT / "runs" / run_name(slot_id, anchor)
    outcome_root = rebound_run_root / "outcome_binding_v1"
    namespace["EVIDENCE_ROOT"] = EVIDENCE_ROOT
    namespace["COHORT_ROOT"] = COHORT_ROOT
    namespace["SLOT_RUN_ROOT"] = rebound_run_root
    namespace["INNER_SESSION"] = (
        rebound_run_root
        / "synchronized_session"
        / "synchronized_v1_1_session"
    )
    namespace["OUTCOME_ROOT"] = outcome_root
    namespace["FUTURE_CAPTURE_DIR"] = (
        outcome_root / "future_closed_candle_capture"
    )
    namespace["OUTCOME_PACKAGE_DIR"] = (
        outcome_root / "forward_outcome_package"
    )


def verify_namespace_paths(
    namespace: dict[str, Any],
    expected_run_root: Path,
) -> None:
    expected_root = EVIDENCE_ROOT.resolve()
    for key in ("COHORT_ROOT", "RUN_ROOT", "SLOT_RUN_ROOT", "OUTCOME_ROOT"):
        if key not in namespace:
            continue
        value = Path(namespace[key]).resolve()
        if value != expected_root and expected_root not in value.parents:
            fail(f"TEMPLATE_PATH_NOT_REBOUND key={key} path={value}")
    actual_run_root = namespace.get("RUN_ROOT", namespace.get("SLOT_RUN_ROOT"))
    if Path(actual_run_root).resolve() != expected_run_root.resolve():
        fail("TEMPLATE_RUN_ROOT_REBIND_MISMATCH")


def read_admission_observation_id(slot_id: str) -> str:
    path = admission_dir(slot_id) / "admission_receipt.json"
    if not path.is_file() or path.is_symlink():
        fail(f"ADMISSION_RECEIPT_MISSING: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    observation_id = str(value.get("observation_id", "")).strip()
    if not observation_id:
        fail("ADMISSION_OBSERVATION_ID_MISSING")
    return observation_id


def self_check(repo: Path) -> int:
    print("=== DAILY EVENING RUNNER SELF CHECK V3 ===")
    print("REAL_NETWORK_REQUEST_ALLOWED=False")
    print("REAL_MARKET_DATA_FETCHED=False")
    print("REAL_COHORT_MODIFICATION_ALLOWED=False")
    verify_external_root_and_path_budget(repo)
    plan = validate_plan_with_frozen_contract(repo)
    verify_closed_components(repo)
    verify_template(repo / CONTEXT_TEMPLATE_RELATIVE, CONTEXT_TEMPLATE_SHA256, "CONTEXT")
    verify_template(repo / OUTCOME_TEMPLATE_RELATIVE, OUTCOME_TEMPLATE_SHA256, "OUTCOME")
    fake_head = "0" * 40
    for item in plan["slots"]:
        slot_id = item["slot_id"]
        anchor = parse_utc(item["context_anchor_open_utc"])
        transform_context_template(
            repo,
            slot_id=slot_id,
            anchor=anchor,
            expected_head=fake_head,
        )
        transform_outcome_template(
            repo,
            slot_id=slot_id,
            anchor=anchor,
            observation_id="LONGREVIEW_SELF_CHECK_ONLY",
            expected_head=fake_head,
        )
    last = plan["slots"][-1]
    sample_slot_id = last["slot_id"]
    sample_anchor = parse_utc(last["context_anchor_open_utc"])
    expected_run_root = run_root(sample_slot_id, sample_anchor)
    context_namespace = namespace_from_source(
        transform_context_template(
            repo,
            slot_id=sample_slot_id,
            anchor=sample_anchor,
            expected_head=fake_head,
        ),
        "daily_evening_context_path_rebind_self_check",
    )
    bind_context_namespace_paths(
        context_namespace,
        slot_id=sample_slot_id,
        anchor=sample_anchor,
    )
    verify_namespace_paths(context_namespace, expected_run_root)
    outcome_namespace = namespace_from_source(
        transform_outcome_template(
            repo,
            slot_id=sample_slot_id,
            anchor=sample_anchor,
            observation_id="LONGREVIEW_SELF_CHECK_ONLY",
            expected_head=fake_head,
        ),
        "daily_evening_outcome_path_rebind_self_check",
    )
    bind_outcome_namespace_paths(
        outcome_namespace,
        slot_id=sample_slot_id,
        anchor=sample_anchor,
    )
    verify_namespace_paths(outcome_namespace, expected_run_root)
    print("ALL_30_CONTEXT_TRANSFORMS_COMPILE=True")
    print("ALL_30_OUTCOME_TRANSFORMS_COMPILE=True")
    print("TEMPLATE_EXTERNAL_PATH_REBIND_VERIFIED=True")
    print("REAL_HTTP_CALLS=0")
    print("OFFICIAL_APPEND_EXECUTED=False")
    print("SELF_CHECK_PASSED=True")
    return 0


def initialize_root(repo: Path) -> int:
    print("=== INITIALIZE DAILY EVENING COHORT ROOT V3 ===")
    head = verify_real_repo(repo)
    plan = validate_plan_with_frozen_contract(repo)
    first_anchor = parse_utc(plan["slots"][0]["context_anchor_open_utc"])
    initialization_deadline = first_anchor - BAR * 2 + CAPTURE_GRACE
    now = datetime.now(timezone.utc)
    print(f"INITIALIZATION_DEADLINE_UTC={utc(initialization_deadline)}")
    if now >= initialization_deadline:
        fail(
            "FULL_COHORT_INITIALIZATION_WINDOW_EXPIRED "
            f"now={utc(now)} deadline={utc(initialization_deadline)}"
        )
    sys.path.insert(0, str(repo))
    from src.evaluation import context_evaluation_prospective_cohort_v1 as cohort

    COHORT_ROOT.parent.mkdir(parents=True, exist_ok=True)
    if COHORT_ROOT.exists() or COHORT_ROOT.is_symlink():
        fail(f"COHORT_ROOT_ALREADY_EXISTS: {COHORT_ROOT}")
    result = cohort.initialize_prospective_cohort_v1(
        repo_root=repo,
        plan_json=repo / PLAN_RELATIVE,
        cohort_root=COHORT_ROOT,
        authorization=cohort.INITIALIZE_AUTHORIZATION,
    )
    print(f"HEAD={head}")
    print(f"COHORT_ROOT={COHORT_ROOT}")
    print(f"COHORT_ID={result['cohort_id']}")
    print(f"PLANNED_SLOTS={result['planned_slots']}")
    print(
        "PREREGISTERED_HORIZONS="
        + ",".join(str(x) for x in result["preregistered_horizons_bars"])
    )
    print("FORWARD_OUTCOMES_READ=False")
    print("NETWORK_REQUEST_EXECUTED=False")
    print("MARKET_DATA_FETCHED=False")
    print("OFFICIAL_APPEND_EXECUTED=False")
    print("DAILY_EVENING_COHORT_ROOT_INITIALIZED=True")
    return 0


def print_slot_status(slot: dict[str, Any], now: datetime) -> None:
    slot_id = slot["slot_id"]
    anchor = parse_utc(slot["context_anchor_open_utc"])
    capture_target = anchor - BAR + CAPTURE_GRACE
    window_open = capture_target - BAR
    latest_safe = capture_target - timedelta(
        seconds=MINIMUM_PRE_SESSION_BUFFER_SECONDS
    )
    h16 = anchor + H16
    admission = admission_dir(slot_id).is_dir()
    binding = binding_dir(slot_id).is_dir()
    if binding:
        state = "BOUND"
    elif admission:
        state = "ADMITTED_OUTCOME_NOT_BOUND"
    elif now > anchor + BAR * 2:
        state = "SLOT_NOT_ADMITTED_PAST"
    else:
        state = "PLANNED"
    print(f"SLOT_ID={slot_id}")
    print(f"STATE={state}")
    print(f"CONTEXT_ANCHOR_OPEN_UTC={utc(anchor)}")
    print(f"CAPTURE_TARGET_UTC={utc(capture_target)}")
    print(f"EXECUTION_WINDOW_OPENS_AFTER_UTC={utc(window_open)}")
    print(f"LATEST_SAFE_START_UTC={utc(latest_safe)}")
    print(f"H16_MATURITY_UTC={utc(h16)}")
    print(f"ADMISSION_EXISTS={admission}")
    print(f"BINDING_EXISTS={binding}")


def status(repo: Path, slot_id: str | None) -> int:
    print("=== DAILY EVENING COHORT STATUS V3 ===")
    verify_real_repo(repo)
    plan = load_plan(repo)
    now = datetime.now(timezone.utc)
    print(f"NOW_UTC={utc(now)}")
    print(f"COHORT_ROOT_EXISTS={COHORT_ROOT.is_dir()}")
    if not COHORT_ROOT.is_dir():
        print("NEXT_STEP=INITIALIZE_ROOT")
        return 0
    slots = plan["slots"]
    if slot_id:
        print_slot_status(slot_from_plan(plan, slot_id), now)
        return 0
    admitted = sum(admission_dir(x["slot_id"]).is_dir() for x in slots)
    bound = sum(binding_dir(x["slot_id"]).is_dir() for x in slots)
    print(f"PLANNED_SLOTS={len(slots)}")
    print(f"ADMITTED_SLOTS={admitted}")
    print(f"BOUND_SLOTS={bound}")
    upcoming = [x for x in slots if parse_utc(x["context_anchor_open_utc"]) > now]
    if upcoming:
        print("=== NEXT PLANNED SLOT ===")
        print_slot_status(upcoming[0], now)
    else:
        print("NEXT_PLANNED_SLOT=NONE")
    return 0


def offline_validate_context(repo: Path, slot_id: str) -> int:
    head = verify_real_repo(repo)
    plan = load_plan(repo)
    slot = slot_from_plan(plan, slot_id)
    anchor = parse_utc(slot["context_anchor_open_utc"])
    source = transform_context_template(
        repo,
        slot_id=slot_id,
        anchor=anchor,
        expected_head=head,
    )
    namespace = namespace_from_source(source, f"daily_evening_context_{slot_id}")
    bind_context_namespace_paths(
        namespace, slot_id=slot_id, anchor=anchor
    )
    return int(namespace["offline_validate"](repo))


def execute_context(
    repo: Path,
    slot_id: str,
    source_attestation: str | None,
) -> int:
    head = verify_real_repo(repo)
    plan = load_plan(repo)
    slot = slot_from_plan(plan, slot_id)
    anchor = parse_utc(slot["context_anchor_open_utc"])
    source = transform_context_template(
        repo,
        slot_id=slot_id,
        anchor=anchor,
        expected_head=head,
    )
    namespace = namespace_from_source(source, f"daily_evening_context_{slot_id}")
    bind_context_namespace_paths(
        namespace, slot_id=slot_id, anchor=anchor
    )
    return int(namespace["execute_real"](repo, source_attestation))


def offline_validate_binding(repo: Path, slot_id: str) -> int:
    head = verify_real_repo(repo)
    plan = load_plan(repo)
    slot = slot_from_plan(plan, slot_id)
    anchor = parse_utc(slot["context_anchor_open_utc"])
    observation_id = read_admission_observation_id(slot_id)
    source = transform_outcome_template(
        repo,
        slot_id=slot_id,
        anchor=anchor,
        observation_id=observation_id,
        expected_head=head,
    )
    namespace = namespace_from_source(source, f"daily_evening_outcome_{slot_id}")
    bind_outcome_namespace_paths(
        namespace, slot_id=slot_id, anchor=anchor
    )
    return int(namespace["offline_validate"](repo))


def bind_outcomes(
    repo: Path,
    slot_id: str,
    source_attestation: str | None,
) -> int:
    head = verify_real_repo(repo)
    plan = load_plan(repo)
    slot = slot_from_plan(plan, slot_id)
    anchor = parse_utc(slot["context_anchor_open_utc"])
    observation_id = read_admission_observation_id(slot_id)
    source = transform_outcome_template(
        repo,
        slot_id=slot_id,
        anchor=anchor,
        observation_id=observation_id,
        expected_head=head,
    )
    namespace = namespace_from_source(source, f"daily_evening_outcome_{slot_id}")
    bind_outcome_namespace_paths(
        namespace, slot_id=slot_id, anchor=anchor
    )
    return int(namespace["execute"](repo, source_attestation))


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Supervised, plan-bound runner for CONTEXT_LEVEL_A_DAILY_EVENING_30_V3"
        )
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-check", action="store_true")
    mode.add_argument("--initialize-root", action="store_true")
    mode.add_argument("--status", action="store_true")
    mode.add_argument("--offline-validate-context", action="store_true")
    mode.add_argument("--execute-context", action="store_true")
    mode.add_argument("--offline-validate-binding", action="store_true")
    mode.add_argument("--bind-outcomes", action="store_true")
    parser.add_argument("--slot", default=None)
    parser.add_argument("--source-attestation", default=None)
    parser.add_argument(
        "--repo",
        default=str(Path.home() / "OpenClawProjects" / "trading-ai"),
    )
    args = parser.parse_args()
    repo = Path(args.repo).resolve()

    slot_modes = (
        args.offline_validate_context,
        args.execute_context,
        args.offline_validate_binding,
        args.bind_outcomes,
    )
    if any(slot_modes) and not args.slot:
        fail("--slot is required for this mode")
    if (args.execute_context or args.bind_outcomes) and (
        args.source_attestation != SOURCE_ATTESTATION
    ):
        fail(
            "REAL_SOURCE_HUMAN_ATTESTATION_REQUIRED "
            f"expected={SOURCE_ATTESTATION}"
        )

    if args.self_check:
        return self_check(repo)
    if args.initialize_root:
        return initialize_root(repo)
    if args.status:
        return status(repo, args.slot)
    if args.offline_validate_context:
        return offline_validate_context(repo, args.slot.upper())
    if args.execute_context:
        return execute_context(
            repo,
            args.slot.upper(),
            args.source_attestation,
        )
    if args.offline_validate_binding:
        return offline_validate_binding(repo, args.slot.upper())
    if args.bind_outcomes:
        return bind_outcomes(
            repo,
            args.slot.upper(),
            args.source_attestation,
        )
    fail("UNREACHABLE_MODE")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("DAILY_EVENING_RUNNER_STATUS=FAILED", file=sys.stderr)
        print(f"ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
        print("NO_RESET_NO_FORCE_NO_AMEND=True", file=sys.stderr)
        raise
