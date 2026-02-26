import pandas as pd

import altair as alt
alt.data_transformers.enable('vegafusion')

import warnings
warnings.filterwarnings('ignore', module='altair')

walmart_df = pd.read_csv('data/raw/walmart_sales_data.csv')
walmart_df['Date'] =  pd.to_datetime(walmart_df['Date'], format='%Y-%m-%d')

def resample_sum():

        df = walmart_df.copy()

        metric = ['gross income', 'Total', 'cogs', 'gross margin percentage']

        print(metric)

        city = 'all'

        if city=='all':
            # resample_freq = 'we'

            # print(resample_freq)

            # if input.agg() == 'week':
            #     resample_freq = 'W'
            # else:
            #     resample_freq = 'D'

            resample_freq = 'W'

            # Make date the index for resampling by week 
            df = df.set_index('Date')
            
            # Resample metric by summing across the chosen resampling period
            # Note that if you resample on entire data frame metric per category info is lost
            df_lst = []

            for met in metric:
                print(met)
                col_df = df.resample(resample_freq)[met].sum()
                col_df = col_df.reset_index()
                col_df['metric'] = met
                # Put df in long format for time series plot
                col_df = col_df.rename(columns={met: 'value'})
                df_lst.append(col_df)

            # Concatenate the city data frames for sorting by color in line plot
            concat_df = pd.concat(df_lst)
            concat_df = concat_df.set_index('Date')

            return concat_df, metric, city

concat_df, metric, city = resample_sum()

print(concat_df)

def line_plot(df, metrics, category) -> alt.Chart:
    df = df.copy()
    
    df = df.reset_index()
    
    lines = []
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#ADD8E6', '#D2D236', "#AE2020"]
    
    for col, met in zip(colors, metrics):
        if met =='gross margin percentage':
             unit = '%'
        else:
            unit = 'K'

        df_met = df[df['metric'] == met]
        line = alt.Chart(df_met).mark_line().encode(
            x=alt.X('Date:T', axis=alt.Axis(labelAngle=270)),
            y=alt.Y('value:Q', title=met, axis=alt.Axis(labelExpr=f"datum.value + '{unit}'")),
            stroke=alt.Stroke('metric:N', legend=alt.Legend(title=''))
            # color=alt.Color(stroke= alt.value(col), legend=alt.Legend(title=''))
        )
        lines.append(line)
    
    comb = alt.layer(*lines).properties(
        width=1420, height=300,
        title=f'Time Series Across {category}'
    ).resolve_scale(y='independent')

    return comb 

# def line_plot(df, metrics, category) -> alt.Chart:
#     df = df.copy()
#     df = df.reset_index()
#     colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#ADD8E6']
    
#     return alt.Chart(df).mark_line().encode(
#         x=alt.X('Date:T', axis=alt.Axis(labelAngle=270)),
#         y=alt.Y('value:Q', title='Value', axis=alt.Axis(labelExpr="datum.value + 'K'")),
#         stroke=alt.Stroke('metric:N', scale=alt.Scale(domain=metrics, range=colors), legend=alt.Legend(title='Metric'))
#     ).properties(width=1420, height=300, title=f'Time Series Across {category}').resolve_scale(y='independent')

# def line_plot(df, metrics, category) -> alt.Chart:
#     df = df.copy()
#     df = df.reset_index()
#     colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#ADD8E6']
    
#     line = alt.Chart(df).mark_line().encode(
#         x=alt.X('Date:T', axis=alt.Axis(labelAngle=270)),
#         y=alt.Y('value:Q', title='Value', axis=alt.Axis(labelExpr="datum.value + 'K'")),
#         stroke=alt.Stroke('metric:N', scale=alt.Scale(domain=metrics, range=colors), legend=alt.Legend(title='Metric'))
#     ).properties(width=1420, height=300, title=f'Time Series Across {category}').resolve_scale(y='independent')

#     return line

walmart_df = pd.read_csv('data/raw/walmart_sales_data.csv')

line = line_plot(concat_df,
            metric,
            metric,
          )
line.save('time_series.png', ppi=300)