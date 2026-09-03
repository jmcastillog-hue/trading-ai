from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

EXPECTED_HEAD = "beefd785be607db17f2faa910674a8fb6268f00b"
EXPECTED_OFFICIAL_DATASET_SHA256 = "e3fa86a461fd46f4d66dc2e03f185e49b7b3438d3cbc33340c01f51310514ff1"
EXPECTED_OFFICIAL_MANIFEST_SHA256 = "99fc1f3f0e57bc11ec79c2c08481450a1bda1d7eaf8b84e85962fd25c3d4806e"
COHORT_ID = "CONTEXT_LEVEL_A_ROTATING_DAILY_30_V1"
SLOT_ID = "S008"
OBSERVATION_ID = "LONGREVIEW_2ED6D147FC8A4640D3FD2431"
CONTEXT_ANCHOR = datetime(2026, 8, 30, 18, 0, tzinfo=timezone.utc)
REFERENCE_BOUNDARY = datetime(2026, 8, 30, 17, 45, tzinfo=timezone.utc)
H16_MATURITY = datetime(2026, 8, 30, 22, 0, tzinfo=timezone.utc)
BAR = timedelta(minutes=15)
CLOSE_EPSILON = timedelta(milliseconds=1)
SOURCE_ATTESTATION = "REAL_MARKET_DATA_SOURCE_HUMAN_ATTESTED_NOT_SYNTHETIC"
OFFICIAL_APPEND_GATE = "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
EVIDENCE_ROOT = Path.home() / "TradingAI-Evidence"
COHORT_ROOT = EVIDENCE_ROOT / "context_evaluation_cohorts" / COHORT_ID
SLOT_RUN_ROOT = EVIDENCE_ROOT / "runs" / "S008_20260830T180000Z"
INNER_SESSION = SLOT_RUN_ROOT / "synchronized_session" / "synchronized_v1_1_session"
OUTCOME_ROOT = SLOT_RUN_ROOT / "outcome_binding_v1"
FUTURE_CAPTURE_DIR = OUTCOME_ROOT / "future_closed_candle_capture"
OUTCOME_PACKAGE_DIR = OUTCOME_ROOT / "forward_outcome_package"
NETWORK_PHASE_ENTERED = False


def fail(message: str) -> None:
    raise RuntimeError(message)


def utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def parse_utc(value: Any) -> datetime:
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        fail(f"TIMESTAMP_TIMEZONE_REQUIRED: {value}")
    return dt.astimezone(timezone.utc)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode != 0:
        fail(f"GIT_COMMAND_FAILED rc={r.returncode} cmd={' '.join(args)} stderr={r.stderr.strip()}")
    return r.stdout.strip()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"JSON_MAPPING_REQUIRED: {path}")
    return value


def verify_repo(repo: Path) -> tuple[str, str]:
    if not (repo / ".git").is_dir():
        fail(f"REPOSITORY_INVALID: {repo}")
    branch = git(repo, "branch", "--show-current")
    head = git(repo, "rev-parse", "HEAD")
    main = git(repo, "rev-parse", "main")
    status = git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    print(f"ACTIVE_BRANCH={branch}")
    print(f"HEAD={head}")
    print(f"MAIN={main}")
    print(f"WORKING_TREE_CLEAN={status == ''}")
    if branch != "main" or head != EXPECTED_HEAD or main != EXPECTED_HEAD or status:
        fail("REPOSITORY_STATE_MISMATCH")
    if os.environ.get(OFFICIAL_APPEND_GATE) == "1":
        fail("OFFICIAL_APPEND_GATE_ENABLED")
    dataset = repo / "data/forward/long_forward_observation_dataset_v1.csv"
    manifest = repo / "data/forward/long_forward_observation_dataset_v1.manifest.csv"
    lock = repo / "data/forward/long_forward_observation_dataset_v1.lock"
    if lock.exists() or lock.is_symlink():
        fail("OFFICIAL_APPEND_LOCK_PRESENT")
    ds = sha256_file(dataset)
    mf = sha256_file(manifest)
    if ds != EXPECTED_OFFICIAL_DATASET_SHA256 or mf != EXPECTED_OFFICIAL_MANIFEST_SHA256:
        fail("OFFICIAL_ARTIFACT_SHA256_MISMATCH")
    print("OFFICIAL_ARTIFACTS_UNCHANGED=True")
    print("OFFICIAL_APPEND_GATE_ENABLED=False")
    return ds, mf


def import_contracts(repo: Path) -> dict[str, Any]:
    sys.path.insert(0, str(repo))
    from src.exchange import long_primary_public_closed_candle_capture_v1 as spot
    from src.long_side import forward_outcome_labeler_v1 as labeler
    from src.evaluation import context_evaluation_prospective_cohort_v1 as cohort
    return {"spot": spot, "labeler": labeler, "cohort": cohort}


def verify_s008(contracts: dict[str, Any]) -> dict[str, Any]:
    cohort = contracts["cohort"]
    adir = COHORT_ROOT / "admissions" / SLOT_ID
    bdir = COHORT_ROOT / "bindings" / SLOT_ID
    if not SLOT_RUN_ROOT.is_dir() or not INNER_SESSION.is_dir() or not adir.is_dir():
        fail("S008_REQUIRED_ARTIFACT_MISSING")
    if bdir.exists() or bdir.is_symlink():
        fail("S008_BINDING_ALREADY_EXISTS")
    receipt = cohort.validate_admission_receipt_v1(adir)
    if receipt.get("slot_id") != SLOT_ID or receipt.get("observation_id") != OBSERVATION_ID:
        fail("S008_ADMISSION_IDENTITY_MISMATCH")
    if parse_utc(receipt["context_anchor_open_utc"]) != CONTEXT_ANCHOR:
        fail("S008_CONTEXT_ANCHOR_MISMATCH")
    context_dir = Path(receipt["context_pack_directory"]).resolve()
    context_manifest = context_dir / "manifest.sha256"
    if not context_manifest.is_file():
        fail("S008_CONTEXT_PACK_MANIFEST_MISSING")
    if sha256_file(context_manifest) != receipt["context_pack_manifest_sha256"]:
        fail("S008_CONTEXT_PACK_CHANGED_AFTER_ADMISSION")
    print("S008_PROSPECTIVE_ADMISSION_VALID=True")
    print(f"S008_OBSERVATION_ID={OBSERVATION_ID}")
    print("S008_CONTEXT_PACK_UNCHANGED_SINCE_ADMISSION=True")
    print("S008_BINDING_ALREADY_EXISTS=False")
    return receipt


def latest_expected_closed_open(now: datetime) -> datetime:
    floor = now.astimezone(timezone.utc).replace(minute=(now.minute // 15) * 15, second=0, microsecond=0)
    return floor - BAR


def verify_retention(now: datetime) -> None:
    if now < H16_MATURITY:
        fail("H16_NOT_MATURED")
    latest_open = latest_expected_closed_open(now)
    earliest_open = latest_open - BAR * 62
    print(f"NOW_UTC={utc(now)}")
    print(f"H16_MATURITY_UTC={utc(H16_MATURITY)}")
    print("H16_MATURED=True")
    print(f"PROJECTED_LATEST_CLOSED_OPEN_UTC={utc(latest_open)}")
    print("CONSERVATIVE_EXPECTED_CLOSED_ROWS_FROM_64_REQUEST=63")
    print(f"PROJECTED_EARLIEST_RETAINED_OPEN_UTC={utc(earliest_open)}")
    print(f"REQUIRED_PRIMARY_ANCHOR_OPEN_UTC={utc(REFERENCE_BOUNDARY)}")
    if earliest_open > REFERENCE_BOUNDARY:
        fail("SPOT_64_ROW_RETENTION_WINDOW_LOST")
    print("SPOT_64_ROW_RETENTION_WINDOW_VALID=True")


def build_descriptor(contracts: dict[str, Any]) -> dict[str, Any]:
    descriptor = contracts["labeler"].build_observation_descriptor_from_synchronized_session(
        synchronized_session_directory=INNER_SESSION,
        cycle_index=1,
    )
    if descriptor["observation_id"] != OBSERVATION_ID:
        fail("DESCRIPTOR_OBSERVATION_ID_MISMATCH")
    if parse_utc(descriptor["reference_boundary_utc"]) != REFERENCE_BOUNDARY:
        fail("DESCRIPTOR_REFERENCE_BOUNDARY_MISMATCH")
    if parse_utc(descriptor["synchronized_context_available_at_utc"]) >= CONTEXT_ANCHOR:
        fail("DESCRIPTOR_CONTEXT_CUTOFF_NOT_BEFORE_ANCHOR")
    print("S008_OBSERVATION_DESCRIPTOR_VALID=True")
    return descriptor


def write_synthetic_future_csv(path: Path, reference_price: float) -> None:
    columns = ("open_time_utc","close_time_utc","symbol","timeframe","open","high","low","close","volume","candle_closed")
    rows = []
    current = REFERENCE_BOUNDARY
    for i in range(24):
        o = reference_price * (1.0 + i * 0.00001)
        c = o * 1.00002
        h = max(o, c) * 1.0005
        l = min(o, c) * 0.9995
        rows.append({
            "open_time_utc": utc(current),
            "close_time_utc": utc(current + BAR - CLOSE_EPSILON),
            "symbol": "BTCUSDT", "timeframe": "15m",
            "open": f"{o:.8f}", "high": f"{h:.8f}", "low": f"{l:.8f}", "close": f"{c:.8f}",
            "volume": f"{1000+i:.8f}", "candle_closed": "True",
        })
        current += BAR
    with path.open("x", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(columns), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def verify_outcomes(package: Path, contracts: dict[str, Any]) -> dict[str, Any]:
    labeler = contracts["labeler"]
    validation = labeler.validate_forward_outcome_label_package(package)
    outcomes = read_json(package / "forward_outcomes.json")
    labels = outcomes["synchronized_context_outcome"]["labels"]
    statuses = {h: labels[str(h)]["label_status"] for h in (2,4,16)}
    print(f"H2_STATUS={statuses[2]}")
    print(f"H4_STATUS={statuses[4]}")
    print(f"H16_STATUS={statuses[16]}")
    if statuses != {2:"AVAILABLE",4:"AVAILABLE",16:"AVAILABLE"}:
        fail(f"REQUIRED_HORIZONS_NOT_AVAILABLE: {statuses}")
    print("ALL_PREREGISTERED_REQUIRED_HORIZONS_AVAILABLE=True")
    return validation


def offline_validate(repo: Path) -> int:
    print("=== S008 OUTCOMES + BINDING OFFLINE END-TO-END V1 ===")
    print("MODE=OFFLINE_VALIDATION_ONLY")
    print("REAL_NETWORK_REQUEST_ALLOWED=False")
    print("REAL_COHORT_MODIFICATION_ALLOWED=False")
    print("QUALITY_GATE_EVALUATED=False")
    print("EDGE_ESTABLISHED=False")
    print("SIGNAL_GENERATED=False")
    ds_before, mf_before = verify_repo(repo)
    contracts = import_contracts(repo)
    verify_s008(contracts)
    verify_retention(datetime.now(timezone.utc))
    descriptor = build_descriptor(contracts)
    def forbidden(*args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("OFFLINE_NETWORK_GUARD_TRIGGERED")
    contracts["spot"].requests.get = forbidden
    parent = EVIDENCE_ROOT / "ov"; parent.mkdir(parents=True, exist_ok=True)
    sandbox = parent / ("S008_OUT_" + uuid.uuid4().hex[:10]); sandbox.mkdir()
    print(f"OFFLINE_SANDBOX={sandbox}")
    try:
        source = sandbox / "synthetic_future_closed_candles.csv"
        write_synthetic_future_csv(source, float(descriptor["reference_price"]))
        rows = contracts["labeler"].read_future_closed_candles(source)
        if len(rows) != 24: fail("SYNTHETIC_FUTURE_ROW_COUNT_INVALID")
        print("ACTUAL_FUTURE_CANDLE_READER_EXERCISED=True")
        package = sandbox / "forward_outcome_package"
        contracts["labeler"].prepare_forward_outcome_label_package(
            repo_root=repo,
            synchronized_session_directory=INNER_SESSION,
            cycle_index=1,
            future_closed_candles_csv=source,
            output_directory=package,
            authorization=contracts["labeler"].PACKAGE_AUTHORIZATION,
        )
        verify_outcomes(package, contracts)
        print("ACTUAL_FORWARD_OUTCOME_LABELER_EXERCISED=True")
        cohort_copy = sandbox / "cohort_copy"; shutil.copytree(COHORT_ROOT, cohort_copy)
        result = contracts["cohort"].prepare_outcome_binding_v1(
            repo_root=repo,
            cohort_root=cohort_copy,
            slot_id=SLOT_ID,
            outcome_package_directory=package,
            authorization=contracts["cohort"].BINDING_AUTHORIZATION,
        )
        test_binding = Path(result["binding_directory"])
        receipt = contracts["cohort"].validate_outcome_binding_receipt_v1(test_binding)
        if receipt["observation_id"] != OBSERVATION_ID:
            fail("TEST_BINDING_OBSERVATION_ID_MISMATCH")
        print("ACTUAL_PROSPECTIVE_BINDING_LOGIC_EXERCISED=True")
        print("TEST_BINDING_RECEIPT_CREATED_AND_VALIDATED=True")
        print("TEST_REQUIRED_HORIZONS_AVAILABLE=" + ",".join(str(x) for x in receipt["required_horizons_available"]))
        if (COHORT_ROOT / "bindings" / SLOT_ID).exists():
            fail("REAL_COHORT_MODIFIED_DURING_OFFLINE_TEST")
        if git(repo, "status", "--porcelain=v1", "--untracked-files=all"):
            fail("REPOSITORY_CHANGED_DURING_OFFLINE_TEST")
        if sha256_file(repo / "data/forward/long_forward_observation_dataset_v1.csv") != ds_before:
            fail("OFFICIAL_DATASET_CHANGED")
        if sha256_file(repo / "data/forward/long_forward_observation_dataset_v1.manifest.csv") != mf_before:
            fail("OFFICIAL_MANIFEST_CHANGED")
        print("REAL_HTTP_CALLS=0")
        print("REAL_COHORT_S008_BINDING_CREATED=False")
        print("REPOSITORY_CHANGED=False")
        print("OFFICIAL_DATASET_CHANGED=False")
        print("OFFICIAL_MANIFEST_CHANGED=False")
    finally:
        if sandbox.exists(): shutil.rmtree(sandbox, ignore_errors=False)
    print("OFFLINE_SANDBOX_CLEANED=True")
    print("S008_OUTCOMES_BINDING_OFFLINE_VALIDATION_PASSED=True")
    print("DECISION=S008_OUTCOMES_BINDING_READY_FOR_ONE_SHOT_REAL_CAPTURE_AND_BIND")
    return 0


def execute(repo: Path, source_attestation: str | None) -> int:
    global NETWORK_PHASE_ENTERED
    print("=== S008 REAL OUTCOMES CAPTURE + BINDING V1 ===")
    print("MODE=REAL_SUPERVISED_FOREGROUND_OUTCOME_CAPTURE_AND_BIND")
    print("PUBLIC_READ_ONLY_MARKET_DATA_ONLY=True")
    print("AUTHENTICATED_MARKET_ENDPOINT_USED=False")
    print("ORDER_ENDPOINT_USED=False")
    print("QUALITY_GATE_EVALUATION_ALLOWED=False")
    print("SIGNAL_SEMANTICS=False")
    print("OFFICIAL_APPEND_ALLOWED=False")
    if source_attestation != SOURCE_ATTESTATION:
        fail(f"REAL_SOURCE_HUMAN_ATTESTATION_REQUIRED expected={SOURCE_ATTESTATION}")
    ds_before, mf_before = verify_repo(repo)
    contracts = import_contracts(repo)
    verify_s008(contracts)
    verify_retention(datetime.now(timezone.utc))
    build_descriptor(contracts)
    if OUTCOME_ROOT.exists() or OUTCOME_ROOT.is_symlink():
        fail(f"S008_OUTCOME_ROOT_ALREADY_EXISTS: {OUTCOME_ROOT}")
    OUTCOME_ROOT.mkdir()
    NETWORK_PHASE_ENTERED = True
    capture = contracts["spot"].capture_real_binance_public_closed_candles(
        repo_root=repo,
        output_directory=FUTURE_CAPTURE_DIR,
        authorization=contracts["spot"].REAL_CAPTURE_AUTHORIZATION,
    )
    if int(capture["network_request_count"]) != 1:
        fail("REAL_FUTURE_CAPTURE_REQUEST_COUNT_INVALID")
    source = Path(capture["source_csv"]).resolve()
    rows = contracts["labeler"].read_future_closed_candles(source)
    opens = [parse_utc(row["open_time_utc"]) for row in rows]
    if REFERENCE_BOUNDARY not in opens or CONTEXT_ANCHOR not in opens:
        fail("REAL_FUTURE_SOURCE_REQUIRED_ANCHOR_MISSING")
    bars_from_context = len(opens) - opens.index(CONTEXT_ANCHOR)
    print(f"REAL_FUTURE_CLOSED_CANDLE_ROWS={len(rows)}")
    print(f"REAL_BARS_AVAILABLE_FROM_CONTEXT_ANCHOR={bars_from_context}")
    if bars_from_context < 16:
        fail("REAL_FUTURE_SOURCE_H16_NOT_AVAILABLE")
    contracts["labeler"].prepare_forward_outcome_label_package(
        repo_root=repo,
        synchronized_session_directory=INNER_SESSION,
        cycle_index=1,
        future_closed_candles_csv=source,
        output_directory=OUTCOME_PACKAGE_DIR,
        authorization=contracts["labeler"].PACKAGE_AUTHORIZATION,
    )
    verify_outcomes(OUTCOME_PACKAGE_DIR, contracts)
    binding = contracts["cohort"].prepare_outcome_binding_v1(
        repo_root=repo,
        cohort_root=COHORT_ROOT,
        slot_id=SLOT_ID,
        outcome_package_directory=OUTCOME_PACKAGE_DIR,
        authorization=contracts["cohort"].BINDING_AUTHORIZATION,
    )
    bdir = Path(binding["binding_directory"])
    receipt = contracts["cohort"].validate_outcome_binding_receipt_v1(bdir)
    if receipt["observation_id"] != OBSERVATION_ID:
        fail("REAL_BINDING_OBSERVATION_ID_MISMATCH")
    if git(repo, "status", "--porcelain=v1", "--untracked-files=all"):
        fail("REPOSITORY_CHANGED_DURING_BINDING")
    if sha256_file(repo / "data/forward/long_forward_observation_dataset_v1.csv") != ds_before:
        fail("OFFICIAL_DATASET_CHANGED")
    if sha256_file(repo / "data/forward/long_forward_observation_dataset_v1.manifest.csv") != mf_before:
        fail("OFFICIAL_MANIFEST_CHANGED")
    summary = {
        "schema_version":"S008_OUTCOME_BINDING_EXECUTION_SUMMARY_V1",
        "slot_id":SLOT_ID,"observation_id":OBSERVATION_ID,
        "future_capture_directory":str(FUTURE_CAPTURE_DIR),
        "future_capture_network_request_count":1,
        "outcome_package_directory":str(OUTCOME_PACKAGE_DIR),
        "binding_directory":str(bdir),
        "required_horizons_available":receipt["required_horizons_available"],
        "quality_gate_evaluated":False,"edge_established":False,
        "signal_generated":False,"official_append_executed":False,
    }
    with (OUTCOME_ROOT / "outcome_binding_execution_summary.json").open(
        "x", encoding="utf-8", newline="\n"
    ) as handle:
        handle.write(
            json.dumps(
                summary, sort_keys=True, separators=(",", ":"),
                ensure_ascii=True, allow_nan=False
            ) + "\n"
        )
    print("=== S008 OUTCOME BINDING FINAL CERTIFICATION ===")
    print("SLOT_ID=S008")
    print(f"OBSERVATION_ID={OBSERVATION_ID}")
    print("REAL_FUTURE_MARKET_DATA_REQUEST_COUNT=1")
    print("FORWARD_OUTCOME_PACKAGE_CREATED=True")
    print("H2_AVAILABLE=True")
    print("H4_AVAILABLE=True")
    print("H16_AVAILABLE=True")
    print("REAL_OUTCOME_BINDING_CREATED=True")
    print("REQUIRED_HORIZONS_BOUND=" + ",".join(str(x) for x in receipt["required_horizons_available"]))
    print("OUTCOME_VALUES_USED_FOR_BINDING_SELECTION=False")
    print("QUALITY_GATE_EVALUATED=False")
    print("EDGE_ESTABLISHED=False")
    print("SIGNAL_GENERATED=False")
    print("OFFICIAL_APPEND_EXECUTED=False")
    print("OFFICIAL_DATASET_CHANGED=False")
    print("OFFICIAL_MANIFEST_CHANGED=False")
    print("DECISION=S008_PROSPECTIVE_CONTEXT_AND_MATURED_OUTCOMES_BOUND_READY_FOR_COHORT_MATERIALIZATION_LATER")
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--offline-validate", action="store_true")
    mode.add_argument("--execute", action="store_true")
    p.add_argument("--source-attestation", default=None)
    p.add_argument("--repo", default=str(Path.home()/"OpenClawProjects"/"trading-ai"))
    args = p.parse_args()
    repo = Path(args.repo).resolve()
    return offline_validate(repo) if args.offline_validate else execute(repo, args.source_attestation)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("S008_OUTCOMES_BINDING_RUNNER_STATUS=FAILED", file=sys.stderr)
        print(f"ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
        print(f"MARKET_NETWORK_PHASE_ENTERED={NETWORK_PHASE_ENTERED}", file=sys.stderr)
        if NETWORK_PHASE_ENTERED:
            print("DO_NOT_REPEAT_MARKET_CAPTURE_AUTOMATICALLY=True", file=sys.stderr)
            print("PRESERVE_EXISTING_OUTCOME_ROOT_FOR_RECOVERY=True", file=sys.stderr)
        else:
            print("NO_MARKET_CAPTURE_ATTEMPT_CONSUMED=True", file=sys.stderr)
        print("NO_RESET_NO_FORCE_NO_AMEND=True", file=sys.stderr)
        raise
