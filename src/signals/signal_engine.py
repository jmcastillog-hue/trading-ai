def detect_trend(indicators):

    ema20 = indicators["ema20"]
    ema50 = indicators["ema50"]
    ema200 = indicators["ema200"]

    if ema20 > ema50 > ema200:
        return "BULLISH"

    if ema20 < ema50 < ema200:
        return "BEARISH"

    return "NEUTRAL"


def detect_momentum(indicators):

    rsi = indicators["rsi"]

    if rsi >= 55:
        return "POSITIVE"

    if rsi <= 45:
        return "NEGATIVE"

    return "NEUTRAL"


def detect_probability_bias(probabilities):

    bull = probabilities["bullish_continuation"]
    bear = probabilities["bearish_continuation"]

    if bull > bear:
        return "BULLISH"

    if bear > bull:
        return "BEARISH"

    return "NEUTRAL"


def calculate_confidence(
    trend,
    momentum,
    probability_bias
):

    score = 50

    if trend == "BULLISH":
        score += 15
    elif trend == "BEARISH":
        score -= 15

    if momentum == "POSITIVE":
        score += 15
    elif momentum == "NEGATIVE":
        score -= 15

    if probability_bias == "BULLISH":
        score += 10
    elif probability_bias == "BEARISH":
        score -= 10

    return max(0, min(100, score))


def generate_signal(
    probabilities,
    indicators
):

    trend = detect_trend(indicators)

    momentum = detect_momentum(indicators)

    probability_bias = detect_probability_bias(
        probabilities
    )

    confidence = calculate_confidence(
        trend,
        momentum,
        probability_bias
    )

    if confidence >= 65:
        signal = "LONG"

    elif confidence <= 35:
        signal = "SHORT"

    else:
        signal = "WAIT"

    return {
        "signal": signal,
        "confidence": confidence,
        "trend": trend,
        "momentum": momentum,
        "probability_bias": probability_bias
    }