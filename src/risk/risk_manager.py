def calculate_short_pct(
    entry_price,
    exit_price
):

    return (
        (entry_price - exit_price)
        / entry_price
    ) * 100


def calculate_position_size(
    account_equity,
    risk_per_trade_pct,
    entry_price,
    stop_price
):

    risk_amount = account_equity * (
        risk_per_trade_pct / 100
    )

    stop_distance_pct = (
        (stop_price - entry_price)
        / entry_price
    ) * 100

    if stop_distance_pct <= 0:

        return {
            "valid": False,
            "comment": "Stop inválido para short. El stop debe estar por encima de la entrada."
        }

    position_notional = risk_amount / (
        stop_distance_pct / 100
    )

    btc_size = position_notional / entry_price

    return {
        "valid": True,
        "account_equity": account_equity,
        "risk_per_trade_pct": risk_per_trade_pct,
        "risk_amount": risk_amount,
        "entry_price": entry_price,
        "stop_price": stop_price,
        "stop_distance_pct": stop_distance_pct,
        "position_notional": position_notional,
        "btc_size": btc_size
    }


def calculate_v5_outcomes(
    entry_price,
    stop_price,
    tp1_price,
    tp2_price,
    tp1_close_weight=0.50
):

    stop_result_pct = calculate_short_pct(
        entry_price,
        stop_price
    )

    tp1_result_pct = calculate_short_pct(
        entry_price,
        tp1_price
    )

    tp2_result_pct = calculate_short_pct(
        entry_price,
        tp2_price
    )

    tp1_then_be_result_pct = (
        tp1_result_pct * tp1_close_weight
    )

    tp1_then_tp2_result_pct = (
        tp1_result_pct * tp1_close_weight
    ) + (
        tp2_result_pct * (1 - tp1_close_weight)
    )

    return {
        "stop_result_pct": stop_result_pct,
        "tp1_result_pct": tp1_result_pct,
        "tp2_result_pct": tp2_result_pct,
        "tp1_then_be_result_pct": tp1_then_be_result_pct,
        "tp1_then_tp2_result_pct": tp1_then_tp2_result_pct
    }


def build_risk_report(
    alert,
    account_equity=1000,
    risk_per_trade_pct=1.0,
    max_allowed_stop_pct=5.0,
    leverage=1.0
):

    if not alert.get("entry_signal"):

        return {
            "risk_check": "NO_ENTRY_SIGNAL",
            "comment": "No hay señal de entrada activa. No se calcula tamaño de posición."
        }

    entry_price = float(
        alert["entry_price"]
    )

    stop_price = float(
        alert["stop_price"]
    )

    tp1_price = float(
        alert["tp1_price"]
    )

    tp2_price = float(
        alert["target_price"]
    )

    tp1_close_weight = float(
        alert["tp1_close_weight"]
    )

    position = calculate_position_size(
        account_equity=account_equity,
        risk_per_trade_pct=risk_per_trade_pct,
        entry_price=entry_price,
        stop_price=stop_price
    )

    if not position["valid"]:

        return {
            "risk_check": "INVALID",
            "comment": position["comment"]
        }

    outcomes = calculate_v5_outcomes(
        entry_price=entry_price,
        stop_price=stop_price,
        tp1_price=tp1_price,
        tp2_price=tp2_price,
        tp1_close_weight=tp1_close_weight
    )

    required_margin = (
        position["position_notional"] / leverage
        if leverage > 0
        else position["position_notional"]
    )

    warnings = []

    if position["stop_distance_pct"] > max_allowed_stop_pct:

        warnings.append(
            "La distancia al stop es alta. Reducir tamaño o esperar mejor entrada."
        )

    if required_margin > account_equity:

        warnings.append(
            "El margen requerido supera el capital configurado."
        )

    if leverage > 1:

        warnings.append(
            "El apalancamiento amplifica pérdidas. Validar manualmente antes de operar."
        )

    return {
        "risk_check": "OK",
        "account_equity": account_equity,
        "risk_per_trade_pct": risk_per_trade_pct,
        "risk_amount": position["risk_amount"],
        "entry_price": entry_price,
        "stop_price": stop_price,
        "tp1_price": tp1_price,
        "tp2_price": tp2_price,
        "stop_distance_pct": position["stop_distance_pct"],
        "position_notional": position["position_notional"],
        "btc_size": position["btc_size"],
        "leverage": leverage,
        "required_margin": required_margin,
        "outcomes": outcomes,
        "warnings": warnings
    }