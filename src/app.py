from datetime import date
from shiny import App, ui, render
import altair as alt
import pandas as pd
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
