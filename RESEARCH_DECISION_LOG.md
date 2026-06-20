# Trading-AI / OpenClaw — Research Decision Log

## Estado general

Este documento registra las decisiones técnicas tomadas durante la investigación del sistema de trading cuantitativo del proyecto `trading-ai`.

La regla central del proyecto se mantiene:

```text
Primero medir.
Después probar.
Después alertar.
Después simular.
Y solo al final automatizar.
```

Este proyecto no está todavía en fase de operación real ni de automatización de órdenes. El objetivo actual es construir un sistema de análisis, validación y soporte de decisión.

---

## Arquitectura conceptual actual

```text
Datos de mercado
↓
Python
↓
Indicadores técnicos
↓
Probabilidades históricas
↓
Liquidez / zonas clave
↓
Backtesting
↓
Scoring de entrada
↓
IA analista
↓
Reporte / alerta
↓
José Miguel decide
```

---

# Resumen de fases y decisiones

## Fase 1 — Backtesting Engine V3

Se creó el motor de backtesting V3.

Resultado del baseline EMA:

```text
Return: -8.02%
Win rate: 36.84%
Profit factor: 0.7520
Max drawdown: -17.64%
```

### Decisión

El motor funciona, pero la estrategia EMA básica fue rechazada.

---

## Fase 1.1 — FIB V5 SHORT

Se creó la estrategia FIB V5 para SHORT.

Mejor configuración inicial:

```text
lookback_bars: 48
fib zone: 0.618 - 0.786
min_impulse_pct: 0.02
atr_multiplier: 1.25
risk_reward: 2.5
require_rejection_wick: False
direction: short_only
```

Resultado inicial:

```text
Return: +13.13%
Trades: 10
Win rate: 80.00%
Profit factor: 4.8784
Max drawdown: -1.50%
```

### Decisión

Candidato prometedor inicial, pero pendiente de validación robusta.

---

## Fase 1.2 — Validación robusta FIB V5 SHORT

Dataset ampliado a 5000 velas.

Resultado general:

```text
Return: +14.14%
Trades: 16
Win rate: 68.75%
Profit factor: 2.7382
Max drawdown: -2.97%
```

Por chunks:

```text
CHUNK_1: negativo
CHUNK_2: sin trades
CHUNK_3: casi neutro
CHUNK_4: muy positivo
CHUNK_5: positivo moderado
```

### Decisión

Prometedor, pero no definitivo. Requiere validación por régimen y fuera de muestra.

---

## Fase 1.3 — Validación multi-timeframe

Resultados:

```text
15m:
Return: +14.14%
PF: 2.7382

30m:
Return: -22.81%
PF: 0.3037

1h:
Return: -20.23%
PF: 0.5893

4h:
Return: +2.16%
PF: 1.0554
```

### Decisión

FIB V5 SHORT no es fractal universal. Funciona mejor en BTCUSDT 15m bajo condiciones específicas.

---

## Fase 1.4 — Filtro MTF

Se agregó filtro de régimen multi-timeframe.

Comparación:

```text
FIB V5 sin filtro:
Return: +14.14%
Win rate: 68.75%
PF: 2.7382
MDD: -2.97%

FIB V5 + MTF:
Return: +15.77%
Win rate: 73.33%
PF: 3.3206
MDD: -1.75%
```

### Decisión

El filtro MTF mejora la estrategia SHORT. Mantener como componente válido.

---

## Fase 1.5 — Diagnóstico de trades filtrados

El filtro MTF bloqueó un trade perdedor contra contexto 1H/4H fuertemente alcista.

### Decisión

El filtro MTF aportó valor real al bloquear operaciones contra tendencia superior.

---

## Fase 1.6 — Liquidez V1

Se probó un filtro de liquidez basado en distancia hacia sell-side liquidity.

Resultado mejor por sweep:

```text
lookback: 96
min_atr_distance: 4.0
Trades: 12
Return: +12.36%
Win rate: 75%
PF: 3.4572
MDD: -1.75%
```

### Decisión

Infraestructura útil, pero la definición de liquidez V1 era demasiado simple.

---

## Fase 1.7 — Liquidez V2

Se creó motor de liquidez V2 con swing lows y equal lows.

Comparación:

```text
FIB V5 + MTF:
Trades: 15
Return: +15.77%
Win rate: 73.33%
PF: 3.32
MDD: -1.75%

FIB V5 + MTF + Liquidez V2:
Trades: 10
Return: +13.75%
Win rate: 80.00%
PF: 5.09
MDD: -1.61%
```

### Decisión

Liquidez V2 reduce frecuencia, pero mejora calidad. Es candidata conservadora para el lado SHORT.

---

## Fase 1.8 — Comparación de estrategias candidatas

Ranking:

```text
FIB_V5_BASE:
VALID_CANDIDATE

FIB_V5_MTF:
STRONG_CANDIDATE

FIB_V5_MTF_LIQUIDITY_V1:
STRONG_CANDIDATE

FIB_V5_MTF_LIQUIDITY_V2:
STRONG_CANDIDATE
Mejor quality_score
```

### Decisión

Candidatas principales:

```text
Agresiva: FIB_V5_MTF
Conservadora/calidad: FIB_V5_MTF_LIQUIDITY_V2
```

---

## Fase 1.9 — Validación out-of-sample FIB V5 SHORT

Periodo:

```text
2024-01-01 a 2024-03-01
```

Resultados:

```text
OOS_FIB_V5_MTF:
Return: -2.39%
PF: 0.8331

OOS_FIB_V5_MTF_LIQUIDITY_V2:
Return: -2.88%
PF: 0.6632
```

### Decisión

La estrategia SHORT no funcionó en esta ventana alcista. No es una estrategia universal.

---

## Fase 1.10 — Diagnóstico de régimen OOS

La ventana OOS tuvo:

```text
Market return: +44.10%
Predominio de STRONG_BULLISH en 1H y 4H
```

### Decisión

La falla del SHORT fue coherente con el régimen alcista. Se requiere motor direccional o estrategia LONG separada.

---

# Bloque LONG

## Fase 1.11 — LONG espejo FIB V5

Se creó un LONG espejo mecánico del SHORT.

Resultados OOS:

```text
LONG base:
Return: -15.96%
PF: 0.5069
MDD: -20.69%

LONG + MTF:
Return: -6.19%
PF: 0.7088
MDD: -10.95%
```

### Decisión

LONG espejo rechazado. El LONG no debe ser una copia mecánica del SHORT.

---

## Fase 1.12 — Diagnóstico MAE/MFE LONG

Hallazgos:

```text
Muchos stops fueron seguidos por recuperación.
STOPPED_THEN_RECOVERED:
7 trades
total -104.16
avg post_exit_recovery_r 5.43R
```

También hubo entradas realmente malas:

```text
POOR_ENTRY_NO_FOLLOW_THROUGH:
5 trades
avg MFE 0.17R
```

### Decisión

El LONG fallaba por una combinación de timing, stop y contexto. No bastaba con ajustar una sola variable.

---

## Fase 1.13 — Variantes LONG V2

Mejor variante:

```text
Fib 0.500–0.618
Confirmation: break_prev_high
MTF activo
```

Resultado:

```text
Trades: 30
Return: +1.29%
Win rate: 46.67%
PF: 1.059
MDD: -7.30%
```

### Decisión

LONG V2 mejora frente al espejo original, pero todavía no es robusto.

---

## Fase 1.14 — Risk / Exit Research LONG V2

Mejor configuración:

```text
ATR multiplier: 1.5
Risk/Reward: 2.0
Max holding: 96
```

Resultado:

```text
Trades: 27
Return: +5.57%
Win rate: 55.56%
PF: 1.350
MDD: -3.96%
```

### Decisión

La gestión de salida era parte importante del problema. LONG V2 pasó de negativo a débilmente prometedor en una ventana, pero no se valida todavía.

---

## Fase 1.15 — Validación robusta LONG V2

Resultado en seis ventanas:

```text
Passed: 1
Near breakeven: 2
Failed: 3
Total trades: 162
Average return: -3.32%
Average PF: 0.8603
Worst drawdown: -12.43%
```

### Decisión

LONG V2 no es robusto. No pasa a paper trading.

---

## Fase 1.16 — Regime Filter V2

Comparación:

```text
LONG_V2_OLD_MTF:
162 trades
avg_return: -3.32%
avg_pf: 0.8603
worst_drawdown: -12.43%

LONG_V2_REGIME_V2:
26 trades
avg_return: +0.039%
avg_pf: 0.9710
worst_drawdown: -5.53%
```

### Decisión

Regime Filter V2 redujo sobreoperación y drawdown, pero quedó demasiado estricto y no generó ventaja robusta.

---

## Fase 1.17 — Regime V2 State Whitelist Research

Mejor whitelist en discovery:

```text
PRIOR_POSITIVE_PAIRS_EXPERIMENTAL
```

Resultado:

```text
Trades: 83
Compound return: +26.38%
Average PF: 1.7236
Worst drawdown: -8.01%
Passed: 2
Weak pass: 2
Near breakeven: 1
Failed: 1
```

### Decisión

Resultado muy prometedor, pero con riesgo claro de data-mining. Requiere holdout.

---

## Fase 1.18 — Holdout validation de whitelists LONG V2

Periodo holdout:

```text
2025-01-01 a 2026-01-01
```

Resultado de la whitelist que parecía mejor en discovery:

```text
PRIOR_POSITIVE_PAIRS_EXPERIMENTAL:
Discovery compound return: +26.38%
Holdout compound return: -11.57%
Discovery PF: 1.7236
Holdout PF: 0.6530
```

Baseline sin filtro:

```text
NO_STATE_FILTER_BASELINE:
Holdout compound return: -38.12%
Average PF: 0.6371
Worst drawdown: -18.05%
```

La mejor por score en holdout fue:

```text
EXHAUSTION_REVERSAL_RESEARCH:
Compound return: +4.11%
Total trades: 10
Average PF: 0.8072
Decision: TOO_FEW_TRADES
```

### Decisión

Las whitelists LONG V2 no sobrevivieron holdout.

Conclusión formal:

```text
LONG V2 no pasa a paper trading.
No se convierte en estrategia oficial.
No debe seguir optimizándose por ahora.
```

---

# Decisiones estratégicas actuales

## Estrategias rechazadas

```text
EMA baseline:
Rechazada.

LONG espejo FIB V5:
Rechazada.

LONG V2 sin filtro robusto:
Rechazada.

LONG V2 con Regime V2 whitelists:
Rechazada por holdout.
```

## Estrategias candidatas pendientes

```text
SHORT FIB V5 + MTF:
Candidata agresiva.

SHORT FIB V5 + MTF + Liquidez V2:
Candidata conservadora/calidad.
```

Estas estrategias deben pasar por validación robusta adicional antes de cualquier paper trading.

---

# Conclusión general de investigación

El sistema ya demostró valor como motor de investigación porque evitó convertir hipótesis atractivas en estrategias operativas sin validación.

El bloque LONG enseñó lo siguiente:

```text
1. El LONG no puede ser espejo del SHORT.
2. El LONG mejora con Fib 0.500–0.618 y break_prev_high.
3. La gestión ATR 1.5 / RR 2.0 / holding 96 mejora una ventana.
4. El filtro por régimen reduce pérdidas.
5. Las whitelists pueden parecer muy buenas en discovery.
6. El holdout reveló sobreajuste.
```

Por ahora, el foco técnico debe salir del LONG V2.

---

# Próximo foco recomendado

## Opción principal

```text
Validación robusta ampliada del lado SHORT:
FIB V5 + MTF
FIB V5 + MTF + Liquidez V2
```

Motivo:

```text
El lado SHORT ya mostró mejores métricas in-sample y menor drawdown.
Debe validarse en más ventanas históricas y distintos regímenes.
```

## Opción secundaria

```text
Diseñar LONG desde cero con buy-side liquidity,
no como extensión del LONG V2 actual.
```

## Opción de arquitectura

```text
Crear Strategy Decision Engine:
- registra hipótesis
- estado de validación
- métricas
- decisión
- motivo de rechazo
- siguiente acción
```

---

# Regla operativa vigente

```text
No operar con dinero real.
No automatizar.
No paper trading LONG.
No optimizar de forma indefinida una hipótesis que falló holdout.
```

Estado actual:

```text
Proyecto en fase de investigación cuantitativa.
Próximo foco recomendado: robust validation del lado SHORT.
```
