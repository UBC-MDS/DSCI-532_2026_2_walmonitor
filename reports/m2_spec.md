# App specification

## Updated Job Stories

## Component Inventory

| ID | Type | Shiny widget / renderer |Depends on | Job story |
|---|---|---|---|---|
| input_metric | Input | ui.input_checkbox_group() | -- | #1, #3 |
| input_aggregation | Input | ui.input_checkbox_group() | -- | #1 |
| input_rolling_average | Input | ui.input_checkbox_group() | -- | #2 |
| input_date | Input | ui.input_date_range() | -- | #1, #2 |
| input_branchinpuinp | Input | ui.input_select() | -- | #1, #2, #3 |
| df_filtered | Reactive calc | @reactive.calc | input_metric, input_aggregation, input_rolling_average, input_date, input_branch | #1, #2, #3 |
| plot_sales_trend | Output | @render.plot | df_filtered | #1 |
| plot_sales_mix | Output | @render.plot | df_filtered | #2 |
| plot_product_lines | Output | @render.plot | df_filtered | #3 |
