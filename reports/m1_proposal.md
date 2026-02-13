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

## 3. Research Questions

The dashboard will aim to answer:

1. Which product lines generate the highest total revenue and gross income?
2. How does revenue differ across branches and cities?
3. Do members spend more than normal customers?
4. Which payment methods are most commonly used?
5. Is there a relationship between transaction amount and customer rating?
6. Are there differences in purchasing patterns between genders?

---

## 4. Planned Dashboard Design

The dashboard will include:

- A bar chart showing revenue by product line
- A branch comparison chart (Total sales by Branch)
- A city-level revenue breakdown
- A customer type comparison (Member vs Normal spending)
- A payment method distribution chart
- A scatterplot showing relationship between Total and Rating
- A summary metrics panel:
  - Total revenue
  - Average transaction value
  - Average rating

Interactive filters:
- Branch selector
- City selector
- Product line selector
- Customer type selector
- Gender selector
- Date range filter

The layout will prioritize clarity and comparative insights.

---

## 5. Expected Impact

This dashboard will enable data-driven decision-making by identifying profitable product lines, customer segments, and branch performance differences. Managers can use these insights to improve marketing strategies, optimize inventory, and enhance customer experience.
