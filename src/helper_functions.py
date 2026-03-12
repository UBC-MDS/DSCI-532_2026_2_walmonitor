import re
import pandas as pd

def to_snake_case(name: str) -> str:
    """Convert a string to snake_case, suitable for column names."""
    s = str(name).strip().lower()
    s = s.replace("%", "pct")
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def filter_data(df, start, end, branch, COMP_COL, agg_time, agg_method):
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end) + pd.Timedelta(days=1)
    mask = (df["Date"] >= start_ts) & (df["Date"] < end_ts)


    if branch != "all":
        mask &= df["Branch"] == branch

    SALES_COL = "Total"

    df = df.loc[mask, ["Date", COMP_COL, SALES_COL]].copy()

    if agg_time == "day":
        df["time"] = df["Date"].dt.floor("D")
    else:
        df["time"] = df["Date"].dt.to_period("W-SAT").dt.start_time

    out = (
        df.groupby(["time", COMP_COL], as_index=False)[SALES_COL]
        .agg(agg_method)
        .sort_values(["time", COMP_COL])
        .reset_index(drop=True)
    )

    out = out.rename(columns={c: to_snake_case(c) for c in out.columns})

    return out