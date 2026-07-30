# Phase 11.1 ? OpenClaw Read-Only Local Connection V1

## Objetivo

Conectar el agente local `trading-ai` con el estado validado del
repositorio mediante un ?nico comando de consulta local y de solo
lectura.

La conexi?n no habilita operaciones de trading, se?ales, escritura
del dataset, automatizaci?n, paper trading, capital real ni ejecuci?n
en mercados.

## Implementaci?n

La fase incorpora:

- `src/integration/openclaw_read_only_local_connection_v1.py`
- `src/workflows/run_openclaw_read_only_local_connection_v1.py`
- `tests/test_openclaw_read_only_local_connection_v1.py`

La implementaci?n conserva intactos el contrato hist?rico certificado
y el adaptador read-only anterior. La capa nueva combina ese estado
hist?rico con el manifiesto oficial creado en Phase 10.45.

## Comando autorizado

```text
C:\Users\jmcas\OpenClawProjects\trading-ai\.venv\Scripts\python.exe -m src.workflows.run_openclaw_read_only_local_connection_v1
```

La allowlist del agente restringe la autorizaci?n al ejecutable y al
argumento exacto de este workflow.

## Controles

La conexi?n valida:

- dataset oficial presente y no simb?lico;
- UTF-8 sin BOM y finales de l?nea LF;
- 54 columnas;
- 0 filas de evidencia;
- SHA-256 y tama?o coincidentes con el manifiesto;
- inicializaci?n `create-only`;
- revisi?n humana obligatoria;
- todos los permisos operativos desactivados.

Ante cualquier discrepancia, el comando falla de forma cerrada.

## Validaci?n

Resultados locales:

- compilaci?n Python: aprobada;
- pruebas unitarias: 3 de 3 aprobadas;
- ejecuci?n directa del workflow: exit code 0;
- ejecuci?n mediante OpenClaw: 1 llamada a `exec`, 0 fallos;
- respuesta explicativa humana: aprobada;
- modificaciones externas: ninguna;
- modificaciones del dataset oficial: ninguna.

## Estado certificado

- Candidato LONG primario: investigaci?n solamente.
- Dataset oficial LONG: inicializado y vac?o.
- Filas oficiales de evidencia: 0.
- Revisi?n humana: obligatoria.
- Capital real: prohibido.
- Paper trading: prohibido.
- ?rdenes a exchanges: prohibidas.
- Se?ales y alertas accionables: desactivadas.
- Automatizaci?n operativa: prohibida.

La evidencia sanitizada de la primera ejecuci?n controlada est? en:

`reports/phase_11_1/first_controlled_openclaw_read_only_execution.json`
