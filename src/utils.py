"""
Helper functions for the Walmonitor Dashboard
- to_snake_case() : convert string to snake case
- filter_data() : filter dataframe for given input
"""

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
    """Filter dataframe to contain only specific rows and columns.

    Parameters
    ----------
    df : pd.DataFrame
        The data to be filtered. Needs to contain the following columns : "Date", "Branch", "Total",  
        and the chosen COMP_COL.
    start : str
        The start of the desired date range.
    end : str
        The end of the desired date range.
    branch : str
        The desired branch. Options include "A" (Yangon), "B" (Mandalay), "C" (Naypyitaw), "all".
    COMP_COL : str
        The categories we want to compare. Options include "Product line", "Payment", "Gender", "Customer type".
    agg_time : str
        The period we want to group by. Options include "day", "week".
    agg_method : str
        The method we want to aggregate by. Options include "mean", "sum"

    Returns
    -------
    pd.DataFrame
        The filtered dataframe.

    Examples
    --------
    >>> filter_data(df, pd.to_datetime('2019-01-01'), pd.to_datetime('2019-02-01'), 'A', 'Gender', 'day', 'mean')


    """
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