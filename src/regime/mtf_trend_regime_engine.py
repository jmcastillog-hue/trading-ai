import pandas as pd


def safe_float(value, default=0.0):

    try:
        return float(value)

    except Exception:
        return default


def normalize_df(df):

    df = df.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df = df.dropna(
        subset=numeric_columns
    )

    df = df.sort_values(
        "timestamp"
    )

    df = df.reset_index(
        drop=True
    )

    return df


def calculate_ema(
    series,
    period
):

    return series.ewm(
        span=period,
        adjust=False
    ).mean()


def calculate_rsi(
    series,
    period=14
):

    delta = series.diff()

    gain = delta.where(
        delta > 0,
        0
    )

    loss = -delta.where(
        delta < 0,
        0
    )

    avg_gain = gain.rolling(
        window=period
    ).mean()

    avg_loss = loss.rolling(
        window=period
    ).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (
        100 / (
            1 + rs
        )
    )

    return rsi


def classify_ema_trend(
    close,
    ema20,
    ema50,
    ema200
):

    if (
        close > ema20
        and ema20 > ema50
        and ema50 > ema200
    ):

        return "BULLISH_TREND"

    if (
        close < ema20
        and ema20 < ema50
        and ema50 < ema200
    ):

        return "BEARISH_TREND"

    if (
        close > ema200
        and ema20 > ema50
    ):

        return "BULLISH_PULLBACK_OR_TRANSITION"

    if (
        close < ema200
        and ema20 < ema50
    ):

        return "BEARISH_PULLBACK_OR_TRANSITION"

    if close > ema200:

        return "ABOVE_EMA200_MIXED"

    if close < ema200:

        return "BELOW_EMA200_MIXED"

    return "RANGE"


def classify_momentum(
    rsi
):

    if rsi >= 60:
        return "BULLISH_MOMENTUM"

    if rsi <= 40:
        return "BEARISH_MOMENTUM"

    if rsi > 55:
        return "MILD_BULLISH_MOMENTUM"

    if rsi < 45:
        return "MILD_BEARISH_MOMENTUM"

    return "NEUTRAL_MOMENTUM"


def detect_recent_swings(
    df,
    left_bars=2,
    right_bars=2,
    lookback=150
):

    recent_df = df.tail(
        lookback
    ).copy()

    recent_df = recent_df.reset_index(
        drop=True
    )

    swing_highs = []
    swing_lows = []

    for index in range(
        left_bars,
        len(recent_df) - right_bars
    ):

        window = recent_df.iloc[
            index - left_bars:index + right_bars + 1
        ]

        current = recent_df.iloc[
            index
        ]

        current_high = current["high"]
        current_low = current["low"]

        if current_high >= window["high"].max():

            swing_highs.append({
                "index": index,
                "timestamp": str(
                    current["timestamp"]
                ),
                "price": safe_float(
                    current_high
                )
            })

        if current_low <= window["low"].min():

            swing_lows.append({
                "index": index,
                "timestamp": str(
                    current["timestamp"]
                ),
                "price": safe_float(
                    current_low
                )
            })

    return {
        "swing_highs": swing_highs,
        "swing_lows": swing_lows
    }


def classify_structure(
    swing_data
):

    swing_highs = swing_data["swing_highs"]
    swing_lows = swing_data["swing_lows"]

    if (
        len(swing_highs) < 2
        or len(swing_lows) < 2
    ):

        return {
            "structure": "INSUFFICIENT_SWINGS",
            "last_high": None,
            "previous_high": None,
            "last_low": None,
            "previous_low": None
        }

    previous_high = swing_highs[-2]
    last_high = swing_highs[-1]

    previous_low = swing_lows[-2]
    last_low = swing_lows[-1]

    higher_high = (
        last_high["price"]
        > previous_high["price"]
    )

    higher_low = (
        last_low["price"]
        > previous_low["price"]
    )

    lower_high = (
        last_high["price"]
        < previous_high["price"]
    )

    lower_low = (
        last_low["price"]
        < previous_low["price"]
    )

    if higher_high and higher_low:

        structure = "BULLISH_STRUCTURE"

    elif lower_high and lower_low:

        structure = "BEARISH_STRUCTURE"

    elif lower_high and higher_low:

        structure = "COMPRESSION_OR_RANGE"

    elif higher_high and lower_low:

        structure = "EXPANSION_VOLATILE"

    else:

        structure = "MIXED_STRUCTURE"

    return {
        "structure": structure,
        "last_high": last_high,
        "previous_high": previous_high,
        "last_low": last_low,
        "previous_low": previous_low
    }


def score_timeframe(
    ema_trend,
    momentum,
    structure
):

    score = 0

    if ema_trend == "BULLISH_TREND":
        score += 3

    elif ema_trend == "BEARISH_TREND":
        score -= 3

    elif ema_trend in [
        "BULLISH_PULLBACK_OR_TRANSITION",
        "ABOVE_EMA200_MIXED"
    ]:
        score += 1

    elif ema_trend in [
        "BEARISH_PULLBACK_OR_TRANSITION",
        "BELOW_EMA200_MIXED"
    ]:
        score -= 1

    if momentum == "BULLISH_MOMENTUM":
        score += 1

    elif momentum == "BEARISH_MOMENTUM":
        score -= 1

    elif momentum == "MILD_BULLISH_MOMENTUM":
        score += 0.5

    elif momentum == "MILD_BEARISH_MOMENTUM":
        score -= 0.5

    if structure == "BULLISH_STRUCTURE":
        score += 1

    elif structure == "BEARISH_STRUCTURE":
        score -= 1

    return score


def classify_final_bias(
    score
):

    if score >= 3:
        return "BULLISH"

    if score <= -3:
        return "BEARISH"

    if score > 0:
        return "BULLISH_TRANSITION"

    if score < 0:
        return "BEARISH_TRANSITION"

    return "NEUTRAL_RANGE"


def analyze_timeframe(
    df,
    timeframe_label
):

    df = normalize_df(
        df
    )

    if len(df) < 220:

        return {
            "timeframe": timeframe_label,
            "valid": False,
            "comment": "Datos insuficientes para EMA200 y estructura."
        }

    df["ema20"] = calculate_ema(
        df["close"],
        20
    )

    df["ema50"] = calculate_ema(
        df["close"],
        50
    )

    df["ema200"] = calculate_ema(
        df["close"],
        200
    )

    df["rsi"] = calculate_rsi(
        df["close"],
        14
    )

    latest = df.iloc[-1]

    close = safe_float(
        latest["close"]
    )

    ema20 = safe_float(
        latest["ema20"]
    )

    ema50 = safe_float(
        latest["ema50"]
    )

    ema200 = safe_float(
        latest["ema200"]
    )

    rsi = safe_float(
        latest["rsi"]
    )

    ema_trend = classify_ema_trend(
        close=close,
        ema20=ema20,
        ema50=ema50,
        ema200=ema200
    )

    momentum = classify_momentum(
        rsi
    )

    swing_data = detect_recent_swings(
        df,
        left_bars=2,
        right_bars=2,
        lookback=150
    )

    structure_data = classify_structure(
        swing_data
    )

    structure = structure_data[
        "structure"
    ]

    score = score_timeframe(
        ema_trend=ema_trend,
        momentum=momentum,
        structure=structure
    )

    final_bias = classify_final_bias(
        score
    )

    return {
        "timeframe": timeframe_label,
        "valid": True,
        "latest_timestamp": str(
            latest["timestamp"]
        ),
        "close": close,
        "ema20": ema20,
        "ema50": ema50,
        "ema200": ema200,
        "rsi": rsi,
        "ema_trend": ema_trend,
        "momentum": momentum,
        "structure": structure,
        "score": score,
        "final_bias": final_bias,
        "last_high": structure_data.get("last_high"),
        "previous_high": structure_data.get("previous_high"),
        "last_low": structure_data.get("last_low"),
        "previous_low": structure_data.get("previous_low")
    }


def is_bearish(
    bias
):

    return bias in [
        "BEARISH",
        "BEARISH_TRANSITION"
    ]


def is_bullish(
    bias
):

    return bias in [
        "BULLISH",
        "BULLISH_TRANSITION"
    ]


def build_regime_summary(
    analyses
):

    d1 = analyses.get(
        "1d",
        {}
    )

    h4 = analyses.get(
        "4h",
        {}
    )

    h1 = analyses.get(
        "1h",
        {}
    )

    m30 = analyses.get(
        "30m",
        {}
    )

    d1_bias = d1.get(
        "final_bias",
        "UNKNOWN"
    )

    h4_bias = h4.get(
        "final_bias",
        "UNKNOWN"
    )

    h1_bias = h1.get(
        "final_bias",
        "UNKNOWN"
    )

    m30_bias = m30.get(
        "final_bias",
        "UNKNOWN"
    )

    market_regime = "MIXED_OR_UNCLEAR"
    preferred_direction = "WAIT"
    trend_change_risk = "UNKNOWN"
    comment = "Contexto mixto. Esperar mayor claridad."

    if (
        is_bearish(d1_bias)
        and is_bearish(h4_bias)
        and is_bearish(h1_bias)
        and is_bearish(m30_bias)
    ):

        market_regime = "BEARISH_CONTINUATION"
        preferred_direction = "SHORT"
        trend_change_risk = "LOW"
        comment = "Todas las temporalidades relevantes mantienen sesgo bajista."

    elif (
        is_bearish(d1_bias)
        and is_bullish(h4_bias)
        and (
            is_bearish(h1_bias)
            or is_bearish(m30_bias)
        )
    ):

        market_regime = "BEARISH_CONTEXT_WITH_4H_PULLBACK"
        preferred_direction = "SHORT_AFTER_CONFIRMATION"
        trend_change_risk = "MEDIUM"
        comment = "Diario bajista con rebote/transición en 4H, pero 1H/30M muestran debilidad. Contexto compatible con short tras confirmación."

    elif (
        is_bearish(d1_bias)
        and is_bullish(h4_bias)
    ):

        market_regime = "POSSIBLE_4H_REVERSAL_INSIDE_1D_BEARISH_CONTEXT"
        preferred_direction = "WAIT"
        trend_change_risk = "HIGH"
        comment = "4H intenta revertir contra contexto diario bajista. No asumir cambio mayor sin confirmación adicional."

    elif (
        is_bearish(d1_bias)
        and is_bullish(h4_bias)
    ):

        market_regime = "POSSIBLE_4H_REVERSAL_INSIDE_1D_BEARISH_CONTEXT"
        preferred_direction = "WAIT"
        trend_change_risk = "HIGH"
        comment = "4H intenta revertir contra contexto diario bajista. No asumir cambio mayor sin confirmación."

    elif (
        is_bullish(d1_bias)
        and is_bullish(h4_bias)
        and is_bullish(h1_bias)
        and is_bullish(m30_bias)
    ):

        market_regime = "BULLISH_CONTINUATION"
        preferred_direction = "LONG"
        trend_change_risk = "LOW"
        comment = "Todas las temporalidades relevantes mantienen sesgo alcista."

    elif (
        is_bullish(d1_bias)
        and is_bullish(h4_bias)
        and (
            is_bearish(h1_bias)
            or is_bearish(m30_bias)
        )
    ):

        market_regime = "BULLISH_PULLBACK"
        preferred_direction = "LONG_AFTER_CONFIRMATION"
        trend_change_risk = "MEDIUM"
        comment = "Temporalidades mayores alcistas con retroceso en temporalidades menores."

    elif (
        is_bullish(d1_bias)
        and is_bearish(h4_bias)
    ):

        market_regime = "POSSIBLE_4H_DISTRIBUTION_INSIDE_1D_BULLISH_CONTEXT"
        preferred_direction = "WAIT"
        trend_change_risk = "HIGH"
        comment = "4H se debilita contra contexto diario alcista. Posible distribución o corrección."

    return {
        "market_regime": market_regime,
        "preferred_direction": preferred_direction,
        "trend_change_risk": trend_change_risk,
        "comment": comment,
        "bias_map": {
            "1d": d1_bias,
            "4h": h4_bias,
            "1h": h1_bias,
            "30m": m30_bias
        }
    }


def generate_mtf_trend_regime(
    timeframe_data
):

    analyses = {}

    for timeframe_label, df in timeframe_data.items():

        analyses[timeframe_label] = analyze_timeframe(
            df=df,
            timeframe_label=timeframe_label
        )

    summary = build_regime_summary(
        analyses
    )

    return {
        "summary": summary,
        "timeframes": analyses
    }


def format_float(
    value,
    decimals=2
):

    try:
        return f"{float(value):.{decimals}f}"

    except Exception:
        return str(value)


def build_mtf_regime_report_text(
    regime
):

    summary = regime["summary"]
    timeframes = regime["timeframes"]

    lines = []

    lines.append(
        "=== MTF TREND REGIME ENGINE V1 ==="
    )

    lines.append(
        ""
    )

    lines.append(
        f"market_regime: {summary.get('market_regime')}"
    )

    lines.append(
        f"preferred_direction: {summary.get('preferred_direction')}"
    )

    lines.append(
        f"trend_change_risk: {summary.get('trend_change_risk')}"
    )

    lines.append(
        f"comment: {summary.get('comment')}"
    )

    lines.append(
        ""
    )

    lines.append(
        "--- BIAS MAP ---"
    )

    for timeframe, bias in summary.get("bias_map", {}).items():

        lines.append(
            f"{timeframe}: {bias}"
        )

    for timeframe in [
        "1d",
        "4h",
        "1h",
        "30m"
    ]:

        analysis = timeframes.get(
            timeframe,
            {}
        )

        lines.append(
            ""
        )

        lines.append(
            f"--- TIMEFRAME {timeframe.upper()} ---"
        )

        if not analysis.get("valid"):

            lines.append(
                f"valid: False"
            )

            lines.append(
                f"comment: {analysis.get('comment')}"
            )

            continue

        lines.append(
            f"timestamp: {analysis.get('latest_timestamp')}"
        )

        lines.append(
            f"close: {format_float(analysis.get('close'))}"
        )

        lines.append(
            f"ema20: {format_float(analysis.get('ema20'))}"
        )

        lines.append(
            f"ema50: {format_float(analysis.get('ema50'))}"
        )

        lines.append(
            f"ema200: {format_float(analysis.get('ema200'))}"
        )

        lines.append(
            f"rsi: {format_float(analysis.get('rsi'))}"
        )

        lines.append(
            f"ema_trend: {analysis.get('ema_trend')}"
        )

        lines.append(
            f"momentum: {analysis.get('momentum')}"
        )

        lines.append(
            f"structure: {analysis.get('structure')}"
        )

        lines.append(
            f"score: {format_float(analysis.get('score'))}"
        )

        lines.append(
            f"final_bias: {analysis.get('final_bias')}"
        )

    lines.append(
        ""
    )

    lines.append(
        "Nota: Este módulo entrega contexto multi-timeframe. No ejecuta operaciones ni reemplaza la señal Fib V5."
    )

    return "\n".join(
        lines
    )