from datetime import date
from shiny import App, ui, render
import pandas as pd
import altair as alt
from shinywidgets import render_altair, output_widget 

## Input choices
METRIC_CHOICES = {
    "total": "Total Sales",
    "gross": "Gross Income",
    "cogs": "COGS",
    "margin": "Margin %",
}

BRANCH_CHOICES = {
    "all": "All Branches / Cities",
    "A": "Branch A",
    "B": "Branch B",
    "C": "Branch C",
}

# Default date range
DEFAULT_START = date(2019, 1, 1)
DEFAULT_END = date(2019, 3, 30)

## App interface
app_ui = ui.page_fluid(
    ui.div(
        ui.h2("Walmonitor 0.1.0"),
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
                selected=["total", "gross"],
            ),
            # Aggregation: day vs week
            ui.input_radio_buttons(
                "agg",
                "Aggregation",
                choices={"day": "Day", "week": "Week"},
                selected="day",
                inline=True,
            ),
            # Rolling average: none vs 7 days
            ui.input_radio_buttons(
                "roll",
                "Rolling average",
                choices={"none": "None", "7d": "7 days"},
                selected="none",
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
                "Branch / City",
                choices=BRANCH_CHOICES,
                selected="all",
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
                    ui.panel_conditional(   # Used Claude to suggest which ui.* to use for adding a slider conditional on user input
                        "input.agg === 'day'",
                        ui.input_slider(
                            "range",
                            "Select a date range",
                            min = pd.to_datetime('2019-01-01'),
                            max = pd.to_datetime('2019-03-31'),
                            value = [pd.to_datetime('2019-01-01'),pd.to_datetime('2019-01-31')],
                            ticks = True,
                            step = 1,
                            time_format="%Y-%m-%d"
                        ),
                        ui.help_text("Suggested range size : 1 month"),
                    ),
                    output_widget("stack_plot"),
                    full_screen = True
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
            # # TODO: remove debug section in final version
            # ui.hr(),
            # ui.card(
            #     ui.card_header("Debug (current inputs)"),
            #     ui.output_text_verbatim("debug_inputs"),
            # ),
        ),
    ),
)


## Server
def server(input, output, session):
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
        walmart_df = pd.read_csv('data/raw/walmart_sales_data.csv')
        walmart_df['Date']=pd.to_datetime(walmart_df['Date'])

        # If user chooses to aggregate by day 
        if input.agg()=='day':
            start_date = pd.to_datetime(input.range()[0])
            end_date = pd.to_datetime(input.range()[1])
            prod_sum = walmart_df[walmart_df["Date"].between(start_date, end_date, inclusive='both')].groupby([walmart_df['Date'],walmart_df['Product line']]).agg({'Total':'mean'})
        else: # If user chooses to aggregate by week
            prod_sum = walmart_df.groupby(['Product line', pd.Grouper(key='Date', freq='W-MON')]).agg({'Total':'mean'})
        
        chart = alt.Chart(prod_sum.reset_index()).mark_area().encode(
            y=alt.Y('Total',title='Total sales'),
            x = 'Date:T',
            color = 'Product line',
            tooltip=['Product line','Date','Total']
        )
        return chart

app = App(app_ui, server)
