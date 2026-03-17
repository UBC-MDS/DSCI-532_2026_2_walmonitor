import re
import pandas as pd
import altair as alt
import warnings
from datetime import date
from pathlib import Path

from shiny import App, ui, render, reactive, req
from shinywidgets import render_altair, output_widget

import chatlas as ctl
from dotenv import load_dotenv
from querychat import QueryChat

load_dotenv()

alt.data_transformers.enable("vegafusion")
warnings.filterwarnings("ignore", module="altair")


## Colour palette
TAB10_HEX = [
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

DEFAULT_START = date(2019, 2, 1)
DEFAULT_END = date(2019, 3, 30)
DEFAULT_START_MIN = date(2019, 1, 1)
DEFAULT_END_MAX = date(2019, 3, 30)

## Load data
DATA_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "raw" / "walmart_sales_data.csv"
)
DATA_RAW = pd.read_csv(DATA_PATH)
DATA_RAW["Date"] = pd.to_datetime(DATA_RAW["Date"])
BASE_COLS = ["Date", "Branch", "Product line"] + list(METRIC_CHOICES.keys())
DATA_BASE = DATA_RAW[BASE_COLS].copy()  # Crop unused columns

# Module level (outside server)
BASELINE_MONTH = DATA_BASE[
    (DATA_BASE["Date"] >= pd.Timestamp(date(2019, 1, 1)))
    & (DATA_BASE["Date"] < pd.Timestamp(date(2019, 2, 1)))
]

BASELINE_LABEL = BASELINE_MONTH["Date"].max().strftime("%b %Y")


## Helper functions
def to_snake_case(name: str) -> str:
    """Convert a string to snake_case, suitable for column names."""
    s = str(name).strip().lower()
    s = s.replace("%", "pct")
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def tooltip_title(name: str) -> str:
    """Convert snake_case field names to sentence case for tooltips."""
    if str(name) == "time":
        return "Date"
    return str(name).replace("_", " ").capitalize()


def make_comparison_color_scale(df: pd.DataFrame, comparison: str) -> alt.Scale:
    """Build a stable color scale so category colors stay consistent across charts."""
    base_values = sorted([x for x in df[comparison].dropna().unique() if x != "Other"])
    domain = base_values + (["Other"] if "Other" in df[comparison].values else [])
    range_ = TAB10_HEX[: len(base_values)] + (["#b3b3b3"] if "Other" in domain else [])
    return alt.Scale(domain=domain, range=range_)


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
        .mark_line(point=alt.OverlayMarkDef(size=90))
        .encode(
            x=alt.X(
                "date:T",
                axis=alt.Axis(
                    labelAngle=0,
                    title="Date",
                    format="%b %d",
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
                    labelFontSize=15,
                    titleFontSize=15,
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
    df: pd.DataFrame,
    top_n: int = 6,
    method: str = "sum",
    comparison: str = "product_line",
) -> alt.Chart:
    rank = (
        df.groupby(comparison, dropna=False)["total"]
        .agg("sum" if method == "sum" else "mean")
        .sort_values(ascending=False)
    )

    top = rank.head(top_n)
    if len(rank) > top_n:
        top = pd.concat([top, pd.Series({"Other": rank.iloc[top_n:].sum()})])

    plot_df = (
        top.rename_axis(comparison)
        .reset_index(name="total")
        .sort_values("total", ascending=False)
    )

    color_scale = make_comparison_color_scale(plot_df, comparison)

    return (
        alt.Chart(plot_df)
        .mark_bar()
        .encode(
            x=alt.X(
                "total:Q",
                title="Total Sales" if method == "sum" else "Average Sales",
            ),
            y=alt.Y(
                f"{comparison}:N",
                sort="-x",
                title="",
            ),
            color=alt.Color(
                f"{comparison}:N",
                title=tooltip_title(comparison),
                scale=color_scale,
                legend=None,
            ),
            tooltip=[
                alt.Tooltip(f"{comparison}:N", title=tooltip_title(comparison)),
                alt.Tooltip(
                    "total:Q",
                    title="Total sales" if method == "sum" else "Average sales",
                    format=",.2f",
                ),
            ],
        )
        .properties(height=450, width="container")
    )


## Querychat
qc = QueryChat(
    DATA_RAW.copy(),
    "walmart",
    client=ctl.ChatGithub(model="gpt-4.1-mini"),
    greeting="""👋 Ask me anything about the Walmart sales.

* <span class="suggestion">What city generates the highest gross income on average?</span>
* <span class="suggestion">Show me the top 10 times with the highest average total sales.</span>
* <span class="suggestion">What is the relationship between unit price and quantity sold?</span>
* <span class="suggestion">What is the average total sales per transaction?</span>
    """,
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
        """,
)

## App interface
app_ui = ui.page_fluid(
    ui.tags.style("""
        .dashboard-sidebar h4,
        .dashboard-sidebar .control-label,
        .dashboard-sidebar .form-label,
        .dashboard-sidebar .shiny-input-checkboxgroup > label,
        .dashboard-sidebar .shiny-input-radiogroup > label,
        .dashboard-sidebar .shiny-input-container > label {
            font-size: 1.2rem !important;
        }
        .vg-tooltip {
            font-size: 16px !important;
            padding: 10px 12px !important;
        }
        .vg-tooltip table {
            font-size: 16px !important;
        }
    """),
    ui.div(
        ui.h1("Walmonitor 0.3.0"),
        style="margin-top: 24px; margin-bottom: 24px; margin-left: 24px;",
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
                        "Group By",
                        choices=AGG_CHOICES,
                        selected=DEFAULT_AGG,
                        inline=True,
                    ),
                    # Aggregation method: sum vs mean
                    ui.input_radio_buttons(
                        "input_agg_method",
                        "Apply",
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
                        min=DEFAULT_START_MIN,
                        max=DEFAULT_END_MAX,
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
                    class_="dashboard-sidebar",
                ),
                # View panel on the right
                ui.div(
                    ui.layout_columns(
                        ui.value_box(
                            f"Average Sales vs. {BASELINE_LABEL}",
                            ui.output_ui("sales_change"),
                            height="150px",
                        ),
                        ui.value_box(
                            "Gross Income Shown",
                            ui.output_ui("gross_income_viewed"),
                            height="150px",
                        ),
                        ui.value_box(
                            "Total Sales Shown",
                            ui.output_ui("total_sales_viewed"),
                            height="150px",
                        ),
                        ui.value_box(
                            ui.output_text("min_max_selected"),
                            ui.output_ui("min_max_sales_viewed"),
                            height="150px",
                        ),
                        fill=False,
                    ),
                    ui.layout_columns(
                        ui.card(
                            ui.card_header(
                                ui.tags.span(
                                    ui.output_text("selected_metrics"),
                                    style="font-size: 1.2rem;",
                                )
                            ),
                            output_widget("plot_sales_trend"),
                        ),
                        col_widths=(12,),
                    ),
                    ui.layout_columns(
                        ui.card(
                            ui.card_header(
                                ui.tags.span(
                                    "Sales Mix Over Time", style="font-size: 1.2rem;"
                                )
                            ),
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
                                            width="95%",
                                        ),
                                        style="margin-top: -5px; margin-bottom: -20px; padding-left: 40px; font-size: 1.2rem;",
                                    ),
                                ),
                            ),
                            output_widget("plot_sales_mix"),
                            full_screen=True,
                        ),
                        ui.card(
                            ui.card_header("Ranked Sales", style="font-size: 1.2rem;"),
                            ui.div(
                                output_widget("plot_product_lines"),
                                style="height: 200px;",
                            ),
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
                qc.sidebar(),
                ui.card(
                    ui.card_header(ui.output_text("chat_title")),
                    ui.output_data_frame("chat_table"),
                    fill=True,
                ),
                ui.layout_columns(
                    ui.card(
                        ui.card_header("Sales by Product Line"),
                        output_widget("chat_plot_bar"),
                        full_screen=True,
                    ),
                    ui.card(
                        ui.card_header("Sales Trend"),
                        output_widget("chat_plot_trend"),
                        full_screen=True,
                    ),
                    col_widths=(5, 7),
                    fill=False,
                ),
                ui.download_button(
                    "download_chat_data", "⬇️ Download Filtered Data as CSV"
                ),
                fillable=True,
            ),
        ),
    ),
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
    def df_rel_baseline() -> pd.DataFrame:
        """
        Apply filters and aggregations to the baseline month data,
        returning the processed DataFrame.
        """
        df = BASELINE_MONTH

        # Filter rows by branch
        branch = input.input_branch()
        if branch != "all":
            df = df[df["Branch"] == branch]

        # Filter columns by metrics
        metrics = DEFAULT_METRICS
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
    @render_altair
    def plot_product_lines():  # bottom right plot
        """Render the ranked product lines plot based on the filtered data."""
        return make_ranked_product_lines_bars(
            df_filtered_product(),
            method=input.input_agg_method(),
            comparison=to_snake_case(input.input_comparison()),
        ).configure_axis(titleFontSize=15, labelFontSize=15)

    @render_altair
    def plot_sales_mix():  # bottom left plot
        """
        This function uses user input to determine what to compare in the plot (Product line, Customer type, Payment type, Gender)
        and what date range to choose from if the values are aggregated by day.
        """
        data = df_filtered_product()

        input_comparison = to_snake_case(input.input_comparison())

        if input.input_agg() == "day":
            start_date = pd.to_datetime(input.input_slider_range()[0])
            end_date = pd.to_datetime(input.input_slider_range()[1])
            data = data[data["time"].between(start_date, end_date, inclusive="both")]

        color_scale = make_comparison_color_scale(data, input_comparison)

        chart = (
            alt.Chart(data)
            .mark_area()
            .encode(
                y=alt.Y("total:Q", title="Total Sales"),
                x=alt.X("time:T", title="Date", axis=alt.Axis(labelAngle=0)),
                color=alt.Color(
                    f"{input_comparison}:N",
                    title=input.input_comparison(),
                    scale=color_scale,
                    legend=alt.Legend(
                        orient="bottom",
                        direction="horizontal",
                        columns=3,
                        labelFontSize=15,
                        titleFontSize=15,
                    ),
                ),
                tooltip=[
                    alt.Tooltip(
                        f"{input_comparison}:N", title=tooltip_title(input_comparison)
                    ),
                    alt.Tooltip("time:T", title="Date"),
                    alt.Tooltip("total:Q", title="Total sales", format=",.2f"),
                ],
            )
        )

        return chart.configure_axis(titleFontSize=15, labelFontSize=15)

    @output
    @render_altair
    def plot_sales_trend():  # top plot
        """Render the time-series line plot based on the filtered data."""
        return make_line_plot(df_filtered(), input.input_metrics()).configure_axis(
            titleFontSize=15, labelFontSize=15
        )

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

    @render_altair
    def chat_plot_bar():
        df = qc_vals.df()
        if (
            df is None
            or df.empty
            or "Product line" not in df.columns
            or "Total" not in df.columns
        ):
            return (
                alt.Chart(pd.DataFrame({"note": ["No data"]}))
                .mark_text()
                .encode(text="note:N")
            )
        summary = (
            df.groupby("Product line", as_index=False)["Total"]
            .sum()
            .sort_values("Total", ascending=False)
        )
        return (
            alt.Chart(summary)
            .mark_bar()
            .encode(
                x=alt.X("Total:Q", title="Total Sales"),
                y=alt.Y("Product line:N", sort="-x", title=""),
                tooltip=["Product line", "Total"],
            )
            .properties(height=280, width="container")
        )

    @render_altair
    def chat_plot_trend():
        df = qc_vals.df()
        if (
            df is None
            or df.empty
            or "Date" not in df.columns
            or "Total" not in df.columns
        ):
            return (
                alt.Chart(pd.DataFrame({"note": ["No data"]}))
                .mark_text()
                .encode(text="note:N")
            )
        df = df.copy()
        df["Date"] = pd.to_datetime(df["Date"])
        daily = df.groupby("Date", as_index=False)["Total"].sum()
        return (
            alt.Chart(daily)
            .mark_line()
            .encode(
                x=alt.X("Date:T", title="Date"),
                y=alt.Y("Total:Q", title="Total Sales"),
                tooltip=["Date:T", "Total:Q"],
            )
            .properties(height=280, width="container")
        )

    @render.download(filename="filtered_data.csv")
    def download_chat_data():
        df = qc_vals.df()
        if df is None:
            df = pd.DataFrame()
        yield df.to_csv(index=False)

    @render.text
    def sales_change():

        req("Total" in input.input_metrics())

        total_sales_change_percent = 100 * (
            df_filtered()["total"].mean() / df_rel_baseline()["total"].mean() - 1
        )

        color = "green" if total_sales_change_percent >= 0 else "red"
        change_symbol = "+" if total_sales_change_percent >= 0 else ""
        html_string = ui.HTML(
            f'<span style="color:{color}; font-weight:bold;">{change_symbol}{total_sales_change_percent:,.2f}%</span>'
        )

        return html_string

    @render.text
    def gross_income_viewed():

        req("gross income" in input.input_metrics())

        gross_income_total = df_filtered()["gross_income"].sum()

        html_string = ui.HTML(
            f'<span style="color:{"black"}; font-weight:bold;">${gross_income_total:,.0f}</span>'
        )

        return html_string

    @render.text
    def total_sales_viewed():

        req("Total" in input.input_metrics())

        total_sales = df_filtered()["total"].sum()

        html_string = ui.HTML(
            f'<span style="color:{"black"}; font-weight:bold;">{"$"}{total_sales:,.0f}</span>'
        )

        return html_string

    @render.text
    def selected_metrics():

        if len(input.input_metrics()) < 1:
            title_string = "No Metrics Selected, Please Select One or More Metrics"
        else:
            metric_lst = [
                str(METRIC_CHOICES[metric]) for metric in input.input_metrics()
            ]
            title_string = (
                ", ".join(metric_lst)
                + " Over Time - "
                + BRANCH_CHOICES[input.input_branch()]
            )

        return title_string

    @render.text
    def min_max_sales_viewed():

        if len(input.input_metrics()) < 1:
            return ui.HTML(
                f'<span style="color:{"black"}; font-weight:bold; font-size:1.2rem;">Select A Metric</span>'
            )

        if "Total" in input.input_metrics():
            metric = to_snake_case("total")
        else:
            metric = to_snake_case(input.input_metrics()[0])

        min_sales = min(df_filtered()[metric])
        max_sales = max(df_filtered()[metric])

        if metric == "gross_margin_percentage":
            unit_pre = ""
            unit_suf = "%"
        else:
            unit_pre = "$"
            unit_suf = ""

        html_string = ui.HTML(
            f'<span style="color:{"black"}; font-weight:bold; font-size:1.2rem;">Max: {unit_pre}{max_sales:,.0f}{unit_suf}</span>'
            f'<span style="color:{"black"}; font-weight:bold; font-size:1rem;">Min: {unit_pre}{min_sales:,.0f}{unit_suf}</span>'
        )

        return html_string

    @render.text
    def min_max_selected():

        if len(input.input_metrics()) < 1:
            return "Max/Min of Key Metrics"

        if "Total" in input.input_metrics():
            metric = "Total"
        else:
            metric = input.input_metrics()[0]

        label = METRIC_CHOICES[metric]

        return f"{label} Shown"

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
