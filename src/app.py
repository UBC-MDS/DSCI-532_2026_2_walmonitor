import re
import pandas as pd
from datetime import date
from pathlib import Path

from shiny import App, ui, render, reactive

from shiny import App, ui, render
import altair as alt
import pandas as pd
from shinywidgets import render_altair, output_widget

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
                    ui.layout_columns(
                        ui.panel_conditional(   # Used Claude to suggest which ui.* to use for adding a slider conditional on user input
                            "input.agg === 'day'", # If the user chooses to aggregate by day, then use a slider to determine what date range to show
                            ui.input_slider(
                                "range",
                                "Select a date range:",
                                min = pd.to_datetime('2019-01-01'),
                                max = pd.to_datetime('2019-03-31'),
                                value = [pd.to_datetime('2019-02-01'),pd.to_datetime('2019-02-28')],
                                ticks = True,
                                step = 1,
                                time_format="%Y-%m-%d"
                            ),
                              ui.help_text(
                                  "Suggested range size : 1 month" 
                                  ),
                        ),
                        ui.input_select( # User decides what comparison they want highlighted on the plot
                            "comp",
                            "Compare",
                            choices={
                                "Product line": "Product line",
                                "Payment": "Payment type",
                                "Gender": "Gender",
                                "Customer type": "Customer type",
                            },
                            selected="product_line",
                        ),
                        col_widths=[7, 5]
                    ),
                    output_widget("stack_plot"),
                    full_screen=True
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

    # @output
    # @render.text
    # def debug_inputs():
    #     return (
    #         f"metrics = {list(input.metrics())}\n"
    #         f"aggregation = {input.agg()}\n"
    #         f"rolling_avg = {input.roll()}\n"
    #         f"date_range = {input.date_range()}\n"
    #         f"branch = {input.branch()}\n"
    #     )
    @render_altair
    def stack_plot():
        """
        This function uses user input to determine what to compare in the plot (Product line, Customer type, Payment type, Gender) 
        and what date range to choose from if the values are aggregated by day.
        
        TODO : add data from reactive calc 
        """
        walmart_df = pd.read_csv('data/raw/walmart_sales_data.csv')
        walmart_df['Date']=pd.to_datetime(walmart_df['Date'])
        input_comparison = input.comp()

        # If user chooses to aggregate by day 
        if input.agg()=='day':
            start_date = pd.to_datetime(input.range()[0])
            end_date = pd.to_datetime(input.range()[1])
            prod_sum = walmart_df[walmart_df["Date"].between(start_date, end_date, inclusive='both')].groupby([walmart_df['Date'],walmart_df[input_comparison]]).agg({'Total':'mean'})
        
        # If user chooses to aggregate by week
        else:
            prod_sum = walmart_df.groupby([input_comparison, pd.Grouper(key='Date', freq='W-MON')]).agg({'Total':'mean'})

        # Plotting the stack plot
        chart = alt.Chart(prod_sum.reset_index()).mark_area().encode(
            y=alt.Y('Total',title='Total sales'),
            x = 'Date:T',
            color = input_comparison,
            tooltip=[input_comparison,'Date','Total']
        )
        
        return chart

    

app = App(app_ui, server)
