import re
import pandas as pd
from datetime import date
from pathlib import Path

from shiny import App, ui, render, reactive


## Input choices and defaults
METRIC_CHOICES = {
    # "column name": "label",
    "Total": "Total Sales",
    "gross income": "Gross Income",
    "cogs": "COGS",
    "gross margin percentage": "Margin %",
}
DEFAULT_METRICS = ["Total", "gross income"]

AGG_CHOICES = {"day": "Day", "week": "Week"}
DEFAULT_AGG = "day"

METHOD_CHOICES = {"sum": "Sum", "mean": "Mean"}
DEFAULT_METHOD = "sum"

BRANCH_CHOICES = {
    "all": "All Branches",
    "A": "Branch A",
    "B": "Branch B",
    "C": "Branch C",
}
DEFAULT_BRANCH = "all"

DEFAULT_START = date(2019, 1, 1)
DEFAULT_END = date(2019, 3, 30)


## Load data
DATA_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "raw" / "walmart_sales_data.csv"
)
DATA_RAW = pd.read_csv(DATA_PATH)
DATA_RAW["Date"] = pd.to_datetime(DATA_RAW["Date"])

# Crop unused columns for this view (hard-coded)
BASE_COLS = ["Date", "Branch"] + list(METRIC_CHOICES.keys())
DATA_BASE = DATA_RAW[BASE_COLS].copy()


def to_snake_case(name: str) -> str:
    s = str(name).strip().lower()
    s = s.replace("%", "pct")
    s = re.sub(r"[^\w\s]", " ", s) 
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


## App interface
app_ui = ui.page_fluid(
    ui.div(
        ui.h2("Walmonitor 0.2.0"),
        style="margin-top: 24px;",
    ),
    # Control panel on the left
    ui.layout_sidebar(
        ui.sidebar(
            ui.h4("Controls"),
            # Metrics checkboxes
            ui.input_checkbox_group(
                "metrics",
                "Metrics",
                choices=METRIC_CHOICES,
                selected=DEFAULT_METRICS,
            ),
            # Aggregation: day vs week
            ui.input_radio_buttons(
                "agg",
                "Aggregation",
                choices=AGG_CHOICES,
                selected=DEFAULT_AGG,
                inline=True,
            ),
            # Rolling average: none vs 7 days
            ui.input_radio_buttons(
                "method",
                "Aggregation method",
                choices=METHOD_CHOICES,
                selected=DEFAULT_METHOD,
                inline=True,
            ),
            # Date range
            ui.input_date_range(
                "date_range",
                "Date range",
                start=DEFAULT_START,
                end=DEFAULT_END,
                min=DEFAULT_START,
                max=DEFAULT_END,
            ),
            # Branch dropdown
            ui.input_select(
                "branch",
                "Branch",
                choices=BRANCH_CHOICES,
                selected=DEFAULT_BRANCH,
            ),
            width=320,
        ),
        # View panel on the right
        ui.div(
            ui.layout_columns(
                ui.card(
                    ui.card_header("Metrics Over Time"),
                    ui.div(
                        {
                            "style": (
                                "height: 260px; display:flex; align-items:center; "
                                "justify-content:center; color:#6b7280; "
                                "border: 1px dashed #d1d5db; border-radius: 10px;"
                            )
                        },
                        "Time-series overlay lines",
                    ),
                ),
                col_widths=(12,),
            ),
            ui.layout_columns(
                ui.card(
                    ui.card_header("Sales Mix Over Time"),
                    ui.div(
                        {
                            "style": (
                                "height: 300px; display:flex; align-items:center; "
                                "justify-content:center; color:#6b7280; "
                                "border: 1px dashed #d1d5db; border-radius: 10px;"
                            )
                        },
                        "Stacked filled area chart",
                    ),
                ),
                ui.card(
                    ui.card_header("Ranked Product Lines"),
                    ui.div(
                        {
                            "style": (
                                "height: 300px; display:flex; align-items:center; "
                                "justify-content:center; color:#6b7280; "
                                "border: 1px dashed #d1d5db; border-radius: 10px;"
                            )
                        },
                        "Ranked horizontal bars",
                    ),
                ),
                col_widths=(7, 5),
            ),
            # TODO: to be commented out before release
            ui.hr(),
            ui.layout_columns(
                ui.card(
                    ui.card_header("df_filtered (debug)"),
                    ui.output_data_frame("tbl_filtered"),
                ),
                ui.card(
                    ui.card_header("Inputs (debug)"),
                    ui.output_text_verbatim("debug_inputs"),
                ),
                col_widths=(7, 5),
            ),
        ),
    ),
)


## Server
def server(input, output, session):
    @reactive.calc
    def df_filtered() -> pd.DataFrame:
        df = DATA_BASE.copy()

        # Filter rows by date range
        start, end = input.date_range()
        start_ts = pd.Timestamp(start)
        end_ts = pd.Timestamp(end) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
        df = df[(df["Date"] >= start_ts) & (df["Date"] <= end_ts)]

        # Filter rows by branch
        branch = input.branch()
        if branch != "all":
            df = df[df["Branch"] == branch]

        # Filter columns by metrics
        metrics = list(input.metrics() or [])
        if not metrics:
            return pd.DataFrame(columns=["time"])

        df = df[["Date"] + metrics].copy()

        # Aggregate by day/week and sum/mean
        if input.agg() == "day":
            df["date"] = df["Date"].dt.floor("D")
        else:
            df["date"] = (
                df["Date"].dt.to_period("W-SAT").dt.start_time
            )  # Week starting Sunday

        out = df.groupby("date", as_index=False)[metrics].agg(input.method())
        out = out.sort_values("date").reset_index(drop=True)
        out = out.rename(columns={c: to_snake_case(c) for c in out.columns})

        return out

    # TODO: to be commented out before release
    @output
    @render.data_frame
    def tbl_filtered():
        return render.DataGrid(df_filtered(), height="280px")

    # TODO: to be commented out before release
    @output
    @render.text
    def debug_inputs():
        return (
            f"metrics = {list(input.metrics() or [])}\n"
            f"aggregation = {input.agg()}\n"
            f"method = {input.method()}\n"
            f"date_range = {input.date_range()}\n"
            f"branch = {input.branch()}\n"
            f"number of filtered rows = {len(df_filtered())}\n"
        )


app = App(app_ui, server)
