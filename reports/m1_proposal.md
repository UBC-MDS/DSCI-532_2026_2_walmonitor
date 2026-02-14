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
