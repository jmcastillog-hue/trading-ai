# Phase 11.4 — OpenClaw Controlled Local Utility Connection V1

## Objective

Connect OpenClaw to the Phase 11.3 local auxiliary router through one narrow,
fail-closed command surface.

This phase does not expose Ollama directly to OpenClaw. OpenClaw invokes a
Python connection wrapper, which decodes a canonical base64url request token,
reconstructs the mandatory safety flags and delegates only approved low-risk
tasks to the validated Phase 11.3 router.

## Command contract

```text
C:\Users\jmcas\OpenClawProjects\trading-ai\.venv\Scripts\python.exe -m src.workflows.run_openclaw_controlled_local_utility_connection_v1 <canonical-base64url-request>
```

The workflow accepts exactly one request-token argument. It rejects:

- missing or extra arguments;
- whitespace, padding and shell metacharacters in the token;
- non-canonical base64url;
- duplicate JSON fields;
- non-canonical JSON;
- unknown request fields;
- unknown or critical tasks;
- missing human review;
- invalid token or payload sizes.

## Allowed task classes

OpenClaw may request only:

- deterministic status or blocked-action templates;
- rewriting;
- summarization of validated text;
- simplification;
- human-readable formatting;
- classification against supplied labels;
- extraction of supplied fields.

Architecture, code changes, scientific validation, risk decisions, security
permissions, trading decisions, browser actions, message sending and external
actions are rejected before the local router is called.

## Request token

The decoded request contains exactly:

```json
{
  "connection_request_schema_version": "OPENCLAW_CONTROLLED_LOCAL_UTILITY_REQUEST_V1",
  "request_id": "phase-11-4-first-controlled-rewrite-v1",
  "task_type": "REWRITE_MESSAGE",
  "payload": {
    "text": "El dataset oficial está disponible y contiene cero filas de evidencia. La revisión humana es obligatoria y la ejecución operativa no está permitida."
  },
  "max_output_tokens": 96,
  "human_review_required": true
}
```

The first controlled request token is:

```text
eyJjb25uZWN0aW9uX3JlcXVlc3Rfc2NoZW1hX3ZlcnNpb24iOiJPUEVOQ0xBV19DT05UUk9MTEVEX0xPQ0FMX1VUSUxJVFlfUkVRVUVTVF9WMSIsImh1bWFuX3Jldmlld19yZXF1aXJlZCI6dHJ1ZSwibWF4X291dHB1dF90b2tlbnMiOjk2LCJwYXlsb2FkIjp7InRleHQiOiJFbCBkYXRhc2V0IG9maWNpYWwgZXN0XHUwMGUxIGRpc3BvbmlibGUgeSBjb250aWVuZSBjZXJvIGZpbGFzIGRlIGV2aWRlbmNpYS4gTGEgcmV2aXNpXHUwMGYzbiBodW1hbmEgZXMgb2JsaWdhdG9yaWEgeSBsYSBlamVjdWNpXHUwMGYzbiBvcGVyYXRpdmEgbm8gZXN0XHUwMGUxIHBlcm1pdGlkYS4ifSwicmVxdWVzdF9pZCI6InBoYXNlLTExLTQtZmlyc3QtY29udHJvbGxlZC1yZXdyaXRlLXYxIiwidGFza190eXBlIjoiUkVXUklURV9NRVNTQUdFIn0
```

## First controlled command

```text
C:\Users\jmcas\OpenClawProjects\trading-ai\.venv\Scripts\python.exe -m src.workflows.run_openclaw_controlled_local_utility_connection_v1 eyJjb25uZWN0aW9uX3JlcXVlc3Rfc2NoZW1hX3ZlcnNpb24iOiJPUEVOQ0xBV19DT05UUk9MTEVEX0xPQ0FMX1VUSUxJVFlfUkVRVUVTVF9WMSIsImh1bWFuX3Jldmlld19yZXF1aXJlZCI6dHJ1ZSwibWF4X291dHB1dF90b2tlbnMiOjk2LCJwYXlsb2FkIjp7InRleHQiOiJFbCBkYXRhc2V0IG9maWNpYWwgZXN0XHUwMGUxIGRpc3BvbmlibGUgeSBjb250aWVuZSBjZXJvIGZpbGFzIGRlIGV2aWRlbmNpYS4gTGEgcmV2aXNpXHUwMGYzbiBodW1hbmEgZXMgb2JsaWdhdG9yaWEgeSBsYSBlamVjdWNpXHUwMGYzbiBvcGVyYXRpdmEgbm8gZXN0XHUwMGUxIHBlcm1pdGlkYS4ifSwicmVxdWVzdF9pZCI6InBoYXNlLTExLTQtZmlyc3QtY29udHJvbGxlZC1yZXdyaXRlLXYxIiwidGFza190eXBlIjoiUkVXUklURV9NRVNTQUdFIn0
```

## Foreground execution boundary

The controlled OpenClaw call fixes `yieldMs` at `120000` milliseconds and the process timeout at `180` seconds. This keeps the guarded local-model request in the foreground and prevents loss of an in-memory background process session.

## OpenClaw execution

Run one Gateway-backed turn without delivery:

```powershell
openclaw agent `
    --agent trading-ai `
    --message-file docs\PHASE_11_4_FIRST_CONTROLLED_OPENCLAW_PROMPT_V1.md `
    --json
```

Do not use `--deliver`.

## Exec approval boundary

The preferred effective policy is `ask` or strict `allowlist`, never `full`.

The Python executable must not have a broad path-only allowlist entry. A
path-only interpreter entry would allow other Python modules or scripts.

A hand-authored argument restriction for this connection has the following
shape:

```text
pattern:
C:\Users\jmcas\OpenClawProjects\trading-ai\.venv\Scripts\python.exe

argPattern:
^-m src\.workflows\.run_openclaw_controlled_local_utility_connection_v1 [A-Za-z0-9_-]{1,11000}$
```

The semantic safety boundary remains Python validation. The argument pattern
only prevents OpenClaw from using the approved interpreter entry for another
module or for shell-style arguments.

Before the controlled execution, inspect the effective policy:

```powershell
openclaw exec-policy show
openclaw approvals get --json
```

If an existing path-only rule allows the same Python executable, stop and
remove or replace that broad rule before continuing.

## Output contract

Success writes JSON to `stdout` and leaves `stderr` empty. Failure writes a
fail-closed JSON object to `stderr` and returns a non-zero exit code.

Every successful response preserves:

```text
human_review_required = true
external_action_allowed = false
other_openclaw_tool_invocation_allowed = false
browser_control_allowed = false
message_send_allowed = false
trading_execution_allowed = false
official_dataset_write_allowed = false
signal_generation_enabled = false
paper_trade_execution_allowed = false
real_capital_allowed = false
market_execution_allowed = false
automation_allowed = false
```

## Validation sequence

1. Compile all Phase 11.4 Python files.
2. Re-run Phase 11.1, 11.2 and 11.3 tests.
3. Run Phase 11.4 unit tests.
4. Validate the wrapper directly with live Ollama.
5. Confirm the official dataset and manifest remain unchanged.
6. Inspect OpenClaw exec policy.
7. Run the first controlled OpenClaw turn exactly once.
8. Record sanitized evidence.
9. Commit and merge only after the OpenClaw execution passes.

## Still prohibited

- shell freedom;
- extra OpenClaw tools;
- retries after an ambiguous or failed execution;
- browser control;
- message delivery;
- Quantfury;
- trading signals;
- paper trading;
- real capital;
- exchange execution;
- official dataset writes;
- autonomous operation.
