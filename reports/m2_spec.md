# App specification

## Updated User Stories

| #   | User Story                       | Status         | Notes                         |
| --- | ------------------------------- | -------------- | ----------------------------- |
| 1   | As the Operations manager, I want to monitor sales metrics over time for all three branches combined or specific branches, so I can spot peaks, dips, and trends for high-level store planning, labour allocation and performance improvement targets overall or for a specific branch. | 🔄 Revised | Modified to include examination of the performance of all branches together or a specific selected branch on the dashboard, for a more targeted look at sales metric trends over time.                             |
| 2   | As the Operations manager, I want to see which product lines are gaining/losing importance, as well as how sales are spread across payment methods and customer characteristics (like gender, membership, etc.), so I can detect structural shifts and react with inventory/promo focus.| 🔄 Revised     | Added sales metric mix over time across multiple toggleable categories to make the dashboard more informative to the user beyond just the product lines.|
| 3   | As the Operations manager, I want to identify the top product lines, payment methods and customer characteristics over the entire analyzed time period, and whether the rankings differ by sales vs gross income so I know what to prioritize in the annual report.|  🔄 Revised   | Expanded the set of ranked categories for sales metrics to include other categories than just product line to compliment the sales  mix over time chart and user story 2 output, as well as provided high-level sales insight for the entire examined period of time.|

## Database
- Reactive calculations now rely on the walmart data in parquet format and a ibis/duckdb connection (as of release 0.4.0).
- Dataframe calculations described below are lazily evaluated based on the database reference rather than the csv data.

## Component Inventory

| ID | Type | Shiny widget / renderer | Depends on | User story |
| --- | --- | --- | --- | --- |
| `input_metrics` | Input | `ui.input_checkbox_group()` | -- | #1, #3 |
| `input_agg` | Input | `ui.input_radio_buttons()` | -- | #1 |
| `input_agg_method` | Input | `ui.input_radio_buttons()` | -- | #2 |
| `input_date_range` | Input | `ui.input_date_range()` | -- | #1, #2 |
| `input_branch` | Input | `ui.input_select()` | -- | #1, #2, #3 |
| `input_comparison` | Input | `ui.input_select()` | -- | #2, #3 |
| `input_slider_range` | Input | `ui.input_slider()` | `input_agg`,`input_date_range` | #2 |
| `df_filtered` | Reactive calc | `@reactive.calc` | `input_metrics`, `input_agg`, `input_agg_method`, `input_date_range`, `input_branch` | #1 |
| `df_filtered_product` | Reactive calc | `@reactive.calc` | `input_metrics`, `input_agg`, `input_agg_method`, `input_date_range`, `input_branch`,`input_comparison` | #2, #3 |
| `plot_sales_trend` | Output | `@render_altair` | `df_filtered` | #1 |
| `plot_sales_mix` | Output | `@render_altair` | `df_filtered_product`, `input_comparison`, `input_slider_range` | #2 |
| `plot_product_lines` | Output | `@render_altair` | `df_filtered_product`, `input_comparison` | #3 |

## Reactivity Diagram

```mermaid
flowchart LR
  A[/input_metrics/] --> F{{df_filtered}}
  B[/input_agg/] --> F
  C[/input_agg_method/] --> F
  D[/input_date_range/] --> F
  E[/input_branch/] --> F

  I[/input_slider_range/] --> P2 
  
  B --> I
  D --> I

  F --> P1([plot_sales_trend])

  B --> G{{df_filtered_product}}
  C --> G
  D --> G
  E --> G
  H[/input_comparison/] --> G

  G --> P2([plot_sales_mix])
  G --> P3([plot_product_lines]) 
  
```

## Calculation Details

The dashboard consists of two reactive calculations `df_filtered` and `df_filtered_product`, that take any user input changes to automatically update the plotted outputs on the dashboard in real time. Each reactive calculation depends on user inputs which can be modified in the left-hand dashboard panel and each reactive calculation produces a different modified DataFrame, which are then consumed by `altair` charts. These inputs allow the user to change which sales metrics are displayed, the aggregation method used per period, the examined date range and whether the metrics are displayed for a single branch or for all the branches combined.

### `df_filtered`

- Inputs: `input_metrics`, `input_agg`, `input_agg_method`, `input_date_range`, `input_branch`
- Transformation: filter the raw dataset by date range, selected metrics, chosen aggregation method, aggregation period and selected branches in a way compatible with the sales trend plot.
- Outputs:
  - `plot_sales_trend`: An Altair chart that displays the time series lines in the top half of the dashboard.

### `df_filtered_product`

- Inputs: `input_metrics`, `input_agg`, `input_agg_method`, `input_date_range`, `input_branch`, `input_comparison`
- Transformation: filter the raw dataset by date range, selected metrics, chosen aggregation method, aggregation period and selected branches in a way compatible with the stacked area and ranked bar plots.
- Outputs:
  - `plot_sales_mix`: An Altair chart of the stacked area over time displayed in the bottom left of the dashboard.
  - `plot_product_lines`: An Altair chart of the ranked bars displayed in the bottom right of the dashboard


## Tests

To verify the core logic of the dashboard, the following tests have been implemented:

- `filter_data()` : Unit tests (`pytest`) to ensure the returned dataframe is as expected.
