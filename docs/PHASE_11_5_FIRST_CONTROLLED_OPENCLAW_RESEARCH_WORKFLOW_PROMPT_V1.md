# Phase 11.5 — First Controlled OpenClaw Read-Only Research Workflow

Execute exactly one controlled read-only research workflow request.

## Mandatory tool policy

- Use only the `exec` tool.
- Make exactly one tool call.
- Do not use `process`.
- Do not retry.
- Do not use browser, web, read, write, message or any other tool.
- Do not modify any file.
- Do not send or deliver anything externally.
- Use exactly the command, workdir, yieldMs and timeout below.
- Keep the execution in the foreground.

## Exact exec tool call

```json
{
  "command": "C:\\Users\\jmcas\\OpenClawProjects\\trading-ai\\.venv\\Scripts\\python.exe -m src.workflows.run_openclaw_controlled_read_only_research_workflow_v1 eyJleHBsYW5hdGlvbl9tb2RlIjoiREVURVJNSU5JU1RJQ19URU1QTEFURSIsImh1bWFuX3Jldmlld19yZXF1aXJlZCI6dHJ1ZSwibWF4X291dHB1dF90b2tlbnMiOjExMiwib3BlcmF0aW9uIjoiR0VUX0FORF9FWFBMQUlOX1ZBTElEQVRFRF9SRVNFQVJDSF9TVEFUVVMiLCJyZXF1ZXN0X2lkIjoicGhhc2UtMTEtNS1maXJzdC1jb250cm9sbGVkLXJlc2VhcmNoLXN1bW1hcnktdjEiLCJ3b3JrZmxvd19yZXF1ZXN0X3NjaGVtYV92ZXJzaW9uIjoiT1BFTkNMQVdfQ09OVFJPTExFRF9SRUFEX09OTFlfUkVTRUFSQ0hfV09SS0ZMT1dfUkVRVUVTVF9WMSJ9",
  "workdir": "C:\\Users\\jmcas\\OpenClawProjects\\trading-ai",
  "yieldMs": 120000,
  "timeout": 180
}
```

## Accept the result only when

- exit code is `0`;
- `stderr` is empty;
- `stdout` is valid JSON;
- `decision` is
  `OPENCLAW_CONTROLLED_READ_ONLY_RESEARCH_WORKFLOW_COMPLETED_FOR_HUMAN_REVIEW`;
- `source_connection_schema_version` is
  `OPENCLAW_READ_ONLY_LOCAL_CONNECTION_V1`;
- `explanation_route` is `PYTHON_TEMPLATE`;
- `local_model_called` is `false`;
- `human_review.required` is `true`;
- every operational permission is `false`;
- official dataset state remains
  `INITIALIZED_EMPTY_READY_FOR_CONTROLLED_EVIDENCE`;
- official evidence-row count remains `0`.

If any condition fails, stop without another tool call.

## Required final response

```text
FINISH_STATE: CONTINUE
PHASE_STATE: Phase 11.5 controlled read-only research workflow
REQUEST_ID: phase-11-5-first-controlled-research-summary-v1
SOURCE_CONNECTION: OPENCLAW_READ_ONLY_LOCAL_CONNECTION_V1
EXPLANATION_ROUTE: PYTHON_TEMPLATE
DECISION: <value from JSON>
LOCAL_MODEL_CALLED: false
RESEARCH_SUMMARY: <human-readable output from JSON>
OFFICIAL_EVIDENCE_ROWS: <value from JSON>
ACTION_COMPLETED: One exact read-only research workflow executed through exec.
NEXT_ACTION: Human review of sanitized evidence.
APPROVAL_REQUIRED: no external or operational action was requested.
```
