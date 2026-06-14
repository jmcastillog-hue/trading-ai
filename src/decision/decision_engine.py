def evaluate_decision(
    alert,
    risk_report,
    preferred_max_stop_pct=5.0,
    hard_max_stop_pct=10.0,
    max_margin_usage_pct=20.0,
    allow_real_trade=False
):

    setup_active = alert.get(
        "setup_active",
        False
    )

    entry_signal = alert.get(
        "entry_signal",
        False
    )

    state = alert.get(
        "state",
        "UNKNOWN"
    )

    if not setup_active:

        return {
            "decision": "NO_ACTION",
            "permission": "BLOCKED",
            "reason": "No hay setup activo.",
            "state": state
        }

    if not entry_signal:

        return {
            "decision": "WATCH_ONLY",
            "permission": "ALERT_ONLY",
            "reason": "Hay setup activo, pero todavía no existe señal de entrada.",
            "state": state
        }

    if risk_report.get("risk_check") != "OK":

        return {
            "decision": "BLOCKED",
            "permission": "BLOCKED",
            "reason": risk_report.get(
                "comment",
                "El risk manager no aprobó la operación."
            ),
            "state": state
        }

    account_equity = float(
        risk_report["account_equity"]
    )

    required_margin = float(
        risk_report["required_margin"]
    )

    stop_distance_pct = float(
        risk_report["stop_distance_pct"]
    )

    margin_usage_pct = (
        required_margin / account_equity
    ) * 100

    warnings = []

    if stop_distance_pct > preferred_max_stop_pct:

        warnings.append(
            "La distancia al stop supera el máximo preferido."
        )

    if stop_distance_pct > hard_max_stop_pct:

        return {
            "decision": "BLOCKED",
            "permission": "BLOCKED",
            "reason": "La distancia al stop supera el máximo duro permitido.",
            "state": state,
            "stop_distance_pct": stop_distance_pct,
            "margin_usage_pct": margin_usage_pct,
            "warnings": warnings
        }

    if margin_usage_pct > max_margin_usage_pct:

        return {
            "decision": "BLOCKED",
            "permission": "BLOCKED",
            "reason": "El margen requerido supera el máximo permitido sobre la cuenta.",
            "state": state,
            "stop_distance_pct": stop_distance_pct,
            "margin_usage_pct": margin_usage_pct,
            "warnings": warnings
        }

    if not allow_real_trade:

        return {
            "decision": "PAPER_TRADE_ONLY",
            "permission": "SIMULATION_ONLY",
            "reason": "La señal es válida, pero el sistema está configurado en modo no operativo.",
            "state": state,
            "stop_distance_pct": stop_distance_pct,
            "margin_usage_pct": margin_usage_pct,
            "warnings": warnings,
            "suggested_action": "Registrar la señal y hacer seguimiento manual."
        }

    if stop_distance_pct > preferred_max_stop_pct:

        return {
            "decision": "SMALL_SIZE_ONLY",
            "permission": "MANUAL_REVIEW_REQUIRED",
            "reason": "Señal válida, pero stop amplio. Solo considerar tamaño reducido y revisión manual.",
            "state": state,
            "stop_distance_pct": stop_distance_pct,
            "margin_usage_pct": margin_usage_pct,
            "warnings": warnings,
            "suggested_action": "Reducir riesgo por trade o esperar mejor entrada."
        }

    return {
        "decision": "TRADE_CANDIDATE",
        "permission": "MANUAL_REVIEW_REQUIRED",
        "reason": "Señal válida con riesgo dentro de parámetros. Requiere revisión manual antes de operar.",
        "state": state,
        "stop_distance_pct": stop_distance_pct,
        "margin_usage_pct": margin_usage_pct,
        "warnings": warnings,
        "suggested_action": "Validar contexto de mercado, liquidez y tamaño antes de cualquier ejecución."
    }


def build_decision_report_text(
    alert,
    risk_report,
    decision
):

    lines = []

    lines.append(
        "=== FIB V5 DECISION ENGINE ==="
    )

    lines.append(
        ""
    )

    lines.append(
        f"decision: {decision.get('decision')}"
    )

    lines.append(
        f"permission: {decision.get('permission')}"
    )

    lines.append(
        f"state: {decision.get('state')}"
    )

    lines.append(
        f"reason: {decision.get('reason')}"
    )

    suggested_action = decision.get(
        "suggested_action"
    )

    if suggested_action:

        lines.append(
            f"suggested_action: {suggested_action}"
        )

    lines.append(
        ""
    )

    lines.append(
        "--- ALERTA ---"
    )

    lines.append(
        f"setup_active: {alert.get('setup_active')}"
    )

    lines.append(
        f"entry_signal: {alert.get('entry_signal')}"
    )

    lines.append(
        f"bias: {alert.get('bias')}"
    )

    lines.append(
        f"current_price: {alert.get('current_price')}"
    )

    if alert.get("entry_signal"):

        lines.append(
            f"entry_price: {alert.get('entry_price')}"
        )

        lines.append(
            f"stop_price: {alert.get('stop_price')}"
        )

        lines.append(
            f"tp1_price: {alert.get('tp1_price')}"
        )

        lines.append(
            f"tp2_price: {alert.get('target_price')}"
        )

    lines.append(
        ""
    )

    lines.append(
        "--- RIESGO ---"
    )

    lines.append(
        f"risk_check: {risk_report.get('risk_check')}"
    )

    if risk_report.get("risk_check") == "OK":

        lines.append(
            f"account_equity: {risk_report.get('account_equity')}"
        )

        lines.append(
            f"risk_per_trade_pct: {risk_report.get('risk_per_trade_pct')}"
        )

        lines.append(
            f"risk_amount: {risk_report.get('risk_amount')}"
        )

        lines.append(
            f"stop_distance_pct: {risk_report.get('stop_distance_pct')}"
        )

        lines.append(
            f"position_notional: {risk_report.get('position_notional')}"
        )

        lines.append(
            f"btc_size: {risk_report.get('btc_size')}"
        )

        lines.append(
            f"required_margin: {risk_report.get('required_margin')}"
        )

        outcomes = risk_report.get(
            "outcomes",
            {}
        )

        lines.append(
            ""
        )

        lines.append(
            "--- RESULTADOS POTENCIALES ---"
        )

        lines.append(
            f"stop_directo_pct: {outcomes.get('stop_result_pct')}"
        )

        lines.append(
            f"tp1_pct: {outcomes.get('tp1_result_pct')}"
        )

        lines.append(
            f"tp2_pct: {outcomes.get('tp2_result_pct')}"
        )

        lines.append(
            f"tp1_then_be_pct: {outcomes.get('tp1_then_be_result_pct')}"
        )

        lines.append(
            f"tp1_then_tp2_pct: {outcomes.get('tp1_then_tp2_result_pct')}"
        )

    warnings = decision.get(
        "warnings",
        []
    )

    if len(warnings) > 0:

        lines.append(
            ""
        )

        lines.append(
            "--- ADVERTENCIAS ---"
        )

        for warning in warnings:

            lines.append(
                f"- {warning}"
            )

    lines.append(
        ""
    )

    lines.append(
        "Nota: Este módulo no ejecuta operaciones. Solo clasifica la señal y el riesgo."
    )

    return "\n".join(
        lines
    )