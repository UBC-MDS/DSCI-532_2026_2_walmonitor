# CHANGELOG

## [0.4.0]

### Added

- Unit tests for data filtering logic (`tests/unit/test_filter_data.py`).
- UI tests for dashboard interactivity (`tests/playwright/test_ui.py`).
- Reactive feature between the ranked bar plot and the stacked area plot. Click on a bar in the ranked bar plot to filter the stacked area plot with the corresponding category.
- Instructions for running tests added to `README.md`.
- Instructions for setting up API keys for the LLM chatbot feature added to `README.md`.

### Changed

- `vegafusion` removed from `app.py` as it is no longer used.
- "COGS" replaced with "Cost of Goods Sold" to enhance clarity.
- Colour of the stacked area plot updated with more opacity to reduce contrast.
- LLM chatbot interface moved from the side bar to the top of the view to make it more prominent.
- Data processed to `parquet` format for faster loading and better performance.
- Data now filtered by `ibis` and DuckDB instead of `pandas` for better performance and scalability.
- Data percentage KPI box replaced by "Gross Income Shown" to better reflect user stories.

### Fixed

- LLM chatbot now correctly responds to user queries without errors on the first interaction.
- KPI box titles and values no longer overlap when browser is zoomed too large.

### Known Issues

- The y-axis of the line plot is hard to read when different metrics are selected due to the varying scales of the metrics. This makes it difficult to compare trends across different metrics.
- The LLM chatbot interface is not occupying the full width of its UI card, which makes it look less visually appealing and may affect the user experience when interacting with the chatbot.

### Release Highlights

- Performance improvements by switching to `parquet` format and using `ibis` with DuckDB for data processing.
- UI improvements to enhance readability and user experience.
- Addition of unit tests and UI tests to ensure reliability.
- Addition of interactive features to enhance user engagement.

### Collaboration

- **Summary of workflow:** During the lab, each team member is assigned a set of tasks, which they break down into smaller chores. Any substantial feature implementation starts with an update to the design documentation. Completed chores are submitted as pull requests and reviewed by a teammate — if everything looks good, the PR is approved and merged into dev; otherwise, the reviewer leaves detailed comments outlining the required changes.

- **CONTRIBUTING.md:** PR [#126](https://github.com/UBC-MDS/DSCI-532_2026_2_walmonitor/pull/126)
- **M3 retrospective:** After the collaboration feedback from M3 we decided to split larger tasks into smaller chores (use parent and sub-issues to track tasks and chores) to try and make PRs cleaner. We also decided to start any substantial feature implementation with an update to the design documentation.
- **M4:** In this milestone we ensured that every PR clearly describes its changes, that large PRs include a short comment noting what was reviewed, and that the design documentation `reports/m2_spec.md` is kept up to date whenever substantial changes are made.

### Reflection

- With all the implemented feedback, the dashboard now provides a comprehensive view of key insights from the Walmart Sales Data. It is designed to let users quickly understand sales trends, branch performance, and product line breakdowns at a glance.
- Current limitations: The dashboard is currently built around the specific format of the Walmart Sales dataset. Any change to the raw data format (e.g., renamed columns, different date formats) will break the existing logic and tests. Adapting the dashboard to a new dataset will require prior checks to ensure the data matches the expected format.
- To verify the core logic of the dashboard, the following tests have been implemented:
  - `test_filter_data`: Unit tests (`pytest`) to ensure that for every input (date range, aggregation method and range, comparison column, branch), the function filters the dataframe as expected. This ensures that the plots `plot_sales_mix` and `plot_product_lines` show the correct data.
  - `test_ui`: Playwright UI tests (`pytest-playwright`) to verify that user interactions with the dashboard filters correctly update the UI:
    - `test_branch_filter_updates_display`: Verifies that selecting a specific branch updates the value boxes, ensuring the dashboard responds to branch filter changes.
    - `test_date_range_filter`: Verifies that changing the date range updates the dashboard, ensuring only data within the selected range is displayed.
    - `test_aggregation_toggle`: Verifies that switching between Day and Week aggregation correctly updates the radio button state, ensuring the time grouping logic works correctly for both modes.

- **Feedback prioritization:** Functional improvements were prioritized over cosmetic changes, as ensuring the dashboard worked correctly was essential to meeting the milestone requirements.

- The M3 collaboration feedback (issue [#73](https://github.com/UBC-MDS/DSCI-532_2026_2_walmonitor/issues/73)) shaped our workflow the most this milestone. We found that the specific comments were very useful for pinpointing the problem areas we needed to address going forward. For example, feedback noted that some PRs were too large, which led us to start splitting tasks into smaller chores and adding detailed descriptions to every PR. This made reviews faster and more thorough by ensuring no changes were missed.

## [0.3.0]

### Added

- LLM chatbot interface for user queries about the dashboard data and insights (`src/app.py`).
- Dependencies for LLM chatbot interface (`requirements.txt`).
- Summary statistics cards above the line plot (`src/app.py`).
- Data source reference in EDA (`notebooks/eda_analysis.ipynb`) and `README.md`.

### Changed

- `shiny` and `vegafusion` versions updated to resolve conflicts.
- `matplotlib` removed from dependencies as it is no longer used in the app.
- Font sizes increased for control bar, UI card titles, date slider, and tooltips for better readability.
- Point mark size increased in the line plot for better visibility.
- Default date range changed to past three months.
- The ranked bar plot reconstructed with `altair` instead of `matplotlib` for better visual consistency and interactivity with the rest of the dashboard.

### Known Issues

- The ranked bar plot and the line plot on the LLM chatbot interface are not occupying the full height of their respective UI cards.
- The ranked bar plot is not as visually appealing as the other two plots due to the layout constraints of the dashboard.

### Reflection

- The LLM chatbot interface was added to allow users to ask questions about the data and insights displayed on the dashboard. This feature was implemented using the `OpenAI` API. The chatbot interface is designed to provide users with a more interactive and engaging experience when exploring the dashboard.
- The summary statistics cards were added to provide users with quick insights into key metrics such as comparison to a cutoff point, percentage of data shown, and the maximum and minimum metrics found in the filtered data. These cards are designed to be visually appealing and easy to read, allowing users to quickly grasp important information at a glance.
- We explored some themes to improve the overall aesthetics of the dashboard, but found them not doing significantly better than the default `shiny` theme. We decided to keep the default theme for its simplicity and clean look for now. It may be worth customizing our theme in the future or adding colours to some UI elements to make the dashboard more engaging.

## [0.2.0]

### Added

- Functional dashboard app with three interactive charts (`src/app.py`)
- Demo animation (`img/demo.gif`)
- Component inventory (`reports/m2_spec.md`)
- Reactivity diagram and description (`reports/m2_spec.md`)
- `pip` dependencies for app deployment (`requirements.txt`)

### Changed

- User stories and specifications refined (`reports/m2_spec.md`)
- `conda` environment updated to include `matplotlib` and upgrade `altair` to version 5.5.0 with `vegafusion`(`environment.yml`).

### Known Issues

- Minor UI issues with spacing and padding.
- The line plot and the ranked bar plot are missing a mouse on-hover tooltip to show the exact values of the data points.
- The ranked bar plot is not as visually appealing as the other two plots due to the layout constraints of the dashboard.

### Reflection

- All three user stories were refined and implemented in the app. We aimed to provide a user interface that was intuitive and user-friendly, allowing users to easily navigate through the different sections of the dashboard. However, due to the the layout of different types of plots (e.g. tall vs. wide), we had to make some compromises in the design of the dashboard. For instance, we had to place the stacked area plot and the ranked bar plot on the same row to allow the top space reserved for the most informative line plot. This resulted in a less than ideal layout for the ranked bar plot, which is too tall and not as wide as it could be.
- The overall layout remains the same as the initial sketch with some minor UI improvements to better fulfill the refined user stories.
  - Add a comparison input to the left control bar to allow different comparison options for the stacked area plot and the ranked bar plot.
  - Remove the date range slider from the line plot to allow an overall view of trends.
  - Add a date range slider to the stacked area plot to allow better-looking charts.
  - Remove the metric and overlay selectors for the ranked bar plot to avoid confusion and make it more straightforward to use.

## [0.1.0]

### Added

- Dataset for dashboard views (`data/raw/walmart_sales_data.csv`)
- README (`README.md`)
- Project proposal (`reports/m1_proposal.md`)
- Project description (`description.md`)
- Code of conduct (`CODE_OF_CONDUCT.md`)
- Contributing guidelines (`CONTRIBUTING.md`)
- Exploratory data analysis (`notebooks/eda_analysis.ipynb`)
- App sketch and description (`reports/m1_proposal.md`)
- Skeleton app (`src/app.py`)
- Development dependencies (`environment.yml`)
