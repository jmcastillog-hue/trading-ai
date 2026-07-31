# Phase 11.2 — OpenClaw Read-Only End-to-End Runbook and Recovery V1

## Objetivo

Cerrar el MVP local de consulta read-only mediante una ejecución reproducible de punta a punta, un runbook operativo y procedimientos de recuperación fail-closed.

Esta fase no incorpora nuevos permisos. No habilita señales, alertas accionables, escritura del dataset, paper trading, capital real, exchanges, navegador, mensajería ni automatización operativa.

## Comando autorizado

```text
C:\Users\jmcas\OpenClawProjects\trading-ai\.venv\Scripts\python.exe -m src.workflows.run_openclaw_read_only_local_connection_v1
```

El comando debe ejecutarse desde la raíz del repositorio. No admite argumentos adicionales.

## Flujo end-to-end

1. OpenClaw invoca una vez el comando exacto autorizado.
2. Python valida el contrato histórico read-only.
3. Python valida el dataset oficial y su manifiesto.
4. Python produce una respuesta JSON limitada a estado científico y restricciones.
5. OpenClaw explica el resultado a una persona.
6. Ningún archivo oficial es modificado.

## Estado esperado

- `decision`: `CURRENT_VALIDATED_RESEARCH_STATUS_CONNECTED_FOR_HUMAN_EXPLANATION_ONLY`;
- dataset oficial presente y no simbólico;
- 54 columnas;
- 0 filas de evidencia;
- revisión humana obligatoria;
- campos accionables ausentes;
- todos los permisos operativos en `False`.

## Evidencia de OpenClaw reutilizada

Phase 11.2 no amplía las herramientas del agente. Revalida la evidencia sanitizada y versionada de la primera ejecución real de Phase 11.1:

```text
reports/phase_11_1/first_controlled_openclaw_read_only_execution.json
```

La evidencia debe conservar:

- agente `trading-ai`;
- proveedor `openai`;
- modelo `gpt-5.6-sol`;
- una única llamada a `exec`;
- cero fallos de herramienta;
- comando exacto autorizado;
- resultado read-only aprobado;
- todos los permisos operativos deshabilitados.

## Diagnóstico rápido

### El comando termina con código 20

Causa: se agregaron argumentos no autorizados.

Recuperación: ejecutar exactamente el comando definido en este documento.

### El comando termina con código 1

Causa: validación fail-closed. Puede corresponder a dataset ausente, manifiesto inconsistente, hash diferente, finales de línea incorrectos, BOM UTF-8, columnas inesperadas o permiso prohibido habilitado.

Recuperación:

1. No editar manualmente el dataset ni el manifiesto.
2. Ejecutar `git status --short`.
3. Comparar los archivos oficiales con `origin/main`.
4. Restaurar únicamente desde Git si no existen cambios legítimos pendientes.
5. Repetir primero las pruebas unitarias y luego el workflow.

### OpenClaw no puede invocar el comando

Causa probable: allowlist, ruta del intérprete, entorno virtual o directorio de trabajo incorrectos.

Recuperación:

1. Confirmar que existe `.venv\Scripts\python.exe`.
2. Ejecutar el comando manualmente desde la raíz del repositorio.
3. Confirmar que la allowlist contiene solo el ejecutable y el módulo exactos.
4. No ampliar la allowlist a shell libre, navegador o rutas arbitrarias.

### El JSON contiene campos accionables

Decisión: fallo crítico. No usar la salida.

Recuperación: detener la integración, ejecutar las pruebas negativas y revisar `src/integration/openclaw_read_only_local_connection_v1.py` antes de continuar.

## Verificación de integridad

La validación de Phase 11.2 comprueba:

- evidencia de OpenClaw de Phase 11.1 íntegra y limitada;
- ejecución directa exitosa;
- JSON válido por `stdout`;
- `stderr` vacío en éxito;
- decisión exacta;
- dataset oficial sin modificaciones;
- manifiesto oficial sin modificaciones;
- ausencia de campos accionables;
- restricciones operativas completas;
- fallo cerrado con argumentos adicionales;
- fallo cerrado con dataset alterado en una copia temporal;
- runbook y comando exacto presentes.

## Procedimiento de recuperación seguro

```powershell
Set-Location C:\Users\jmcas\OpenClawProjects\trading-ai

git --no-pager status --short
python -m unittest tests.test_openclaw_read_only_local_connection_v1 -v
python -m unittest tests.test_openclaw_read_only_end_to_end_runbook_and_recovery_v1 -v
python -m src.workflows.validate_openclaw_read_only_end_to_end_runbook_and_recovery_v1
```

Si cualquier paso falla, no se debe ampliar permisos ni continuar con integraciones nuevas.

## Criterio de cierre del MVP read-only

Phase 11.2 queda aprobada únicamente cuando:

- todas las pruebas pasan;
- la ejecución end-to-end es reproducible;
- las copias oficiales permanecen sin cambios;
- la recuperación fail-closed está validada;
- OpenClaw conserva una única capacidad local de consulta humana;
- no se habilita ninguna operación externa.

## Próxima fase

Phase 11.3 — Local Auxiliary Model Routing V1.

Esa fase podrá evaluar Ollama para redacción, resumen, clasificación y formato de bajo riesgo, manteniendo GPT-5.6 como modelo principal y sin otorgar herramientas operativas al modelo local.
