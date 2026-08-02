# Phase 11.5 — OpenClaw Controlled Read-Only Research Workflow V1

## Purpose

Phase 11.5 composes the already validated Phase 11.1 read-only research
status connection with the Phase 11.4 controlled local language utility
boundary.

The workflow performs exactly this sequence:

```text
validated repository status
    ↓
Phase 11.1 read-only connection
    ↓
allowlisted non-actionable research snapshot
    ↓
deterministic template or Phase 11.4 local summary
    ↓
structured response for mandatory human review
```

## Fixed operation

```text
GET_AND_EXPLAIN_VALIDATED_RESEARCH_STATUS
```

The request is canonical JSON transported as canonical base64url. Unknown
fields, duplicate fields, noncanonical JSON, unsupported modes, disabled
human review, shell metacharacters and oversized requests fail closed.

## Explanation modes

- `DETERMINISTIC_TEMPLATE`: formats the validated source without calling a
  model.
- `LOCAL_OLLAMA_SUMMARY`: delegates only `SUMMARIZE_VALIDATED_TEXT` through
  the Phase 11.4 boundary and requires route `LOCAL_OLLAMA`.

The model does not calculate, infer or change scientific status. Python
remains the authority.

## Fixed source

The workflow calls the Phase 11.1 `build_connection_status` function. It
does not accept a path, filename, symbol, market, strategy or arbitrary
text from OpenClaw.

## Response boundary

The response may contain only:

- current validated candidate dispositions;
- official dataset state and evidence-row count;
- lockbox and holdout state;
- project-completion state;
- an explanation derived only from that validated status;
- explicit restrictions;
- mandatory human review.

## Prohibited

The workflow cannot provide or enable:

- entries, stops, targets, leverage, side, quantity or orders;
- strategy selection or mutation;
- signal generation;
- official dataset writes;
- browser control;
- messages or external delivery;
- paper trading or real capital;
- exchange or market execution;
- automation;
- permission overrides.

## First controlled route

The first controlled request uses `DETERMINISTIC_TEMPLATE`. Exact scientific status uses deterministic formatting. Phase 11.4 already validates the optional `LOCAL_OLLAMA` route, so Phase 11.5 does not repeat it as an acceptance dependency.

## First controlled command

```text
C:\Users\jmcas\OpenClawProjects\trading-ai\.venv\Scripts\python.exe -m src.workflows.run_openclaw_controlled_read_only_research_workflow_v1 eyJleHBsYW5hdGlvbl9tb2RlIjoiREVURVJNSU5JU1RJQ19URU1QTEFURSIsImh1bWFuX3Jldmlld19yZXF1aXJlZCI6dHJ1ZSwibWF4X291dHB1dF90b2tlbnMiOjExMiwib3BlcmF0aW9uIjoiR0VUX0FORF9FWFBMQUlOX1ZBTElEQVRFRF9SRVNFQVJDSF9TVEFUVVMiLCJyZXF1ZXN0X2lkIjoicGhhc2UtMTEtNS1maXJzdC1jb250cm9sbGVkLXJlc2VhcmNoLXN1bW1hcnktdjEiLCJ3b3JrZmxvd19yZXF1ZXN0X3NjaGVtYV92ZXJzaW9uIjoiT1BFTkNMQVdfQ09OVFJPTExFRF9SRUFEX09OTFlfUkVTRUFSQ0hfV09SS0ZMT1dfUkVRVUVTVF9WMSJ9
```

## Required OpenClaw exec parameters

```json
{
  "command": "C:\\Users\\jmcas\\OpenClawProjects\\trading-ai\\.venv\\Scripts\\python.exe -m src.workflows.run_openclaw_controlled_read_only_research_workflow_v1 eyJleHBsYW5hdGlvbl9tb2RlIjoiREVURVJNSU5JU1RJQ19URU1QTEFURSIsImh1bWFuX3Jldmlld19yZXF1aXJlZCI6dHJ1ZSwibWF4X291dHB1dF90b2tlbnMiOjExMiwib3BlcmF0aW9uIjoiR0VUX0FORF9FWFBMQUlOX1ZBTElEQVRFRF9SRVNFQVJDSF9TVEFUVVMiLCJyZXF1ZXN0X2lkIjoicGhhc2UtMTEtNS1maXJzdC1jb250cm9sbGVkLXJlc2VhcmNoLXN1bW1hcnktdjEiLCJ3b3JrZmxvd19yZXF1ZXN0X3NjaGVtYV92ZXJzaW9uIjoiT1BFTkNMQVdfQ09OVFJPTExFRF9SRUFEX09OTFlfUkVTRUFSQ0hfV09SS0ZMT1dfUkVRVUVTVF9WMSJ9",
  "workdir": "C:\\Users\\jmcas\\OpenClawProjects\\trading-ai",
  "yieldMs": 120000,
  "timeout": 180
}
```

The first controlled run must use one `exec` call, no `process`, no retry,
no delivery and no other tool.

## Exact first-test allowlist argument pattern

```text
^-m src\.workflows\.run_openclaw_controlled_read_only_research_workflow_v1 eyJleHBsYW5hdGlvbl9tb2RlIjoiREVURVJNSU5JU1RJQ19URU1QTEFURSIsImh1bWFuX3Jldmlld19yZXF1aXJlZCI6dHJ1ZSwibWF4X291dHB1dF90b2tlbnMiOjExMiwib3BlcmF0aW9uIjoiR0VUX0FORF9FWFBMQUlOX1ZBTElEQVRFRF9SRVNFQVJDSF9TVEFUVVMiLCJyZXF1ZXN0X2lkIjoicGhhc2UtMTEtNS1maXJzdC1jb250cm9sbGVkLXJlc2VhcmNoLXN1bW1hcnktdjEiLCJ3b3JrZmxvd19yZXF1ZXN0X3NjaGVtYV92ZXJzaW9uIjoiT1BFTkNMQVdfQ09OVFJPTExFRF9SRUFEX09OTFlfUkVTRUFSQ0hfV09SS0ZMT1dfUkVRVUVTVF9WMSJ9$
```

Do not add a path-only rule for `python.exe`.

## Phase boundary

Preparation and direct validation do not run OpenClaw. A later controlled
step installs or verifies the exact rule and executes the command once.

## Formal validation status

- Decision:
  `PHASE_11_5_OPENCLAW_CONTROLLED_READ_ONLY_RESEARCH_WORKFLOW_VALIDATED`
- OpenClaw run ID: `ca3e73c6-e1d8-4e32-921c-3267fbae9d51`
- OpenClaw session ID: `744567c7-6661-493e-b09f-c9661673d219`
- Tool calls: `1`
- Tool failures: `0`
- Tool: `exec`
- Explanation route: `PYTHON_TEMPLATE`
- Local model called: `false`
- Official evidence rows: `0`
- Human review required: `true`
- External and operational actions: `false`
- Repository modified by OpenClaw: `false`
