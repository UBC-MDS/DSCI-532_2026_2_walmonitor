import pandas as pd

import altair as alt
alt.data_transformers.enable('vegafusion')

import warnings
warnings.filterwarnings('ignore', module='altair')

def line_plot(df,
              metric,
              colour,
              resample_freq: str = 'W'
              ) -> alt.Chart:

    df = df.copy()
    df['Date'] = pd.to_datetime(df['Date'])

    # Make date the index for resampling by week 
    df = df.set_index('Date')

    # Resample sales for each city by summing across the chosen resampling period
    # Note that if you resample on entire data frame metric per colour info is lost
    df_lst = []
    for col in df[colour]:
        col_df = df[df[colour] == col
                            ].resample(resample_freq)[metric].sum()
        col_df = col_df.reset_index()
        col_df[colour] = col
        df_lst.append(col_df)

    # Concatenate the city data frames for sorting by color in line plot
    concat_df = pd.concat(df_lst)

    # Create the weekly sales line plot for the cities
    line = alt.Chart(concat_df).mark_line().encode(
        x = alt.X('Date:T',
                axis=alt.Axis(labelAngle=45)),
        y = alt.Y(metric, title=metric.split(':')[0],
                axis=alt.Axis(labelExpr="datum.value + 'K'")),
                color=colour
    ).properties(width = 400, height = 250,
                title='Time Series Visualization')

    return line

# walmart_df = pd.read_csv('data/raw/walmart_sales_data.csv')

# line_plot(df = walmart_df,
#           metric = 'gross income',
#           colour = 'City',
#           )