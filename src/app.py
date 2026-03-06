import re
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
import warnings
from datetime import date
from pathlib import Path

from shiny import App, ui, render, reactive
from shinywidgets import render_altair, output_widget

import chatlas as ctl
import pandas as pd
from dotenv import load_dotenv
from querychat import QueryChat

load_dotenv()

alt.data_transformers.enable("vegafusion")
warnings.filterwarnings("ignore", module="altair")


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
    "A": "Branch A (Yangon)",
    "B": "Branch B (Mandalay)",
    "C": "Branch C (Naypyitaw)",
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
BASE_COLS = ["Date", "Branch", "Product line"] + list(METRIC_CHOICES.keys())
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


def make_line_plot(df_wide, metrics) -> alt.Chart:
    if df_wide.empty or not metrics:
        return (
            alt.Chart(pd.DataFrame({"note": ["Select at least one metric."]}))
            .mark_text(align="left")
            .encode(text="note:N")
            .properties(height=260, width="container")
        )

    selected_cols = [to_snake_case(m) for m in metrics]
    selected_cols = [c for c in selected_cols if c in df_wide.columns]

    snake_to_label = {to_snake_case(k): v for k, v in METRIC_CHOICES.items()}

    df_long = df_wide[["date"] + selected_cols].melt(
        id_vars="date", var_name="metric", value_name="value"
    )
    df_long["metric_label"] = (
        df_long["metric"].map(snake_to_label).fillna(df_long["metric"])
    )

    chart = (
        alt.Chart(df_long)
        .mark_line()
        .encode(
            x=alt.X(
                "date:T",
                axis=alt.Axis(
                    labelAngle=0,
                    format="%Y-%m-%d",
                    title="Date",
                ),
            ),
            y=alt.Y("value:Q", title=None),
            color=alt.Color(
                "metric_label:N",
                legend=alt.Legend(
                    title="Metrics",
                    orient="top-right",
                    direction="vertical",
                    fillColor="white",
                    strokeColor="#ddd",
                    padding=6,
                ),
            ),
            tooltip=[
                alt.Tooltip("date:T", title="Date"),
                alt.Tooltip("metric_label:N", title="Metric"),
                alt.Tooltip("value:Q", title="Value", format=",.2f"),
            ],
        )
        .properties(height=350, width="container")
    )

    return chart


def make_ranked_product_lines_bars(
    df, top_n=6, method="sum", comparison="product_line"
):
    rank = (
        df.groupby(comparison, dropna=False)["total"]
        .agg("sum" if method == "sum" else "mean")
        .sort_values(ascending=False)
    )

    top = rank.head(top_n)
    if len(rank) > top_n:
        top = pd.concat([top, pd.Series({"Other": rank.iloc[top_n:].sum()})])

    labels = top.index.tolist()[::-1]
    values = top.values[::-1]

    palette = list(plt.get_cmap("tab10").colors)
    # consistent mapping by alphabetical order (stable across filters)
    base_lines = sorted([x for x in df[comparison].dropna().unique() if x != "Other"])
    color_map = {name: palette[i % len(palette)] for i, name in enumerate(base_lines)}
    color_map["Other"] = (0.7, 0.7, 0.7)  # neutral gray for "Other"

    bar_colors = [color_map.get(lbl, palette[0]) for lbl in labels]

    max_len = max((len(str(x)) for x in labels), default=10)
    fig_w = 7.8
    fig_h = max(3.2, 0.45 * len(labels) + 1.2)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    ax.barh(labels, values, color=bar_colors)

    ax.set_ylabel("")
    ax.set_xlabel(
        "Total Sales" if method == "sum" else "Average Sales",
        labelpad=10,  # <- adds padding under x-axis label
    )

    # Give y tick labels some breathing room
    ax.tick_params(axis="y", pad=6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    left_margin = min(0.55, max(0.25, 0.18 + 0.012 * max_len))
    fig.subplots_adjust(left=left_margin, right=0.97, top=0.90, bottom=0.22)

    return fig

## Querychat
qc = QueryChat(
    DATA_RAW.copy(),
    "walmart",
    client=ctl.ChatGithub(model="gpt-4.1-mini"),
    greeting="""👋 Ask me anything about the Walmart Sales.

        * <span class="suggestion">What city generates the highest gross income on average?</span>
        * <span class="suggestion">How do sales prices vary over the given time period from January to March?</span>
        * <span class="suggestion">What is the relationship between unit price and quantity sold?</span>
        * <span class="suggestion">What is the average total sales per transaction?</span>
    """ ,
    data_description="""
        Walmart Sales Data (1000 Transactions).
        - Invoice ID: Invoice of the sales made 
        - Branch: Branch at which sales were made, 'A' (Yangon), 'B' (Mandalay), or 'C' (Naypyitaw)
        - City: The location of the branch, 'Yangon', 'Mandalay', or 'Naypyitaw'
        - Customer type: The type of the customer, 'Normal', or 'Member'
        - Gender: Gender of the customer making purchase, 'Male', or 'Female'
        - Product line: Product line of the product sold, 'Health and beauty', 'Electronic accessories', 'Home and lifestyle', 'Sports and travel', 'Food and beverages', or 'Fashion accessories'
        - Unit price: The price of each product
        - Quantity : The amount of the product sold
        - Tax 5% : The amount of tax on the purchase
        - Total : The total cost of the purchase
        - Date : The date on which the purchase was made
        - Time : The time at which the purchase was made
        - Payment : The type of payment method used, 'Cash', 'Ewallet', or 'Credit card'
        - cogs : Cost Of Goods sold
        - gross margin percentage : Gross margin percentage
        - gross income : Gross income
        - Rating : Rating
        """
)

## App interface
app_ui = ui.page_fluid(

    ui.div(
        ui.h1("Walmonitor 0.2.0"),
        style="margin-top: 24px;",
    ),
    
    ui.navset_tab(
        # ── Tab 1: Dashboard ───────────────────────────────────────────────────────
        ui.nav_panel(
            "Dashboard",
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
                    ui.output_ui("metrics_warning"),
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
                    ui.input_select(  # User decides what comparison they want highlighted on the plot
                        "input_comparison",
                        "Compare sales by",
                        choices={
                            "Product line": "Product line",
                            "Payment": "Payment type",
                            "Gender": "Gender",
                            "Customer type": "Customer type",
                        },
                        selected="Product line",
                    ),
                    width=320,
                ),
            # View panel on the right
            ui.div(
                ui.layout_columns(
                    ui.card(
                        ui.card_header("Metrics Over Time"),
                        output_widget("plot_sales_trend"),
                    ),
                    col_widths=(12,),
                ),
                ui.layout_columns(
                    ui.card(
                        ui.card_header("Sales Mix Over Time"),
                        ui.panel_conditional(
                            "input.input_agg === 'day'",
                            ui.div(
                                ui.div(
                                    ui.help_text(
                                        "For the best results, use the slider to view a smaller date range (e.g. one month)."
                                    ),
                                    style="margin-bottom: 8px;",
                                ),
                                ui.div(
                                    ui.input_slider(
                                        "input_slider_range",
                                        "",
                                        min=pd.to_datetime("2019-01-01"),
                                        max=pd.to_datetime("2019-03-31"),
                                        value=[
                                            pd.to_datetime("2019-02-01"),
                                            pd.to_datetime("2019-02-28"),
                                        ],
                                        ticks=True,
                                        step=1,
                                        time_format="%Y-%m-%d",
                                    ),
                                    style="margin-top: -20px; margin-bottom: -20px; padding-left: 40px;",
                                ),
                            ),
                        ),
                        output_widget("plot_sales_mix"),
                        full_screen=True,
                    ),
                    ui.card(
                        ui.card_header("Ranked Sales"),
                        ui.output_plot("plot_product_lines", height="200px"),
                        full_screen=True,
                    ),
                    col_widths=(7, 5),
                ),
            ),
        ),
        ),
        # ── Tab 2: LLM Chat ───────────────────────────────────────────────────────
        ui.nav_panel(
            "LLM Chat",
            ui.layout_sidebar(
            qc.sidebar(title='Ask any questions:'),
            ui.card(
                ui.card_header(ui.output_text("chat_title")),
                ui.output_data_frame("chat_table"),
                fill=True,
            ),
            fillable=True,
            )  
        )
    )
)





## Server
def server(input, output, session):

    # ── Tab 1: reactive calcs ─────────────────────────────────────────────────
    ## Reactive calcs
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

    @reactive.calc
    def df_filtered_product() -> pd.DataFrame:
        df = DATA_RAW

        start, end = input.input_date_range()
        start_ts = pd.Timestamp(start)
        end_ts = pd.Timestamp(end) + pd.Timedelta(days=1)
        mask = (df["Date"] >= start_ts) & (df["Date"] < end_ts)

        branch = input.input_branch()
        if branch != "all":
            mask &= df["Branch"] == branch

        COMP_COL = input.input_comparison()
        SALES_COL = "Total"

        df = df.loc[mask, ["Date", COMP_COL, SALES_COL]].copy()

        if input.input_agg() == "day":
            df["time"] = df["Date"].dt.floor("D")
        else:
            df["time"] = df["Date"].dt.to_period("W-SAT").dt.start_time

        out = (
            df.groupby(["time", COMP_COL], as_index=False)[SALES_COL]
            .agg(input.input_agg_method())
            .sort_values(["time", COMP_COL])
            .reset_index(drop=True)
        )

        out = out.rename(columns={c: to_snake_case(c) for c in out.columns})

        return out

    @reactive.effect
    def _update_dates():
        start, end = input.input_date_range()[0], input.input_date_range()[1]
        ui.update_slider(
            "input_slider_range",
            label="",
            min=start,
            max=end,
            value=[start, end],
            step=1,
            time_format="%Y-%m-%d",
        )

    ## Outputs
    @render.plot
    def plot_product_lines():  # bottom right plot
        """Render the ranked product lines plot based on the filtered data."""
        return make_ranked_product_lines_bars(
            df_filtered_product(),
            method=input.input_agg_method(),
            comparison=to_snake_case(input.input_comparison()),
        )

    @render_altair
    def plot_sales_mix():  # bottom left plot
        """
        This function uses user input to determine what to compare in the plot (Product line, Customer type, Payment type, Gender)
        and what date range to choose from if the values are aggregated by day.
        """
        # Tab10 Hex Colors to match matplotlib tab10
        tab10_hex = [
            "#1f77b4",
            "#ff7f0e",
            "#2ca02c",
            "#d62728",
            "#9467bd",
            "#8c564b",
            "#e377c2",
            "#7f7f7f",
            "#bcbd22",
            "#17becf",
        ]

        data = df_filtered_product()
        input_comparison = to_snake_case(input.input_comparison())

        # If user chooses to aggregate by day
        if input.input_agg() == "day":
            start_date = pd.to_datetime(input.input_slider_range()[0])
            end_date = pd.to_datetime(input.input_slider_range()[1])
            data = data[data["time"].between(start_date, end_date, inclusive="both")]

        # Plotting the stack plot
        chart = (
            alt.Chart(data)
            .mark_area()
            .encode(
                y=alt.Y("total", title="Total sales"),
                x=alt.X("time:T", title="Date"),
                color=alt.Color(
                    input_comparison,
                    title=input.input_comparison(),
                    scale=alt.Scale(range=tab10_hex),
                    legend=alt.Legend(
                        orient="bottom",
                        direction="horizontal",
                        columns=3
                    ),
                ),
                tooltip=[input_comparison, "time", "total"],
            )
        )

        return chart

    @output
    @render_altair
    def plot_sales_trend():  # top plot
        """Render the time-series line plot based on the filtered data."""
        return make_line_plot(df_filtered(), input.input_metrics())

    @output
    @render.ui
    def metrics_warning():
        """
        Outputs a warning message if no metric is selected.
        """
        if (
            len(input.input_metrics()) == 0
        ):  # Used Claude.ai to help suggest ways to warn user to select at least one metric
            return ui.help_text("⚠️ Please select at least one metric.⚠️")
        
    # ── Tab 2: querychat ──────────────────────────────────────────────────────
    qc_vals = qc.server()

    @render.text
    def chat_title():
        return qc_vals.title() or "Walmart dataset"

    @render.data_frame
    def chat_table():
        return qc_vals.df()

    # ## Debug outputs (to be removed before release)
    # @output
    # @render.data_frame
    # def tbl_filtered():
    #     """For debug only: Display the filtered DataFrame"""
    #     return render.DataGrid(df_filtered(), height="280px")

    # @output
    # @render.data_frame
    # def tbl_filtered_product():
    #     """For debug only: Display the filtered DataFrame"""
    #     return render.DataGrid(df_filtered_product(), height="280px")

    # @output
    # @render.text
    # def debug_inputs():
    #     """For debug only: Display the current input values"""
    #     return (
    #         f"metrics = {list(input.input_metrics() or [])}\n"
    #         f"aggregation = {input.input_agg()}\n"
    #         f"method = {input.input_agg_method()}\n"
    #         f"date_range = {input.input_date_range()}\n"
    #         f"branch = {input.input_branch()}\n"
    #         f"number of filtered rows = {len(df_filtered())}\n"
    #   )


app = App(app_ui, server)
