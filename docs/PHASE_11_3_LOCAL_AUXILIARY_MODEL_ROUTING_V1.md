# Phase 11.3 — Local Auxiliary Model Routing V1

## Objective

Add a strict local routing layer that reduces principal-model token usage without
allowing a small local model to make scientific, security, trading or external
action decisions.

Phase 11.3 preserves the completed Phase 11.2 read-only MVP.

## Routing policy

The router has exactly three routes:

```text
Validated request
    |
    +-- PYTHON_TEMPLATE
    |     Exact, deterministic, zero-token status and blocked-action messages.
    |
    +-- LOCAL_OLLAMA
    |     Low-risk language utilities using trading-ai-local-fast.
    |
    +-- MODEL_PRINCIPAL_REQUIRED
          Architecture, code, science, risk, security, trading and external actions.
```

The principal-model route does not call a model from this module. It returns a
structured escalation decision for OpenClaw or the human operator.

## Allowed local tasks

- `REWRITE_MESSAGE`
- `SUMMARIZE_VALIDATED_TEXT`
- `SIMPLIFY_EXPLANATION`
- `FORMAT_HUMAN_MESSAGE`
- `CLASSIFY_TEXT`
- `EXTRACT_FIELDS`

Local tasks are language transformations only. Input data must already be
validated by deterministic Python code or reviewed by a human.

## Deterministic template tasks

- `BUILD_VALIDATED_STATUS_MESSAGE`
- `BUILD_BLOCKED_ACTION_MESSAGE`

These tasks do not invoke Ollama and consume zero model tokens.

## Principal-model tasks

- `ARCHITECTURE_REVIEW`
- `CODE_CHANGE`
- `SCIENTIFIC_VALIDATION`
- `RISK_DECISION`
- `SECURITY_PERMISSION_CHANGE`
- `TRADING_DECISION`
- `BROWSER_ACTION`
- `MESSAGE_SEND`
- `EXTERNAL_ACTION`

These tasks always return `MODEL_PRINCIPAL_REQUIRED`.

## Local Ollama boundary

The implementation uses only:

```text
http://127.0.0.1:11434
```

Allowed endpoints:

```text
GET  /api/tags
POST /api/chat
```

The request fixes:

- model: `trading-ai-local-fast`
- `think: false`
- `stream: false`
- `num_ctx: 4096`
- temperature: `0`
- maximum generation: `64` to `160` tokens
- keep-alive: `2m`
- structured JSON output through `format: "json"`
- exact output keys, types, labels and lengths revalidated by deterministic Python
- no tools
- no arbitrary URL
- no cloud endpoint
- no browser
- no message delivery
- no file write
- no shell execution
- no trading action

## Fail-closed request contract

Every request must contain exactly:

```json
{
  "task_type": "REWRITE_MESSAGE",
  "payload": {
    "text": "Validated source text."
  },
  "max_output_tokens": 96,
  "human_review_required": true,
  "allow_external_action": false,
  "allow_actionable_trading_fields": false
}
```

Unknown fields, unknown tasks, missing human review, external-action permission,
actionable trading fields, oversized payloads and non-finite JSON values fail
closed.

## Human review

Every successful output preserves:

```text
human_review_required = true
external_action_allowed = false
browser_control_allowed = false
message_send_allowed = false
trading_execution_allowed = false
official_dataset_write_allowed = false
```

The output is a draft or explanation. It is not a command.

### Local grammar compatibility decision

The controlled live validation showed that this local backend accepts `think: false`, JSON mode and a simple JSON Schema, but rejects the fuller response schema with `Failed to initialize samplers: failed to parse grammar`. Phase 11.3 therefore uses Ollama JSON mode and performs the authoritative allowlist, exact-key, type, label and length validation in deterministic Python. Any mismatch still fails closed.

## README encoding correction

Phase 11.3 repairs only the mojibake sequences introduced in the Phase 11.2
README update. The correction is exact and count-checked. It is not a general
rewrite of the README and does not reopen Phase 11.2.

## Validation

The phase validates:

- deterministic template routing;
- low-risk Ollama routing with a fake client;
- mandatory escalation of critical tasks;
- rejection of external-action permission;
- rejection of actionable trading payload keys;
- rejection of unknown tasks;
- exact local endpoint;
- `think: false`;
- no tool definition in the Ollama request;
- structured output validation;
- live detection of `trading-ai-local-fast`;
- one controlled live local rewrite;
- sanitized evidence generation;
- Phase 11.1 and Phase 11.2 regression tests;
- README UTF-8 integrity.

## Still prohibited

- sending a message;
- producing an operational alert;
- controlling Microsoft Edge;
- accessing Quantfury;
- generating a trading signal;
- modifying the official evidence dataset;
- paper trading;
- real capital;
- exchange execution;
- autonomous operation.

## Next finite phase

Phase 11.4 — OpenClaw Controlled Local Utility Connection V1.

That phase may allow OpenClaw to invoke only the exact one-shot router command
for low-risk language utilities. It will not add browser, messaging or trading
tools.
