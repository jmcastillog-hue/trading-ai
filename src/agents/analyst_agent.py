def generate_analysis(
    asset,
    timeframe,
    probability_report,
    indicator_report,
    signal_report
):

    lines = []

    lines.append("=== ANALYST AGENT V1 ===\n")

    lines.append(
        f"Activo: {asset}"
    )

    lines.append(
        f"Timeframe: {timeframe}\n"
    )

    lines.append(
        f"Señal: {signal_report['signal']}"
    )

    lines.append(
        f"Confianza: {signal_report['confidence']}/100"
    )

    lines.append(
        f"Tendencia: {signal_report['trend']}"
    )

    lines.append(
        f"Momentum: {signal_report['momentum']}"
    )

    lines.append(
        f"Sesgo probabilístico: {signal_report['probability_bias']}\n"
    )

    lines.append("Lectura técnica:")

    if signal_report["trend"] == "BEARISH":
        lines.append(
            "- Las medias móviles muestran estructura bajista."
        )
    elif signal_report["trend"] == "BULLISH":
        lines.append(
            "- Las medias móviles muestran estructura alcista."
        )
    else:
        lines.append(
            "- Las medias móviles no muestran una estructura clara."
        )

    lines.append(
        f"- RSI actual: {indicator_report['rsi']:.2f}."
    )

    lines.append(
        f"- ATR actual: {indicator_report['atr']:.2f}."
    )

    lines.append(
        f"- Continuación alcista histórica: {probability_report['bullish_continuation']:.2f}%."
    )

    lines.append(
        f"- Continuación bajista histórica: {probability_report['bearish_continuation']:.2f}%."
    )

    lines.append("\nConclusión:")

    if signal_report["signal"] == "LONG":
        lines.append(
            "El sistema detecta un sesgo favorable a posiciones largas, pero requiere confirmación manual."
        )
    elif signal_report["signal"] == "SHORT":
        lines.append(
            "El sistema detecta un sesgo favorable a posiciones cortas, pero requiere confirmación manual."
        )
    else:
        lines.append(
            "El sistema recomienda esperar. No hay ventaja suficiente para tomar una decisión direccional."
        )

    lines.append(
        "\nNota: Este reporte no ejecuta operaciones ni constituye recomendación financiera."
    )

    return "\n".join(lines)