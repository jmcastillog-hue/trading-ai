def find_equal_highs(
    df,
    lookback=96,
    tolerance_pct=0.15,
    min_touches=2
):

    recent_data = df.tail(lookback)

    highs = recent_data["high"].tolist()

    clusters = []

    for price in highs:

        cluster = [
            h for h in highs
            if abs(h - price) / price * 100 <= tolerance_pct
        ]

        if len(cluster) >= min_touches:

            level = sum(cluster) / len(cluster)

            clusters.append({
                "level": float(level),
                "touches": len(cluster)
            })

    unique_clusters = []

    for cluster in clusters:

        exists = False

        for existing in unique_clusters:

            if (
                abs(existing["level"] - cluster["level"])
                / cluster["level"]
                * 100
                <= tolerance_pct
            ):
                exists = True
                break

        if not exists:
            unique_clusters.append(cluster)

    unique_clusters = sorted(
        unique_clusters,
        key=lambda x: x["level"],
        reverse=True
    )

    return unique_clusters