\# Trading-AI / OpenClaw Quant Trading System



Sistema local de análisis cuantitativo y apoyo a la decisión para trading de criptomonedas.



\## Objetivo



Construir un centro de inteligencia de trading que permita analizar datos de mercado, calcular probabilidades históricas, detectar zonas de liquidez, generar señales, ejecutar backtesting y producir reportes con apoyo de IA local.



Este proyecto no busca, en su fase actual, operar automáticamente con dinero real. Su propósito es apoyar la toma de decisiones y validar estrategias antes de arriesgar capital.



\## Arquitectura general



Datos de mercado  

↓  

Python  

↓  

Indicadores técnicos  

↓  

Probabilidades históricas  

↓  

Liquidez  

↓  

Backtesting  

↓  

Scoring  

↓  

IA analista  

↓  

Reporte  

↓  

Decisión humana  



\## Tecnologías usadas



\- Python

\- Pandas

\- NumPy

\- OpenPyXL

\- Requests

\- python-binance

\- ta

\- OpenClaw

\- LM Studio

\- Qwen local model

\- Git / GitHub



\## Estructura del proyecto



```text

trading-ai/

│

├── config/

├── data/

├── logs/

├── notebooks/

├── reports/

├── scripts/

├── src/

│   ├── agents/

│   ├── analysis/

│   ├── backtesting/

│   ├── exchange/

│   ├── indicators/

│   ├── liquidity/

│   ├── quantitative/

│   ├── signals/

│   ├── workflows/

│   └── utils/

│

├── tests/

├── README.md

├── PROJECT\_STATUS.md

├── requirements.txt

└── .gitignore

