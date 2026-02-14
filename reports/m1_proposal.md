# Supermarket Sales Performance Dashboard Proposal

## 1. Motivation and Purpose

### Target Audience
The target audience for this dashboard is regional supermarket managers and business analysts. I am acting as a data analyst responsible for providing insights into customer behavior, product performance, and revenue drivers.

### Problem
Supermarket managers need to understand which product lines generate the most revenue, how customer demographics influence purchasing behavior, and how different payment methods and locations impact profitability. Without a clear analytical dashboard, it is difficult to identify high-performing segments or detect patterns in customer satisfaction and revenue generation.

### Solution
This dashboard will provide interactive visualizations that allow managers to explore sales performance by branch, city, product line, customer type, and payment method. It will help identify revenue drivers, analyze customer satisfaction ratings, and compare profitability across branches. This supports strategic decisions related to marketing, pricing, and product placement.

--- 

## 2. Description of the Data

The dataset contains 1000 transaction-level records from Walmart supermarket branches, with 17 variables.

### Stats
- Observations: 1000 transactions
- Variables: 17 columns
- Each row represents a single purchase transaction.

Key variables include:
- `Branch` – Store branch (A, B, C)
- `City` – Store location
- `Customer type` – Member or Normal
- `Gender` – Customer gender
- `Product line` – Product category
- `Unit price` – Price per item
- `Quantity` – Number of items purchased
- `Total` – Total transaction amount
- `Payment` – Payment method
- `gross income` – Gross profit from transaction
- `Rating` – Customer satisfaction rating

### Relevance
The `Total` and `gross income` variables measure revenue and profitability. Categorical variables such as `Product line`, `Branch`, `City`, and `Customer type` allow segmentation analysis. `Rating` provides insight into customer satisfaction. Together, these variables allow comprehensive performance and behavioral analysis.

---

## 3. Research Questions & Usage Scenarios

### User Persona and Usage Scenario

The user of this dashboard is an Operations Manager for Walmart, located in Myanmar. They are responsible for monitoring the Operations of branches in three cities (Yangon, Naypyitaw, Mandalay) and providing data-driven insight for actionable financial improvements. They are primarily concerned with tracking microeconomic variables like daily sales revenue, transaction volume and cost of goods over time for the branches, while monitoring how these responses are spread across different product lines, payment methods and customer characteristics. Using these metrics and an effective dashboard, the user can make timely, informed logistical decisions on large scale inventory, as well as propose new product and membership offerings. The dashboard will enable these insights through time-series plots with adjustable scales, accompanied with aggregate sales data plots/summaries across categorizations of products and customers.

### Usage Stories

1. As the Operations manager, I want to monitor sales metrics over time so I can spot peaks, dips, and trends for high-level store planning, labour allocation and performance improvement targets.

2. As the Operations manager, I want to see which product lines are gaining/losing importance so I can detect structural shifts and react with inventory/promo focus.

3. As the Operations manager, I want to identify the top product lines and whether their rankings differ by sales vs gross income so I know what to prioritize in the annual report.