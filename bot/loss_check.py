"""Calculate metal loss % per department and flag the ones over the limit.

Loss (g) = issue - return
Loss %   = loss / issue * 100   (per department, for one day)

Run:
    python -m bot.loss_check                     # latest day, from the Google Sheet
    python -m bot.loss_check --date 2026-09-29   # a chosen day
    python -m bot.loss_check --local             # use data/dummy_metal_loss.csv
"""

import argparse

import pandas as pd

from bot import config


def load_data(local=False):
    """Read the production data from the Google Sheet (or the local CSV)."""
    source = config.LOCAL_CSV if local else config.SHEET_CSV_URL
    df = pd.read_csv(source, parse_dates=["date"])
    return df


def department_loss(df, day=None):
    """Return loss % per department for one day (the latest day if not given)."""
    day = pd.Timestamp(day) if day else df["date"].max()
    day_df = df[df["date"] == day]
    if day_df.empty:
        raise ValueError(f"No data for {day.date()}")

    result = (
        day_df.groupby("department", as_index=False)
        .agg(issue_g=("issue_weight_g", "sum"), return_g=("return_weight_g", "sum"))
    )
    result["loss_g"] = result["issue_g"] - result["return_g"]
    result["loss_pct"] = result["loss_g"] / result["issue_g"] * 100
    result["over_limit"] = result["loss_pct"] > config.LOSS_LIMIT_PCT
    result = result.sort_values("loss_pct", ascending=False).reset_index(drop=True)
    return day, result


def flagged(result):
    """Only the departments over the limit."""
    return result[result["over_limit"]]


def main():
    parser = argparse.ArgumentParser(description="Check metal loss % per department.")
    parser.add_argument("--date", help="Day to check (YYYY-MM-DD). Default: latest day.")
    parser.add_argument("--local", action="store_true", help="Use the local CSV file.")
    args = parser.parse_args()

    df = load_data(local=args.local)
    day, result = department_loss(df, args.date)

    print(f"\nMetal loss for {day.date()} (limit {config.LOSS_LIMIT_PCT}%)\n")
    table = result.copy()
    table["over_limit"] = table["over_limit"].map({True: "YES", False: ""})
    print(table.to_string(index=False, float_format=lambda x: f"{x:.2f}"))

    over = flagged(result)
    print()
    if over.empty:
        print("All OK - no department is over the limit.")
    else:
        print(f"{len(over)} department(s) over the limit:")
        for row in over.itertuples():
            print(f"  - {row.department}: {row.loss_pct:.2f}% ({row.loss_g:.2f} g lost)")


if __name__ == "__main__":
    main()
