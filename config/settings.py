from pathlib import Path

# Rutas principales del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

# Configuración de mercado
DEFAULT_SYMBOL = "BTCUSDT"
DEFAULT_TIMEFRAME = "15m"
DEFAULT_LIMIT = 1000

# Archivos principales
BTC_15M_FILE = DATA_DIR / "btcusdt_15m.csv"
QUANT_REPORT_FILE = REPORTS_DIR / "quantitative_analysis.txt"

# Configuración de riesgo base
DEFAULT_INITIAL_CAPITAL = 1000
DEFAULT_RISK_PER_TRADE = 0.01
DEFAULT_FEE_RATE = 0.001

# Configuración IA local
LOCAL_AI_PROVIDER = "lmstudio"
LOCAL_MODEL = "qwen/qwen3-4b-thinking-2507"
