import re
import pandas as pd
from datetime import date
from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_altair
import altair as alt
alt.data_transformers.enable('vegafusion')
import warnings
warnings.filterwarnings('ignore', module='altair')
import pandas as pd
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
    "all": "All Branches / Cities",
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
BASE_COLS = ["Date", "Branch"] + list(METRIC_CHOICES.keys())
DATA_BASE = DATA_RAW[BASE_COLS].copy()  # Crop unused columns


## Helper functions
def to_snake_case(name: str) -> str:
    """Convert a string to snake_case, suitable for column names."""
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
                "input_metrics",
                "Metrics",
                choices=METRIC_CHOICES,
                selected=DEFAULT_METRICS,
            ),
            # Aggregation: day vs week
            ui.input_radio_buttons(
                "input_agg",
                "Aggregation",
                choices=AGG_CHOICES,
                selected=DEFAULT_AGG,
                inline=True,
            ),
            # Aggregation method: sum vs mean
            ui.input_radio_buttons(
                "input_agg_method",
                "Aggregation method",
                choices=METHOD_CHOICES,
                selected=DEFAULT_METHOD,
                inline=True,
            ),
            # Date range
            ui.input_date_range(
                "input_date_range",
                "Date range",
                start=DEFAULT_START,
                end=DEFAULT_END,
                min=DEFAULT_START,
                max=DEFAULT_END,
            ),
            # Branch dropdown
            ui.input_select(
                "input_branch",
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
                                "height: 400px; display:flex; align-items:center; "
                                "justify-content:center; color:#6b7280; "
                                "border: 1px dashed #d1d5db; border-radius: 10px;"
                            )
                        },
                        output_widget("time_series_line"),
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

# ── helpers ─────────────────────────────────────────────────────────
def line_plot(df, metrics, category) -> alt.Chart:
    df = df.copy()
    
    df = df.reset_index()
    
    lines = []

    branch_map = {'A': 'Yangon', 'B': 'Mandalay', 'C': 'Naypyitaw'}

    if category in branch_map.keys():
        category = branch_map[category]
    
    for met in metrics:
        met_sc = to_snake_case(met)
    
        if met_sc =='gross_margin_percentage':
             unit = '%'
        else:
            unit = 'K'

        df_met = df[df['metric'] == met_sc]

        df_met['metric'] = met.title()

        line = alt.Chart(df_met).mark_line().encode(
            x=alt.X('date:T', axis=alt.Axis(labelAngle=270)),
            y=alt.Y('value:Q', title=met.title(), axis=alt.Axis(labelExpr=f"datum.value + '{unit}'")),
            color=alt.Color('metric:N', legend=alt.Legend(title=''))
        )
        
        lines.append(line)
    
    if category == 'all':
        title = f'Time Series Across {category.title()} Cities'
    else:
        title = f'Time Series for the City of {category.title()}'

    comb = alt.layer(*lines).properties(
        width=1400, height=300,
        title=title
    )

    return comb 

# ── server ──────────────────────────────────────────────────────────
def server(input, output, session):
    @reactive.calc
    def df_filtered() -> pd.DataFrame:
        """
        Apply filters and aggregations to the base data,
        returning the processed DataFrame.
        """
        df = DATA_BASE.copy()

        # Filter rows by date range
        start, end = input.input_date_range()
        start_ts = pd.Timestamp(start)
        end_ts = pd.Timestamp(end) + pd.Timedelta(days=1)
        df = df[(df["Date"] >= start_ts) & (df["Date"] < end_ts)]

        # Filter rows by branch
        branch = input.input_branch()
        if branch != "all":
            df = df[df["Branch"] == branch]

        # Filter columns by metrics
        metrics = list(input.input_metrics() or [])
        if not metrics:
            return pd.DataFrame(columns=["date"])

        df = df[["Date"] + metrics].copy()

        # Aggregate by day/week and sum/mean
        if input.input_agg() == "day":
            df["date"] = df["Date"].dt.floor("D")
        else:
            df["date"] = (
                df["Date"].dt.to_period("W-SAT").dt.start_time
            )  # Week starting Sunday

        out = df.groupby("date", as_index=False)[metrics].agg(input.input_agg_method())
        out = out.sort_values("date").reset_index(drop=True)
        out = out.rename(columns={c: to_snake_case(c) for c in out.columns})

        return out

    # TODO: to be commented out before release
    @output
    @render.data_frame
    def tbl_filtered():
        """For debug only: Display the filtered DataFrame"""
        return render.DataGrid(df_filtered(), height="280px")

    # TODO: to be commented out before release
    @output
    @render.text
    def debug_inputs():
        """For debug only: Display the current input values"""
        return (
            f"metrics = {list(input.input_metrics() or [])}\n"
            f"aggregation = {input.input_agg()}\n"
            f"method = {input.input_agg_method()}\n"
            f"date_range = {input.input_date_range()}\n"
            f"branch = {input.input_branch()}\n"
            f"number of filtered rows = {len(df_filtered())}\n"
        )

    @reactive.calc
    def resample():

        df = df_filtered()

        df['date'] =  pd.to_datetime(df['date'], format='%Y-%m-%d')

        metric = input.input_metrics()

        city = input.input_branch()
            
        if input.input_agg() == 'week':
            resample_freq = 'W'
        else:
            resample_freq = 'D'

        # Make date the index for resampling by week 
        df = df.set_index('date')
        
        # Resample metric by summing or averaging across the chosen resampling period
        # Note that if you resample on entire data frame metric per category info is lost
        df_lst = []

        for met in metric:
            met = to_snake_case(met)
            if met == 'gross_margin_percentage':
                # for percentage average instead of summing
                col_df = df.resample(resample_freq)[met].mean()
                col_df = col_df.reset_index()
                col_df['metric'] = met
                # Put df in long format for time series plot
                col_df = col_df.rename(columns={met: 'value'})
                df_lst.append(col_df)
            else:
                # sum metrics that are totaled across resample period
                col_df = df.resample(resample_freq)[met].sum()
                col_df = col_df.reset_index()
                col_df['metric'] = met
                # Put df in long format for time series plot
                col_df = col_df.rename(columns={met: 'value'})
                df_lst.append(col_df)
            
        # Concatenate the resampled data frames for line plot
        concat_df = pd.concat(df_lst)

        return concat_df, metric, city

    @output
    @render_altair
    def time_series_line():

        resamp_df, metric, city = resample()

        line = line_plot(resamp_df, metric, city)

        return line

app = App(app_ui, server)
