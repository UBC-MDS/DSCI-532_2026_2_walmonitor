# App specification

## Updated Job Stories

## Component Inventory

## Reactivity Diagram

```mermaid
flowchart TD
  A[/input_metrics/] --> F{{df_filtered}}
  B[/input_agg/] --> F
  C[/input_agg_method/] --> F
  D[/input_date_range/] --> F
  E[/input_branch/] --> F
  F --> P1([plot_sales_trend])
  F --> P2([plot_sales_mix])
  F --> P3([plot_product_lines])  
```
