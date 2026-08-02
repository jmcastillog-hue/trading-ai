# Primera consulta OpenClaw supervisada — Phase 11.6

Este documento prepara una única ejecución controlada posterior. No debe
ejecutarse durante la validación de fuente de Phase 11.6.

## Token exacto

`eyJodW1hbl9yZXZpZXdfcmVxdWlyZWQiOnRydWUsInF1ZXJ5X2lkIjoiRVZJREVOQ0VfREFUQVNFVF9TVEFUVVMiLCJxdWVyeV9yZXF1ZXN0X3NjaGVtYV92ZXJzaW9uIjoiT1BFTkNMQVdfU1VQRVJWSVNFRF9SRUFEX09OTFlfUkVTRUFSQ0hfUVVFUllfUkVRVUVTVF9WMSIsInJlcXVlc3RfaWQiOiJwaGFzZS0xMS02LWZpcnN0LWNvbnRyb2xsZWQtZXZpZGVuY2Utc3RhdHVzLXYxIn0`

## Comando exacto previsto

```powershell
& "C:\Users\jmcas\OpenClawProjects\trading-ai\.venv\Scripts\python.exe" `
  "C:\Users\jmcas\OpenClawProjects\trading-ai\src\workflows\run_openclaw_supervised_read_only_research_query_v1.py" `
  "eyJodW1hbl9yZXZpZXdfcmVxdWlyZWQiOnRydWUsInF1ZXJ5X2lkIjoiRVZJREVOQ0VfREFUQVNFVF9TVEFUVVMiLCJxdWVyeV9yZXF1ZXN0X3NjaGVtYV92ZXJzaW9uIjoiT1BFTkNMQVdfU1VQRVJWSVNFRF9SRUFEX09OTFlfUkVTRUFSQ0hfUVVFUllfUkVRVUVTVF9WMSIsInJlcXVlc3RfaWQiOiJwaGFzZS0xMS02LWZpcnN0LWNvbnRyb2xsZWQtZXZpZGVuY2Utc3RhdHVzLXYxIn0"
```

## Condiciones para la etapa posterior

- Inspeccionar primero la política actual de OpenClaw.
- Crear una única regla exacta ligada al comando y token anteriores.
- No crear una regla general para `python.exe`.
- Ejecutar una sola prueba foreground mediante `exec`.
- Usar `yieldMs=120000` y `timeout=180`.
- No usar `process`.
- No iniciar OpenClaw mediante Ollama.
- No repetir la ejecución si ya ocurrió.
- No crear commit hasta validar la ejecución real.

La salida debe conservar `query_route=PYTHON_TEMPLATE`,
`local_model_called=false` y `human_review_required=true`.
