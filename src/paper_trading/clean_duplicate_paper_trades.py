import os
import sys

import pandas as pd

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            ".."
        )
    )
)

from src.paper_trading.paper_trade_logger import (
    load_paper_trades,
    save_paper_trades,
    setup_key_from_record,
    OPEN_STATUSES,
    PAPER_TRADES_FILE
)


def clean_duplicate_open_trades():

    df = load_paper_trades(
        PAPER_TRADES_FILE
    )

    if len(df) == 0:

        print(
            "No hay paper trades registrados."
        )

        return

    kept_rows = []
    seen_open_setups = set()
    removed_count = 0

    for _, row in df.iterrows():

        row_dict = row.to_dict()

        status = row_dict.get(
            "status",
            ""
        )

        setup_key = setup_key_from_record(
            row_dict
        )

        if status in OPEN_STATUSES:

            if setup_key in seen_open_setups:

                removed_count += 1
                continue

            seen_open_setups.add(
                setup_key
            )

        kept_rows.append(
            row_dict
        )

    cleaned_df = pd.DataFrame(
        kept_rows
    )

    save_paper_trades(
        cleaned_df,
        PAPER_TRADES_FILE
    )

    print(
        "\n=== CLEAN DUPLICATE PAPER TRADES ===\n"
    )

    print(
        f"original_trades: {len(df)}"
    )

    print(
        f"removed_duplicates: {removed_count}"
    )

    print(
        f"final_trades: {len(cleaned_df)}"
    )

    print(
        f"file: {PAPER_TRADES_FILE}"
    )


if __name__ == "__main__":
    clean_duplicate_open_trades()