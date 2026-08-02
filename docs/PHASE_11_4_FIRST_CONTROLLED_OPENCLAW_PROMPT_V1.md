# Phase 11.4 — First Controlled OpenClaw Local Utility Execution V1

Execute exactly one controlled local utility request.

## Mandatory tool policy

- Use only the `exec` tool.
- Make exactly one tool call.
- Do not retry if the command fails.
- Do not use browser, message, web, filesystem-write, patch, process or any other tool.
- Do not modify any file.
- Do not deliver or send the response to any external channel.
- Use the exact working directory and command below.
- Do not add shell operators, redirections, pipes, environment overrides or extra arguments.

## Exact working directory

```text
C:\Users\jmcas\OpenClawProjects\trading-ai
```

## Exact command

```text
C:\Users\jmcas\OpenClawProjects\trading-ai\.venv\Scripts\python.exe -m src.workflows.run_openclaw_controlled_local_utility_connection_v1 eyJjb25uZWN0aW9uX3JlcXVlc3Rfc2NoZW1hX3ZlcnNpb24iOiJPUEVOQ0xBV19DT05UUk9MTEVEX0xPQ0FMX1VUSUxJVFlfUkVRVUVTVF9WMSIsImh1bWFuX3Jldmlld19yZXF1aXJlZCI6dHJ1ZSwibWF4X291dHB1dF90b2tlbnMiOjk2LCJwYXlsb2FkIjp7InRleHQiOiJFbCBkYXRhc2V0IG9maWNpYWwgZXN0XHUwMGUxIGRpc3BvbmlibGUgeSBjb250aWVuZSBjZXJvIGZpbGFzIGRlIGV2aWRlbmNpYS4gTGEgcmV2aXNpXHUwMGYzbiBodW1hbmEgZXMgb2JsaWdhdG9yaWEgeSBsYSBlamVjdWNpXHUwMGYzbiBvcGVyYXRpdmEgbm8gZXN0XHUwMGUxIHBlcm1pdGlkYS4ifSwicmVxdWVzdF9pZCI6InBoYXNlLTExLTQtZmlyc3QtY29udHJvbGxlZC1yZXdyaXRlLXYxIiwidGFza190eXBlIjoiUkVXUklURV9NRVNTQUdFIn0
```

## Exact exec tool call

Use exactly these `exec` parameters:

```json
{
  "command": "C:\\Users\\jmcas\\OpenClawProjects\\trading-ai\\.venv\\Scripts\\python.exe -m src.workflows.run_openclaw_controlled_local_utility_connection_v1 eyJjb25uZWN0aW9uX3JlcXVlc3Rfc2NoZW1hX3ZlcnNpb24iOiJPUEVOQ0xBV19DT05UUk9MTEVEX0xPQ0FMX1VUSUxJVFlfUkVRVUVTVF9WMSIsImh1bWFuX3Jldmlld19yZXF1aXJlZCI6dHJ1ZSwibWF4X291dHB1dF90b2tlbnMiOjk2LCJwYXlsb2FkIjp7InRleHQiOiJFbCBkYXRhc2V0IG9maWNpYWwgZXN0XHUwMGUxIGRpc3BvbmlibGUgeSBjb250aWVuZSBjZXJvIGZpbGFzIGRlIGV2aWRlbmNpYS4gTGEgcmV2aXNpXHUwMGYzbiBodW1hbmEgZXMgb2JsaWdhdG9yaWEgeSBsYSBlamVjdWNpXHUwMGYzbiBvcGVyYXRpdmEgbm8gZXN0XHUwMGUxIHBlcm1pdGlkYS4ifSwicmVxdWVzdF9pZCI6InBoYXNlLTExLTQtZmlyc3QtY29udHJvbGxlZC1yZXdyaXRlLXYxIiwidGFza190eXBlIjoiUkVXUklURV9NRVNTQUdFIn0",
  "workdir": "C:\\Users\\jmcas\\OpenClawProjects\\trading-ai",
  "yieldMs": 120000,
  "timeout": 180
}
```

Do not omit or change `command`, `workdir`, `yieldMs` or `timeout`. Keep the execution in the foreground and do not use `process`.

## Result handling

Use the command output only when:

- exit code is `0`;
- `stderr` is empty;
- `stdout` is valid JSON;
- `decision` is
  `OPENCLAW_CONTROLLED_LOCAL_UTILITY_COMPLETED_FOR_HUMAN_REVIEW`;
- `delegated_route` is `LOCAL_OLLAMA`;
- `request_id` is `phase-11-4-first-controlled-rewrite-v1`;
- every operational permission is `false`;
- `human_review_required` is `true`.

If any condition fails, stop and report the failure without another tool call.

## Required final response format

```text
FINISH_STATE: CONTINUE
PHASE_STATE: Phase 11.4 first controlled local utility execution
REQUEST_ID: phase-11-4-first-controlled-rewrite-v1
DELEGATED_ROUTE: <value from JSON>
DECISION: <value from JSON>
LOCAL_MODEL_CALLED: <value from JSON>
OUTPUT: <human-readable output from JSON>
ACTION_COMPLETED: One exact local utility command executed through exec.
NEXT_ACTION: Human review of the sanitized execution evidence.
APPROVAL_REQUIRED: no external or operational action was requested.
```
