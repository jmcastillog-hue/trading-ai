def calculate_win_rate(trades):

    if len(trades) == 0:
        return 0

    wins = [
        trade for trade in trades
        if trade["result_pct"] > 0
    ]

    return len(wins) / len(trades) * 100


def calculate_expectancy(trades):

    if len(trades) == 0:
        return 0

    total = sum(
        trade["result_pct"]
        for trade in trades
    )

    return total / len(trades)


def calculate_profit_factor(trades):

    gross_profit = sum(
        trade["result_pct"]
        for trade in trades
        if trade["result_pct"] > 0
    )

    gross_loss = abs(
        sum(
            trade["result_pct"]
            for trade in trades
            if trade["result_pct"] < 0
        )
    )

    if gross_loss == 0:
        return 0

    return gross_profit / gross_loss


def calculate_max_drawdown(trades):

    equity = 0
    peak = 0
    max_drawdown = 0

    for trade in trades:

        equity += trade["result_pct"]

        if equity > peak:
            peak = equity

        drawdown = equity - peak

        if drawdown < max_drawdown:
            max_drawdown = drawdown

    return max_drawdown


def generate_performance_report(trades):

    wins = [
        trade for trade in trades
        if trade["result_pct"] > 0
    ]

    losses = [
        trade for trade in trades
        if trade["result_pct"] <= 0
    ]

    return {
        "total_trades": len(trades),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": calculate_win_rate(trades),
        "expectancy": calculate_expectancy(trades),
        "profit_factor": calculate_profit_factor(trades),
        "max_drawdown": calculate_max_drawdown(trades)
    }