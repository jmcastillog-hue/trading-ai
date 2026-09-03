from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

EXPECTED_HEAD = "beefd785be607db17f2faa910674a8fb6268f00b"
EXPECTED_PLAN_SHA256 = (
    "b38d27f8a5eeec320e7b35c11b9c22ab663c047f9b451a218002c746d893ce0b"
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

COHORT_ID = "CONTEXT_LEVEL_A_ROTATING_DAILY_30_V1"
SLOT_ID = "S008"
EXPECTED_ANCHOR_UTC = "2026-08-30T18:00:00+00:00"

BAR = timedelta(minutes=15)
CLOSE_EPSILON = timedelta(milliseconds=1)
CAPTURE_GRACE = timedelta(seconds=5)
EARLIEST_HORIZON_BARS = 2
MINIMUM_PRE_SESSION_BUFFER_SECONDS = 120

OFFICIAL_APPEND_GATE_NAME = (
    "TRADING_AI_OFFICIAL_LONG_EVIDENCE_APPEND_ALLOWED"
)

COHORT_ROOT = (
    Path.home()
    / "TradingAI-Evidence"
    / "context_evaluation_cohorts"
    / COHORT_ID
)

RUN_PARENT = Path.home() / "TradingAI-Evidence" / "runs"
RUN_ROOT = RUN_PARENT / "S008_20260830T180000Z"

OFFLINE_PARENT = Path.home() / "TradingAI-Evidence" / "ov"

NETWORK_PHASE_ENTERED = False
SIMULATED_HTTP_CALL_COUNT = 0


def fail(message: str) -> None:
    raise RuntimeError(message)


def utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def parse_utc(value: Any) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        fail(f"TIMESTAMP_TIMEZONE_REQUIRED: {value}")
    return parsed.astimezone(timezone.utc)


def ceil_15m(value: datetime) -> datetime:
    current = value.astimezone(timezone.utc)
    floor = current.replace(
        minute=(current.minute // 15) * 15,
        second=0,
        microsecond=0,
    )
    return floor if current == floor else floor + BAR


def next_15m_capture_time(now: datetime) -> datetime:
    current = now.astimezone(timezone.utc)
    boundary = current.replace(
        minute=(current.minute // 15) * 15,
        second=0,
        microsecond=0,
    )
    target = boundary + CAPTURE_GRACE
    return target if current <= target else target + BAR


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def canonical_json_sha256(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def write_new_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(canonical_json_bytes(value))
        handle.flush()
        os.fsync(handle.fileno())


def write_new_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(value)
        handle.flush()
        os.fsync(handle.fileno())


def git(repo: Path, *args: str) -> str:
    import subprocess

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


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"JSON_MAPPING_REQUIRED: {path}")
    return value


def verify_repo(repo: Path) -> tuple[str, str]:
    if not (repo / ".git").is_dir():
        fail(f"REPOSITORY_INVALID: {repo}")

    active = git(repo, "branch", "--show-current")
    head = git(repo, "rev-parse", "HEAD")
    main = git(repo, "rev-parse", "main")
    status = git(repo, "status", "--porcelain=v1", "--untracked-files=all")

    print(f"ACTIVE_BRANCH={active}")
    print(f"HEAD={head}")
    print(f"MAIN={main}")
    print(f"WORKING_TREE_CLEAN={status == ''}")

    if active != "main":
        fail(f"ACTIVE_BRANCH_MISMATCH expected=main actual={active}")
    if head != EXPECTED_HEAD or main != EXPECTED_HEAD:
        fail(
            "REPOSITORY_BASE_MISMATCH "
            f"expected={EXPECTED_HEAD} head={head} main={main}"
        )
    if status:
        fail("WORKING_TREE_NOT_CLEAN")

    if os.environ.get(OFFICIAL_APPEND_GATE_NAME) == "1":
        fail("OFFICIAL_APPEND_GATE_ENABLED")

    dataset = repo / "data/forward/long_forward_observation_dataset_v1.csv"
    manifest = (
        repo
        / "data/forward/long_forward_observation_dataset_v1.manifest.csv"
    )
    lock = (
        repo
        / "data/forward/long_forward_observation_dataset_v1.lock"
    )

    if lock.exists() or lock.is_symlink():
        fail("OFFICIAL_LOCK_PRESENT")

    dataset_sha = sha256_file(dataset)
    manifest_sha = sha256_file(manifest)

    if dataset_sha != EXPECTED_OFFICIAL_DATASET_SHA256:
        fail("OFFICIAL_DATASET_SHA256_MISMATCH")
    if manifest_sha != EXPECTED_OFFICIAL_MANIFEST_SHA256:
        fail("OFFICIAL_MANIFEST_SHA256_MISMATCH")

    print("OFFICIAL_ARTIFACTS_UNCHANGED=True")
    print("OFFICIAL_APPEND_GATE_ENABLED=False")

    return dataset_sha, manifest_sha


def verify_cohort_plan() -> tuple[dict[str, Any], datetime]:
    if not COHORT_ROOT.is_dir() or COHORT_ROOT.is_symlink():
        fail(f"COHORT_ROOT_INVALID: {COHORT_ROOT}")

    plan = read_json(COHORT_ROOT / "cohort_plan.json")

    if plan.get("cohort_id") != COHORT_ID:
        fail("COHORT_ID_MISMATCH")

    actual_plan_sha = canonical_json_sha256(plan)
    print(f"CANONICAL_PLAN_SHA256={actual_plan_sha}")

    if actual_plan_sha != EXPECTED_PLAN_SHA256:
        fail("CANONICAL_PLAN_SHA256_MISMATCH")
    if plan.get("hypothesis_manifest_sha256") != EXPECTED_HYPOTHESIS_SHA256:
        fail("HYPOTHESIS_BINDING_MISMATCH")

    matches = [
        item
        for item in plan.get("slots", [])
        if item.get("slot_id") == SLOT_ID
    ]
    if len(matches) != 1:
        fail("S008_NOT_UNIQUELY_PREDECLARED")

    anchor = parse_utc(matches[0]["context_anchor_open_utc"])
    if utc(anchor) != EXPECTED_ANCHOR_UTC:
        fail(
            "S008_ANCHOR_MISMATCH "
            f"expected={EXPECTED_ANCHOR_UTC} actual={utc(anchor)}"
        )

    admission = COHORT_ROOT / "admissions" / SLOT_ID
    binding = COHORT_ROOT / "bindings" / SLOT_ID

    print(f"S008_ADMISSION_ALREADY_EXISTS={admission.exists()}")
    print(f"S008_BINDING_ALREADY_EXISTS={binding.exists()}")

    if admission.exists() or binding.exists():
        fail("S008_ALREADY_HAS_COHORT_ARTIFACTS")

    return plan, anchor


def path_budget_probe() -> None:
    print("=== S008 WINDOWS PATH + FILESYSTEM PROBE ===")
    print(f"REAL_RUN_ROOT={RUN_ROOT}")

    inner = (
        RUN_ROOT
        / "synchronized_session"
        / "synchronized_v1_1_session"
    )
    uuid32 = "f" * 32

    projected = {
        "spot_csv": (
            inner
            / "spot_captures"
            / f".cycle_0001.{uuid32}.tmp"
            / "btc_usdt_15m_closed_candles.csv"
        ),
        "review_packet": (
            inner
            / "reviews"
            / f".cycle_0001.{uuid32}.tmp"
            / "candidate_review_packet.json"
        ),
        "micro_summary": (
            inner
            / "microstructure"
            / f".cycle_0001.tmp-{uuid32}"
            / "microstructure_snapshot.json"
        ),
        "conservative_55_char_payload": (
            inner
            / "microstructure"
            / f".cycle_0001.tmp-{uuid32}"
            / (("x" * 55) + ".json")
        ),
    }

    maximum = 0
    for name, path in projected.items():
        length = len(str(path))
        maximum = max(maximum, length)
        print(f"PROJECTED_PATH_LENGTH[{name}]={length}")

    print(f"MAX_PROJECTED_PATH_LENGTH={maximum}")
    if maximum >= 240:
        fail(f"PATH_BUDGET_TOO_TIGHT projected={maximum}")

    if RUN_ROOT.exists() or RUN_ROOT.is_symlink():
        fail(f"REAL_RUN_ROOT_ALREADY_EXISTS: {RUN_ROOT}")

    RUN_PARENT.mkdir(parents=True, exist_ok=True)

    probe_root = RUN_PARENT / (
        ".S008_20260830T180000Z_PATH_PROBE_" + ("p" * 8)
    )
    if probe_root.exists():
        fail(f"PATH_PROBE_COLLISION: {probe_root}")

    try:
        probe_inner = (
            probe_root
            / "synchronized_session"
            / "synchronized_v1_1_session"
        )
        tests = (
            probe_inner
            / "spot_captures"
            / f".cycle_0001.{uuid32}.tmp"
            / "btc_usdt_15m_closed_candles.csv",
            probe_inner
            / "microstructure"
            / f".cycle_0001.tmp-{uuid32}"
            / (("x" * 55) + ".json"),
        )
        for path in tests:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as handle:
                handle.write(b"offline-path-probe\n")
        print("WINDOWS_REAL_FILESYSTEM_PATH_PROBE=True")
    finally:
        if probe_root.exists():
            shutil.rmtree(probe_root, ignore_errors=False)

    print("PATH_PROBE_CLEANED=True")
    print("WINDOWS_PATH_BUDGET_VALID=True")


class SyntheticClock:
    def __init__(self, value: datetime):
        self.value = value.astimezone(timezone.utc)

    def __call__(self) -> datetime:
        return self.value

    def sleep(self, seconds: float) -> None:
        self.value += timedelta(seconds=max(0.0, seconds))

    def advance(self, seconds: float) -> None:
        self.value += timedelta(seconds=seconds)


class OfflineResponse:
    def __init__(self, payload: object, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def json(self) -> object:
        return self._payload


def offline_micro_payloads(boundary: datetime) -> dict[str, object]:
    boundary_ms = int(boundary.timestamp() * 1000)
    ref_close_ms = boundary_ms - 1
    ref_open_ms = boundary_ms - 15 * 60 * 1000

    def kline(
        open_ms: int,
        close_ms: int,
        o: float,
        h: float,
        l: float,
        c: float,
        v: float,
    ) -> list[object]:
        return [
            open_ms,
            str(o),
            str(h),
            str(l),
            str(c),
            str(v),
            close_ms,
            "0",
            10,
            "0",
            "0",
            "0",
        ]

    bids = [
        [f"{65019.5 - 0.5 * i:.1f}", f"{1.0 + (i % 7) * 0.1:.1f}"]
        for i in range(1000)
    ]
    asks = [
        [f"{65020.5 + 0.5 * i:.1f}", f"{0.9 + (i % 5) * 0.1:.1f}"]
        for i in range(1000)
    ]

    return {
        "/fapi/v1/klines": [
            kline(
                ref_open_ms - 15 * 60 * 1000,
                ref_open_ms - 1,
                64900,
                65000,
                64880,
                64980,
                100,
            ),
            kline(
                ref_open_ms,
                ref_close_ms,
                64980,
                65050,
                64970,
                65020,
                120,
            ),
            kline(
                boundary_ms,
                boundary_ms + 15 * 60 * 1000 - 1,
                65020,
                65030,
                65010,
                65025,
                5,
            ),
        ],
        "/fapi/v1/depth": {
            "lastUpdateId": 123,
            "E": boundary_ms + 2000,
            "T": boundary_ms + 1900,
            "bids": bids,
            "asks": asks,
        },
        "/fapi/v1/openInterest": {
            "openInterest": "12000",
            "symbol": "BTCUSDT",
            "time": boundary_ms + 2500,
        },
        "/fapi/v1/premiumIndex": {
            "symbol": "BTCUSDT",
            "markPrice": "65020",
            "indexPrice": "65000",
            "estimatedSettlePrice": "0",
            "lastFundingRate": "0.0001",
            "interestRate": "0.0001",
            "nextFundingTime": boundary_ms + 8 * 60 * 60 * 1000,
            "time": boundary_ms + 2600,
        },
        "/futures/data/openInterestHist": [
            {
                "symbol": "BTCUSDT",
                "sumOpenInterest": "11800",
                "sumOpenInterestValue": "767000000",
                "CMCCirculatingSupply": "0",
                "timestamp": boundary_ms - 15 * 60 * 1000,
            },
            {
                "symbol": "BTCUSDT",
                "sumOpenInterest": "12000",
                "sumOpenInterestValue": "780000000",
                "CMCCirculatingSupply": "0",
                "timestamp": boundary_ms,
            },
        ],
        "/futures/data/takerlongshortRatio": [
            {
                "buySellRatio": "0.9",
                "buyVol": "90",
                "sellVol": "100",
                "timestamp": boundary_ms - 30 * 60 * 1000,
            },
            {
                "buySellRatio": "1.2",
                "buyVol": "120",
                "sellVol": "100",
                "timestamp": boundary_ms - 15 * 60 * 1000,
            },
        ],
        "/futures/data/globalLongShortAccountRatio": [
            {
                "symbol": "BTCUSDT",
                "longShortRatio": "1.1",
                "longAccount": "0.5238",
                "shortAccount": "0.4762",
                "timestamp": boundary_ms - 15 * 60 * 1000,
            },
            {
                "symbol": "BTCUSDT",
                "longShortRatio": "1.2",
                "longAccount": "0.5455",
                "shortAccount": "0.4545",
                "timestamp": boundary_ms,
            },
        ],
    }


class OfflineMockGet:
    def __init__(self, payloads: dict[str, object]):
        self.payloads = payloads
        self.calls: list[str] = []

    def __call__(self, url: str, *, params: dict[str, object], timeout: int):
        global SIMULATED_HTTP_CALL_COUNT
        path = urlparse(url).path
        self.calls.append(path)
        SIMULATED_HTTP_CALL_COUNT += 1
        if path not in self.payloads:
            return OfflineResponse({"error": "unexpected path"}, 500)
        return OfflineResponse(self.payloads[path], 200)


def import_contracts(repo: Path) -> dict[str, Any]:
    sys.path.insert(0, str(repo))

    from src.exchange import long_primary_public_closed_candle_capture_v1 as spot
    from src.exchange import public_read_only_microstructure_snapshot_v1_1 as micro
    from src.long_side import forward_outcome_labeler_v1 as labeler
    from src.long_side import (
        synchronized_15m_observation_v1_1_microstructure_auth_propagation_v1
        as propagation
    )
    from src.context import liquidity_sweep_pattern_context_v1 as liq
    from src.context import synchronized_microstructure_context_v1 as microctx
    from src.context import context_feature_pack_v1_level_a_standard as pack
    from src.evaluation import context_evaluation_prospective_cohort_v1 as cohort

    return {
        "spot": spot,
        "micro": micro,
        "labeler": labeler,
        "propagation": propagation,
        "liq": liq,
        "microctx": microctx,
        "pack": pack,
        "cohort": cohort,
    }


def forbid_accidental_real_network(contracts: dict[str, Any]) -> None:
    def forbidden(*args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("OFFLINE_NETWORK_GUARD_TRIGGERED")

    contracts["spot"].requests.get = forbidden
    contracts["micro"].requests.get = forbidden


def offline_spot_capture_factory(
    contracts: dict[str, Any],
    clock: SyntheticClock,
    expected_close: datetime,
):
    spot = contracts["spot"]

    def capture(
        *,
        repo_root: Path | str,
        output_directory: Path | str,
        authorization: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        if authorization != spot.REAL_CAPTURE_AUTHORIZATION:
            fail("OFFLINE_SPOT_AUTHORIZATION_MISMATCH")

        repo = Path(repo_root).resolve()
        output = Path(output_directory).resolve()

        if output.exists() or output.is_symlink():
            fail("OFFLINE_SPOT_OUTPUT_EXISTS")
        if not output.parent.is_dir():
            fail("OFFLINE_SPOT_PARENT_INVALID")

        rows: list[dict[str, str]] = []
        first_close = expected_close - BAR * 63

        for index in range(64):
            close_time = first_close + BAR * index
            open_time = close_time - BAR + CLOSE_EPSILON
            base = 64000.0 + index * 3.0
            rows.append(
                {
                    "open_time_utc": utc(open_time),
                    "close_time_utc": utc(close_time),
                    "symbol": "BTCUSDT",
                    "timeframe": "15m",
                    "open": f"{base:.2f}",
                    "high": f"{base + 15:.2f}",
                    "low": f"{base - 15:.2f}",
                    "close": f"{base + 3:.2f}",
                    "volume": f"{100 + index:.2f}",
                    "candle_closed": "True",
                }
            )

        temporary = output.parent / (
            f".{output.name}.{uuid.uuid4().hex}.tmp"
        )

        try:
            temporary.mkdir()

            source = temporary / spot.SOURCE_FILENAME
            with source.open(
                "x",
                encoding="utf-8",
                newline="",
            ) as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=list(spot.SOURCE_COLUMNS),
                    lineterminator="\n",
                )
                writer.writeheader()
                writer.writerows(rows)

            source_sha = sha256_file(source)
            captured_at = clock()

            metadata = {
                "capture_schema_version": spot.CAPTURE_SCHEMA_VERSION,
                "capability": spot.CAPABILITY,
                "implementation_schema_version":
                    spot.IMPLEMENTATION_SCHEMA_VERSION,
                "capture_id": "OFFLINE_SPOT_S008",
                "capture_mode": "ONE_SHOT_FOREGROUND",
                "provider": spot.PROVIDER,
                "endpoint": "OFFLINE_MOCK_NO_NETWORK",
                "symbol": spot.EXPECTED_SYMBOL,
                "timeframe": spot.EXPECTED_TIMEFRAME,
                "request_limit": spot.REQUEST_LIMIT,
                "network_request_count": 1,
                "captured_at_utc": utc(captured_at),
                "closed_candle_rows": len(rows),
                "open_candles_excluded": 0,
                "latest_closed_candle_utc": utc(expected_close),
                "source_artifact": spot.SOURCE_FILENAME,
                "source_artifact_sha256": source_sha,
                "source_columns": list(spot.SOURCE_COLUMNS),
                "latest_candle_only_future_evaluation_contract": True,
                "lookahead_used": False,
                "automatic_or_recurring_capture": False,
                "review_package_created": False,
                "candidate_evaluated": False,
                "candidate_detected": False,
                "manual_confirmation_required": True,
                "manual_confirmed": False,
                "official_dataset_write_allowed": False,
                "official_append_allowed": False,
                "signal_generation_enabled": False,
                "live_alerts_allowed": False,
                "paper_trade_execution_allowed": False,
                "real_capital_allowed": False,
                "market_execution_allowed": False,
                "exchange_execution_allowed": False,
                "automation_allowed": False,
                "execution_allowed": False,
            }

            write_new_json(
                temporary / spot.METADATA_FILENAME,
                metadata,
            )

            manifest_lines = []
            for name in (
                spot.SOURCE_FILENAME,
                spot.METADATA_FILENAME,
            ):
                manifest_lines.append(
                    f"{sha256_file(temporary / name)}  {name}"
                )
            write_new_text(
                temporary / spot.MANIFEST_FILENAME,
                "\n".join(sorted(manifest_lines)) + "\n",
            )

            spot.validate_closed_candle_capture(temporary)
            print("OFFLINE_SPOT_METADATA_CONTRACT_VALIDATED=True")
            os.replace(temporary, output)
        except Exception:
            if temporary.exists():
                shutil.rmtree(temporary, ignore_errors=True)
            raise

        validation = spot.validate_closed_candle_capture(output)

        return {
            "capability": spot.CAPABILITY,
            "capture_id": "OFFLINE_SPOT_S008",
            "output_directory": str(output),
            "source_csv": str(output / spot.SOURCE_FILENAME),
            "metadata_json": str(output / spot.METADATA_FILENAME),
            "source_artifact_sha256":
                sha256_file(output / spot.SOURCE_FILENAME),
            "closed_candle_rows": 64,
            "open_candles_excluded": 0,
            "latest_closed_candle_utc": utc(expected_close),
            "network_request_count": 1,
            "one_shot_foreground": True,
            "review_package_created": False,
            "candidate_evaluated": False,
            "candidate_detected": False,
            "manual_confirmation_required": True,
            "manual_confirmed": False,
            "official_dataset_write_performed": False,
            "official_manifest_write_performed": False,
            "official_append_invoked": False,
            "official_append_environment_gate_modified": False,
            "signal_generation_enabled": False,
            "live_alerts_allowed": False,
            "paper_trade_execution_allowed": False,
            "real_capital_allowed": False,
            "market_execution_allowed": False,
            "exchange_execution_allowed": False,
            "automation_allowed": False,
            "execution_allowed": False,
            "capture_manifest_entries": validation["manifest_entries"],
        }

    return capture


def offline_micro_capture_factory(
    contracts: dict[str, Any],
    clock: SyntheticClock,
    boundary: datetime,
):
    micro = contracts["micro"]
    payloads = offline_micro_payloads(boundary)
    mock_get = OfflineMockGet(payloads)

    def capture(
        *,
        repo_root: Path | str,
        output_directory: Path | str,
        authorization: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        clock.advance(0.500)
        return micro.capture_public_read_only_microstructure_snapshot_v1_1(
            repo_root=repo_root,
            output_directory=output_directory,
            authorization=authorization,
            request_get=mock_get,
            clock=clock,
        )

    capture.mock_get = mock_get  # type: ignore[attr-defined]
    return capture


def offline_human_context(latest: dict[str, Any]) -> dict[str, Any]:
    return {
        "context_only": True,
        "actionable_signal_generated": False,
        "positional_state": "OFFLINE_VALIDATION",
        "latest_candle_direction": "UNSPECIFIED",
    }


def placeholder_components(pack_module: Any) -> dict[str, dict[str, Any]]:
    values: dict[str, dict[str, Any]] = {}
    for item in pack_module.FEATURE_REGISTRY:
        feature_id = str(item["feature_id"])
        values[feature_id] = {
            "feature_id": feature_id,
            "source_kind": str(item["source_kind"]),
            "feature_schema_version":
                feature_id + "_PLACEHOLDER_SCHEMA_V1",
            "status": "NOT_CONFIGURED",
            "reason":
                "NOT_CONFIGURED_FOR_INITIAL_PROSPECTIVE_COHORT_CAPTURE_V1",
            "available_at_utc": None,
            "information_cutoff_utc": None,
            "source_artifact_sha256": None,
            "payload": None,
        }
    return values


def run_post_session_pipeline(
    *,
    repo: Path,
    contracts: dict[str, Any],
    outer_session: Path,
    work_root: Path,
    cohort_root: Path,
    offline_admitted_at: datetime | None,
    offline_produced_at: datetime | None,
) -> dict[str, Any]:
    propagation = contracts["propagation"]
    labeler = contracts["labeler"]
    liq = contracts["liq"]
    microctx = contracts["microctx"]
    pack_module = contracts["pack"]
    cohort = contracts["cohort"]

    outer_validation = propagation.validate_authorization_propagation_session_v1(
        outer_session
    )
    if int(outer_validation["completed_cycles"]) != 1:
        fail("OUTER_SESSION_COMPLETED_CYCLES_INVALID")
    if int(outer_validation["authorization_propagation_count"]) != 1:
        fail("AUTHORIZATION_PROPAGATION_COUNT_INVALID")

    inner_session = outer_session / propagation.INNER_SESSION_DIRECTORY
    if not inner_session.is_dir():
        fail("INNER_SESSION_DIRECTORY_MISSING")

    descriptor = labeler.build_observation_descriptor_from_synchronized_session(
        synchronized_session_directory=inner_session,
        cycle_index=1,
    )

    descriptor_path = work_root / "observation_descriptor.json"
    write_new_json(descriptor_path, descriptor)

    anchor = parse_utc(EXPECTED_ANCHOR_UTC)
    context_cutoff = parse_utc(
        descriptor["synchronized_context_available_at_utc"]
    )
    derived_anchor = ceil_15m(context_cutoff)

    print(f"DESCRIPTOR_OBSERVATION_ID={descriptor['observation_id']}")
    print(
        "DESCRIPTOR_REFERENCE_CLOSED_CANDLE_UTC="
        + descriptor["reference_closed_candle_utc"]
    )
    print(
        "DESCRIPTOR_CONTEXT_CUTOFF_UTC="
        + descriptor["synchronized_context_available_at_utc"]
    )
    print(f"DERIVED_CONTEXT_ANCHOR_OPEN_UTC={utc(derived_anchor)}")

    if derived_anchor != anchor:
        fail(
            "S008_DERIVED_ANCHOR_MISMATCH "
            f"expected={utc(anchor)} actual={utc(derived_anchor)}"
        )

    components_root = work_root / "component_packages"
    components_root.mkdir()

    liq_dir = components_root / "liquidity_sweep"
    microctx_dir = components_root / "microstructure"

    if offline_produced_at is not None:
        produced_liq = offline_produced_at
    else:
        produced_liq = datetime.now(timezone.utc)

    if produced_liq < context_cutoff:
        fail(
            "LIQUIDITY_PRODUCED_AT_BEFORE_CONTEXT_CUTOFF "
            f"produced={utc(produced_liq)} cutoff={utc(context_cutoff)}"
        )

    liq.prepare_liquidity_sweep_pattern_context_v1_package(
        repo_root=repo,
        observation_descriptor_json=descriptor_path,
        closed_candle_capture_directory=(
            inner_session / "spot_captures" / "cycle_0001"
        ),
        output_directory=liq_dir,
        produced_at_utc=utc(produced_liq),
        authorization=liq.PACKAGE_AUTHORIZATION,
    )
    liq_validation = liq.validate_liquidity_sweep_pattern_context_v1_package(
        liq_dir
    )

    if offline_produced_at is not None:
        produced_micro = offline_produced_at + timedelta(milliseconds=1)
    else:
        produced_micro = datetime.now(timezone.utc)

    if produced_micro < context_cutoff:
        fail(
            "MICROSTRUCTURE_PRODUCED_AT_BEFORE_CONTEXT_CUTOFF "
            f"produced={utc(produced_micro)} cutoff={utc(context_cutoff)}"
        )

    microctx.prepare_synchronized_microstructure_context_v1_package(
        repo_root=repo,
        observation_descriptor_json=descriptor_path,
        microstructure_snapshot_directory=(
            inner_session / "microstructure" / "cycle_0001"
        ),
        output_directory=microctx_dir,
        produced_at_utc=utc(produced_micro),
        authorization=microctx.PACKAGE_AUTHORIZATION,
    )
    micro_validation = (
        microctx.validate_synchronized_microstructure_context_v1_package(
            microctx_dir
        )
    )

    if not liq_validation["point_in_time_eligible_under_pack_policy"]:
        fail("LIQUIDITY_COMPONENT_NOT_POINT_IN_TIME_ELIGIBLE")
    if not micro_validation["point_in_time_eligible_under_pack_policy"]:
        fail("MICROSTRUCTURE_COMPONENT_NOT_POINT_IN_TIME_ELIGIBLE")

    components = placeholder_components(pack_module)
    components["LIQUIDITY_SWEEP_PATTERN_CONTEXT_V1"] = read_json(
        liq_dir / liq.COMPONENT_FILENAME
    )
    components["SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1"] = read_json(
        microctx_dir / microctx.COMPONENT_FILENAME
    )

    components_path = work_root / "components.json"
    write_new_json(components_path, components)

    pack_dir = work_root / "context_feature_pack"
    pack_module.prepare_context_feature_pack_v1_package(
        repo_root=repo,
        observation_descriptor_json=descriptor_path,
        components_json=components_path,
        output_directory=pack_dir,
        authorization=pack_module.PACKAGE_AUTHORIZATION,
        pack_id="CTXPACK_S008_20260830T180000Z",
    )

    pack_validation = pack_module.validate_context_feature_pack_v1_package(
        pack_dir
    )
    pack_value = read_json(pack_dir / pack_module.PACK_FILENAME)

    print(
        "PACK_POINT_IN_TIME_ELIGIBLE_FEATURE_COUNT="
        + str(pack_validation["point_in_time_eligible_feature_count"])
    )
    print(
        "PACK_CONTEXT_ANCHOR_OPEN_UTC="
        + pack_validation["context_anchor_open_utc"]
    )

    if int(pack_validation["point_in_time_eligible_feature_count"]) != 2:
        fail("PACK_ELIGIBLE_FEATURE_COUNT_INVALID")
    if pack_validation["context_anchor_open_utc"] != EXPECTED_ANCHOR_UTC:
        fail("PACK_S008_ANCHOR_MISMATCH")

    eligible_ids = [
        item["feature_id"]
        for item in pack_value["features"]
        if item["point_in_time_eligible"]
    ]
    if eligible_ids != [
        "LIQUIDITY_SWEEP_PATTERN_CONTEXT_V1",
        "SYNCHRONIZED_MICROSTRUCTURE_CONTEXT_V1",
    ]:
        fail(f"PACK_ELIGIBLE_FEATURE_IDS_INVALID: {eligible_ids}")

    original_now = None
    if offline_admitted_at is not None:
        original_now = cohort._now_utc
        cohort._now_utc = lambda: offline_admitted_at

    try:
        admission_result = cohort.prepare_context_admission_v1(
            repo_root=repo,
            cohort_root=cohort_root,
            context_pack_directory=pack_dir,
            authorization=cohort.ADMISSION_AUTHORIZATION,
        )
    finally:
        if original_now is not None:
            cohort._now_utc = original_now

    admission_dir = Path(admission_result["admission_directory"])
    receipt = cohort.validate_admission_receipt_v1(admission_dir)

    if admission_result["slot_id"] != SLOT_ID:
        fail("ADMISSION_SLOT_ID_MISMATCH")
    if receipt["context_anchor_open_utc"] != EXPECTED_ANCHOR_UTC:
        fail("ADMISSION_ANCHOR_MISMATCH")

    return {
        "inner_session": inner_session,
        "descriptor": descriptor,
        "context_cutoff": context_cutoff,
        "pack_dir": pack_dir,
        "admission_result": admission_result,
        "eligible_ids": eligible_ids,
        "outer_validation": outer_validation,
    }


def offline_validate(repo: Path) -> int:
    global SIMULATED_HTTP_CALL_COUNT
    SIMULATED_HTTP_CALL_COUNT = 0

    print("=== S008 COMPLETE OFFLINE END-TO-END VALIDATION V1.1 ===")
    print("RUNNER_REPAIR_ATTEMPT=1_OF_10")
    print("REPAIR_1=OFFLINE_SPOT_METADATA_LATEST_CLOSED_CANDLE_UTC")
    print("REPAIR_2=REAL_PRODUCER_TIMESTAMPS_USE_ACTUAL_WALL_CLOCK")
    print("MODE=OFFLINE_END_TO_END")
    print("REAL_NETWORK_REQUEST_ALLOWED=False")
    print("REAL_MARKET_DATA_REQUEST_ALLOWED=False")
    print("REAL_COHORT_MODIFICATION_ALLOWED=False")
    print("FORWARD_OUTCOMES_READ=False")
    print("QUALITY_GATE_EVALUATED=False")
    print("SIGNAL_GENERATED=False")

    dataset_before, manifest_before = verify_repo(repo)
    plan, anchor = verify_cohort_plan()
    path_budget_probe()

    contracts = import_contracts(repo)
    forbid_accidental_real_network(contracts)

    propagation = contracts["propagation"]
    if propagation.MICROSTRUCTURE_V1_1_AUTHORIZATION != (
        contracts["micro"].AUTHORIZATION
    ):
        fail("MICROSTRUCTURE_AUTHORIZATION_CONTRACT_MISMATCH")

    print("MICROSTRUCTURE_AUTHORIZATION_PROPAGATION_CONTRACT_VERIFIED=True")

    reference_boundary = anchor - BAR
    reference_close = reference_boundary - CLOSE_EPSILON

    start = reference_boundary - timedelta(minutes=10)
    clock = SyntheticClock(start)

    spot_capture = offline_spot_capture_factory(
        contracts,
        clock,
        reference_close,
    )
    micro_capture = offline_micro_capture_factory(
        contracts,
        clock,
        reference_boundary,
    )

    OFFLINE_PARENT.mkdir(parents=True, exist_ok=True)
    sandbox = OFFLINE_PARENT / (
        "S008_" + uuid.uuid4().hex[:10]
    )
    if sandbox.exists():
        fail("OFFLINE_SANDBOX_COLLISION")

    sandbox.mkdir()
    print(f"OFFLINE_SANDBOX={sandbox}")

    try:
        outer_session = sandbox / "s"
        session_result = (
            propagation
            .run_bounded_synchronized_15m_session_with_microstructure_auth_propagation_v1(
                repo_root=repo,
                output_directory=outer_session,
                max_cycles=1,
                source_attestation=(
                    "REAL_MARKET_DATA_SOURCE_HUMAN_ATTESTED_NOT_SYNTHETIC"
                ),
                minimum_latest_closed_candle_utc=utc(
                    reference_close - BAR
                ),
                authorization=propagation.SESSION_AUTHORIZATION,
                clock=clock,
                sleeper=clock.sleep,
                spot_capture_callable=spot_capture,
                package_callable=None,
                microstructure_capture_callable=micro_capture,
                microstructure_validate_callable=None,
                human_context_callable=offline_human_context,
            )
        )

        if int(session_result["completed_cycles"]) != 1:
            fail("OFFLINE_SESSION_COMPLETED_CYCLES_INVALID")
        if int(session_result["network_request_count"]) != 8:
            fail("OFFLINE_SESSION_NETWORK_CONTRACT_INVALID")

        print("ACTUAL_SYNCHRONIZED_SESSION_LOGIC_EXERCISED=True")
        print("ACTUAL_REVIEW_PACKAGE_LOGIC_EXERCISED=True")
        print("ACTUAL_AUTH_PROPAGATION_WRAPPER_EXERCISED=True")
        print("ACTUAL_MICROSTRUCTURE_PRODUCER_LOGIC_EXERCISED_WITH_FAKE_HTTP=True")
        print("ACTUAL_SPOT_FILE_LAYOUT_EXERCISED_WITH_OFFLINE_SOURCE=True")

        test_cohort_parent = sandbox / "cohort"
        test_cohort_parent.mkdir()
        test_cohort_root = test_cohort_parent / COHORT_ID

        cohort = contracts["cohort"]
        plan_path = (
            repo
            / "research"
            / "context_evaluation"
            / "context_evaluation_concrete_cohort_plan_v1.json"
        )

        cohort.initialize_prospective_cohort_v1(
            repo_root=repo,
            plan_json=plan_path,
            cohort_root=test_cohort_root,
            authorization=cohort.INITIALIZE_AUTHORIZATION,
        )

        context_cutoff_expected = clock()
        offline_admitted_at = context_cutoff_expected + timedelta(minutes=1)

        result = run_post_session_pipeline(
            repo=repo,
            contracts=contracts,
            outer_session=outer_session,
            work_root=sandbox / "post",
            cohort_root=test_cohort_root,
            offline_admitted_at=offline_admitted_at,
            offline_produced_at=context_cutoff_expected + timedelta(seconds=1),
        )

        print("OBSERVATION_DESCRIPTOR_BUILT=True")
        print("LIQUIDITY_SWEEP_PACKAGE_BUILT_AND_VALIDATED=True")
        print("SYNCHRONIZED_MICROSTRUCTURE_PACKAGE_BUILT_AND_VALIDATED=True")
        print("CONTEXT_FEATURE_PACK_BUILT_AND_VALIDATED=True")
        print("S008_EXACT_ANCHOR_MATCH=True")
        print("TEST_COHORT_INITIALIZED=True")
        print("TEST_ADMISSION_RECEIPT_CREATED_AND_VALIDATED=True")
        print(
            "TEST_ADMISSION_SLOT_ID="
            + result["admission_result"]["slot_id"]
        )

        if SIMULATED_HTTP_CALL_COUNT != 7:
            fail(
                "SIMULATED_HTTP_CALL_COUNT_INVALID "
                f"expected=7 actual={SIMULATED_HTTP_CALL_COUNT}"
            )

        print(f"SIMULATED_IN_MEMORY_HTTP_CALLS={SIMULATED_HTTP_CALL_COUNT}")
        print("REAL_HTTP_CALLS=0")

        if git(repo, "status", "--porcelain=v1", "--untracked-files=all"):
            fail("REPOSITORY_CHANGED_DURING_OFFLINE_VALIDATION")

        if sha256_file(
            repo / "data/forward/long_forward_observation_dataset_v1.csv"
        ) != dataset_before:
            fail("OFFICIAL_DATASET_CHANGED_DURING_OFFLINE_VALIDATION")

        if sha256_file(
            repo
            / "data/forward/long_forward_observation_dataset_v1.manifest.csv"
        ) != manifest_before:
            fail("OFFICIAL_MANIFEST_CHANGED_DURING_OFFLINE_VALIDATION")

        print("REPOSITORY_CHANGED=False")
        print("OFFICIAL_DATASET_CHANGED=False")
        print("OFFICIAL_MANIFEST_CHANGED=False")
        print("REAL_COHORT_S008_ADMISSION_CREATED=False")
        print("REAL_OUTCOME_BINDING_CREATED=False")
        print("FORWARD_OUTCOMES_READ=False")
        print("QUALITY_GATE_EVALUATED=False")
        print("EDGE_ESTABLISHED=False")
        print("SIGNAL_GENERATED=False")

    finally:
        if sandbox.exists():
            shutil.rmtree(sandbox, ignore_errors=False)

    print("OFFLINE_SANDBOX_CLEANED=True")
    print("S008_COMPLETE_OFFLINE_END_TO_END_VALIDATION_PASSED=True")
    print(
        "DECISION="
        "S008_RUNNER_OFFLINE_END_TO_END_VALIDATED_READY_FOR_FINAL_PRECHECK"
    )
    print(
        "NEXT_STEP="
        "RUN_FINAL_PREFLIGHT_INSIDE_S008_EXECUTION_WINDOW_THEN_EXECUTE_ONCE"
    )
    return 0


def execute_real(repo: Path, source_attestation: str | None) -> int:
    global NETWORK_PHASE_ENTERED

    print("=== EXECUTE CONTEXT EVALUATION SLOT S008 V1 ===")
    print("MODE=REAL_SUPERVISED_FOREGROUND_SLOT_CAPTURE")
    print("PUBLIC_READ_ONLY_MARKET_DATA_ONLY=True")
    print("AUTHENTICATED_MARKET_ENDPOINT_USED=False")
    print("ORDER_ENDPOINT_USED=False")
    print("OFFICIAL_APPEND_ALLOWED=False")
    print("FORWARD_OUTCOME_READ_ALLOWED=False")
    print("QUALITY_GATE_EVALUATION_ALLOWED=False")
    print("SIGNAL_SEMANTICS=False")

    dataset_before, manifest_before = verify_repo(repo)
    _, anchor = verify_cohort_plan()
    path_budget_probe()

    contracts = import_contracts(repo)
    propagation = contracts["propagation"]

    expected_attestation = (
        "REAL_MARKET_DATA_SOURCE_HUMAN_ATTESTED_NOT_SYNTHETIC"
    )
    if source_attestation != expected_attestation:
        fail(
            "REAL_SOURCE_HUMAN_ATTESTATION_REQUIRED "
            f"expected={expected_attestation}"
        )
    print("REAL_SOURCE_HUMAN_ATTESTATION_VERIFIED=True")

    if propagation.MICROSTRUCTURE_V1_1_AUTHORIZATION != (
        contracts["micro"].AUTHORIZATION
    ):
        fail("MICROSTRUCTURE_AUTHORIZATION_CONTRACT_MISMATCH")

    print("MICROSTRUCTURE_AUTHORIZATION_PROPAGATION_CONTRACT_VERIFIED=True")

    reference_boundary = anchor - BAR
    reference_close = reference_boundary - CLOSE_EPSILON
    required_capture_target = reference_boundary + CAPTURE_GRACE
    previous_capture_target = required_capture_target - BAR
    admission_deadline = anchor + BAR * EARLIEST_HORIZON_BARS

    now = datetime.now(timezone.utc)
    next_target = next_15m_capture_time(now)

    print(f"NOW_UTC={utc(now)}")
    print(f"CONTEXT_ANCHOR_OPEN_UTC={utc(anchor)}")
    print(f"REQUIRED_CAPTURE_TARGET_UTC={utc(required_capture_target)}")
    print(f"EXECUTION_WINDOW_OPENS_AFTER_UTC={utc(previous_capture_target)}")
    print(f"EXECUTION_WINDOW_CLOSES_AT_UTC={utc(required_capture_target)}")
    print(f"ADMISSION_DEADLINE_UTC={utc(admission_deadline)}")
    print(f"NEXT_SYNCHRONIZED_CAPTURE_TARGET_UTC={utc(next_target)}")

    if not (previous_capture_target < now <= required_capture_target):
        fail("EXECUTION_OUTSIDE_S008_FROZEN_WINDOW")
    if next_target != required_capture_target:
        fail("NEXT_CAPTURE_TARGET_MISMATCH")

    seconds_to_target = (
        required_capture_target - now
    ).total_seconds()
    print(f"SECONDS_TO_CAPTURE_TARGET={seconds_to_target:.3f}")
    print(
        "MINIMUM_PRE_SESSION_BUFFER_SECONDS="
        + str(MINIMUM_PRE_SESSION_BUFFER_SECONDS)
    )
    if seconds_to_target < MINIMUM_PRE_SESSION_BUFFER_SECONDS:
        fail("INSUFFICIENT_PRE_SESSION_BUFFER")

    if RUN_ROOT.exists() or RUN_ROOT.is_symlink():
        fail(f"RUN_ROOT_ALREADY_EXISTS: {RUN_ROOT}")

    RUN_PARENT.mkdir(parents=True, exist_ok=True)
    RUN_ROOT.mkdir()

    outer_session = RUN_ROOT / "synchronized_session"

    NETWORK_PHASE_ENTERED = True

    session_result = (
        propagation
        .run_bounded_synchronized_15m_session_with_microstructure_auth_propagation_v1(
            repo_root=repo,
            output_directory=outer_session,
            max_cycles=1,
            source_attestation=source_attestation,
            minimum_latest_closed_candle_utc=utc(reference_close - BAR),
            authorization=propagation.SESSION_AUTHORIZATION,
        )
    )

    if int(session_result["completed_cycles"]) != 1:
        fail("REAL_SESSION_COMPLETED_CYCLES_INVALID")
    if int(session_result["network_request_count"]) != 8:
        fail("REAL_SESSION_REQUEST_COUNT_INVALID")

    result = run_post_session_pipeline(
        repo=repo,
        contracts=contracts,
        outer_session=outer_session,
        work_root=RUN_ROOT / "post",
        cohort_root=COHORT_ROOT,
        offline_admitted_at=None,
        offline_produced_at=None,
    )

    admitted_at = parse_utc(
        result["admission_result"]["admitted_at_utc"]
    )
    if admitted_at >= admission_deadline:
        fail("ADMISSION_NOT_BEFORE_H2_DEADLINE")

    summary = {
        "schema_version":
            "CONTEXT_EVALUATION_PROSPECTIVE_SLOT_EXECUTION_SUMMARY_V1",
        "cohort_id": COHORT_ID,
        "slot_id": SLOT_ID,
        "observation_id": result["descriptor"]["observation_id"],
        "context_anchor_open_utc": utc(anchor),
        "context_cutoff_utc": utc(result["context_cutoff"]),
        "admitted_at_utc":
            result["admission_result"]["admitted_at_utc"],
        "available_component_ids": result["eligible_ids"],
        "real_market_data_request_count": 8,
        "forward_outcomes_read": False,
        "outcome_binding_created": False,
        "quality_gate_evaluated": False,
        "edge_established": False,
        "signal_generated": False,
        "official_append_executed": False,
        "official_dataset_changed": False,
        "official_manifest_changed": False,
    }
    write_new_json(RUN_ROOT / "slot_execution_summary.json", summary)

    if git(repo, "status", "--porcelain=v1", "--untracked-files=all"):
        fail("REPOSITORY_CHANGED_DURING_REAL_SLOT")

    if sha256_file(
        repo / "data/forward/long_forward_observation_dataset_v1.csv"
    ) != dataset_before:
        fail("OFFICIAL_DATASET_CHANGED_DURING_REAL_SLOT")

    if sha256_file(
        repo
        / "data/forward/long_forward_observation_dataset_v1.manifest.csv"
    ) != manifest_before:
        fail("OFFICIAL_MANIFEST_CHANGED_DURING_REAL_SLOT")

    print("=== S008 FINAL CERTIFICATION ===")
    print("SLOT_ID=S008")
    print("SYNCHRONIZED_SESSION_COMPLETED=True")
    print("MICROSTRUCTURE_AUTHORIZATION_PROPAGATED=True")
    print("REAL_MARKET_DATA_REQUEST_COUNT=8")
    print("CONTEXT_ANCHOR_EXACT_MATCH=True")
    print("LIQUIDITY_SWEEP_POINT_IN_TIME_ELIGIBLE=True")
    print("SYNCHRONIZED_MICROSTRUCTURE_POINT_IN_TIME_ELIGIBLE=True")
    print("OTHER_LEVEL_A_COMPONENTS_NOT_CONFIGURED=True")
    print("REAL_ADMISSION_RECEIPT_CREATED=True")
    print("REAL_OUTCOME_BINDING_CREATED=False")
    print("FORWARD_OUTCOMES_READ=False")
    print("QUALITY_GATE_EVALUATED=False")
    print("EDGE_ESTABLISHED=False")
    print("SIGNAL_GENERATED=False")
    print("OFFICIAL_APPEND_EXECUTED=False")
    print("OFFICIAL_DATASET_CHANGED=False")
    print("OFFICIAL_MANIFEST_CHANGED=False")
    print(
        "DECISION="
        "S008_CAPTURED_CONTEXT_PACKED_AND_PROSPECTIVELY_ADMITTED"
    )
    print(
        "NEXT_STEP="
        "WAIT_FOR_H16_MATURITY_THEN_PREPARE_FUTURE_OUTCOME_CAPTURE"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--offline-validate", action="store_true")
    mode.add_argument("--execute", action="store_true")
    parser.add_argument(
        "--source-attestation",
        default=None,
    )
    parser.add_argument(
        "--repo",
        default=str(
            Path.home()
            / "OpenClawProjects"
            / "trading-ai"
        ),
    )
    args = parser.parse_args()

    repo = Path(args.repo).resolve()

    if args.offline_validate:
        return offline_validate(repo)

    return execute_real(repo, args.source_attestation)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("S008_RUNNER_STATUS=FAILED", file=sys.stderr)
        print(
            f"ERROR={type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        print(
            f"MARKET_NETWORK_PHASE_ENTERED={NETWORK_PHASE_ENTERED}",
            file=sys.stderr,
        )
        if NETWORK_PHASE_ENTERED:
            print(
                "DO_NOT_REPEAT_MARKET_CAPTURE_AUTOMATICALLY=True",
                file=sys.stderr,
            )
            print(
                "PRESERVE_PARTIAL_RUN_ROOT_FOR_RECOVERY=True",
                file=sys.stderr,
            )
        else:
            print(
                "NO_MARKET_CAPTURE_ATTEMPT_CONSUMED=True",
                file=sys.stderr,
            )
        print("NO_RESET_NO_FORCE_NO_AMEND=True", file=sys.stderr)
        raise
