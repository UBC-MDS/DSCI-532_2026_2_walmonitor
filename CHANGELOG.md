# CHANGELOG

## [0.2.0]

### Added

* Functional dashboard app with three interactive charts (`src/app.py`)
* Demo animation (`img/demo.gif`)
* Component inventory(`reports/m2_spec.md`)
* Reactivity diagram and description (`reports/m2_spec.md`)
* `pip` dependencies for app deployment (`requirements.txt`)

### Changed

* User stories and specifications refined (`reports/m2_spec.md`)
* `conda` environment updated to include `matplotlib` and upgrade `altair` to version 5.5.0 with `vegafusion`(`environment.yml`).

### Known Issues

* Minor UI issues with spacing and padding.
* The line plot and the ranked bar plot are missing a mouse on-hover tooltip to show the exact values of the data points.
* The ranked bar plot is not as visually appealing as the other two plots due to the layout constraints of the dashboard.

### Reflection

* All three user stories were refined and implemented in the app. We aimed to provide a user interface that was intuitive and user-friendly, allowing users to easily navigate through the different sections of the dashboard. However, due to the the layout of different types of plots (e.g. tall vs. wide), we had to make some compromises in the design of the dashboard. For instance, we had to place the stacked area plot and the ranked bar plot on the same row to allow the top space reserved for the most informative line plot. This resulted in a less than ideal layout for the ranked bar plot, which is too tall and not as wide as it could be.
* The overall layout remains the same as the initial sketch with some minor UI improvements to better fulfill the refined user stories.
  * Add a comparison input to the left control bar to allow different comparison options for the stacked area plot and the ranked bar plot.
  * Remove the date range slider from the line plot to allow an overall view of trends.
  * Add a date range slider to the stacked area plot to allow better-looking charts.
  * Remove the metric and overlay selectors for the ranked bar plot to avoid confusion and make it more straightforward to use.

## [0.1.0]

### Added

* Dataset for dashboard views (`data/raw/walmart_sales_data.csv`)
* README (`README.md`)
* Project proposal (`reports/m1_proposal.md`)
* Project description (`description.md`)
* Code of conduct (`CODE_OF_CONDUCT.md`)
* Contributing guidelines (`CONTRIBUTING.md`)
* Exploratory data analysis (`notebooks/eda_analysis.ipynb`)
* App sketch and description (`reports/m1_proposal.md`)
* Skeleton app (`src/app.py`)
* Development dependencies (`environment.yml`)
