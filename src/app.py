from datetime import date
from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_altair
import altair as alt
alt.data_transformers.enable('vegafusion')
import warnings
warnings.filterwarnings('ignore', module='altair')
import pandas as pd

## Input choices
METRIC_CHOICES = {
    "Total": "Total Sales",
    "gross income": "Gross Income",
    "cogs": "COGS",
    "gross margin percentage": "Margin %",
}

BRANCH_CHOICES = {
    "all": "All Branches / Cities",
    "Yangon": "Branch A (Yangon)",
    "Mandalay": "Branch B (Mandalay)",
    "Naypyitaw": "Branch C (Naypyitaw)",
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
                selected=["Total", "gross income"],
            ),
            # Aggregation: day vs week
            ui.input_radio_buttons(
                "agg",
                "Aggregation",
                choices={"day": "Day", "week": "Week"},
                selected="week",
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
            # # TODO: remove debug section in final version
            # ui.hr(),
            # ui.card(
            #     ui.card_header("Debug (current inputs)"),
            #     ui.output_text_verbatim("debug_inputs"),
            # ),
        ),
    ),
)

# ── data ─────────────────────────────────────────────────────────
walmart_df = pd.read_csv('data/raw/walmart_sales_data.csv')
walmart_df['Date'] =  pd.to_datetime(walmart_df['Date'], format='%Y-%m-%d')

# ── helpers ─────────────────────────────────────────────────────────
def line_plot(df, metrics, category) -> alt.Chart:
    df = df.copy()
    
    df = df.reset_index()
    
    lines = []
    
    for met in metrics:
        
        if met =='gross margin percentage':
             unit = '%'
        else:
            unit = 'K'

        df_met = df[df['metric'] == met]

        line = alt.Chart(df_met).mark_line().encode(
            x=alt.X('Date:T', axis=alt.Axis(labelAngle=270)),
            y=alt.Y('value:Q', title=met, axis=alt.Axis(labelExpr=f"datum.value + '{unit}'")),
            stroke=alt.Stroke('metric:N', legend=alt.Legend(title=''))
        )
        
        lines.append(line)
    
    comb = alt.layer(*lines).properties(
        width=1400, height=300,
        title=f'Time Series Across {category}'
    )

    return comb 

# ── server ──────────────────────────────────────────────────────────
def server(input, output, session):

    @reactive.calc
    def resample():

        df = walmart_df.copy()

        metric = input.metrics()

        city = input.branch()

        if not city == 'all':

            df = df[df['City'] == city]
            
        if input.agg() == 'week':
            resample_freq = 'W'
        else:
            resample_freq = 'D'

        # Make date the index for resampling by week 
        df = df.set_index('Date')
        
        # Resample metric by summing or averaging across the chosen resampling period
        # Note that if you resample on entire data frame metric per category info is lost
        df_lst = []

        for met in metric:
            if met == 'gross margin percentage':
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

    @render_altair
    def time_series_line():

        resamp_df, metric, city = resample()

        line = line_plot(resamp_df, metric, city)

        return line

app = App(app_ui, server)
