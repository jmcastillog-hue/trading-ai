# Phase 11.6 — OpenClaw Supervised Read-Only Research Query V1

## Decisión de diseño

`PHASE_11_6_OPENCLAW_SUPERVISED_READ_ONLY_RESEARCH_QUERY_V1` es una capa
estrecha, determinista y supervisada sobre
`openclaw_controlled_read_only_research_workflow_v1` de Phase 11.5.

No es una interfaz de preguntas libres. La solicitud contiene exactamente
cuatro campos y `query_id` pertenece a un catálogo cerrado.

## Catálogo cerrado

1. `PROJECT_COMPLETION_STATUS`
2. `LONG_RESEARCH_STATUS`
3. `SHORT_RESEARCH_STATUS`
4. `EVIDENCE_DATASET_STATUS`
5. `RESEARCH_LOCK_STATUS`
6. `OPERATIONAL_PERMISSION_STATUS`

## Contrato de solicitud

- Esquema: `OPENCLAW_SUPERVISED_READ_ONLY_RESEARCH_QUERY_REQUEST_V1`.
- `request_id`: identificador ASCII seguro, en minúsculas y con guiones.
- `query_id`: uno de los seis valores cerrados.
- `human_review_required`: siempre `true`.
- `additionalProperties`: `false`.

El token es JSON canónico codificado como Base64URL sin relleno. El
decodificador rechaza claves duplicadas, variantes no canónicas y cualquier
carácter fuera del alfabeto Base64URL, incluidos metacaracteres de shell.

## Ruta de ejecución

La capa construye internamente una solicitud de Phase 11.5 con:

- operación `GET_AND_EXPLAIN_VALIDATED_RESEARCH_STATUS`;
- modo `DETERMINISTIC_TEMPLATE`;
- `max_output_tokens=112`;
- revisión humana obligatoria;
- `request_id` fuente fijo
  `phase-11-5-first-controlled-research-summary-v1`, separado del
  `request_id` público de Phase 11.6.

La única ruta permitida es `PYTHON_TEMPLATE`. `local_model_called` debe ser
`false`. La respuesta fuente se valida con el validador oficial de Phase
11.5 y con comprobaciones estrictas de claves, restricciones, versiones y
permisos operativos.

## Límites de seguridad

La implementación no acepta texto libre, prompts, símbolos, estrategias,
mercados, rutas, comandos, parámetros de orden, destinos externos ni campos
desconocidos. No genera señales ni recomendaciones. No controla navegador,
no envía mensajes, no ejecuta paper trading o trading real, no usa capital,
no automatiza acciones y no escribe el dataset ni su manifiesto.

Toda respuesta exige revisión humana. Cualquier cambio del contrato fuente
provoca fallo cerrado.

## Primera consulta

Archivo:
`examples/phase_11_6_first_controlled_supervised_query_request_v1.json`

Token canónico:

`eyJodW1hbl9yZXZpZXdfcmVxdWlyZWQiOnRydWUsInF1ZXJ5X2lkIjoiRVZJREVOQ0VfREFUQVNFVF9TVEFUVVMiLCJxdWVyeV9yZXF1ZXN0X3NjaGVtYV92ZXJzaW9uIjoiT1BFTkNMQVdfU1VQRVJWSVNFRF9SRUFEX09OTFlfUkVTRUFSQ0hfUVVFUllfUkVRVUVTVF9WMSIsInJlcXVlc3RfaWQiOiJwaGFzZS0xMS02LWZpcnN0LWNvbnRyb2xsZWQtZXZpZGVuY2Utc3RhdHVzLXYxIn0`

Resultado directo requerido:

- `query_id=EVIDENCE_DATASET_STATUS`
- `query_route=PYTHON_TEMPLATE`
- `local_model_called=false`
- `long_official_dataset_state=INITIALIZED_EMPTY_READY_FOR_CONTROLLED_EVIDENCE`
- `long_official_evidence_row_count=0`

## Validación de esta etapa

La validación de fuente ejecuta `py_compile`, 62 pruebas acumuladas, diez
controles negativos, el runner directo, el validador y `git diff --check`.
También verifica antes y después los hashes oficiales.

Esta etapa no ejecuta OpenClaw, no ejecuta Ollama, no modifica aprobaciones,
no crea commit y no realiza acciones externas.
